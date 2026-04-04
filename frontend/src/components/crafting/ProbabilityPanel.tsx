/**
 * P25 — ProbabilityPanel
 *
 * Displays a 2×3 grid of stat cards derived from CraftOptimizationResult.
 * Colour-codes key metrics (success probability, score) by threshold.
 */

import type { CraftOptimizationResult } from "@/pages/crafting/CraftingPage";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function pct(v: number, decimals = 1) {
  return `${(v * 100).toFixed(decimals)}%`;
}

function successColor(v: number): string {
  if (v >= 0.7) return "text-green-400";
  if (v >= 0.5) return "text-yellow-400";
  return "text-red-400";
}

function scoreColor(v: number): string {
  if (v >= 0.8) return "text-green-400";
  if (v >= 0.6) return "text-yellow-400";
  return "text-red-400";
}

// ---------------------------------------------------------------------------
// Sub-component
// ---------------------------------------------------------------------------

function StatCard({
  label,
  value,
  colorClass = "text-gray-100",
}: {
  label: string;
  value: string;
  colorClass?: string;
}) {
  return (
    <div className="rounded-md border border-[#2a3050] bg-[#0d1123] p-3 flex flex-col gap-1">
      <p className="text-[10px] uppercase tracking-wider text-gray-500">{label}</p>
      <p className={`text-base font-bold font-mono ${colorClass}`}>{value}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  result: CraftOptimizationResult | null;
}

export default function ProbabilityPanel({ result }: Props) {
  if (!result) {
    return (
      <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider mb-3">
          Simulation Results
        </h2>
        <p className="text-xs text-gray-500 text-center py-6">
          Run simulation to see results.
        </p>
      </div>
    );
  }

  const ciLow  = pct(result.confidence_interval[0]);
  const ciHigh = pct(result.confidence_interval[1]);

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
      <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider">
        Simulation Results
      </h2>

      <div className="grid grid-cols-2 gap-2">
        <StatCard
          label="Success Probability"
          value={pct(result.success_probability)}
          colorClass={successColor(result.success_probability)}
        />
        <StatCard
          label="Score"
          value={result.score.toFixed(2)}
          colorClass={scoreColor(result.score)}
        />
        <StatCard
          label="Mean FP Cost"
          value={result.mean_fp_cost.toFixed(1)}
        />
        <StatCard
          label="Fracture Rate"
          value={pct(result.fracture_rate)}
          colorClass="text-orange-400"
        />
        <StatCard
          label="95% Confidence Interval"
          value={`${ciLow} – ${ciHigh}`}
          colorClass="text-[#22d3ee]"
        />
        <StatCard
          label="Steps"
          value={String(result.steps)}
          colorClass="text-gray-100"
        />
      </div>
    </div>
  );
}
