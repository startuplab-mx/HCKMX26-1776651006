import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../colors";

interface ChatMsg {
  from: "user" | "bot";
  text: string;
  color?: string;
  delay: number;
}

const ChatBubble: React.FC<{
  msg: ChatMsg;
}> = ({ msg }) => {
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
        marginBottom: 12,
        opacity: s,
        transform: `translateY(${(1 - s) * 15}px)`,
      }}
    >
      <div
        style={{
          maxWidth: 580,
          padding: "16px 22px",
          borderRadius: isUser ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
          background: isUser ? "#075E54" : "#1E2A30",
          fontSize: 22,
          lineHeight: 1.5,
          color: msg.color || COLORS.cream,
          whiteSpace: "pre-wrap",
        }}
      >
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
        marginBottom: 12,
      }}
    >
      <div
        style={{
          padding: "16px 24px",
          borderRadius: "20px 20px 20px 4px",
          background: "#1E2A30",
          display: "flex",
          gap: 8,
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 10,
              height: 10,
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

export const Scene4_BotDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in
  const fadeIn = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const messages: ChatMsg[] = [
    { from: "user", text: "Hola", delay: 40 },
    {
      from: "bot",
      text: "🛡️ Hola, soy Nahual. Estoy aqui para ayudarte a identificar si alguien esta intentando reclutarte o amenazarte en linea.",
      delay: 80,
    },
    {
      from: "user",
      text: "Me dijeron que si no respondo me van a matar",
      delay: 180,
    },
    {
      from: "bot",
      text: "Recibido. Dame unos segundos... 🔍",
      delay: 240,
    },
    {
      from: "bot",
      text: "🚨 PELIGRO — Actua ahora\n\nRiesgo: 100%\nFase: Coercion",
      color: COLORS.red,
      delay: 340,
    },
    {
      from: "bot",
      text: "🧠 Por que?\n1. Se detecto amenaza directa recibida\n2. Patron de coercion activa",
      delay: 420,
    },
    {
      from: "bot",
      text: "🛡️ Guia legal · 🔴 URGENCIA INMEDIATA\n\nContactos:\n• Policia Cibernetica: 088\n• Linea de la Vida: 800-911-2000",
      color: COLORS.yellow,
      delay: 510,
    },
    {
      from: "bot",
      text: "Me das el WhatsApp de un adulto de confianza?",
      delay: 600,
    },
    { from: "user", text: "+52 844 597 8949", delay: 670 },
    {
      from: "bot",
      text: "✅ Aviso + reporte PDF enviados al adulto de confianza",
      color: COLORS.green,
      delay: 730,
    },
  ];

  // PDF mockup appears at the end
  const pdfOpacity = interpolate(frame, [780, 810], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const pdfSpring = spring({
    frame: frame - 780,
    fps,
    durationInFrames: 25,
  });

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
      {/* Phone mockup - left side */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            width: 480,
            height: 900,
            background: "#0B141A",
            borderRadius: 40,
            border: `3px solid ${COLORS.carbon}`,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* WhatsApp header */}
          <div
            style={{
              background: "#1F2C34",
              padding: "20px 24px",
              display: "flex",
              alignItems: "center",
              gap: 16,
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: "50%",
                background: `linear-gradient(135deg, ${COLORS.cobre}, ${COLORS.cobreLight})`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
              }}
            >
              🛡️
            </div>
            <div>
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: COLORS.cream,
                }}
              >
                Nahual
              </div>
              <div style={{ fontSize: 13, color: "#8696A0" }}>en linea</div>
            </div>
          </div>

          {/* Chat area */}
          <div
            style={{
              flex: 1,
              padding: "20px 16px",
              overflowY: "hidden",
              display: "flex",
              flexDirection: "column",
              justifyContent: "flex-end",
            }}
          >
            <TypingIndicator showAt={60} hideAt={80} />
            {messages.map((msg, i) => (
              <ChatBubble key={i} msg={msg} />
            ))}
            <TypingIndicator showAt={220} hideAt={240} />
            <TypingIndicator showAt={300} hideAt={340} />
          </div>
        </div>
      </div>

      {/* PDF mockup - right side */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            opacity: pdfOpacity,
            transform: `scale(${pdfSpring}) rotate(${(1 - pdfSpring) * -5}deg)`,
            width: 500,
            background: COLORS.white,
            borderRadius: 12,
            padding: 48,
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 30,
            }}
          >
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                color: COLORS.carbon,
              }}
            >
              🛡️ NAHUAL
            </div>
            <div
              style={{
                fontSize: 14,
                color: COLORS.red,
                fontWeight: 700,
                background: "#FEE2E2",
                padding: "4px 12px",
                borderRadius: 8,
              }}
            >
              PELIGRO
            </div>
          </div>

          <div
            style={{
              fontSize: 14,
              color: "#666",
              marginBottom: 6,
            }}
          >
            Folio: NAH-2026-0847
          </div>
          <div
            style={{
              fontSize: 14,
              color: "#666",
              marginBottom: 24,
              borderBottom: "1px solid #eee",
              paddingBottom: 16,
            }}
          >
            Fecha: 25/04/2026
          </div>

          <div
            style={{ fontSize: 18, fontWeight: 700, color: COLORS.carbon, marginBottom: 12 }}
          >
            Resultado del analisis
          </div>
          <div style={{ fontSize: 15, color: "#444", lineHeight: 1.8 }}>
            Nivel de riesgo:{" "}
            <span style={{ color: COLORS.red, fontWeight: 700 }}>100%</span>
            <br />
            Fase detectada:{" "}
            <span style={{ fontWeight: 600 }}>Coercion</span>
            <br />
            Patron: Amenaza directa
            <br />
            Recomendacion: Contacto inmediato con autoridades
          </div>

          <div
            style={{
              marginTop: 24,
              padding: "12px 16px",
              background: "#FEF3C7",
              borderRadius: 8,
              fontSize: 13,
              color: "#92400E",
            }}
          >
            Este reporte fue generado automaticamente por Nahual y no
            constituye un dictamen legal.
          </div>
        </div>
      </div>
    </div>
  );
};
