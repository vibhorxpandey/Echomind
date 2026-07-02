"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const TEAM = [
  { name: "Vibhor Pandey", role: "Founder" },
  { name: "Bhavya Dubey", role: "Co-founder" },
  { name: "Yuvraj Arora", role: "Co-founder" },
  { name: "Rohit Singh Rajawat", role: "Co-founder" },
];

function initials(name: string) {
  return name.split(" ").map((n) => n[0]).slice(0, 2).join("");
}

/** Persistent bottom-right team credit. Compact pill that expands on hover/tap. */
export default function FoundersBadge() {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="fixed bottom-4 right-4 z-50 select-none"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-12 right-0 w-56 rounded-2xl border border-violet/30 bg-panel/95 p-3 shadow-[0_0_30px_rgba(139,92,246,0.25)] backdrop-blur-xl"
          >
            <p className="mb-2 font-mono text-[10px] tracking-[0.2em] text-violet/70">
              BUILT BY
            </p>
            <ul className="space-y-2">
              {TEAM.map((m) => (
                <li key={m.name} className="flex items-center gap-2.5">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet to-glow text-[10px] font-bold text-white">
                    {initials(m.name)}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-xs font-semibold text-slate-100">
                      {m.name}
                    </span>
                    <span className="block font-mono text-[10px] text-slate-500">
                      {m.role}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Collapsed pill */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Founding team"
        className="flex items-center gap-2 rounded-full border border-edge bg-panel/80 py-1.5 pl-2 pr-3 backdrop-blur-md transition-colors hover:border-violet/50"
      >
        <span className="flex -space-x-2">
          {TEAM.map((m) => (
            <span
              key={m.name}
              className="flex h-6 w-6 items-center justify-center rounded-full border border-panel bg-gradient-to-br from-violet to-glow text-[9px] font-bold text-white"
            >
              {initials(m.name)}
            </span>
          ))}
        </span>
        <span className="font-mono text-[10px] tracking-wider text-slate-400">TEAM</span>
      </button>
    </div>
  );
}
