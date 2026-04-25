import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";
import { FunnelDiagram } from "@/components/graphics/funnel-diagram";
import { site } from "@/content/site";

export function ProblemSection() {
  return (
    <SectionShell
      id="problema"
      eyebrow="El problema"
      title="El problema ya está ocurriendo en plataformas cotidianas."
      copy="Nahual no parte de una intuición abstracta. Parte de investigación pública, evidencia digital observable y una secuencia de captación que hoy sucede antes del daño visible."
    >
      <div className="grid gap-8 lg:grid-cols-[0.92fr_1.08fr]">
        <div className="space-y-4">
          {site.problemNarrative.map((paragraph, index) => (
            <Reveal
              key={paragraph}
              delay={index * 0.08}
              className="panel p-6"
            >
              <p className="text-base leading-8 text-[rgba(245,240,235,0.78)]">{paragraph}</p>
            </Reveal>
          ))}
        </div>
        <Reveal delay={0.18}>
          <FunnelDiagram />
        </Reveal>
      </div>
    </SectionShell>
  );
}
