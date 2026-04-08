from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    permit_context: dict       # current permit info from the user
    search_results: list       # RAG retrieval results
    prediction_result: dict    # ML model prediction
    requirements: list         # permit requirements list
