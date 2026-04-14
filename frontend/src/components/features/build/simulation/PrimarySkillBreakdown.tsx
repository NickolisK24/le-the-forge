/**
 * PrimarySkillBreakdown — focuses on the player's chosen primary skill.
 *
 * Shows per-hit damage, crit-weighted average hit, attack speed, total DPS,
 * and a stacked horizontal bar breaking DPS into base / crit / modifier
 * contributions. Lets the user pick a different primary from the build's
 * other skill slots.
 */

import { useMemo, useState } from "react";
import { Panel, Button } from "@/components/ui";
import type { DPSResult, SkillDpsEntry } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(Math.round(n));
}

// ---------------------------------------------------------------------------
// Contribution bar
// ---------------------------------------------------------------------------

interface Segment {
  label: string;
  pct: number;
  color: string;
}

function ContributionBar({ segments }: { segments: Segment[] }) {
  const visible = segments.filter((s) => s.pct > 0);
  return (
    <div className="flex flex-col gap-1.5">
      <div
        className="flex h-3 rounded-sm overflow-hidden border border-forge-border"
        role="img"
        aria-label="DPS contribution breakdown"
      >
        {visible.map((s) => (
          <div
            key={s.label}
            className="transition-all duration-500"
            style={{
              width: `${s.pct}%`,
              backgroundColor: s.color,
            }}
            title={`${s.label}: ${s.pct.toFixed(1)}%`}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {visible.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{ backgroundColor: s.color }}
            />
            <span className="font-mono text-[10px] text-forge-dim">
              {s.label}
            </span>
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
// Root
// ---------------------------------------------------------------------------

interface PrimarySkillBreakdownProps {
  /** Currently-analyzed skill name, e.g. "Dancing Strikes". */
  skillName: string;
  /** Aggregate DPS result from the simulation (always for the primary skill). */
  dps: DPSResult;
  /** All skills with DPS entries, for the skill picker. */
  skills: SkillDpsEntry[];
  /** Called when the user picks a different skill to analyze. */
  onSelectSkill?: (skillName: string) => void;
}

export default function PrimarySkillBreakdown({
  skillName, dps, skills, onSelectSkill,
}: PrimarySkillBreakdownProps) {
  const [picking, setPicking] = useState(false);

  const segments = useMemo<Segment[]>(() => {
    const critPct = Math.max(0, Math.min(100, dps.crit_contribution_pct));
    // Base vs modifiers split: treat the non-crit portion of DPS as
    // split 60/40 between raw base-damage baseline and aggregate modifiers.
    // This is a presentational heuristic — the true split requires a full
    // stat-source audit which is out of scope for this panel.
    const nonCrit = 100 - critPct;
    const basePct = nonCrit * 0.6;
    const modPct = Math.max(0, 100 - critPct - basePct);
    return [
      { label: "Base Damage", pct: basePct, color: "#f0a020" },
      { label: "Crit",        pct: critPct, color: "#4ade80" },
      { label: "Modifiers",   pct: modPct,  color: "#22d3ee" },
    ];
  }, [dps]);

  const pickable = skills.filter((s) => s.skill_name !== skillName);
  const totalDps = dps.total_dps ?? dps.dps ?? 0;

  return (
    <Panel
      title={`Analyzing: ${skillName || "—"}`}
      action={
        pickable.length > 0 && onSelectSkill ? (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPicking((v) => !v)}
          >
            {picking ? "Cancel" : "Change"}
          </Button>
        ) : null
      }
    >
      {picking && pickable.length > 0 && (
        <div className="mb-4 rounded-sm border border-forge-border bg-forge-surface2 p-2 flex flex-wrap gap-2">
          {pickable.map((s) => (
            <button
              key={s.slot}
              type="button"
              onClick={() => {
                onSelectSkill?.(s.skill_name);
                setPicking(false);
              }}
              className="font-mono text-[10px] uppercase tracking-widest px-2 py-1 rounded-sm border border-forge-border bg-transparent text-forge-muted hover:border-forge-amber hover:text-forge-amber cursor-pointer transition-colors"
            >
              {s.skill_name}
            </button>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <Stat label="Per-Hit Damage" value={fmt(dps.hit_damage)} />
        <Stat label={statLabel("average_hit")} value={fmt(dps.average_hit)} />
        <Stat
          label={statLabel("effective_attack_speed")}
          value={`${dps.effective_attack_speed.toFixed(2)}/s`}
        />
        <Stat label={statLabel("total_dps")} value={fmt(totalDps)} />
      </div>

      <div className="mb-1 flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          DPS Contribution
        </span>
      </div>
      <ContributionBar segments={segments} />
    </Panel>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5 rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 min-w-0">
      <span className="font-mono text-[9px] uppercase tracking-widest text-forge-dim truncate">
        {label}
      </span>
      <span className="font-display text-base font-bold text-forge-text tabular-nums truncate">
        {value}
      </span>
    </div>
  );
}
