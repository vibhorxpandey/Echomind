# DECISIONS.md — defaults chosen without asking

- **Python 3.14 instead of 3.11**: the machine has Python 3.14.3 and no 3.11. Using 3.14; all pinned deps install cleanly on it. (Will note here if anything had to change because of this.)
- **No Docker on this machine**: Qdrant client resolution order is (1) `QDRANT_URL` env → Qdrant Cloud, (2) `localhost:6333` if reachable → local Docker, (3) **embedded local mode** (`QdrantClient(path="qdrant_local_data/")`) — no server needed, fully supported by qdrant-client including the Query API with RRF fusion. The demo runs out of the box with zero infra.
- **Embedded-mode single-process constraint**: qdrant embedded mode locks its data dir, so ingestion happens inside the backend process (on startup if collections are missing, or via `POST /ingest`), not as a separate long-running process.
- **No chunking**: dataset documents are 150–400 words — each doc is embedded whole as one point. Chunking would add complexity with no retrieval benefit at this size.
- **Reranker**: `jinaai/jina-reranker-v1-tiny-en` via fastembed `TextCrossEncoder` (CPU-fast).
- **agent_memory is dense-only**: memory summaries are short paraphrases; hybrid search adds nothing there. `club_knowledge` is the hybrid collection.
- **Answer fallback without GOOGLE_API_KEY**: if no Gemini key is set, `/chat` still works — it runs the full retrieval pipeline and returns an extractive answer built from top chunks, clearly labeled `"mode": "retrieval-only"`. This keeps the retrieval-trace demo alive even if the key dies on stage.
- **Dataset determinism**: `random.seed(42)`, no LLM calls; generated JSON is committed at `data/club_docs.json`.
- **Fictional entities**: Nexus Tech Club at "Kaveri Institute of Technology" (fictional), fictional people and sponsors throughout.
- **Dev-up script**: `run.ps1` (Windows-native) and `run.sh` (Git Bash) — both install-if-needed, ingest-if-needed, then start backend (:8000) and frontend (:3000).
- **ADK session service**: `InMemorySessionService` — conversation state resets on server restart, but long-term memory survives via the `agent_memory` Qdrant collection (that's the point of the feature).
