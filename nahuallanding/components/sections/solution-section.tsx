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
      title="Dos modos de protección. Un solo objetivo."
      copy="Nahual entra donde el riesgo aparece: primero en la conversación, después en la evidencia. Un canal reactivo para ayuda inmediata y un canal proactivo para monitoreo contextual."
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
            El menor pega o reenvía un mensaje sospechoso. Nahual clasifica el riesgo, explica por qué lo considera peligroso y sugiere el siguiente paso sin quitar control al usuario.
          </p>
          <ChatMockup />
        </Reveal>

        <Reveal delay={0.1} className="panel p-6">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <p className="terminal-text text-cobre-light">modo proactivo</p>
              <h3 className="mt-3 text-3xl font-black text-cream">Nahual Shield</h3>
            </div>
            <span className="rounded-full border border-[rgba(245,240,235,0.1)] bg-[rgba(245,240,235,0.04)] p-3 text-cream">
              <PanelsTopLeft className="h-5 w-5" />
            </span>
          </div>
          <p className="mb-6 max-w-xl text-dim">
            La extensión monitorea texto visible en web y detecta señales de captación en tiempo real sobre WhatsApp Web, Instagram o Discord, con la opción de escalar directo al bot.
          </p>
          <BrowserShieldMockup />
        </Reveal>
      </div>
    </SectionShell>
  );
}
