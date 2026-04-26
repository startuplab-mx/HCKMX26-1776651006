import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

import { ParticleField } from "../components/ParticleField";

const NAHUAL_LETTERS = "NAHUAL".split("");

const Pillar: React.FC<{
  icon: string;
  title: string;
  subtitle: string;
  delay: number;
}> = ({ icon, title, subtitle, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, durationInFrames: 25 });

  return (
    <div
      style={{
        opacity: s,
        transform: `translateY(${(1 - s) * 40}px)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: 380,
        textAlign: "center",
      }}
    >
      <div
        style={{
          width: 100,
          height: 100,
          borderRadius: 24,
          background: `linear-gradient(135deg, ${COLORS.cobre}, ${COLORS.cobreLight})`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 48,
          marginBottom: 24,
        }}
      >
        {icon}
      </div>
      <div
        style={{
          fontSize: 28,
          fontWeight: 700,
          color: COLORS.cream,
          marginBottom: 8,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 20,
          color: COLORS.cream,
          opacity: 0.6,
        }}
      >
        {subtitle}
      </div>
    </div>
  );
};

export const Scene3_Solution: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in from black
  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Shield logo animation
  const logoScale = spring({ frame, fps, durationInFrames: 30 });

  // Letter-by-letter reveal for "NAHUAL"
  const letterDelay = 6; // frames between each letter
  const letterStart = 30;

  // Glow rings expanding from logo
  const ringCount = 3;
  const ringStart = 50;

  // Subtitle
  const subtitleOpacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateRight: "clamp",
  });
  const subtitleY = interpolate(frame, [80, 110], [20, 0], {
    extrapolateRight: "clamp",
  });

  // Stats bar at bottom
  const statsOpacity = interpolate(frame, [300, 330], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(frame, [395, 420], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: COLORS.darkGray,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeIn * fadeOut,
        position: "relative",
      }}
    >
      <ParticleField count={35} />

      {/* Shield logo with glow rings */}
      <div
        style={{
          position: "relative",
          transform: `scale(${logoScale})`,
          marginBottom: 10,
          zIndex: 10,
        }}
      >
        {/* Glow rings */}
        {Array.from({ length: ringCount }).map((_, i) => {
          const ringFrame = frame - ringStart - i * 20;
          const ringScale = ringFrame > 0
            ? interpolate(ringFrame, [0, 60], [0.5, 2.5 + i * 0.8], { extrapolateRight: "clamp" })
            : 0;
          const ringOpacity = ringFrame > 0
            ? interpolate(ringFrame, [0, 60], [0.6, 0], { extrapolateRight: "clamp" })
            : 0;

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                width: 80,
                height: 80,
                borderRadius: "50%",
                border: `2px solid ${COLORS.cobreGlow}`,
                transform: `translate(-50%, -50%) scale(${ringScale})`,
                opacity: ringOpacity,
                pointerEvents: "none",
              }}
            />
          );
        })}
        <div style={{ fontSize: 64, position: "relative", zIndex: 2 }}>🛡️</div>
      </div>

      {/* Title — letter-by-letter */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 80,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontSize: 72,
            fontWeight: 900,
            letterSpacing: 8,
            marginBottom: 16,
            display: "flex",
            justifyContent: "center",
          }}
        >
          {NAHUAL_LETTERS.map((letter, i) => {
            const lFrame = frame - letterStart - i * letterDelay;
            const lOpacity = interpolate(lFrame, [0, 8], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const lY = interpolate(lFrame, [0, 8], [20, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const glowPulse =
              lFrame > 10 ? 6 + 4 * Math.sin((frame - letterStart) * 0.06 + i * 0.5) : 0;

            return (
              <span
                key={i}
                style={{
                  color: COLORS.cobre,
                  opacity: lOpacity,
                  transform: `translateY(${lY}px)`,
                  display: "inline-block",
                  textShadow: `0 0 ${glowPulse}px ${COLORS.cobreGlow}`,
                }}
              >
                {letter}
              </span>
            );
          })}
        </div>
        <div
          style={{
            opacity: subtitleOpacity,
            transform: `translateY(${subtitleY}px)`,
            fontSize: 28,
            fontWeight: 300,
            color: COLORS.cream,
            maxWidth: 900,
          }}
        >
          El primer sistema de deteccion de reclutamiento criminal digital en
          Mexico
        </div>
      </div>

      {/* 3 Pillars */}
      <div
        style={{
          display: "flex",
          gap: 80,
          justifyContent: "center",
          zIndex: 10,
        }}
      >
        <Pillar
          icon="💬"
          title="Bot de WhatsApp"
          subtitle="Canal reactivo"
          delay={140}
        />
        <Pillar
          icon="🔍"
          title="Extension de navegador"
          subtitle="Deteccion proactiva"
          delay={190}
        />
        <Pillar
          icon="📊"
          title="Panel de inteligencia"
          subtitle="Dataset abierto"
          delay={240}
        />
      </div>

      {/* Stats bar */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          opacity: statsOpacity,
          display: "flex",
          gap: 40,
          fontSize: 22,
          color: COLORS.cobreLight,
          fontWeight: 600,
          zIndex: 10,
        }}
      >
        <span>900 patrones verificados</span>
        <span style={{ color: COLORS.cream, opacity: 0.3 }}>|</span>
        <span>4 capas cognitivas</span>
        <span style={{ color: COLORS.cream, opacity: 0.3 }}>|</span>
        <span>Marco legal de 12 articulos</span>
      </div>
    </div>
  );
};
