import { ImageResponse } from "next/og";

export const alt = "Nahual — Detección de Reclutamiento Criminal Digital";
export const size = {
  width: 1200,
  height: 630
};

export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          background:
            "radial-gradient(circle at top right, rgba(193,106,76,0.18), transparent 30%), linear-gradient(160deg, #0d1013 0%, #1e2428 55%, #13171b 100%)",
          color: "#f5f0eb",
          padding: 56,
          fontFamily: "Inter, sans-serif"
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            width: "100%",
            border: "1px solid rgba(245,240,235,0.12)",
            borderRadius: 28,
            padding: 42,
            background: "rgba(58,66,73,0.18)"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div
              style={{
                fontSize: 18,
                letterSpacing: "0.35em",
                textTransform: "uppercase",
                color: "#d4845a"
              }}
            >
              Hackathon 404 · Threat Not Found 2026
            </div>
            <div
              style={{
                fontSize: 18,
                letterSpacing: "0.24em",
                textTransform: "uppercase",
                color: "rgba(245,240,235,0.64)"
              }}
            >
              Protección digital para menores
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 44 }}>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 18 }}>
              <div
                style={{
                  fontSize: 118,
                  fontWeight: 900,
                  letterSpacing: "-0.07em",
                  lineHeight: 0.9
                }}
              >
                NAHUAL
              </div>
              <div
                style={{
                  fontSize: 32,
                  lineHeight: 1.2,
                  maxWidth: 640,
                  color: "rgba(245,240,235,0.84)"
                }}
              >
                Detecta manipulación digital antes de que escale a daño real.
              </div>
            </div>
            <div
              style={{
                width: 320,
                height: 320,
                borderRadius: 28,
                border: "1px solid rgba(193,106,76,0.3)",
                backgroundColor: "rgba(15,17,20,0.45)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 30,
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                color: "#d4845a"
              }}
            >
              Jaguar nodal
            </div>
          </div>
        </div>
      </div>
    ),
    {
      ...size
    }
  );
}
