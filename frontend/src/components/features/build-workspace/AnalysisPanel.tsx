/**
 * AnalysisPanel — presentation layer for the unified workspace (phase 3).
 *
 * Composes the purpose-built phase-3 presentation components:
 *   1. BuildScoreCard          — hero card with letter grade + summary.
 *   2. OffenseCard + DefenseCard — side-by-side stat cards.
 *   3. PrimarySkillBreakdown    — per-skill DPS card.
 *   4. SkillsSummaryTable       — 5-row table with expand-on-click detail.
 *   5. "What to improve next"   — StatUpgradePanel + UpgradeCandidatesPanel
 *                                   (slug-scoped; saved builds only).
 *   6. AdvancedAnalysisAccordion — boss / corruption / gear (slug-scoped).
 *
 * The four phase-2 states (idle, pending, success, error) still govern
 * what the panel renders as a whole:
 *   - idle         → empty-state message ("Select a class and specialize
 *                    a skill to see analysis.") + optional icon.
 *   - pending (no prior result) → skeletons for each section.
 *   - pending (with prior)      → prior composition stays visible, a
 *                                 non-intrusive "Updating…" badge appears
 *                                 in the panel header.
 *   - success                   → full composition.
 *   - error                     → error block + retry button (unchanged).
 *
 * The 520px minimum height from phase 2 is preserved so the empty-state
 * and error transitions don't collapse the rail.
 */

import { useQuery } from "@tanstack/react-query";

import { buildsApi } from "@/lib/api";
import type { OptimizeMode } from "@/types";
import { useState } from "react";

import { useBuildWorkspaceStore } from "@/store";
import {
  runAnalysisNow,
  buildIsSimulatable,
} from "@/hooks/useDebouncedAnalysis";

import BuildScoreCard from "./analysis/BuildScoreCard";
import OffenseCard from "./analysis/OffenseCard";
import DefenseCard from "./analysis/DefenseCard";
import PrimarySkillBreakdown from "./analysis/PrimarySkillBreakdown";
import SkillsSummaryTable from "./analysis/SkillsSummaryTable";
import AdvancedAnalysisAccordion from "./analysis/AdvancedAnalysisAccordion";

import StatUpgradePanel from "@/components/features/build/StatUpgradePanel";
import UpgradeCandidatesPanel from "@/components/features/build/UpgradeCandidatesPanel";

// ---------------------------------------------------------------------------
// Layout constants
// ---------------------------------------------------------------------------

/**
 * Phase-2 reserved 520 px of vertical space on the empty/pending states so
 * the editor column doesn't reflow under the panel as analysis lands.
 * Phase 3's full composition naturally exceeds that on success, so the
 * min-height's only remaining job is the empty / error states — still a
 * worthwhile floor to keep.
 */
const PANEL_MIN_HEIGHT = "min-h-[520px]";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface AnalysisPanelProps {
  /**
   * Optional handler the workspace passes in so components inside the
   * panel (score card, primary-skill breakdown) can request a jump back to
   * the Skills tab. When omitted the buttons hide themselves.
   */
  onOpenSkills?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function AnalysisPanel({ onOpenSkills }: AnalysisPanelProps = {}) {
  const status = useBuildWorkspaceStore((s) => s.analysisStatus);
  const result = useBuildWorkspaceStore((s) => s.analysisResult);
  const error = useBuildWorkspaceStore((s) => s.analysisError);
  const build = useBuildWorkspaceStore((s) => s.build);
  const slug = useBuildWorkspaceStore((s) => s.identity.slug);

  const simulatable = buildIsSimulatable(build);

  // The error state lives outside the pending/success branches because it
  // owns the whole panel — phase 2 contract.
  const showError = simulatable && status === "error";

  // Show the "Updating…" badge only when a request is in flight AND we
  // already have a prior result. When no prior result exists, the per-
  // section skeletons carry that signal instead.
  const showUpdatingBadge = simulatable && status === "pending" && result !== null;

  return (
    <aside
      data-testid="workspace-analysis-panel"
      data-analysis-status={status}
      className={`relative rounded-lg border border-white/10 bg-black/30 p-4 ${PANEL_MIN_HEIGHT}`}
    >
      <PanelHeader showUpdatingBadge={showUpdatingBadge} />

      {!simulatable && (
        <IdlePanel message="Select a class and specialize a skill to see analysis." />
      )}

      {simulatable && status === "idle" && !result && (
        <IdlePanel message="Edit your build to see analysis." />
      )}

      {showError && <ErrorPanel message={error ?? "Analysis failed"} />}

      {simulatable && !showError && (status !== "idle" || result) && (
        <div className="flex flex-col gap-4 min-w-0">
          {/* 1. Score card */}
          <BuildScoreCard
            result={result}
            status={status}
            characterClass={build.character_class}
            mastery={build.mastery}
            onOpenSkills={onOpenSkills}
          />

          {/* 2. Offense + Defense */}
          {result ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <OffenseCard dps={result.dps} stats={result.stats} />
              <DefenseCard defense={result.defense} />
            </div>
          ) : (
            <SectionSkeletonGrid />
          )}

          {/* 3. Primary skill breakdown */}
          {result ? (
            <PrimarySkillBreakdown
              skillName={result.primary_skill}
              dps={result.dps}
              onOpenSkills={onOpenSkills}
            />
          ) : (
            <SectionSkeleton height="h-40" />
          )}

          {/* 4. All skills summary */}
          {result ? (
            <SkillsSummaryTable
              skills={build.skills.map((s) => ({
                slot: s.slot,
                skill_name: s.skill_name,
                points_allocated: s.points_allocated,
              }))}
              dpsPerSkill={result.dps_per_skill ?? []}
              primaryDps={result.dps}
              primarySkillName={result.primary_skill}
            />
          ) : (
            <SectionSkeleton height="h-48" />
          )}

          {/* 5. What to improve next — slug-scoped */}
          {slug && <ImproveNextSection slug={slug} hasResult={!!result} />}

          {/* 6. Advanced analysis accordion */}
          <AdvancedAnalysisAccordion slug={slug} />
        </div>
      )}
    </aside>
  );
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

function PanelHeader({ showUpdatingBadge }: { showUpdatingBadge: boolean }) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-base font-semibold text-white">Analysis</h2>
      {showUpdatingBadge && (
        <span
          data-testid="analysis-pending-indicator"
          className="flex items-center gap-1.5 text-xs text-white/60"
          aria-live="polite"
        >
          <span
            className="inline-block h-2 w-2 animate-pulse rounded-full bg-forge-cyan"
            aria-hidden="true"
          />
          Updating…
        </span>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Idle state
// ---------------------------------------------------------------------------

function IdlePanel({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div
      data-testid="analysis-idle"
      className="flex h-full min-h-[440px] flex-col items-center justify-center text-center text-sm text-white/50 gap-3"
    >
      {/* Subtle built-in icon — no new asset. */}
      <svg
        aria-hidden="true"
        width="36"
        height="36"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-forge-dim"
      >
        <path d="M12 3v2" />
        <path d="M12 19v2" />
        <path d="M4.93 4.93 6.34 6.34" />
        <path d="M17.66 17.66 19.07 19.07" />
        <path d="M3 12h2" />
        <path d="M19 12h2" />
        <path d="M4.93 19.07 6.34 17.66" />
        <path d="M17.66 6.34 19.07 4.93" />
        <circle cx="12" cy="12" r="4" />
      </svg>
      <p className="max-w-[22rem]">{message}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------

function ErrorPanel({ message }: { message: string }) {
  return (
    <div
      data-testid="analysis-error"
      className="flex h-full min-h-[440px] flex-col items-center justify-center gap-3 text-center text-sm"
    >
      <p className="text-red-400" role="alert">
        {message}
      </p>
      <button
        type="button"
        data-testid="analysis-retry"
        onClick={() => runAnalysisNow()}
        className="rounded border border-forge-cyan/40 bg-forge-cyan/10 px-4 py-2 text-forge-cyan hover:bg-forge-cyan/20 min-h-[44px]"
      >
        Retry
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section skeletons
// ---------------------------------------------------------------------------

function SectionSkeleton({ height = "h-24" }: { height?: string }) {
  return (
    <div
      data-testid="analysis-skeleton"
      className={`animate-pulse rounded border border-white/5 bg-white/5 ${height}`}
    />
  );
}

function SectionSkeletonGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="analysis-skeleton-grid">
      <SectionSkeleton height="h-40" />
      <SectionSkeleton height="h-40" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// "What to improve next" section — slug-scoped
// ---------------------------------------------------------------------------

function ImproveNextSection({ slug, hasResult }: { slug: string; hasResult: boolean }) {
  const [mode, setMode] = useState<OptimizeMode>("balanced");
  const query = useQuery({
    queryKey: ["optimize", slug, mode],
    queryFn: () => buildsApi.optimize(slug, mode),
    enabled: hasResult,
    staleTime: 30 * 60 * 1000,
    select: (res) => res.data,
  });

  return (
    <section data-testid="improve-next-section" className="flex flex-col gap-3 min-w-0">
      <div className="flex flex-col gap-1">
        <h3 className="font-display text-lg font-bold tracking-wider text-forge-text">
          What to improve next
        </h3>
        <p className="font-body text-sm text-forge-dim">
          These stats will give you the biggest improvement per forge
          potential invested.
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2 min-w-0">
        <StatUpgradePanel
          rankings={query.data?.stat_rankings ?? []}
          mode={mode}
          onModeChange={setMode}
          isLoading={query.isLoading}
          error={query.error as Error | null}
          onRetry={() => query.refetch()}
        />
        <UpgradeCandidatesPanel
          candidates={query.data?.top_upgrade_candidates ?? []}
          isLoading={query.isLoading}
          error={query.error as Error | null}
          onRetry={() => query.refetch()}
        />
      </div>
    </section>
  );
}
