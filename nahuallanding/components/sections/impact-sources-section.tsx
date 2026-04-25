import { site } from "@/content/site";
import { CountUp } from "@/components/ui/count-up";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function ImpactSourcesSection() {
  return (
    <SectionShell
      id="impacto"
      eyebrow="Impacto + respaldo"
      title="El pitch cierra con datos, evidencia y una ruta clara de confianza."
      copy="Nahual no se presenta como promesa abstracta de IA. Se presenta como una herramienta concreta, con señales mapeadas, validación temprana y un marco público de investigación que justifica su urgencia."
    >
      <div className="space-y-8">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {site.impactStats.map((stat, index) => (
            <Reveal key={stat.label} delay={index * 0.05}>
              <div className="panel p-5">
                <p className="terminal-text text-cobre-light">impacto</p>
                <div className="mt-4 text-5xl font-black text-cream">
                  <CountUp value={stat.value} suffix={stat.suffix} />
                </div>
                <p className="mt-3 text-sm font-semibold leading-6 text-[rgba(245,240,235,0.82)]">
                  {stat.label}
                </p>
                <p className="mt-2 text-sm leading-6 text-dim">{stat.detail}</p>
              </div>
            </Reveal>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <Reveal className="panel p-6">
            <p className="terminal-text mb-4 text-cobre-light">respaldo institucional</p>
            <div className="grid gap-3">
              {site.institutionBadges.map((badge) => (
                <div
                  key={badge}
                  className="rounded-[20px] border border-[rgba(245,240,235,0.08)] bg-[rgba(245,240,235,0.04)] px-4 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-[rgba(245,240,235,0.74)]"
                >
                  {badge}
                </div>
              ))}
            </div>
            <p className="mt-5 text-sm leading-7 text-dim">
              Investigación basada en ONC, REDIM, Seminario sobre Violencia y Paz del Colmex, FBI y evidencia agregada levantada por el propio equipo durante el hackathon.
            </p>
          </Reveal>

          <Reveal delay={0.08} className="panel p-6">
            <p className="terminal-text mb-4 text-cobre-light">fuentes</p>
            <div className="space-y-4">
              {site.sources.map((source) => (
                <a
                  key={source.href}
                  href={source.href}
                  target="_blank"
                  rel="noreferrer"
                  className="block rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(15,17,20,0.56)] p-5 transition hover:border-[rgba(193,106,76,0.24)]"
                >
                  <p className="text-lg font-bold text-cream">{source.label}</p>
                  <p className="mt-2 text-sm leading-7 text-dim">{source.note}</p>
                </a>
              ))}
            </div>
          </Reveal>
        </div>
      </div>
    </SectionShell>
  );
}
