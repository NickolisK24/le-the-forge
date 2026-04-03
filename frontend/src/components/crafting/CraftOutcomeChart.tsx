/**
 * P26 — CraftOutcomeChart
 *
 * BarChart showing a mock normal-distribution outcome spread centred on
 * result.success_probability. Uses Recharts with amber bars and a reference
 * line at the mean.
 */

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { CraftOptimizationResult } from "@/pages/crafting/CraftingPage";

// ---------------------------------------------------------------------------
// Distribution generator
// ---------------------------------------------------------------------------

const N_BARS = 20;

/** Approximate normal PDF value (unnormalised) */
function normalPdf(x: number, mu: number, sigma: number): number {
  return Math.exp(-0.5 * ((x - mu) / sigma) ** 2);
}

function buildDistribution(successProb: number) {
  const sigma = 0.12;
  const bars = Array.from({ length: N_BARS }, (_, i) => {
    const x = i / (N_BARS - 1); // 0 → 1
    const freq = normalPdf(x, successProb, sigma);
    return {
      score: x.toFixed(2),
      frequency: Math.round(freq * 100),
    };
  });
  return bars;
}

// ---------------------------------------------------------------------------
// Custom tooltip
// ---------------------------------------------------------------------------

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] px-2 py-1 text-xs text-gray-200">
      <p>Score: <span className="text-[#f5a623]">{label}</span></p>
      <p>Freq: <span className="text-[#22d3ee]">{payload[0]?.value}</span></p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  result: CraftOptimizationResult | null;
}

export default function CraftOutcomeChart({ result }: Props) {
  const data = useMemo(
    () => (result ? buildDistribution(result.success_probability) : []),
    [result?.success_probability]
  );

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
      <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider">
        Outcome Distribution
      </h2>

      {!result ? (
        <p className="text-xs text-gray-500 text-center py-10">
          Run simulation to see distribution.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3050" vertical={false} />
            <XAxis
              dataKey="score"
              tick={{ fill: "#6b7280", fontSize: 10 }}
              label={{
                value: "Outcome Score (0–1)",
                position: "insideBottom",
                offset: -2,
                fill: "#6b7280",
                fontSize: 10,
              }}
            />
            <YAxis
              tick={{ fill: "#6b7280", fontSize: 10 }}
              label={{
                value: "Frequency",
                angle: -90,
                position: "insideLeft",
                fill: "#6b7280",
                fontSize: 10,
              }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#ffffff0a" }} />
            <ReferenceLine
              x={result.success_probability.toFixed(2)}
              stroke="#22d3ee"
              strokeDasharray="4 2"
              label={{ value: "Mean", fill: "#22d3ee", fontSize: 10, position: "top" }}
            />
            <Bar dataKey="frequency" fill="#f5a623" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
