import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { COLORS } from "../colors";

export const ScoreThermometer: React.FC<{
  score: number;
  startFrame: number;
  duration?: number;
  width?: number;
  height?: number;
  showLabel?: boolean;
}> = ({
  score,
  startFrame,
  duration = 60,
  width = 400,
  height = 32,
  showLabel = true,
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(
    frame,
    [startFrame, startFrame + duration],
    [0, score / 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const currentScore = progress * 100;
  const color =
    currentScore < 33
      ? COLORS.green
      : currentScore < 66
        ? COLORS.yellow
        : COLORS.red;

  const label =
    currentScore < 33
      ? "SEGURO"
      : currentScore < 66
        ? "ATENCION"
        : "PELIGRO";

  return (
    <div style={{ width }}>
      <div
        style={{
          width: "100%",
          height,
          borderRadius: height / 2,
          background: "rgba(255,255,255,0.08)",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: "100%",
            borderRadius: height / 2,
            background: `linear-gradient(90deg, ${COLORS.green}, ${COLORS.yellow}, ${COLORS.red})`,
            transition: "none",
          }}
        />
      </div>
      {showLabel && currentScore > 5 && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: 8,
            fontSize: 16,
            fontWeight: 700,
          }}
        >
          <span style={{ color }}>{label}</span>
          <span style={{ color }}>{Math.round(currentScore)}%</span>
        </div>
      )}
    </div>
  );
};
