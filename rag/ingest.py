"""
Ingests correction_comments.json into ChromaDB.

Run:
    python -m rag.ingest
"""
import json
import chromadb


def ingest_comments(data_path: str = "data/correction_comments.json", db_path: str = "./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(
        name="permit_corrections",
        metadata={"hnsw:space": "cosine"},
    )

    with open(data_path) as f:
        comments = json.load(f)

    # ChromaDB upsert — safe to re-run
    collection.upsert(
        ids=[c["id"] for c in comments],
        documents=[c["content"] for c in comments],
        metadatas=[c["metadata"] for c in comments],
    )
    print(f"Ingested {len(comments)} comments into ChromaDB (collection: permit_corrections)")


if __name__ == "__main__":
    ingest_comments()
