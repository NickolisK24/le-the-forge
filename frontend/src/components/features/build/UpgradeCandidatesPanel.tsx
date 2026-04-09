/**
 * UpgradeCandidatesPanel — Phase 4 affix efficiency rankings.
 *
 * Shows the top upgrade candidates sorted by efficiency score
 * (impact per forge potential cost). Top 3 are highlighted.
 * Shares the same TanStack Query data as StatUpgradePanel.
 */

import { clsx } from "clsx";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import type { UpgradeCandidate } from "@/types";

const PODIUM_COLORS = [
  "border-forge-gold text-forge-gold bg-forge-gold/8",
  "border-forge-amber text-forge-amber bg-forge-amber/8",
  "border-forge-cyan text-forge-cyan bg-forge-cyan/8",
];

function EfficiencyBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(Math.abs(value) / max * 100, 100) : 0;
  return (
    <div className="h-1.5 rounded-full overflow-hidden bg-white/5 flex-1">
      <div
        className="h-full rounded-full transition-all duration-300 bg-forge-amber"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

interface UpgradeCandidatesPanelProps {
  candidates: UpgradeCandidate[];
  isLoading: boolean;
  error: Error | null;
  onRetry?: () => void;
}

export default function UpgradeCandidatesPanel({
  candidates,
  isLoading,
  error,
  onRetry,
}: UpgradeCandidatesPanelProps) {
  const maxEfficiency = candidates.length > 0
    ? Math.max(...candidates.map((c) => Math.abs(c.efficiency_score)))
    : 1;

  return (
    <Panel title="Top Upgrade Candidates">
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Spinner size={24} />
        </div>
      )}

      {error && (
        <ErrorMessage
          title="Failed to load candidates"
          message={error.message}
          onRetry={onRetry}
        />
      )}

      {!isLoading && !error && candidates.length === 0 && (
        <p className="text-forge-dim text-sm text-center py-6">
          No upgrade candidates available.
        </p>
      )}

      {!isLoading && !error && candidates.length > 0 && (
        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
          {candidates.map((candidate, idx) => {
            const isTop3 = idx < 3;
            return (
              <div
                key={candidate.affix_id}
                className={clsx(
                  "rounded-sm border p-2.5 transition-colors",
                  isTop3
                    ? PODIUM_COLORS[idx]
                    : "border-forge-border bg-transparent"
                )}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={clsx(
                      "font-mono text-[10px] w-5 text-right shrink-0",
                      isTop3 ? "font-bold" : "text-forge-dim"
                    )}>
                      #{candidate.rank}
                    </span>
                    <span className={clsx(
                      "font-mono text-xs truncate",
                      isTop3 ? "font-semibold" : "text-forge-text"
                    )}>
                      {candidate.label}
                    </span>
                  </div>
                  <span className="font-mono text-[10px] text-forge-dim shrink-0 ml-2">
                    {candidate.fp_cost} FP
                  </span>
                </div>

                <div className="flex items-center gap-2 mb-1">
                  <EfficiencyBar value={candidate.efficiency_score} max={maxEfficiency} />
                  <span className="font-mono text-[10px] text-forge-amber shrink-0 w-14 text-right">
                    {candidate.efficiency_score.toFixed(2)}
                  </span>
                </div>

                <div className="flex gap-3 font-mono text-[10px]">
                  <span className={clsx(
                    candidate.dps_gain_pct > 0 ? "text-forge-amber" : "text-forge-dim"
                  )}>
                    {candidate.dps_gain_pct > 0 ? "+" : ""}{candidate.dps_gain_pct.toFixed(1)}% DPS
                  </span>
                  <span className={clsx(
                    candidate.ehp_gain_pct > 0 ? "text-forge-cyan" : "text-forge-dim"
                  )}>
                    {candidate.ehp_gain_pct > 0 ? "+" : ""}{candidate.ehp_gain_pct.toFixed(1)}% EHP
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
}
