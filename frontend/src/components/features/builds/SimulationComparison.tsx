/**
 * SimulationComparison — fetches and displays side-by-side simulation results
 * for two builds. Rendered below the existing stat diff in BuildComparisonPage.
 */

import { useQuery } from "@tanstack/react-query";
import { compareApi } from "@/lib/api";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import type { ComparisonResult } from "@/types";

const C = {
  amber: "#f0a020",
  green: "#4ade80",
  red: "#f87171",
  cyan: "#22d3ee",
  dim: "#5a6080",
};

function WinnerBadge({ winner, side }: { winner: string; side: "a" | "b" }) {
  if (winner === "tie" || winner !== side) return null;
  return (
    <span
      className="inline-block ml-2 px-1.5 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider"
      style={{ background: `${C.green}20`, color: C.green, border: `1px solid ${C.green}40` }}
    >
      Winner
    </span>
  );
}

function StatCard({
  label,
  valueA,
  valueB,
  winner,
  format,
}: {
  label: string;
  valueA: number;
  valueB: number;
  winner: string;
  format?: (v: number) => string;
}) {
  const fmt = format ?? ((v: number) => v.toLocaleString(undefined, { maximumFractionDigits: 0 }));
  return (
    <div className="flex items-center justify-between py-2 border-b border-forge-border/30 last:border-b-0">
      <div className="flex-1 text-right pr-4">
        <span
          className="font-mono text-sm tabular-nums"
          style={{ color: winner === "a" ? C.green : winner === "b" ? C.dim : undefined }}
        >
          {fmt(valueA)}
        </span>
        <WinnerBadge winner={winner} side="a" />
      </div>
      <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim text-center w-36 shrink-0">
        {label}
      </div>
      <div className="flex-1 pl-4">
        <WinnerBadge winner={winner} side="b" />
        <span
          className="font-mono text-sm tabular-nums"
          style={{ color: winner === "b" ? C.green : winner === "a" ? C.dim : undefined }}
        >
          {fmt(valueB)}
        </span>
      </div>
    </div>
  );
}

function OverallWinnerBanner({ data }: { data: ComparisonResult }) {
  const winnerName =
    data.overall_winner === "a" ? data.name_a : data.overall_winner === "b" ? data.name_b : null;

  return (
    <div
      className="rounded border px-6 py-4 text-center mb-4"
      style={{
        borderColor: winnerName ? `${C.amber}50` : `${C.dim}30`,
        background: winnerName ? `${C.amber}08` : undefined,
      }}
    >
      <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
        Overall Winner (60% DPS / 40% EHP)
      </div>
      <div
        className="font-display text-xl font-bold"
        style={{ color: winnerName ? C.amber : C.dim }}
      >
        {winnerName ?? "Tie"}
      </div>
      <div className="font-mono text-xs text-forge-dim mt-1">
        Score: {data.overall_score_a} vs {data.overall_score_b}
      </div>
    </div>
  );
}

function SkillComparisonSection({ data }: { data: ComparisonResult }) {
  const { skill_comparison: sc } = data;
  return (
    <Panel title="Skill Comparison" className="mt-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-2">
            {data.name_a}
          </div>
          {sc.skills_a.map((s, i) => (
            <div key={i} className="font-body text-sm text-forge-text py-1">
              <span
                className="mr-1"
                style={{ color: sc.shared.includes(s.skill_name) ? C.cyan : undefined }}
              >
                {s.skill_name}
              </span>
              <span className="font-mono text-[11px] text-forge-dim">{s.points_allocated}pts</span>
            </div>
          ))}
          {sc.skills_a.length === 0 && (
            <span className="font-mono text-xs text-forge-dim">No skills</span>
          )}
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-2">
            {data.name_b}
          </div>
          {sc.skills_b.map((s, i) => (
            <div key={i} className="font-body text-sm text-forge-text py-1">
              <span
                className="mr-1"
                style={{ color: sc.shared.includes(s.skill_name) ? C.cyan : undefined }}
              >
                {s.skill_name}
              </span>
              <span className="font-mono text-[11px] text-forge-dim">{s.points_allocated}pts</span>
            </div>
          ))}
          {sc.skills_b.length === 0 && (
            <span className="font-mono text-xs text-forge-dim">No skills</span>
          )}
        </div>
      </div>
      {sc.shared.length > 0 && (
        <div className="mt-3 pt-3 border-t border-forge-border/30">
          <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
            Shared:{" "}
          </span>
          <span className="font-body text-sm" style={{ color: C.cyan }}>
            {sc.shared.join(", ")}
          </span>
        </div>
      )}
    </Panel>
  );
}

const pctFmt = (v: number) => `${v.toFixed(1)}%`;

export default function SimulationComparison({
  slugA,
  slugB,
}: {
  slugA: string;
  slugB: string;
}) {
  const { data: res, isLoading, isError } = useQuery({
    queryKey: ["compare", "simulation", slugA, slugB],
    queryFn: () => compareApi.compare(slugA, slugB),
    enabled: Boolean(slugA) && Boolean(slugB) && slugA !== slugB,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  if (!slugA || !slugB || slugA === slugB) return null;

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    );
  }

  if (isError || !res?.data) {
    return (
      <ErrorMessage
        title="Simulation comparison unavailable"
        message="Could not run simulation for one or both builds. They may be missing skills or class data."
      />
    );
  }

  const data = res.data;

  return (
    <div className="mt-8">
      <div className="font-display text-lg font-bold text-forge-amber tracking-wider mb-4">
        Simulation Comparison
      </div>

      <OverallWinnerBanner data={data} />

      {/* DPS Comparison */}
      <Panel title="DPS Comparison" className="mb-4">
        <StatCard label="Total DPS" valueA={data.dps.total_dps_a} valueB={data.dps.total_dps_b} winner={data.dps.winner} />
        <StatCard label="Raw DPS" valueA={data.dps.raw_dps_a} valueB={data.dps.raw_dps_b} winner={data.dps.winner} />
        <StatCard label="Crit Contribution" valueA={data.dps.crit_contribution_a} valueB={data.dps.crit_contribution_b} winner={data.dps.winner} format={pctFmt} />
        <StatCard label="Ailment DPS" valueA={data.dps.ailment_dps_a} valueB={data.dps.ailment_dps_b} winner={data.dps.winner} />
      </Panel>

      {/* EHP Comparison */}
      <Panel title="EHP Comparison" className="mb-4">
        <StatCard label="Effective HP" valueA={data.ehp.effective_hp_a} valueB={data.ehp.effective_hp_b} winner={data.ehp.winner} />
        <StatCard label="Max Health" valueA={data.ehp.max_health_a} valueB={data.ehp.max_health_b} winner={data.ehp.winner} />
        <StatCard label="Armor Reduction" valueA={data.ehp.armor_reduction_pct_a} valueB={data.ehp.armor_reduction_pct_b} winner={data.ehp.winner} format={pctFmt} />
        <StatCard label="Avg Resistance" valueA={data.ehp.avg_resistance_a} valueB={data.ehp.avg_resistance_b} winner={data.ehp.winner} format={pctFmt} />
        <StatCard label="Survivability" valueA={data.ehp.survivability_score_a} valueB={data.ehp.survivability_score_b} winner={data.ehp.winner} format={(v) => `${v}/100`} />
      </Panel>

      {/* Skills */}
      <SkillComparisonSection data={data} />
    </div>
  );
}
