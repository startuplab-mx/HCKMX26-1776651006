import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";


// Waveform bars
const WaveformBar: React.FC<{ index: number; active: boolean }> = ({
  index,
  active,
}) => {
  const frame = useCurrentFrame();
  const baseHeight = 10 + ((index * 7) % 30);
  const animHeight = active
    ? baseHeight + 15 * Math.sin(frame * 0.15 + index * 0.8)
    : baseHeight;

  return (
    <div
      style={{
        width: 4,
        height: Math.abs(animHeight),
        background: active ? COLORS.cobre : "rgba(255,255,255,0.2)",
        borderRadius: 2,
      }}
    />
  );
};

export const Scene6_Multimedia: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame, fps, durationInFrames: 25 });

  // Audio section timing
  const waveformActive = frame >= 40 && frame < 120;
  const whisperOpacity = interpolate(frame, [120, 140], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const transcriptionOpacity = interpolate(frame, [155, 175], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Image section timing
  const imageStart = 190;
  const screenshotSpring = spring({
    frame: frame - imageStart,
    fps,
    durationInFrames: 20,
  });
  const visionOpacity = interpolate(frame, [230, 250], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ocrOpacity = interpolate(frame, [260, 280], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Bottom note
  const noteOpacity = interpolate(frame, [310, 340], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(frame, [365, 390], [1, 0], {
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
      {/* Title */}
      <div
        style={{
          opacity: titleSpring,
          transform: `translateY(${(1 - titleSpring) * 20}px)`,
          marginBottom: 60,
          textAlign: "center",
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
          Analisis Multimedia
        </div>
        <div style={{ fontSize: 44, fontWeight: 900, color: COLORS.cream }}>
          No solo texto —{" "}
          <span style={{ color: COLORS.cobre }}>audio e imagenes</span>
        </div>
      </div>

      {/* Two columns */}
      <div
        style={{
          display: "flex",
          gap: 60,
          width: "100%",
          maxWidth: 1500,
          zIndex: 10,
        }}
      >
        {/* AUDIO section */}
        <div
          style={{
            flex: 1,
            background: "rgba(255,255,255,0.03)",
            borderRadius: 24,
            padding: 40,
            border: `1px solid ${COLORS.cobre}22`,
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: COLORS.cobre,
              letterSpacing: 2,
              textTransform: "uppercase",
              marginBottom: 24,
            }}
          >
            🎤 Audio
          </div>

          {/* Waveform */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 3,
              height: 60,
              marginBottom: 24,
            }}
          >
            {Array.from({ length: 40 }).map((_, i) => (
              <WaveformBar key={i} index={i} active={waveformActive} />
            ))}
          </div>

          {/* Arrow → Whisper */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              marginBottom: 20,
              opacity: whisperOpacity,
            }}
          >
            <div
              style={{
                fontSize: 24,
                color: COLORS.cobreLight,
              }}
            >
              →
            </div>
            <div
              style={{
                background: "rgba(193,106,76,0.15)",
                borderRadius: 12,
                padding: "12px 20px",
                fontSize: 18,
                fontWeight: 700,
                color: COLORS.cobre,
              }}
            >
              Whisper STT
            </div>
          </div>

          {/* Transcription result */}
          <div
            style={{
              opacity: transcriptionOpacity,
              background: "rgba(255,255,255,0.05)",
              borderRadius: 12,
              padding: 20,
              fontSize: 16,
              color: COLORS.cream,
              lineHeight: 1.6,
              fontStyle: "italic",
              borderLeft: `3px solid ${COLORS.yellow}`,
            }}
          >
            "Te voy a dar $15,000 a la semana si mueves paquetes por la
            frontera..."
          </div>
        </div>

        {/* IMAGE section */}
        <div
          style={{
            flex: 1,
            background: "rgba(255,255,255,0.03)",
            borderRadius: 24,
            padding: 40,
            border: `1px solid ${COLORS.cobre}22`,
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: COLORS.cobre,
              letterSpacing: 2,
              textTransform: "uppercase",
              marginBottom: 24,
            }}
          >
            📸 Imagen
          </div>

          {/* Screenshot mockup */}
          <div
            style={{
              opacity: screenshotSpring,
              transform: `scale(${screenshotSpring})`,
              background: "#262626",
              borderRadius: 12,
              padding: 20,
              marginBottom: 20,
              height: 100,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                fontSize: 15,
                color: COLORS.cream,
                opacity: 0.6,
                textAlign: "center",
              }}
            >
              📱 Screenshot de chat sospechoso
            </div>
          </div>

          {/* Arrow → Claude Vision */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              marginBottom: 20,
              opacity: visionOpacity,
            }}
          >
            <div style={{ fontSize: 24, color: COLORS.cobreLight }}>→</div>
            <div
              style={{
                background: "rgba(59,130,246,0.15)",
                borderRadius: 12,
                padding: "12px 20px",
                fontSize: 18,
                fontWeight: 700,
                color: COLORS.blue,
              }}
            >
              Claude Vision + OCR
            </div>
          </div>

          {/* OCR result */}
          <div
            style={{
              opacity: ocrOpacity,
              background: "rgba(255,255,255,0.05)",
              borderRadius: 12,
              padding: 20,
              fontSize: 16,
              color: COLORS.cream,
              lineHeight: 1.6,
              borderLeft: `3px solid ${COLORS.red}`,
            }}
          >
            Texto extraido: "Necesito gente para un jale en Reynosa, pago en
            efectivo, sin preguntas"
            <div style={{ marginTop: 8, color: COLORS.red, fontWeight: 700 }}>
              → Riesgo: 92% | Fase: Enganche
            </div>
          </div>
        </div>
      </div>

      {/* Bottom note */}
      <div
        style={{
          opacity: noteOpacity,
          marginTop: 40,
          padding: "16px 32px",
          background: "rgba(34,197,94,0.1)",
          borderRadius: 12,
          border: `1px solid ${COLORS.green}33`,
          fontSize: 18,
          color: COLORS.green,
          fontWeight: 600,
          textAlign: "center",
          zIndex: 10,
        }}
      >
        🔒 Confirmacion del usuario siempre requerida antes de enviar datos
      </div>
    </div>
  );
};
