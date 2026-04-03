/**
 * M17 — Confidence Interval Chart
 *
 * Shows convergence of the confidence interval as n_runs grows.
 * Three lines: mean (amber solid), lower bound (cyan dashed), upper bound (cyan dashed).
 */

import {
  LineChart,
  Line,
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

interface ConvergencePoint {
  n_runs: number;
  mean: number;
  lower: number;
  upper: number;
}

interface Props {
  intervals: ConvergencePoint[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtDmg(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}k`;
  return String(Math.round(v));
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ConfidenceIntervalChart({ intervals }: Props) {
  if (!intervals || intervals.length === 0) {
    return (
      <div className="flex items-center justify-center h-[280px] text-forge-dim font-mono text-sm rounded border border-forge-border">
        No convergence data
      </div>
    );
  }

  return (
    <div className="bg-[#10152a] rounded border border-forge-border p-4">
      <h3 className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70 mb-3">
        CI Convergence
      </h3>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart
          data={intervals}
          margin={{ top: 8, right: 16, left: 0, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" />
          <XAxis
            dataKey="n_runs"
            tickFormatter={(v: number) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v)}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 10 }}
            label={{
              value: "Runs",
              position: "insideBottom",
              offset: -4,
              fill: "#5a6580",
              fontSize: 10,
            }}
          />
          <YAxis
            tickFormatter={fmtDmg}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 10 }}
            width={52}
          />
          <Tooltip
            contentStyle={{
              background: "#10152a",
              border: "1px solid #2a3050",
              fontSize: 12,
              color: "#c8d0e0",
            }}
            labelFormatter={(v: number) => `n = ${v.toLocaleString()}`}
            formatter={(value: number, name: string) => [fmtDmg(value), name]}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, color: "#8090b0" }}
          />

          {/* Mean — amber solid */}
          <Line
            type="monotone"
            dataKey="mean"
            name="Mean"
            stroke="#f5a623"
            strokeWidth={2}
            dot={{ r: 3, fill: "#f5a623" }}
            isAnimationActive={false}
          />
          {/* Lower bound — cyan dashed */}
          <Line
            type="monotone"
            dataKey="lower"
            name="Lower (95% CI)"
            stroke="#60c0e0"
            strokeWidth={1.5}
            strokeDasharray="5 3"
            dot={{ r: 2, fill: "#60c0e0" }}
            isAnimationActive={false}
          />
          {/* Upper bound — cyan dashed */}
          <Line
            type="monotone"
            dataKey="upper"
            name="Upper (95% CI)"
            stroke="#60c0e0"
            strokeWidth={1.5}
            strokeDasharray="5 3"
            dot={{ r: 2, fill: "#60c0e0" }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
