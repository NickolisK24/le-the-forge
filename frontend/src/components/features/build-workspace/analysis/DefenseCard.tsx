/**
 * DefenseCard — defensive stat panel for the unified AnalysisPanel.
 *
 * Rows (prompt §4):
 *   - Max health
 *   - Effective HP
 *   - Armor damage reduction (%)
 *   - Average elemental resistance (%)
 *   - Survivability rating — with a 0 to 100 horizontal bar
 *
 * Each row uses the plain-English label from statLabels.ts and a benchmark
 * color dot from statBenchmarks.ts. Values are formatted through
 * `./format.ts`.
 */

import type { DefenseResult } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";
import {
  getBenchmarkTier,
  BENCHMARK_COLORS,
  type BenchmarkTier,
} from "@/constants/statBenchmarks";

import { fmtNumber, fmtPct } from "./format";

// ---------------------------------------------------------------------------
// Row primitive — the defense card reuses the offense-card layout but also
// supports an inline progress bar (for the survivability row).
// ---------------------------------------------------------------------------

interface RowProps {
  label: string;
  value: string;
  tier?: BenchmarkTier;
  /** When present, renders a 0..max progress bar below the row. */
  progress?: { value: number; max: number };
  testId?: string;
}

function Row({ label, value, tier, progress, testId }: RowProps) {
  const dotColor = tier ? BENCHMARK_COLORS[tier] : undefined;
  return (
    <div
      data-testid={testId}
      data-tier={tier}
      className="py-1.5 border-b border-forge-border/30 last:border-b-0"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          {dotColor && (
            <span
              aria-hidden="true"
              className="shrink-0 w-2 h-2 rounded-full"
              style={{
                backgroundColor: dotColor,
                boxShadow: `0 0 6px ${dotColor}80`,
              }}
            />
          )}
          <span className="font-body text-xs text-forge-muted truncate">
            {label}
          </span>
        </div>
        <span className="font-mono text-xs text-forge-text tabular-nums shrink-0">
          {value}
        </span>
      </div>
      {progress && (
        <div
          className="mt-1.5 h-1 rounded-full bg-forge-surface2 overflow-hidden"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={progress.max}
          aria-valuenow={progress.value}
          data-testid={`${testId}-bar`}
        >
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.min(100, (progress.value / progress.max) * 100)}%`,
              backgroundColor: dotColor ?? "#f0a020",
            }}
          />
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export interface DefenseCardProps {
  defense: DefenseResult;
}

export default function DefenseCard({ defense: def }: DefenseCardProps) {
  const maxHealth = def.max_health ?? 0;
  const ehp = def.effective_hp ?? 0;
  const armor = def.armor_reduction_pct ?? 0;
  const avgRes = def.avg_resistance ?? 0;
  const surv = def.survivability_score ?? 0;

  return (
    <section
      data-testid="defense-card"
      className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0"
    >
      <header className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-3 shrink-0">
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
          Defense
        </span>
      </header>
      <div className="p-4 flex flex-col">
        <Row
          testId="defense-row-max-health"
          label={statLabel("max_health")}
          value={fmtNumber(maxHealth)}
        />
        <Row
          testId="defense-row-effective-hp"
          label={statLabel("effective_hp")}
          value={fmtNumber(ehp)}
          tier={getBenchmarkTier("effective_hp", ehp)}
        />
        <Row
          testId="defense-row-armor-reduction"
          label={statLabel("armor_reduction_pct")}
          value={fmtPct(armor)}
          tier={getBenchmarkTier("armor_reduction_pct", armor)}
        />
        <Row
          testId="defense-row-avg-resistance"
          label={statLabel("avg_resistance")}
          value={fmtPct(avgRes)}
          tier={getBenchmarkTier("avg_resistance", avgRes)}
        />
        <Row
          testId="defense-row-survivability"
          label={statLabel("survivability_score")}
          value={`${Math.round(surv)} / 100`}
          tier={getBenchmarkTier("survivability_score", surv)}
          progress={{ value: surv, max: 100 }}
        />
      </div>
    </section>
  );
}
