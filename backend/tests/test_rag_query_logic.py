"""
Tests for RAG query confidence filtering.
"""

from app.services.rag_service import RAGService
from app.services.vector_store import VectorStoreService


def test_query_returns_no_reliable_matches_for_low_scores(monkeypatch):
    def fake_search(self, **kwargs):
        return [
            {"content": "Employee: A", "metadata": {"type": "resource", "name": "A"}, "score": 0.23},
            {"content": "Employee: B", "metadata": {"type": "resource", "name": "B"}, "score": 0.2},
        ]

    monkeypatch.setattr(VectorStoreService, "search", fake_search)

    service = RAGService()
    result = service.query("sdfsdfsfsdf", n_context_docs=5, user_role="user", username="user")

    assert result["context_used"] == 0
    assert result["sources"] == []
    assert "No reliable matches were found" in result["answer"]


def test_query_keeps_confident_matches_only(monkeypatch):
    def fake_search(self, **kwargs):
        return [
            {"content": "Employee: A", "metadata": {"type": "resource", "name": "A"}, "score": 0.52},
            {"content": "Employee: B", "metadata": {"type": "resource", "name": "B"}, "score": 0.21},
        ]

    monkeypatch.setattr(VectorStoreService, "search", fake_search)
    monkeypatch.setattr("app.services.rag_service._call_llm", lambda provider, client, context, query: "ok")

    service = RAGService()
    result = service.query("find python", n_context_docs=5, user_role="user", username="user")

    assert result["context_used"] == 1
    assert len(result["sources"]) == 1
    assert result["sources"][0]["metadata"]["name"] == "A"


def test_query_respects_top_n_intent(monkeypatch):
    def fake_search(self, **kwargs):
        return [
            {"content": "Employee: A", "metadata": {"type": "resource", "name": "A"}, "score": 0.9},
            {"content": "Employee: B", "metadata": {"type": "resource", "name": "B"}, "score": 0.8},
            {"content": "Employee: C", "metadata": {"type": "resource", "name": "C"}, "score": 0.7},
        ]

    monkeypatch.setattr(VectorStoreService, "search", fake_search)
    monkeypatch.setattr("app.services.rag_service._call_llm", lambda provider, client, context, query: "ok")

    service = RAGService()
    result = service.query("Find top 1 employee for Python", n_context_docs=5, user_role="user", username="user")

    assert result["context_used"] == 1
    assert len(result["sources"]) == 1
    assert result["sources"][0]["metadata"]["name"] == "A"
