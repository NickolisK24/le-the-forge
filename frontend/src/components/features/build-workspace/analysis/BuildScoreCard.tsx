/**
 * BuildScoreCard — hero card at the top of the unified AnalysisPanel.
 *
 * Responsibilities:
 *   - Primary skill / class / mastery summary line with a "Change" button
 *     that opens the skill selector on the Skills tab.
 *   - Overall Build Rating letter (S/A/B/C/D) computed from a weighted sum
 *     of DPS efficiency (40 %), EHP efficiency (30 %), and survivability
 *     score (30 %).
 *   - Three stat pills with benchmark-tier colours.
 *   - One-sentence auto-generated summary driven by the weakest dimension.
 *
 * This component is purpose-built for the phase-3 workspace. It composes
 * the same maths as the legacy `features/build/simulation/BuildScoreCard`
 * but adds state handling for the pending skeleton and the idle "hide the
 * card entirely" case, both specified by the phase-3 prompt.
 */

import type { BuildSimulationResult, StatUpgrade } from "@/lib/api";
import type { AnalysisStatus } from "@/store/buildWorkspace";
import {
  getBenchmarkTier,
  BENCHMARK_COLORS,
  type BenchmarkTier,
} from "@/constants/statBenchmarks";

// ---------------------------------------------------------------------------
// Benchmark upper bounds used to normalise the raw values into 0..1.
// These mirror the "strong" thresholds in statBenchmarks.ts on purpose:
// hitting the strong threshold = full credit on that dimension.
// ---------------------------------------------------------------------------

export const DPS_UPPER_BOUND           = 20_000;
export const EHP_UPPER_BOUND           = 8_000;
export const SURVIVABILITY_UPPER_BOUND = 100;

// ---------------------------------------------------------------------------
// Rating math
// ---------------------------------------------------------------------------

export type BuildGrade = "S" | "A" | "B" | "C" | "D";

export interface BuildRating {
  score: number;
  letter: BuildGrade;
  color: string;
  dpsEfficiency: number;
  ehpEfficiency: number;
  survEfficiency: number;
}

/**
 * Letter-grade palette. See phase-3 notes §2.3 for the rationale on the
 * C-tier switching from amber to yellow.
 */
export const GRADE_COLORS: Record<BuildGrade, string> = {
  S: "#f0a020", // forge-amber / gold
  A: "#4ade80", // green
  B: "#22d3ee", // cyan (close to forge-cyan)
  C: "#facc15", // yellow
  D: "#f87171", // red
};

export function computeBuildRating(
  dps: number,
  effectiveHp: number,
  survivabilityScore: number,
): BuildRating {
  const dpsEfficiency  = clamp01(dps / DPS_UPPER_BOUND);
  const ehpEfficiency  = clamp01(effectiveHp / EHP_UPPER_BOUND);
  const survEfficiency = clamp01(survivabilityScore / SURVIVABILITY_UPPER_BOUND);

  const weighted = dpsEfficiency * 40 + ehpEfficiency * 30 + survEfficiency * 30;
  const score = Math.max(0, Math.min(100, Math.round(weighted)));

  let letter: BuildGrade;
  if (score >= 90) letter = "S";
  else if (score >= 75) letter = "A";
  else if (score >= 60) letter = "B";
  else if (score >= 45) letter = "C";
  else letter = "D";

  return {
    score,
    letter,
    color: GRADE_COLORS[letter],
    dpsEfficiency,
    ehpEfficiency,
    survEfficiency,
  };
}

function clamp01(n: number): number {
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

// ---------------------------------------------------------------------------
// Summary sentence — branches specified by the phase-3 prompt.
// ---------------------------------------------------------------------------

export interface SummaryInput {
  rating: BuildRating;
  survivabilityScore: number;
  weaknesses: string[];
  topUpgrade?: StatUpgrade | null;
  /**
   * Elemental resistance values (fire / cold / lightning / void / necrotic).
   * When every value is within `ELEMENTAL_RES_TIGHT_SPREAD_PCT` of every
   * other value, the summary uses generic "elemental resistances" phrasing
   * instead of singling out one — there is no real "weakest" when they are
   * all equally low.
   */
  elementalResistances?: number[];
}

/**
 * Threshold (in percentage points) under which all elemental resistances
 * are considered "tied" and the summary should not single one out.
 */
export const ELEMENTAL_RES_TIGHT_SPREAD_PCT = 5;

/**
 * Returns true when the spread (max - min) of the provided resistance
 * values is within `ELEMENTAL_RES_TIGHT_SPREAD_PCT`. A list with fewer
 * than two entries is trivially "tight" — no meaningful single call-out
 * is possible.
 */
export function elementalResistancesAreTight(xs: readonly number[]): boolean {
  if (!xs || xs.length < 2) return true;
  const finite = xs.filter((n) => Number.isFinite(n));
  if (finite.length < 2) return true;
  const min = Math.min(...finite);
  const max = Math.max(...finite);
  return max - min <= ELEMENTAL_RES_TIGHT_SPREAD_PCT;
}

/**
 * Returns the one-sentence build summary. Branches, in priority order:
 *
 *  0. Overall score is below 20 → "Build needs significant investment
 *     before analysis is meaningful. Allocate skill points, passives,
 *     and gear to see accurate results."  This catches the freshly-
 *     initialised build case where the weighted score is a single digit
 *     and the "balanced" language of the fallback is misleading.
 *  1. Both DPS efficiency and survivability are strong (DPS efficiency
 *     >= 0.6 AND survivability score >= 75, matching
 *     `STAT_BENCHMARKS.survivability_score.strong`) → "Well-rounded ...".
 *  2. Survivability score is below 50 → "... with low survivability.
 *     Consider improving {weakest resistance type}."
 *  3. DPS efficiency is below 0.6 → "... with room to improve damage
 *     output. Consider {top stat upgrade recommendation}."
 *  4. Fallback → "Balanced build with room for refinement."
 */
export function computeSummary(input: SummaryInput): string {
  const {
    rating,
    survivabilityScore,
    weaknesses,
    topUpgrade,
    elementalResistances,
  } = input;
  const { dpsEfficiency, score } = rating;

  // Branch 0 — catastrophically low score (fresh-build floor).
  if (score < 20) {
    return (
      "Build needs significant investment before analysis is meaningful. " +
      "Allocate skill points, passives, and gear to see accurate results."
    );
  }

  // Branch 1 — both DPS efficiency and survivability are strong.
  // "Strong" is read against the statBenchmarks tiers: DPS >= 0.6 clears
  // the phase-3 "average-or-better" bar; survivability >= 75 is the
  // documented "strong" tier.
  if (dpsEfficiency >= 0.6 && survivabilityScore >= 75) {
    return "Well-rounded build ready for endgame content.";
  }

  // Branch 2 — low survivability.
  if (survivabilityScore < 50) {
    // If every elemental resistance is within 5 % of every other, there is
    // no real "weakest" — singling one out reads as arbitrary. Use the
    // generic plural phrasing instead.
    if (
      elementalResistances &&
      elementalResistances.length >= 2 &&
      elementalResistancesAreTight(elementalResistances)
    ) {
      return "Balanced build with low survivability. Consider improving elemental resistances.";
    }
    const weakest = pickFirstNonEmpty(weaknesses);
    if (weakest) {
      return `Balanced build with low survivability. Consider improving ${weakest}.`;
    }
    return "Balanced build with low survivability. Consider improving your weakest resistance.";
  }

  // Branch 3 — weak damage.
  if (dpsEfficiency < 0.6) {
    const upgradeLabel = topUpgrade?.label?.trim();
    if (upgradeLabel) {
      return `Balanced build with room to improve damage output. Consider ${upgradeLabel}.`;
    }
    return "Balanced build with room to improve damage output. Consider upgrading offensive affixes.";
  }

  // Branch 4 — fallback.
  return "Balanced build with room for refinement.";
}

function pickFirstNonEmpty(xs: string[]): string | null {
  for (const x of xs) {
    if (typeof x === "string" && x.trim().length > 0) return x;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Benchmarked stat pill
// ---------------------------------------------------------------------------

interface PillProps {
  label: string;
  value: string;
  tier: BenchmarkTier;
}

function StatPill({ label, value, tier }: PillProps) {
  const color = BENCHMARK_COLORS[tier];
  return (
    <div
      data-testid={`score-pill-${tier}`}
      className="flex flex-col gap-0.5 rounded-sm border bg-forge-surface2 px-3 py-2 min-w-0 flex-1"
      style={{ borderColor: `${color}55` }}
    >
      <span className="font-mono text-[9px] uppercase tracking-widest text-forge-dim truncate">
        {label}
      </span>
      <span
        className="font-display text-lg font-bold tabular-nums truncate"
        style={{ color }}
      >
        {value}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Number formatting
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(Math.round(n));
}

// ---------------------------------------------------------------------------
// Skeleton
// ---------------------------------------------------------------------------

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-sm bg-forge-surface2 ${className ?? ""}`}
    />
  );
}

function SkeletonCard() {
  return (
    <div
      data-testid="score-card-skeleton"
      className="flex flex-col gap-3 rounded border border-forge-border bg-forge-surface p-4"
    >
      <div className="flex items-center justify-between gap-2">
        <Skeleton className="h-5 w-48" />
        <Skeleton className="h-4 w-28" />
      </div>
      <div className="flex flex-col sm:flex-row gap-3">
        <Skeleton className="h-24 sm:w-28" />
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 flex-1">
          <Skeleton className="h-14" />
          <Skeleton className="h-14" />
          <Skeleton className="h-14" />
        </div>
      </div>
      <Skeleton className="h-4 w-full" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Public props
// ---------------------------------------------------------------------------

export interface BuildScoreCardProps {
  /**
   * Latest analysis result, or `null` when the panel has not yet produced
   * a success response. Must be `null` — never the empty object — so the
   * skeleton/idle branches remain exhaustive.
   */
  result: BuildSimulationResult | null;
  /** Workspace analysis status driving idle/pending/success rendering. */
  status: AnalysisStatus;
  /** Character class from the working copy of the build. */
  characterClass: string;
  /** Mastery from the working copy of the build. */
  mastery: string;
  /**
   * Called when the user clicks "Change" to override the primary skill or
   * clicks "Go to skills" when no primary skill is detected. The workspace
   * opens the Skills tab in response — phase 3 does not own tab navigation.
   */
  onOpenSkills?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function BuildScoreCard({
  result,
  status,
  characterClass,
  mastery,
  onOpenSkills,
}: BuildScoreCardProps) {
  // Idle with no result — do not render. The AnalysisPanel renders its own
  // empty state message in this case.
  if (status === "idle" && !result) {
    return null;
  }

  // Pending with no prior result — render a skeleton matching the card
  // layout so the panel does not collapse when the first request lands.
  if (status === "pending" && !result) {
    return <SkeletonCard />;
  }

  // Error or stale — if we somehow got here without a result, render the
  // skeleton as a layout-stable placeholder. The AnalysisPanel handles
  // the error message itself so this branch should rarely fire.
  if (!result) {
    return <SkeletonCard />;
  }

  const dps = result.dps.total_dps ?? result.dps.dps ?? 0;
  const ehp = result.defense.effective_hp ?? 0;
  const surv = result.defense.survivability_score ?? 0;

  const rating = computeBuildRating(dps, ehp, surv);
  const summary = computeSummary({
    rating,
    survivabilityScore: surv,
    weaknesses: result.defense.weaknesses ?? [],
    topUpgrade: result.stat_upgrades?.[0] ?? null,
    elementalResistances: [
      result.defense.fire_res,
      result.defense.cold_res,
      result.defense.lightning_res,
      result.defense.void_res,
      result.defense.necrotic_res,
    ],
  });

  const hasPrimarySkill =
    typeof result.primary_skill === "string" &&
    result.primary_skill.trim().length > 0;

  return (
    <div
      data-testid="build-score-card"
      data-grade={rating.letter}
      className="flex flex-col gap-3 rounded border border-forge-border bg-forge-surface p-4"
    >
      {/* Row 1 — title + class/mastery.
           "Build Rating" is the header (phase-3 follow-up: the old
           "Analyzing: {skill}" duplicated the PrimarySkillBreakdown card's
           title). The detected primary skill is surfaced as a subtitle. */}
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div className="flex flex-col gap-0.5 min-w-0">
          <h3
            data-testid="score-card-title"
            className="font-display text-lg font-bold text-forge-text tracking-wider"
          >
            Build Rating
          </h3>
          <div
            data-testid="score-card-subtitle"
            className="flex items-center gap-2 min-w-0"
          >
            <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim truncate">
              {hasPrimarySkill ? (
                <>
                  Analyzing{" "}
                  <span className="text-forge-amber">
                    {result.primary_skill}
                  </span>
                </>
              ) : (
                "No primary skill detected"
              )}
            </span>
            {onOpenSkills && (
              <button
                type="button"
                onClick={onOpenSkills}
                data-testid="score-card-change-skill"
                className="shrink-0 rounded-sm border border-forge-border px-2 py-1 font-mono text-[10px] uppercase tracking-widest text-forge-muted hover:border-forge-amber hover:text-forge-amber transition-colors min-h-[44px] sm:min-h-0"
              >
                {hasPrimarySkill ? "Change" : "Go to skills"}
              </button>
            )}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 font-mono text-[11px] uppercase tracking-widest">
          <span className="rounded-sm border border-forge-purple/40 bg-forge-purple/10 px-2 py-0.5 text-forge-purple">
            {characterClass || "—"}
          </span>
          <span className="rounded-sm border border-forge-border px-2 py-0.5 text-forge-muted">
            {mastery || "—"}
          </span>
        </div>
      </div>

      {/* Row 2 — letter grade + stat pills */}
      <div className="flex flex-col sm:flex-row items-stretch gap-3">
        <div
          data-testid="score-card-grade"
          data-grade={rating.letter}
          className="relative flex items-center justify-center rounded-sm border bg-forge-surface2 min-h-[96px] sm:min-w-[112px]"
          style={{
            borderColor: `${rating.color}55`,
            boxShadow: `inset 0 0 40px ${rating.color}22`,
          }}
          aria-label={`Overall build rating ${rating.letter}, ${rating.score} out of 100`}
        >
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
              {rating.score} / 100
            </span>
          </div>
        </div>

        {/* Pills — stacked on mobile (single col), 3-up on sm+. */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 flex-1">
          <StatPill
            label="Total DPS"
            value={fmt(dps)}
            tier={getBenchmarkTier("total_dps", dps)}
          />
          <StatPill
            label="Effective HP"
            value={fmt(ehp)}
            tier={getBenchmarkTier("effective_hp", ehp)}
          />
          <StatPill
            label="Survivability"
            value={`${Math.round(surv)} / 100`}
            tier={getBenchmarkTier("survivability_score", surv)}
          />
        </div>
      </div>

      {/* Row 3 — summary sentence */}
      <p
        data-testid="score-card-summary"
        className="font-body text-sm text-forge-dim leading-relaxed"
      >
        {summary}
      </p>
    </div>
  );
}
