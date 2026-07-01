# EchoMind — 2.5-Minute Demo Script

*Setup before recording: backend + frontend running (`./run.sh`), browser at
localhost:3000, window sized so the Retrieval Trace sidebar is fully visible.
Ask the storyline-1 question once in an earlier session so memory recall has
something to find — or just record straight through; turn 4 recalls turn 1.*

---

**[0:00–0:20] — Hook**

> "Every May, college clubs get a lobotomy. The seniors graduate, and everything they
> learned — which sponsor ghosts, why events lose money, how to get budgets approved —
> walks out the door with them. This is EchoMind: the senior who never graduates. We fed
> it five years of a club's real paperwork — 299 minutes, budgets, emails, post-mortems
> and handover notes — and it answers like someone who was there."

---

**[0:20–1:00] — Storyline 1: cross-document synthesis**

Type: **"Why did HackNexus 2023 lose money?"**

> "No single document says 'we lost ₹18,000 because X'. The answer is scattered across a
> budget reconciliation, a post-mortem, and two meeting minutes. Watch the sidebar — the
> agent runs hybrid search on Qdrant, fuses dense and BM25 results, and a cross-encoder
> reranks them. You can see every score, and the arrows show where the reranker
> overruled the fused ranking."

Point at the answer: venue double-booking (+₹9,500), TechVerse pulling out ₹25,000 five
days before, no contingency line — every claim cited by document and year.

---

**[1:00–1:35] — Storyline 2: the agent warns you**

Type: **"Should we approach TechVerse Solutions to sponsor our next event?"**

> "Here's the institutional-memory part. The agent doesn't just answer — it warns. It
> found that TechVerse ghosted the club in 2023 *and again in 2024*, and that a
> treasurer's handover note literally says 'never rely on TechVerse'. A first-year with
> zero context just got five years of hard-won judgment in ten seconds."

---

**[1:35–2:05] — Storyline 6: contradiction flagging**

Type: **"When is the annual fest held?"**

> "Trick question — the archive disagrees with itself. A 2022 planning doc says the fest
> is every March; 2024 minutes moved it permanently to September. EchoMind doesn't pick
> one silently — it flags the contradiction, cites both documents, and explains the 2024
> decision supersedes. That's what you want from a senior: not just an answer, but 'careful,
> the old docs are stale.'"

---

**[2:05–2:30] — Memory recall + close**

Type: **"Last time we talked about an event that lost money — which sponsor was involved again?"**

> "And EchoMind remembers its own conversations. That purple block in the sidebar is a
> hit from its long-term memory collection in Qdrant — a past Q&A turn, retrieved and
> injected before answering. Google ADK agent, Gemini 2.5 Flash, hybrid Qdrant retrieval
> with reranking, Lyzr audit mirror — the senior who never graduates. Thanks!"

---

*Fallback: if the LLM hiccups on stage, the app degrades to a labeled retrieval-only
mode — the trace sidebar still works, so the retrieval demo survives.*
