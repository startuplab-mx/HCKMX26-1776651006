import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";
import { FilmGrain } from "../components/FilmGrain";
import { GlowText } from "../components/GlowText";

const HASH_TARGET = "a7f3b2e1c9d4f6a8b0e2c5d7f1a3b9e4";
const HASH_CHARS = "0123456789abcdef";

const LAWS = [
  { code: "CPEUM Art. 16", desc: "Derecho a la privacidad", icon: "📜" },
  { code: "LGDNNA Art. 47", desc: "Proteccion de niñez digital", icon: "🛡️" },
  { code: "CPF Art. 209", desc: "Corrupcion de menores", icon: "⚖️" },
  { code: "Ley Olimpia", desc: "Violencia digital", icon: "🔒" },
];

export const Scene9_Privacy: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame, fps, durationInFrames: 25 });

  // Hash animation — characters transform one by one
  const hashStart = 40;
  const hashCharsRevealed = Math.min(
    HASH_TARGET.length,
    Math.max(0, Math.floor((frame - hashStart) * 0.6))
  );

  // Build animated hash string
  const hashDisplay = HASH_TARGET.split("").map((targetChar, i) => {
    if (i < hashCharsRevealed) {
      return targetChar;
    }
    if (i < hashCharsRevealed + 3 && frame >= hashStart) {
      // Scrambling effect
      const scrambleIdx = (frame * 7 + i * 13) % HASH_CHARS.length;
      return HASH_CHARS[scrambleIdx];
    }
    return "·";
  });

  // "Never store original" text
  const neverStoreOpacity = interpolate(frame, [100, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Law carousel
  const lawStart = 140;

  // Prison sentence
  const prisonOpacity = interpolate(frame, [290, 320], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const prisonScale = spring({
    frame: frame - 290,
    fps,
    durationInFrames: 20,
    config: { mass: 0.5, damping: 10 },
  });

  // Fade out
  const fadeOut = interpolate(frame, [335, 360], [1, 0], {
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
        padding: 80,
      }}
    >
      <FilmGrain opacity={0.03} />

      {/* Title */}
      <div
        style={{
          opacity: titleSpring,
          transform: `translateY(${(1 - titleSpring) * 20}px)`,
          textAlign: "center",
          marginBottom: 50,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontSize: 18,
            color: COLORS.cobreLight,
            fontWeight: 600,
            letterSpacing: 3,
            textTransform: "uppercase",
            marginBottom: 8,
          }}
        >
          Privacidad y Marco Legal
        </div>
        <div style={{ fontSize: 44, fontWeight: 900, color: COLORS.cream }}>
          <span style={{ color: COLORS.green }}>Zero-Knowledge</span> por
          diseño
        </div>
      </div>

      {/* Hash SHA-256 animation */}
      <div
        style={{
          marginBottom: 20,
          textAlign: "center",
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontSize: 14,
            color: COLORS.cobreLight,
            fontWeight: 600,
            letterSpacing: 2,
            marginBottom: 12,
          }}
        >
          SHA-256 HASH
        </div>
        <div
          style={{
            fontFamily: "monospace",
            fontSize: 28,
            letterSpacing: 2,
            padding: "16px 32px",
            background: "rgba(255,255,255,0.04)",
            borderRadius: 16,
            border: `1px solid ${COLORS.green}33`,
            display: "flex",
            justifyContent: "center",
          }}
        >
          {hashDisplay.map((char, i) => (
            <span
              key={i}
              style={{
                color:
                  i < hashCharsRevealed
                    ? COLORS.green
                    : i < hashCharsRevealed + 3 && frame >= hashStart
                      ? COLORS.yellow
                      : "rgba(255,255,255,0.2)",
                transition: "none",
              }}
            >
              {char}
            </span>
          ))}
        </div>
      </div>

      {/* "Never store original" */}
      <div
        style={{
          opacity: neverStoreOpacity,
          fontSize: 22,
          color: COLORS.cream,
          textAlign: "center",
          marginBottom: 50,
          zIndex: 10,
        }}
      >
        🔒 Nunca almacenamos el mensaje original —{" "}
        <span style={{ color: COLORS.green, fontWeight: 700 }}>
          solo el hash para deduplicacion
        </span>
      </div>

      {/* Law carousel */}
      <div
        style={{
          display: "flex",
          gap: 24,
          marginBottom: 50,
          zIndex: 10,
        }}
      >
        {LAWS.map((law, i) => {
          const delay = lawStart + i * 30;
          const s = spring({ frame: frame - delay, fps, durationInFrames: 20 });

          return (
            <div
              key={law.code}
              style={{
                opacity: s,
                transform: `translateY(${(1 - s) * 30}px) scale(${0.9 + s * 0.1})`,
                background: "rgba(255,255,255,0.04)",
                borderRadius: 20,
                padding: "28px 32px",
                textAlign: "center",
                border: `1px solid ${COLORS.cobre}22`,
                width: 260,
              }}
            >
              <div style={{ fontSize: 40, marginBottom: 12 }}>{law.icon}</div>
              <div
                style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: COLORS.cobre,
                  marginBottom: 8,
                }}
              >
                {law.code}
              </div>
              <div
                style={{
                  fontSize: 15,
                  color: COLORS.cream,
                  opacity: 0.7,
                  lineHeight: 1.4,
                }}
              >
                {law.desc}
              </div>
            </div>
          );
        })}
      </div>

      {/* Prison sentence impact */}
      <div
        style={{
          opacity: prisonOpacity,
          transform: `scale(${prisonScale})`,
          textAlign: "center",
          zIndex: 10,
        }}
      >
        <GlowText
          text="Hasta 18 años de prision"
          fontSize={52}
          color={COLORS.red}
          glowColor={COLORS.red}
        />
        <div
          style={{
            marginTop: 12,
            fontSize: 18,
            color: COLORS.cream,
            opacity: 0.6,
          }}
        >
          para quien reclute menores digitalmente
        </div>
      </div>
    </div>
  );
};
