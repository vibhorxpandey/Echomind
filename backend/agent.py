"""EchoMind root agent (Google ADK + Gemini 2.5 Flash).

Tools wrap the retrieval pipeline. Every tool call appends its retrieval
results to a per-turn trace buffer so /chat can return the full retrieval
trace to the UI. If GOOGLE_API_KEY is missing or the LLM call fails, /chat
falls back to a retrieval-only extractive answer (mode="retrieval-only").
"""

import os
import uuid

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from backend.config import log
from backend.memory import recall_memory
from backend.retrieval import hybrid_search

# Per-turn trace buffer. The demo server handles one chat turn at a time,
# so a module-level buffer is sufficient (reset at the start of each turn).
TRACE: list[dict] = []
MEMORY_HITS: list[dict] = []


def _record(tool: str, args: dict, out: dict) -> None:
    TRACE.append({"tool": tool, "args": args, "results": out["results"],
                  "trace": out["trace"]})


def search_knowledge(query: str, doc_type_filter: str = "", year_filter: int = 0) -> dict:
    """Search the club's full knowledge base (minutes, budgets, sponsor emails,
    post-mortems, handover notes, member profiles, project docs) using hybrid
    semantic + keyword search with reranking.

    Args:
        query: What to search for. Use focused sub-queries for multi-part questions.
        doc_type_filter: Optional. One of: meeting_minutes, event_budget,
            sponsor_email, post_mortem, handover_note, member_profile, project_doc.
        year_filter: Optional. Restrict to a year 2021-2025 (0 = all years).

    Returns:
        dict with 'results': list of documents (title, doc_type, year, author, content).
    """
    out = hybrid_search(query, doc_type=doc_type_filter or None,
                        year=year_filter or None, top_k=5)
    _record("search_knowledge", {"query": query, "doc_type_filter": doc_type_filter,
                                 "year_filter": year_filter}, out)
    return {"results": [
        {"title": r["title"], "doc_type": r["doc_type"], "year": r["year"],
         "date": r["date"], "author": r["author"], "content": r["content"]}
        for r in out["results"]
    ]}


def get_member_info(name: str) -> dict:
    """Look up a club member: their profile and any handover notes they wrote.

    Args:
        name: The member's name (full or partial).

    Returns:
        dict with 'profile' and 'handover_notes' document lists.
    """
    prof = hybrid_search(f"member profile {name}", doc_type="member_profile", top_k=3)
    hand = hybrid_search(f"handover note by {name}", doc_type="handover_note", top_k=3)
    _record("get_member_info", {"name": name, "facet": "profile"}, prof)
    _record("get_member_info", {"name": name, "facet": "handover"}, hand)
    strip = lambda rs: [{"title": r["title"], "year": r["year"], "author": r["author"],
                         "content": r["content"]} for r in rs]
    return {"profile": strip(prof["results"]), "handover_notes": strip(hand["results"])}


def get_event_history(event_name: str) -> dict:
    """Get the full history of a club event across all years: budgets,
    post-mortems, and meeting minutes that discuss it.

    Args:
        event_name: e.g. "HackNexus", "Nexus Annual Fest", "TechFest".

    Returns:
        dict with 'documents': relevant docs sorted by year.
    """
    out = hybrid_search(f"{event_name} event planning budget outcome post-mortem", top_k=8)
    _record("get_event_history", {"event_name": event_name}, out)
    docs = sorted(out["results"], key=lambda r: r["year"])
    return {"documents": [
        {"title": r["title"], "doc_type": r["doc_type"], "year": r["year"],
         "content": r["content"]} for r in docs
    ]}


def recall_conversation(query: str) -> dict:
    """Recall what EchoMind discussed with users in past conversations
    (its own long-term memory, persisted across sessions).

    Args:
        query: Topic to recall past conversations about.

    Returns:
        dict with 'memories': past Q&A summaries with relevance scores.
    """
    hits = recall_memory(query, top_k=3)
    MEMORY_HITS.extend(hits)
    return {"memories": hits}


INSTRUCTION = """You are EchoMind, the institutional memory of Nexus Tech Club
(founded 2021 at Kaveri Institute of Technology). You have ingested every
meeting minute, event budget, sponsor email, post-mortem, handover note,
member profile, and project doc from 2021-2025. You are "the senior who never
graduates": you answer like a wise senior member who was there for all of it.

Rules:
1. ALWAYS ground answers in retrieved documents. Cite sources inline by
   document title and year, e.g. (HackNexus 2023 Post-Mortem, 2023).
2. For questions spanning multiple topics or years, DECOMPOSE into several
   focused search_knowledge calls (e.g. one per sub-topic or year) and
   synthesize across the results. Prefer 2-4 targeted searches over one vague one.
3. FLAG CONTRADICTIONS: if retrieved documents disagree (e.g. different years
   state different facts), say so explicitly, cite both, and explain which is
   more recent/authoritative.
4. WARN ABOUT PAST FAILURES: if the question touches anything the club has
   been burned by before (e.g. a sponsor that ghosted, a venue mishap),
   proactively surface that history even if not directly asked.
5. Use recall_conversation when the user references earlier discussions
   ("as we discussed", "last time", "again") or when past conversations would
   add context.
6. Be concise but complete: a short direct answer first, then the supporting
   detail with citations. Use rupee amounts and concrete numbers from the docs.
7. If the knowledge base has nothing relevant, say so honestly - never invent
   club history."""

root_agent = Agent(
    name="echomind",
    model=os.getenv("ECHOMIND_MODEL", "gemini-2.5-flash"),
    description="Institutional memory agent for Nexus Tech Club.",
    instruction=INSTRUCTION,
    tools=[search_knowledge, get_member_info, get_event_history, recall_conversation],
)

_session_service = InMemorySessionService()
_runner = Runner(agent=root_agent, app_name="echomind", session_service=_session_service)
_known_sessions: set[str] = set()

USER_ID = "club-member"


async def run_agent(message: str, session_id: str) -> tuple[str, list[str]]:
    """Run one turn through the ADK runner. Returns (answer, tool_call_names)."""
    if session_id not in _known_sessions:
        await _session_service.create_session(
            app_name="echomind", user_id=USER_ID, session_id=session_id)
        _known_sessions.add(session_id)

    content = types.Content(role="user", parts=[types.Part(text=message)])
    answer, tool_calls = "", []
    async for event in _runner.run_async(user_id=USER_ID, session_id=session_id,
                                         new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    tool_calls.append(part.function_call.name)
        if event.is_final_response() and event.content and event.content.parts:
            answer = "".join(p.text or "" for p in event.content.parts)
    return answer, tool_calls


def extractive_fallback(message: str) -> str:
    """Retrieval-only answer when no Gemini key is available."""
    out = hybrid_search(message, top_k=3)
    _record("search_knowledge", {"query": message, "fallback": True}, out)
    if not out["results"]:
        return "I couldn't find anything relevant in the club's knowledge base."
    lines = ["(Retrieval-only mode - set GOOGLE_API_KEY for synthesized answers.)",
             "Most relevant club documents:"]
    for r in out["results"]:
        lines.append(f"\n- {r['title']} ({r['doc_type']}, {r['year']}): {r['content'][:300]}...")
    return "\n".join(lines)


def reset_turn_buffers() -> None:
    TRACE.clear()
    MEMORY_HITS.clear()


def gemini_available() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY", "").strip())
