"use client";

import { motion, useReducedMotion } from "framer-motion";

export function BrowserShieldMockup() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="metal-frame">
      <div className="browser-top mb-4">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-danger" />
          <span className="h-2.5 w-2.5 rounded-full bg-warning" />
          <span className="h-2.5 w-2.5 rounded-full bg-success" />
        </div>
        <div className="w-[62%] rounded-full border border-[rgba(245,240,235,0.08)] bg-[rgba(245,240,235,0.04)] px-4 py-2 text-center font-mono text-[11px] uppercase tracking-[0.22em] text-[rgba(245,240,235,0.44)]">
          Nahual Shield / overlay monitor
        </div>
      </div>
      <div className="relative overflow-hidden rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(14,18,20,0.92)] p-4">
        <div className="grid gap-3 pr-0 md:pr-40">
          {[
            "oye, vi que andas buscando salida y trabajo",
            "te puedo acomodar con pago rápido",
            "solo pásate a Telegram para explicarte bien",
            "nadie tiene que enterarse"
          ].map((line, index) => (
            <motion.div
              key={line}
              className={`rounded-[18px] border px-4 py-3 text-sm ${
                index === 2
                  ? "border-danger/50 bg-danger/10 text-cream"
                  : "border-[rgba(245,240,235,0.06)] bg-[rgba(245,240,235,0.04)] text-[rgba(245,240,235,0.74)]"
              }`}
              animate={
                reduceMotion || index !== 2
                  ? undefined
                  : {
                      boxShadow: [
                        "0 0 0 rgba(239,68,68,0)",
                        "0 0 0 1px rgba(239,68,68,0.35), 0 0 24px rgba(239,68,68,0.24)",
                        "0 0 0 rgba(239,68,68,0)"
                      ]
                    }
              }
              transition={{ duration: 2.1, repeat: Infinity, ease: "easeInOut" }}
            >
              {line}
            </motion.div>
          ))}
        </div>

        <motion.div
          className="mt-4 md:absolute md:right-4 md:top-6 md:mt-0 md:w-36"
          initial={reduceMotion ? false : { x: 28, opacity: 0 }}
          whileInView={reduceMotion ? undefined : { x: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.55, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="rounded-[22px] border border-[rgba(239,68,68,0.24)] bg-[linear-gradient(180deg,rgba(239,68,68,0.14),rgba(15,17,20,0.96))] p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.26em] text-danger">escala inmediata</p>
            <h4 className="mt-3 text-lg font-black text-cream">Nahual Shield</h4>
            <p className="mt-2 text-sm leading-6 text-[rgba(245,240,235,0.7)]">
              Detectó cambio de plataforma + secreto + incentivo económico.
            </p>
            <button className="mt-4 w-full rounded-full border border-[rgba(193,106,76,0.28)] bg-[rgba(193,106,76,0.12)] px-4 py-2 text-sm font-semibold text-cobre-light">
              Reportar al bot
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
