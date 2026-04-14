/**
 * BuildScoreCard — hero card at the top of the simulation page.
 *
 * Converts raw sim numbers into a single 0–100 rating + letter grade plus
 * a plain-English summary of the build's biggest weakness, so that a
 * player can understand their build strength at a glance.
 */

import { Panel } from "@/components/ui";
import { statLabel } from "@/constants/statLabels";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface BuildScoreCardProps {
  skillName: string;
  characterClass: string;
  mastery: string;
  dps: number;
  effectiveHp: number;
  survivabilityScore: number;
  /** Backend-provided weakness strings, e.g. "Low Fire Resistance (12%)". */
  weaknesses: string[];
  /** Optional top upgrade label from stat rankings. */
  topUpgrade?: string | null;
  isLoading?: boolean;
}

// ---------------------------------------------------------------------------
// Rating math
// ---------------------------------------------------------------------------

export interface BuildRating {
  rating: number;
  letter: "S" | "A" | "B" | "C" | "D";
  color: string;
  dpsEfficiency: number;
  ehpEfficiency: number;
  survEfficiency: number;
}

export function computeBuildRating(
  dps: number,
  effectiveHp: number,
  survivabilityScore: number,
): BuildRating {
  const dpsEfficiency  = Math.min(Math.max(dps, 0) / 20_000, 1.0);
  const ehpEfficiency  = Math.min(Math.max(effectiveHp, 0) / 8_000, 1.0);
  const survEfficiency = Math.min(Math.max(survivabilityScore, 0) / 100, 1.0);
  const rating = Math.round(
    dpsEfficiency * 40 + ehpEfficiency * 30 + survEfficiency * 30,
  );

  let letter: BuildRating["letter"];
  let color: string;
  if (rating >= 90)      { letter = "S"; color = "#f0a020"; }
  else if (rating >= 75) { letter = "A"; color = "#4ade80"; }
  else if (rating >= 60) { letter = "B"; color = "#22d3ee"; }
  else if (rating >= 45) { letter = "C"; color = "#f0a020"; }
  else                   { letter = "D"; color = "#f87171"; }

  return { rating, letter, color, dpsEfficiency, ehpEfficiency, survEfficiency };
}

// ---------------------------------------------------------------------------
// Plain-English summary
// ---------------------------------------------------------------------------

export function computeSummary(
  rating: BuildRating,
  survivabilityScore: number,
  weaknesses: string[],
  topUpgrade?: string | null,
): string {
  const { dpsEfficiency, ehpEfficiency, survEfficiency } = rating;

  // Well-rounded and strong
  if (rating.rating >= 75 && dpsEfficiency >= 0.6 && ehpEfficiency >= 0.6) {
    return "Well-rounded build ready for endgame content.";
  }

  const dpsWeak  = dpsEfficiency < 0.6;
  const survWeak = ehpEfficiency < 0.6 || survEfficiency < 0.6;

  // Both below average
  if (dpsWeak && survWeak) {
    return "Build needs investment in both offense and defense to reach endgame viability.";
  }

  // Survivability weakest
  const survivabilityIsWeakest =
    survEfficiency <= dpsEfficiency && survEfficiency <= ehpEfficiency;

  if (survivabilityIsWeakest && survivabilityScore < 50) {
    const firstWeakness = weaknesses.find((w) => w && w.trim().length > 0);
    if (firstWeakness) {
      return `Strong damage output, but survivability needs work. Prioritize improving ${firstWeakness}.`;
    }
    return "Strong damage output, but survivability needs work. Prioritize improving resistances and effective HP.";
  }

  // DPS weakest
  const dpsIsWeakest =
    dpsEfficiency <= ehpEfficiency && dpsEfficiency <= survEfficiency;
  if (dpsIsWeakest && dpsEfficiency < 0.6) {
    if (topUpgrade && topUpgrade.trim().length > 0) {
      return `Solid defenses, but damage output has room to grow. ${topUpgrade}`;
    }
    return "Solid defenses, but damage output has room to grow. Consider upgrading offensive affixes.";
  }

  // Fallback — generic but still informative
  return "Build is making steady progress. Run another simulation after making upgrades to track improvement.";
}

// ---------------------------------------------------------------------------
// Presentation
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(Math.round(n));
}

function StatPill({
  label, value,
}: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5 rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 min-w-0 flex-1">
      <span className="font-mono text-[9px] uppercase tracking-widest text-forge-dim truncate">
        {label}
      </span>
      <span className="font-display text-lg font-bold text-forge-text tabular-nums truncate">
        {value}
      </span>
    </div>
  );
}

function Skeleton({ className }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded-sm bg-forge-surface2 ${className ?? ""}`} />
  );
}

export default function BuildScoreCard({
  skillName, characterClass, mastery,
  dps, effectiveHp, survivabilityScore,
  weaknesses, topUpgrade, isLoading,
}: BuildScoreCardProps) {
  const rating = computeBuildRating(dps, effectiveHp, survivabilityScore);
  const summary = computeSummary(rating, survivabilityScore, weaknesses, topUpgrade);

  return (
    <Panel>
      <div className="flex flex-col gap-3">
        {/* Row 1: skill name + class / mastery */}
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <div className="min-w-0">
            {isLoading ? (
              <Skeleton className="h-6 w-48" />
            ) : (
              <h2 className="font-display text-xl font-bold text-forge-text tracking-wider truncate">
                {skillName || "No Primary Skill"}
              </h2>
            )}
          </div>
          {isLoading ? (
            <Skeleton className="h-4 w-32" />
          ) : (
            <div className="flex flex-wrap items-center gap-2 font-mono text-[11px] uppercase tracking-widest">
              <span className="rounded-sm border border-forge-purple/40 bg-forge-purple/8 px-2 py-0.5 text-forge-purple">
                {characterClass}
              </span>
              <span className="rounded-sm border border-forge-border px-2 py-0.5 text-forge-muted">
                {mastery}
              </span>
            </div>
          )}
        </div>

        {/* Row 2: grade letter + stat pills */}
        <div className="flex flex-col sm:flex-row items-stretch gap-3">
          {/* Letter grade */}
          <div
            className="relative flex items-center justify-center rounded-sm border bg-forge-surface2 min-h-[100px] sm:min-w-[120px]"
            style={{
              borderColor: `${rating.color}55`,
              boxShadow: isLoading ? undefined : `inset 0 0 40px ${rating.color}22`,
            }}
            aria-label={`Build rating ${rating.letter} (${rating.rating} out of 100)`}
          >
            {isLoading ? (
              <Skeleton className="h-16 w-16" />
            ) : (
              <div className="flex flex-col items-center">
                <span
                  className="font-display font-bold leading-none"
                  style={{
                    color: rating.color,
                    fontSize: "4rem",
                    textShadow: `0 0 22px ${rating.color}60`,
                  }}
                >
                  {rating.letter}
                </span>
                <span className="mt-1 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                  {rating.rating} / 100
                </span>
              </div>
            )}
          </div>

          {/* Stat pills */}
          <div className="flex flex-1 flex-wrap gap-2">
            {isLoading ? (
              <>
                <Skeleton className="h-14 flex-1 min-w-[120px]" />
                <Skeleton className="h-14 flex-1 min-w-[120px]" />
                <Skeleton className="h-14 flex-1 min-w-[120px]" />
              </>
            ) : (
              <>
                <StatPill label={statLabel("total_dps")} value={fmt(dps)} />
                <StatPill label="Effective HP" value={fmt(effectiveHp)} />
                <StatPill
                  label="Survivability"
                  value={`${Math.round(survivabilityScore)} / 100`}
                />
              </>
            )}
          </div>
        </div>

        {/* Row 3: plain-English summary */}
        {isLoading ? (
          <Skeleton className="h-4 w-full" />
        ) : (
          <p className="font-body text-sm text-forge-dim leading-relaxed">
            {summary}
          </p>
        )}
      </div>
    </Panel>
  );
}
