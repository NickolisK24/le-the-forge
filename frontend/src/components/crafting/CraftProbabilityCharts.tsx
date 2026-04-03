/**
 * UI10 — Craft Probability Charts
 *
 * Success/failure distribution charts using recharts:
 *   Left  — Pie chart (success vs failure)
 *   Right — Bar chart (FP cost distribution)
 */

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CraftProbabilityChartsProps {
  successRate?: number; // 0-1
  distributionData?: Array<{ attempt: number; success: boolean; fpUsed: number }>;
}

// ---------------------------------------------------------------------------
// Colors from forge theme (CSS vars not available in recharts, use hex)
// ---------------------------------------------------------------------------

const COLOR_GREEN  = "#4ade80"; // forge-green
const COLOR_RED    = "#ef4444"; // forge-red
const COLOR_AMBER  = "#f5a623"; // forge-amber
const COLOR_BORDER = "#2a3050"; // forge-border
const COLOR_DIM    = "#5a6580"; // forge-dim
const COLOR_MUTED  = "#8090b0"; // forge-muted

// ---------------------------------------------------------------------------
// FP bucket builder
// ---------------------------------------------------------------------------

function buildFpBuckets(
  data: Array<{ fpUsed: number }>
): Array<{ bucket: string; count: number }> {
  if (data.length === 0) {
    // Placeholder empty buckets
    return [
      { bucket: "0-20",   count: 0 },
      { bucket: "21-40",  count: 0 },
      { bucket: "41-60",  count: 0 },
      { bucket: "61-80",  count: 0 },
      { bucket: "81-100", count: 0 },
    ];
  }

  const bucketSize = 20;
  const max = Math.max(...data.map((d) => d.fpUsed));
  const numBuckets = Math.max(5, Math.ceil(max / bucketSize));
  const buckets: Record<string, number> = {};

  for (let i = 0; i < numBuckets; i++) {
    const lo = i * bucketSize + 1;
    const hi = (i + 1) * bucketSize;
    const label = i === 0 ? `0-${hi}` : `${lo}-${hi}`;
    buckets[label] = 0;
  }

  for (const d of data) {
    const idx = Math.floor(d.fpUsed / bucketSize);
    const lo = idx * bucketSize + 1;
    const hi = (idx + 1) * bucketSize;
    const label = idx === 0 ? `0-${hi}` : `${lo}-${hi}`;
    if (buckets[label] !== undefined) buckets[label]++;
    else buckets[label] = 1;
  }

  return Object.entries(buckets).map(([bucket, count]) => ({ bucket, count }));
}

// ---------------------------------------------------------------------------
// Custom tooltip
// ---------------------------------------------------------------------------

const tooltipStyle = {
  background: "#10152a",
  border: `1px solid ${COLOR_BORDER}`,
  fontSize: 12,
  color: "#c8d0e0",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CraftProbabilityCharts({
  successRate,
  distributionData = [],
}: CraftProbabilityChartsProps) {
  const rate = successRate ?? 0;
  const successPct = Math.round(rate * 100);
  const failurePct = 100 - successPct;

  const pieData = [
    { name: "Success", value: successPct || 0 },
    { name: "Failure", value: failurePct || 100 },
  ];

  const fpBuckets = buildFpBuckets(distributionData);

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      {/* Pie chart: success vs failure */}
      <div className="rounded border border-forge-border bg-forge-surface2 p-4">
        <div className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70 mb-3">
          Success vs Failure
        </div>

        <ResponsiveContainer width="100%" height={180}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={45}
              outerRadius={70}
              dataKey="value"
              strokeWidth={0}
            >
              <Cell fill={COLOR_GREEN} />
              <Cell fill={COLOR_RED} />
            </Pie>
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(v: number, name: string) => [`${v}%`, name]}
            />
          </PieChart>
        </ResponsiveContainer>

        <div className="flex items-center justify-center gap-4 mt-2">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ background: COLOR_GREEN }} />
            <span className="font-mono text-xs text-forge-muted">
              Success {successPct}%
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ background: COLOR_RED }} />
            <span className="font-mono text-xs text-forge-muted">
              Failure {failurePct}%
            </span>
          </div>
        </div>
      </div>

      {/* Bar chart: FP cost distribution */}
      <div className="rounded border border-forge-border bg-forge-surface2 p-4">
        <div className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70 mb-3">
          FP Cost Distribution
        </div>

        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={fpBuckets} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="bucket"
              stroke={COLOR_DIM}
              tick={{ fill: COLOR_MUTED, fontSize: 10 }}
            />
            <YAxis
              stroke={COLOR_DIM}
              tick={{ fill: COLOR_MUTED, fontSize: 10 }}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(v: number) => [v, "Attempts"]}
            />
            <Bar dataKey="count" fill={COLOR_AMBER} radius={[2, 2, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default CraftProbabilityCharts;
