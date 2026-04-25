import { site } from "@/content/site";

export function DashboardPreview() {
  return (
    <div className="metal-frame h-full">
      <div className="browser-top mb-4">
        <span className="terminal-text">panel de alertas</span>
        <span className="terminal-text text-cobre-light">monitoreo institucional</span>
      </div>
      <div className="space-y-4 rounded-[22px] border border-[rgba(245,240,235,0.08)] bg-[rgba(14,18,20,0.9)] p-4">
        <div className="grid gap-3 sm:grid-cols-4">
          {site.dashboardStats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-[18px] border border-[rgba(245,240,235,0.08)] bg-[rgba(245,240,235,0.04)] p-4"
            >
              <p className="terminal-text">{stat.label}</p>
              <p className="mt-3 text-3xl font-black text-cream">{stat.value}</p>
            </div>
          ))}
        </div>
        <div className="overflow-hidden rounded-[18px] border border-[rgba(245,240,235,0.08)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-[rgba(245,240,235,0.04)] text-[rgba(245,240,235,0.56)]">
              <tr>
                <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.22em]">Timestamp</th>
                <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.22em]">Plataforma</th>
                <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.22em]">Nivel</th>
                <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.22em]">Score</th>
                <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.22em]">Acción</th>
              </tr>
            </thead>
            <tbody>
              {site.dashboardRows.map((row) => (
                <tr
                  key={row.time}
                  className="border-t border-[rgba(245,240,235,0.06)] text-[rgba(245,240,235,0.74)]"
                >
                  <td className="px-4 py-4">{row.time}</td>
                  <td className="px-4 py-4">{row.platform}</td>
                  <td className="px-4 py-4">
                    <span
                      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                        row.level === "PELIGRO"
                          ? "bg-danger/15 text-danger"
                          : row.level === "ATENCIÓN"
                            ? "bg-warning/15 text-warning"
                            : "bg-success/15 text-success"
                      }`}
                    >
                      {row.level}
                    </span>
                  </td>
                  <td className="px-4 py-4 font-mono">{row.score}</td>
                  <td className="px-4 py-4">
                    <button className="rounded-full border border-[rgba(193,106,76,0.2)] px-3 py-1.5 text-xs font-semibold text-cobre-light">
                      Generar PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
