import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "@/lib/api";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import type { GearUpgradeResponse, GearUpgradeCandidate } from "@/types";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface GearUpgradePanelProps {
  slug: string;
}

// ---------------------------------------------------------------------------
// Color tokens
// ---------------------------------------------------------------------------

const C = {
  amber:  "#f0a020",
  cyan:   "#22d3ee",
  green:  "#4ade80",
  red:    "#f87171",
  muted:  "#6b7280",
  text:   "#e5e7eb",
};

const SLOT_OPTIONS = [
  { value: "", label: "All Slots" },
  { value: "helmet", label: "Helmet" },
  { value: "body", label: "Body" },
  { value: "gloves", label: "Gloves" },
  { value: "boots", label: "Boots" },
  { value: "belt", label: "Belt" },
  { value: "amulet", label: "Amulet" },
  { value: "ring1", label: "Ring 1" },
  { value: "ring2", label: "Ring 2" },
  { value: "relic", label: "Relic" },
  { value: "weapon", label: "Weapon" },
  { value: "off_hand", label: "Off Hand" },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function GearUpgradePanel({ slug }: GearUpgradePanelProps) {
  const [slot, setSlot] = useState("");

  const query = useQuery({
    queryKey: ["analysis", "gear", slug, slot],
    queryFn: async () => {
      const res = await analysisApi.gearUpgrades(slug, slot || undefined);
      return res.data;
    },
    enabled: Boolean(slug),
  });

  const result: GearUpgradeResponse | null | undefined = query.data;
  const topCandidates: GearUpgradeCandidate[] =
    result?.top_10_overall ?? [];

  return (
    <Panel title="Gear Upgrades" className="lg:col-span-2">
      {/* Slot filter */}
      <div className="flex items-center gap-3 mb-4">
        <select
          className="rounded bg-surface-2 border border-white/10 px-2 py-1 text-sm text-gray-200"
          value={slot}
          onChange={(e) => setSlot(e.target.value)}
        >
          {SLOT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {/* Loading */}
      {query.isLoading && (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      )}

      {/* Error */}
      {query.error && (
        <ErrorMessage
          message="Failed to load gear upgrades"
          onRetry={() => query.refetch()}
        />
      )}

      {/* Results table */}
      {result && topCandidates.length > 0 && (
        <div className="space-y-3">
          {/* Top pick */}
          <div className="text-xs text-gray-400">
            Top pick:{" "}
            <span style={{ color: C.amber }}>
              {topCandidates[0].item_name}
            </span>{" "}
            — {topCandidates[0].efficiency_score.toFixed(2)} efficiency
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="text-gray-500 border-b border-white/5">
                  <th className="text-left py-1 pr-2">#</th>
                  <th className="text-left py-1 pr-2">Item</th>
                  <th className="text-left py-1 pr-2">Slot</th>
                  <th className="text-right py-1 pr-2">DPS %</th>
                  <th className="text-right py-1 pr-2">EHP %</th>
                  <th className="text-right py-1 pr-2">FP</th>
                  <th className="text-right py-1">Eff.</th>
                </tr>
              </thead>
              <tbody>
                {topCandidates.map((c, i) => {
                  const highlight =
                    i === 0
                      ? "bg-amber-500/5"
                      : i === 1
                        ? "bg-gray-400/5"
                        : i === 2
                          ? "bg-cyan-400/5"
                          : "";
                  return (
                    <tr
                      key={`${c.item_name}-${c.rank}`}
                      className={`border-b border-white/[0.03] ${highlight}`}
                    >
                      <td className="py-1.5 pr-2 text-gray-500">{c.rank}</td>
                      <td
                        className="py-1.5 pr-2 truncate max-w-[180px]"
                        style={{ color: C.text }}
                        title={c.item_name}
                      >
                        {c.item_name}
                      </td>
                      <td className="py-1.5 pr-2 text-gray-500 capitalize">
                        {c.slot}
                      </td>
                      <td className="py-1.5 pr-2 text-right">
                        <span
                          style={{
                            color: c.dps_delta_pct >= 0 ? C.green : C.red,
                          }}
                        >
                          {c.dps_delta_pct >= 0 ? "+" : ""}
                          {c.dps_delta_pct.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-1.5 pr-2 text-right">
                        <span
                          style={{
                            color: c.ehp_delta_pct >= 0 ? C.green : C.red,
                          }}
                        >
                          {c.ehp_delta_pct >= 0 ? "+" : ""}
                          {c.ehp_delta_pct.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-1.5 pr-2 text-right text-gray-400">
                        {c.fp_cost}
                      </td>
                      <td
                        className="py-1.5 text-right"
                        style={{ color: C.amber }}
                      >
                        {c.efficiency_score.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty */}
      {!query.isLoading &&
        !query.error &&
        result &&
        topCandidates.length === 0 && (
          <div className="py-8 text-center text-sm text-gray-500">
            No upgrade candidates found
          </div>
        )}

      {!query.isLoading && !query.error && !result && (
        <div className="py-8 text-center text-sm text-gray-500">
          No gear upgrade data available
        </div>
      )}
    </Panel>
  );
}
