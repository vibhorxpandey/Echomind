"use client";

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
      {type}
    </span>
  );
}

function DeltaArrow({ delta }: { delta: number }) {
  if (delta > 0)
    return <span className="font-mono text-[11px] text-emerald-400" title="promoted by reranker">▲{delta}</span>;
  if (delta < 0)
    return <span className="font-mono text-[11px] text-rose-400" title="demoted by reranker">▼{Math.abs(delta)}</span>;
  return <span className="font-mono text-[11px] text-slate-500">•</span>;
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
    <aside className="flex h-full w-full flex-col overflow-hidden border-l border-edge bg-panel">
      <div className="flex items-center justify-between border-b border-edge px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-slate-200">RETRIEVAL TRACE</h2>
          <p className="text-[11px] text-slate-500">hybrid RRF fusion → cross-encoder rerank</p>
        </div>
        {loading && (
          <span className="flex items-center gap-1.5 text-[11px] text-glow">
            <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-glow" />
            searching…
          </span>
        )}
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-3">
        {memoryHits.length > 0 && (
          <div className="animate-fade-in rounded-lg border border-fuchsia-500/25 bg-fuchsia-500/5 p-3">
            <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold tracking-wider text-fuchsia-300">
              <span>🧠 LONG-TERM MEMORY</span>
              <span className="text-fuchsia-400/60">agent_memory</span>
            </div>
            {memoryHits.map((m, i) => (
              <div key={i} className="mb-1.5 last:mb-0">
                <div className="flex items-baseline justify-between gap-2">
                  <p className="truncate text-xs text-slate-300">“{m.question}”</p>
                  <span className="font-mono text-[11px] text-fuchsia-300">{m.score.toFixed(3)}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {trace.length === 0 && !loading && (
          <div className="mt-16 text-center text-xs text-slate-600">
            <p className="mb-1 text-2xl">◇</p>
            <p>Ask something — every retrieved document,</p>
            <p>score and rerank decision shows up here.</p>
          </div>
        )}

        {trace.map((ev, ti) => (
          <div key={ti} className="animate-slide-in" style={{ animationDelay: `${ti * 120}ms` }}>
            <div className="mb-1.5 flex items-center gap-2">
              <span className="rounded bg-glow/10 px-1.5 py-0.5 font-mono text-[11px] text-glow">
                {ev.tool}
              </span>
              <span className="truncate font-mono text-[11px] text-slate-500">
                {String((ev.args as any).query ?? (ev.args as any).name ?? (ev.args as any).event_name ?? "")}
              </span>
            </div>
            <div className="space-y-1.5">
              {ev.results.map((r, ri) => (
                <div
                  key={r.doc_id + ri}
                  className="group animate-slide-in rounded-lg border border-edge bg-ink/60 p-2.5 transition-colors hover:border-glow/40"
                  style={{ animationDelay: `${ti * 120 + ri * 70}ms` }}
                >
                  <div className="mb-1 flex items-center gap-2">
                    <span className="font-mono text-[11px] text-slate-500">#{r.final_rank}</span>
                    <TypeBadge type={r.doc_type} />
                    <span className="font-mono text-[11px] text-slate-400">{r.year}</span>
                    <span className="ml-auto"><DeltaArrow delta={r.rank_delta} /></span>
                  </div>
                  <p className="mb-1 line-clamp-1 text-xs font-medium text-slate-200">{r.title}</p>
                  <div className="flex items-center gap-3 font-mono text-[11px]">
                    <span className="text-slate-500">
                      fused <span className="text-cyan-300">{r.fused_score.toFixed(4)}</span>
                    </span>
                    {r.rerank_score !== null && (
                      <span className="text-slate-500">
                        rerank <span className="text-amberish">{r.rerank_score.toFixed(4)}</span>
                      </span>
                    )}
                  </div>
                  <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-slate-500 group-hover:text-slate-400">
                    {r.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
