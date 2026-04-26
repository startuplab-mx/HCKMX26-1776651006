import React from "react";
import { COLORS } from "../colors";

export const DashboardMockup: React.FC<{
  children: React.ReactNode;
  sidebarItems?: string[];
  activeItem?: number;
  width?: number;
  height?: number;
}> = ({
  children,
  sidebarItems = ["Dashboard", "Alertas", "Patrones", "Mapa", "Config"],
  activeItem = 0,
  width = 1600,
  height = 860,
}) => {
  return (
    <div
      style={{
        width,
        height,
        background: COLORS.darkGray,
        borderRadius: 20,
        overflow: "hidden",
        border: `2px solid ${COLORS.carbon}`,
        display: "flex",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          width: 220,
          background: COLORS.carbon,
          padding: "30px 0",
          display: "flex",
          flexDirection: "column",
          flexShrink: 0,
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "0 24px",
            marginBottom: 40,
          }}
        >
          <span style={{ fontSize: 24 }}>🛡️</span>
          <span
            style={{
              fontSize: 20,
              fontWeight: 900,
              color: COLORS.cobre,
              letterSpacing: 2,
            }}
          >
            NAHUAL
          </span>
        </div>

        {/* Nav items */}
        {sidebarItems.map((item, i) => (
          <div
            key={item}
            style={{
              padding: "12px 24px",
              fontSize: 15,
              color: i === activeItem ? COLORS.cobre : COLORS.cream,
              fontWeight: i === activeItem ? 700 : 400,
              opacity: i === activeItem ? 1 : 0.5,
              background:
                i === activeItem ? "rgba(193,106,76,0.1)" : "transparent",
              borderLeft:
                i === activeItem
                  ? `3px solid ${COLORS.cobre}`
                  : "3px solid transparent",
            }}
          >
            {item}
          </div>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, padding: 30, overflow: "hidden" }}>
        {children}
      </div>
    </div>
  );
};
