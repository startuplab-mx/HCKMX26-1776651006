import { FlowDiagram } from "@/components/graphics/flow-diagram";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function FlowSection() {
  return (
    <SectionShell
      id="flujo"
      eyebrow="Flujo conversacional"
      title="Sistema de triage, no chatbot genérico."
      copy="El bot reconoce 13+ comandos universales (menu, ayuda, privacidad, estado, reset, reporte) que funcionan en cualquier estado. Distingue cierres conversacionales (gracias, ok, bye, no) de mensajes a analizar. Detecta distress (tengo miedo, necesito ayuda) y responde con empatía + Línea de la Vida 800-911-2000 antes de pedir el contenido sospechoso."
    >
      <Reveal>
        <FlowDiagram />
      </Reveal>
    </SectionShell>
  );
}
