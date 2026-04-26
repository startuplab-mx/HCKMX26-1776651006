import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

import { PhoneMockup } from "../components/PhoneMockup";
import { ScoreThermometer } from "../components/ScoreThermometer";

interface ChatMsg {
  from: "user" | "bot";
  text: string;
  color?: string;
  delay: number;
  badge?: string;
  badgeColor?: string;
}

const ChatBubble: React.FC<{ msg: ChatMsg }> = ({ msg }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - msg.delay,
    fps,
    durationInFrames: 15,
    config: { mass: 0.4, damping: 12 },
  });

  if (frame < msg.delay) return null;
  const isUser = msg.from === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 10,
        opacity: s,
        transform: `translateY(${(1 - s) * 12}px)`,
      }}
    >
      <div
        style={{
          maxWidth: 400,
          padding: "14px 18px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          background: isUser ? "#075E54" : "#1E2A30",
          fontSize: 18,
          lineHeight: 1.5,
          color: msg.color || COLORS.cream,
          whiteSpace: "pre-wrap",
          position: "relative",
        }}
      >
        {msg.badge && (
          <div
            style={{
              display: "inline-block",
              padding: "2px 8px",
              borderRadius: 6,
              background: `${msg.badgeColor || COLORS.red}22`,
              color: msg.badgeColor || COLORS.red,
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: 1,
              marginBottom: 6,
            }}
          >
            {msg.badge}
          </div>
        )}
        {msg.text}
      </div>
    </div>
  );
};

const TypingIndicator: React.FC<{ showAt: number; hideAt: number }> = ({
  showAt,
  hideAt,
}) => {
  const frame = useCurrentFrame();
  if (frame < showAt || frame >= hideAt) return null;
  const dotPhase = (frame - showAt) * 0.15;

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "flex-start",
        marginBottom: 10,
      }}
    >
      <div
        style={{
          padding: "14px 20px",
          borderRadius: "18px 18px 18px 4px",
          background: "#1E2A30",
          display: "flex",
          gap: 6,
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: COLORS.cobreLight,
              opacity: 0.4 + 0.6 * Math.abs(Math.sin(dotPhase + i * 1.2)),
            }}
          />
        ))}
      </div>
    </div>
  );
};

export const Scene5_BotDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 5 progressive messages showing score escalation
  const messages: ChatMsg[] = [
    { from: "user", text: "Hola", delay: 30 },
    {
      from: "bot",
      text: "🛡️ Hola, soy Nahual. Estoy aqui para ayudarte a identificar si alguien esta intentando reclutarte.",
      delay: 70,
    },
    {
      from: "user",
      text: "Un vato me ofrecio $15k a la semana por mover cosas",
      delay: 160,
    },
    {
      from: "bot",
      text: "⚠️ ATENCION — Riesgo: 78%\nFase: Enganche\nPatron: Oferta economica sospechosa",
      color: COLORS.yellow,
      delay: 230,
      badge: "HEURISTIC",
      badgeColor: COLORS.yellow,
    },
    {
      from: "user",
      text: "Tambien me dijo que si no acepto me van a buscar",
      delay: 340,
    },
    {
      from: "bot",
      text: "🚨 PELIGRO — Riesgo: 96%\nFase: Coercion\nAmenaza directa detectada",
      color: COLORS.red,
      delay: 410,
      badge: "OVERRIDE",
      badgeColor: COLORS.red,
    },
    {
      from: "user",
      text: "Me dijeron que si no respondo me van a matar",
      delay: 490,
    },
    {
      from: "bot",
      text: "🚨 PELIGRO CRITICO — Riesgo: 100%\nFase: Coercion maxima\n\n📞 Policia Cibernetica: 088\n📞 Linea de la Vida: 800-911-2000\n\n¿Me das el WhatsApp de un adulto de confianza?",
      color: COLORS.red,
      delay: 560,
      badge: "OVERRIDE",
      badgeColor: COLORS.red,
    },
    { from: "user", text: "+52 844 597 8949", delay: 660 },
    {
      from: "bot",
      text: "✅ Aviso + reporte PDF enviados al adulto de confianza",
      color: COLORS.green,
      delay: 720,
    },
  ];

  // Score graph (SVG path with strokeDasharray animation)
  const scorePoints = [
    { frame: 0, score: 0 },
    { frame: 230, score: 0 },
    { frame: 280, score: 78 },
    { frame: 410, score: 78 },
    { frame: 450, score: 96 },
    { frame: 560, score: 96 },
    { frame: 600, score: 100 },
  ];

  const graphW = 380;
  const graphH = 180;
  const graphPath = scorePoints
    .map((p, i) => {
      const x = (p.frame / 750) * graphW;
      const y = graphH - (p.score / 100) * (graphH - 20);
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
  const graphLen = 800;
  const graphProgress = interpolate(frame, [60, 750], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // PDF mockup
  const pdfOpacity = interpolate(frame, [760, 790], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pdfSpring = spring({ frame: frame - 760, fps, durationInFrames: 25 });

  // Guardian notification
  const notifOpacity = interpolate(frame, [810, 840], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const notifSpring = spring({ frame: frame - 810, fps, durationInFrames: 20 });

  // Fade out
  const fadeOut = interpolate(frame, [870, 900], [1, 0], {
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
      {/* LEFT — Phone mockup */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 10,
        }}
      >
        <PhoneMockup>
          <TypingIndicator showAt={50} hideAt={70} />
          {messages.map((msg, i) => (
            <ChatBubble key={i} msg={msg} />
          ))}
          <TypingIndicator showAt={200} hideAt={230} />
          <TypingIndicator showAt={380} hideAt={410} />
          <TypingIndicator showAt={530} hideAt={560} />
          <TypingIndicator showAt={690} hideAt={720} />
        </PhoneMockup>
      </div>

      {/* RIGHT — Score graph + PDF + notification */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 40,
          gap: 30,
          zIndex: 10,
        }}
      >
        {/* Score graph */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            borderRadius: 20,
            padding: 30,
            width: graphW + 60,
          }}
        >
          <div
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: COLORS.cream,
              marginBottom: 16,
            }}
          >
            Score de riesgo en tiempo real
          </div>
          <svg width={graphW} height={graphH}>
            {/* Grid lines */}
            {[0, 33, 66, 100].map((v) => (
              <line
                key={v}
                x1={0}
                x2={graphW}
                y1={graphH - (v / 100) * (graphH - 20)}
                y2={graphH - (v / 100) * (graphH - 20)}
                stroke="rgba(255,255,255,0.06)"
                strokeWidth={1}
              />
            ))}
            {/* Score path */}
            <path
              d={graphPath}
              fill="none"
              stroke={COLORS.cobre}
              strokeWidth={3}
              strokeDasharray={graphLen}
              strokeDashoffset={graphLen * (1 - graphProgress)}
              strokeLinecap="round"
            />
            {/* Area */}
            <path
              d={`${graphPath} L ${graphW} ${graphH} L 0 ${graphH} Z`}
              fill={`${COLORS.cobre}08`}
              opacity={graphProgress}
            />
          </svg>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 11,
              color: COLORS.cream,
              opacity: 0.4,
              marginTop: 6,
            }}
          >
            <span>Inicio</span>
            <span>78%</span>
            <span>96%</span>
            <span>100%</span>
          </div>
        </div>

        {/* PDF mockup */}
        <div
          style={{
            opacity: pdfOpacity,
            transform: `scale(${pdfSpring}) rotate(${(1 - pdfSpring) * -3}deg)`,
            width: 420,
            background: COLORS.white,
            borderRadius: 12,
            padding: 32,
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <div style={{ fontSize: 22, fontWeight: 900, color: COLORS.carbon }}>
              🛡️ NAHUAL
            </div>
            <div
              style={{
                fontSize: 12,
                color: COLORS.red,
                fontWeight: 700,
                background: "#FEE2E2",
                padding: "3px 10px",
                borderRadius: 6,
              }}
            >
              PELIGRO
            </div>
          </div>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
            Folio: NAH-2026-0847
          </div>
          <div style={{ fontSize: 12, color: "#666", marginBottom: 12 }}>
            Riesgo: 100% · Fase: Coercion · Patron: Amenaza directa
          </div>
          <div
            style={{
              padding: "8px 12px",
              background: "#FEF3C7",
              borderRadius: 6,
              fontSize: 11,
              color: "#92400E",
            }}
          >
            Reporte generado automaticamente por Nahual
          </div>
        </div>

        {/* Guardian notification */}
        <div
          style={{
            opacity: notifOpacity,
            transform: `translateY(${(1 - notifSpring) * 20}px)`,
            padding: "16px 24px",
            background: "rgba(34,197,94,0.1)",
            borderRadius: 16,
            border: `1px solid ${COLORS.green}44`,
            display: "flex",
            alignItems: "center",
            gap: 16,
            width: 420,
          }}
        >
          <div style={{ fontSize: 32 }}>📱</div>
          <div>
            <div
              style={{
                fontSize: 16,
                fontWeight: 700,
                color: COLORS.green,
                marginBottom: 4,
              }}
            >
              Notificacion enviada al guardian
            </div>
            <div style={{ fontSize: 13, color: COLORS.cream, opacity: 0.7 }}>
              +52 844 597 8949 · Reporte PDF adjunto
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
