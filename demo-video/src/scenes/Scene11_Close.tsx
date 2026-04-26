import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";
import { FilmGrain } from "../components/FilmGrain";
import { ParticleField } from "../components/ParticleField";
import { GlowText } from "../components/GlowText";

export const Scene11_Close: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  // "Not just hackathon code" line
  const line1Opacity = interpolate(frame, [10, 35], [0, 1], {
    extrapolateRight: "clamp",
  });
  const line1Y = interpolate(frame, [10, 35], [20, 0], {
    extrapolateRight: "clamp",
  });

  // "Real solution" line
  const line2Opacity = interpolate(frame, [40, 65], [0, 1], {
    extrapolateRight: "clamp",
  });
  const line2Y = interpolate(frame, [40, 65], [20, 0], {
    extrapolateRight: "clamp",
  });

  // Lines fade out
  const linesFadeOut = interpolate(frame, [80, 95], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Logo with glow rings
  const logoSpring = spring({
    frame: frame - 100,
    fps,
    durationInFrames: 25,
    config: { mass: 0.6, damping: 10 },
  });

  // Glow rings expanding from logo
  const ringCount = 4;

  // Contact info
  const contactOpacity = interpolate(frame, [140, 160], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Team
  const teamOpacity = interpolate(frame, [165, 185], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Hackathon badge
  const badgeSpring = spring({ frame: frame - 195, fps, durationInFrames: 20 });

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
      <FilmGrain opacity={0.04} />
      <ParticleField count={50} />

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
      {frame < 95 && (
        <div style={{ textAlign: "center", opacity: linesFadeOut, zIndex: 10 }}>
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

      {/* Logo with glow rings */}
      {frame >= 100 && (
        <div
          style={{
            transform: `scale(${logoSpring})`,
            textAlign: "center",
            marginBottom: 30,
            position: "relative",
            zIndex: 10,
          }}
        >
          {/* Expanding glow rings */}
          {Array.from({ length: ringCount }).map((_, i) => {
            const ringFrame = frame - 110 - i * 15;
            const ringScale = ringFrame > 0
              ? interpolate(ringFrame, [0, 50], [0.5, 3 + i * 0.6], { extrapolateRight: "clamp" })
              : 0;
            const ringOpacity = ringFrame > 0
              ? interpolate(ringFrame, [0, 50], [0.5, 0], { extrapolateRight: "clamp" })
              : 0;

            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  top: "30%",
                  left: "50%",
                  width: 100,
                  height: 100,
                  borderRadius: "50%",
                  border: `2px solid ${COLORS.cobreGlow}`,
                  transform: `translate(-50%, -50%) scale(${ringScale})`,
                  opacity: ringOpacity,
                  pointerEvents: "none",
                }}
              />
            );
          })}

          <div
            style={{
              fontSize: 52,
              marginBottom: 16,
              position: "relative",
              zIndex: 2,
            }}
          >
            🛡️
          </div>
          <GlowText text="NAHUAL" fontSize={96} style={{ letterSpacing: 12 }} />
        </div>
      )}

      {/* Contact info */}
      <div
        style={{
          opacity: contactOpacity,
          textAlign: "center",
          marginBottom: 24,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: COLORS.cream,
            marginBottom: 8,
          }}
        >
          nahualsec.com
        </div>
        <div style={{ fontSize: 22, color: COLORS.cobreLight }}>
          Bot: +52 844 538 7404
        </div>
      </div>

      {/* Team */}
      <div
        style={{
          opacity: teamOpacity,
          textAlign: "center",
          marginBottom: 24,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontSize: 14,
            color: COLORS.cream,
            opacity: 0.4,
            marginBottom: 6,
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
          bottom: 40,
          opacity: badgeSpring,
          transform: `scale(${badgeSpring})`,
          display: "flex",
          alignItems: "center",
          gap: 16,
          padding: "14px 32px",
          background: "rgba(255,255,255,0.05)",
          borderRadius: 50,
          border: `1px solid rgba(255,255,255,0.1)`,
          zIndex: 10,
        }}
      >
        <div style={{ fontSize: 16, color: COLORS.cream, opacity: 0.6 }}>
          Hackathon 404: Threat Not Found
        </div>
        <div style={{ color: COLORS.cream, opacity: 0.3 }}>|</div>
        <div style={{ fontSize: 16, color: COLORS.cobreLight, fontWeight: 600 }}>
          Abril 2026
        </div>
        <div style={{ color: COLORS.cream, opacity: 0.3 }}>|</div>
        <div style={{ fontSize: 16, color: COLORS.yellow, fontWeight: 700 }}>
          $25,000 USD
        </div>
      </div>
    </div>
  );
};
