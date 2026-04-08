/**
 * PointEconomyPanel — displays point budget, tier unlock status, and validation errors.
 */

import type { ValidationResult, TierStatus } from "@/logic/validatePassiveBuild";
import { MAX_PASSIVE_POINTS } from "@/logic/validatePassiveBuild";

interface Props {
  validation: ValidationResult;
}

export default function PointEconomyPanel({ validation }: Props) {
  const {
    valid, pointsSpent, basePointsSpent, pointsRemaining,
    errors, tiers, selectedMasteries,
  } = validation;

  // Only show tiers that have allocated nodes at or above their threshold
  const relevantTiers = tiers.filter((t) => t.tier <= Math.max(basePointsSpent + 10, 20));

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Point Economy
        </span>
        <span className={`font-mono text-xs font-bold ${valid ? "text-green-400" : "text-red-400"}`}>
          {valid ? "LEGAL" : "INVALID"}
        </span>
      </div>

      {/* Point budget bar */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="font-mono text-xs text-forge-muted">
            Points: <span className="text-forge-amber font-bold">{pointsSpent}</span> / {MAX_PASSIVE_POINTS}
          </span>
          <span className="font-mono text-xs text-forge-dim">
            {pointsRemaining} remaining
          </span>
        </div>
        <div className="h-2 rounded-full bg-forge-surface2 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              pointsSpent > MAX_PASSIVE_POINTS ? "bg-red-500" : "bg-forge-amber"
            }`}
            style={{ width: `${Math.min(100, (pointsSpent / MAX_PASSIVE_POINTS) * 100)}%` }}
          />
        </div>
        <div className="flex justify-between mt-1 font-mono text-[10px] text-forge-dim">
          <span>Base: {basePointsSpent}</span>
          <span>Mastery: {pointsSpent - basePointsSpent}</span>
          {selectedMasteries.length > 0 && (
            <span>Mastery: {selectedMasteries.join(", ")}</span>
          )}
        </div>
      </div>

      {/* Tier unlock status */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
          Tier Status
        </div>
        <div className="grid grid-cols-5 sm:grid-cols-10 gap-1">
          {relevantTiers.map((tier) => (
            <TierBadge key={tier.tier} tier={tier} />
          ))}
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-red-400 mb-1">
            Validation Errors
          </div>
          <div className="space-y-0.5">
            {errors.map((err, i) => (
              <div key={i} className="font-mono text-xs text-red-400/80">
                ✗ {err}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TierBadge({ tier }: { tier: TierStatus }) {
  return (
    <div
      className={`rounded px-1.5 py-0.5 text-center font-mono text-[10px] ${
        tier.unlocked
          ? "bg-green-500/15 text-green-400"
          : "bg-forge-surface2 text-forge-dim"
      }`}
      title={`Tier ${tier.tier}: requires ${tier.required} base points (have ${tier.spent})`}
    >
      {tier.tier === 0 ? "0" : tier.tier}
      <span className="ml-0.5">{tier.unlocked ? "✓" : "✗"}</span>
    </div>
  );
}
