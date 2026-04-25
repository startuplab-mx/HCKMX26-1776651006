import { FlowDiagram } from "@/components/graphics/flow-diagram";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function FlowSection() {
  return (
    <SectionShell
      id="flujo"
      eyebrow="Flujo conversacional"
      title="El bot responde como sistema de triage, no como chatbot genérico."
      copy="El flujo busca tres cosas: reconocer riesgo, explicar por qué lo ve y activar la siguiente acción con el menor nivel de fricción posible."
    >
      <Reveal>
        <FlowDiagram />
      </Reveal>
    </SectionShell>
  );
}
