import { Sequence } from "remotion";
import { Scene1_Hook } from "./scenes/Scene1_Hook";
import { Scene2_Problem } from "./scenes/Scene2_Problem";
import { Scene3_Solution } from "./scenes/Scene3_Solution";
import { Scene4_BotDemo } from "./scenes/Scene4_BotDemo";
import { Scene5_Extension } from "./scenes/Scene5_Extension";
import { Scene6_Platform } from "./scenes/Scene6_Platform";
import { Scene7_Close } from "./scenes/Scene7_Close";
import { COLORS } from "./colors";

export const NahualDemo: React.FC = () => {
  return (
    <div
      style={{
        background: COLORS.darkGray,
        width: "100%",
        height: "100%",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      {/* Scene 1: Hook emocional (0-15s) */}
      <Sequence from={0} durationInFrames={450}>
        <Scene1_Hook />
      </Sequence>

      {/* Scene 2: El problema (15-30s) */}
      <Sequence from={450} durationInFrames={450}>
        <Scene2_Problem />
      </Sequence>

      {/* Scene 3: Que es Nahual (30-45s) */}
      <Sequence from={900} durationInFrames={450}>
        <Scene3_Solution />
      </Sequence>

      {/* Scene 4: Demo del bot (45-75s) */}
      <Sequence from={1350} durationInFrames={900}>
        <Scene4_BotDemo />
      </Sequence>

      {/* Scene 5: Extension + Panel (75-90s) */}
      <Sequence from={2250} durationInFrames={450}>
        <Scene5_Extension />
      </Sequence>

      {/* Scene 6: NahualPlatform / Datos (90-105s) */}
      <Sequence from={2700} durationInFrames={450}>
        <Scene6_Platform />
      </Sequence>

      {/* Scene 7: Cierre + CTA (105-120s) */}
      <Sequence from={3150} durationInFrames={450}>
        <Scene7_Close />
      </Sequence>
    </div>
  );
};
