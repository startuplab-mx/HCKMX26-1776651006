import { site } from "@/content/site";

export function FooterSection() {
  return (
    <footer className="border-t border-[rgba(245,240,235,0.08)]">
      <div className="section-wrap py-10">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-2xl font-black text-cream">Nahual</p>
            <p className="mt-2 text-sm leading-7 text-dim">
              Sistema de Detección de Reclutamiento Criminal Digital · Open Source · Licencia MIT
            </p>
            <p className="text-sm leading-7 text-dim">
              Hackathon 404: Threat Not Found 2026 · Equipo Vanguard — Armando Flores & Marco Espinosa
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <a
              href={site.repoUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-[rgba(245,240,235,0.12)] px-4 py-2 text-sm font-semibold text-cream transition hover:border-[rgba(193,106,76,0.28)] hover:text-cobre-light"
            >
              GitHub
            </a>
            <a
              href="#arquitectura"
              className="rounded-full border border-[rgba(245,240,235,0.12)] px-4 py-2 text-sm font-semibold text-cream transition hover:border-[rgba(193,106,76,0.28)] hover:text-cobre-light"
            >
              Arquitectura
            </a>
            <a
              href="mailto:equipo@nahual.ai"
              className="rounded-full border border-[rgba(245,240,235,0.12)] px-4 py-2 text-sm font-semibold text-cream transition hover:border-[rgba(193,106,76,0.28)] hover:text-cobre-light"
            >
              Contacto
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
