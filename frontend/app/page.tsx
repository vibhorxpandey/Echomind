"use client";

import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import TracePanel from "@/components/TracePanel";
import WebGLErrorBoundary from "@/components/WebGLErrorBoundary";
import { ChatMessage, ChatResponse, MemoryHit, TraceEvent } from "@/lib/types";

const Constellation = dynamic(() => import("@/components/Constellation"), {
  ssr: false,
  loading: () => null,
});

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const SUGGESTIONS = [
  "Why did HackNexus 2023 lose money?",
  "Should we trust TechVerse Solutions?",
  "When is the annual fest held?",
  "How do we get budgets approved faster?",
];

const THINKING_COPY = [
  "Searching 299 memories…",
  "Reranking evidence…",
  "Synthesizing across years…",
  "Cross-referencing documents…",
  "Surfacing contradictions…",
];

// Minimal markdown renderer — bold, lists, paragraphs, citation pills
function mdToHtml(md: string): string {
  const esc = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const bold = esc.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  // Citation patterns like [doc_id] or (source: ...) → pill
  const cited = bold.replace(
    /\[([^\]]{2,60})\]/g,
    '<span class="citation">$1</span>'
  );
  const lines = cited.split("\n");
  let html = "", inOl = false, inUl = false;
  const close = () => {
    if (inOl) { html += "</ol>"; inOl = false; }
    if (inUl) { html += "</ul>"; inUl = false; }
  };
  for (const line of lines) {
    const ol = line.match(/^\s*\d+\.\s+(.*)/);
    const ul = line.match(/^\s*[-*]\s+(.*)/);
    if (ol) {
      if (!inOl) { close(); html += "<ol>"; inOl = true; }
      html += `<li>${ol[1]}</li>`;
    } else if (ul) {
      if (!inUl) { close(); html += "<ul>"; inUl = true; }
      html += `<li>${ul[1]}</li>`;
    } else {
      close();
      if (line.trim()) html += `<p>${line}</p>`;
    }
  }
  close();
  return html;
}

function ThinkingOrb({ copy }: { copy: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex items-center gap-3"
    >
      {/* Glowing orb */}
      <div className="relative flex h-8 w-8 shrink-0 items-center justify-center">
        <div className="absolute inset-0 rounded-full bg-glow/20 blur-md" />
        <div className="relative flex gap-0.5">
          {[0, 200, 400].map((delay) => (
            <span
              key={delay}
              className="h-1 w-1 animate-pulse-dot rounded-full bg-glow"
              style={{ animationDelay: `${delay}ms` }}
            />
          ))}
        </div>
      </div>
      <span className="font-mono text-xs italic text-glow/70">{copy}</span>
    </motion.div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [memoryHits, setMemoryHits] = useState<MemoryHit[]>([]);
  const [health, setHealth] = useState<"ok" | "down" | "checking">("checking");
  const [thinkingCopy, setThinkingCopy] = useState(THINKING_COPY[0]);
  const [videoError, setVideoError] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(`web-${Math.random().toString(36).slice(2, 10)}`);
  const prefersReducedMotion = useReducedMotion();
  const chatActive = messages.length > 0;

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => setHealth(r.ok ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Cycle thinking copy while loading
  useEffect(() => {
    if (!loading) return;
    let i = 0;
    const id = setInterval(() => {
      i = (i + 1) % THINKING_COPY.length;
      setThinkingCopy(THINKING_COPY[i]);
    }, 1800);
    return () => clearInterval(id);
  }, [loading]);

  async function send(text?: string) {
    const q = (text ?? input).trim();
    if (!q || loading) return;
    setInput("");
    setLoading(true);
    setMessages((m) => [...m, { role: "user", text: q }]);
    setTrace([]);
    setMemoryHits([]);
    setThinkingCopy(THINKING_COPY[0]);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, session_id: sessionId.current }),
      });
      const data: ChatResponse = await res.json();
      setMessages((m) => [
        ...m,
        { role: "agent", text: data.answer, mode: data.mode, latency_ms: data.latency_ms },
      ]);
      setTrace(data.retrieval_trace);
      setMemoryHits(data.memory_hits);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "agent", text: "⚠️ Backend unreachable — is uvicorn running on :8000?", mode: "error" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // ─── Shared input bar ────────────────────────────────────────────────────
  const InputBar = (
    <div className="mx-auto flex w-full max-w-2xl items-center gap-2">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && send()}
        placeholder="Ask about any event, sponsor, budget or member since 2021…"
        className="flex-1 rounded-xl border border-edge bg-ink/80 px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none backdrop-blur transition-colors focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/20"
      />
      <button
        onClick={() => send()}
        disabled={loading || !input.trim()}
        className="rounded-xl border border-violet-500/30 bg-violet-500/15 px-4 py-2.5 text-sm font-semibold text-violet-300 transition-all hover:bg-violet-500/25 hover:text-violet-200 disabled:opacity-30"
      >
        Ask
      </button>
    </div>
  );

  // ─── Constellation background (shared) ───────────────────────────────────
  const ConstellationBg = (
    <WebGLErrorBoundary>
      <motion.div
        className="pointer-events-none fixed inset-0 z-0"
        animate={
          prefersReducedMotion
            ? {}
            : chatActive
            ? { opacity: 0.25, filter: "blur(2px)" }
            : { opacity: 1, filter: "blur(0px)" }
        }
        transition={{ duration: 0.8, ease: "easeInOut" }}
      >
        <Constellation thinking={loading} chatActive={chatActive} className="h-full w-full" />
      </motion.div>
    </WebGLErrorBoundary>
  );

  // ─── Radial vignette overlay in chat state ───────────────────────────────
  const Vignette = chatActive && (
    <div
      className="pointer-events-none fixed inset-0 z-[1]"
      style={{
        background:
          "radial-gradient(ellipse 70% 70% at 30% 50%, transparent 0%, #0a0a12cc 60%, #0a0a12 100%)",
      }}
    />
  );

  return (
    <div className="relative flex h-screen flex-col overflow-hidden bg-ink">
      {ConstellationBg}
      {Vignette}

      {/* Header — always visible */}
      <header className="relative z-10 flex items-center justify-between border-b border-edge/60 bg-ink/60 px-5 py-3 backdrop-blur-md">
        <div className="flex items-baseline gap-3">
          <h1 className="shimmer-text text-xl font-bold tracking-tight">EchoMind</h1>
          <p className="text-xs italic text-slate-500">The senior who never graduates.</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="hidden font-mono text-[11px] text-slate-600 sm:inline">
            Nexus Tech Club · est. 2021
          </span>
          <span className="flex items-center gap-1.5 font-mono text-[11px] text-slate-500">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                health === "ok"
                  ? "bg-emerald-400 shadow-[0_0_6px_#34d399]"
                  : health === "down"
                  ? "bg-rose-500"
                  : "bg-amber-400 animate-pulse-dot"
              }`}
            />
            {health === "ok" ? "backend live" : health === "down" ? "backend down" : "checking"}
          </span>
        </div>
      </header>

      {/* ── HERO STATE ──────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {!chatActive && (
          <motion.main
            key="hero"
            initial={false}
            exit={
              prefersReducedMotion
                ? { opacity: 0 }
                : { opacity: 0, y: -24, transition: { duration: 0.4 } }
            }
            className="relative z-10 flex flex-1 flex-col items-center justify-center gap-8 px-6 py-8"
          >
            {/* Title block */}
            <div className="text-center">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.7 }}
                className="mb-3 text-5xl font-bold tracking-tight sm:text-6xl"
              >
                <span className="shimmer-text">EchoMind</span>
              </motion.h2>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.45, duration: 0.7 }}
                className="text-base text-slate-400 sm:text-lg"
              >
                The senior who never graduates.
              </motion.p>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7, duration: 0.7 }}
                className="mt-2 text-sm text-slate-600"
              >
                5 years · 299 documents · hybrid retrieval + long-term memory
              </motion.p>
            </div>

            {/* Demo video */}
            {!videoError && (
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.85, duration: 0.6 }}
                className="w-full max-w-3xl"
              >
                <div className="overflow-hidden rounded-2xl shadow-[0_0_40px_rgba(139,92,246,0.25)] ring-1 ring-violet-500/20">
                  <video
                    src="/demo.mp4"
                    controls
                    playsInline
                    preload="metadata"
                    onError={() => setVideoError(true)}
                    className="w-full"
                    style={{ display: "block" }}
                  />
                </div>
              </motion.div>
            )}

            {/* Suggestion chips */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0, duration: 0.5 }}
              className="flex flex-wrap justify-center gap-2"
            >
              {SUGGESTIONS.map((s) => (
                <motion.button
                  key={s}
                  onClick={() => send(s)}
                  whileHover={prefersReducedMotion ? {} : { scale: 1.04, y: -2 }}
                  whileTap={prefersReducedMotion ? {} : { scale: 0.97 }}
                  className="rounded-full border border-edge bg-panel/70 px-3 py-1.5 text-xs text-slate-400 backdrop-blur-sm transition-colors hover:border-violet-500/50 hover:text-violet-300"
                >
                  {s}
                </motion.button>
              ))}
            </motion.div>

            {/* Input bar */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.1, duration: 0.5 }}
              className="w-full max-w-2xl"
            >
              {InputBar}
            </motion.div>
          </motion.main>
        )}
      </AnimatePresence>

      {/* ── CHAT STATE ──────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {chatActive && (
          <motion.main
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="relative z-10 flex min-h-0 flex-1"
          >
            {/* Chat pane — 65% */}
            <section className="flex min-w-0 flex-1 flex-col">
              {/* Messages */}
              <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
                {messages.map((m, i) =>
                  m.role === "user" ? (
                    <motion.div
                      key={i}
                      initial={prefersReducedMotion ? {} : { opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ type: "spring", stiffness: 300, damping: 28 }}
                      className="flex justify-end"
                    >
                      <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-violet-500/15 px-4 py-2.5 text-sm text-violet-100 ring-1 ring-violet-500/20">
                        {m.text}
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key={i}
                      initial={prefersReducedMotion ? {} : { opacity: 0, x: -16 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ type: "spring", stiffness: 260, damping: 26 }}
                      className="flex justify-start"
                    >
                      <div className="max-w-[88%] rounded-2xl rounded-bl-sm border border-edge bg-panel/80 px-4 py-3 text-sm leading-relaxed text-slate-200 backdrop-blur-sm">
                        <div
                          className="answer-md"
                          dangerouslySetInnerHTML={{ __html: mdToHtml(m.text) }}
                        />
                        <div className="mt-2 flex items-center gap-2 border-t border-edge/50 pt-1.5">
                          <span
                            className={`font-mono text-[10px] ${
                              m.mode === "agent" ? "text-emerald-400" : "text-amber-400"
                            }`}
                          >
                            {m.mode === "agent"
                              ? "◈ ADK agent · gemini-2.5-flash"
                              : `◈ ${m.mode}`}
                          </span>
                          {m.latency_ms != null && (
                            <span className="font-mono text-[10px] text-slate-600">
                              {(m.latency_ms / 1000).toFixed(1)}s
                            </span>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  )
                )}

                {/* Thinking indicator */}
                <AnimatePresence>
                  {loading && (
                    <motion.div
                      key="thinking"
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -4 }}
                      className="flex justify-start pl-1"
                    >
                      <ThinkingOrb copy={thinkingCopy} />
                    </motion.div>
                  )}
                </AnimatePresence>

                <div ref={bottomRef} />
              </div>

              {/* Input bar in chat mode */}
              <div className="border-t border-edge/60 bg-ink/60 p-4 backdrop-blur-md">
                {InputBar}
              </div>
            </section>

            {/* Trace sidebar — 35% */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15, duration: 0.4 }}
              className="hidden w-[380px] shrink-0 lg:block xl:w-[420px]"
            >
              <TracePanel trace={trace} memoryHits={memoryHits} loading={loading} />
            </motion.div>
          </motion.main>
        )}
      </AnimatePresence>
    </div>
  );
}
