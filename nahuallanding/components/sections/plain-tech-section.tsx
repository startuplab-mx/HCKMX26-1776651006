"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

import { site } from "@/content/site";
import { Reveal } from "@/components/ui/reveal";

/**
 * Cómo funciona por dentro — explica la pila técnica en lenguaje plano,
 * con un toggle que revela la ficha técnica para engineers. Idea: el
 * jurado no técnico entiende por qué importa, y el jurado técnico puede
 * verificar profundidad sin abandonar la página.
 *
 * Cada item viene de `site.plainTech` (ver content/site.ts) y refleja
 * una capa real del sistema, no marketing. Cuando agregas hardening
 * nuevo en backend / bot / extension / panel, agrégalo ahí también.
 */
export function PlainTechSection() {
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <section id="bajo-el-capo" className="py-24 md:py-32">
      <div className="section-wrap">
        <Reveal>
          <div className="flex items-center gap-4 mb-4">
            <div className="h-0.5 w-12 bg-[#c16a4c]" />
            <h2 className="text-3xl md:text-5xl font-bold uppercase tracking-tight text-[#f5f0eb]">
              Cómo funciona por dentro
            </h2>
          </div>
          <p className="text-[#f5f0eb]/70 text-lg md:text-xl max-w-3xl mb-12">
            Cada característica está pensada para responder a una pregunta
            concreta: ¿qué pasa si alguien intenta romper el sistema? ¿qué
            pasa si el menor está en crisis a media conversación? ¿qué pasa
            si un atacante quiere envenenar el modelo? Aquí está la versión
            corta y la ficha técnica.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 relative z-10">
          {site.plainTech.map((item, idx) => {
            const isOpen = openId === item.id;
            return (
              <Reveal key={item.id} delay={0.04 * idx}>
                <article
                  className={`flex flex-col p-6 lg:p-8 rounded-2xl border transition-all duration-300 ease-out ${
                    isOpen
                      ? "bg-[#3a4249]/45 border-[#c16a4c]/55"
                      : "bg-[#3a4249]/20 border-[#f5f0eb]/8 hover:border-[#c16a4c]/30 hover:bg-[#3a4249]/30"
                  }`}
                >
                  <header className="flex items-start gap-3 mb-3">
                    <span
                      aria-hidden
                      className="mt-1 h-2 w-2 rounded-full bg-[#c16a4c] flex-shrink-0"
                    />
                    <h3 className="text-lg lg:text-xl font-bold tracking-tight text-[#f5f0eb] leading-snug flex-1">
                      {item.title}
                    </h3>
                  </header>

                  <p className="text-[#f5f0eb]/75 leading-relaxed text-base lg:text-[17px] mb-4">
                    {item.layman}
                  </p>

                  {item.technical ? (
                    <>
                      <button
                        type="button"
                        onClick={() => setOpenId(isOpen ? null : item.id)}
                        className="self-start inline-flex items-center gap-2 text-xs uppercase tracking-wider text-[#c16a4c] hover:text-[#d4845a] transition-colors"
                        aria-expanded={isOpen}
                        aria-controls={`tech-${item.id}`}
                      >
                        <ChevronDown
                          size={14}
                          className={`transition-transform ${isOpen ? "rotate-180" : ""}`}
                        />
                        {isOpen ? "Ocultar ficha técnica" : "Ver ficha técnica"}
                      </button>

                      {isOpen ? (
                        <pre
                          id={`tech-${item.id}`}
                          className="mt-4 p-4 rounded-lg bg-[#0d1013]/70 border border-[#f5f0eb]/8 text-[12.5px] text-[#f5f0eb]/85 font-mono leading-relaxed whitespace-pre-wrap break-words"
                        >
                          {item.technical}
                        </pre>
                      ) : null}
                    </>
                  ) : null}
                </article>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
