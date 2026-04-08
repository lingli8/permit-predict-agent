import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic

from agent.state import AgentState
from agent.tools.permit_search import permit_search
from agent.tools.predict_timeline import predict_timeline
from agent.tools.get_requirements import get_requirements
from agent.memory import memory

load_dotenv()

# --- Tools ---
tools = [permit_search, predict_timeline, get_requirements]

# --- LLM ---
llm = ChatAnthropic(
    model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
    temperature=0,
).bind_tools(tools)

# --- Guardrail: max tool calls per turn ---
MAX_TOOL_CALLS = 5


def agent_node(state: AgentState):
    """Agent decides what to do next based on conversation history."""
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState):
    """Route: if the last message has tool calls, run them; otherwise finish."""
    last_message = state["messages"][-1]

    # Count how many tool-call rounds have already happened
    tool_call_count = sum(
        1
        for m in state["messages"]
        if hasattr(m, "tool_calls") and m.tool_calls
    )
    if tool_call_count >= MAX_TOOL_CALLS:
        return END  # force stop — prevents infinite loops

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# --- Build graph ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END},
)
workflow.add_edge("tools", "agent")  # tool results feed back to agent

# Compile with short-term memory checkpointer
app = workflow.compile(checkpointer=memory)
