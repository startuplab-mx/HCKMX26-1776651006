import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

export const AnimatedCounter: React.FC<{
  from?: number;
  to: number;
  startFrame: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  style?: React.CSSProperties;
}> = ({
  from = 0,
  to,
  startFrame,
  duration = 60,
  decimals = 0,
  suffix = "",
  prefix = "",
  style,
}) => {
  const frame = useCurrentFrame();

  const value = interpolate(
    frame,
    [startFrame, startFrame + duration],
    [from, to],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <span style={style}>
      {prefix}
      {decimals > 0 ? value.toFixed(decimals) : Math.round(value)}
      {suffix}
    </span>
  );
};
