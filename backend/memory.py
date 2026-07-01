"""Long-term agent memory: Qdrant collection "agent_memory".

After every /chat turn we embed a summary of (question + answer) and store it.
Before answering, the pipeline (and the recall_conversation tool) searches this
collection so the agent remembers past conversations across sessions/restarts.
Dense-only — memory summaries are short paraphrases, hybrid adds nothing here.
"""

import time
import uuid

from qdrant_client import models

from backend.config import DENSE_DIM, MEMORY_COLLECTION, get_qdrant_client, log
from backend.retrieval import dense_model


def ensure_memory_collection() -> None:
    client = get_qdrant_client()
    if not client.collection_exists(MEMORY_COLLECTION):
        client.create_collection(
            collection_name=MEMORY_COLLECTION,
            vectors_config={"dense": models.VectorParams(size=DENSE_DIM, distance=models.Distance.COSINE)},
        )
        log.info("Created memory collection %s", MEMORY_COLLECTION)


def store_memory(question: str, answer: str, session_id: str = "default") -> None:
    ensure_memory_collection()
    summary = f"User asked: {question}\nEchoMind answered: {answer[:700]}"
    vec = next(dense_model().passage_embed([summary])).tolist()
    get_qdrant_client().upsert(
        MEMORY_COLLECTION,
        points=[models.PointStruct(
            id=str(uuid.uuid4()),
            vector={"dense": vec},
            payload={"question": question, "summary": summary,
                     "session_id": session_id, "timestamp": time.time()},
        )],
        wait=True,
    )


def recall_memory(query: str, top_k: int = 3, min_score: float = 0.55) -> list[dict]:
    ensure_memory_collection()
    vec = next(dense_model().query_embed(query)).tolist()
    points = get_qdrant_client().query_points(
        MEMORY_COLLECTION, query=vec, using="dense", limit=top_k, with_payload=True,
    ).points
    return [
        {"score": round(p.score, 4), "question": p.payload.get("question", ""),
         "summary": p.payload.get("summary", ""), "timestamp": p.payload.get("timestamp")}
        for p in points if p.score >= min_score
    ]
