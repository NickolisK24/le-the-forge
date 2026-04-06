/**
 * ConditionalStatViewer — displays conditional modifier evaluation results.
 *
 * Shows which conditions passed/failed and what was applied/skipped.
 * Also runs built-in validation tests.
 */

import { useMemo } from "react";
import type { ConditionalEvalResult } from "@/types/conditionalStats";
import { CONDITIONAL_TESTS, runConditionalTest } from "@/logic/conditionalStatEngine";

interface Props {
  results: ConditionalEvalResult[];
}

export default function ConditionalStatViewer({ results }: Props) {
  const testResults = useMemo(() => CONDITIONAL_TESTS.map(runConditionalTest), []);
  const allPassed = testResults.every((r) => r.passed);

  const applied = results.filter((r) => r.conditionMet);
  const skipped = results.filter((r) => !r.conditionMet);

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Conditional Modifiers
        </span>
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] text-forge-dim">
            {applied.length} applied · {skipped.length} skipped
          </span>
          <span className={`font-mono text-[10px] font-bold ${allPassed ? "text-green-400" : "text-red-400"}`}>
            Tests: {testResults.filter((r) => r.passed).length}/{testResults.length}
          </span>
        </div>
      </div>

      {/* Active conditional results */}
      {results.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-[10px]">
            <thead>
              <tr className="border-b border-forge-border">
                <th className="text-left py-1 pr-3 text-forge-dim">Modifier</th>
                <th className="text-left py-1 px-2 text-forge-dim">Condition</th>
                <th className="text-center py-1 px-2 text-forge-dim">Status</th>
                <th className="text-right py-1 pl-2 text-forge-dim">Applied</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i} className="border-b border-forge-border/30">
                  <td className="py-0.5 pr-3 text-forge-muted truncate max-w-[160px]" title={r.modifier.source}>
                    {r.modifier.description}
                  </td>
                  <td className="py-0.5 px-2 text-forge-dim truncate max-w-[140px]" title={r.reason}>
                    {r.reason}
                  </td>
                  <td className="py-0.5 px-2 text-center">
                    <span className={r.conditionMet ? "text-green-400" : "text-red-400"}>
                      {r.conditionMet ? "PASS" : "FAIL"}
                    </span>
                  </td>
                  <td className="py-0.5 pl-2 text-right text-forge-text">
                    {r.conditionMet ? (
                      <span className="font-semibold">
                        {r.appliedFlat !== 0 && `${r.appliedFlat > 0 ? "+" : ""}${r.appliedFlat}`}
                        {r.appliedFlat !== 0 && r.appliedPercent !== 0 && ", "}
                        {r.appliedPercent !== 0 && `${r.appliedPercent > 0 ? "+" : ""}${r.appliedPercent}%`}
                      </span>
                    ) : (
                      <span className="text-forge-dim">Skipped</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-forge-dim">No conditional modifiers registered.</p>
      )}

      {/* Validation tests */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
          Conditional Engine Tests
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
