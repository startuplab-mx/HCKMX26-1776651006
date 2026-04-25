"use client";

import { motion } from "framer-motion";
import { Mic, Activity, ShieldCheck, Scale } from "lucide-react";
import { site } from "@/content/site";
import { SectionShell } from "@/components/ui/section-shell";
import { Reveal } from "@/components/ui/reveal";

const iconMap: Record<string, React.ReactNode> = {
  mic: <Mic size={28} className="text-[#d4845a]" />,
  activity: <Activity size={28} className="text-[#d4845a]" />,
  shield: <ShieldCheck size={28} className="text-[#d4845a]" />,
  scale: <Scale size={28} className="text-[#d4845a]" />
};

export function AdvancedFeaturesSection() {
  return (
    <SectionShell id="capacidades">
      <Reveal>
        <div className="flex items-center gap-4 mb-4">
          <div className="h-0.5 w-12 bg-[#c16a4c]" />
          <h2 className="text-3xl md:text-5xl font-bold uppercase tracking-tight text-[#f5f0eb]">
            Bajo el Capó
          </h2>
        </div>
        <p className="text-[#f5f0eb]/70 text-lg md:text-xl max-w-2xl mb-16">
          Más allá de lo evidente, Nahual incorpora mecanismos profundos que elevan su categoría de herramienta preventiva a protocolo de inteligencia digital.
        </p>
      </Reveal>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8 relative z-10">
        {site.advancedFeatures.map((feature, idx) => (
          <Reveal key={feature.id} delay={0.1 * idx}>
            <div
              className="flex flex-col gap-5 p-8 lg:p-10 rounded-2xl bg-[#3a4249]/20 border border-[#f5f0eb]/5 hover:border-[#c16a4c]/30 hover:bg-[#3a4249]/40 transition-all duration-500 ease-out h-full group"
            >
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-xl bg-[#0d1013]/60 flex items-center justify-center border border-[#f5f0eb]/5 group-hover:scale-110 group-hover:border-[#c16a4c]/40 transition-all duration-300">
                  {iconMap[feature.icon]}
                </div>
                <h3 className="text-xl lg:text-2xl font-bold tracking-tight text-[#f5f0eb] leading-tight">
                  {feature.title}
                </h3>
              </div>
              <p className="text-[#f5f0eb]/70 leading-relaxed text-base lg:text-lg">
                {feature.description}
              </p>
            </div>
          </Reveal>
        ))}
      </div>
    </SectionShell>
  );
}
