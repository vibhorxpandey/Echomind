"""Retrieval ablation: sparse-only vs dense-only vs hybrid+rerank.

15 eval queries with expected source doc ids (the planted storylines).
Metric: recall@5 = share of queries with >=1 expected doc in the top 5.
Prints a markdown table to paste into the README.

Run with the backend STOPPED if using embedded Qdrant (single-process lock):
  .venv/Scripts/python.exe scripts/ablation.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.retrieval import hybrid_search  # noqa: E402

# (query, {acceptable expected doc_ids})
EVAL_SET: list[tuple[str, set[str]]] = [
    ("why did HackNexus 2023 lose money",
     {"s1-postmortem-hacknexus-2023", "s1-budget-hacknexus-2023"}),
    ("venue double-booking forced a last-minute move",
     {"s1-postmortem-hacknexus-2023", "s1-minutes-venue-clash-2023"}),
    ("sponsor pulled out five days before the event",
     {"s1-minutes-emergency-2023", "s1-postmortem-hacknexus-2023",
      "s2-email-techverse-silence-2024"}),
    ("what is the history with TechVerse Solutions",
     {"s2-email-techverse-thread-2024", "s2-email-techverse-silence-2024",
      "s2-handover-treasurer-2024"}),
    ("which sponsor should we never rely on",
     {"s2-handover-treasurer-2024", "s2-email-techverse-silence-2024"}),
    ("how do we get budget approvals faster from Prof. Mehra",
     {"s3-handover-secretary-2022", "s3-handover-treasurer-2023"}),
    ("submit requisitions before the 5th of the month with a one-page summary",
     {"s3-handover-secretary-2022", "s3-handover-treasurer-2023"}),
    ("why did club membership drop 40 percent",
     {"s4-minutes-agm-2025", "s4-review-membership-2024"}),
    ("decision to discontinue beginner workshops",
     {"s4-minutes-workshops-cut-2024", "s4-review-membership-2024"}),
    ("how first-years typically join the club and why sign-ups collapsed",
     {"s4-review-membership-2024", "s4-minutes-agm-2025"}),
    ("Cloudnine Devtools sponsorship Rs.50,000",
     {"s5-email-cloudnine-2025", "s5-postmortem-sponsor-2025",
      "s5-minutes-hacknexus-win-2025"}),
    ("what changed in the sponsor pitch between 2023 and 2025",
     {"s5-postmortem-sponsor-2025"}),
    ("largest sponsorship in club history milestone payments",
     {"s5-postmortem-sponsor-2025", "s5-email-cloudnine-2025",
      "s5-minutes-hacknexus-win-2025"}),
    ("when is the Nexus Annual Fest held",
     {"s6-festplan-march-2022", "s6-minutes-fest-moved-2024"}),
    ("why was the annual fest moved to September",
     {"s6-minutes-fest-moved-2024"}),
]

CONFIGS = [
    ("Sparse only (BM25)", "sparse"),
    ("Dense only (bge-small)", "dense"),
    ("Hybrid RRF + rerank", "hybrid_rerank"),
]


def run():
    rows = []
    per_query: dict[str, list[str]] = {}
    n = len(EVAL_SET)
    for label, mode in CONFIGS:
        r5 = r1 = 0
        mrr = 0.0
        marks = []
        for query, expected in EVAL_SET:
            out = hybrid_search(query, top_k=5, mode=mode)
            ids = [r["doc_id"] for r in out["results"]]
            first = next((i for i, d in enumerate(ids) if d in expected), None)
            if first is not None:
                r5 += 1
                mrr += 1.0 / (first + 1)
                r1 += first == 0
            marks.append(str(first + 1) if first is not None else ".")
        rows.append((label, r1, r5, mrr / n))
        per_query[label] = marks

    print("\nPer-query rank of first expected doc (. = not in top 5):")
    for label, marks in per_query.items():
        print(f"  {label:28s} {' '.join(marks)}")

    print("\nMarkdown table:\n")
    print("| Retrieval config | Recall@1 | Recall@5 | MRR@5 |")
    print("|---|---|---|---|")
    for label, r1, r5, mrr in rows:
        print(f"| {label} | {r1}/{n} ({r1 / n * 100:.0f}%) "
              f"| {r5}/{n} ({r5 / n * 100:.0f}%) | {mrr:.3f} |")
    print()


if __name__ == "__main__":
    run()
