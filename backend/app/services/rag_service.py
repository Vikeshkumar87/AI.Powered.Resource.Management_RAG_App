"""
RAG (Retrieval-Augmented Generation) service for intelligent resource queries.
"""
import logging
from typing import List, Dict, Any, Optional
from app.services.vector_store import VectorStoreService
from app.config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an AI assistant for a Resource Allocation and Bench Management system.
Your role is to help managers find the right resources for projects, analyze bench status,
and provide intelligent recommendations for team composition.

When answering questions:
- Be specific about resource names, skills, and availability
- Provide actionable recommendations
- Consider skill matches, experience levels, and availability
- Highlight any concerns or gaps in the team composition
- Format your response clearly with relevant details
"""


def _get_llm_client():
    """Get the configured LLM client."""
    provider = settings.llm_provider.lower()

    if provider == "openai" and settings.openai_api_key:
        try:
            from openai import OpenAI
            return ("openai", OpenAI(api_key=settings.openai_api_key))
        except ImportError:
            logger.warning("OpenAI package not available")

    if provider == "ollama":
        try:
            import httpx
            return (
                "ollama",
                httpx.Client(
                    base_url=settings.ollama_base_url,
                    timeout=httpx.Timeout(120.0, connect=10.0),
                ),
            )
        except ImportError:
            logger.warning("httpx not available for Ollama")

    return ("demo", None)


def _call_llm(provider: str, client, context: str, query: str) -> str:
    """Call the configured LLM to generate a response."""
    if provider == "openai" and client:
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context from our resource database:\n\n{context}\n\nQuestion: {query}",
                },
            ]
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")

    if provider == "ollama" and client:
        try:
            prompt = (
                f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Question: {query}\n\nAnswer:"
            )
            response = client.post(
                "/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")

    # Demo mode: generate a structured response from context
    return _demo_response(context, query)


def _demo_response(context: str, query: str) -> str:
    """Generate a demo response when no LLM is configured."""
    if not context:
        return (
            "No relevant resources or projects found matching your query. "
            "Please ensure the system has been seeded with data using the /admin/seed endpoint, "
            "and that the vector store has been indexed."
        )

    lines = context.strip().split("\n")
    entries = [l for l in lines if l.strip() and l.startswith(("Employee:", "Project:"))]

    if not entries:
        return (
            f"Based on your query '{query}', here is the relevant information from our database:\n\n"
            f"{context}\n\n"
            "Please configure an LLM provider (OpenAI or Ollama) for more intelligent analysis."
        )

    response_parts = [
        f"Based on your query: **'{query}'**\n",
        "Here are the most relevant matches from our resource database:\n",
    ]

    for i, entry in enumerate(entries[:5], 1):
        response_parts.append(f"\n**{i}.** {entry}")

    response_parts.append(
        "\n\n*Note: This is a demo response. Configure LLM_PROVIDER=openai or LLM_PROVIDER=ollama "
        "in your .env file for AI-powered analysis and recommendations.*"
    )

    return "\n".join(response_parts)


class RAGService:
    """
    RAG service that combines vector search with LLM generation
    for intelligent resource allocation queries.
    """

    def __init__(self):
        self.vs = VectorStoreService()
        self.provider, self.client = _get_llm_client()

    def query(
        self,
        question: str,
        n_context_docs: int = 5,
        filter_type: Optional[str] = None,
        filter_bench: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Process a natural language query using RAG.

        Args:
            question: The user's natural language question
            n_context_docs: Number of context documents to retrieve
            filter_type: Filter documents by type ("resource" or "project")
            filter_bench: If True, only retrieve bench resources

        Returns:
            Dict with 'answer', 'sources', and 'context_used'
        """
        # 1. Retrieve relevant documents from vector store
        docs = self.vs.search(
            query=question,
            n_results=n_context_docs,
            filter_type=filter_type,
            filter_bench=filter_bench,
        )

        # 2. Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"{i}. {doc['content']}")

        context = "\n".join(context_parts)

        # 3. Generate answer using LLM (or demo mode)
        answer = _call_llm(self.provider, self.client, context, question)

        return {
            "answer": answer,
            "sources": docs,
            "context_used": len(docs),
            "llm_provider": self.provider,
        }

    def recommend_resources(
        self,
        project_requirements: str,
        required_skills: List[str],
        team_size: int = 1,
        n_candidates: int = 10,
    ) -> Dict[str, Any]:
        """
        Recommend resources for a project based on requirements.

        Args:
            project_requirements: Natural language description of the project
            required_skills: List of required skills
            team_size: Number of resources needed
            n_candidates: Number of candidates to consider

        Returns:
            Dict with recommendations and reasoning
        """
        skills_str = ", ".join(required_skills)
        query = (
            f"Find available resources with skills in {skills_str} "
            f"for: {project_requirements}. "
            f"Looking for {team_size} team member(s)."
        )

        # Search for bench resources specifically
        bench_docs = self.vs.search(
            query=query,
            n_results=n_candidates,
            filter_type="resource",
            filter_bench=True,
        )

        # Also search all resources if bench doesn't have enough
        if len(bench_docs) < team_size:
            all_docs = self.vs.search(
                query=query,
                n_results=n_candidates,
                filter_type="resource",
            )
        else:
            all_docs = bench_docs

        context_parts = []
        if bench_docs:
            context_parts.append("=== Available Bench Resources ===")
            for i, doc in enumerate(bench_docs, 1):
                context_parts.append(f"{i}. {doc['content']}")

        if all_docs and all_docs != bench_docs:
            context_parts.append("\n=== All Resources (including allocated) ===")
            for i, doc in enumerate(all_docs[:5], 1):
                context_parts.append(f"{i}. {doc['content']}")

        context = "\n".join(context_parts)

        recommendation_query = (
            f"Recommend the best {team_size} resource(s) from the available candidates "
            f"for a project requiring: {project_requirements}. "
            f"Required skills: {skills_str}. "
            f"Prioritize bench resources (immediately available). "
            f"Explain why each recommended resource is a good fit."
        )

        answer = _call_llm(self.provider, self.client, context, recommendation_query)

        return {
            "recommendation": answer,
            "bench_candidates": bench_docs,
            "all_candidates": all_docs,
            "team_size_requested": team_size,
            "llm_provider": self.provider,
        }
