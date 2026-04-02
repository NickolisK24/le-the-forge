/**
 * G15 — Rotation Results Panel
 *
 * Displays summary stats and per-skill damage breakdown from a rotation result.
 */

import type { RotationResult } from "@/services/rotationApi";

interface Props {
  result:    RotationResult | null;
  isLoading: boolean;
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col">
      <span className="text-xs uppercase tracking-wide text-forge-muted">{label}</span>
      <span className="font-mono text-sm font-semibold text-forge-text">
        {typeof value === "number" ? value.toFixed(2) : value}
      </span>
    </div>
  );
}

export default function RotationResultsPanel({ result, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="animate-pulse space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-4 rounded bg-forge-border/30" />
        ))}
      </div>
    );
  }

  if (!result) return null;

  const m = result.rotation_metrics;
  const skillIds = Object.keys(m.damage_by_skill).sort(
    (a, b) => (m.damage_by_skill[b] ?? 0) - (m.damage_by_skill[a] ?? 0)
  );

  return (
    <div className="space-y-6">
      {/* Summary row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Total Damage"  value={result.total_damage.toFixed(0)} />
        <Stat label="DPS"           value={result.dps.toFixed(1)} />
        <Stat label="Total Casts"   value={result.total_casts} />
        <Stat label="Uptime"        value={`${(m.uptime_fraction * 100).toFixed(1)}%`} />
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Idle Time (s)"    value={m.idle_time.toFixed(2)} />
        <Stat label="Efficiency"       value={`${(m.efficiency * 100).toFixed(1)}%`} />
        <Stat label="Avg Interval (s)" value={m.avg_cast_interval.toFixed(2)} />
        <Stat label="Duration Used (s)" value={m.duration_used.toFixed(2)} />
      </div>

      {/* Per-skill breakdown */}
      {skillIds.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs uppercase tracking-wide text-forge-muted">
            Damage by Skill
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-forge-border text-xs uppercase text-forge-muted">
                <th className="py-1 text-left">Skill</th>
                <th className="py-1 text-right">Casts</th>
                <th className="py-1 text-right">Damage</th>
                <th className="py-1 text-right">Share</th>
              </tr>
            </thead>
            <tbody>
              {skillIds.map((sid) => {
                const dmg   = m.damage_by_skill[sid] ?? 0;
                const count = m.cast_counts[sid] ?? 0;
                const share = result.total_damage > 0
                  ? ((dmg / result.total_damage) * 100).toFixed(1)
                  : "0.0";
                return (
                  <tr key={sid} className="border-b border-forge-border/30">
                    <td className="py-1.5 font-mono text-forge-text">{sid}</td>
                    <td className="py-1.5 text-right font-mono text-forge-muted">{count}</td>
                    <td className="py-1.5 text-right font-mono text-forge-text">{dmg.toFixed(0)}</td>
                    <td className="py-1.5 text-right font-mono text-forge-muted">{share}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
