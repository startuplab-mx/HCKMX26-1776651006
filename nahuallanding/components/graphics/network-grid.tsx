export function NetworkGrid() {
  const nodes = [
    { left: "8%", top: "12%" },
    { left: "21%", top: "26%" },
    { left: "39%", top: "10%" },
    { left: "52%", top: "20%" },
    { left: "67%", top: "14%" },
    { left: "83%", top: "22%" },
    { left: "14%", top: "62%" },
    { left: "29%", top: "54%" },
    { left: "51%", top: "63%" },
    { left: "73%", top: "58%" },
    { left: "88%", top: "72%" }
  ];

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(193,106,76,0.12),transparent_35%),linear-gradient(180deg,rgba(255,255,255,0.02),transparent_30%)]" />
      <div className="absolute inset-0 grid-background animate-pulse-grid opacity-30" />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent,rgba(193,106,76,0.05),transparent)] opacity-60" />
      <svg
        className="absolute inset-0 h-full w-full opacity-50"
        viewBox="0 0 1440 900"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M64 194H412L590 86L812 182H1180L1368 118"
          stroke="rgba(245,240,235,0.08)"
          strokeWidth="1.25"
          strokeDasharray="4 10"
        />
        <path
          d="M38 640H312L418 512H742L886 604H1320"
          stroke="rgba(245,240,235,0.08)"
          strokeWidth="1.25"
          strokeDasharray="4 10"
        />
        <path
          d="M214 122L368 296L650 252L866 400L1184 336"
          stroke="rgba(193,106,76,0.12)"
          strokeWidth="1.2"
          strokeDasharray="6 12"
        />
      </svg>
      {nodes.map((node, index) => (
        <span
          key={`${node.left}-${node.top}`}
          className="absolute h-2.5 w-2.5 rounded-full bg-cobre/60 shadow-[0_0_18px_rgba(193,106,76,0.55)]"
          style={{
            left: node.left,
            top: node.top,
            animationDelay: `${index * 0.28}s`
          }}
        />
      ))}
    </div>
  );
}
