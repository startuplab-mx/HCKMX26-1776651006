import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./content/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        carbon: "var(--carbon)",
        "carbon-light": "var(--carbon-light)",
        "carbon-dark": "var(--carbon-dark)",
        cobre: "var(--cobre)",
        "cobre-light": "var(--cobre-light)",
        "cobre-dark": "var(--cobre-dark)",
        cream: "var(--cream)",
        success: "var(--green)",
        warning: "var(--yellow)",
        danger: "var(--red)"
      },
      fontFamily: {
        sans: ["var(--font-body)", "sans-serif"],
        display: ["var(--font-display)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"]
      },
      boxShadow: {
        copper: "0 0 0 1px rgba(193, 106, 76, 0.25), 0 24px 80px rgba(11, 14, 17, 0.45)",
        glow: "0 0 24px rgba(193, 106, 76, 0.28)"
      },
      backgroundImage: {
        "grid-carbon":
          "linear-gradient(rgba(245,240,235,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(245,240,235,0.06) 1px, transparent 1px)"
      },
      animation: {
        "pulse-grid": "pulseGrid 6s ease-in-out infinite",
        "flow-x": "flowX 9s linear infinite",
        "scan-line": "scanLine 5s linear infinite"
      },
      keyframes: {
        pulseGrid: {
          "0%, 100%": { opacity: "0.28" },
          "50%": { opacity: "0.58" }
        },
        flowX: {
          "0%": { transform: "translateX(-35%)" },
          "100%": { transform: "translateX(135%)" }
        },
        scanLine: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(200%)" }
        }
      }
    }
  },
  plugins: []
};

export default config;
