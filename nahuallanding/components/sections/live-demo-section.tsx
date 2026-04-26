"use client";

import { ArrowUpRight, MessageCircle, Monitor, Code2 } from "lucide-react";
import { site } from "@/content/site";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

/**
 * Live demo CTA section — points visitors at the actual production
 * deployment so judges and prospective testers can interact with the
 * system without scheduling a demo.
 */
export function LiveDemoSection() {
  const live = site.liveDemo;
  const cards = [
    {
      key: "bot",
      icon: <MessageCircle size={28} className="text-[#d4845a]" />,
      eyebrow: "Bot WhatsApp",
      title: live.botPhone,
      body:
        "Reactivo · texto / audio / captura · responde en 2-3s con análisis + por qué + marco legal + opción de avisar a un adulto. Bot vinculado en producción 24/7.",
      cta: "Abrir en WhatsApp",
      href: live.waLink,
    },
    {
      key: "panel",
      icon: <Monitor size={28} className="text-[#d4845a]" />,
      eyebrow: "Panel Web",
      title: live.panelUrl.replace(/^https?:\/\//, ""),
      body:
        "Auto-refresh 5s · Manual analyze textbox · 🔬 Deep healthcheck · PELIGRO toast con audio cue · Filtros + CSV export.",
      cta: "Abrir panel",
      href: live.panelUrl,
    },
    {
      key: "swagger",
      icon: <Code2 size={28} className="text-[#d4845a]" />,
      eyebrow: "Swagger API",
      title: "/docs",
      body:
        "33+ endpoints documentados — /analyze, /alert, /admin/dataset-info, /bayesian/predict, /admin/healthcheck-deep. Esquemas Pydantic. PII-free.",
      cta: "Explorar API",
      href: live.swaggerUrl,
    },
  ];

  return (
    <SectionShell id="live">
      <Reveal>
        <div className="flex items-center gap-4 mb-4">
          <div className="h-0.5 w-12 bg-[#c16a4c]" />
          <h2 className="text-3xl md:text-5xl font-bold uppercase tracking-tight text-[#f5f0eb]">
            Producción 24/7
          </h2>
        </div>
        <p className="text-[#f5f0eb]/70 text-lg md:text-xl max-w-2xl mb-16">
          El sistema está corriendo en vivo. Puedes probar cualquiera de las tres superficies sin
          esperar a una demo agendada.
        </p>
      </Reveal>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 relative z-10">
        {cards.map((card, idx) => (
          <Reveal key={card.key} delay={0.1 * idx}>
            <a
              href={card.href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col gap-5 p-8 lg:p-10 rounded-2xl bg-[#3a4249]/20 border border-[#f5f0eb]/5 hover:border-[#c16a4c]/40 hover:bg-[#3a4249]/40 transition-all duration-500 ease-out h-full group"
            >
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-xl bg-[#0d1013]/60 flex items-center justify-center border border-[#f5f0eb]/5 group-hover:scale-110 group-hover:border-[#c16a4c]/40 transition-all duration-300">
                  {card.icon}
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-[0.2em] text-[#c16a4c]">
                    {card.eyebrow}
                  </div>
                  <h3 className="text-xl lg:text-2xl font-bold tracking-tight text-[#f5f0eb] leading-tight">
                    {card.title}
                  </h3>
                </div>
              </div>
              <p className="text-[#f5f0eb]/70 leading-relaxed text-sm lg:text-base flex-1">
                {card.body}
              </p>
              <div className="flex items-center gap-1 text-sm text-[#c16a4c] group-hover:gap-2 transition-all">
                <span>{card.cta}</span>
                <ArrowUpRight size={16} />
              </div>
            </a>
          </Reveal>
        ))}
      </div>

      <Reveal delay={0.3}>
        <p className="text-xs text-[#f5f0eb]/40 mt-8 italic max-w-2xl">{live.note}</p>
      </Reveal>
    </SectionShell>
  );
}
