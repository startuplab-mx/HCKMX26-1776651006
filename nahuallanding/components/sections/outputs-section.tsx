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
          <p className="terminal-text mb-4 text-cobre-light">panel de alertas · live</p>
          <h3 className="mb-4 text-3xl font-black text-cream">Monitoreo en tiempo real para padres e instituciones</h3>
          <p className="mb-6 max-w-2xl text-dim">
            Auto-refresh cada 5s · manual analyze textbox · 🔬 deep healthcheck (DB+Anthropic+Groq) · 🚨 PELIGRO toast con audio cue · filtros por estado · CSV export. <a href="http://159.223.187.6/" target="_blank" rel="noreferrer" className="text-cobre-light underline">Verlo en vivo →</a>
          </p>
          <DashboardPreview />
        </Reveal>
        <Reveal delay={0.1} className="panel p-6">
          <p className="terminal-text mb-4 text-cobre-light">reporte forense PDF</p>
          <h3 className="mb-4 text-3xl font-black text-cream">Listo para Fiscalía. Generado en segundos.</h3>
          <p className="mb-6 text-dim">
            Folio NAH-2026-XXXX · marco legal mexicano (LGDNNA Art. 47 + 101 Bis 2, CPF 209 Sextus, Ley Olimpia, LGAMVLV 20 Quáter) · autoridades + derechos · sin PII original (solo SHA-256 + categorías).
          </p>
          <PdfPreview />
        </Reveal>
      </div>
    </SectionShell>
  );
}
