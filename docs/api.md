# API

## POST /chat
Request: `{ "message": string, "session_id": string }`

Response:
```json
{
  "answer": "string",
  "mode": "agent | retrieval-only | error",
  "tool_calls": ["search_knowledge", "..."],
  "retrieval_trace": [{ "tool": "...", "args": {}, "results": [], "trace": {} }],
  "memory_hits": [{ "score": 0.0, "question": "...", "summary": "..." }],
  "latency_ms": 0
}
```

## POST /ingest
Re-indexes `data/club_docs.json` into the `club_knowledge` collection.

## GET /health
`{ "status": "ok", "gemini": true, "collections": { "club_knowledge": 299, "agent_memory": N } }`
