"""
Tests for RAG access filtering.
"""

from app.services.vector_store import VectorStoreService


class _FakeCollection:
    def count(self):
        return 3

    def query(self, **kwargs):
        return {
            "documents": [[
                "Employee: Public Resource",
                "Policy: Admin Only",
                "Project: Public Project",
            ]],
            "metadatas": [[
                {"type": "resource", "name": "Public Resource", "access_level": "public", "allowed_roles": "admin,user"},
                {"type": "document", "name": "Admin Only", "access_level": "admin", "allowed_roles": "admin"},
                {"type": "project", "name": "Public Project", "access_level": "public", "allowed_roles": "admin,user"},
            ]],
            "distances": [[0.1, 0.2, 0.3]],
        }


def test_vector_store_hides_admin_documents_for_standard_users():
    store = VectorStoreService()
    store._initialized = True
    store._collection = _FakeCollection()
    store._embed = lambda text: [0.1, 0.2, 0.3]

    results = store.search("test query", n_results=5, user_role="user", username="user")

    assert len(results) == 2
    assert all(item["metadata"]["type"] != "document" for item in results)


def test_vector_store_returns_admin_documents_for_admin_users():
    store = VectorStoreService()
    store._initialized = True
    store._collection = _FakeCollection()
    store._embed = lambda text: [0.1, 0.2, 0.3]

    results = store.search("test query", n_results=5, user_role="admin", username="admin")

    assert len(results) == 3
    assert any(item["metadata"]["type"] == "document" for item in results)


def test_rag_query_route_passes_role_to_service(client, monkeypatch):
    captured = {}

    class FakeRAG:
        def query(self, **kwargs):
            captured.update(kwargs)
            return {
                "answer": "ok",
                "sources": [],
                "context_used": 0,
                "llm_provider": "demo",
            }

    monkeypatch.setattr("app.routes.rag.RAGService", lambda: FakeRAG())

    response = client.post(
        "/api/v1/rag/query",
        headers={"X-User-Role": "user"},
        json={"question": "Who is available?"},
    )

    assert response.status_code == 200
    assert captured["user_role"] == "user"