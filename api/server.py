"""
FastAPI server exposing the LangGraph agent over HTTP.

Run:
    uvicorn api.server:api --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.graph import app as agent_app

api = FastAPI(title="PermitPredict Agent API", version="1.0.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    tools_used: list[str]
    sources: list[dict]


@api.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    try:
        result = agent_app.invoke(
            {
                "messages": [HumanMessage(content=request.message)],
                "permit_context": {},
                "search_results": [],
                "prediction_result": {},
                "requirements": [],
            },
            config=config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages = result["messages"]

    # Extract final AI response text
    ai_response = ""
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            ai_response = m.content if isinstance(m.content, str) else str(m.content)
            break

    # Collect tool names that were called
    tools_used = []
    sources = []
    for m in messages:
        if isinstance(m, AIMessage) and hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tools_used.append(tc["name"])
        if isinstance(m, ToolMessage):
            sources.append({"tool": m.name, "content": m.content[:200]})

    return ChatResponse(response=ai_response, tools_used=tools_used, sources=sources)


@api.get("/health")
async def health():
    return {"status": "ok"}
