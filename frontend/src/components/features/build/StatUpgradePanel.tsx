/**
 * StatUpgradePanel — Phase 4 stat sensitivity rankings.
 *
 * Shows ranked stats by impact score with proportional bars.
 * Mode toggle switches between balanced/offense/defense weighting.
 * Uses TanStack Query with shared cache key so UpgradeCandidatesPanel
 * can reuse the same data without a second fetch.
 */

import { clsx } from "clsx";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import type { OptimizeMode, StatRankingEntry } from "@/types";

const C = {
  amber: "#f0a020",
  cyan: "#22d3ee",
  green: "#4ade80",
  muted: "#6b7280",
};

const MODE_LABELS: Record<OptimizeMode, string> = {
  balanced: "Balanced",
  offense: "Offense",
  defense: "Defense",
};

const MODE_COLORS: Record<OptimizeMode, string> = {
  balanced: "border-forge-amber text-forge-amber",
  offense: "border-forge-red text-forge-red",
  defense: "border-forge-cyan text-forge-cyan",
};

function ImpactBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.min(Math.abs(value) / max * 100, 100) : 0;
  return (
    <div className="h-2 rounded-full overflow-hidden bg-white/5">
      <div
        className="h-full rounded-full transition-all duration-300"
        style={{ width: `${pct}%`, backgroundColor: color }}
      />
    </div>
  );
}

interface StatUpgradePanelProps {
  rankings: StatRankingEntry[];
  mode: OptimizeMode;
  onModeChange: (mode: OptimizeMode) => void;
  isLoading: boolean;
  error: Error | null;
  onRetry?: () => void;
}

export default function StatUpgradePanel({
  rankings,
  mode,
  onModeChange,
  isLoading,
  error,
  onRetry,
}: StatUpgradePanelProps) {
  const maxImpact = rankings.length > 0
    ? Math.max(...rankings.map((r) => Math.abs(r.impact_score)))
    : 1;

  const modeToggle = (
    <div className="flex gap-1">
      {(Object.keys(MODE_LABELS) as OptimizeMode[]).map((m) => (
        <button
          key={m}
          onClick={() => onModeChange(m)}
          className={clsx(
            "px-2 py-1 font-mono text-[10px] uppercase tracking-widest rounded-sm border transition-all",
            m === mode
              ? MODE_COLORS[m]
              : "border-forge-border text-forge-dim hover:text-forge-muted"
          )}
        >
          {MODE_LABELS[m]}
        </button>
      ))}
    </div>
  );

  return (
    <Panel title="Stat Rankings" action={modeToggle}>
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Spinner size={24} />
        </div>
      )}

      {error && (
        <ErrorMessage
          title="Failed to load optimization"
          message={error.message}
          onRetry={onRetry}
        />
      )}

      {!isLoading && !error && rankings.length === 0 && (
        <p className="text-forge-dim text-sm text-center py-6">
          No stat rankings available for this build.
        </p>
      )}

      {!isLoading && !error && rankings.length > 0 && (
        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
          {rankings.map((entry) => (
            <div key={entry.stat_key} className="group">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-mono text-[10px] text-forge-dim w-5 text-right shrink-0">
                    #{entry.rank}
                  </span>
                  <span className="font-mono text-xs text-forge-text truncate">
                    {entry.label}
                  </span>
                </div>
                <div className="flex items-center gap-3 shrink-0 font-mono text-[10px]">
                  <span className={clsx(
                    entry.dps_gain_pct > 0 ? "text-forge-amber" : "text-forge-dim"
                  )}>
                    {entry.dps_gain_pct > 0 ? "+" : ""}{entry.dps_gain_pct.toFixed(1)}% DPS
                  </span>
                  <span className={clsx(
                    entry.ehp_gain_pct > 0 ? "text-forge-cyan" : "text-forge-dim"
                  )}>
                    {entry.ehp_gain_pct > 0 ? "+" : ""}{entry.ehp_gain_pct.toFixed(1)}% EHP
                  </span>
                </div>
              </div>
              <ImpactBar
                value={entry.impact_score}
                max={maxImpact}
                color={mode === "defense" ? C.cyan : mode === "offense" ? C.amber : C.green}
              />
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}
