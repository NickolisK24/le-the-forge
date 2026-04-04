/**
 * F13 — Variant Comparison Panel
 *
 * Side-by-side comparison of two optimization results.
 * Left = base build (#1 rank by default), Right = selected rank.
 */

import type { OptimizationResultItem } from "@/services/optimizerApi";

interface StatRowProps {
  label: string;
  left:  string | number;
  right: string | number;
}

function StatRow({ label, left, right }: StatRowProps) {
  const leftNum  = typeof left  === "number" ? left  : parseFloat(String(left));
  const rightNum = typeof right === "number" ? right : parseFloat(String(right));
  const diff = !isNaN(leftNum) && !isNaN(rightNum) ? rightNum - leftNum : null;

  return (
    <tr className="border-b border-forge-border/30 text-sm">
      <td className="py-1.5 pr-4 text-forge-muted">{label}</td>
      <td className="py-1.5 pr-4 text-right font-mono text-forge-text">
        {typeof left === "number" ? left.toFixed(2) : left}
      </td>
      <td className="py-1.5 text-right font-mono text-forge-text">
        {typeof right === "number" ? right.toFixed(2) : right}
      </td>
      <td className="py-1.5 pl-4 text-right font-mono text-xs">
        {diff !== null && diff !== 0 && (
          <span className={diff > 0 ? "text-green-400" : "text-red-400"}>
            {diff > 0 ? "+" : ""}{diff.toFixed(2)}
          </span>
        )}
      </td>
    </tr>
  );
}

interface Props {
  base:     OptimizationResultItem;
  compared: OptimizationResultItem;
}

export default function VariantComparisonPanel({ base, compared }: Props) {
  const bSim = base.simulation_output;
  const cSim = compared.simulation_output;

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-forge-accent uppercase tracking-wider">
          Variant Comparison
        </h3>
        <div className="flex gap-6 text-xs text-forge-muted">
          <span className="font-semibold text-forge-text">#{base.rank} (Best)</span>
          <span className="font-semibold text-forge-text">#{compared.rank} (Selected)</span>
          <span className="w-16 text-right">Δ</span>
        </div>
      </div>

      <table className="w-full">
        <thead>
          <tr className="text-xs uppercase tracking-wide text-forge-muted">
            <th className="py-1 pr-4 text-left">Stat</th>
            <th className="py-1 pr-4 text-right">#{base.rank}</th>
            <th className="py-1 text-right">#{compared.rank}</th>
            <th className="py-1 pl-4 text-right">Δ</th>
          </tr>
        </thead>
        <tbody>
          <StatRow label="Score"        left={base.score}           right={compared.score} />
          <StatRow label="DPS"          left={bSim.dps}             right={cSim.dps} />
          <StatRow label="Total Damage" left={bSim.total_damage}    right={cSim.total_damage} />
          <StatRow label="Elapsed (s)"  left={bSim.elapsed_time}    right={cSim.elapsed_time} />
          <StatRow label="Ticks"        left={bSim.ticks_simulated} right={cSim.ticks_simulated} />
          <StatRow label="Downtime"     left={bSim.downtime_ticks}  right={cSim.downtime_ticks} />
          <StatRow
            label="Enemy Dead"
            left={bSim.all_enemies_dead ? "Yes" : "No"}
            right={cSim.all_enemies_dead ? "Yes" : "No"}
          />
        </tbody>
      </table>

      {/* Mutations summary */}
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p className="mb-1 text-xs uppercase tracking-wide text-forge-muted">
            #{base.rank} Mutations
          </p>
          {base.mutations_applied.length === 0 ? (
            <p className="text-xs italic text-forge-muted">base build</p>
          ) : (
            <ul className="space-y-0.5">
              {base.mutations_applied.map((m, i) => (
                <li key={i} className="text-xs text-forge-text">{m}</li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <p className="mb-1 text-xs uppercase tracking-wide text-forge-muted">
            #{compared.rank} Mutations
          </p>
          {compared.mutations_applied.length === 0 ? (
            <p className="text-xs italic text-forge-muted">base build</p>
          ) : (
            <ul className="space-y-0.5">
              {compared.mutations_applied.map((m, i) => (
                <li key={i} className="text-xs text-forge-text">{m}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
