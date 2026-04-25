"use client";

import { motion, useReducedMotion } from "framer-motion";

import { site } from "@/content/site";

export function FunnelDiagram() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="panel p-6">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="terminal-text text-cobre-light">ciclo de reclutamiento</p>
          <h3 className="mt-2 text-2xl font-black text-cream">Fases que Nahual busca interrumpir</h3>
        </div>
        <span className="terminal-text">detección temprana</span>
      </div>
      <div className="grid gap-4">
        {site.pipeline.map((step, index) => (
          <motion.div
            key={step.title}
            className="relative overflow-hidden rounded-[24px] border border-[rgba(245,240,235,0.08)] bg-[rgba(15,17,20,0.58)] p-5"
            initial={reduceMotion ? false : { opacity: 0, x: 32 }}
            whileInView={reduceMotion ? undefined : { opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-20% 0px" }}
            transition={{
              duration: 0.65,
              ease: [0.22, 1, 0.36, 1],
              delay: index * 0.14
            }}
          >
            <div
              className="absolute inset-y-0 left-0 w-1"
              style={{ backgroundColor: step.accent }}
            />
            <div className="flex items-start gap-4">
              <div
                className="mt-1 h-3.5 w-3.5 rounded-full shadow-[0_0_18px_currentColor]"
                style={{ color: step.accent, backgroundColor: step.accent }}
              />
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xl font-black text-cream">{step.title}</span>
                  <span className="rounded-full border border-[rgba(245,240,235,0.08)] px-3 py-1 font-mono text-[11px] uppercase tracking-[0.24em] text-[rgba(245,240,235,0.54)]">
                    fase {index + 1}
                  </span>
                </div>
                <p className="text-dim">{step.description}</p>
                <p className="font-mono text-sm text-cobre-light">{step.example}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
