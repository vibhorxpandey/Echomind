# EchoMind Architecture

```mermaid
flowchart TB
    U["👤 Club member"] --> FE["Next.js 14 UI<br/>chat pane + retrieval-trace sidebar"]
    FE -->|"POST /chat {message, session_id}"| API["FastAPI backend<br/>/chat · /ingest · /health"]

    API -->|"pre-answer recall"| MEM[("Qdrant: agent_memory<br/>dense bge-small 384-d")]
    API --> RUNNER["Google ADK Runner<br/>InMemorySessionService"]

    subgraph AGENT["ADK root agent · echomind"]
        LLM["Gemini 2.5 Flash<br/>(GOOGLE_API_KEY)"]
        T1["search_knowledge<br/>(query, doc_type?, year?)"]
        T2["get_member_info(name)"]
        T3["get_event_history(event)"]
        T4["recall_conversation(query)"]
        LLM --> T1 & T2 & T3 & T4
    end

    RUNNER --> AGENT

    subgraph RET["Hybrid retrieval pipeline (fastembed, CPU)"]
        QV["query embed:<br/>dense bge-small-en-v1.5<br/>sparse Qdrant/bm25"]
        FUSE["Qdrant Query API<br/>2× Prefetch → RRF fusion (top-20)"]
        RR["cross-encoder rerank<br/>jina-reranker-v1-tiny-en → top-5"]
        QV --> FUSE --> RR
    end

    T1 & T2 & T3 --> RET
    FUSE --> KB[("Qdrant: club_knowledge<br/>299 docs · named vectors dense+sparse")]
    T4 --> MEM

    API -->|"post-answer: store (Q+A) summary"| MEM
    API -.->|"fire-and-forget mirror<br/>(only if LYZR_API_KEY)"| LYZR["Lyzr Studio agent<br/>v3 inference API"]

    RET -->|"per-tool-call trace<br/>(fused + rerank scores, rank Δ)"| API
    API -->|"answer + retrieval_trace + memory_hits"| FE

    ING["data/generate_dataset.py<br/>seeded, deterministic, 299 docs"] -->|"POST /ingest / startup"| KB
```

## Data flow of one question

1. UI posts the message to `/chat`.
2. Backend searches `agent_memory` first; relevant past conversations are injected as
   context (long-term memory).
3. ADK runner passes the message to the Gemini-powered root agent, which decomposes it
   into one or more tool calls.
4. Each retrieval tool runs the hybrid pipeline: dense + sparse query embedding → Qdrant
   Query API with two prefetch branches → RRF fusion (top-20) → cross-encoder rerank
   (top-5). Every candidate's fused score, rerank score, and rank movement is appended
   to the turn's trace buffer.
5. The agent synthesizes an answer with title+year citations, contradiction flags, and
   past-failure warnings.
6. Backend stores a (Q+A) summary embedding into `agent_memory`, optionally mirrors the
   turn to Lyzr, and returns `{answer, retrieval_trace, memory_hits}` — the UI renders
   the trace sidebar from exactly what the agent saw.

## Qdrant collections

| Collection | Vectors | Contents |
|---|---|---|
| `club_knowledge` | named: `dense` (384-d cosine) + `sparse` (BM25, IDF modifier) | 299 club documents with payload: doc_id, title, doc_type, year, date, author, content |
| `agent_memory` | `dense` (384-d cosine) | one point per past conversation turn: question, summary, session_id, timestamp |

Client fallback chain: Qdrant Cloud (`QDRANT_URL`) → local docker (`localhost:6333`) →
embedded local mode (`qdrant_local_data/`, zero infra).
