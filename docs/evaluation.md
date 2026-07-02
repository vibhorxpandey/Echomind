# Evaluation

`scripts/ablation.py` runs ~15 eval queries (each with expected source doc ids)
against three retrieval configs and prints a markdown table.

## Configs
- **sparse only** — BM25.
- **dense only** — bge-small-en-v1.5.
- **hybrid + rerank** — RRF fusion of both -> cross-encoder rerank.

## Metrics
- **Recall@5** — expected doc in top 5.
- **Recall@1** — expected doc ranked first.
- **MRR@5** — mean reciprocal rank.

At 299 docs Recall@5 saturates (sparse also hits it), so MRR is the discriminating
metric: hybrid+rerank ~0.967 vs dense ~0.922 vs sparse ~0.822.
