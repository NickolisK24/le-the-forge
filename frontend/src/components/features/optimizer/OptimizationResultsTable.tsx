/**
 * F12 — Optimization Results Table
 *
 * Renders a ranked table of optimization results.
 * Columns: Rank, Score, DPS, Total Damage, Mutations Applied.
 */

import type { OptimizationResultItem } from "@/services/optimizerApi";

interface Props {
  results:       OptimizationResultItem[];
  metric:        string;
  selectedRank:  number | null;
  onSelectRank:  (rank: number) => void;
}

export default function OptimizationResultsTable({
  results,
  metric,
  selectedRank,
  onSelectRank,
}: Props) {
  if (results.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-forge-muted">
        No results — all variants failed simulation or were filtered by constraints.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-forge-border text-xs uppercase tracking-wide text-forge-muted">
            <th className="px-3 py-2 text-left">Rank</th>
            <th className="px-3 py-2 text-right">Score ({metric})</th>
            <th className="px-3 py-2 text-right">DPS</th>
            <th className="px-3 py-2 text-right">Total Dmg</th>
            <th className="px-3 py-2 text-left">Mutations</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => {
            const isSelected = r.rank === selectedRank;
            return (
              <tr
                key={r.rank}
                role="button"
                tabIndex={0}
                aria-selected={isSelected}
                onClick={() => onSelectRank(r.rank)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelectRank(r.rank);
                  }
                }}
                className={`
                  cursor-pointer border-b border-forge-border/50 transition-colors
                  hover:bg-forge-border/20 focus:outline-none focus:ring-1 focus:ring-forge-accent/50
                  ${isSelected ? "bg-forge-accent/10 ring-1 ring-inset ring-forge-accent/30" : ""}
                `}
              >
                <td className="px-3 py-2 font-mono font-semibold text-forge-accent">
                  #{r.rank}
                </td>
                <td className="px-3 py-2 text-right font-mono text-forge-text">
                  {r.score.toFixed(2)}
                </td>
                <td className="px-3 py-2 text-right font-mono text-forge-text">
                  {r.simulation_output.dps.toFixed(1)}
                </td>
                <td className="px-3 py-2 text-right font-mono text-forge-text">
                  {r.simulation_output.total_damage.toFixed(0)}
                </td>
                <td className="px-3 py-2 text-forge-muted">
                  {r.mutations_applied.length === 0 ? (
                    <span className="italic">base build</span>
                  ) : (
                    <span title={r.mutations_applied.join("\n")}>
                      {r.mutations_applied[0]}
                      {r.mutations_applied.length > 1 && (
                        <span className="ml-1 text-xs opacity-60">
                          +{r.mutations_applied.length - 1} more
                        </span>
                      )}
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
