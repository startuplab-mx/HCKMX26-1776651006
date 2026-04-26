import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

const StatBlock: React.FC<{
  value: string;
  label: string;
  color: string;
  opacity: number;
  scale: number;
}> = ({ value, label, color, opacity, scale }) => (
  <div
    style={{
      opacity,
      transform: `scale(${scale})`,
      display: "flex",
      alignItems: "center",
      gap: 24,
      marginBottom: 20,
    }}
  >
    <span
      style={{
        fontSize: 72,
        fontWeight: 900,
        color,
        letterSpacing: -2,
      }}
    >
      {value}
    </span>
    <span
      style={{
        fontSize: 28,
        color: COLORS.cream,
        opacity: 0.8,
        maxWidth: 500,
      }}
    >
      {label}
    </span>
  </div>
);

export const Scene1_Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Headline fade in
  const headlineOpacity = interpolate(frame, [0, 40], [0, 1], {
    extrapolateRight: "clamp",
  });
  const headlineY = interpolate(frame, [0, 40], [30, 0], {
    extrapolateRight: "clamp",
  });
  // Headline fades out before stats
  const headlineFadeOut = interpolate(frame, [80, 100], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stat 1: +20.6%
  const stat1Spring = spring({ frame: frame - 100, fps, durationInFrames: 30 });
  const stat1Value = interpolate(frame, [100, 160], [0, 20.6], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stat 2: +56%
  const stat2Spring = spring({ frame: frame - 180, fps, durationInFrames: 30 });
  const stat2Value = interpolate(frame, [180, 230], [0, 56], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stat 3: 22.9M
  const stat3Spring = spring({ frame: frame - 260, fps, durationInFrames: 30 });
  const stat3Value = interpolate(frame, [260, 310], [0, 22.9], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stats fade out
  const statsFadeOut = interpolate(frame, [340, 360], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Final question
  const questionOpacity = interpolate(frame, [370, 400], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const questionScale = spring({
    frame: frame - 370,
    fps,
    durationInFrames: 20,
    config: { mass: 0.5, damping: 10 },
  });

  // Final fade to black
  const fadeToBlack = interpolate(frame, [430, 450], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: 120,
        background: COLORS.darkGray,
        position: "relative",
      }}
    >
      {/* Headline */}
      {frame < 100 && (
        <div
          style={{
            opacity: headlineOpacity * headlineFadeOut,
            transform: `translateY(${headlineY}px)`,
            fontSize: 36,
            color: COLORS.cream,
            textAlign: "center",
            lineHeight: 1.5,
            maxWidth: 1100,
            fontWeight: 300,
          }}
        >
          Esta semana, Infobae reporto que el crimen organizado traslado el
          reclutamiento de jovenes al{" "}
          <span style={{ color: COLORS.cobre, fontWeight: 700 }}>
            entorno digital
          </span>
          .
        </div>
      )}

      {/* Stats */}
      {frame >= 100 && frame < 360 && (
        <div style={{ opacity: statsFadeOut }}>
          <StatBlock
            value={`+${stat1Value.toFixed(1)}%`}
            label="Reclutamiento de adolescentes (REDIM 2025)"
            color={COLORS.red}
            opacity={stat1Spring}
            scale={stat1Spring}
          />
          <StatBlock
            value={`+${Math.round(stat2Value)}%`}
            label="Sextorsion digital (Consejo Ciudadano)"
            color={COLORS.yellow}
            opacity={stat2Spring}
            scale={stat2Spring}
          />
          <StatBlock
            value={`${stat3Value.toFixed(1)}M`}
            label="Menores conectados a internet (INEGI)"
            color={COLORS.cobre}
            opacity={stat3Spring}
            scale={stat3Spring}
          />
        </div>
      )}

      {/* Final question */}
      {frame >= 370 && (
        <div
          style={{
            opacity: questionOpacity,
            transform: `scale(${questionScale})`,
            fontSize: 80,
            fontWeight: 900,
            color: COLORS.cream,
            textAlign: "center",
          }}
        >
          Quien los protege?
        </div>
      )}

      {/* Fade to black overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "black",
          opacity: fadeToBlack,
        }}
      />
    </div>
  );
};
