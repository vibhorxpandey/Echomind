"use client";

import { useEffect, useRef, useState } from "react";
import TracePanel from "@/components/TracePanel";
import { ChatMessage, ChatResponse, MemoryHit, TraceEvent } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const SUGGESTIONS = [
  "Why did HackNexus 2023 lose money?",
  "Should we trust TechVerse Solutions as a sponsor?",
  "When is the annual fest held?",
  "How do we get budgets approved faster?",
  "Why did membership drop in 2024?",
  "What made the 2025 sponsor pitch work?",
];

// Minimal markdown: **bold**, numbered/bullet lists, paragraphs.
function mdToHtml(md: string): string {
  const esc = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const bold = esc.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  const lines = bold.split("\n");
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

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [memoryHits, setMemoryHits] = useState<MemoryHit[]>([]);
  const [health, setHealth] = useState<"ok" | "down" | "checking">("checking");
  const bottomRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(`web-${Math.random().toString(36).slice(2, 10)}`);

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => setHealth(r.ok ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text?: string) {
    const q = (text ?? input).trim();
    if (!q || loading) return;
    setInput("");
    setLoading(true);
    setMessages((m) => [...m, { role: "user", text: q }]);
    setTrace([]);
    setMemoryHits([]);
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
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-edge bg-panel/80 px-5 py-3 backdrop-blur">
        <div className="flex items-baseline gap-3">
          <h1 className="bg-gradient-to-r from-cyan-300 to-violet-400 bg-clip-text text-xl font-bold tracking-tight text-transparent">
            EchoMind
          </h1>
          <p className="text-xs italic text-slate-400">The senior who never graduates.</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="font-mono text-[11px] text-slate-500">Nexus Tech Club · est. 2021</span>
          <span className="flex items-center gap-1.5 text-[11px] text-slate-400">
            <span
              className={`h-2 w-2 rounded-full ${
                health === "ok" ? "bg-emerald-400" : health === "down" ? "bg-rose-500" : "bg-amber-400"
              }`}
            />
            {health === "ok" ? "backend live" : health === "down" ? "backend down" : "checking"}
          </span>
        </div>
      </header>

      <main className="flex min-h-0 flex-1">
        <section className="flex min-w-0 flex-1 flex-col">
          <div className="flex-1 space-y-4 overflow-y-auto px-6 py-5">
            {messages.length === 0 && (
              <div className="mx-auto mt-14 max-w-lg text-center">
                <p className="mb-2 text-3xl">🎓</p>
                <h2 className="mb-1 text-lg font-semibold text-slate-200">
                  Ask the senior who was there for all of it
                </h2>
                <p className="mb-6 text-sm text-slate-500">
                  5 years of minutes, budgets, sponsor emails, post-mortems and handover notes —
                  with receipts for every answer.
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => send(s)}
                      className="rounded-full border border-edge bg-panel px-3 py-1.5 text-xs text-slate-300 transition-colors hover:border-glow/50 hover:text-glow"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((m, i) =>
              m.role === "user" ? (
                <div key={i} className="flex justify-end">
                  <div className="animate-fade-in max-w-[80%] rounded-2xl rounded-br-sm bg-glow/10 px-4 py-2.5 text-sm text-cyan-100">
                    {m.text}
                  </div>
                </div>
              ) : (
                <div key={i} className="flex justify-start">
                  <div className="animate-fade-in max-w-[85%] rounded-2xl rounded-bl-sm border border-edge bg-panel px-4 py-3 text-sm leading-relaxed text-slate-200">
                    <div className="answer-md" dangerouslySetInnerHTML={{ __html: mdToHtml(m.text) }} />
                    <div className="mt-2 flex items-center gap-2 border-t border-edge/60 pt-1.5">
                      <span
                        className={`font-mono text-[10px] ${
                          m.mode === "agent" ? "text-emerald-400" : "text-amber-400"
                        }`}
                      >
                        {m.mode === "agent" ? "◈ ADK agent · gemini-2.5-flash" : `◈ ${m.mode}`}
                      </span>
                      {m.latency_ms != null && (
                        <span className="font-mono text-[10px] text-slate-500">{(m.latency_ms / 1000).toFixed(1)}s</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            )}

            {loading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-2 rounded-2xl border border-edge bg-panel px-4 py-3 text-sm text-slate-400">
                  <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-glow" />
                  <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-glow" style={{ animationDelay: "200ms" }} />
                  <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-glow" style={{ animationDelay: "400ms" }} />
                  <span className="ml-1 text-xs italic">consulting five years of club archives…</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-edge bg-panel/60 p-4">
            <div className="mx-auto flex max-w-3xl items-center gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Ask about any event, sponsor, budget or member since 2021…"
                className="flex-1 rounded-xl border border-edge bg-ink px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none transition-colors focus:border-glow/50"
              />
              <button
                onClick={() => send()}
                disabled={loading || !input.trim()}
                className="rounded-xl bg-glow/15 px-4 py-2.5 text-sm font-medium text-glow transition-colors hover:bg-glow/25 disabled:opacity-40"
              >
                Ask
              </button>
            </div>
          </div>
        </section>

        <div className="hidden w-[400px] shrink-0 lg:block xl:w-[440px]">
          <TracePanel trace={trace} memoryHits={memoryHits} loading={loading} />
        </div>
      </main>
    </div>
  );
}
