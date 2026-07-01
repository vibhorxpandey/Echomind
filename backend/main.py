"""EchoMind FastAPI backend.

POST /chat   {message, session_id?} -> answer + retrieval trace + memory hits
POST /ingest -> re-index the dataset into club_knowledge
GET  /health -> status + collection counts
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import agent as ag
from backend.config import KNOWLEDGE_COLLECTION, MEMORY_COLLECTION, get_qdrant_client, log
from backend.lyzr_integration import notify_lyzr
from backend.memory import ensure_memory_collection, recall_memory, store_memory
from backend.retrieval import ingest_documents, knowledge_ready, warm_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    warm_models()
    ensure_memory_collection()
    if not knowledge_ready():
        log.info("club_knowledge empty - ingesting dataset on startup...")
        ingest_documents()
    log.info("EchoMind backend ready. Gemini: %s",
             "available" if ag.gemini_available() else "NOT SET (retrieval-only mode)")
    yield


app = FastAPI(title="EchoMind", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"], allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.get("/health")
def health():
    client = get_qdrant_client()
    counts = {}
    for coll in (KNOWLEDGE_COLLECTION, MEMORY_COLLECTION):
        try:
            counts[coll] = client.count(coll).count
        except Exception:
            counts[coll] = None
    return {"status": "ok", "gemini": ag.gemini_available(), "collections": counts}


@app.post("/ingest")
def ingest():
    n = ingest_documents()
    return {"status": "ok", "documents_indexed": n}


@app.post("/chat")
async def chat(req: ChatRequest):
    t0 = time.time()
    ag.reset_turn_buffers()

    # Long-term memory: surface relevant past conversations before answering.
    pre_memories = recall_memory(req.message, top_k=2)
    message = req.message
    if pre_memories:
        ctx = "\n".join(f"- {m['summary']}" for m in pre_memories)
        message = (f"{req.message}\n\n[Long-term memory: you discussed related topics "
                   f"before. Use only to understand what the user refers to - you must "
                   f"still verify all facts with your search tools this turn:\n{ctx}]")

    mode, tool_calls = "agent", []
    if ag.gemini_available():
        try:
            answer, tool_calls = await ag.run_agent(message, req.session_id)
            if not answer.strip():
                raise RuntimeError("empty agent response")
        except Exception as e:
            log.warning("Agent failed (%s) - falling back to retrieval-only.", e)
            mode = "retrieval-only"
            answer = ag.extractive_fallback(req.message)
    else:
        mode = "retrieval-only"
        answer = ag.extractive_fallback(req.message)

    store_memory(req.message, answer, req.session_id)
    notify_lyzr(req.message, answer)

    return {
        "answer": answer,
        "mode": mode,
        "tool_calls": tool_calls,
        "retrieval_trace": ag.TRACE,
        "memory_hits": pre_memories + ag.MEMORY_HITS,
        "latency_ms": int((time.time() - t0) * 1000),
    }
