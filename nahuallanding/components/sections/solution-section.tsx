import { MessageCircleMore, PanelsTopLeft } from "lucide-react";

import { BrowserShieldMockup } from "@/components/mockups/browser-shield-mockup";
import { ChatMockup } from "@/components/mockups/chat-mockup";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

export function SolutionSection() {
  return (
    <SectionShell
      id="solucion"
      eyebrow="La solución"
      title="Tres superficies. Un solo cerebro de 4 capas."
      copy="Nahual entra donde el riesgo aparece: en la conversación reactiva (bot WhatsApp), en el monitoreo proactivo (extensión Chrome) y en la operación institucional (panel web). Las tres comparten el mismo clasificador con heurístico, Bayesiano, Sonnet 4.5 y detector de trayectoria."
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <Reveal className="panel p-6">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <p className="terminal-text text-cobre-light">modo reactivo</p>
              <h3 className="mt-3 text-3xl font-black text-cream">Bot de WhatsApp</h3>
            </div>
            <span className="rounded-full border border-[rgba(37,211,102,0.18)] bg-[rgba(37,211,102,0.12)] p-3 text-[#25d366]">
              <MessageCircleMore className="h-5 w-5" />
            </span>
          </div>
          <p className="mb-6 max-w-xl text-dim">
            El menor pega o reenvía un mensaje sospechoso (texto, audio, captura). Nahual clasifica el riesgo, explica <em>por qué</em> con los pattern_ids que matchearon, y sugiere el siguiente paso. Soporta 13+ comandos universales (menu, ayuda, privacidad, reset, reporte) y detección de distress (Línea de la Vida + 088).
          </p>
          <ChatMockup />
        </Reveal>

        <Reveal delay={0.1} className="panel p-6">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <p className="terminal-text text-cobre-light">modo proactivo · v1.3.0</p>
              <h3 className="mt-3 text-3xl font-black text-cream">Nahual Shield</h3>
            </div>
            <span className="rounded-full border border-[rgba(245,240,235,0.1)] bg-[rgba(245,240,235,0.04)] p-3 text-cream">
              <PanelsTopLeft className="h-5 w-5" />
            </span>
          </div>
          <p className="mb-6 max-w-xl text-dim">
            Extensión Chrome (Manifest V3) que monitorea WhatsApp Web · Instagram · Discord · Roblox. URL allowlist + whitelist + scope al chat container para evitar falsos positivos en catálogos / store / settings. Overlay con CTA al bot vía wa.me deeplink.
          </p>
          <BrowserShieldMockup />
        </Reveal>
      </div>
    </SectionShell>
  );
}
