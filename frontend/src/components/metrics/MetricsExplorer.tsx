/**
 * N15 — Metrics Explorer
 *
 * Summary stat cards + sortable DPS breakdown table.
 */

import { useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DpsRow {
  source: string;
  total_damage: number;
  dps: number;
  hit_count: number;
  crit_count: number;
  crit_rate: number;
}

export interface MetricsExplorerProps {
  dps_breakdown: DpsRow[];
  total_damage: number;
  overall_dps: number;
  peak_dps: number;
  mean_dps: number;
  duration: number;
}

// ---------------------------------------------------------------------------
// Types for sorting
// ---------------------------------------------------------------------------

type SortKey = keyof DpsRow;
type SortDir = "asc" | "desc";

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-[#2a3050] bg-[#0d1124] px-4 py-3">
      <p className="font-mono text-[10px] uppercase tracking-widest text-[#6b7280] mb-1">{label}</p>
      <p className="font-mono text-lg font-bold text-[#f5a623]">{value}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: "source",       label: "Source" },
  { key: "total_damage", label: "Total Damage" },
  { key: "dps",          label: "DPS" },
  { key: "hit_count",    label: "Hits" },
  { key: "crit_count",   label: "Crits" },
  { key: "crit_rate",    label: "Crit Rate %" },
];

export default function MetricsExplorer({
  dps_breakdown,
  total_damage,
  overall_dps,
  peak_dps,
  mean_dps,
}: MetricsExplorerProps) {
  const [sortKey, setSortKey] = useState<SortKey>("total_damage");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  const sorted = [...dps_breakdown].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (typeof av === "string" && typeof bv === "string") {
      return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    }
    const an = av as number;
    const bn = bv as number;
    return sortDir === "asc" ? an - bn : bn - an;
  });

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4 space-y-4">
      <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280]">
        Metrics Explorer
      </p>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Total Damage"  value={total_damage.toLocaleString()} />
        <StatCard label="Overall DPS"   value={overall_dps.toLocaleString(undefined, { maximumFractionDigits: 1 })} />
        <StatCard label="Peak DPS"      value={peak_dps.toLocaleString(undefined, { maximumFractionDigits: 1 })} />
        <StatCard label="Mean DPS"      value={mean_dps.toLocaleString(undefined, { maximumFractionDigits: 1 })} />
      </div>

      {/* Sortable table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-[#2a3050]">
              {COLUMNS.map(({ key, label }) => (
                <th
                  key={key}
                  onClick={() => handleSort(key)}
                  className="py-2 px-3 font-mono text-[11px] uppercase tracking-widest text-[#6b7280] cursor-pointer select-none hover:text-[#f5a623] whitespace-nowrap"
                >
                  {label}
                  {sortKey === key && (
                    <span className="ml-1 text-[#f5a623]">
                      {sortDir === "asc" ? "↑" : "↓"}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, i) => (
              <tr
                key={row.source}
                className={i % 2 === 0 ? "bg-[#10152a]" : "bg-[#0d1124]"}
              >
                <td className="py-1.5 px-3 font-mono text-xs text-[#c8d0e0]">{row.source}</td>
                <td className="py-1.5 px-3 font-mono text-xs text-[#c8d0e0]">
                  {row.total_damage.toLocaleString()}
                </td>
                <td className="py-1.5 px-3 font-mono text-xs text-[#c8d0e0]">
                  {row.dps.toLocaleString(undefined, { maximumFractionDigits: 1 })}
                </td>
                <td className="py-1.5 px-3 font-mono text-xs text-[#c8d0e0]">
                  {row.hit_count.toLocaleString()}
                </td>
                <td className="py-1.5 px-3 font-mono text-xs text-[#c8d0e0]">
                  {row.crit_count.toLocaleString()}
                </td>
                <td className="py-1.5 px-3 font-mono text-xs text-[#c8d0e0]">
                  {(row.crit_rate * 100).toLocaleString(undefined, { maximumFractionDigits: 1 })}%
                </td>
              </tr>
            ))}
            {sorted.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="py-6 text-center font-mono text-sm text-[#6b7280]"
                >
                  No data
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
