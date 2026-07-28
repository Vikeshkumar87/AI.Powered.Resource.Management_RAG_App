"""
Tests for admin document ingestion.
"""

from app.services.vector_store import VectorStoreService


def test_ingest_documents_indexes_chunks(client, monkeypatch):
    captured = []

    def fake_add_document_chunk(self, document_id, text, metadata, **kwargs):
        captured.append((document_id, text, metadata, kwargs))

    monkeypatch.setattr(VectorStoreService, "add_document_chunk", fake_add_document_chunk)

    response = client.post(
        "/api/v1/admin/ingest-documents",
        headers={"X-User-Role": "admin"},
        files=[
            (
                "files",
                (
                    "policy.txt",
                    b"This is a sample policy document used for ingestion testing.",
                    "text/plain",
                ),
            )
        ],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["files_processed"] == 1
    assert data["chunks_indexed"] == 1
    assert captured
    assert captured[0][0].startswith("doc_policy_")
    assert captured[0][3]["default_roles"] == "admin"
