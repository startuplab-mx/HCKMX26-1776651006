"use client";

import { motion, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

const messages = [
  {
    author: "user",
    text: "Me ofrecieron $15,000 por ser guardia de seguridad, me pagan el viaje."
  },
  { author: "bot", text: "🔍 Analizando lenguaje, contexto y patrones de captación…" },
  {
    author: "bot",
    text: "🚨 Riesgo alto detectado. Fases: captación + enganche. Señales: oferta económica, traslado pagado y cambio de entorno."
  },
  {
    author: "bot",
    text: "¿Quieres que guarde evidencia, te comparta pasos de seguridad o alerte a un adulto de confianza?"
  }
] as const;

export function ChatMockup() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inView = useInView(containerRef, { once: true, margin: "-20% 0px" });
  const reduceMotion = useReducedMotion();
  const [visibleCount, setVisibleCount] = useState(reduceMotion ? messages.length : 0);

  useEffect(() => {
    if (!inView || reduceMotion) {
      return;
    }

    const timeouts = messages.map((_, index) =>
      window.setTimeout(() => {
        setVisibleCount(index + 1);
      }, 550 + index * 760)
    );

    return () => {
      timeouts.forEach((timeout) => window.clearTimeout(timeout));
    };
  }, [inView, reduceMotion]);

  return (
    <div ref={containerRef} className="metal-frame">
      <div className="browser-top mb-4">
        <div className="flex items-center gap-2">
          <span className="h-9 w-9 rounded-full bg-[rgba(37,211,102,0.16)] ring-1 ring-[rgba(37,211,102,0.2)]" />
          <div>
            <p className="text-sm font-semibold text-cream">Nahual Bot</p>
            <p className="text-xs text-[rgba(245,240,235,0.5)]">Protección reactiva vía WhatsApp</p>
          </div>
        </div>
        <span className="terminal-text">modo reactivo</span>
      </div>
      <div className="space-y-3 rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(14,18,20,0.88)] p-4">
        {messages.slice(0, visibleCount).map((message, index) => {
          const isBot = message.author === "bot";
          const showTyping =
            index === 0 && visibleCount < 2 && !reduceMotion;

          return (
            <div key={`${message.author}-${index}`}>
              <motion.div
                initial={reduceMotion ? false : { opacity: 0, y: 12 }}
                animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                className={`max-w-[86%] rounded-[20px] px-4 py-3 text-sm leading-6 ${
                  isBot
                    ? "border border-[rgba(193,106,76,0.16)] bg-[rgba(193,106,76,0.08)] text-cream"
                    : "ml-auto bg-[rgba(245,240,235,0.08)] text-[rgba(245,240,235,0.9)]"
                }`}
              >
                {message.text}
              </motion.div>
              {showTyping ? (
                <div className="mt-3 inline-flex items-center gap-1 rounded-full border border-[rgba(193,106,76,0.16)] bg-[rgba(193,106,76,0.08)] px-3 py-2">
                  {[0, 1, 2].map((dot) => (
                    <motion.span
                      key={dot}
                      className="h-1.5 w-1.5 rounded-full bg-cobre-light"
                      animate={reduceMotion ? undefined : { opacity: [0.25, 1, 0.25] }}
                      transition={{
                        duration: 0.9,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: dot * 0.12
                      }}
                    />
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
