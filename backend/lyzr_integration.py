"""Thin Lyzr integration (sponsor stack requirement).

If LYZR_API_KEY is set, each answered question is mirrored to a Lyzr agent for
an independent second-opinion summary (fire-and-forget, logged, never blocking).
If unset, this module no-ops with a single log line per call.
"""

import os
import threading

import httpx

from backend.config import log

LYZR_ENDPOINT = os.getenv("LYZR_ENDPOINT", "https://agent-prod.studio.lyzr.ai/v3/inference/chat/")
LYZR_AGENT_ID = os.getenv("LYZR_AGENT_ID", "")


def notify_lyzr(question: str, answer: str) -> None:
    """Mirror the turn to Lyzr in a daemon thread. Never raises, never blocks."""
    api_key = os.getenv("LYZR_API_KEY", "").strip()
    if not api_key:
        log.info("Lyzr: LYZR_API_KEY not set — skipping (no-op).")
        return

    def _send():
        try:
            resp = httpx.post(
                LYZR_ENDPOINT,
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "user_id": "echomind@nexus.club",
                    "agent_id": LYZR_AGENT_ID,
                    "session_id": "echomind-mirror",
                    "message": f"Club Q&A turn for audit. Q: {question}\nA: {answer[:500]}",
                },
                timeout=15,
            )
            log.info("Lyzr: mirrored turn, status=%s", resp.status_code)
        except Exception as e:
            log.warning("Lyzr: mirror failed (%s) — main flow unaffected.", e)

    threading.Thread(target=_send, daemon=True).start()
