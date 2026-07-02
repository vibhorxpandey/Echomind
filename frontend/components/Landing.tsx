"use client";

import { useState, type RefObject } from "react";
import { motion } from "framer-motion";

const SUGGESTIONS = [
  "Why did HackNexus 2023 lose money?",
  "Should we trust TechVerse Solutions?",
  "When is the annual fest held?",
  "How do we get budgets approved faster?",
];

const HOW_IT_WORKS = [
  {
    k: "01",
    title: "Hybrid Retrieval",
    body: "Every document is indexed twice — dense BGE embeddings for meaning and sparse BM25 for exact terms. Qdrant fuses both with Reciprocal Rank Fusion, so it catches the idea and the keyword.",
    accent: "text-glow",
  },
  {
    k: "02",
    title: "Cross-Encoder Rerank",
    body: "The top 20 fused candidates are re-scored by a cross-encoder that reads query and document together, promoting the truly relevant to the final top 5. You see every rank change in the trace.",
    accent: "text-amberish",
  },
  {
    k: "03",
    title: "Long-Term Memory",
    body: "After each answer, EchoMind stores a summary in a second Qdrant collection. Ask a follow-up weeks later and it recalls the earlier conversation — the agent that remembers what it already told you.",
    accent: "text-violet",
  },
];

const CAPABILITIES = [
  { q: "The ₹18,000 HackNexus loss", a: "Traces the cause across a budget sheet, a post-mortem and meeting minutes — venue double-booking plus a sponsor who pulled out five days before." },
  { q: "The TechVerse ghosting pattern", a: "Connects a 2023 withdrawal to a 2024 email thread and a handover note that says, in plain words, \"never rely on TechVerse.\"" },
  { q: "The fest-date contradiction", a: "Flags that a 2022 doc says March and a 2024 doc says September — and tells you which one supersedes the other." },
  { q: "The budget-approval trick", a: "Surfaces the institutional hack buried in two handover notes: submit before the 5th with a one-page summary and approvals come 3× faster." },
];

const STACK = [
  { name: "Google ADK + Gemini", role: "The reasoning agent — decomposes questions, calls tools, synthesizes across years." },
  { name: "Qdrant", role: "Two collections: hybrid knowledge search and long-term conversational memory." },
  { name: "Lyzr", role: "Agent-ops integration layer, wired in as a thin, non-blocking module." },
];

function Section({
  children,
  scrollRoot,
  className = "",
}: {
  children: React.ReactNode;
  scrollRoot: RefObject<HTMLDivElement>;
  className?: string;
}) {
  return (
    <section
      className={`flex min-h-full snap-start flex-col items-center justify-center px-6 py-16 ${className}`}
    >
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ root: scrollRoot, amount: 0.35, once: false }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="w-full"
      >
        {children}
      </motion.div>
    </section>
  );
}

export default function Landing({
  scrollRef,
  onSend,
}: {
  scrollRef: RefObject<HTMLDivElement>;
  onSend: (text: string) => void;
}) {
  const [ask, setAsk] = useState("");

  const scrollDown = () => {
    scrollRef.current?.scrollBy({ top: window.innerHeight, behavior: "smooth" });
  };
  const scrollToAsk = () => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  };

  return (
    <div
      ref={scrollRef}
      className="relative z-10 h-full snap-y snap-mandatory overflow-y-auto scroll-smooth"
    >
      {/* ── HERO ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto max-w-3xl text-center">
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mb-4 font-mono text-xs tracking-[0.3em] text-violet/70"
          >
            INSTITUTIONAL MEMORY, ALIVE
          </motion.p>
          <h1 className="shimmer-text mb-4 text-6xl font-bold tracking-tight sm:text-8xl">
            EchoMind
          </h1>
          <p className="mb-3 text-xl text-slate-200 sm:text-2xl">
            The senior who never graduates.
          </p>
          <p className="mx-auto max-w-xl text-sm text-slate-400">
            An AI agent that remembers everything a club has ever learned — five years of
            minutes, budgets, sponsor emails and post-mortems, answered with receipts.
          </p>
          <div className="mt-10 flex items-center justify-center gap-3">
            <button
              onClick={scrollToAsk}
              className="rounded-full border border-violet/40 bg-violet/15 px-6 py-2.5 text-sm font-semibold text-violet-200 transition-all hover:bg-violet/25"
            >
              Ask the senior →
            </button>
            <button
              onClick={scrollDown}
              className="rounded-full border border-edge bg-panel/50 px-5 py-2.5 text-sm text-slate-300 backdrop-blur-sm transition-colors hover:border-glow/50 hover:text-glow"
            >
              Explore ↓
            </button>
          </div>
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="mt-16 font-mono text-[11px] tracking-widest text-slate-600"
          >
            SWIPE TO DISCOVER
          </motion.div>
        </div>
      </Section>

      {/* ── PROBLEM ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-4 font-mono text-xs tracking-[0.3em] text-rose-400/70">THE PROBLEM</p>
          <h2 className="mb-6 text-4xl font-bold text-slate-100 sm:text-5xl">
            Clubs forget everything.
          </h2>
          <p className="text-lg leading-relaxed text-slate-300">
            When seniors graduate, years of hard-won knowledge walk out the door with them.
            Which sponsor ghosted. Why the last hackathon lost money. The trick to getting a
            budget approved. Every new committee relearns the same lessons — the expensive way.
          </p>
        </div>
      </Section>

      {/* ── SOLUTION ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto max-w-2xl text-center">
          <p className="mb-4 font-mono text-xs tracking-[0.3em] text-glow/70">THE SOLUTION</p>
          <h2 className="mb-6 text-4xl font-bold sm:text-5xl">
            <span className="shimmer-text">EchoMind never graduates.</span>
          </h2>
          <p className="text-lg leading-relaxed text-slate-300">
            It ingests a club&apos;s entire history and becomes the senior you can always ask —
            answering with citations to the exact document and year, synthesizing across
            storylines, flagging contradictions, and warning you about the mistakes that
            already burned the club once.
          </p>
        </div>
      </Section>

      {/* ── HOW IT WORKS ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto max-w-5xl">
          <p className="mb-4 text-center font-mono text-xs tracking-[0.3em] text-slate-500">
            HOW IT WORKS
          </p>
          <h2 className="mb-10 text-center text-3xl font-bold text-slate-100 sm:text-4xl">
            Retrieval you can watch think.
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            {HOW_IT_WORKS.map((c) => (
              <div
                key={c.k}
                className="rounded-2xl border border-edge bg-panel/60 p-6 backdrop-blur-md transition-colors hover:border-violet/40"
              >
                <div className={`mb-3 font-mono text-2xl font-bold ${c.accent}`}>{c.k}</div>
                <h3 className="mb-2 text-lg font-semibold text-slate-100">{c.title}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{c.body}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ── CAPABILITIES ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto max-w-4xl">
          <p className="mb-4 text-center font-mono text-xs tracking-[0.3em] text-amberish/70">
            WHAT IT UNCOVERS
          </p>
          <h2 className="mb-10 text-center text-3xl font-bold text-slate-100 sm:text-4xl">
            Buried stories, connected.
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {CAPABILITIES.map((c) => (
              <div
                key={c.q}
                className="rounded-2xl border border-edge bg-panel/60 p-5 backdrop-blur-md transition-colors hover:border-amberish/40"
              >
                <h3 className="mb-2 text-base font-semibold text-amber-200">{c.q}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{c.a}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ── SPONSOR STACK ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto max-w-4xl">
          <p className="mb-4 text-center font-mono text-xs tracking-[0.3em] text-slate-500">
            BUILT WITH
          </p>
          <h2 className="mb-10 text-center text-3xl font-bold text-slate-100 sm:text-4xl">
            A serious agent stack.
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            {STACK.map((s) => (
              <div
                key={s.name}
                className="rounded-2xl border border-edge bg-gradient-to-br from-panel/70 to-panel/40 p-6 backdrop-blur-md"
              >
                <h3 className="mb-2 bg-gradient-to-r from-cyan-300 to-violet-300 bg-clip-text text-lg font-bold text-transparent">
                  {s.name}
                </h3>
                <p className="text-sm leading-relaxed text-slate-400">{s.role}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ── ASK CTA ── */}
      <Section scrollRoot={scrollRef}>
        <div className="mx-auto w-full max-w-2xl text-center">
          <h2 className="mb-3 text-4xl font-bold sm:text-5xl">
            <span className="shimmer-text">Ask the senior.</span>
          </h2>
          <p className="mb-8 text-sm text-slate-400">
            Five years of institutional memory. One question away.
          </p>
          <div className="mb-5 flex items-center gap-2">
            <input
              value={ask}
              onChange={(e) => setAsk(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && ask.trim()) onSend(ask.trim());
              }}
              placeholder="Ask about any event, sponsor, budget or member since 2021…"
              className="flex-1 rounded-xl border border-edge bg-ink/70 px-4 py-3 text-sm text-slate-200 placeholder-slate-600 outline-none backdrop-blur transition-colors focus:border-violet/60 focus:ring-1 focus:ring-violet/25"
            />
            <button
              onClick={() => ask.trim() && onSend(ask.trim())}
              disabled={!ask.trim()}
              className="rounded-xl border border-violet/40 bg-violet/20 px-5 py-3 text-sm font-semibold text-violet-200 transition-all hover:bg-violet/30 disabled:opacity-30"
            >
              Ask
            </button>
          </div>
          <div className="flex flex-wrap justify-center gap-2">
            {SUGGESTIONS.map((s) => (
              <motion.button
                key={s}
                onClick={() => onSend(s)}
                whileHover={{ scale: 1.04, y: -2 }}
                whileTap={{ scale: 0.97 }}
                className="rounded-full border border-edge bg-panel/60 px-3 py-1.5 text-xs text-slate-400 backdrop-blur-sm transition-colors hover:border-violet/50 hover:text-violet-300"
              >
                {s}
              </motion.button>
            ))}
          </div>
        </div>
      </Section>
    </div>
  );
}
