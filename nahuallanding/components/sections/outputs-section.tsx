import { DashboardPreview } from "@/components/mockups/dashboard-preview";
import { PdfPreview } from "@/components/mockups/pdf-preview";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function OutputsSection() {
  return (
    <SectionShell
      id="outputs"
      eyebrow="Outputs institucionales"
      title="Visibilidad operativa para actuar, no solo para observar."
      copy="La demostración no termina en la alerta. Nahual también muestra cómo se vería la operación diaria y cómo se empaquetaría la evidencia para canalización o denuncia."
    >
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Reveal className="panel p-6">
          <p className="terminal-text mb-4 text-cobre-light">panel de alertas</p>
          <h3 className="mb-4 text-3xl font-black text-cream">Monitoreo en tiempo real para padres e instituciones</h3>
          <p className="mb-6 max-w-2xl text-dim">
            Vista centralizada de alertas con score, plataforma, nivel de riesgo y generación inmediata de reporte PDF para escalar el caso.
          </p>
          <DashboardPreview />
        </Reveal>
        <Reveal delay={0.1} className="panel p-6">
          <p className="terminal-text mb-4 text-cobre-light">reporte de incidente</p>
          <h3 className="mb-4 text-3xl font-black text-cream">Listo para Fiscalía. Generado en segundos.</h3>
          <p className="mb-6 text-dim">
            El reporte resume evidencia, interpretación del score, metadatos y rutas mínimas de acción para no perder tiempo cuando el caso ya pasó de señal a incidente.
          </p>
          <PdfPreview />
        </Reveal>
      </div>
    </SectionShell>
  );
}
