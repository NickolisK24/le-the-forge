/**
 * D9 — Damage Timeline Chart
 *
 * Visualises damage_per_tick over fight time using Recharts.
 * Downsamples to at most 500 points to keep rendering fast.
 */

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Props {
  data: number[];
  tickSize: number;
}

const MAX_POINTS = 500;

function downsample(values: number[], maxPoints: number): { t: number; dmg: number }[] {
  if (values.length === 0) return [];
  const step = Math.max(1, Math.floor(values.length / maxPoints));
  const out: { t: number; dmg: number }[] = [];
  for (let i = 0; i < values.length; i += step) {
    const chunk = values.slice(i, i + step);
    const avg = chunk.reduce((a, b) => a + b, 0) / chunk.length;
    out.push({ t: i, dmg: Math.round(avg) });
  }
  return out;
}

export default function DamageChart({ data, tickSize }: Props) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-forge-muted text-sm rounded border border-forge-border">
        No data
      </div>
    );
  }

  const points = downsample(data, MAX_POINTS);

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Damage Timeline
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={points} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="dmgGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f0a020" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#f0a020" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" />
          <XAxis
            dataKey="t"
            tickFormatter={(v) => `${(v * tickSize).toFixed(0)}s`}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 11 }}
          />
          <YAxis
            tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v))}
            stroke="#5a6580"
            tick={{ fill: "#8090b0", fontSize: 11 }}
            width={48}
          />
          <Tooltip
            contentStyle={{
              background: "#10152a",
              border: "1px solid #2a3050",
              fontSize: 12,
              color: "#c8d0e0",
            }}
            formatter={(v: number) => [v.toLocaleString(), "Damage"]}
            labelFormatter={(t: number) => `t = ${(t * tickSize).toFixed(2)}s`}
          />
          <Area
            type="monotone"
            dataKey="dmg"
            stroke="#f0a020"
            strokeWidth={1.5}
            fill="url(#dmgGrad)"
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </section>
  );
}
