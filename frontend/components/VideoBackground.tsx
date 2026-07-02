"use client";

import { useState } from "react";
import { motion, useReducedMotion, type MotionValue } from "framer-motion";

interface Props {
  dim?: boolean;
  scale?: MotionValue<number>;
  y?: MotionValue<string>;
}

/**
 * Fullscreen fixed video background (demo.mp4). Scrubs subtly with scroll via
 * the scale / y motion values passed from the parent's useScroll.
 * - onError → animated CSS gradient fallback (no broken element, chat unaffected)
 * - prefers-reduced-motion → paused first frame, no parallax
 */
export default function VideoBackground({ dim = false, scale, y }: Props) {
  const [failed, setFailed] = useState(false);
  const reduce = useReducedMotion();

  if (failed) {
    return (
      <div className="fixed inset-0 z-0 bg-gradient-to-br from-[#0a0a12] via-[#150826] to-[#0a1622]">
        <div className="absolute inset-0 animate-pulse bg-[radial-gradient(ellipse_at_30%_30%,rgba(139,92,246,0.15),transparent_60%),radial-gradient(ellipse_at_70%_70%,rgba(34,211,238,0.12),transparent_60%)]" />
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-0 overflow-hidden bg-ink">
      <motion.video
        src="/demo.mp4"
        autoPlay={!reduce}
        muted
        loop
        playsInline
        preload="auto"
        onError={() => setFailed(true)}
        style={reduce ? undefined : { scale, y }}
        className="absolute inset-0 h-full w-full object-cover"
      />

      {/* Legibility overlays — lighter on landing, heavy blur in chat */}
      <div
        className={`absolute inset-0 transition-all duration-700 ${
          dim
            ? "bg-ink/92 backdrop-blur-xl"
            : "bg-gradient-to-b from-ink/75 via-ink/45 to-ink/85"
        }`}
      />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_10%,rgba(10,10,18,0.65)_100%)]" />
      {/* Violet/cyan tint for brand cohesion */}
      {!dim && (
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(139,92,246,0.12),transparent_45%),radial-gradient(circle_at_85%_75%,rgba(34,211,238,0.10),transparent_45%)]" />
      )}
    </div>
  );
}
