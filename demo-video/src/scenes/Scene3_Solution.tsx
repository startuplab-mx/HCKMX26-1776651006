import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

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

  // Title text
  const titleOpacity = interpolate(frame, [30, 55], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [30, 55], [20, 0], {
    extrapolateRight: "clamp",
  });

  // Stats bar at bottom
  const statsOpacity = interpolate(frame, [300, 330], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(frame, [430, 450], [1, 0], {
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
      {/* Nahual shield logo */}
      <div
        style={{
          transform: `scale(${logoScale})`,
          fontSize: 64,
          marginBottom: 10,
        }}
      >
        🛡️
      </div>

      {/* Title */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          textAlign: "center",
          marginBottom: 80,
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 900,
            color: COLORS.cobre,
            letterSpacing: 6,
            marginBottom: 16,
          }}
        >
          NAHUAL
        </div>
        <div
          style={{
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
        }}
      >
        <Pillar
          icon="💬"
          title="Bot de WhatsApp"
          subtitle="Canal reactivo"
          delay={120}
        />
        <Pillar
          icon="🔍"
          title="Extension de navegador"
          subtitle="Deteccion proactiva"
          delay={170}
        />
        <Pillar
          icon="📊"
          title="Panel de inteligencia"
          subtitle="Dataset abierto"
          delay={220}
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
        }}
      >
        <span>870 patrones verificados</span>
        <span style={{ color: COLORS.cream, opacity: 0.3 }}>|</span>
        <span>4 capas cognitivas</span>
        <span style={{ color: COLORS.cream, opacity: 0.3 }}>|</span>
        <span>Marco legal de 12 articulos</span>
      </div>
    </div>
  );
};
