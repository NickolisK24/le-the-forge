/**
 * L22 — Distance Timeline View
 *
 * Recharts line chart that shows how the distance between tracked entity
 * pairs changes over simulation time. Renders a horizontal threshold line
 * (if provided) to visualise safe/danger zones.
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DistanceSample {
  time: number;
  [pairKey: string]: number; // "entityA:entityB" → distance
}

export interface DistanceTimelineProps {
  /** Array of time-sampled distance data points */
  data?: DistanceSample[];
  /** Pair keys to display */
  pairs?: string[];
  /** Danger threshold (enemy min-range) rendered as a red dashed line */
  dangerThreshold?: number;
  /** Safe threshold (enemy max-range) rendered as a green dashed line */
  safeThreshold?: number;
  /** Chart title */
  title?: string;
  height?: number;
}

const PAIR_COLORS = [
  "#f0a020",
  "#00d4f5",
  "#3dca74",
  "#b87fff",
  "#ff5050",
  "#ffb83f",
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DistanceTimeline({
  data = [],
  pairs = [],
  dangerThreshold,
  safeThreshold,
  title = "Distance Over Time",
  height = 280,
}: DistanceTimelineProps) {
  if (data.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-forge-border bg-forge-surface text-forge-muted text-sm font-mono"
        style={{ height }}
      >
        No distance data
      </div>
    );
  }

  const displayPairs = pairs.length > 0 ? pairs : Object.keys(data[0]).filter((k) => k !== "time");

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-3 flex flex-col gap-2">
      {title && (
        <h3 className="text-sm font-display text-forge-amber tracking-wide">{title}</h3>
      )}

      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 6, right: 24, bottom: 4, left: 0 }}>
          <CartesianGrid stroke="rgba(80,100,210,0.12)" strokeDasharray="3 3" />

          <XAxis
            dataKey="time"
            tickFormatter={(v: number) => `${v.toFixed(1)}s`}
            tick={{ fill: "#8890b8", fontSize: 10, fontFamily: "JetBrains Mono, monospace" }}
            label={{ value: "Time (s)", position: "insideBottom", offset: -2, fill: "#4a5480", fontSize: 10 }}
          />

          <YAxis
            tick={{ fill: "#8890b8", fontSize: 10, fontFamily: "JetBrains Mono, monospace" }}
            label={{ value: "Distance (u)", angle: -90, position: "insideLeft", fill: "#4a5480", fontSize: 10 }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0c0f1c",
              border: "1px solid rgba(80,100,210,0.3)",
              borderRadius: "6px",
              fontSize: "11px",
              fontFamily: "JetBrains Mono, monospace",
              color: "#eceef8",
            }}
            formatter={(value: number) => [`${value.toFixed(2)} u`]}
          />

          <Legend
            wrapperStyle={{ fontSize: "10px", fontFamily: "JetBrains Mono, monospace", color: "#8890b8" }}
          />

          {/* Danger threshold */}
          {dangerThreshold !== undefined && (
            <ReferenceLine
              y={dangerThreshold}
              stroke="#ff5050"
              strokeDasharray="4 3"
              label={{ value: "min range", fill: "#ff5050", fontSize: 9 }}
            />
          )}

          {/* Safe threshold */}
          {safeThreshold !== undefined && (
            <ReferenceLine
              y={safeThreshold}
              stroke="#3dca74"
              strokeDasharray="4 3"
              label={{ value: "max range", fill: "#3dca74", fontSize: 9 }}
            />
          )}

          {displayPairs.map((pair, idx) => (
            <Line
              key={pair}
              type="monotone"
              dataKey={pair}
              stroke={PAIR_COLORS[idx % PAIR_COLORS.length]}
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3 }}
              name={pair}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
