import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

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

const siteUrl = "https://nahual-landing.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Nahual — Detección de Reclutamiento Criminal Digital",
  description:
    "Sistema de detección de reclutamiento criminal digital para menores en México. Bot de WhatsApp + Extensión de navegador + análisis modular.",
  openGraph: {
    title: "Nahual — Protección Digital para Menores",
    description:
      "El primer sistema en México diseñado para detectar reclutamiento criminal digital antes de que el menor desaparezca.",
    images: ["/opengraph-image"],
    locale: "es_MX",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Nahual — Protección Digital para Menores",
    description:
      "Bot de WhatsApp, extensión y clasificador para detectar reclutamiento criminal digital."
  }
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
