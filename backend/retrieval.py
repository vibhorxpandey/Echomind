"""Hybrid retrieval pipeline: fastembed dense+sparse -> Qdrant RRF fusion -> cross-encoder rerank.

One collection ("club_knowledge") with named vectors:
  dense  : BAAI/bge-small-en-v1.5 (384-dim, cosine)
  sparse : Qdrant/bm25 (IDF modifier)

hybrid_search() returns top_k reranked results plus a full retrieval trace
(fused rank/score, rerank score, rank delta) — the payload behind the UI sidebar.
"""

import json
import uuid
from functools import lru_cache

from fastembed import SparseTextEmbedding, TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder
from qdrant_client import models

from backend.config import (
    DATASET_PATH,
    DENSE_DIM,
    DENSE_MODEL,
    KNOWLEDGE_COLLECTION,
    RERANK_MODEL,
    SPARSE_MODEL,
    get_qdrant_client,
    log,
)


@lru_cache(maxsize=1)
def dense_model() -> TextEmbedding:
    log.info("Loading dense model %s ...", DENSE_MODEL)
    return TextEmbedding(DENSE_MODEL)


@lru_cache(maxsize=1)
def sparse_model() -> SparseTextEmbedding:
    log.info("Loading sparse model %s ...", SPARSE_MODEL)
    return SparseTextEmbedding(SPARSE_MODEL)


@lru_cache(maxsize=1)
def reranker() -> TextCrossEncoder:
    log.info("Loading reranker %s ...", RERANK_MODEL)
    return TextCrossEncoder(RERANK_MODEL)


def warm_models() -> None:
    dense_model(), sparse_model(), reranker()


def _point_id(doc_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, doc_id))


def knowledge_ready() -> bool:
    client = get_qdrant_client()
    try:
        return client.count(KNOWLEDGE_COLLECTION).count > 0
    except Exception:
        return False


def ingest_documents() -> int:
    """(Re)create club_knowledge and index the full dataset. Returns doc count."""
    client = get_qdrant_client()
    docs = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    if client.collection_exists(KNOWLEDGE_COLLECTION):
        client.delete_collection(KNOWLEDGE_COLLECTION)
    client.create_collection(
        collection_name=KNOWLEDGE_COLLECTION,
        vectors_config={
            "dense": models.VectorParams(size=DENSE_DIM, distance=models.Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
        },
    )

    texts = [f"{d['title']}. {d['content']}" for d in docs]
    log.info("Embedding %d documents (dense + sparse)...", len(docs))
    dense_vecs = list(dense_model().passage_embed(texts, batch_size=64))
    sparse_vecs = list(sparse_model().embed(texts, batch_size=64))

    points = [
        models.PointStruct(
            id=_point_id(d["id"]),
            vector={
                "dense": dense_vecs[i].tolist(),
                "sparse": models.SparseVector(
                    indices=sparse_vecs[i].indices.tolist(),
                    values=sparse_vecs[i].values.tolist(),
                ),
            },
            payload={
                "doc_id": d["id"], "title": d["title"], "doc_type": d["doc_type"],
                "year": d["year"], "date": d["date"], "author": d["author"],
                "content": d["content"],
            },
        )
        for i, d in enumerate(docs)
    ]
    client.upsert(KNOWLEDGE_COLLECTION, points=points, wait=True)
    log.info("Ingested %d docs into %s", len(points), KNOWLEDGE_COLLECTION)
    return len(points)


def _build_filter(doc_type: str | None = None, year: int | None = None):
    conditions = []
    if doc_type:
        conditions.append(models.FieldCondition(key="doc_type", match=models.MatchValue(value=doc_type)))
    if year:
        conditions.append(models.FieldCondition(key="year", match=models.MatchValue(value=int(year))))
    return models.Filter(must=conditions) if conditions else None


def _query_vectors(query: str):
    dense_q = next(dense_model().query_embed(query)).tolist()
    sq = next(sparse_model().query_embed(query))
    sparse_q = models.SparseVector(indices=sq.indices.tolist(), values=sq.values.tolist())
    return dense_q, sparse_q


def hybrid_search(
    query: str,
    doc_type: str | None = None,
    year: int | None = None,
    top_k: int = 5,
    prefetch_k: int = 20,
    mode: str = "hybrid_rerank",  # hybrid_rerank | hybrid | dense | sparse (ablation)
) -> dict:
    """Run retrieval and return {"results": [...], "trace": {...}}.

    Each result carries: doc_id, title, doc_type, year, date, author, content,
    fused_score, fused_rank, rerank_score, final_rank, rank_delta.
    """
    client = get_qdrant_client()
    flt = _build_filter(doc_type, year)
    dense_q, sparse_q = _query_vectors(query)

    if mode == "dense":
        res = client.query_points(
            KNOWLEDGE_COLLECTION, query=dense_q, using="dense",
            query_filter=flt, limit=top_k, with_payload=True,
        ).points
    elif mode == "sparse":
        res = client.query_points(
            KNOWLEDGE_COLLECTION, query=sparse_q, using="sparse",
            query_filter=flt, limit=top_k, with_payload=True,
        ).points
    else:
        res = client.query_points(
            KNOWLEDGE_COLLECTION,
            prefetch=[
                models.Prefetch(query=sparse_q, using="sparse", filter=flt, limit=prefetch_k),
                models.Prefetch(query=dense_q, using="dense", filter=flt, limit=prefetch_k),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=prefetch_k,
            with_payload=True,
        ).points

    candidates = [
        {**p.payload, "fused_score": round(p.score, 4), "fused_rank": i + 1,
         "rerank_score": None}
        for i, p in enumerate(res)
    ]

    if mode == "hybrid_rerank" and candidates:
        scores = list(reranker().rerank(query, [c["content"] for c in candidates]))
        for c, s in zip(candidates, scores):
            c["rerank_score"] = round(float(s), 4)
        candidates.sort(key=lambda c: c["rerank_score"], reverse=True)

    results = candidates[:top_k]
    for i, c in enumerate(results):
        c["final_rank"] = i + 1
        c["rank_delta"] = c["fused_rank"] - c["final_rank"]  # + means reranker promoted it

    return {
        "results": results,
        "trace": {
            "query": query,
            "mode": mode,
            "filters": {"doc_type": doc_type, "year": year},
            "candidates_considered": len(candidates),
            "top_k": top_k,
        },
    }
