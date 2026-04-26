import { ArchitectureDiagram } from "@/components/graphics/architecture-diagram";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function ArchitectureSection() {
  return (
    <SectionShell
      id="arquitectura"
      eyebrow="Arquitectura"
      title="4 capas cognitivas. Modular. Open source."
      copy="Cada capa aporta una señal independiente: un heurístico determinista de 900 patrones, un clasificador Bayesiano que aprende del feedback, un LLM que entiende contexto sutil, y un detector de trayectoria que ve la progresión entre mensajes. Ninguna capa puede engañar a las otras. Todo cabe en 1 GB de RAM, sin GPU."
    >
      <Reveal>
        <ArchitectureDiagram />
      </Reveal>
    </SectionShell>
  );
}
