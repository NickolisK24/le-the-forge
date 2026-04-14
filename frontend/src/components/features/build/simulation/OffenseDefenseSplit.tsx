/**
 * OffenseDefenseSplit — side-by-side Offense / Defense stat cards.
 *
 * Each row displays a human label, the value, and a coloured dot
 * indicating where the value falls against an approximate benchmark.
 * On mobile the two cards stack into a single column.
 */

import { Panel } from "@/components/ui";
import type { DPSResult, DefenseResult } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";
import {
  getBenchmarkTier,
  BENCHMARK_COLORS,
  BENCHMARK_DISCLAIMER,
  type BenchmarkTier,
} from "@/constants/statBenchmarks";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(Math.round(n));
}

function fmtPct(n: number): string {
  return `${n.toFixed(1)}%`;
}

function fmtPctFromFraction(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function fmtMultiplier(n: number): string {
  return `${n.toFixed(2)}×`;
}

// ---------------------------------------------------------------------------
// Stat row
// ---------------------------------------------------------------------------

interface StatRowProps {
  label: string;
  value: string;
  tier?: BenchmarkTier;
  /** Render a progress bar below the row (used for survivability). */
  progress?: { value: number; max: number };
}

function StatRow({ label, value, tier, progress }: StatRowProps) {
  const dotColor = tier ? BENCHMARK_COLORS[tier] : undefined;

  return (
    <div className="py-1.5 border-b border-forge-border/30 last:border-b-0">
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
          <span className="font-body text-xs text-forge-muted truncate">{label}</span>
        </div>
        <span className="font-mono text-xs text-forge-text tabular-nums shrink-0">
          {value}
        </span>
      </div>
      {progress && (
        <div className="mt-1.5 h-1 rounded-full bg-forge-surface2 overflow-hidden">
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
// Offense card
// ---------------------------------------------------------------------------

function OffenseCard({ dps, stats }: { dps: DPSResult; stats: Record<string, number> }) {
  const totalDps = dps.total_dps ?? dps.dps ?? 0;
  const critChance = stats.crit_chance ?? 0;          // fraction 0–1
  const critMultiplier = stats.crit_multiplier ?? 0;  // e.g. 2.0

  return (
    <Panel title="Offense">
      <div className="flex flex-col">
        <StatRow
          label={statLabel("total_dps")}
          value={fmt(totalDps)}
          tier={getBenchmarkTier("total_dps", totalDps)}
        />
        <StatRow
          label="Hit Damage DPS"
          value={fmt(dps.dps)}
        />
        {dps.ailment_dps > 0 && (
          <StatRow
            label={statLabel("ailment_dps")}
            value={fmt(dps.ailment_dps)}
          />
        )}
        <StatRow
          label={statLabel("effective_attack_speed")}
          value={`${dps.effective_attack_speed.toFixed(2)}/s`}
        />
        <StatRow
          label={statLabel("crit_chance")}
          value={fmtPctFromFraction(critChance)}
          tier={getBenchmarkTier("crit_chance", critChance)}
        />
        <StatRow
          label={statLabel("crit_multiplier")}
          value={critMultiplier > 0 ? fmtMultiplier(critMultiplier) : "—"}
        />
        <StatRow
          label={statLabel("crit_contribution_pct")}
          value={fmtPct(dps.crit_contribution_pct)}
        />
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Defense card
// ---------------------------------------------------------------------------

function DefenseCard({ def }: { def: DefenseResult }) {
  return (
    <Panel title="Defense">
      <div className="flex flex-col">
        <StatRow
          label={statLabel("max_health")}
          value={fmt(def.max_health)}
        />
        <StatRow
          label={statLabel("effective_hp")}
          value={fmt(def.effective_hp)}
          tier={getBenchmarkTier("effective_hp", def.effective_hp)}
        />
        {def.ward_buffer > 0 && (
          <StatRow
            label={statLabel("ward_buffer")}
            value={fmt(def.ward_buffer)}
          />
        )}
        <StatRow
          label={statLabel("armor_mitigation_pct")}
          value={fmtPct(def.armor_reduction_pct)}
          tier={getBenchmarkTier("armor_mitigation_pct", def.armor_reduction_pct)}
        />
        <StatRow
          label={statLabel("avg_resistance")}
          value={fmtPct(def.avg_resistance)}
          tier={getBenchmarkTier("avg_resistance", def.avg_resistance)}
        />
        {def.dodge_chance_pct > 0 && (
          <StatRow
            label={statLabel("dodge_chance_pct")}
            value={fmtPct(def.dodge_chance_pct)}
            tier={getBenchmarkTier("dodge_chance_pct", def.dodge_chance_pct)}
          />
        )}
        <StatRow
          label={statLabel("survivability_score")}
          value={`${def.survivability_score} / 100`}
          tier={getBenchmarkTier("survivability_score", def.survivability_score)}
          progress={{ value: def.survivability_score, max: 100 }}
        />
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------

interface OffenseDefenseSplitProps {
  dps: DPSResult;
  defense: DefenseResult;
  stats: Record<string, number>;
}

export default function OffenseDefenseSplit({ dps, defense, stats }: OffenseDefenseSplitProps) {
  return (
    <div className="flex flex-col gap-1">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <OffenseCard dps={dps} stats={stats} />
        <DefenseCard def={defense} />
      </div>
      <p className="font-mono text-[10px] italic text-forge-dim px-1">
        {BENCHMARK_DISCLAIMER}
      </p>
    </div>
  );
}
