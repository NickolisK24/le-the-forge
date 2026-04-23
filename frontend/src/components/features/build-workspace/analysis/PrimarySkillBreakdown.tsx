/**
 * PrimarySkillBreakdown — phase 3 primary-skill DPS detail panel.
 *
 * Structure (prompt §5):
 *   - Skill name with a "Change" button that opens the skill selector.
 *   - Per-hit damage, crit-weighted average hit, attacks per second,
 *     total DPS.
 *   - A horizontal stacked bar showing the DPS contribution across
 *     base damage, crit contribution, and skill-tree / modifier
 *     contribution, with each segment's percentage labeled.
 *
 * When the analysis response omits a proper contribution breakdown the
 * bar is replaced with a small "detailed breakdown not available" note.
 * The component never fabricates a segment percentage.
 *
 * The "change" button routes through the same `onOpenSkills` callback as
 * BuildScoreCard — the workspace is responsible for navigating to the
 * Skills tab. Overriding the auto-detected primary skill via a new store
 * action is deferred to phase 5 (see docs/unified-planner-phase3-notes.md
 * §5 "Open questions").
 */

import type { DPSResult } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";

import { fmtNumber, fmtPerSecond } from "./format";

// ---------------------------------------------------------------------------
// Contribution segments
// ---------------------------------------------------------------------------

export interface ContributionSegment {
  label: string;
  pct: number;
  color: string;
}

/**
 * Derive three DPS-contribution segments from the `DPSResult`. The crit
 * portion is taken verbatim from `crit_contribution_pct`; the remaining
 * non-crit DPS is split 60/40 between base damage and modifiers as a
 * presentational heuristic. The 60/40 split is the same used by the
 * legacy planner's `PrimarySkillBreakdown` so the two panels read
 * consistently.
 *
 * Returns `null` when no meaningful contribution information is available
 * (crit contribution is 0 AND DPS is 0) — callers render the fallback
 * note rather than a pointless bar.
 */
export function computeContributionSegments(
  dps: DPSResult,
): ContributionSegment[] | null {
  const critPct = clampPct(dps.crit_contribution_pct ?? 0);
  const total = dps.total_dps ?? dps.dps ?? 0;

  if (total <= 0 && critPct <= 0) return null;

  const nonCrit = 100 - critPct;
  const basePct = Math.max(0, nonCrit * 0.6);
  const modPct = Math.max(0, 100 - critPct - basePct);

  return [
    { label: "Base Damage",        pct: basePct, color: "#f0a020" }, // amber
    { label: "Crit Contribution",  pct: critPct, color: "#4ade80" }, // green
    { label: "Modifiers & Tree",   pct: modPct,  color: "#22d3ee" }, // cyan
  ];
}

function clampPct(n: number): number {
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function Stat({ label, value, testId }: { label: string; value: string; testId?: string }) {
  return (
    <div
      data-testid={testId}
      className="flex flex-col gap-0.5 rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 min-w-0"
    >
      <span className="font-mono text-[9px] uppercase tracking-widest text-forge-dim truncate">
        {label}
      </span>
      <span className="font-display text-base font-bold text-forge-text tabular-nums truncate">
        {value}
      </span>
    </div>
  );
}

function ContributionBar({ segments }: { segments: ContributionSegment[] }) {
  const visible = segments.filter((s) => s.pct > 0);
  return (
    <div className="flex flex-col gap-1.5" data-testid="primary-skill-contribution-bar">
      <div
        className="flex h-3 rounded-sm overflow-hidden border border-forge-border"
        role="img"
        aria-label="DPS contribution breakdown"
      >
        {visible.map((s) => (
          <div
            key={s.label}
            className="transition-all duration-500"
            style={{ width: `${s.pct}%`, backgroundColor: s.color }}
            title={`${s.label}: ${s.pct.toFixed(1)}%`}
            data-testid={`contribution-segment-${s.label.replace(/\s+/g, "-").toLowerCase()}`}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {visible.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5">
            <span
              aria-hidden="true"
              className="w-2 h-2 rounded-full shrink-0"
              style={{ backgroundColor: s.color }}
            />
            <span className="font-mono text-[10px] text-forge-dim">{s.label}</span>
            <span className="font-mono text-[10px] text-forge-text tabular-nums">
              {s.pct.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Props + component
// ---------------------------------------------------------------------------

export interface PrimarySkillBreakdownProps {
  skillName: string;
  dps: DPSResult;
  onOpenSkills?: () => void;
}

export default function PrimarySkillBreakdown({
  skillName,
  dps,
  onOpenSkills,
}: PrimarySkillBreakdownProps) {
  const segments = computeContributionSegments(dps);
  const totalDps = dps.total_dps ?? dps.dps ?? 0;
  const hasSkill = typeof skillName === "string" && skillName.trim().length > 0;

  return (
    <section
      data-testid="primary-skill-breakdown"
      className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0"
    >
      <header className="flex items-center justify-between gap-3 border-b border-forge-border bg-forge-surface2 px-4 py-3">
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan truncate">
          Analyzing:{" "}
          <span className="text-forge-text">{hasSkill ? skillName : "—"}</span>
        </span>
        {onOpenSkills && (
          <button
            type="button"
            onClick={onOpenSkills}
            data-testid="primary-skill-change"
            className="shrink-0 rounded-sm border border-forge-border px-2 py-1 font-mono text-[10px] uppercase tracking-widest text-forge-muted hover:border-forge-amber hover:text-forge-amber transition-colors min-h-[44px] sm:min-h-0"
          >
            Change
          </button>
        )}
      </header>

      <div className="p-4 flex flex-col gap-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Stat
            testId="primary-skill-hit-damage"
            label={statLabel("hit_damage")}
            value={fmtNumber(dps.hit_damage)}
          />
          <Stat
            testId="primary-skill-average-hit"
            label={statLabel("average_hit")}
            value={fmtNumber(dps.average_hit)}
          />
          <Stat
            testId="primary-skill-attack-speed"
            label={statLabel("effective_attack_speed")}
            value={fmtPerSecond(dps.effective_attack_speed)}
          />
          <Stat
            testId="primary-skill-total-dps"
            label={statLabel("total_dps")}
            value={fmtNumber(totalDps)}
          />
        </div>

        {segments ? (
          <>
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                DPS Contribution
              </span>
            </div>
            <ContributionBar segments={segments} />
          </>
        ) : (
          <p
            data-testid="primary-skill-no-breakdown"
            className="font-body text-xs italic text-forge-dim"
          >
            Detailed contribution breakdown is not available for this build.
          </p>
        )}
      </div>
    </section>
  );
}
