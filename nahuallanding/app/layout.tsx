import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

// @ts-ignore
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap"
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap"
});

const siteUrl = "https://nahualsec.com";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Nahual — Detección de Reclutamiento Criminal Digital",
  description:
    "Sistema de 4 capas cognitivas (heurístico + bayesiano + LLM + trayectoria) para detectar captación criminal en WhatsApp, Instagram, Discord y Roblox. 900 patrones, 99.6% accuracy en suite de validación. Bot live en producción.",
  keywords: [
    "reclutamiento criminal",
    "detección menores",
    "México",
    "sextorsión",
    "WhatsApp bot",
    "clasificador de riesgo",
    "Bayesian Naive",
    "Claude API",
    "open source",
    "hackathon 404",
  ],
  authors: [{ name: "Equipo Vanguard — Armando Flores & Marco Espinosa" }],
  openGraph: {
    title: "Nahual — Protección Digital para Menores en México",
    description:
      "El primer sistema en México con 4 capas cognitivas para detectar reclutamiento criminal digital. Heurístico (900 patrones) + Naive Bayes (1031 docs) + Claude Sonnet 4.5 + detector de trayectoria. Live en +52 844 538 7404.",
    images: ["/opengraph-image"],
    locale: "es_MX",
    type: "website",
    siteName: "Nahual",
    url: siteUrl,
  },
  twitter: {
    card: "summary_large_image",
    title: "Nahual — Detección de reclutamiento criminal en menores · MX",
    description:
      "4 capas cognitivas · 900 patrones · 99.6% accuracy · Bot WhatsApp + extensión Chrome + panel web · Privacy-first (Art. 16 CPEUM).",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es-MX" className="scroll-smooth">
      <body
        className={`${inter.variable} ${mono.variable} bg-carbon-dark font-sans text-cream antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
