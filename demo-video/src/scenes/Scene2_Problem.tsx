import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";


// Recruitment phases timeline
const PHASES = [
  { label: "1. Contacto", desc: "DMs inocentes en redes sociales", icon: "📱", color: COLORS.yellow },
  { label: "2. Enganche", desc: "Ofertas de dinero facil ($15k/semana)", icon: "💰", color: COLORS.yellow },
  { label: "3. Compromiso", desc: "Tareas pequeñas que escalan", icon: "📦", color: COLORS.red },
  { label: "4. Coercion", desc: "Amenazas de muerte si no cooperan", icon: "💀", color: COLORS.red },
];

const PLATFORMS = [
  { name: "TikTok", color: "#333" },
  { name: "WhatsApp", color: "#25D366" },
  { name: "Instagram", color: "#C13584" },
  { name: "Roblox", color: "#666" },
  { name: "Discord", color: "#5865F2" },
];

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
      <div style={{ fontSize: 48 }}>{emoji}</div>
      <div
        style={{
          fontSize: 13,
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

  // Fade in from black
  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame, fps, durationInFrames: 25 });

  // Timeline phases stagger
  const phaseDelays = [60, 120, 180, 240];

  // Platform 3D flips
  const platformStartFrame = 310;

  // Bottom punchline
  const bottomOpacity = interpolate(frame, [420, 460], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const bottomSpring = spring({
    frame: frame - 420,
    fps,
    durationInFrames: 25,
  });

  // Fade out
  const fadeOut = interpolate(frame, [570, 600], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: COLORS.darkGray,
        padding: 80,
        display: "flex",
        flexDirection: "column",
        opacity: fadeIn * fadeOut,
        position: "relative",
      }}
    >
      {/* Title */}
      <div
        style={{
          fontSize: 44,
          fontWeight: 300,
          color: COLORS.cream,
          opacity: titleSpring,
          transform: `translateY(${(1 - titleSpring) * 20}px)`,
          marginBottom: 50,
          zIndex: 10,
        }}
      >
        Los carteles usan{" "}
        <span style={{ color: COLORS.red, fontWeight: 700 }}>
          plataformas digitales
        </span>
      </div>

      {/* 4-Phase Timeline */}
      <div
        style={{
          display: "flex",
          gap: 20,
          marginBottom: 40,
          zIndex: 10,
        }}
      >
        {PHASES.map((phase, i) => {
          const delay = phaseDelays[i];
          const s = spring({ frame: frame - delay, fps, durationInFrames: 20 });
          const lineWidth = i < 3 ? interpolate(frame, [delay + 15, delay + 35], [0, 100], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }) : 0;

          return (
            <React.Fragment key={phase.label}>
              <div
                style={{
                  opacity: s,
                  transform: `translateY(${(1 - s) * 30}px)`,
                  background: "rgba(255,255,255,0.04)",
                  borderRadius: 16,
                  padding: "20px 24px",
                  border: `1px solid ${phase.color}33`,
                  width: 260,
                }}
              >
                <div style={{ fontSize: 32, marginBottom: 8 }}>{phase.icon}</div>
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    color: phase.color,
                    marginBottom: 6,
                  }}
                >
                  {phase.label}
                </div>
                <div
                  style={{
                    fontSize: 15,
                    color: COLORS.cream,
                    opacity: 0.7,
                    lineHeight: 1.4,
                  }}
                >
                  {phase.desc}
                </div>
              </div>
              {i < 3 && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    width: 40,
                  }}
                >
                  <div
                    style={{
                      height: 2,
                      width: `${lineWidth}%`,
                      background: phase.color,
                      opacity: 0.5,
                    }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Platform icons with 3D flip */}
      <div
        style={{
          display: "flex",
          gap: 24,
          justifyContent: "center",
          marginBottom: 30,
          zIndex: 10,
        }}
      >
        {PLATFORMS.map((p, i) => {
          const delay = platformStartFrame + i * 12;
          const s = spring({ frame: frame - delay, fps, durationInFrames: 20 });
          const rotateY = interpolate(s, [0, 1], [90, 0]);

          return (
            <div
              key={p.name}
              style={{
                opacity: s,
                transform: `perspective(800px) rotateY(${rotateY}deg)`,
                background: p.color,
                borderRadius: 18,
                width: 110,
                height: 110,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 15,
                fontWeight: 700,
                color: COLORS.white,
                textAlign: "center",
                lineHeight: 1.2,
              }}
            >
              {p.name}
            </div>
          );
        })}
      </div>

      {/* Floating emojis */}
      <EmojiFloat emoji="🍕" label="Chapiza" x={1550} y={180} delay={150} />
      <EmojiFloat emoji="🐓" label="CJNG" x={1650} y={320} delay={180} />
      <EmojiFloat emoji="💀" label="Amenaza" x={1500} y={450} delay={210} />

      {/* Bottom punch line */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 80,
          right: 80,
          opacity: bottomOpacity,
          transform: `scale(${bottomSpring})`,
          zIndex: 10,
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
