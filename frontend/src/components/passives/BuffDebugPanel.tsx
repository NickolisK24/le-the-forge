/**
 * BuffDebugPanel — displays active buffs/debuffs with duration, stacks, and modifiers.
 */

import type { ActiveBuff } from "@/types/buff";
import type { BuffTestResult } from "@/logic/buffManager";

interface Props {
  activeBuffs: ActiveBuff[];
  testResults: BuffTestResult[];
}

export default function BuffDebugPanel({ activeBuffs, testResults }: Props) {
  const buffs = activeBuffs.filter((b) => !b.definition.isDebuff);
  const debuffs = activeBuffs.filter((b) => b.definition.isDebuff);
  const allPassed = testResults.every((r) => r.passed);

  return (
    <div className="mt-4 rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Buffs / Debuffs
        </span>
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] text-forge-dim">
            {buffs.length} buffs · {debuffs.length} debuffs
          </span>
          <span className={`font-mono text-[10px] font-bold ${allPassed ? "text-green-400" : "text-red-400"}`}>
            Tests: {testResults.filter((r) => r.passed).length}/{testResults.length}
          </span>
        </div>
      </div>

      {/* Active buffs/debuffs */}
      {activeBuffs.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-[10px]">
            <thead>
              <tr className="border-b border-forge-border">
                <th className="text-left py-1 pr-3 text-forge-dim">Name</th>
                <th className="text-center py-1 px-2 text-forge-dim">Type</th>
                <th className="text-right py-1 px-2 text-forge-dim">Stacks</th>
                <th className="text-right py-1 px-2 text-forge-dim">Duration</th>
                <th className="text-left py-1 pl-2 text-forge-dim">Modifiers</th>
              </tr>
            </thead>
            <tbody>
              {activeBuffs.map((buff) => (
                <tr key={buff.definition.id} className="border-b border-forge-border/30">
                  <td className="py-0.5 pr-3 text-forge-muted">{buff.definition.name}</td>
                  <td className="py-0.5 px-2 text-center">
                    <span className={buff.definition.isDebuff ? "text-red-400" : "text-green-400"}>
                      {buff.definition.isDebuff ? "Debuff" : "Buff"}
                    </span>
                  </td>
                  <td className="py-0.5 px-2 text-right text-forge-amber">
                    {buff.stacks}{buff.definition.maxStacks > 1 ? `/${buff.definition.maxStacks}` : ""}
                  </td>
                  <td className="py-0.5 px-2 text-right text-forge-cyan">
                    {buff.remainingSeconds === -1 ? "∞" : `${buff.remainingSeconds.toFixed(1)}s`}
                  </td>
                  <td className="py-0.5 pl-2 text-forge-muted truncate max-w-[200px]">
                    {buff.definition.modifiers.map((m) =>
                      `${m.value > 0 ? "+" : ""}${m.value * buff.stacks}${m.type === "percent" ? "%" : ""} ${m.statId}`
                    ).join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-forge-dim">No active buffs or debuffs.</p>
      )}

      {/* Test results */}
      <div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
          Buff Engine Tests
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
