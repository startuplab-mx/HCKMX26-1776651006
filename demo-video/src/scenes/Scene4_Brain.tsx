import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

import { ScoreThermometer } from "../components/ScoreThermometer";
import { GlowText } from "../components/GlowText";

const LAYERS = [
  {
    name: "Override Layer",
    desc: "Palabras clave criticas: amenaza directa, extorsion, secuestro",
    icon: "⚡",
    color: COLORS.red,
  },
  {
    name: "Heuristic Layer",
    desc: "Patrones linguisticos: urgencia, ofertas monetarias, aislamiento",
    icon: "🔍",
    color: COLORS.yellow,
  },
  {
    name: "Bayesian Layer",
    desc: "Probabilidad condicional basada en 900 patrones verificados",
    icon: "📊",
    color: COLORS.blue,
  },
  {
    name: "LLM Layer",
    desc: "Analisis contextual profundo con Claude para ambiguedades",
    icon: "🧠",
    color: COLORS.cobreLight,
  },
];

export const Scene4_Brain: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame, fps, durationInFrames: 25 });

  // Layer stagger (each layer appears 60 frames apart)
  const layerDelays = [60, 130, 200, 270];

  // Trajectory arrow connecting them
  const trajectoryProgress = interpolate(frame, [300, 380], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Risk formula
  const formulaOpacity = interpolate(frame, [390, 420], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Thermometer
  const thermoStart = 430;

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
        display: "flex",
        opacity: fadeIn * fadeOut,
        position: "relative",
      }}
    >
      {/* LEFT — Cognitive Layers */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "60px 40px 60px 80px",
          zIndex: 10,
        }}
      >
        <div
          style={{
            opacity: titleSpring,
            transform: `translateY(${(1 - titleSpring) * 20}px)`,
            marginBottom: 40,
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
            Arquitectura Cognitiva
          </div>
          <GlowText text="El Cerebro de Nahual" fontSize={48} />
        </div>

        {/* 4 Layers stacked */}
        {LAYERS.map((layer, i) => {
          const delay = layerDelays[i];
          const s = spring({ frame: frame - delay, fps, durationInFrames: 20 });
          const slideX = interpolate(s, [0, 1], [-60, 0]);

          return (
            <div
              key={layer.name}
              style={{
                opacity: s,
                transform: `translateX(${slideX}px)`,
                display: "flex",
                alignItems: "center",
                gap: 20,
                marginBottom: 16,
                padding: "18px 24px",
                background: "rgba(255,255,255,0.03)",
                borderRadius: 16,
                borderLeft: `4px solid ${layer.color}`,
              }}
            >
              <div style={{ fontSize: 36 }}>{layer.icon}</div>
              <div>
                <div
                  style={{
                    fontSize: 22,
                    fontWeight: 700,
                    color: layer.color,
                    marginBottom: 4,
                  }}
                >
                  {layer.name}
                </div>
                <div
                  style={{
                    fontSize: 15,
                    color: COLORS.cream,
                    opacity: 0.7,
                    lineHeight: 1.4,
                  }}
                >
                  {layer.desc}
                </div>
              </div>
            </div>
          );
        })}

        {/* Trajectory arrow */}
        <div
          style={{
            marginTop: 12,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <div
            style={{
              height: 3,
              width: `${trajectoryProgress * 100}%`,
              maxWidth: 500,
              background: `linear-gradient(90deg, ${COLORS.red}, ${COLORS.yellow}, ${COLORS.blue}, ${COLORS.cobreLight})`,
              borderRadius: 2,
            }}
          />
          {trajectoryProgress > 0.9 && (
            <span
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: COLORS.cobre,
              }}
            >
              → Trajectory Score
            </span>
          )}
        </div>
      </div>

      {/* RIGHT — Formula + Thermometer */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          zIndex: 10,
        }}
      >
        {/* Risk formula */}
        <div
          style={{
            opacity: formulaOpacity,
            textAlign: "center",
            marginBottom: 60,
          }}
        >
          <div
            style={{
              fontSize: 16,
              color: COLORS.cobreLight,
              fontWeight: 600,
              letterSpacing: 3,
              textTransform: "uppercase",
              marginBottom: 20,
            }}
          >
            Formula de riesgo
          </div>
          <div
            style={{
              fontSize: 28,
              fontWeight: 300,
              color: COLORS.cream,
              fontFamily: "monospace",
              background: "rgba(255,255,255,0.04)",
              padding: "20px 32px",
              borderRadius: 16,
              border: `1px solid ${COLORS.cobre}33`,
            }}
          >
            <span style={{ color: COLORS.red }}>Override</span> ×{" "}
            <span style={{ color: COLORS.yellow }}>Heuristic</span> +{" "}
            <span style={{ color: COLORS.blue }}>Bayesian</span> ×{" "}
            <span style={{ color: COLORS.cobreLight }}>LLM</span>
          </div>
          <div
            style={{
              marginTop: 12,
              fontSize: 14,
              color: COLORS.cream,
              opacity: 0.5,
            }}
          >
            Si Override detecta amenaza directa → riesgo = 100% automatico
          </div>
        </div>

        {/* Thermometer demo */}
        <div
          style={{
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 16,
              color: COLORS.cobreLight,
              fontWeight: 600,
              letterSpacing: 3,
              textTransform: "uppercase",
              marginBottom: 20,
            }}
          >
            Escala de riesgo
          </div>
          <ScoreThermometer
            score={96}
            startFrame={thermoStart}
            duration={100}
            width={450}
            height={36}
          />
        </div>

        {/* Labels below thermometer */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            width: 450,
            marginTop: 16,
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          <span style={{ color: COLORS.green }}>SEGURO</span>
          <span style={{ color: COLORS.yellow }}>ATENCION</span>
          <span style={{ color: COLORS.red }}>PELIGRO</span>
        </div>
      </div>
    </div>
  );
};
