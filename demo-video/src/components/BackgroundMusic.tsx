import React from "react";
import { Audio, staticFile, interpolate, useCurrentFrame } from "remotion";

export const BackgroundMusic: React.FC<{
  src?: string;
  totalFrames?: number;
}> = ({ src = "music.mp3", totalFrames = 5400 }) => {
  const frame = useCurrentFrame();

  // Volume keyframes: fade in, low during content, up during transitions, fade out
  const volume = interpolate(
    frame,
    [0, 60, 120, totalFrames - 180, totalFrames - 30, totalFrames],
    [0, 0.12, 0.08, 0.08, 0.04, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  try {
    return <Audio src={staticFile(src)} volume={volume} />;
  } catch {
    return null;
  }
};
