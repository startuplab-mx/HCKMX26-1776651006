import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

export const Scene7_Close: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in from black
  const fadeIn = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  // "Not just a hackathon code" line
  const line1Opacity = interpolate(frame, [20, 50], [0, 1], {
    extrapolateRight: "clamp",
  });
  const line1Y = interpolate(frame, [20, 50], [20, 0], {
    extrapolateRight: "clamp",
  });

  // "It's a real solution" line
  const line2Opacity = interpolate(frame, [70, 100], [0, 1], {
    extrapolateRight: "clamp",
  });
  const line2Y = interpolate(frame, [70, 100], [20, 0], {
    extrapolateRight: "clamp",
  });

  // Lines fade out
  const linesFadeOut = interpolate(frame, [140, 160], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Logo appears
  const logoSpring = spring({
    frame: frame - 170,
    fps,
    durationInFrames: 30,
    config: { mass: 0.6, damping: 10 },
  });

  // Glow pulse
  const glowIntensity =
    frame > 200 ? 20 + 10 * Math.sin((frame - 200) * 0.06) : 0;

  // Contact info
  const contactOpacity = interpolate(frame, [250, 280], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Team
  const teamOpacity = interpolate(frame, [310, 340], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Hackathon badge
  const badgeSpring = spring({ frame: frame - 370, fps, durationInFrames: 25 });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: COLORS.carbon,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeIn,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Background gradient orbs */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${COLORS.cobre}15, transparent)`,
          top: -100,
          right: -100,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${COLORS.cobre}10, transparent)`,
          bottom: -50,
          left: -50,
        }}
      />

      {/* Manifesto lines */}
      {frame < 160 && (
        <div style={{ textAlign: "center", opacity: linesFadeOut }}>
          <div
            style={{
              opacity: line1Opacity,
              transform: `translateY(${line1Y}px)`,
              fontSize: 40,
              fontWeight: 300,
              color: COLORS.cream,
              marginBottom: 20,
            }}
          >
            Nahual no es un codigo para un hackathon
          </div>
          <div
            style={{
              opacity: line2Opacity,
              transform: `translateY(${line2Y}px)`,
              fontSize: 48,
              fontWeight: 900,
              color: COLORS.cobre,
            }}
          >
            Es una solucion real contra la guerra del narco
          </div>
        </div>
      )}

      {/* Logo */}
      {frame >= 170 && (
        <div
          style={{
            transform: `scale(${logoSpring})`,
            textAlign: "center",
            marginBottom: 40,
          }}
        >
          <div
            style={{
              fontSize: 48,
              marginBottom: 16,
              filter: `drop-shadow(0 0 ${glowIntensity}px ${COLORS.cobre})`,
            }}
          >
            🛡️
          </div>
          <div
            style={{
              fontSize: 96,
              fontWeight: 900,
              color: COLORS.cobre,
              letterSpacing: 12,
              textShadow: `0 0 ${glowIntensity * 2}px ${COLORS.cobre}66`,
            }}
          >
            NAHUAL
          </div>
        </div>
      )}

      {/* Contact info */}
      <div
        style={{
          opacity: contactOpacity,
          textAlign: "center",
          marginBottom: 40,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: COLORS.cream,
            marginBottom: 12,
          }}
        >
          nahualsec.com
        </div>
        <div
          style={{
            fontSize: 22,
            color: COLORS.cobreLight,
          }}
        >
          Bot: +52 844 538 7404
        </div>
      </div>

      {/* Team */}
      <div
        style={{
          opacity: teamOpacity,
          textAlign: "center",
          marginBottom: 40,
        }}
      >
        <div
          style={{
            fontSize: 14,
            color: COLORS.cream,
            opacity: 0.4,
            marginBottom: 8,
            letterSpacing: 4,
            textTransform: "uppercase",
          }}
        >
          Equipo Vanguard
        </div>
        <div
          style={{
            fontSize: 24,
            color: COLORS.cream,
            fontWeight: 600,
          }}
        >
          Armando Flores · Marco Espinosa
        </div>
      </div>

      {/* Hackathon badge */}
      <div
        style={{
          position: "absolute",
          bottom: 50,
          opacity: badgeSpring,
          transform: `scale(${badgeSpring})`,
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "12px 28px",
          background: "rgba(255,255,255,0.05)",
          borderRadius: 50,
          border: `1px solid rgba(255,255,255,0.1)`,
        }}
      >
        <div style={{ fontSize: 16, color: COLORS.cream, opacity: 0.6 }}>
          Hackathon 404: Threat Not Found
        </div>
        <div style={{ color: COLORS.cream, opacity: 0.3 }}>|</div>
        <div style={{ fontSize: 16, color: COLORS.cobreLight, fontWeight: 600 }}>
          Abril 2026
        </div>
      </div>
    </div>
  );
};
