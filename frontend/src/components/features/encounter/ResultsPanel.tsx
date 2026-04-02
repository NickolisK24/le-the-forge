/**
 * D8 — Results Panel
 *
 * Displays simulation results: total damage, DPS, elapsed time, kills, casts.
 */

import type { EncounterResult } from "@/services/encounterApi";

interface Props {
  result: EncounterResult | null;
  isLoading: boolean;
}

function fmt(n: number, decimals = 0): string {
  return n.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-forge-border bg-forge-surface px-4 py-3">
      <div className="text-xs text-forge-muted uppercase tracking-wide mb-1">{label}</div>
      <div className="text-lg font-bold text-forge-text">{value}</div>
    </div>
  );
}

export default function ResultsPanel({ result, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12 text-forge-muted text-sm">
        Simulating…
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center py-12 text-forge-muted text-sm">
        Configure your build and encounter, then press Run Simulation.
      </div>
    );
  }

  const uptimePct = result.ticks_simulated > 0
    ? ((1 - result.downtime_ticks / result.ticks_simulated) * 100).toFixed(1)
    : "100.0";

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Results
      </h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <StatCard label="Total Damage"  value={fmt(result.total_damage)} />
        <StatCard label="DPS"           value={fmt(result.dps, 1)} />
        <StatCard label="Elapsed Time"  value={`${result.elapsed_time.toFixed(2)}s`} />
        <StatCard label="Enemies Killed" value={String(result.enemies_killed)} />
        <StatCard label="Total Casts"   value={fmt(result.total_casts)} />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Ticks"         value={fmt(result.ticks_simulated)} />
        <StatCard label="Downtime Ticks" value={fmt(result.downtime_ticks)} />
        <StatCard label="Uptime"        value={`${uptimePct}%`} />
        <StatCard
          label="Active Phase"
          value={result.active_phase_id ?? "—"}
        />
      </div>

      {result.all_enemies_dead && (
        <p className="mt-3 text-sm text-green-400">All enemies defeated.</p>
      )}
    </section>
  );
}
