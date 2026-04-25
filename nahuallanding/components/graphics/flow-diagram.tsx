"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

const orderedNodes = [
  "INICIO",
  "BIENVENIDA",
  "RECIBIR_MSG",
  "ANALIZANDO",
  "ATENCIÓN",
  "PELIGRO",
  "ALERTAR",
  "REPORTE"
];

export function FlowDiagram() {
  const reduceMotion = useReducedMotion();
  const [active, setActive] = useState(0);

  useEffect(() => {
    if (reduceMotion) {
      return;
    }

    const timer = window.setInterval(() => {
      setActive((current) => (current + 1) % orderedNodes.length);
    }, 900);

    return () => window.clearInterval(timer);
  }, [reduceMotion]);

  const isActive = (id: string) => orderedNodes.indexOf(id) <= active;

  return (
    <div className="panel p-5 sm:p-6">
      <div className="browser-top mb-5">
        <span className="terminal-text">state machine / bot orchestration</span>
        <span className="terminal-text text-cobre-light">flujo conversacional</span>
      </div>
      <svg viewBox="0 0 980 420" className="h-auto w-full" fill="none" aria-label="Flujo conversacional">
        <defs>
          <linearGradient id="flowCopper" x1="0" x2="1" y1="0.5" y2="0.5">
            <stop offset="0%" stopColor="rgba(245,240,235,0.18)" />
            <stop offset="100%" stopColor="rgba(212,132,90,0.7)" />
          </linearGradient>
        </defs>

        {[
          "M118 104 H260",
          "M378 104 H520",
          "M638 104 H760",
          "M830 104 V200",
          "M830 200 H700",
          "M830 200 H905",
          "M700 200 V308",
          "M905 200 V308"
        ].map((path, index) => (
          <path
            key={path}
            d={path}
            stroke="url(#flowCopper)"
            strokeWidth="2"
            strokeDasharray="5 8"
            opacity={isActive(orderedNodes[Math.min(index, orderedNodes.length - 1)]) ? 1 : 0.24}
          />
        ))}

        {[
          { id: "INICIO", x: 40, y: 72, w: 78, h: 62, fill: "rgba(58,66,73,0.74)" },
          { id: "BIENVENIDA", x: 260, y: 58, w: 120, h: 90, fill: "rgba(58,66,73,0.74)" },
          { id: "RECIBIR_MSG", x: 520, y: 58, w: 120, h: 90, fill: "rgba(58,66,73,0.74)" },
          { id: "ANALIZANDO", x: 760, y: 58, w: 140, h: 92, fill: "rgba(193,106,76,0.12)" },
          { id: "SEGURO", x: 234, y: 284, w: 110, h: 78, fill: "rgba(34,197,94,0.14)" },
          { id: "ATENCIÓN", x: 524, y: 284, w: 110, h: 78, fill: "rgba(234,179,8,0.14)" },
          { id: "PELIGRO", x: 684, y: 172, w: 116, h: 56, fill: "rgba(239,68,68,0.16)" },
          { id: "ALERTAR", x: 642, y: 308, w: 110, h: 78, fill: "rgba(239,68,68,0.12)" },
          { id: "REPORTE", x: 850, y: 308, w: 110, h: 78, fill: "rgba(193,106,76,0.14)" },
          { id: "INFO", x: 418, y: 284, w: 88, h: 78, fill: "rgba(245,240,235,0.04)" }
        ].map((node, index) => (
          <motion.g
            key={node.id}
            initial={reduceMotion ? false : { opacity: 0, y: 10 }}
            whileInView={reduceMotion ? undefined : { opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{
              duration: 0.5,
              delay: 0.08 + index * 0.04,
              ease: [0.22, 1, 0.36, 1]
            }}
          >
            <rect
              x={node.x}
              y={node.y}
              rx="18"
              width={node.w}
              height={node.h}
              fill={node.fill}
              stroke={isActive(node.id) ? "rgba(212,132,90,0.85)" : "rgba(245,240,235,0.1)"}
              strokeWidth="1.4"
            />
            <text
              x={node.x + node.w / 2}
              y={node.y + node.h / 2 - 6}
              textAnchor="middle"
              fill="#f5f0eb"
              fontSize="14"
              fontWeight="700"
              letterSpacing="0.08em"
            >
              {node.id}
            </text>
            {node.id === "ANALIZANDO" ? (
              <text
                x={node.x + node.w / 2}
                y={node.y + node.h / 2 + 18}
                textAnchor="middle"
                fill="rgba(245,240,235,0.54)"
                fontSize="11"
                letterSpacing="0.16em"
              >
                SPINNER + SCORE
              </text>
            ) : null}
          </motion.g>
        ))}
      </svg>
    </div>
  );
}
