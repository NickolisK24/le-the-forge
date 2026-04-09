import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { analysisApi } from "@/lib/api";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import type { BossAnalysisResponse, BossListItem } from "@/types";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface BossEncounterPanelProps {
  slug: string;
}

// ---------------------------------------------------------------------------
// Color tokens (matches SimulationDashboard)
// ---------------------------------------------------------------------------

const C = {
  amber:  "#f0a020",
  cyan:   "#22d3ee",
  green:  "#4ade80",
  red:    "#f87171",
  muted:  "#6b7280",
  border: "rgba(255,255,255,0.08)",
  text:   "#e5e7eb",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function BossEncounterPanel({ slug }: BossEncounterPanelProps) {
  const [bossId, setBossId] = useState("boss_standard");
  const [corruption, setCorruption] = useState(0);

  const bossesQuery = useQuery({
    queryKey: ["entities", "bosses"],
    queryFn: async () => {
      const res = await analysisApi.bosses();
      return res.data ?? [];
    },
    staleTime: 24 * 60 * 60 * 1000,
  });

  const analysisQuery = useQuery({
    queryKey: ["analysis", "boss", slug, bossId, corruption],
    queryFn: async () => {
      const res = await analysisApi.boss(slug, bossId, corruption);
      return res.data;
    },
    enabled: Boolean(slug && bossId),
  });

  const bosses: BossListItem[] = bossesQuery.data ?? [];
  const result: BossAnalysisResponse | null | undefined = analysisQuery.data;

  return (
    <Panel title="Boss Encounter">
      {/* Controls */}
      <div className="flex flex-wrap gap-3 mb-4">
        <select
          className="rounded bg-surface-2 border border-white/10 px-2 py-1 text-sm text-gray-200"
          value={bossId}
          onChange={(e) => setBossId(e.target.value)}
        >
          {bosses.length === 0 && (
            <option value="boss_standard">Standard Boss</option>
          )}
          {bosses.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>

        <label className="flex items-center gap-2 text-sm text-gray-400">
          Corruption
          <input
            type="number"
            className="w-20 rounded bg-surface-2 border border-white/10 px-2 py-1 text-sm text-gray-200"
            min={0}
            max={500}
            step={100}
            value={corruption}
            onChange={(e) =>
              setCorruption(Math.max(0, Math.min(500, Number(e.target.value))))
            }
          />
        </label>
      </div>

      {/* Loading */}
      {analysisQuery.isLoading && (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      )}

      {/* Error */}
      {analysisQuery.error && (
        <ErrorMessage
          message="Failed to load boss analysis"
          onRetry={() => analysisQuery.refetch()}
        />
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Enrage warning */}
          {!result.summary.can_kill_before_enrage && (
            <div className="rounded border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
              Cannot kill before enrage — TTK{" "}
              {result.summary.total_ttk_seconds.toFixed(1)}s
            </div>
          )}

          {/* Phase timeline */}
          <div className="space-y-2">
            {result.phases.map((phase) => {
              const isImmune = phase.dps === 0 && phase.warnings.some((w) => w.includes("Immunity"));
              return (
                <div
                  key={phase.phase}
                  className="flex items-center gap-3 rounded border border-white/5 bg-white/[0.02] px-3 py-2"
                >
                  <span className="text-xs font-mono text-gray-500 w-6">
                    P{phase.phase}
                  </span>

                  {isImmune ? (
                    <span className="text-xs text-amber-400 italic flex-1">
                      Immunity Phase
                    </span>
                  ) : (
                    <>
                      {/* DPS bar */}
                      <div className="flex-1">
                        <div className="flex justify-between text-xs mb-0.5">
                          <span style={{ color: C.amber }}>
                            {phase.dps.toLocaleString()} DPS
                          </span>
                          <span className="text-gray-500">
                            {phase.ttk_seconds === Infinity
                              ? "---"
                              : `${phase.ttk_seconds.toFixed(1)}s`}
                          </span>
                        </div>
                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${Math.min(100, (phase.dps / Math.max(1, ...result.phases.map((p) => p.dps))) * 100)}%`,
                              backgroundColor: C.amber,
                            }}
                          />
                        </div>
                      </div>

                      {/* Survival */}
                      <div className="w-20 text-right">
                        <span
                          className="text-xs font-mono"
                          style={{
                            color:
                              phase.survival_score >= 70
                                ? C.green
                                : phase.survival_score >= 40
                                  ? C.amber
                                  : C.red,
                          }}
                        >
                          {phase.survival_score}/100
                        </span>
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>

          {/* Summary */}
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="rounded bg-white/[0.02] px-3 py-2">
              <div className="text-gray-500">Total TTK</div>
              <div className="text-lg" style={{ color: C.text }}>
                {result.summary.total_ttk_seconds === Infinity
                  ? "---"
                  : `${result.summary.total_ttk_seconds.toFixed(1)}s`}
              </div>
            </div>
            <div className="rounded bg-white/[0.02] px-3 py-2">
              <div className="text-gray-500">Survival</div>
              <div
                className="text-lg"
                style={{
                  color:
                    result.summary.overall_survival_score >= 70
                      ? C.green
                      : result.summary.overall_survival_score >= 40
                        ? C.amber
                        : C.red,
                }}
              >
                {result.summary.overall_survival_score}/100
              </div>
            </div>
          </div>

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <div className="text-xs text-gray-500 space-y-0.5">
              {result.warnings.map((w, i) => (
                <div key={i}>{w}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!analysisQuery.isLoading && !analysisQuery.error && !result && (
        <div className="py-8 text-center text-sm text-gray-500">
          Select a boss to analyze
        </div>
      )}
    </Panel>
  );
}
