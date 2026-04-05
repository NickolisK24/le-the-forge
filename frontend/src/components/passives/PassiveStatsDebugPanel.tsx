/**
 * PassiveStatsDebugPanel — development-only display of computed passive stats.
 *
 * Shows all aggregated stat bonuses from allocated passive nodes.
 * Renders below the passive tree canvas.
 */

import type { AggregatedStat } from "@/types/passiveEffects";
import { formatStat, sortedStats } from "@/logic/computePassiveStats";

interface Props {
  stats: Map<string, AggregatedStat>;
  totalPoints: number;
  allocatedCount: number;
}

export default function PassiveStatsDebugPanel({ stats, totalPoints, allocatedCount }: Props) {
  const sorted = sortedStats(stats);

  if (sorted.length === 0) {
    return (
      <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-2">
          Passive Stats
        </div>
        <p className="font-mono text-xs text-forge-dim">
          No stats allocated. Click nodes to see computed bonuses.
        </p>
      </div>
    );
  }

  // Split into flat-only, percent-only, and mixed
  const flatStats = sorted.filter((s) => s.flat !== 0 && s.percent === 0);
  const percentStats = sorted.filter((s) => s.flat === 0 && s.percent !== 0);
  const mixedStats = sorted.filter((s) => s.flat !== 0 && s.percent !== 0);

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Passive Stats
        </span>
        <span className="font-mono text-[10px] text-forge-dim">
          {allocatedCount} nodes · {totalPoints} points · {sorted.length} stats
        </span>
      </div>

      {/* Stat grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-1">
        {sorted.map((stat) => (
          <div key={stat.statId} className="flex justify-between gap-2 font-mono text-xs">
            <span className="text-forge-muted truncate">{stat.statId}</span>
            <span className={
              stat.flat > 0 || stat.percent > 0
                ? "text-forge-cyan font-semibold whitespace-nowrap"
                : "text-red-400 font-semibold whitespace-nowrap"
            }>
              {formatStat(stat)}
            </span>
          </div>
        ))}
      </div>

      {/* Summary row */}
      <div className="mt-3 pt-2 border-t border-forge-border flex gap-6 font-mono text-[10px] text-forge-dim">
        <span>Flat stats: {flatStats.length}</span>
        <span>Percent stats: {percentStats.length}</span>
        {mixedStats.length > 0 && <span>Mixed: {mixedStats.length}</span>}
      </div>
    </div>
  );
}
