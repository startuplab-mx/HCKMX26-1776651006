import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

const PlatformIcon: React.FC<{
  name: string;
  color: string;
  delay: number;
}> = ({ name, color, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, durationInFrames: 20 });

  return (
    <div
      style={{
        opacity: s,
        transform: `scale(${s}) rotate(${(1 - s) * 15}deg)`,
        background: color,
        borderRadius: 20,
        width: 120,
        height: 120,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 16,
        fontWeight: 700,
        color: COLORS.white,
        textAlign: "center",
        lineHeight: 1.2,
      }}
    >
      {name}
    </div>
  );
};

const EmojiFloat: React.FC<{
  emoji: string;
  label: string;
  x: number;
  y: number;
  delay: number;
}> = ({ emoji, label, x, y, delay }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 20], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const float = Math.sin((frame - delay) * 0.05) * 8;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y + float,
        opacity,
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 56 }}>{emoji}</div>
      <div
        style={{
          fontSize: 14,
          color: COLORS.cobreLight,
          marginTop: 4,
          fontWeight: 600,
        }}
      >
        = {label}
      </div>
    </div>
  );
};

export const Scene2_Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade from black
  const fadeIn = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame, fps, durationInFrames: 25 });

  // Platforms row
  const platforms = [
    { name: "TikTok", color: "#333", delay: 30 },
    { name: "WhatsApp", color: "#25D366", delay: 45 },
    { name: "Instagram", color: "#C13584", delay: 60 },
    { name: "Roblox", color: "#666", delay: 75 },
    { name: "Discord", color: "#5865F2", delay: 90 },
  ];

  // Threats text
  const threat1Opacity = interpolate(frame, [150, 170], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const threat2Opacity = interpolate(frame, [200, 220], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Bottom line
  const bottomOpacity = interpolate(frame, [300, 330], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const bottomSpring = spring({
    frame: frame - 300,
    fps,
    durationInFrames: 25,
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
        padding: 100,
        display: "flex",
        flexDirection: "column",
        opacity: fadeIn * fadeOut,
        position: "relative",
      }}
    >
      {/* Title */}
      <div
        style={{
          fontSize: 42,
          fontWeight: 300,
          color: COLORS.cream,
          opacity: titleSpring,
          transform: `translateY(${(1 - titleSpring) * 20}px)`,
          marginBottom: 60,
        }}
      >
        Los carteles usan{" "}
        <span style={{ color: COLORS.red, fontWeight: 700 }}>
          plataformas digitales
        </span>
      </div>

      {/* Platforms row */}
      <div
        style={{
          display: "flex",
          gap: 30,
          marginBottom: 60,
          justifyContent: "center",
        }}
      >
        {platforms.map((p) => (
          <PlatformIcon key={p.name} {...p} />
        ))}
      </div>

      {/* Floating emojis */}
      <EmojiFloat emoji="🍕" label="Chapiza" x={1500} y={200} delay={120} />
      <EmojiFloat emoji="🐓" label="CJNG" x={1600} y={350} delay={140} />
      <EmojiFloat emoji="💀" label="Amenaza" x={1450} y={480} delay={160} />

      {/* Threat lines */}
      <div style={{ marginLeft: 40 }}>
        <div
          style={{
            opacity: threat1Opacity,
            fontSize: 32,
            color: COLORS.yellow,
            marginBottom: 24,
            fontWeight: 600,
          }}
        >
          Ofertas falsas de $15,000/semana
        </div>
        <div
          style={{
            opacity: threat2Opacity,
            fontSize: 32,
            color: COLORS.red,
            marginBottom: 24,
            fontWeight: 600,
          }}
        >
          Amenazas de muerte si no cooperan
        </div>
      </div>

      {/* Bottom punch line */}
      <div
        style={{
          position: "absolute",
          bottom: 100,
          left: 100,
          right: 100,
          opacity: bottomOpacity,
          transform: `scale(${bottomSpring})`,
        }}
      >
        <div
          style={{
            fontSize: 36,
            fontWeight: 700,
            color: COLORS.cobre,
            textAlign: "center",
            borderTop: `2px solid ${COLORS.cobre}`,
            paddingTop: 30,
          }}
        >
          Hoy, no existe una herramienta en Mexico que detecte esto
        </div>
      </div>
    </div>
  );
};
