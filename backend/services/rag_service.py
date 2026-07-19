"""
RAG service: retrieves top-K similar employee profiles via FAISS,
then asks an LLM to generate ranked recommendations with justifications.
"""
import json
from openai import AsyncOpenAI
from backend.config import settings
from backend.services.embedding_service import search_similar_employees

_client: AsyncOpenAI = None


def _get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


def _build_context(candidates: list[dict]) -> str:
    lines = []
    for i, emp in enumerate(candidates, 1):
        skills = ", ".join(emp.get("skills", []))
        certs = ", ".join(emp.get("certifications", []))
        lines.append(
            f"{i}. {emp['name']} (ID: {emp['employee_id']})\n"
            f"   Skills: {skills}\n"
            f"   Experience: {emp['experience_years']} years | Domain: {emp['domain']}\n"
            f"   Certifications: {certs}\n"
            f"   Availability: {emp['availability']} | Utilization: {emp['utilization_percent']}%\n"
            f"   Similarity Score: {emp.get('similarity_score', 0)}%\n"
            f"   Resume: {emp.get('resume_text', '')[:300]}...\n"
        )
    return "\n".join(lines)


SYSTEM_PROMPT = """You are an expert AI Resource Manager. 
Your job is to recommend the best-fit employees for a staffing request based on 
the candidate profiles provided. 

For each recommended employee, provide:
- Match score (0-100%)
- Key reasons for the match
- Any skill gaps compared to the request
- Upskilling suggestions if gaps exist

Always respond in valid JSON with this structure:
{
  "recommendations": [
    {
      "employee_id": "...",
      "name": "...",
      "match_score": 92,
      "reasons": ["reason1", "reason2"],
      "skill_gaps": ["gap1"],
      "upskilling_suggestions": ["suggestion1"]
    }
  ],
  "summary": "Brief overall summary"
}"""


async def query_rag(query: str, top_k: int = 3) -> dict:
    # Step 1: Retrieve top-K similar employees from FAISS
    try:
        candidates = search_similar_employees(query, top_k=top_k + 2)
    except FileNotFoundError as e:
        return {"error": str(e), "recommendations": []}

    # Step 2: Filter to available or partial employees first
    available = [c for c in candidates if c.get("availability") in ("available", "partial")]
    if len(available) < top_k:
        available = candidates  # fallback to all if not enough available

    candidates_for_llm = available[:top_k + 2]
    context = _build_context(candidates_for_llm)

    user_message = (
        f"Staffing Request: {query}\n\n"
        f"Candidate Employee Profiles:\n{context}\n\n"
        f"Please recommend the top {top_k} best-fit employees from these candidates."
    )

    # Step 3: Call LLM
    try:
        client = _get_openai_client()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
    except Exception as e:
        # Fallback: return structured results from FAISS scores without LLM
        result = _fallback_recommendations(candidates_for_llm, top_k, str(e))

    return result


def _fallback_recommendations(candidates: list[dict], top_k: int, error: str) -> dict:
    """Return FAISS-based recommendations without LLM when OpenAI is unavailable."""
    recommendations = []
    for emp in candidates[:top_k]:
        recommendations.append({
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "match_score": emp.get("similarity_score", 0),
            "reasons": [
                f"Skills: {', '.join(emp.get('skills', []))}",
                f"Experience: {emp['experience_years']} years in {emp['domain']}",
                f"Availability: {emp['availability']}",
            ],
            "skill_gaps": [],
            "upskilling_suggestions": [],
        })
    return {
        "recommendations": recommendations,
        "summary": f"Results based on semantic similarity (LLM unavailable: {error})",
    }
