import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import { noise3D } from "@remotion/noise";

const COLS = 50;
const ROWS = 28;

export const FilmGrain: React.FC<{ opacity?: number }> = ({
  opacity = 0.04,
}) => {
  const frame = useCurrentFrame();

  const cells = useMemo(() => {
    const result: { x: number; y: number; key: string }[] = [];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        result.push({ x: c, y: r, key: `${c}-${r}` });
      }
    }
    return result;
  }, []);

  const cellW = 1920 / COLS;
  const cellH = 1080 / ROWS;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: 1920,
        height: 1080,
        pointerEvents: "none",
        zIndex: 100,
      }}
    >
      <svg width={1920} height={1080}>
        {cells.map(({ x, y, key }) => {
          const n = noise3D("grain", x * 0.3, y * 0.3, frame * 0.15);
          const brightness = 128 + Math.round(n * 128);
          return (
            <rect
              key={key}
              x={x * cellW}
              y={y * cellH}
              width={cellW}
              height={cellH}
              fill={`rgb(${brightness},${brightness},${brightness})`}
              opacity={opacity}
            />
          );
        })}
      </svg>
    </div>
  );
};
