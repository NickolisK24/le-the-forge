/**
 * I16 — Multi-Target Chart
 *
 * Visualises cumulative damage per target over fight time using Recharts.
 * Each target gets its own coloured line. Down-samples to 300 points max.
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
import type { DamageEvent } from "@/lib/api";

interface Props {
  events: DamageEvent[];
}

const PALETTE = [
  "#f0a020", "#60c0e0", "#a080e0", "#60e0a0",
  "#e06080", "#e0c060", "#80e060", "#c060e0",
];

function buildChartData(
  events: DamageEvent[],
  targetIds: string[],
): { t: number; [key: string]: number }[] {
  if (events.length === 0) return [];

  // Accumulate cumulative damage per target at each unique time point
  const cumulative: Record<string, number> = Object.fromEntries(targetIds.map(id => [id, 0]));
  const rows: { t: number; [key: string]: number }[] = [];

  let i = 0;
  while (i < events.length) {
    const t = events[i].time;
    // Process all events at the same timestamp
    while (i < events.length && events[i].time === t) {
      const ev = events[i];
      cumulative[ev.target_id] = (cumulative[ev.target_id] ?? 0) + ev.damage;
      i++;
    }
    rows.push({ t, ...cumulative });
  }

  // Down-sample if too many points
  const MAX = 300;
  if (rows.length <= MAX) return rows;
  const step = Math.ceil(rows.length / MAX);
  return rows.filter((_, idx) => idx % step === 0 || idx === rows.length - 1);
}

export default function MultiTargetChart({ events }: Props) {
  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-forge-muted text-sm rounded border border-forge-border">
        No data
      </div>
    );
  }

  const targetIds = Array.from(new Set(events.map(e => e.target_id)));
  const data = buildChartData(events, targetIds);

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Cumulative Damage per Target
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" />
          <XAxis
            dataKey="t"
            tickFormatter={(v: number) => `${v.toFixed(1)}s`}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 11 }}
          />
          <YAxis
            tickFormatter={(v: number) =>
              v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M`
              : v >= 1000 ? `${(v / 1000).toFixed(0)}k`
              : String(v)
            }
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 11 }}
            width={52}
          />
          <Tooltip
            contentStyle={{
              background: "#10152a",
              border: "1px solid #2a3050",
              fontSize: 12,
              color: "#c8d0e0",
            }}
            labelFormatter={(t: number) => `t = ${t.toFixed(2)}s`}
            formatter={(v: number, name: string) => [v.toLocaleString(), name]}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: "#8090b0" }}
          />
          {targetIds.map((id, i) => (
            <Line
              key={id}
              type="monotone"
              dataKey={id}
              stroke={PALETTE[i % PALETTE.length]}
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
