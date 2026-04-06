/**
 * ResolutionPipelineViewer — shows stat values at each pipeline stage.
 *
 * Displays: FLAT → PERCENT → DERIVED → FINAL
 * Plus conversion trace and resolution test results.
 */

import { useMemo } from "react";
import type { ResolutionSnapshot } from "@/logic/debugStatResolution";
import {
  RESOLUTION_TESTS,
  runResolutionTest,
} from "@/logic/debugStatResolution";

interface Props {
  snapshot: ResolutionSnapshot;
}

export default function ResolutionPipelineViewer({ snapshot }: Props) {
  const testResults = useMemo(() => RESOLUTION_TESTS.map(runResolutionTest), []);
  const allPassed = testResults.every((r) => r.passed);

  // Collect all stat IDs across stages
  const allStatIds = new Set<string>();
  for (const key of Object.keys(snapshot.afterFlat)) allStatIds.add(key);
  for (const key of Object.keys(snapshot.afterPercent)) allStatIds.add(key);
  for (const key of Object.keys(snapshot.afterDerived)) allStatIds.add(key);
  const sortedStats = Array.from(allStatIds).sort();

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Resolution Pipeline
        </span>
        <div className="flex items-center gap-3">
          <span className={`font-mono text-[10px] ${snapshot.orderValid ? "text-green-400" : "text-yellow-400"}`}>
            Order: {snapshot.orderValid ? "Valid" : "Issues"}
          </span>
          <span className={`font-mono text-[10px] font-bold ${allPassed ? "text-green-400" : "text-red-400"}`}>
            Tests: {testResults.filter((r) => r.passed).length}/{testResults.length}
          </span>
        </div>
      </div>

      {/* Stage table */}
      {sortedStats.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-[10px]">
            <thead>
              <tr className="border-b border-forge-border">
                <th className="text-left py-1 pr-3 text-forge-dim">Stat</th>
                <th className="text-right py-1 px-2 text-forge-muted">Flat</th>
                <th className="text-right py-1 px-2 text-forge-cyan">+Percent</th>
                <th className="text-right py-1 px-2 text-forge-amber">+Derived</th>
                <th className="text-right py-1 pl-2 text-forge-text font-bold">Final</th>
              </tr>
            </thead>
            <tbody>
              {sortedStats.map((stat) => (
                <tr key={stat} className="border-b border-forge-border/30">
                  <td className="py-0.5 pr-3 text-forge-muted truncate max-w-[140px]">{stat}</td>
                  <td className="py-0.5 px-2 text-right text-forge-muted">{fmtStage(snapshot.afterFlat[stat])}</td>
                  <td className="py-0.5 px-2 text-right text-forge-cyan">{fmtStage(snapshot.afterPercent[stat])}</td>
                  <td className="py-0.5 px-2 text-right text-forge-amber">{fmtStage(snapshot.afterDerived[stat])}</td>
                  <td className="py-0.5 pl-2 text-right text-forge-text font-semibold">{fmtStage(snapshot.finalStats[stat])}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-forge-dim">No stats to resolve.</p>
      )}

      {/* Conversion trace */}
      {snapshot.conversions.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-amber mb-1">
            Derived Conversions ({snapshot.conversions.length})
          </div>
          {snapshot.conversions.map((c, i) => (
            <div key={i} className="font-mono text-[10px] text-forge-muted">
              <span className="text-forge-amber">{c.ruleName}</span>
              {" = "}
              <span className="text-forge-dim">{c.description}</span>
              {" → "}
              <span className="text-forge-text font-semibold">{c.result > 0 ? `+${c.result}` : c.result}</span>
              <span className="text-forge-dim/50 ml-2">
                (from: {Object.entries(c.sources).map(([k, v]) => `${k}=${v}`).join(", ")})
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Circular dependency warnings */}
      {snapshot.circularDeps.length > 0 && (
        <div className="rounded bg-red-500/10 border border-red-500/20 px-3 py-2">
          <div className="font-mono text-[10px] uppercase tracking-widest text-red-400 mb-1">
            Circular Dependencies Detected
          </div>
          <div className="font-mono text-[10px] text-red-400/80">
            {snapshot.circularDeps.join(", ")}
          </div>
        </div>
      )}

      {/* Warnings */}
      {snapshot.warnings.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-yellow-400 mb-1">
            Warnings ({snapshot.warnings.length})
          </div>
          {snapshot.warnings.map((w, i) => (
            <div key={i} className="font-mono text-[10px] text-yellow-400/70">⚠ {w}</div>
          ))}
        </div>
      )}

      {/* Resolution tests */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
          Resolution Tests
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

function fmtStage(v: number | undefined): string {
  if (v === undefined || v === 0) return "—";
  return v > 0 ? `+${v}` : `${v}`;
}
