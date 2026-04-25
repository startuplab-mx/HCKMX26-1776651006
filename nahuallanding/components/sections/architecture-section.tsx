import { ArchitectureDiagram } from "@/components/graphics/architecture-diagram";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function ArchitectureSection() {
  return (
    <SectionShell
      id="arquitectura"
      eyebrow="Arquitectura"
      title="Modular. Escalable. Open source."
      copy="La arquitectura prioriza trazabilidad, bajo costo operativo y explicación comprensible del riesgo. Todo lo esencial cabe en una cadena clara de captura, clasificación, evidencia y monitoreo."
    >
      <Reveal>
        <ArchitectureDiagram />
      </Reveal>
    </SectionShell>
  );
}
