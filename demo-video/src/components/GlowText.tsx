import React from "react";
import { useCurrentFrame } from "remotion";
import { COLORS } from "../colors";

export const GlowText: React.FC<{
  text: string;
  fontSize?: number;
  color?: string;
  glowColor?: string;
  style?: React.CSSProperties;
}> = ({
  text,
  fontSize = 64,
  color = COLORS.cobre,
  glowColor = COLORS.cobreGlow,
  style,
}) => {
  const frame = useCurrentFrame();
  const pulse = 8 + 6 * Math.sin(frame * 0.06);

  return (
    <span
      style={{
        fontSize,
        fontWeight: 900,
        color,
        textShadow: `0 0 ${pulse}px ${glowColor}, 0 0 ${pulse * 2}px ${glowColor}44`,
        ...style,
      }}
    >
      {text}
    </span>
  );
};
