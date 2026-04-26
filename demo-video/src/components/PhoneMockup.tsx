import React from "react";
import { COLORS } from "../colors";

export const PhoneMockup: React.FC<{
  children: React.ReactNode;
  headerTitle?: string;
  headerSubtitle?: string;
  width?: number;
  height?: number;
}> = ({
  children,
  headerTitle = "Nahual",
  headerSubtitle = "en linea",
  width = 480,
  height = 900,
}) => {
  return (
    <div
      style={{
        width,
        height,
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
          flexShrink: 0,
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
            {headerTitle}
          </div>
          <div style={{ fontSize: 13, color: "#8696A0" }}>{headerSubtitle}</div>
        </div>
      </div>

      {/* Chat content */}
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
        {children}
      </div>
    </div>
  );
};
