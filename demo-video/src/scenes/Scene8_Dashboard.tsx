import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

import { DashboardMockup } from "../components/DashboardMockup";
import { AnimatedCounter } from "../components/AnimatedCounter";

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
        gap: 12,
        padding: "12px 16px",
        background: "rgba(255,255,255,0.03)",
        borderRadius: 10,
        borderLeft: `4px solid ${color}`,
        marginBottom: 8,
      }}
    >
      <div
        style={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 6px ${color}`,
        }}
      />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: COLORS.cream }}>
          {level}
        </div>
        <div style={{ fontSize: 12, color: COLORS.cream, opacity: 0.6 }}>
          {text}
        </div>
      </div>
      <div style={{ fontSize: 11, color: COLORS.cream, opacity: 0.4 }}>
        {time}
      </div>
    </div>
  );
};

export const Scene8_Dashboard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  const dashSpring = spring({ frame: frame - 10, fps, durationInFrames: 30 });

  // Stats pulse
  const statsPulse = 1 + 0.02 * Math.sin(frame * 0.08);

  // "Why" section
  const whyOpacity = interpolate(frame, [280, 310], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Test box typing
  const testBoxStart = 340;
  const testText = "Oye bro tengo un jale facil para ti";
  const typedChars = Math.min(
    testText.length,
    Math.max(0, Math.floor((frame - testBoxStart) * 0.8))
  );
  const verdictOpacity = interpolate(frame, [410, 430], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Timeseries chart
  const chartProgress = interpolate(frame, [440, 520], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(frame, [515, 540], [1, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // SVG chart points
  const chartData = [10, 15, 12, 28, 45, 38, 52, 65, 58, 72, 85, 78];
  const chartPath = chartData
    .map((val, i) => {
      const x = 20 + (i / (chartData.length - 1)) * 460;
      const y = 120 - val;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
  const chartLen = 600;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: COLORS.darkGray,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeIn * fadeOut,
        position: "relative",
      }}
    >
      <div
        style={{
          opacity: dashSpring,
          transform: `scale(${dashSpring * 0.1 + 0.9})`,
          zIndex: 10,
        }}
      >
        <DashboardMockup>
          {/* Top stats row */}
          <div
            style={{
              display: "flex",
              gap: 16,
              marginBottom: 20,
              transform: `scale(${statsPulse})`,
            }}
          >
            {[
              { label: "Analisis hoy", color: COLORS.cobre },
              { label: "Alertas activas", color: COLORS.red },
              { label: "Patrones", color: COLORS.green },
            ].map((stat, i) => (
              <div
                key={stat.label}
                style={{
                  flex: 1,
                  background: "rgba(255,255,255,0.04)",
                  borderRadius: 14,
                  padding: "16px 20px",
                  textAlign: "center",
                  border: `1px solid ${stat.color}22`,
                }}
              >
                <AnimatedCounter
                  to={i === 0 ? 147 : i === 1 ? 12 : 900}
                  startFrame={40 + i * 15}
                  duration={50}
                  style={{
                    fontSize: 36,
                    fontWeight: 900,
                    color: stat.color,
                  }}
                />
                <div
                  style={{
                    fontSize: 12,
                    color: COLORS.cream,
                    opacity: 0.6,
                    marginTop: 4,
                  }}
                >
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          {/* Middle row: Alerts + Why */}
          <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
            {/* Alerts list */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.cream,
                  marginBottom: 10,
                }}
              >
                Alertas recientes
              </div>
              <AlertRow
                level="PELIGRO"
                color={COLORS.red}
                text="Amenaza directa — Saltillo"
                time="hace 2min"
                delay={100}
              />
              <AlertRow
                level="PELIGRO"
                color={COLORS.red}
                text="Coercion activa — CDMX"
                time="hace 8min"
                delay={130}
              />
              <AlertRow
                level="ATENCION"
                color={COLORS.yellow}
                text="Oferta sospechosa — Monterrey"
                time="hace 15min"
                delay={160}
              />
              <AlertRow
                level="SEGURO"
                color={COLORS.green}
                text="Contenido verificado — Guadalajara"
                time="hace 1h"
                delay={190}
              />
            </div>

            {/* "Why" + Legal */}
            <div
              style={{
                flex: 1,
                opacity: whyOpacity,
              }}
            >
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.cream,
                  marginBottom: 10,
                }}
              >
                ¿Por que es peligroso?
              </div>
              <div
                style={{
                  background: "rgba(239,68,68,0.08)",
                  borderRadius: 12,
                  padding: 16,
                  fontSize: 14,
                  color: COLORS.cream,
                  lineHeight: 1.7,
                  borderLeft: `3px solid ${COLORS.red}`,
                  marginBottom: 12,
                }}
              >
                1. Patron de amenaza directa detectado
                {"\n"}2. Urgencia en el mensaje
                {"\n"}3. Aislamiento del menor
              </div>
              <div
                style={{
                  background: "rgba(234,179,8,0.08)",
                  borderRadius: 12,
                  padding: 16,
                  fontSize: 13,
                  color: COLORS.yellow,
                  lineHeight: 1.6,
                  borderLeft: `3px solid ${COLORS.yellow}`,
                }}
              >
                Marco legal: Art. 209 CPF, Ley Olimpia, LGDNNA Art. 47
              </div>
            </div>
          </div>

          {/* Bottom row: Test box + Chart */}
          <div style={{ display: "flex", gap: 16 }}>
            {/* Test box with typing */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.cream,
                  marginBottom: 10,
                }}
              >
                Probar mensaje
              </div>
              <div
                style={{
                  background: "rgba(255,255,255,0.05)",
                  borderRadius: 12,
                  padding: 16,
                  border: `1px solid ${COLORS.cobre}33`,
                  minHeight: 46,
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <span
                  style={{
                    fontSize: 15,
                    color: COLORS.cream,
                    fontFamily: "monospace",
                  }}
                >
                  {testText.slice(0, typedChars)}
                  {frame >= testBoxStart && typedChars < testText.length && (
                    <span
                      style={{
                        opacity: Math.sin(frame * 0.2) > 0 ? 1 : 0,
                        color: COLORS.cobre,
                      }}
                    >
                      |
                    </span>
                  )}
                </span>
              </div>
              {/* Verdict */}
              <div
                style={{
                  opacity: verdictOpacity,
                  marginTop: 10,
                  padding: "10px 16px",
                  background: "rgba(239,68,68,0.1)",
                  borderRadius: 10,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span
                  style={{
                    fontSize: 14,
                    fontWeight: 700,
                    color: COLORS.red,
                  }}
                >
                  ⚠️ ATENCION — Riesgo: 78%
                </span>
                <span
                  style={{
                    fontSize: 12,
                    color: COLORS.cream,
                    opacity: 0.6,
                  }}
                >
                  Fase: Enganche
                </span>
              </div>
            </div>

            {/* Timeseries chart */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.cream,
                  marginBottom: 10,
                }}
              >
                Actividad (7 dias)
              </div>
              <svg width={500} height={140} style={{ overflow: "visible" }}>
                <path
                  d={chartPath}
                  fill="none"
                  stroke={COLORS.cobre}
                  strokeWidth={2.5}
                  strokeDasharray={chartLen}
                  strokeDashoffset={chartLen * (1 - chartProgress)}
                  strokeLinecap="round"
                />
                {/* Area fill */}
                <path
                  d={`${chartPath} L 480 120 L 20 120 Z`}
                  fill={`${COLORS.cobre}11`}
                  opacity={chartProgress}
                />
              </svg>
            </div>
          </div>
        </DashboardMockup>
      </div>
    </div>
  );
};
