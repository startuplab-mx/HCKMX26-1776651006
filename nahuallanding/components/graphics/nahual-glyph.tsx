"use client";

import { motion, useReducedMotion } from "framer-motion";

const outlinePaths = [
  "M124 424 L228 350 L214 314 L120 250 L266 262 L212 206 L118 162 L312 170 L302 58 L360 176 L424 178 L426 40 L514 192 L646 202 L598 312 L842 332 L796 488 L474 488 L422 572 L274 572 L126 424 Z",
  "M392 226 C392 260 420 288 454 288 C488 288 516 260 516 226",
  "M548 226 C548 260 576 288 610 288 C644 288 672 260 672 226",
  "M456 544 L516 418 L562 500 L610 418 L656 500 L706 418 L752 500",
  "M404 488 L360 544 L316 544 C316 508 348 488 404 488"
];

const meshPaths = [
  "M214 314 L330 320 L370 176",
  "M330 320 L454 226 L610 226",
  "M454 226 L514 192 L598 312",
  "M598 312 L842 332",
  "M610 226 L690 418 L752 500",
  "M404 488 L474 488 L610 418",
  "M274 572 L316 544 L456 544 L474 488",
  "M228 350 L330 320 L404 488"
];

const nodes = [
  { cx: 214, cy: 314 },
  { cx: 330, cy: 320 },
  { cx: 370, cy: 176 },
  { cx: 454, cy: 226 },
  { cx: 610, cy: 226 },
  { cx: 514, cy: 192 },
  { cx: 598, cy: 312 },
  { cx: 842, cy: 332 },
  { cx: 690, cy: 418 },
  { cx: 752, cy: 500 },
  { cx: 474, cy: 488 },
  { cx: 316, cy: 544 },
  { cx: 456, cy: 544 }
];

export function NahualGlyph() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="relative mx-auto flex w-full max-w-[42rem] items-center justify-center">
      <div className="absolute inset-[14%] rounded-full bg-radial-copper blur-3xl" />
      <div className="absolute inset-0 rounded-[40px] border border-[rgba(193,106,76,0.16)] bg-[rgba(15,17,20,0.22)]" />
      <div className="relative w-full rounded-[40px] border border-[rgba(245,240,235,0.08)] bg-[linear-gradient(180deg,rgba(58,66,73,0.24),rgba(15,17,20,0.18))] p-4 sm:p-6">
        <div className="mb-3 flex items-center justify-between px-2">
          <span className="terminal-text">NAHUAL NODAL</span>
          <span className="terminal-text text-cobre-light">protección digital / glyph</span>
        </div>
        <div className="relative overflow-hidden rounded-[28px] border border-[rgba(245,240,235,0.06)] bg-[radial-gradient(circle_at_top,rgba(193,106,76,0.08),transparent_35%),rgba(15,17,20,0.56)] p-4 sm:p-6">
          <div className="absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(193,106,76,0.5),transparent)]" />
          <svg
            viewBox="0 0 960 640"
            className="h-auto w-full"
            fill="none"
            aria-label="Glyph de jaguar nodal"
          >
            <defs>
              <linearGradient id="glyphStroke" x1="126" x2="796" y1="58" y2="572">
                <stop offset="0%" stopColor="rgba(245,240,235,0.75)" />
                <stop offset="48%" stopColor="#d4845a" />
                <stop offset="100%" stopColor="rgba(193,106,76,0.84)" />
              </linearGradient>
              <radialGradient id="glyphGlow" cx="50%" cy="45%" r="62%">
                <stop offset="0%" stopColor="rgba(212,132,90,0.35)" />
                <stop offset="100%" stopColor="rgba(212,132,90,0)" />
              </radialGradient>
            </defs>

            <rect x="0" y="0" width="960" height="640" rx="24" fill="url(#glyphGlow)" />

            {meshPaths.map((path, index) => (
              <motion.path
                key={path}
                d={path}
                stroke="rgba(212,132,90,0.48)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeDasharray="2 10"
                initial={reduceMotion ? false : { pathLength: 0, opacity: 0 }}
                animate={reduceMotion ? undefined : { pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 0.9,
                  ease: [0.22, 1, 0.36, 1],
                  delay: 0.55 + index * 0.08
                }}
              />
            ))}

            {outlinePaths.map((path, index) => (
              <motion.path
                key={path}
                d={path}
                stroke="url(#glyphStroke)"
                strokeWidth={index === 0 ? 3 : 2.4}
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={reduceMotion ? false : { pathLength: 0, opacity: 0 }}
                animate={reduceMotion ? undefined : { pathLength: 1, opacity: 1 }}
                transition={{
                  duration: index === 0 ? 1.25 : 0.85,
                  ease: [0.22, 1, 0.36, 1],
                  delay: index === 0 ? 0.08 : 0.32 + index * 0.08
                }}
              />
            ))}

            {nodes.map((node, index) => (
              <g key={`${node.cx}-${node.cy}`}>
                <motion.circle
                  cx={node.cx}
                  cy={node.cy}
                  r="6"
                  fill="#f5f0eb"
                  initial={reduceMotion ? false : { opacity: 0, scale: 0.4 }}
                  animate={
                    reduceMotion
                      ? undefined
                      : {
                          opacity: [0.4, 1, 0.4],
                          scale: [0.86, 1.12, 0.86]
                        }
                  }
                  transition={{
                    duration: 2.4,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 1.1 + index * 0.08
                  }}
                />
                <circle
                  cx={node.cx}
                  cy={node.cy}
                  r="12"
                  fill="rgba(212,132,90,0.08)"
                  stroke="rgba(212,132,90,0.22)"
                />
              </g>
            ))}
          </svg>
        </div>
      </div>
    </div>
  );
}
