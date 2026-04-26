"use client";

import { motion } from "framer-motion";
import { useState } from "react";

import { RiskGauge } from "@/components/graphics/risk-gauge";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";
import { site } from "@/content/site";

export function ClassifierSection() {
  const [active, setActive] = useState(site.classifierPhases[2].id);

  return (
    <SectionShell
      id="clasificador"
      eyebrow="El clasificador"
      title="900 patrones. 4 fases. Detección en milisegundos."
      copy="Nahual pondera señales por fase con un dataset bilingüe (lenguaje del agresor + reportes de la víctima), reconoce umbrales de peligro inminente y aplica un override automático cuando coerción o explotación cruzan el 80%. El objetivo no es solo etiquetar — es orientar la respuesta correcta en tiempo real."
    >
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="grid gap-4 md:grid-cols-2">
          {site.classifierPhases.map((phase, index) => {
            const isActive = active === phase.id;

            return (
              <Reveal key={phase.id} delay={index * 0.06}>
                <motion.button
                  type="button"
                  onMouseEnter={() => setActive(phase.id)}
                  onFocus={() => setActive(phase.id)}
                  onClick={() => setActive(phase.id)}
                  className="panel h-full p-5 text-left"
                  animate={{
                    scale: isActive ? 1.01 : 1,
                    borderColor: isActive ? "rgba(212,132,90,0.32)" : "rgba(245,240,235,0.08)"
                  }}
                  transition={{ duration: 0.25, ease: "easeOut" }}
                >
                  <div className="mb-4 flex items-center justify-between gap-4">
                    <div>
                      <p className="font-mono text-[11px] uppercase tracking-[0.24em]" style={{ color: phase.accent }}>
                        fase {index + 1}
                      </p>
                      <h3 className="mt-2 text-2xl font-black text-cream">{phase.title}</h3>
                    </div>
                    <span
                      className="rounded-full px-3 py-1 text-sm font-bold"
                      style={{
                        backgroundColor: "rgba(245,240,235,0.05)",
                        color: phase.accent
                      }}
                    >
                      {phase.weight}
                    </span>
                  </div>
                  <p className="text-sm leading-7 text-dim">{phase.summary}</p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {phase.patterns.map((pattern) => (
                      <span
                        key={pattern}
                        className="rounded-full border border-[rgba(245,240,235,0.08)] px-3 py-1.5 text-sm text-[rgba(245,240,235,0.76)]"
                      >
                        {pattern}
                      </span>
                    ))}
                  </div>
                  <p className="mt-5 text-xs uppercase tracking-[0.18em] text-[rgba(245,240,235,0.4)]">
                    Fuente: {phase.source}
                  </p>
                  {phase.badge ? (
                    <p className="mt-3 rounded-[16px] border border-[rgba(239,68,68,0.16)] bg-[rgba(239,68,68,0.08)] px-3 py-2 text-xs font-mono uppercase tracking-[0.16em] text-danger">
                      {phase.badge}
                    </p>
                  ) : null}
                </motion.button>
              </Reveal>
            );
          })}
        </div>

        <Reveal delay={0.12} className="space-y-6">
          <div className="panel p-6">
            <p className="terminal-text mb-3 text-cobre-light">fórmula de puntuación</p>
            <div className="rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(15,17,20,0.72)] px-4 py-5 font-mono text-sm text-[rgba(245,240,235,0.78)]">
              {site.riskFormula}
            </div>
            <p className="mt-4 text-sm leading-7 text-dim">
              Las fases no pesan igual. La coerción y la explotación elevan el score más rápido, y ciertas frases críticas pueden activar override sin esperar acumulación.
            </p>
          </div>
          <RiskGauge value={site.riskScore} />
        </Reveal>
      </div>
    </SectionShell>
  );
}
