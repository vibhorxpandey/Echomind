"use client";

import { AnimatePresence, motion } from "framer-motion";
import { MemoryHit, TraceEvent } from "@/lib/types";

const TYPE_STYLES: Record<string, string> = {
  meeting_minutes: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  event_budget: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  sponsor_email: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  post_mortem: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  handover_note: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  member_profile: "bg-teal-500/15 text-teal-300 border-teal-500/30",
  project_doc: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
};

function TypeBadge({ type }: { type: string }) {
  const cls = TYPE_STYLES[type] ?? "bg-slate-500/15 text-slate-300 border-slate-500/30";
  return (
    <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium tracking-wide ${cls}`}>
      {type.replace(/_/g, " ")}
    </span>
  );
}

function DeltaArrow({ delta }: { delta: number }) {
  if (delta > 0)
    return (
      <span className="font-mono text-[11px] font-bold text-emerald-400" title="promoted by reranker">
        ▲{delta}
      </span>
    );
  if (delta < 0)
    return (
      <span className="font-mono text-[11px] font-bold text-amber-400" title="demoted by reranker">
        ▼{Math.abs(delta)}
      </span>
    );
  return <span className="font-mono text-[11px] text-slate-600">•</span>;
}


export default function TracePanel({
  trace,
  memoryHits,
  loading,
}: {
  trace: TraceEvent[];
  memoryHits: MemoryHit[];
  loading: boolean;
}) {
  return (
    <aside className="flex h-full w-full flex-col overflow-hidden border-l border-edge bg-panel/95 backdrop-blur-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-edge px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold tracking-widest text-slate-200">
            RETRIEVAL TRACE
          </h2>
          <p className="font-mono text-[10px] text-slate-600">
            hybrid RRF fusion → cross-encoder rerank
          </p>
        </div>
        <AnimatePresence>
          {loading && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-1.5 font-mono text-[11px] text-glow"
            >
              <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-glow" />
              scanning…
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-3">
        {/* ── Memory banner — the star judging feature ── */}
        <AnimatePresence>
          {memoryHits.length > 0 && (
            <motion.div
              key="memory-banner"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: "spring", stiffness: 260, damping: 24 }}
              className="relative overflow-hidden rounded-xl border border-amber-500/40 bg-gradient-to-br from-amber-500/10 to-orange-500/5 p-3"
            >
              {/* Glow pulse behind the banner */}
              <div className="pointer-events-none absolute -inset-1 rounded-xl bg-amber-500/5 blur-xl" />
              <div className="relative">
                <div className="mb-2 flex items-center gap-2">
                  <span className="text-base">🧠</span>
                  <span className="text-xs font-bold tracking-widest text-amber-300">
                    RECALLED FROM MEMORY
                  </span>
                  <span className="ml-auto rounded border border-amber-500/30 bg-amber-500/10 px-1.5 py-0.5 font-mono text-[9px] text-amber-400">
                    agent_memory ✦
                  </span>
                </div>
                <p className="mb-2 text-[10px] text-amber-200/60">
                  Long-term memory surfaced these past conversations as context:
                </p>
                {memoryHits.map((m, i) => (
                  <div
                    key={i}
                    className="mb-1.5 flex items-baseline justify-between gap-2 last:mb-0"
                  >
                    <p className="truncate text-[11px] text-amber-100/80">"{m.question}"</p>
                    <span className="shrink-0 font-mono text-[11px] font-bold text-amber-300">
                      {m.score.toFixed(3)}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Empty state ── */}
        {trace.length === 0 && !loading && memoryHits.length === 0 && (
          <div className="mt-20 text-center text-xs text-slate-700">
            <p className="mb-2 text-3xl opacity-30">◈</p>
            <p className="text-slate-600">Ask something — every retrieved document,</p>
            <p className="text-slate-600">score and rerank decision surfaces here.</p>
          </div>
        )}

        {/* ── Trace events ── */}
        <AnimatePresence>
          {trace.map((ev, ti) => (
            <motion.div
              key={`${ev.tool}-${ti}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: ti * 0.1 }}
            >
              {/* Tool call label */}
              <div className="mb-2 flex items-center gap-2">
                <span className="rounded-md bg-violet-500/15 px-2 py-0.5 font-mono text-[11px] font-semibold text-violet-300 ring-1 ring-violet-500/20">
                  {ev.tool}
                </span>
                <span className="max-w-[180px] truncate font-mono text-[10px] text-slate-600">
                  {String(
                    (ev.args as Record<string, unknown>).query ??
                    (ev.args as Record<string, unknown>).name ??
                    (ev.args as Record<string, unknown>).event_name ??
                    ""
                  )}
                </span>
                <span className="ml-auto font-mono text-[10px] text-slate-700">
                  {ev.trace.candidates_considered} cands
                </span>
              </div>

              {/* Result cards */}
              <div className="space-y-1.5">
                {ev.results.map((r, ri) => (
                  <motion.div
                    key={r.doc_id + ri}
                    initial={{ opacity: 0, x: 18, scale: 0.97 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    transition={{ delay: ri * 0.08, type: "spring" as const, stiffness: 300, damping: 28 }}
                    className="group rounded-xl border border-edge bg-ink/70 p-2.5 backdrop-blur-sm transition-colors duration-200 hover:border-violet-500/40 hover:bg-ink"
                  >
                    <div className="mb-1.5 flex items-center gap-2">
                      <span className="font-mono text-[10px] text-slate-600">#{r.final_rank}</span>
                      <TypeBadge type={r.doc_type} />
                      <span className="font-mono text-[10px] text-slate-500">{r.year}</span>
                      <span className="ml-auto">
                        <DeltaArrow delta={r.rank_delta} />
                      </span>
                    </div>

                    <p className="mb-1.5 line-clamp-1 text-xs font-semibold text-slate-200">
                      {r.title}
                    </p>

                    <div className="mb-1 flex items-center gap-4 font-mono text-[10px]">
                      <span className="text-slate-600">
                        fused{" "}
                        <span className="font-bold text-glow">{r.fused_score.toFixed(4)}</span>
                      </span>
                      {r.rerank_score !== null && (
                        <span className="text-slate-600">
                          rerank{" "}
                          <span className="font-bold text-amberish">
                            {r.rerank_score.toFixed(4)}
                          </span>
                        </span>
                      )}
                    </div>

                    <p className="line-clamp-2 text-[10px] leading-relaxed text-slate-600 transition-colors group-hover:text-slate-500">
                      {r.content.slice(0, 200)}
                    </p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </aside>
  );
}
