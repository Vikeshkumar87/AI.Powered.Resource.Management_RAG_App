"""
RAG query and recommendation API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG - AI Queries"])


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Natural language question about resources or projects",
        json_schema_extra={"example": "Who are the Python developers currently on the bench?"},
    )
    n_context_docs: int = Field(default=5, ge=1, le=20, description="Number of context docs to use")
    filter_type: Optional[str] = Field(
        None,
        description="Filter by 'resource' or 'project'",
    )
    filter_bench: Optional[bool] = Field(
        None,
        description="If True, only search bench resources",
    )


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    context_used: int
    llm_provider: str


class RecommendRequest(BaseModel):
    project_requirements: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language description of the project requirements",
        json_schema_extra={"example": "Need a senior backend developer for a 6-month FinTech microservices project"},
    )
    required_skills: List[str] = Field(
        default=[],
        description="List of required skills",
        json_schema_extra={"example": ["Python", "FastAPI", "PostgreSQL", "Docker"]},
    )
    team_size: int = Field(default=1, ge=1, le=50, description="Number of resources needed")
    n_candidates: int = Field(default=10, ge=1, le=30, description="Number of candidates to consider")


class RecommendResponse(BaseModel):
    recommendation: str
    bench_candidates: List[Dict[str, Any]]
    all_candidates: List[Dict[str, Any]]
    team_size_requested: int
    llm_provider: str


def _get_rag_service() -> RAGService:
    return RAGService()


@router.post("/query", response_model=QueryResponse)
def query_resources(
    request: QueryRequest,
    rag: RAGService = Depends(_get_rag_service),
):
    """
    Ask a natural language question about resources and projects.

    Examples:
    - "Who are the available Python developers on the bench?"
    - "Show me all resources with more than 5 years of experience"
    - "Which projects need React developers?"
    - "Find cloud architects available for a new project"
    """
    try:
        result = rag.query(
            question=request.question,
            n_context_docs=request.n_context_docs,
            filter_type=request.filter_type,
            filter_bench=request.filter_bench,
        )
        return QueryResponse(
            question=request.question,
            **result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/recommend", response_model=RecommendResponse)
def recommend_resources(
    request: RecommendRequest,
    rag: RAGService = Depends(_get_rag_service),
):
    """
    Get AI-powered resource recommendations for a project.

    Provide project requirements and required skills to get intelligent
    recommendations from available (bench) resources, with reasoning
    for why each candidate is a good fit.
    """
    try:
        result = rag.recommend_resources(
            project_requirements=request.project_requirements,
            required_skills=request.required_skills,
            team_size=request.team_size,
            n_candidates=request.n_candidates,
        )
        return RecommendResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/search")
def semantic_search(
    q: str = Query(..., min_length=3, description="Search query"),
    n: int = Query(5, ge=1, le=20, description="Number of results"),
    type: Optional[str] = Query(None, description="Filter by 'resource' or 'project'"),
    bench_only: bool = Query(False, description="Only return bench resources"),
    rag: RAGService = Depends(_get_rag_service),
):
    """
    Perform semantic search over resources and projects.

    Returns ranked results based on semantic similarity to the query,
    not just keyword matching.
    """
    try:
        docs = rag.vs.search(
            query=q,
            n_results=n,
            filter_type=type,
            filter_bench=True if bench_only else None,
        )
        return {
            "query": q,
            "results": docs,
            "total_found": len(docs),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
