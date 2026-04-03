/**
 * N11 — Timeline Panel
 *
 * Renders a Recharts LineChart bucketing TimelineEvents into ticks,
 * drawing separate lines for damage (amber), buff (cyan), and movement (gray).
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

export interface TimelineEvent {
  time: number;
  event_type: string;
  source: string;
  value: number;
}

export interface TimelinePanelProps {
  events: TimelineEvent[];
  duration: number;
  tickSize?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildTicks(
  events: TimelineEvent[],
  duration: number,
  tickSize: number
): { time: number; damage: number; buff: number; movement: number }[] {
  const numBuckets = Math.max(1, Math.ceil(duration / tickSize));
  const buckets = Array.from({ length: numBuckets }, (_, i) => ({
    time: parseFloat((i * tickSize).toFixed(4)),
    damage: 0,
    buff: 0,
    movement: 0,
  }));

  for (const ev of events) {
    const idx = Math.min(
      Math.floor(ev.time / tickSize),
      numBuckets - 1
    );
    const type = ev.event_type.toLowerCase();
    if (type === "damage") {
      buckets[idx].damage += ev.value;
    } else if (type === "buff") {
      buckets[idx].buff += ev.value;
    } else if (type === "movement") {
      buckets[idx].movement += ev.value;
    }
  }

  return buckets;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function TimelinePanel({
  events,
  duration,
  tickSize = 0.5,
}: TimelinePanelProps) {
  const data = buildTicks(events, duration, tickSize);

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280] mb-3">
        Timeline
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" />
          <XAxis
            dataKey="time"
            tickFormatter={(v: number) => `${v.toFixed(1)}s`}
            tick={{ fill: "#6b7280", fontSize: 11, fontFamily: "monospace" }}
            axisLine={{ stroke: "#2a3050" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 11, fontFamily: "monospace" }}
            axisLine={{ stroke: "#2a3050" }}
            tickLine={false}
            width={48}
          />
          <Tooltip
            contentStyle={{
              background: "#10152a",
              border: "1px solid #2a3050",
              fontFamily: "monospace",
              fontSize: 12,
              color: "#c8d0e0",
            }}
            labelFormatter={(v) => `t = ${Number(v).toFixed(2)}s`}
          />
          <Legend
            wrapperStyle={{ fontFamily: "monospace", fontSize: 12, color: "#c8d0e0", paddingTop: 8 }}
          />
          <Line
            type="monotone"
            dataKey="damage"
            stroke="#f5a623"
            dot={false}
            strokeWidth={1.5}
            name="Damage"
          />
          <Line
            type="monotone"
            dataKey="buff"
            stroke="#22d3ee"
            dot={false}
            strokeWidth={1.5}
            name="Buff"
          />
          <Line
            type="monotone"
            dataKey="movement"
            stroke="#6b7280"
            dot={false}
            strokeWidth={1.5}
            name="Movement"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
