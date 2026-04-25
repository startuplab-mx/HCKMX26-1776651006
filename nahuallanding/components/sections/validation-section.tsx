import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";
import { site } from "@/content/site";

export function ValidationSection() {
  return (
    <SectionShell
      id="validacion"
      eyebrow="Validación juvenil"
      title="La necesidad no es hipotética. Ya fue reportada por jóvenes."
      copy="Durante el hackathon levantamos una encuesta rápida con 129 jóvenes para entender exposición, disposición de uso y qué condiciones de confianza debería respetar Nahual desde el día uno."
    >
      <div className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
        <Reveal className="panel p-6">
          <p className="terminal-text mb-4 text-cobre-light">hallazgos clave</p>
          <div className="space-y-4">
            {site.validationHighlights.map((highlight) => (
              <div
                key={highlight.title}
                className="rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(245,240,235,0.04)] p-5"
              >
                <div className="flex items-end justify-between gap-4">
                  <div>
                    <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-cobre-light">
                      {highlight.title}
                    </p>
                    <p className="mt-3 text-4xl font-black text-cream">{highlight.value}</p>
                  </div>
                </div>
                <p className="mt-4 text-sm leading-7 text-dim">{highlight.description}</p>
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={0.08} className="space-y-6">
          <div className="panel p-6">
            <p className="terminal-text mb-5 text-cobre-light">qué genera confianza</p>
            <div className="space-y-4">
              {site.privacyBars.map((bar) => (
                <div key={bar.label}>
                  <div className="mb-2 flex items-center justify-between gap-4 text-sm text-[rgba(245,240,235,0.76)]">
                    <span>{bar.label}</span>
                    <span className="font-mono text-cobre-light">{bar.value}%</span>
                  </div>
                  <div className="h-3 rounded-full bg-[rgba(245,240,235,0.06)]">
                    <div
                      className="h-3 rounded-full bg-[linear-gradient(90deg,rgba(212,132,90,0.65),rgba(245,240,235,0.88))]"
                      style={{ width: `${bar.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel p-6">
            <p className="terminal-text mb-5 text-cobre-light">preferencia de control</p>
            <div className="grid gap-3 sm:grid-cols-3">
              {site.controlPreference.map((item) => (
                <div
                  key={item.label}
                  className="rounded-[20px] border border-[rgba(245,240,235,0.08)] bg-[rgba(15,17,20,0.58)] p-4"
                >
                  <p className="text-3xl font-black text-cream">{item.value}%</p>
                  <p className="mt-3 text-sm leading-6 text-dim">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </SectionShell>
  );
}
