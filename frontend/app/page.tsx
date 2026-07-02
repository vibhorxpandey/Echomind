"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import TracePanel from "@/components/TracePanel";
import VideoBackground from "@/components/VideoBackground";
import Landing from "@/components/Landing";
import FoundersBadge from "@/components/FoundersBadge";
import { ChatMessage, ChatResponse, MemoryHit, TraceEvent } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const THINKING_COPY = [
  "Searching 299 memories…",
  "Reranking evidence…",
  "Synthesizing across years…",
  "Cross-referencing documents…",
  "Surfacing contradictions…",
];

// Minimal markdown: bold, lists, paragraphs, citation pills
function mdToHtml(md: string): string {
  const esc = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const bold = esc.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  const cited = bold.replace(/\[([^\]]{2,60})\]/g, '<span class="citation">$1</span>');
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
  const bottomRef = useRef<HTMLDivElement>(null);
  const landingScrollRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(`web-${Math.random().toString(36).slice(2, 10)}`);
  const prefersReducedMotion = useReducedMotion();
  const chatActive = messages.length > 0;

  // Scroll-driven video parallax (the video "moves" as you swipe)
  const { scrollYProgress } = useScroll({ container: landingScrollRef });
  const vidScale = useTransform(scrollYProgress, [0, 1], [1.12, 1.4]);
  const vidY = useTransform(scrollYProgress, [0, 1], ["0%", "-6%"]);

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => setHealth(r.ok ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

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

  return (
    <div className="relative flex h-screen flex-col overflow-hidden bg-ink">
      <VideoBackground
        dim={chatActive}
        scale={chatActive ? undefined : vidScale}
        y={chatActive ? undefined : vidY}
      />

      {/* Header — always visible */}
      <header className="relative z-20 flex items-center justify-between border-b border-edge/50 bg-ink/40 px-5 py-3 backdrop-blur-md">
        <div className="flex items-baseline gap-3">
          <h1 className="shimmer-text text-xl font-bold tracking-tight">EchoMind</h1>
          <p className="hidden text-xs italic text-slate-400 sm:block">
            The senior who never graduates.
          </p>
        </div>
        <div className="flex items-center gap-4">
          {chatActive && (
            <button
              onClick={() => {
                setMessages([]);
                setTrace([]);
                setMemoryHits([]);
              }}
              className="font-mono text-[11px] text-slate-500 transition-colors hover:text-violet-300"
            >
              ← home
            </button>
          )}
          <span className="hidden font-mono text-[11px] text-slate-600 md:inline">
            Nexus Tech Club · est. 2021
          </span>
          <span className="flex items-center gap-1.5 font-mono text-[11px] text-slate-500">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                health === "ok"
                  ? "bg-emerald-400 shadow-[0_0_6px_#34d399]"
                  : health === "down"
                  ? "bg-rose-500"
                  : "animate-pulse-dot bg-amber-400"
              }`}
            />
            {health === "ok" ? "backend live" : health === "down" ? "backend down" : "checking"}
          </span>
        </div>
      </header>

      {/* ── LANDING (video-background scroll experience) ── */}
      {!chatActive && (
        <main className="relative z-10 min-h-0 flex-1">
          <Landing scrollRef={landingScrollRef} onSend={send} />
        </main>
      )}

      {/* ── CHAT STATE ── */}
      {chatActive && (
        <motion.main
          key="chat"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="relative z-10 flex min-h-0 flex-1"
        >
          {/* Chat pane */}
          <section className="flex min-w-0 flex-1 flex-col">
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
                    <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-violet/20 px-4 py-2.5 text-sm text-violet-100 ring-1 ring-violet/25">
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
                    <div className="max-w-[88%] rounded-2xl rounded-bl-sm border border-edge bg-panel/85 px-4 py-3 text-sm leading-relaxed text-slate-200 backdrop-blur-sm">
                      <div className="answer-md" dangerouslySetInnerHTML={{ __html: mdToHtml(m.text) }} />
                      <div className="mt-2 flex items-center gap-2 border-t border-edge/50 pt-1.5">
                        <span
                          className={`font-mono text-[10px] ${
                            m.mode === "agent" ? "text-emerald-400" : "text-amber-400"
                          }`}
                        >
                          {m.mode === "agent" ? "◈ ADK agent · gemini-2.5-flash" : `◈ ${m.mode}`}
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

            <div className="border-t border-edge/60 bg-ink/50 p-4 backdrop-blur-md">
              <div className="mx-auto flex w-full max-w-2xl items-center gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && send()}
                  placeholder="Ask a follow-up…"
                  className="flex-1 rounded-xl border border-edge bg-ink/80 px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none backdrop-blur transition-colors focus:border-violet/60 focus:ring-1 focus:ring-violet/20"
                />
                <button
                  onClick={() => send()}
                  disabled={loading || !input.trim()}
                  className="rounded-xl border border-violet/30 bg-violet/15 px-4 py-2.5 text-sm font-semibold text-violet-300 transition-all hover:bg-violet/25 disabled:opacity-30"
                >
                  Ask
                </button>
              </div>
            </div>
          </section>

          {/* Trace sidebar */}
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

      {/* Persistent founding-team credit, bottom-right on every state */}
      <FoundersBadge />
    </div>
  );
}
