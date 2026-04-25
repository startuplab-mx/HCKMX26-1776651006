"use client";

import { ArrowDown, ArrowUpRight, ShieldAlert } from "lucide-react";

import { site } from "@/content/site";
import { NahualGlyph } from "@/components/graphics/nahual-glyph";
import { NetworkGrid } from "@/components/graphics/network-grid";
import { CountUp } from "@/components/ui/count-up";
import { Reveal } from "@/components/ui/reveal";

export function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden border-b border-[rgba(245,240,235,0.08)]">
      <NetworkGrid />
      <div className="section-wrap flex min-h-screen flex-col justify-center pt-28">
        <div className="grid items-center gap-12 lg:grid-cols-[1.02fr_0.98fr]">
          <div className="relative z-10">
            <Reveal>
              <div className="eyebrow">
                <ShieldAlert className="h-4 w-4" />
                {site.badge}
              </div>
            </Reveal>
            <Reveal delay={0.08}>
              <p className="terminal-text mb-5 text-cobre-light">protección digital / mx / 2026</p>
            </Reveal>
            <Reveal delay={0.12}>
              <h1 className="max-w-4xl text-balance font-display text-[3.55rem] font-black leading-[0.84] text-cream sm:text-[5.4rem] lg:text-[8rem]">
                {site.heroTitle}
              </h1>
            </Reveal>
            <Reveal delay={0.18}>
              <p className="mt-5 max-w-3xl text-[1.92rem] font-semibold leading-tight text-[rgba(245,240,235,0.86)] sm:text-3xl">
                {site.heroLabel}
              </p>
            </Reveal>
            <Reveal delay={0.24}>
              <p className="mt-6 max-w-2xl text-xl font-semibold leading-8 text-cream sm:text-2xl">
                {site.heroTagline}
              </p>
            </Reveal>
            <Reveal delay={0.3}>
              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <a
                  href="#problema"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-[rgba(193,106,76,0.26)] bg-cobre px-6 py-3 text-sm font-semibold text-white transition hover:bg-cobre-light"
                >
                  Conoce el sistema
                  <ArrowDown className="h-4 w-4" />
                </a>
                <a
                  href={site.repoUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-[rgba(245,240,235,0.12)] bg-[rgba(245,240,235,0.04)] px-6 py-3 text-sm font-semibold text-cream transition hover:border-[rgba(193,106,76,0.28)] hover:text-cobre-light"
                >
                  <ArrowUpRight className="h-4 w-4" />
                  GitHub
                </a>
              </div>
            </Reveal>
            <Reveal delay={0.34}>
              <p className="mt-6 max-w-2xl text-base leading-7 text-[rgba(245,240,235,0.68)] sm:text-lg sm:leading-8">
                <span className="sm:hidden">
                  Bot de WhatsApp, extensión y clasificador para alertas tempranas en conversaciones digitales.
                </span>
                <span className="hidden sm:block">{site.heroCopy}</span>
              </p>
            </Reveal>
            <Reveal delay={0.4}>
              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                {site.heroMetrics.map((metric) => (
                  <div key={metric.label} className="panel p-5">
                    <p className="terminal-text mb-4 text-cobre-light">validación</p>
                    <CountUp
                      value={metric.value}
                      suffix={metric.suffix}
                      className="text-4xl font-black text-cream"
                    />
                    <p className="mt-3 text-sm font-semibold leading-6 text-[rgba(245,240,235,0.84)]">
                      {metric.label}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-[rgba(245,240,235,0.56)]">{metric.detail}</p>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.14} className="relative z-10">
            <NahualGlyph />
          </Reveal>
        </div>

        <Reveal delay={0.46}>
          <div className="mt-12 grid gap-4 lg:grid-cols-3">
            {site.signalTape.map((item) => (
              <div key={item} className="signal-line rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(15,17,20,0.5)] px-5 py-4">
                <p className="text-sm leading-7 text-[rgba(245,240,235,0.66)]">{item}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
