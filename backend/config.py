"""Env loading and Qdrant client resolution (cloud -> local docker -> embedded)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

log = logging.getLogger("echomind")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

KNOWLEDGE_COLLECTION = "club_knowledge"
MEMORY_COLLECTION = "agent_memory"
DATASET_PATH = ROOT / "data" / "club_docs.json"

DENSE_MODEL = "BAAI/bge-small-en-v1.5"     # 384-dim
SPARSE_MODEL = "Qdrant/bm25"
RERANK_MODEL = "jinaai/jina-reranker-v1-tiny-en"
DENSE_DIM = 384

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Cloud (QDRANT_URL) -> local docker (localhost:6333) -> embedded local mode."""
    global _client
    if _client is not None:
        return _client

    url = os.getenv("QDRANT_URL", "").strip()
    if url:
        _client = QdrantClient(url=url, api_key=os.getenv("QDRANT_API_KEY") or None)
        log.info("Qdrant: connected to cloud at %s", url)
        return _client

    try:
        candidate = QdrantClient(url="http://localhost:6333", timeout=2)
        candidate.get_collections()
        _client = candidate
        log.info("Qdrant: connected to local docker at localhost:6333")
        return _client
    except Exception:
        pass

    local_path = ROOT / "qdrant_local_data"
    _client = QdrantClient(path=str(local_path))
    log.info("Qdrant: using embedded local mode at %s", local_path)
    return _client
