/**
 * SkillTreeDebugPanel — simple debug display for skill tree allocation state.
 *
 * Shows: allocated nodes, points spent, stats, validation status.
 * No full rendering — just data verification.
 */

import type { SkillNode, SkillAllocationMap } from "@/types/skillTree";
import type { SkillTreeValidationResult } from "@/logic/validateSkillTree";
import { MAX_SKILL_POINTS } from "@/types/skillTree";

interface Props {
  skillName: string;
  nodes: SkillNode[];
  allocated: SkillAllocationMap;
  validation: SkillTreeValidationResult;
  stats: Record<string, number>;
}

export default function SkillTreeDebugPanel({ skillName, nodes, allocated, validation, stats }: Props) {
  const allocEntries = Array.from(allocated.entries())
    .filter(([, pts]) => pts > 0)
    .sort(([a], [b]) => a - b);

  const nodeById = new Map<number, SkillNode>();
  for (const n of nodes) nodeById.set(n.id, n);

  const statEntries = Object.entries(stats).sort(([a], [b]) => a.localeCompare(b));

  return (
    <div className="rounded border border-forge-border bg-forge-surface px-4 py-3 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-display text-sm font-bold text-forge-amber">{skillName}</span>
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs text-forge-dim">
            {validation.pointsSpent} / {MAX_SKILL_POINTS} pts
          </span>
          <span className={`font-mono text-[10px] font-bold ${validation.valid ? "text-green-400" : "text-red-400"}`}>
            {validation.valid ? "VALID" : "INVALID"}
          </span>
        </div>
      </div>

      {/* Allocated nodes */}
      {allocEntries.length > 0 ? (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
            Allocated Nodes
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-0.5">
            {allocEntries.map(([nodeId, pts]) => {
              const node = nodeById.get(nodeId);
              return (
                <div key={nodeId} className="flex justify-between gap-2 font-mono text-xs">
                  <span className="text-forge-muted truncate">{node?.name ?? `#${nodeId}`}</span>
                  <span className="text-forge-cyan font-semibold">{pts}/{node?.maxPoints ?? "?"}</span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <p className="font-mono text-xs text-forge-dim">No skill nodes allocated.</p>
      )}

      {/* Stats */}
      {statEntries.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
            Skill Stats
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-0.5">
            {statEntries.map(([key, val]) => (
              <div key={key} className="flex justify-between gap-2 font-mono text-xs">
                <span className="text-forge-muted truncate">{key}</span>
                <span className="text-forge-text font-semibold">{val > 0 ? `+${val}` : val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation errors */}
      {validation.errors.length > 0 && (
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-red-400 mb-1">
            Errors
          </div>
          {validation.errors.map((err, i) => (
            <div key={i} className="font-mono text-xs text-red-400/80">✗ {err}</div>
          ))}
        </div>
      )}
    </div>
  );
}
