/**
 * PassiveStatsDebugPanel — development display of raw and resolved passive stats.
 *
 * Two sections:
 *   RAW STATS    — flat + percent from aggregation (computePassiveStats output)
 *   RESOLVED STATS — final values after percent scaling + derived stats
 */

import type { AggregatedStat } from "@/types/passiveEffects";
import type { StatPool } from "@/logic/statResolutionPipeline";
import { formatStat, sortedStats } from "@/logic/computePassiveStats";

interface Props {
  stats: Map<string, AggregatedStat>;
  resolvedStats: StatPool;
  totalPoints: number;
  allocatedCount: number;
}

export default function PassiveStatsDebugPanel({ stats, resolvedStats, totalPoints, allocatedCount }: Props) {
  const rawSorted = sortedStats(stats);
  const resolvedEntries = Array.from(resolvedStats.entries())
    .filter(([, v]) => v !== 0)
    .sort(([a], [b]) => a.localeCompare(b));

  if (rawSorted.length === 0) {
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

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Passive Stats
        </span>
        <span className="font-mono text-[10px] text-forge-dim">
          {allocatedCount} nodes · {totalPoints} points · {rawSorted.length} raw · {resolvedEntries.length} resolved
        </span>
      </div>

      {/* RAW STATS */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1.5">
          Raw Stats <span className="text-forge-dim/50">(flat + percent)</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-1">
          {rawSorted.map((stat) => (
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
      </div>

      {/* RESOLVED STATS */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-amber mb-1.5">
          Resolved Stats <span className="text-forge-dim/50">(after scaling + derived)</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-1">
          {resolvedEntries.map(([statId, value]) => {
            const isDerived = statId.startsWith("Derived ");
            const displayName = isDerived ? statId.replace("Derived ", "") : statId;
            const rounded = Math.round(value * 100) / 100;
            return (
              <div key={statId} className="flex justify-between gap-2 font-mono text-xs">
                <span className={isDerived ? "text-forge-amber/70 truncate" : "text-forge-muted truncate"}>
                  {displayName}
                  {isDerived && <span className="text-forge-dim/50"> (d)</span>}
                </span>
                <span className="text-forge-text font-semibold whitespace-nowrap">
                  {rounded > 0 ? `+${rounded}` : rounded}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary */}
      <div className="pt-2 border-t border-forge-border flex gap-6 font-mono text-[10px] text-forge-dim">
        <span>Raw: {rawSorted.length}</span>
        <span>Resolved: {resolvedEntries.length}</span>
        <span>Derived: {resolvedEntries.filter(([k]) => k.startsWith("Derived ")).length}</span>
      </div>
    </div>
  );
}
