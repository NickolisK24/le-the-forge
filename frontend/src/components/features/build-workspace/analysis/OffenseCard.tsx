/**
 * OffenseCard — offense stat panel for the unified AnalysisPanel.
 *
 * Rows (prompt §4):
 *   - Primary skill DPS
 *   - Crit chance (%)
 *   - Crit multiplier (%)
 *   - Effective attack speed (attacks per second)
 *   - Ailment DPS (omitted if the build has no meaningful ailment damage)
 *
 * Each row uses the plain-English label from statLabels.ts and a benchmark
 * color dot from statBenchmarks.ts. Values are formatted through
 * `./format.ts` so the whole analysis panel shares one formatter.
 */

import type { DPSResult } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";
import {
  getBenchmarkTier,
  BENCHMARK_COLORS,
  type BenchmarkTier,
} from "@/constants/statBenchmarks";

import { fmtNumber, fmtPct, fmtPctFromFraction, fmtPerSecond } from "./format";

// ---------------------------------------------------------------------------
// Row primitive
// ---------------------------------------------------------------------------

interface RowProps {
  label: string;
  value: string;
  tier?: BenchmarkTier;
  testId?: string;
}

function Row({ label, value, tier, testId }: RowProps) {
  const dotColor = tier ? BENCHMARK_COLORS[tier] : undefined;
  return (
    <div
      data-testid={testId}
      data-tier={tier}
      className="flex items-center justify-between gap-3 py-1.5 border-b border-forge-border/30 last:border-b-0"
    >
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
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface OffenseCardProps {
  dps: DPSResult;
  stats: Record<string, number>;
}

/**
 * Ailment DPS is "meaningful" when it is a non-trivial share of total DPS or
 * a non-trivial absolute number. The threshold pair exists so a 0.5-DPS
 * floating-point artefact doesn't light up the row on a pure-hit build.
 */
function hasMeaningfulAilments(dps: DPSResult): boolean {
  const ailment = dps.ailment_dps ?? 0;
  const total = dps.total_dps ?? dps.dps ?? 0;
  if (ailment <= 1) return false; // rounds to 0 in the display anyway
  if (total > 0 && ailment / total < 0.01) return false; // < 1% share
  return true;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function OffenseCard({ dps, stats }: OffenseCardProps) {
  const totalDps = dps.total_dps ?? dps.dps ?? 0;
  const hitDps = dps.dps ?? 0;
  const critChance = stats.crit_chance ?? 0;            // fraction 0..1
  const critMultiplier = stats.crit_multiplier ?? 0;    // e.g. 2.0 ==> 200%
  const eas = dps.effective_attack_speed ?? 0;

  return (
    <section
      data-testid="offense-card"
      className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0"
    >
      <header className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-3 shrink-0">
        <span className="font-mono text-xs uppercase tracking-widest text-forge-amber">
          Offense
        </span>
      </header>
      <div className="p-4 flex flex-col">
        <Row
          testId="offense-row-total-dps"
          label={statLabel("total_dps")}
          value={fmtNumber(totalDps)}
          tier={getBenchmarkTier("total_dps", totalDps)}
        />
        <Row
          testId="offense-row-hit-dps"
          label={statLabel("hit_dps")}
          value={fmtNumber(hitDps)}
        />
        {hasMeaningfulAilments(dps) && (
          <Row
            testId="offense-row-ailment-dps"
            label={statLabel("ailment_dps")}
            value={fmtNumber(dps.ailment_dps)}
          />
        )}
        <Row
          testId="offense-row-crit-chance"
          label={statLabel("crit_chance")}
          value={fmtPctFromFraction(critChance)}
          tier={getBenchmarkTier("crit_chance", critChance)}
        />
        <Row
          testId="offense-row-crit-multiplier"
          label={statLabel("crit_multiplier")}
          // Multiplier is presented as a percentage per the phase-3 prompt
          // (e.g. 2.0 × ==> 200 %). fmtPctFromFraction accepts a 0..1
          // fraction, so divide by 1 via `*100` semantics — but the engine
          // gives us the multiplier directly, so just render the percent.
          value={
            critMultiplier > 0 ? `${(critMultiplier * 100).toFixed(1)}%` : "—"
          }
        />
        <Row
          testId="offense-row-crit-contribution"
          label={statLabel("crit_contribution_pct")}
          value={fmtPct(dps.crit_contribution_pct)}
        />
        <Row
          testId="offense-row-attack-speed"
          label={statLabel("effective_attack_speed")}
          value={fmtPerSecond(eas)}
        />
      </div>
    </section>
  );
}
