import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import { COLORS } from "../colors";

interface Particle {
  id: number;
  baseX: number;
  baseY: number;
  size: number;
  speed: number;
  phase: number;
  depth: number;
}

export const ParticleField: React.FC<{ count?: number }> = ({
  count = 50,
}) => {
  const frame = useCurrentFrame();

  const particles = useMemo<Particle[]>(() => {
    const result: Particle[] = [];
    for (let i = 0; i < count; i++) {
      const seed = i * 7919;
      result.push({
        id: i,
        baseX: ((seed * 13) % 1920),
        baseY: ((seed * 17) % 1080),
        size: 2 + (seed % 4),
        speed: 0.3 + ((seed * 3) % 10) / 10,
        phase: (seed % 628) / 100,
        depth: 0.3 + ((seed * 11) % 7) / 10,
      });
    }
    return result;
  }, [count]);

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: 1920,
        height: 1080,
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      {particles.map((p) => {
        const x = p.baseX + Math.sin(frame * 0.02 * p.speed + p.phase) * 30;
        const y = p.baseY + Math.cos(frame * 0.015 * p.speed + p.phase) * 20 - frame * 0.3 * p.speed;
        const wrappedY = ((y % 1080) + 1080) % 1080;
        const alpha = p.depth * (0.4 + 0.3 * Math.sin(frame * 0.03 + p.phase));

        return (
          <div
            key={p.id}
            style={{
              position: "absolute",
              left: x,
              top: wrappedY,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background: COLORS.cobre,
              opacity: alpha,
              boxShadow: `0 0 ${p.size * 2}px ${COLORS.cobre}44`,
            }}
          />
        );
      })}
    </div>
  );
};
