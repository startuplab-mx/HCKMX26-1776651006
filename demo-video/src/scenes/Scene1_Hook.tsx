import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

import { ParticleField } from "../components/ParticleField";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { GlowText } from "../components/GlowText";

const StatBlock: React.FC<{
  children: React.ReactNode;
  label: string;
  color: string;
  opacity: number;
  scale: number;
}> = ({ children, label, color, opacity, scale }) => (
  <div
    style={{
      opacity,
      transform: `scale(${scale})`,
      display: "flex",
      alignItems: "center",
      gap: 24,
      marginBottom: 24,
    }}
  >
    <span
      style={{
        fontSize: 76,
        fontWeight: 900,
        color,
        letterSpacing: -2,
      }}
    >
      {children}
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

  // Headline fade in (0-50)
  const headlineOpacity = interpolate(frame, [0, 50], [0, 1], {
    extrapolateRight: "clamp",
  });
  const headlineY = interpolate(frame, [0, 50], [30, 0], {
    extrapolateRight: "clamp",
  });
  // Headline fades out before stats
  const headlineFadeOut = interpolate(frame, [100, 130], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stat springs (staggered)
  const stat1Spring = spring({ frame: frame - 140, fps, durationInFrames: 30 });
  const stat2Spring = spring({ frame: frame - 210, fps, durationInFrames: 30 });
  const stat3Spring = spring({ frame: frame - 280, fps, durationInFrames: 30 });

  // Stats fade out
  const statsFadeOut = interpolate(frame, [380, 410], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Final question with screen shake + red flash
  const questionOpacity = interpolate(frame, [430, 460], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const questionScale = spring({
    frame: frame - 430,
    fps,
    durationInFrames: 20,
    config: { mass: 0.5, damping: 10 },
  });

  // Screen shake effect on "¿Quién los protege?"
  const shakeActive = frame >= 430 && frame < 470;
  const shakeX = shakeActive ? Math.sin(frame * 1.2) * 6 : 0;
  const shakeY = shakeActive ? Math.cos(frame * 1.5) * 4 : 0;

  // Red flash at impact moment
  const redFlash = interpolate(frame, [430, 440, 460], [0, 0.25, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Final fade to black
  const fadeToBlack = interpolate(frame, [510, 540], [0, 1], {
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
        transform: `translate(${shakeX}px, ${shakeY}px)`,
      }}
    >
      <ParticleField count={40} />

      {/* Headline */}
      {frame < 130 && (
        <div
          style={{
            opacity: headlineOpacity * headlineFadeOut,
            transform: `translateY(${headlineY}px)`,
            fontSize: 38,
            color: COLORS.cream,
            textAlign: "center",
            lineHeight: 1.5,
            maxWidth: 1100,
            fontWeight: 300,
            zIndex: 10,
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

      {/* Animated Stats */}
      {frame >= 140 && frame < 410 && (
        <div style={{ opacity: statsFadeOut, zIndex: 10 }}>
          <StatBlock
            label="Reclutamiento de adolescentes (REDIM 2025)"
            color={COLORS.red}
            opacity={stat1Spring}
            scale={stat1Spring}
          >
            <AnimatedCounter
              to={20.6}
              startFrame={140}
              duration={60}
              decimals={1}
              prefix="+"
              suffix="%"
              style={{ color: "inherit", fontSize: "inherit", fontWeight: "inherit" }}
            />
          </StatBlock>
          <StatBlock
            label="Sextorsion digital (Consejo Ciudadano)"
            color={COLORS.yellow}
            opacity={stat2Spring}
            scale={stat2Spring}
          >
            <AnimatedCounter
              to={56}
              startFrame={210}
              duration={50}
              prefix="+"
              suffix="%"
              style={{ color: "inherit", fontSize: "inherit", fontWeight: "inherit" }}
            />
          </StatBlock>
          <StatBlock
            label="Menores conectados a internet (INEGI)"
            color={COLORS.cobre}
            opacity={stat3Spring}
            scale={stat3Spring}
          >
            <AnimatedCounter
              to={22.9}
              startFrame={280}
              duration={50}
              decimals={1}
              suffix="M"
              style={{ color: "inherit", fontSize: "inherit", fontWeight: "inherit" }}
            />
          </StatBlock>
        </div>
      )}

      {/* Final question */}
      {frame >= 430 && (
        <div
          style={{
            opacity: questionOpacity,
            transform: `scale(${questionScale})`,
            textAlign: "center",
            zIndex: 10,
          }}
        >
          <GlowText
            text="¿Quien los protege?"
            fontSize={84}
            color={COLORS.cream}
            glowColor={COLORS.cobreGlow}
          />
        </div>
      )}

      {/* Red flash overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: COLORS.red,
          opacity: redFlash,
          pointerEvents: "none",
          zIndex: 90,
        }}
      />

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
          zIndex: 95,
        }}
      />
    </div>
  );
};
