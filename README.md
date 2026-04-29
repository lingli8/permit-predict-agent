# PermitPredict Agent

AI agent system for Seattle construction permit advisory,  
built with LangGraph, RAG, and FastAPI.

An extension of [PermitPredict](https://permitpredict.vercel.app) —  
1st Place winner at the City of Seattle PACT-Athon.

---

## What it does

Answers permit-related questions using multi-step reasoning:

- **Semantic search** over 992 historical correction comments
- **ML prediction** for permit approval timeline and delay risk  
- **Requirements lookup** by permit type and review category

The agent classifies each query, selects the right tools,  
and loops until it has a complete answer (max 5 tool calls per turn).

---

## Architecture

```
User query
    │
    ▼
FastAPI endpoint
    │
    ▼
LangGraph Agent
    ├── Tool 1: RAG (ChromaDB semantic search)
    ├── Tool 2: ML prediction API
    └── Tool 3: Rule-based requirements lookup
    │
    ▼
Structured JSON response
(response · tools_used · sources with provenance)
```

---

## Key metrics

| Metric | Result |
|---|---|
| Retrieval precision@5 | 80% across 20 eval queries |
| Fire & Zoning accuracy | 100% |
| Permit comments indexed | 992 → 56 embedding-ready docs |
| Max tool calls per turn | 5 (guardrail) |

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph |
| Vector database | ChromaDB |
| Embeddings | Sentence-Transformers |
| LLM | Anthropic Claude API |
| API layer | FastAPI + Pydantic |
| ML model | XGBoost + Random Forest |

---

## Project structure

```
permit-predict-agent/
├── agent/          # LangGraph agent + tool routing logic
├── api/            # FastAPI endpoints + Pydantic models
├── rag/            # RAG pipeline + ChromaDB ingestion
├── data/           # Permit correction comments dataset
├── tests/          # Retrieval evaluation (20 test queries)
├── .env.example    # Required environment variables
└── requirements.txt
```

---

## Getting started

```bash
# Clone the repo
git clone https://github.com/lingli8/permit-predict-agent.git
cd permit-predict-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run the API
uvicorn api.main:app --reload
```

---

## Related

- [PermitPredict (original)](https://permitpredict.vercel.app) — full-stack ML app
- [City of Seattle Innovation Blog](https://lnkd.in/eSG9H7Pn) — featured coverage
- [LinkedIn](https://linkedin.com/in/lingli-yang-74430a383)
