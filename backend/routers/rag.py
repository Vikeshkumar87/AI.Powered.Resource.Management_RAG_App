from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.rag_service import query_rag

router = APIRouter(prefix="/api/rag", tags=["RAG"])


class RAGQuery(BaseModel):
    query: str
    top_k: int = 3


@router.post("/query")
async def rag_query(request: RAGQuery):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    result = await query_rag(request.query, request.top_k)
    return result
