# EchoMind Backend

FastAPI service wrapping the ADK agent + hybrid retrieval + long-term memory.

## Run
```bash
.venv/Scripts/python -m uvicorn backend.main:app --port 8000
```

## Endpoints
- `POST /chat`   -> `{answer, mode, tool_calls, retrieval_trace, memory_hits, latency_ms}`
- `POST /ingest` -> re-index the dataset into Qdrant
- `GET  /health` -> `{status, gemini, collections}`

## Modules
- `config.py`     — env + Qdrant client fallback (Cloud -> docker -> embedded)
- `retrieval.py`  — dense+sparse embed, RRF fusion, cross-encoder rerank
- `memory.py`     — agent_memory collection (store/recall past turns)
- `agent.py`      — ADK root agent, 4 tools, system instruction
- `main.py`       — FastAPI app + lifespan (ensure collections)
- `lyzr_integration.py` — optional fire-and-forget mirror
