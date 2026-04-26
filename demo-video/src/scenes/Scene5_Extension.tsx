import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
  Img,
  staticFile,
} from "remotion";
import { COLORS } from "../colors";

const AlertRow: React.FC<{
  level: string;
  color: string;
  text: string;
  time: string;
  delay: number;
}> = ({ level, color, text, time, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, durationInFrames: 15 });

  return (
    <div
      style={{
        opacity: s,
        transform: `translateX(${(1 - s) * 30}px)`,
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "14px 20px",
        background: "rgba(255,255,255,0.03)",
        borderRadius: 12,
        borderLeft: `4px solid ${color}`,
        marginBottom: 10,
      }}
    >
      <div
        style={{
          width: 10,
          height: 10,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 8px ${color}`,
        }}
      />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 16, fontWeight: 600, color: COLORS.cream }}>
          {level}
        </div>
        <div style={{ fontSize: 14, color: COLORS.cream, opacity: 0.6 }}>
          {text}
        </div>
      </div>
      <div style={{ fontSize: 13, color: COLORS.cream, opacity: 0.4 }}>
        {time}
      </div>
    </div>
  );
};

export const Scene5_Extension: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Left side: Extension mockup
  const extSlide = spring({ frame, fps, durationInFrames: 30 });

  // Right side: Panel mockup
  const panelSlide = spring({ frame: frame - 15, fps, durationInFrames: 30 });

  // Shield overlay animation
  const shieldPulse =
    frame > 60 ? 0.9 + 0.1 * Math.sin((frame - 60) * 0.08) : 0;
  const shieldOpacity = interpolate(frame, [60, 80], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stats
  const statSpring = spring({ frame: frame - 200, fps, durationInFrames: 25 });
  const surveyValue = interpolate(frame, [200, 260], [0, 92.3], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const contribValue = interpolate(frame, [240, 300], [0, 4], {
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
        opacity: fadeIn * fadeOut,
      }}
    >
      {/* LEFT — Extension mockup */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          transform: `translateX(${(1 - extSlide) * -80}px)`,
          opacity: extSlide,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: COLORS.cobre,
            marginBottom: 30,
            textAlign: "center",
          }}
        >
          Extension de Navegador
        </div>

        {/* Fake browser window */}
        <div
          style={{
            width: 700,
            height: 500,
            background: "#111",
            borderRadius: 16,
            overflow: "hidden",
            border: `2px solid ${COLORS.carbon}`,
            position: "relative",
          }}
        >
          {/* Browser chrome */}
          <div
            style={{
              height: 40,
              background: "#2A2A2A",
              display: "flex",
              alignItems: "center",
              padding: "0 16px",
              gap: 8,
            }}
          >
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#FF5F57",
              }}
            />
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#FEBC2E",
              }}
            />
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#28C840",
              }}
            />
            <div
              style={{
                marginLeft: 20,
                flex: 1,
                height: 24,
                background: "#444",
                borderRadius: 6,
                display: "flex",
                alignItems: "center",
                paddingLeft: 12,
                fontSize: 12,
                color: "#888",
              }}
            >
              instagram.com/messages
            </div>
          </div>

          {/* Fake DM content */}
          <div style={{ padding: 30, color: COLORS.cream, fontSize: 16 }}>
            <div style={{ marginBottom: 20, opacity: 0.5 }}>
              usuario_desconocido
            </div>
            <div
              style={{
                background: "#262626",
                padding: 16,
                borderRadius: 16,
                marginBottom: 10,
              }}
            >
              Hey bro, tengo un jale facil, $15k a la semana 💰
            </div>
            <div
              style={{
                background: "#262626",
                padding: 16,
                borderRadius: 16,
              }}
            >
              Solo necesito que muevas unas cosas por Saltillo 🚗
            </div>
          </div>

          {/* Nahual Shield overlay */}
          <div
            style={{
              position: "absolute",
              top: 40,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(239, 68, 68, 0.15)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              opacity: shieldOpacity,
            }}
          >
            <div
              style={{
                background: "rgba(26, 29, 32, 0.95)",
                borderRadius: 20,
                padding: "30px 50px",
                textAlign: "center",
                border: `2px solid ${COLORS.red}`,
                transform: `scale(${shieldPulse})`,
              }}
            >
              <div style={{ fontSize: 48, marginBottom: 12 }}>🛡️</div>
              <div
                style={{
                  fontSize: 24,
                  fontWeight: 900,
                  color: COLORS.red,
                  marginBottom: 8,
                }}
              >
                NAHUAL SHIELD
              </div>
              <div style={{ fontSize: 16, color: COLORS.cream }}>
                Posible reclutamiento detectado
              </div>
              <div
                style={{
                  fontSize: 14,
                  color: COLORS.yellow,
                  marginTop: 8,
                }}
              >
                Fase: Enganche · Riesgo: 87%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div
        style={{
          width: 2,
          background: `linear-gradient(transparent, ${COLORS.cobre}, transparent)`,
        }}
      />

      {/* RIGHT — Panel mockup */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          transform: `translateX(${(1 - panelSlide) * 80}px)`,
          opacity: panelSlide,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: COLORS.cobre,
            marginBottom: 30,
            textAlign: "center",
          }}
        >
          Panel de Inteligencia
        </div>

        {/* Panel card */}
        <div
          style={{
            width: 650,
            background: COLORS.carbon,
            borderRadius: 16,
            padding: 30,
            border: `1px solid rgba(255,255,255,0.08)`,
          }}
        >
          {/* Stats row */}
          <div
            style={{
              display: "flex",
              gap: 20,
              marginBottom: 30,
              opacity: statSpring,
            }}
          >
            <div
              style={{
                flex: 1,
                background: "rgba(34,197,94,0.1)",
                borderRadius: 12,
                padding: 20,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: 36,
                  fontWeight: 900,
                  color: COLORS.green,
                }}
              >
                {surveyValue.toFixed(1)}%
              </div>
              <div style={{ fontSize: 13, color: COLORS.cream, opacity: 0.6 }}>
                Usaria Nahual
              </div>
            </div>
            <div
              style={{
                flex: 1,
                background: "rgba(193,106,76,0.1)",
                borderRadius: 12,
                padding: 20,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: 36,
                  fontWeight: 900,
                  color: COLORS.cobre,
                }}
              >
                {Math.round(contribValue)}
              </div>
              <div style={{ fontSize: 13, color: COLORS.cream, opacity: 0.6 }}>
                Contribuciones anonimas
              </div>
            </div>
          </div>

          {/* Alert list */}
          <div style={{ fontSize: 16, fontWeight: 600, color: COLORS.cream, marginBottom: 14 }}>
            Alertas recientes
          </div>
          <AlertRow
            level="PELIGRO"
            color={COLORS.red}
            text="Amenaza directa — Saltillo"
            time="hace 2min"
            delay={130}
          />
          <AlertRow
            level="ATENCION"
            color={COLORS.yellow}
            text="Oferta sospechosa — CDMX"
            time="hace 15min"
            delay={160}
          />
          <AlertRow
            level="SEGURO"
            color={COLORS.green}
            text="Contenido verificado — Monterrey"
            time="hace 1h"
            delay={190}
          />
        </div>
      </div>
    </div>
  );
};
