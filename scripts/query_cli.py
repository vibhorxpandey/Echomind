"""CLI proof for the retrieval pipeline (M1/M2).

Usage:
  python scripts/query_cli.py --ingest
  python scripts/query_cli.py "why did HackNexus 2023 lose money?"
  python scripts/query_cli.py "fest timing" --mode dense --doc-type meeting_minutes --year 2024

Note: with embedded Qdrant, stop the backend server before running this
(single-process lock on qdrant_local_data/).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.retrieval import hybrid_search, ingest_documents  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default=None)
    ap.add_argument("--ingest", action="store_true")
    ap.add_argument("--mode", default="hybrid_rerank",
                    choices=["hybrid_rerank", "hybrid", "dense", "sparse"])
    ap.add_argument("--doc-type", default=None)
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()

    if args.ingest:
        n = ingest_documents()
        print(f"Ingested {n} documents.")
        if not args.query:
            return

    if not args.query:
        ap.error("provide a query or --ingest")

    out = hybrid_search(args.query, doc_type=args.doc_type, year=args.year,
                        top_k=args.top_k, mode=args.mode)
    print(f"\nQuery: {args.query}  (mode={args.mode})")
    print(f"Candidates considered: {out['trace']['candidates_considered']}\n")
    for r in out["results"]:
        delta = f"{r['rank_delta']:+d}" if r["rank_delta"] else "0"
        rr = f"{r['rerank_score']:.4f}" if r["rerank_score"] is not None else "  -  "
        print(f"#{r['final_rank']}  fused={r['fused_score']:.4f}  rerank={rr}  drank={delta}")
        print(f"    [{r['doc_type']} | {r['year']}] {r['title']}  (id={r['doc_id']})")
        print(f"    {r['content'][:140]}...\n")


if __name__ == "__main__":
    main()
