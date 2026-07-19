"""
Vector store service using ChromaDB for semantic search.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Manages ChromaDB vector store for resources and projects."""

    def __init__(self):
        self._client = None
        self._collection = None
        self._embeddings = None
        self._initialized = False

    def _initialize(self):
        """Lazily initialize ChromaDB and embedding model."""
        if self._initialized:
            return

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            from app.config import settings

            self._embeddings = SentenceTransformer(settings.embedding_model)
            self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._initialized = True
            logger.info("VectorStoreService initialized successfully")
        except ImportError as e:
            logger.warning(f"ChromaDB/sentence-transformers not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {e}")

    def _embed(self, text: str) -> List[float]:
        """Create embedding for a text string."""
        return self._embeddings.encode(text).tolist()

    def add_resource(self, resource) -> None:
        """Add a resource document to the vector store."""
        self._initialize()
        if not self._initialized:
            return

        doc_id = f"resource_{resource.id}"
        text = resource.to_document_string()
        embedding = self._embed(text)

        self._collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "type": "resource",
                "resource_id": str(resource.id),
                "name": resource.name,
                "department": resource.department,
                "is_on_bench": str(resource.is_on_bench),
                "skills": ",".join(resource.skills) if resource.skills else "",
            }],
        )

    def update_resource(self, resource) -> None:
        """Update a resource document in the vector store."""
        self.add_resource(resource)  # Upsert handles update

    def delete_resource(self, resource_id: int) -> None:
        """Delete a resource from the vector store."""
        self._initialize()
        if not self._initialized:
            return
        try:
            self._collection.delete(ids=[f"resource_{resource_id}"])
        except Exception as e:
            logger.warning(f"Could not delete resource {resource_id} from vector store: {e}")

    def add_project(self, project) -> None:
        """Add a project document to the vector store."""
        self._initialize()
        if not self._initialized:
            return

        doc_id = f"project_{project.id}"
        text = project.to_document_string()
        embedding = self._embed(text)

        self._collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "type": "project",
                "project_id": str(project.id),
                "name": project.name,
                "client": project.client,
                "status": project.status,
                "required_skills": ",".join(project.required_skills) if project.required_skills else "",
            }],
        )

    def update_project(self, project) -> None:
        """Update a project document in the vector store."""
        self.add_project(project)

    def delete_project(self, project_id: int) -> None:
        """Delete a project from the vector store."""
        self._initialize()
        if not self._initialized:
            return
        try:
            self._collection.delete(ids=[f"project_{project_id}"])
        except Exception as e:
            logger.warning(f"Could not delete project {project_id} from vector store: {e}")

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_type: Optional[str] = None,
        filter_bench: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over resources and projects.

        Args:
            query: Natural language search query
            n_results: Number of results to return
            filter_type: Filter by document type ("resource" or "project")
            filter_bench: If True, only return bench resources

        Returns:
            List of matching documents with metadata
        """
        self._initialize()
        if not self._initialized:
            return []

        try:
            query_embedding = self._embed(query)
            conditions = []

            if filter_type:
                conditions.append({"type": {"$eq": filter_type}})

            if filter_bench is not None:
                conditions.append({"is_on_bench": {"$eq": str(filter_bench)}})

            where_filter = None
            if len(conditions) == 1:
                where_filter = conditions[0]
            elif len(conditions) > 1:
                # Chroma expects one top-level operator when combining metadata filters.
                where_filter = {"$and": conditions}

            kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": min(n_results, self._collection.count() or 1),
                "include": ["documents", "metadatas", "distances"],
            }
            if where_filter is not None:
                kwargs["where"] = where_filter

            results = self._collection.query(**kwargs)

            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "score": 1.0 - (results["distances"][0][i] if results.get("distances") else 0),
                    })

            return documents

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def get_collection_count(self) -> int:
        """Get the total number of documents in the vector store."""
        self._initialize()
        if not self._initialized:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def rebuild_index(self, resources: List, projects: List) -> int:
        """Rebuild the entire vector store index from scratch."""
        self._initialize()
        if not self._initialized:
            return 0

        count = 0
        for resource in resources:
            try:
                self.add_resource(resource)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to index resource {resource.id}: {e}")

        for project in projects:
            try:
                self.add_project(project)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to index project {project.id}: {e}")

        return count
