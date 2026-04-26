import React from "react";
import { COLORS } from "../colors";

export const BrowserMockup: React.FC<{
  children: React.ReactNode;
  url?: string;
  width?: number;
  height?: number;
}> = ({ children, url = "chrome-extension://nahual", width = 800, height = 560 }) => {
  return (
    <div
      style={{
        width,
        height,
        background: "#111",
        borderRadius: 16,
        overflow: "hidden",
        border: `2px solid ${COLORS.carbon}`,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Chrome bar */}
      <div
        style={{
          height: 40,
          background: "#2A2A2A",
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
          flexShrink: 0,
        }}
      >
        <div
          style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F57" }}
        />
        <div
          style={{ width: 12, height: 12, borderRadius: "50%", background: "#FEBC2E" }}
        />
        <div
          style={{ width: 12, height: 12, borderRadius: "50%", background: "#28C840" }}
        />
        <div
          style={{
            marginLeft: 20,
            flex: 1,
            height: 24,
            background: "#444",
            borderRadius: 6,
            display: "flex",
            alignItems: "center",
            paddingLeft: 12,
            fontSize: 12,
            color: "#888",
          }}
        >
          {url}
        </div>
      </div>

      {/* Content area */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {children}
      </div>
    </div>
  );
};
