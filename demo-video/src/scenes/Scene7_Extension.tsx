import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

import { BrowserMockup } from "../components/BrowserMockup";

const PLATFORMS_COMPAT = [
  { name: "Instagram", color: "#C13584" },
  { name: "TikTok", color: "#333" },
  { name: "WhatsApp Web", color: "#25D366" },
  { name: "Discord", color: "#5865F2" },
];

export const Scene7_Extension: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  const browserSpring = spring({ frame, fps, durationInFrames: 30 });

  // Scanning line (green line sweeping vertically)
  const scanLineY = interpolate(frame, [60, 180], [0, 520], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scanLineOpacity = frame >= 60 && frame < 180 ? 0.8 : 0;

  // Shield overlay after scan
  const shieldOpacity = interpolate(frame, [190, 210], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shieldPulse =
    frame > 210 ? 0.95 + 0.05 * Math.sin((frame - 210) * 0.08) : 0;

  // Platform compatibility badges
  const platformStart = 300;

  // "Zero data sent" badge
  const zeroBadgeOpacity = interpolate(frame, [380, 400], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const zeroBadgeSpring = spring({
    frame: frame - 380,
    fps,
    durationInFrames: 20,
  });

  // Fade out
  const fadeOut = interpolate(frame, [425, 450], [1, 0], {
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
        padding: 60,
      }}
    >
      {/* Title */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 30,
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
          Deteccion Proactiva
        </div>
        <div style={{ fontSize: 40, fontWeight: 900, color: COLORS.cream }}>
          Nahual Shield —{" "}
          <span style={{ color: COLORS.green }}>Extension de Navegador</span>
        </div>
      </div>

      {/* Browser fullscreen */}
      <div
        style={{
          opacity: browserSpring,
          transform: `scale(${0.9 + browserSpring * 0.1})`,
          zIndex: 10,
          marginBottom: 30,
        }}
      >
        <BrowserMockup url="instagram.com/messages" width={1100} height={500}>
          {/* DM content */}
          <div style={{ padding: 30, color: COLORS.cream, fontSize: 16 }}>
            <div style={{ marginBottom: 16, opacity: 0.5, fontSize: 14 }}>
              usuario_desconocido
            </div>
            <div
              style={{
                background: "#262626",
                padding: 16,
                borderRadius: 16,
                marginBottom: 10,
                fontSize: 18,
              }}
            >
              Hey bro, tengo un jale facil, $15k a la semana 💰
            </div>
            <div
              style={{
                background: "#262626",
                padding: 16,
                borderRadius: 16,
                marginBottom: 10,
                fontSize: 18,
              }}
            >
              Solo necesito que muevas unas cosas por Saltillo 🚗
            </div>
            <div
              style={{
                background: "#262626",
                padding: 16,
                borderRadius: 16,
                fontSize: 18,
              }}
            >
              No le digas a nadie, esto es entre tu y yo 🤫
            </div>
          </div>

          {/* Green scanning line (MutationObserver) */}
          <div
            style={{
              position: "absolute",
              top: scanLineY,
              left: 0,
              right: 0,
              height: 3,
              background: `linear-gradient(90deg, transparent, ${COLORS.green}, transparent)`,
              opacity: scanLineOpacity,
              boxShadow: `0 0 20px ${COLORS.green}66`,
              pointerEvents: "none",
            }}
          />

          {/* Nahual Shield overlay */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(239, 68, 68, 0.12)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              opacity: shieldOpacity,
              pointerEvents: "none",
            }}
          >
            <div
              style={{
                background: "rgba(26, 29, 32, 0.96)",
                borderRadius: 24,
                padding: "36px 56px",
                textAlign: "center",
                border: `2px solid ${COLORS.red}`,
                transform: `scale(${shieldPulse})`,
              }}
            >
              <div style={{ fontSize: 52, marginBottom: 12 }}>🛡️</div>
              <div
                style={{
                  fontSize: 28,
                  fontWeight: 900,
                  color: COLORS.red,
                  marginBottom: 8,
                }}
              >
                NAHUAL SHIELD
              </div>
              <div
                style={{
                  fontSize: 18,
                  color: COLORS.cream,
                  marginBottom: 8,
                }}
              >
                Posible reclutamiento detectado
              </div>
              <div
                style={{
                  fontSize: 16,
                  color: COLORS.yellow,
                }}
              >
                Fase: Enganche · Riesgo: 87% · MutationObserver activo
              </div>
            </div>
          </div>
        </BrowserMockup>
      </div>

      {/* Platform compatibility + zero data */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 30,
          zIndex: 10,
        }}
      >
        {/* Platforms */}
        <div style={{ display: "flex", gap: 12 }}>
          {PLATFORMS_COMPAT.map((p, i) => {
            const delay = platformStart + i * 15;
            const s = spring({ frame: frame - delay, fps, durationInFrames: 15 });

            return (
              <div
                key={p.name}
                style={{
                  opacity: s,
                  transform: `scale(${s})`,
                  background: p.color,
                  borderRadius: 12,
                  padding: "8px 18px",
                  fontSize: 14,
                  fontWeight: 700,
                  color: COLORS.white,
                }}
              >
                {p.name}
              </div>
            );
          })}
        </div>

        {/* Zero data badge */}
        <div
          style={{
            opacity: zeroBadgeOpacity,
            transform: `scale(${zeroBadgeSpring})`,
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "10px 24px",
            background: "rgba(34,197,94,0.1)",
            borderRadius: 50,
            border: `1px solid ${COLORS.green}44`,
          }}
        >
          <span style={{ fontSize: 20 }}>🔒</span>
          <span
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: COLORS.green,
            }}
          >
            Cero datos enviados a servidores externos
          </span>
        </div>
      </div>
    </div>
  );
};
