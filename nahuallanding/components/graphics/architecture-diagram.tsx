"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useMemo, useState } from "react";

import { site } from "@/content/site";

export function ArchitectureDiagram() {
  const reduceMotion = useReducedMotion();
  const [activeNode, setActiveNode] = useState(site.architectureNodes[1].id);

  const nodeMap = useMemo(
    () => new Map(site.architectureNodes.map((node) => [node.id, node])),
    []
  );

  const selected = nodeMap.get(activeNode) ?? site.architectureNodes[1];

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <div className="panel overflow-hidden p-4 sm:p-6">
        <div className="browser-top mb-6">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-danger" />
            <span className="h-2.5 w-2.5 rounded-full bg-warning" />
            <span className="h-2.5 w-2.5 rounded-full bg-success" />
          </div>
          <span className="terminal-text">arquitectura modular / open source</span>
        </div>
        <div className="relative overflow-hidden rounded-[24px] border border-[rgba(245,240,235,0.08)] bg-[rgba(15,17,20,0.6)] p-2">
          <svg viewBox="0 0 720 500" className="h-auto w-full" fill="none" aria-label="Diagrama de arquitectura">
            {site.architectureEdges.map((edge, index) => {
              const from = nodeMap.get(edge.from);
              const to = nodeMap.get(edge.to);

              if (!from || !to) {
                return null;
              }

              const startX = from.x + from.w / 2;
              const startY = from.y + from.h;
              const endX = to.x + to.w / 2;
              const endY = to.y;

              return (
                <g key={`${edge.from}-${edge.to}`}>
                  <path
                    d={`M${startX} ${startY} C ${startX} ${(startY + endY) / 2}, ${endX} ${(startY + endY) / 2}, ${endX} ${endY}`}
                    stroke="rgba(245,240,235,0.18)"
                    strokeWidth="1.2"
                    strokeDasharray="4 10"
                  />
                  {reduceMotion ? null : (
                    <motion.circle
                      r="4"
                      fill="#d4845a"
                      animate={{
                        cx: [startX, endX],
                        cy: [startY, endY]
                      }}
                      transition={{
                        duration: 2.6,
                        repeat: Infinity,
                        ease: "linear",
                        delay: index * 0.22
                      }}
                    />
                  )}
                </g>
              );
            })}

            {site.architectureNodes.map((node, index) => (
              <motion.g
                key={node.id}
                onMouseEnter={() => setActiveNode(node.id)}
                onFocus={() => setActiveNode(node.id)}
                tabIndex={0}
                initial={reduceMotion ? false : { opacity: 0, y: 12 }}
                whileInView={reduceMotion ? undefined : { opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{
                  duration: 0.55,
                  ease: [0.22, 1, 0.36, 1],
                  delay: 0.1 + index * 0.06
                }}
              >
                <rect
                  x={node.x}
                  y={node.y}
                  width={node.w}
                  height={node.h}
                  rx={16}
                  fill={activeNode === node.id ? "rgba(193,106,76,0.15)" : "rgba(58,66,73,0.58)"}
                  stroke={activeNode === node.id ? "rgba(212,132,90,0.9)" : "rgba(245,240,235,0.12)"}
                  strokeWidth="1.6"
                />
                <text
                  x={node.x + node.w / 2}
                  y={node.y + 22}
                  textAnchor="middle"
                  fill="#f5f0eb"
                  fontSize="14"
                  fontWeight="700"
                  letterSpacing="-0.02em"
                >
                  {node.title}
                </text>
                <text
                  x={node.x + node.w / 2}
                  y={node.y + 39}
                  textAnchor="middle"
                  fill="rgba(245,240,235,0.56)"
                  fontSize="10"
                  letterSpacing="0.24em"
                >
                  {node.subtitle.toUpperCase()}
                </text>
              </motion.g>
            ))}
          </svg>
        </div>
      </div>

      <div className="space-y-4">
        <div className="panel p-5">
          <p className="terminal-text mb-3 text-cobre-light">tooltip técnico</p>
          <h3 className="text-2xl font-black text-cream">{selected.title}</h3>
          <p className="mt-2 font-mono text-xs uppercase tracking-[0.22em] text-[rgba(245,240,235,0.5)]">
            {selected.subtitle}
          </p>
          <p className="mt-4 text-sm leading-7 text-dim">{selected.detail}</p>
        </div>
        <div className="panel p-5">
          <p className="terminal-text mb-4">stack</p>
          <div className="flex flex-wrap gap-2">
            {site.techStack.map((tech) => (
              <span
                key={tech}
                className="rounded-full border border-[rgba(245,240,235,0.08)] bg-[rgba(245,240,235,0.04)] px-3 py-1.5 text-sm text-[rgba(245,240,235,0.74)]"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
