from langchain_core.tools import tool
from rag.retriever import PermitRAGRetriever

retriever = PermitRAGRetriever()


@tool
def permit_search(query: str, review_type: str = None) -> str:
    """Search the permit correction knowledge base for relevant information.
    Use this when the user asks about common issues, corrections, or delays
    for specific permit types."""
    filters = {"review_type": review_type} if review_type else None
    results = retriever.search(query, n_results=5, filters=filters)

    if not results["documents"] or not results["documents"][0]:
        return "No relevant permit correction information found."

    formatted = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        formatted.append(f"[{meta['review_type']}] {doc}")

    return "\n\n".join(formatted)
