"use client";

import { motion, useReducedMotion } from "framer-motion";

type RiskGaugeProps = {
  value: number;
};

export function RiskGauge({ value }: RiskGaugeProps) {
  const reduceMotion = useReducedMotion();
  const clamped = Math.min(Math.max(value, 0), 1);
  const rotation = -100 + clamped * 200;

  return (
    <div className="panel p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="terminal-text text-cobre-light">risk meter</p>
          <h3 className="mt-2 text-2xl font-black text-cream">Score demo</h3>
        </div>
        <span className="rounded-full border border-[rgba(239,68,68,0.28)] bg-[rgba(239,68,68,0.12)] px-3 py-1 font-mono text-xs uppercase tracking-[0.22em] text-danger">
          peligro
        </span>
      </div>
      <div className="relative mx-auto flex max-w-[22rem] justify-center">
        <svg viewBox="0 0 280 180" className="w-full" fill="none" aria-label="Medidor de riesgo">
          <path d="M36 148a104 104 0 0 1 208 0" stroke="rgba(245,240,235,0.08)" strokeWidth="18" strokeLinecap="round" />
          <path d="M36 148a104 104 0 0 1 70-90" stroke="var(--green)" strokeWidth="18" strokeLinecap="round" />
          <path d="M106 58a104 104 0 0 1 69-8" stroke="var(--yellow)" strokeWidth="18" strokeLinecap="round" />
          <path d="M175 50a104 104 0 0 1 69 98" stroke="var(--red)" strokeWidth="18" strokeLinecap="round" />
          <g transform="translate(140 148)">
            <motion.g
              initial={reduceMotion ? false : { rotate: -100 }}
              animate={reduceMotion ? undefined : { rotate: rotation }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            >
              <line x1="0" y1="0" x2="0" y2="-88" stroke="#f5f0eb" strokeWidth="4" strokeLinecap="round" />
              <circle cx="0" cy="-88" r="8" fill="#d4845a" />
            </motion.g>
            <circle cx="0" cy="0" r="16" fill="rgba(15,17,20,0.96)" stroke="rgba(245,240,235,0.14)" />
          </g>
        </svg>
        <div className="absolute bottom-0 text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-[rgba(245,240,235,0.54)]">
            demo score
          </p>
          <p className="mt-2 text-4xl font-black text-cream">{value.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
}
