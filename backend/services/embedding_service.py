"""
Embedding service: generates OpenAI embeddings for employee profiles
and persists a FAISS index to disk for similarity search.
"""
import os
import pickle
import numpy as np
import faiss
from openai import OpenAI
from backend.config import settings

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

_client: OpenAI = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def _embed_texts(texts: list[str]) -> np.ndarray:
    """Call OpenAI Embeddings API in batches and return float32 array."""
    client = _get_client()
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=batch)
        all_embeddings.extend([item.embedding for item in response.data])
    arr = np.array(all_embeddings, dtype="float32")
    # Normalise for cosine similarity via inner product
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.maximum(norms, 1e-10)


def build_employee_text(emp: dict) -> str:
    """Construct a rich text representation of an employee for embedding."""
    skills = ", ".join(emp.get("skills", []))
    certs = ", ".join(emp.get("certifications", []))
    return (
        f"Name: {emp.get('name', '')}. "
        f"Skills: {skills}. "
        f"Experience: {emp.get('experience_years', 0)} years. "
        f"Certifications: {certs}. "
        f"Domain: {emp.get('domain', '')}. "
        f"Availability: {emp.get('availability', '')}. "
        f"Utilization: {emp.get('utilization_percent', 0)}%. "
        f"Resume: {emp.get('resume_text', '')}"
    )


def build_and_save_index(employees: list[dict], index_path: str):
    """Generate OpenAI embeddings for all employees, save FAISS index + metadata."""
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    print(f"Generating OpenAI embeddings ({OPENAI_EMBEDDING_MODEL}) for {len(employees)} employees...")
    texts = [build_employee_text(e) for e in employees]
    embeddings = _embed_texts(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner Product on normalised vectors == cosine similarity
    index.add(embeddings)

    faiss.write_index(index, f"{index_path}.faiss")
    with open(f"{index_path}.pkl", "wb") as f:
        pickle.dump(employees, f)

    print(f"FAISS index saved → {index_path}.faiss ({len(employees)} vectors, dim={dim})")


def load_index(index_path: str):
    """Load FAISS index and employee metadata from disk."""
    index = faiss.read_index(f"{index_path}.faiss")
    with open(f"{index_path}.pkl", "rb") as f:
        employees = pickle.load(f)
    return index, employees


def search_similar_employees(query: str, top_k: int = 5) -> list[dict]:
    """Embed the query with OpenAI and return top-K most similar employees."""
    index_path = settings.faiss_index_path
    if not os.path.exists(f"{index_path}.faiss"):
        raise FileNotFoundError(
            "FAISS index not found. Run scripts/build_vector_store.py first."
        )

    index, employees = load_index(index_path)

    query_embedding = _embed_texts([query])  # shape (1, dim), already normalised

    scores, indices = index.search(query_embedding, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        emp = employees[idx].copy()
        emp["similarity_score"] = round(float(score) * 100, 1)
        results.append(emp)
    return results
