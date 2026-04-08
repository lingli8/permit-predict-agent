"""
End-to-end agent tests covering single-tool and multi-tool reasoning.
Also tests multi-turn memory (context carries across turns).

Run:
    python -m tests.test_agent
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import app

SEP = "=" * 60


def run_turn(state_seed: dict, config: dict, label: str) -> dict:
    print(f"\n{SEP}\n{label}\n{SEP}")
    result = app.invoke(state_seed, config=config)
    last = [m for m in result["messages"] if isinstance(m, AIMessage)][-1]
    tools_called = [
        tc["name"]
        for m in result["messages"]
        if hasattr(m, "tool_calls") and m.tool_calls
        for tc in m.tool_calls
    ]
    print(f"Tools called : {tools_called}")
    print(f"Response     :\n{last.content[:600]}")
    return result


def test_single_tool():
    """Simple question — should only call permit_search."""
    config = {"configurable": {"thread_id": "test_single"}}
    run_turn(
        {
            "messages": [HumanMessage(content="What corrections are most common for ECA reviews?")],
            "permit_context": {},
            "search_results": [],
            "prediction_result": {},
            "requirements": [],
        },
        config,
        "TEST 1 — Single tool (permit_search)",
    )


def test_multi_tool():
    """Complex question — should trigger get_requirements + permit_search."""
    config = {"configurable": {"thread_id": "test_multi"}}
    run_turn(
        {
            "messages": [HumanMessage(content=(
                "I want to build a new house in Seattle, budget around $800K. "
                "What permits do I need and what are the most common correction issues?"
            ))],
            "permit_context": {},
            "search_results": [],
            "prediction_result": {},
            "requirements": [],
        },
        config,
        "TEST 2 — Multi-tool (get_requirements + permit_search)",
    )


def test_memory():
    """Two-turn conversation — second turn should remember first turn context."""
    config = {"configurable": {"thread_id": "test_memory"}}
    seed = {
        "messages": [],
        "permit_context": {},
        "search_results": [],
        "prediction_result": {},
        "requirements": [],
    }

    # Turn 1
    seed["messages"] = [HumanMessage(content="What are common structural corrections for a new building?")]
    run_turn(seed, config, "TEST 3a — Memory turn 1")

    # Turn 2 — agent should know we're talking about structural corrections
    run_turn(
        {"messages": [HumanMessage(content="What about drainage? How does it compare?")]},
        config,
        "TEST 3b — Memory turn 2 (agent should remember context from turn 1)",
    )


if __name__ == "__main__":
    test_single_tool()
    test_multi_tool()
    test_memory()
    print(f"\n{SEP}\nAll tests complete.\n{SEP}")
