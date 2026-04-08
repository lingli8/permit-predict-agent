import chromadb


class PermitRAGRetriever:
    def __init__(self, db_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="permit_corrections",
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, query: str, n_results: int = 5, filters: dict = None) -> dict:
        """Semantic search with optional metadata filtering by review_type."""
        where_filter = None
        if filters and filters.get("review_type"):
            where_filter = {"review_type": filters["review_type"]}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )
        return results

    def count(self) -> int:
        return self.collection.count()
