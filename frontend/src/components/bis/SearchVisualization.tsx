/**
 * Q28 — SearchVisualization
 *
 * Score distribution histogram + score-vs-rank line chart.
 * Animated loading state while search is in progress.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import type { BisSearchResult } from "@/pages/bis/BisSearchPage";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  results: BisSearchResult[];
  isSearching: boolean;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BUCKETS = [
  { label: "0.4–0.5", lo: 0.4, hi: 0.5 },
  { label: "0.5–0.6", lo: 0.5, hi: 0.6 },
  { label: "0.6–0.7", lo: 0.6, hi: 0.7 },
  { label: "0.7–0.8", lo: 0.7, hi: 0.8 },
  { label: "0.8–0.9", lo: 0.8, hi: 0.9 },
  { label: "0.9–1.0", lo: 0.9, hi: 1.01 },
];

function buildHistogram(results: BisSearchResult[]) {
  return BUCKETS.map(({ label, lo, hi }) => ({
    bucket: label,
    count: results.filter((r) => r.score >= lo && r.score < hi).length,
  }));
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SearchVisualization({ results, isSearching }: Props) {
  // Loading state
  if (isSearching) {
    return (
      <div className="rounded-lg border border-forge-border bg-forge-surface p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Search Analytics
        </h2>
        <div className="flex flex-col items-center justify-center gap-3 py-10">
          <div className="flex gap-1.5">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="h-2.5 w-2.5 rounded-full bg-[#f5a623] animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
          <p className="text-sm text-forge-muted">Search in progress...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (results.length === 0) {
    return (
      <div className="rounded-lg border border-forge-border bg-forge-surface p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Search Analytics
        </h2>
        <div className="flex items-center justify-center py-10">
          <p className="text-sm text-forge-muted">Run a search to see visualization</p>
        </div>
      </div>
    );
  }

  const histogram = buildHistogram(results);
  const rankLine  = [...results]
    .sort((a, b) => a.rank - b.rank)
    .map((r) => ({ rank: r.rank, score: +(r.score * 100).toFixed(2) }));

  const tooltipStyle = {
    contentStyle: { background: "#10152a", border: "1px solid #2a3050", borderRadius: 6 },
    labelStyle:   { color: "#c8d0e0", fontSize: 12 },
  };

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-4 space-y-5">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">
        Search Analytics
      </h2>

      {/* Score distribution histogram */}
      <div>
        <p className="mb-2 text-xs text-forge-muted uppercase tracking-wide">Score Distribution</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={histogram}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" vertical={false} />
            <XAxis
              dataKey="bucket"
              tick={{ fill: "#6b7280", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: "#6b7280", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              {...tooltipStyle}
              formatter={(v: number) => [v, "Count"]}
            />
            <Bar dataKey="count" fill="#f5a623" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Score vs rank line chart */}
      <div>
        <p className="mb-2 text-xs text-forge-muted uppercase tracking-wide">Score vs Rank</p>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={rankLine}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" />
            <XAxis
              dataKey="rank"
              label={{ value: "Rank", position: "insideBottom", offset: -3, fill: "#6b7280", fontSize: 10 }}
              tick={{ fill: "#6b7280", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              tickFormatter={(v: number) => `${v}%`}
              tick={{ fill: "#6b7280", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              {...tooltipStyle}
              formatter={(v: number) => [`${v}%`, "Score"]}
              labelFormatter={(label: number) => `Rank #${label}`}
            />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#22d3ee"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#22d3ee" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
