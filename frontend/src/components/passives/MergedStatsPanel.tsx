/**
 * MergedStatsPanel — shows passive stats, skill stats, merged totals,
 * and final resolved character stats side by side.
 *
 * Also runs automated merge validation tests.
 */

import { useMemo } from "react";
import type { StatPool } from "@/logic/statResolutionPipeline";
import {
  MERGE_VALIDATION_TESTS,
  runMergeTest,
  type MergeTestResult,
} from "@/logic/mergeCharacterStats";

interface Props {
  passiveSnapshot: Record<string, number>;
  skillSnapshot: Record<string, number>;
  mergedSnapshot: Record<string, number>;
  finalStats: StatPool;
}

export default function MergedStatsPanel({
  passiveSnapshot, skillSnapshot, mergedSnapshot, finalStats,
}: Props) {
  const testResults = useMemo<MergeTestResult[]>(
    () => MERGE_VALIDATION_TESTS.map(runMergeTest),
    [],
  );
  const allPassed = testResults.every((r) => r.passed);

  const passiveEntries = sortedEntries(passiveSnapshot);
  const skillEntries = sortedEntries(skillSnapshot);
  const mergedEntries = sortedEntries(mergedSnapshot);
  const finalEntries = Array.from(finalStats.entries())
    .filter(([, v]) => v !== 0)
    .sort(([a], [b]) => a.localeCompare(b));

  const hasSkillStats = skillEntries.length > 0;

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Unified Character Stats
        </span>
        <span className={`font-mono text-[10px] font-bold ${allPassed ? "text-green-400" : "text-red-400"}`}>
          Merge Tests: {testResults.filter((r) => r.passed).length}/{testResults.length}
        </span>
      </div>

      {/* Side-by-side: Passive | Skill | Merged */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatColumn title="Passive" entries={passiveEntries} color="text-forge-cyan" />
        <StatColumn title="Skill" entries={skillEntries} color="text-forge-amber" empty={!hasSkillStats} />
        <StatColumn title="Merged" entries={mergedEntries} color="text-forge-text" />
      </div>

      {/* Final resolved */}
      {finalEntries.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-green-400 mb-1.5">
            Final Resolved
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-0.5">
            {finalEntries.map(([key, val]) => {
              const rounded = Math.round(val * 100) / 100;
              const isDerived = key.startsWith("Derived ") || key.startsWith("Base ");
              return (
                <div key={key} className="flex justify-between gap-2 font-mono text-xs">
                  <span className={isDerived ? "text-forge-amber/70 truncate" : "text-forge-muted truncate"}>{key}</span>
                  <span className="text-forge-text font-semibold whitespace-nowrap">{rounded > 0 ? `+${rounded}` : rounded}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Merge tests */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
          Merge Pipeline Tests
        </div>
        <div className="space-y-0.5">
          {testResults.map((r) => (
            <div key={r.name} className="flex items-start gap-2 font-mono text-[10px]">
              <span className={r.passed ? "text-green-400" : "text-red-400"}>
                {r.passed ? "✓" : "✗"}
              </span>
              <span className="text-forge-muted">{r.name}</span>
              {!r.passed && <span className="text-red-400/70">{r.details}</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatColumn({ title, entries, color, empty }: {
  title: string;
  entries: [string, number][];
  color: string;
  empty?: boolean;
}) {
  return (
    <div>
      <div className={`font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1`}>
        {title}
      </div>
      {empty || entries.length === 0 ? (
        <p className="font-mono text-[10px] text-forge-dim/50">No stats</p>
      ) : (
        <div className="space-y-0.5">
          {entries.map(([key, val]) => (
            <div key={key} className="flex justify-between gap-1 font-mono text-[10px]">
              <span className="text-forge-muted truncate">{key}</span>
              <span className={`${color} font-semibold whitespace-nowrap`}>
                {val > 0 ? `+${val}` : val}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function sortedEntries(obj: Record<string, number>): [string, number][] {
  return Object.entries(obj)
    .filter(([, v]) => v !== 0)
    .sort(([a], [b]) => a.localeCompare(b));
}
