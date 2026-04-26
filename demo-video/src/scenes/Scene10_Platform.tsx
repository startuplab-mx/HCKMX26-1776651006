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
import { AnimatedCounter } from "../components/AnimatedCounter";

const HeatDot: React.FC<{
  x: number;
  y: number;
  size: number;
  color: string;
  label: string;
  delay: number;
}> = ({ x, y, size, color, label, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, durationInFrames: 20 });
  const pulse = 1 + 0.08 * Math.sin((frame - delay) * 0.1);

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(-50%, -50%) scale(${s * pulse})`,
        opacity: s,
      }}
    >
      <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${color}88, ${color}22)`,
          border: `2px solid ${color}`,
          boxShadow: `0 0 ${size}px ${color}44`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: size + 8,
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: 14,
          fontWeight: 600,
          color,
          whiteSpace: "nowrap",
        }}
      >
        {label}
      </div>
    </div>
  );
};

export const Scene10_Platform: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  const titleSpring = spring({ frame, fps, durationInFrames: 25 });

  // Map outline
  const mapOpacity = interpolate(frame, [20, 50], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Text blocks
  const text1Opacity = interpolate(frame, [160, 190], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const text2Opacity = interpolate(frame, [210, 240], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Stats
  const statsSpring = spring({ frame: frame - 260, fps, durationInFrames: 25 });

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
        opacity: fadeIn * fadeOut,
        position: "relative",
      }}
    >
      <FilmGrain opacity={0.03} />
      <ParticleField count={30} />

      {/* LEFT — Map */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          position: "relative",
          zIndex: 10,
        }}
      >
        <div
          style={{
            width: 700,
            height: 500,
            position: "relative",
            opacity: mapOpacity,
          }}
        >
          <svg
            viewBox="0 0 700 500"
            style={{ width: "100%", height: "100%", position: "absolute" }}
          >
            <path
              d="M200,80 L280,60 L350,50 L450,55 L520,70 L560,90 L580,60 L620,80 L640,120 L630,160 L600,200 L560,230 L520,260 L500,300 L460,340 L420,370 L380,400 L340,420 L300,430 L260,410 L240,380 L220,340 L200,300 L180,260 L160,220 L140,180 L130,140 L150,100 Z"
              fill="none"
              stroke={COLORS.cobre}
              strokeWidth="2"
              opacity="0.4"
            />
          </svg>

          <HeatDot x={300} y={250} size={60} color={COLORS.red} label="Saltillo" delay={80} />
          <HeatDot x={450} y={300} size={80} color={COLORS.red} label="CDMX" delay={110} />
          <HeatDot x={350} y={230} size={40} color={COLORS.yellow} label="Monterrey" delay={130} />
          <HeatDot x={380} y={350} size={30} color={COLORS.yellow} label="Torreon" delay={150} />
          <HeatDot x={280} y={310} size={35} color={COLORS.yellow} label="Guadalajara" delay={170} />
        </div>
      </div>

      {/* RIGHT — Text */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "60px 80px 60px 40px",
          zIndex: 10,
        }}
      >
        <div
          style={{
            opacity: titleSpring,
            transform: `translateY(${(1 - titleSpring) * 20}px)`,
            fontSize: 44,
            fontWeight: 900,
            color: COLORS.cobre,
            marginBottom: 40,
            lineHeight: 1.2,
          }}
        >
          NahualPlatform
        </div>

        <div
          style={{
            opacity: text1Opacity,
            fontSize: 24,
            color: COLORS.cream,
            lineHeight: 1.6,
            marginBottom: 24,
          }}
        >
          Contribuciones anonimas construyen el{" "}
          <span style={{ color: COLORS.cobre, fontWeight: 700 }}>
            primer mapa abierto de reclutamiento criminal digital en Mexico
          </span>
        </div>

        <div
          style={{
            opacity: text2Opacity * 0.7,
            fontSize: 22,
            color: COLORS.cream,
            lineHeight: 1.6,
            marginBottom: 50,
          }}
        >
          Un mapa que hoy no existe y que las autoridades necesitan
        </div>

        {/* Stats cards */}
        <div
          style={{
            display: "flex",
            gap: 24,
            opacity: statsSpring,
            transform: `translateY(${(1 - statsSpring) * 20}px)`,
          }}
        >
          <div
            style={{
              background: "rgba(193,106,76,0.15)",
              borderRadius: 16,
              padding: "20px 28px",
              textAlign: "center",
              border: `1px solid ${COLORS.cobre}33`,
            }}
          >
            <AnimatedCounter
              to={900}
              startFrame={260}
              duration={50}
              style={{ fontSize: 40, fontWeight: 900, color: COLORS.cobre }}
            />
            <div style={{ fontSize: 14, color: COLORS.cream, opacity: 0.6 }}>
              Patrones
            </div>
          </div>
          <div
            style={{
              background: "rgba(34,197,94,0.15)",
              borderRadius: 16,
              padding: "20px 28px",
              textAlign: "center",
              border: `1px solid ${COLORS.green}33`,
            }}
          >
            <AnimatedCounter
              to={99.6}
              startFrame={275}
              duration={50}
              decimals={1}
              suffix="%"
              style={{ fontSize: 40, fontWeight: 900, color: COLORS.green }}
            />
            <div style={{ fontSize: 14, color: COLORS.cream, opacity: 0.6 }}>
              Accuracy
            </div>
          </div>
          <div
            style={{
              background: "rgba(239,68,68,0.15)",
              borderRadius: 16,
              padding: "20px 28px",
              textAlign: "center",
              border: `1px solid ${COLORS.red}33`,
            }}
          >
            <div style={{ fontSize: 40, fontWeight: 900, color: COLORS.red }}>
              0
            </div>
            <div style={{ fontSize: 14, color: COLORS.cream, opacity: 0.6 }}>
              Falsos negativos
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
