"""
Evaluates RAG retrieval quality using precision@5.
Compares rule-based vs semantic search across test queries.

Run:
    python -m tests.eval_retrieval
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.retriever import PermitRAGRetriever

TEST_QUERIES = [
    {
        "query": "drainage issues for new construction",
        "expected_review_types": ["ECA/GeoTech", "Drainage"],
    },
    {
        "query": "structural concerns for high-cost renovation",
        "expected_review_types": ["Structural"],
    },
    {
        "query": "environmental critical area wetland buffer",
        "expected_review_types": ["ECA/GeoTech"],
    },
    {
        "query": "land use zoning FAR setback compliance",
        "expected_review_types": ["Zoning"],
    },
    {
        "query": "steep slope landslide geotechnical hazard assessment",
        "expected_review_types": ["ECA/GeoTech"],
    },
    {
        "query": "fire suppression sprinkler system requirement",
        "expected_review_types": ["Fire"],
    },
    {
        "query": "energy code compliance insulation mechanical equipment efficiency",
        "expected_review_types": ["Energy"],
    },
    {
        "query": "grading permit stormwater runoff impervious surface",
        "expected_review_types": ["Drainage", "ECA/GeoTech"],
    },
    {
        "query": "building permit corrections for residential addition structural",
        "expected_review_types": ["Structural"],
    },
    {
        "query": "heat pump HVAC ventilation mechanical review",
        "expected_review_types": ["Mechanical"],
    },
    {
        "query": "floor area ratio height setback zoning code",
        "expected_review_types": ["Zoning"],
    },
    {
        "query": "fire egress path width sprinkler life safety",
        "expected_review_types": ["Fire"],
    },
    {
        "query": "hold down anchor bolt shear wall lateral load",
        "expected_review_types": ["Structural"],
    },
    {
        "query": "side sewer connection stormwater infiltration SPU",
        "expected_review_types": ["Drainage"],
    },
    {
        "query": "restaurant kitchen Type I hood exhaust makeup air",
        "expected_review_types": ["Mechanical"],
    },
    {
        "query": "retaining wall geotechnical engineer stamp steep slope",
        "expected_review_types": ["ECA/GeoTech", "Structural"],
    },
    {
        "query": "lot coverage ADU accessory dwelling unit zoning",
        "expected_review_types": ["Zoning"],
    },
    {
        "query": "duct leakage testing WSEC COMcheck energy compliance",
        "expected_review_types": ["Energy"],
    },
    {
        "query": "fire truck turning radius access road fire department",
        "expected_review_types": ["Fire"],
    },
    {
        "query": "gas piping sizing BTU load mechanical",
        "expected_review_types": ["Mechanical"],
    },
]


def evaluate_retrieval(retriever: PermitRAGRetriever, queries: list[dict]) -> dict:
    results = {}
    for tq in queries:
        search_results = retriever.search(tq["query"], n_results=5)
        if not search_results["metadatas"] or not search_results["metadatas"][0]:
            results[tq["query"]] = {"precision@5": 0.0, "retrieved_types": []}
            continue

        retrieved_types = [m["review_type"] for m in search_results["metadatas"][0]]
        relevant = sum(1 for rt in retrieved_types if rt in tq["expected_review_types"])
        precision = relevant / 5

        results[tq["query"]] = {
            "precision@5": precision,
            "retrieved_types": retrieved_types,
            "expected": tq["expected_review_types"],
        }
    return results


def print_report(results: dict):
    precisions = [v["precision@5"] for v in results.values()]
    avg = sum(precisions) / len(precisions) if precisions else 0

    print(f"\n{'='*60}")
    print(f"RAG Retrieval Evaluation  (n={len(results)} queries)")
    print(f"Average precision@5: {avg:.2%}")
    print(f"{'='*60}\n")

    for query, r in results.items():
        p = r["precision@5"]
        mark = "✓" if p >= 0.4 else "✗"
        print(f"{mark} [{p:.0%}] {query[:60]}")
        print(f"      expected:  {r['expected']}")
        print(f"      retrieved: {r['retrieved_types']}\n")


if __name__ == "__main__":
    retriever = PermitRAGRetriever()
    if retriever.count() == 0:
        print("ChromaDB is empty. Run: python -m rag.ingest")
        sys.exit(1)

    results = evaluate_retrieval(retriever, TEST_QUERIES)
    print_report(results)
