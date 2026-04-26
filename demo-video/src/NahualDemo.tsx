import React from "react";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { wipe } from "@remotion/transitions/wipe";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { COLORS } from "./colors";
import { BackgroundMusic } from "./components/BackgroundMusic";

import { Scene1_Hook } from "./scenes/Scene1_Hook";
import { Scene2_Problem } from "./scenes/Scene2_Problem";
import { Scene3_Solution } from "./scenes/Scene3_Solution";
import { Scene4_Brain } from "./scenes/Scene4_Brain";
import { Scene5_BotDemo } from "./scenes/Scene5_BotDemo";
import { Scene6_Multimedia } from "./scenes/Scene6_Multimedia";
import { Scene7_Extension } from "./scenes/Scene7_Extension";
import { Scene8_Dashboard } from "./scenes/Scene8_Dashboard";
import { Scene9_Privacy } from "./scenes/Scene9_Privacy";
import { Scene10_Platform } from "./scenes/Scene10_Platform";
import { Scene11_Close } from "./scenes/Scene11_Close";

const TRANSITION_FRAMES = 30;

export const NahualDemo: React.FC = () => {
  return (
    <div
      style={{
        background: COLORS.darkGray,
        width: "100%",
        height: "100%",
        fontFamily: "Inter, system-ui, sans-serif",
        position: "relative",
      }}
    >
      <BackgroundMusic />

      <TransitionSeries>
        {/* Scene 1: Cold Open / Hook — 18s / 540 frames */}
        <TransitionSeries.Sequence durationInFrames={540}>
          <Scene1_Hook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={clockWipe()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 2: El Problema — 20s / 600 frames */}
        <TransitionSeries.Sequence durationInFrames={600}>
          <Scene2_Problem />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={wipe()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 3: Enter Nahual — 14s / 420 frames */}
        <TransitionSeries.Sequence durationInFrames={420}>
          <Scene3_Solution />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 4: El Cerebro — 20s / 600 frames */}
        <TransitionSeries.Sequence durationInFrames={600}>
          <Scene4_Brain />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 5: Bot Demo — 30s / 900 frames */}
        <TransitionSeries.Sequence durationInFrames={900}>
          <Scene5_BotDemo />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 6: Multimedia — 13s / 390 frames */}
        <TransitionSeries.Sequence durationInFrames={390}>
          <Scene6_Multimedia />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={wipe()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 7: Extension Shield — 15s / 450 frames */}
        <TransitionSeries.Sequence durationInFrames={450}>
          <Scene7_Extension />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={clockWipe()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 8: Panel Dashboard — 18s / 540 frames */}
        <TransitionSeries.Sequence durationInFrames={540}>
          <Scene8_Dashboard />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 9: Privacy + Legal — 12s / 360 frames */}
        <TransitionSeries.Sequence durationInFrames={360}>
          <Scene9_Privacy />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 10: NahualPlatform — 12s / 360 frames */}
        <TransitionSeries.Sequence durationInFrames={360}>
          <Scene10_Platform />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
        />

        {/* Scene 11: Closing — 8s / 240 frames */}
        <TransitionSeries.Sequence durationInFrames={240}>
          <Scene11_Close />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </div>
  );
};
