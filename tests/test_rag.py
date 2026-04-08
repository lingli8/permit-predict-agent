"""
Quick smoke test: compare rule-based vs semantic search on the same query.

Run:
    python -m tests.test_rag
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.retriever import PermitRAGRetriever

# Simulated rule-based lookup (mirrors v8 identifyReviewTypes logic)
RULE_BASED_MAP = {
    ("R-1", "Addition", "high"): ["ECA/GeoTech", "Structural", "Drainage"],
    ("R-1", "New Building", "high"): ["ECA/GeoTech", "Structural", "Drainage", "SEPA"],
    ("C-1", "Addition", "medium"): ["Structural", "Land Use"],
}


def rule_based_lookup(permit_class: str, permit_type: str, cost: float) -> list[str]:
    cost_range = "high" if cost >= 500_000 else "medium" if cost >= 100_000 else "low"
    return RULE_BASED_MAP.get((permit_class, permit_type, cost_range), ["General"])


def main():
    retriever = PermitRAGRetriever()
    print(f"ChromaDB has {retriever.count()} documents\n")

    query = "What corrections are common for a $500K residential addition?"

    print("=== Rule-based ===")
    rule_results = rule_based_lookup("R-1", "Addition", 500_000)
    print(rule_results)

    print("\n=== Semantic search (RAG) ===")
    rag_results = retriever.search(query, n_results=5)
    if rag_results["documents"] and rag_results["documents"][0]:
        for doc, meta in zip(rag_results["documents"][0], rag_results["metadatas"][0]):
            print(f"[{meta['review_type']}] {doc[:120]}...")
    else:
        print("No results — have you run python -m rag.ingest yet?")


if __name__ == "__main__":
    main()
