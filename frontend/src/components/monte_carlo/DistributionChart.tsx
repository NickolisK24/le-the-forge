/**
 * M16 — Distribution Chart
 *
 * Renders a damage distribution histogram using Recharts BarChart.
 * Reference lines mark the mean (amber dashed) and P5/P95 (cyan dotted).
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Bin {
  bin_start: number;
  bin_end: number;
  count: number;
  frequency: number;
}

interface Props {
  distribution: Bin[];
  mean: number;
  percentile_5: number;
  percentile_95: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtDmg(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}k`;
  return String(Math.round(v));
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DistributionChart({
  distribution,
  mean,
  percentile_5,
  percentile_95,
}: Props) {
  if (!distribution || distribution.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-forge-dim font-mono text-sm rounded border border-forge-border">
        No distribution data
      </div>
    );
  }

  return (
    <div className="bg-[#10152a] rounded border border-forge-border p-4">
      <h3 className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70 mb-3">
        Damage Distribution
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={distribution}
          margin={{ top: 8, right: 16, left: 0, bottom: 8 }}
          barCategoryGap="2%"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" vertical={false} />
          <XAxis
            dataKey="bin_start"
            tickFormatter={fmtDmg}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tickFormatter={(v: number) => `${(v * 100).toFixed(1)}%`}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 10 }}
            width={48}
          />
          <Tooltip
            contentStyle={{
              background: "#10152a",
              border: "1px solid #2a3050",
              fontSize: 12,
              color: "#c8d0e0",
            }}
            formatter={(value: number, _name: string) => [
              `${(value * 100).toFixed(2)}%`,
              "Frequency",
            ]}
            labelFormatter={(v: number) => `Bin start: ${fmtDmg(v)}`}
          />

          {/* Mean — amber dashed */}
          <ReferenceLine
            x={mean}
            stroke="#f5a623"
            strokeDasharray="6 3"
            strokeWidth={2}
          />
          {/* P5 — cyan dotted */}
          <ReferenceLine
            x={percentile_5}
            stroke="#60c0e0"
            strokeDasharray="2 4"
            strokeWidth={1.5}
          />
          {/* P95 — cyan dotted */}
          <ReferenceLine
            x={percentile_95}
            stroke="#60c0e0"
            strokeDasharray="2 4"
            strokeWidth={1.5}
          />

          <Bar dataKey="frequency" isAnimationActive={false}>
            {distribution.map((_entry, idx) => (
              <Cell key={idx} fill="#f5a623" fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Manual legend */}
      <div className="flex gap-6 mt-3 justify-center font-mono text-[11px] text-forge-dim">
        <span className="flex items-center gap-1.5">
          <span style={{ display: "inline-block", width: 20, height: 2, background: "#f5a623", borderTop: "2px dashed #f5a623" }} />
          Mean
        </span>
        <span className="flex items-center gap-1.5">
          <span style={{ display: "inline-block", width: 20, height: 2, borderTop: "2px dotted #60c0e0" }} />
          P5 / P95
        </span>
        <span className="flex items-center gap-1.5">
          <span style={{ display: "inline-block", width: 12, height: 12, background: "#f5a623", opacity: 0.8 }} />
          Frequency
        </span>
      </div>
    </div>
  );
}
