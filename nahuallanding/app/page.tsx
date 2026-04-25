import { ArchitectureSection } from "@/components/sections/architecture-section";
import { ClassifierSection } from "@/components/sections/classifier-section";
import { AdvancedFeaturesSection } from "@/components/sections/advanced-features-section";
import { FlowSection } from "@/components/sections/flow-section";
import { FooterSection } from "@/components/sections/footer-section";
import { HeroSection } from "@/components/sections/hero-section";
import { ImpactSourcesSection } from "@/components/sections/impact-sources-section";
import { OutputsSection } from "@/components/sections/outputs-section";
import { ProblemSection } from "@/components/sections/problem-section";
import { RoadmapTeamSection } from "@/components/sections/roadmap-team-section";
import { SolutionSection } from "@/components/sections/solution-section";
import { ValidationSection } from "@/components/sections/validation-section";

export default function HomePage() {
  return (
    <main className="site-shell">
      <HeroSection />
      <ProblemSection />
      <SolutionSection />
      <ValidationSection />
      <ArchitectureSection />
      <ClassifierSection />
      <AdvancedFeaturesSection />
      <FlowSection />
      <OutputsSection />
      <RoadmapTeamSection />
      <ImpactSourcesSection />
      <FooterSection />
    </main>
  );
}
