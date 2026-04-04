/**
 * Q27 — ComparisonViewer
 *
 * Shows the selected BIS result vs the average of all results
 * using a side-by-side Recharts BarChart.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { BisSearchResult } from "@/pages/bis/BisSearchPage";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  selected: BisSearchResult | null;
  allResults: BisSearchResult[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ComparisonViewer({ selected, allResults }: Props) {
  if (!selected) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-forge-border bg-forge-surface p-6 h-[240px]">
        <p className="text-sm text-forge-muted">Select a result to compare</p>
      </div>
    );
  }

  const avg =
    allResults.length > 0
      ? allResults.reduce((sum, r) => sum + r.score, 0) / allResults.length
      : 0;

  const topPercent = Math.max(1, Math.round((1 - selected.percentile / 100) * 100));

  const chartData = [
    {
      name: "Score",
      Selected: +(selected.score * 100).toFixed(2),
      Average:  +(avg          * 100).toFixed(2),
    },
  ];

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-4">
      {/* Header row */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Comparison
        </h2>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-[#1a2040] px-2 py-0.5 text-xs font-medium text-[#22d3ee]">
            Top {topPercent}%
          </span>
        </div>
      </div>

      {/* Selected result summary */}
      <div className="mb-4 grid grid-cols-3 gap-3 text-xs">
        <div className="rounded bg-[#1a2040] px-3 py-2">
          <p className="text-forge-muted mb-0.5">Rank</p>
          <p className="font-semibold text-forge-text">#{selected.rank}</p>
        </div>
        <div className="rounded bg-[#1a2040] px-3 py-2">
          <p className="text-forge-muted mb-0.5">Score</p>
          <p className="font-semibold text-[#f5a623]">{(selected.score * 100).toFixed(1)}%</p>
        </div>
        <div className="rounded bg-[#1a2040] px-3 py-2 col-span-1 overflow-hidden">
          <p className="text-forge-muted mb-0.5">Build ID</p>
          <p className="font-mono text-[#22d3ee] truncate text-[10px]">{selected.build_id}</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={150}>
        <BarChart data={chartData} barCategoryGap="40%">
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: "#6b7280", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `${v}%`}
          />
          <Tooltip
            contentStyle={{ background: "#10152a", border: "1px solid #2a3050", borderRadius: 6 }}
            labelStyle={{ color: "#c8d0e0", fontSize: 12 }}
            formatter={(v: number) => [`${v.toFixed(1)}%`]}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "#9ca3af" }} />
          <Bar dataKey="Selected" fill="#f5a623" radius={[3, 3, 0, 0]} />
          <Bar dataKey="Average"  fill="#22d3ee" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
