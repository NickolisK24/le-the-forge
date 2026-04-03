/**
 * N14 — Comparison Dashboard
 *
 * Side-by-side comparison of two build snapshots with a grouped bar chart
 * and differential section.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface BuildSnapshot {
  build_id: string;
  label: string;
  total_damage: number;
  dps: number;
  crit_rate: number;
  buff_uptime_pct: number;
  kill_time: number | null;
  reliability_score: number;
}

export interface ComparisonDashboardProps {
  builds: BuildSnapshot[];
  differential?: Record<string, number>;
  winner_by_metric?: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const METRICS: { key: keyof BuildSnapshot; label: string }[] = [
  { key: "total_damage",      label: "Total Damage" },
  { key: "dps",               label: "DPS" },
  { key: "crit_rate",         label: "Crit Rate" },
  { key: "buff_uptime_pct",   label: "Buff Uptime %" },
  { key: "reliability_score", label: "Reliability" },
];

function fmt(v: number | null): string {
  if (v === null) return "—";
  return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ComparisonDashboard({
  builds,
  differential,
  winner_by_metric,
}: ComparisonDashboardProps) {
  if (builds.length < 2) {
    return (
      <div className="rounded border border-[#2a3050] bg-[#10152a] p-8 flex items-center justify-center">
        <span className="font-mono text-sm text-[#6b7280]">
          Add at least 2 builds to compare
        </span>
      </div>
    );
  }

  const a = builds[0];
  const b = builds[1];

  // Build chart data
  const chartData = METRICS.map(({ key, label }) => ({
    metric: label,
    [a.label]: typeof a[key] === "number" ? (a[key] as number) : 0,
    [b.label]: typeof b[key] === "number" ? (b[key] as number) : 0,
  }));

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4 space-y-6">
      <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280]">
        Build Comparison
      </p>

      {/* Two-column metric table */}
      <div className="grid grid-cols-2 gap-4">
        {[a, b].map((build, idx) => (
          <div key={build.build_id} className="rounded border border-[#2a3050] bg-[#0d1124] p-3">
            <p className={`font-mono text-xs font-bold mb-2 ${idx === 0 ? "text-[#f5a623]" : "text-[#22d3ee]"}`}>
              {build.label}
            </p>
            {METRICS.map(({ key, label }) => {
              const isWinner = winner_by_metric?.[key] === build.build_id;
              return (
                <div
                  key={key}
                  className="flex justify-between py-1 border-b border-[#2a3050]/40 last:border-0"
                >
                  <span className="font-mono text-[11px] text-[#6b7280]">{label}</span>
                  <span
                    className={`font-mono text-[11px] ${
                      isWinner ? "text-[#f5a623] font-bold" : "text-[#c8d0e0]"
                    }`}
                  >
                    {fmt(build[key] as number | null)}
                    {isWinner && " ★"}
                  </span>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Grouped bar chart */}
      <div>
        <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280] mb-2">
          Metric Comparison
        </p>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData} margin={{ top: 4, right: 16, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" />
            <XAxis
              dataKey="metric"
              tick={{ fill: "#6b7280", fontSize: 10, fontFamily: "monospace" }}
              axisLine={{ stroke: "#2a3050" }}
              tickLine={false}
              angle={-20}
              textAnchor="end"
              interval={0}
            />
            <YAxis
              tick={{ fill: "#6b7280", fontSize: 10, fontFamily: "monospace" }}
              axisLine={{ stroke: "#2a3050" }}
              tickLine={false}
              width={48}
            />
            <Tooltip
              contentStyle={{
                background: "#10152a",
                border: "1px solid #2a3050",
                fontFamily: "monospace",
                fontSize: 11,
                color: "#c8d0e0",
              }}
            />
            <Legend
              wrapperStyle={{ fontFamily: "monospace", fontSize: 11, color: "#c8d0e0" }}
            />
            <Bar dataKey={a.label} fill="#f5a623" radius={[2, 2, 0, 0]} />
            <Bar dataKey={b.label} fill="#22d3ee" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Differential section */}
      {differential && Object.keys(differential).length > 0 && (
        <div>
          <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280] mb-2">
            Delta (A − B)
          </p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {Object.entries(differential).map(([key, delta]) => (
              <div
                key={key}
                className="rounded border border-[#2a3050] bg-[#0d1124] px-3 py-2"
              >
                <p className="font-mono text-[10px] text-[#6b7280] mb-0.5">{key}</p>
                <p
                  className={`font-mono text-sm font-bold ${
                    delta > 0 ? "text-green-400" : delta < 0 ? "text-red-400" : "text-[#c8d0e0]"
                  }`}
                >
                  {delta > 0 ? "+" : ""}
                  {delta.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
