import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from "recharts";
import { analysisApi } from "@/lib/api";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import type { CorruptionAnalysisResponse } from "@/types";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface CorruptionScalingPanelProps {
  slug: string;
  bossId?: string;
}

// ---------------------------------------------------------------------------
// Color tokens
// ---------------------------------------------------------------------------

const C = {
  amber:  "#f0a020",
  cyan:   "#22d3ee",
  green:  "#4ade80",
  red:    "#f87171",
  muted:  "#6b7280",
  surface:"#1a1a2e",
  border: "rgba(255,255,255,0.08)",
  text:   "#e5e7eb",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CorruptionScalingPanel({
  slug,
  bossId,
}: CorruptionScalingPanelProps) {
  const query = useQuery({
    queryKey: ["analysis", "corruption", slug, bossId],
    queryFn: async () => {
      const res = await analysisApi.corruption(slug, bossId);
      return res.data;
    },
    enabled: Boolean(slug),
  });

  const result: CorruptionAnalysisResponse | null | undefined = query.data;

  return (
    <Panel title="Corruption Scaling">
      {/* Loading */}
      {query.isLoading && (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      )}

      {/* Error */}
      {query.error && (
        <ErrorMessage
          message="Failed to load corruption analysis"
          onRetry={() => query.refetch()}
        />
      )}

      {/* Chart */}
      {result && result.curve.length > 0 && (
        <div className="space-y-4">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart
              data={result.curve}
              margin={{ top: 8, right: 16, bottom: 4, left: -8 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={C.border}
                vertical={false}
              />
              <XAxis
                dataKey="corruption"
                tick={{ fill: C.muted, fontSize: 10, fontFamily: "monospace" }}
                axisLine={false}
                tickLine={false}
                label={{
                  value: "Corruption",
                  position: "insideBottomRight",
                  offset: -4,
                  fill: C.muted,
                  fontSize: 10,
                }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: C.muted, fontSize: 10, fontFamily: "monospace" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => `${v}`}
              />
              <Tooltip
                contentStyle={{
                  background: C.surface,
                  border: `1px solid ${C.border}`,
                  borderRadius: 4,
                  fontSize: 11,
                }}
                labelStyle={{ color: C.text }}
                formatter={(value: number, name: string) => {
                  if (name === "dps_efficiency")
                    return [`${(value * 100).toFixed(0)}%`, "DPS Efficiency"];
                  return [`${value}`, "Survivability"];
                }}
                labelFormatter={(label: number) => `Corruption ${label}`}
              />
              <Legend
                wrapperStyle={{
                  fontSize: 10,
                  fontFamily: "monospace",
                  color: C.muted,
                }}
              />
              <ReferenceLine
                x={result.recommended_max_corruption}
                stroke={C.green}
                strokeDasharray="4 2"
                label={{
                  value: `Max: ${result.recommended_max_corruption}`,
                  fill: C.green,
                  fontSize: 10,
                  position: "top",
                }}
              />
              <Line
                type="monotone"
                dataKey="dps_efficiency"
                name="DPS Efficiency"
                stroke={C.amber}
                strokeWidth={2}
                dot={{ fill: C.amber, r: 3 }}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="survivability_score"
                name="Survivability"
                stroke={C.cyan}
                strokeWidth={2}
                dot={{ fill: C.cyan, r: 3 }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>

          {/* Summary card */}
          <div className="rounded bg-white/[0.02] border border-white/5 px-4 py-3">
            <div className="text-sm font-medium" style={{ color: C.green }}>
              Recommended Max Corruption:{" "}
              {result.recommended_max_corruption}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Highest corruption where survivability stays above 70/100.
              Beyond this level, the build becomes increasingly fragile.
            </div>
          </div>
        </div>
      )}

      {/* Empty */}
      {!query.isLoading && !query.error && !result && (
        <div className="py-8 text-center text-sm text-gray-500">
          No corruption data available
        </div>
      )}
    </Panel>
  );
}
