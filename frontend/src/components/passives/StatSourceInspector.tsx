/**
 * StatSourceInspector — per-source stat breakdown with merge validation.
 *
 * Shows: PASSIVE → SKILL → GEAR → MERGED in a table,
 * plus hardened merge test results and warnings.
 */

import { useMemo } from "react";
import type { StatMergeSnapshot } from "@/logic/debugStatMerge";
import {
  HARDENED_MERGE_TESTS,
  runHardenedMergeTest,
} from "@/logic/debugStatMerge";

interface Props {
  snapshot: StatMergeSnapshot;
}

export default function StatSourceInspector({ snapshot }: Props) {
  const testResults = useMemo(() => HARDENED_MERGE_TESTS.map(runHardenedMergeTest), []);
  const allPassed = testResults.every((r) => r.passed);

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Stat Source Inspector
        </span>
        <span className={`font-mono text-[10px] font-bold ${allPassed ? "text-green-400" : "text-red-400"}`}>
          Merge Tests: {testResults.filter((r) => r.passed).length}/{testResults.length}
        </span>
      </div>

      {/* Source breakdown table */}
      {snapshot.breakdown.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-[10px]">
            <thead>
              <tr className="border-b border-forge-border">
                <th className="text-left py-1 pr-4 text-forge-dim">Stat</th>
                <th className="text-right py-1 px-2 text-forge-cyan">Passive</th>
                <th className="text-right py-1 px-2 text-forge-amber">Skill</th>
                <th className="text-right py-1 px-2 text-forge-muted">Gear</th>
                <th className="text-right py-1 pl-2 text-forge-text font-bold">Merged</th>
              </tr>
            </thead>
            <tbody>
              {snapshot.breakdown.map((row) => (
                <tr key={row.statId} className="border-b border-forge-border/30">
                  <td className="py-0.5 pr-4 text-forge-muted truncate max-w-[140px]">{row.statId}</td>
                  <td className="py-0.5 px-2 text-right text-forge-cyan">{fmtVal(row.passive)}</td>
                  <td className="py-0.5 px-2 text-right text-forge-amber">{fmtVal(row.skill)}</td>
                  <td className="py-0.5 px-2 text-right text-forge-muted">{fmtVal(row.gear)}</td>
                  <td className="py-0.5 pl-2 text-right text-forge-text font-semibold">{fmtVal(row.merged)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-forge-dim">No stats from any source.</p>
      )}

      {/* Warnings */}
      {snapshot.warnings.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-yellow-400 mb-1">
            Merge Warnings ({snapshot.warnings.length})
          </div>
          {snapshot.warnings.map((w, i) => (
            <div key={i} className="font-mono text-[10px] text-yellow-400/70">⚠ {w}</div>
          ))}
        </div>
      )}

      {/* Merge tests */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
          Hardened Merge Tests
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

function fmtVal(v: number): string {
  if (v === 0) return "—";
  return v > 0 ? `+${v}` : `${v}`;
}
