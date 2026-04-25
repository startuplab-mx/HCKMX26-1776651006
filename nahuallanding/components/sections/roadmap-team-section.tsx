import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";
import { site } from "@/content/site";

export function RoadmapTeamSection() {
  return (
    <SectionShell
      id="roadmap"
      eyebrow="Roadmap + equipo"
      title="La ambición del proyecto ya tiene forma operativa."
      copy="Nahual está pensado como MVP ejecutable de hackathon, pero con una ruta clara de acompañamiento, piloto y escalamiento. El equipo mezcla construcción técnica con validación clínica."
    >
      <div className="space-y-8">
        <div className="grid gap-4 lg:grid-cols-5">
          {site.roadmap.map((step, index) => (
            <Reveal key={step.phase} delay={index * 0.05}>
              <div className="panel h-full p-5">
                <p className="terminal-text text-cobre-light">{step.date}</p>
                <h3 className="mt-4 text-2xl font-black text-cream">{step.phase}</h3>
                <p className="mt-4 text-sm leading-7 text-dim">{step.description}</p>
              </div>
            </Reveal>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {site.team.map((member, index) => (
            <Reveal key={member.name} delay={0.12 + index * 0.06}>
              <div className="panel h-full p-6">
                <p className="terminal-text text-cobre-light">Equipo Vanguard</p>
                <h3 className="mt-3 text-3xl font-black text-cream">{member.name}</h3>
                <p className="mt-2 text-lg font-semibold text-[rgba(245,240,235,0.78)]">{member.role}</p>
                <p className="mt-2 text-sm uppercase tracking-[0.14em] text-[rgba(245,240,235,0.46)]">
                  {member.background}
                </p>
                <div className="mt-6 space-y-3">
                  {member.bio.map((item) => (
                    <p key={item} className="text-sm leading-7 text-dim">
                      {item}
                    </p>
                  ))}
                </div>
                <div className="mt-6 flex flex-wrap gap-2">
                  {member.chips.map((chip) => (
                    <span
                      key={chip}
                      className="rounded-full border border-[rgba(245,240,235,0.08)] bg-[rgba(245,240,235,0.04)] px-3 py-1.5 text-sm text-[rgba(245,240,235,0.74)]"
                    >
                      {chip}
                    </span>
                  ))}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </SectionShell>
  );
}
