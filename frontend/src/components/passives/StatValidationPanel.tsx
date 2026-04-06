/**
 * StatValidationPanel — dev-only panel showing raw snapshot,
 * resolved character stats, and pipeline validation test results.
 */

import { useMemo } from "react";
import { VALIDATION_TESTS, runStatTest, type StatTestResult } from "@/logic/resolveCharacterStats";

interface Props {
  snapshot: Record<string, number>;
  resolvedCharStats: Record<string, number>;
}

export default function StatValidationPanel({ snapshot, resolvedCharStats }: Props) {
  // Run built-in validation tests
  const testResults = useMemo(() => VALIDATION_TESTS.map(runStatTest), []);
  const allPassed = testResults.every((r) => r.passed);

  const snapshotEntries = Object.entries(snapshot).sort(([a], [b]) => a.localeCompare(b));
  const resolvedEntries = Object.entries(resolvedCharStats).sort(([a], [b]) => a.localeCompare(b));

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Stat Pipeline Validation
        </span>
        <span className={`font-mono text-[10px] font-bold ${allPassed ? "text-green-400" : "text-red-400"}`}>
          Tests: {testResults.filter((r) => r.passed).length}/{testResults.length} passed
        </span>
      </div>

      {/* Raw snapshot */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1.5">
          Raw Passive Snapshot
        </div>
        {snapshotEntries.length === 0 ? (
          <p className="font-mono text-xs text-forge-dim">No passive stats allocated</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-0.5">
            {snapshotEntries.map(([key, val]) => (
              <div key={key} className="flex justify-between gap-2 font-mono text-xs">
                <span className="text-forge-muted truncate">{key}</span>
                <span className="text-forge-cyan font-semibold whitespace-nowrap">
                  {val > 0 ? `+${val}` : val}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resolved character stats */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-amber mb-1.5">
          Final Character Stats
        </div>
        {resolvedEntries.length === 0 ? (
          <p className="font-mono text-xs text-forge-dim">No resolved stats</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-0.5">
            {resolvedEntries.map(([key, val]) => {
              const isDerived = key.startsWith("Derived ") || key.startsWith("Base ");
              return (
                <div key={key} className="flex justify-between gap-2 font-mono text-xs">
                  <span className={isDerived ? "text-forge-amber/70 truncate" : "text-forge-muted truncate"}>
                    {key}
                  </span>
                  <span className="text-forge-text font-semibold whitespace-nowrap">{val}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Validation tests */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1.5">
          Pipeline Tests
        </div>
        <div className="space-y-0.5">
          {testResults.map((r) => (
            <div key={r.name} className="flex items-start gap-2 font-mono text-xs">
              <span className={r.passed ? "text-green-400" : "text-red-400"}>
                {r.passed ? "✓" : "✗"}
              </span>
              <span className="text-forge-muted">{r.name}</span>
              {!r.passed && (
                <span className="text-red-400/70 text-[10px]">{r.details}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
