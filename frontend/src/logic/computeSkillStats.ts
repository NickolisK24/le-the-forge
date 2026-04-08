/**
 * computeSkillStats.ts — Aggregate stat modifiers from allocated skill tree nodes.
 *
 * Mirrors computePassiveStats but works with the skill tree data format.
 * Stats have statName + value string (e.g. "+10%", "+55 flat").
 */

import type { SkillNode, SkillAllocationMap } from "@/types/skillTree";
import type { AggregatedStat } from "@/types/passiveEffects";
import { parseStatValue } from "@/types/passiveEffects";

/**
 * Aggregate all stat modifiers from allocated skill tree nodes.
 *
 * For each allocated node, parses its statModifiers and multiplies by points.
 * Returns Map<statId, AggregatedStat> compatible with the resolution pipeline.
 */
export function computeSkillStats(
  allocated: SkillAllocationMap,
  nodes: SkillNode[],
): Map<string, AggregatedStat> {
  const stats = new Map<string, AggregatedStat>();

  const nodeById = new Map<number, SkillNode>();
  for (const n of nodes) nodeById.set(n.id, n);

  for (const [nodeId, points] of allocated) {
    if (points <= 0 || !Number.isFinite(points)) continue;

    const node = nodeById.get(nodeId);
    if (!node) continue;

    for (const mod of node.statModifiers) {
      if (!mod.statId || !Number.isFinite(mod.value)) continue;

      const scaled = mod.value * points;
      if (!Number.isFinite(scaled)) continue;

      let entry = stats.get(mod.statId);
      if (!entry) {
        entry = { statId: mod.statId, flat: 0, percent: 0 };
        stats.set(mod.statId, entry);
      }

      if (mod.type === "flat") {
        entry.flat += scaled;
      } else {
        entry.percent += scaled;
      }
    }
  }

  return stats;
}

/**
 * Create a flat snapshot of skill tree stats for debug display.
 */
export function createSkillStatSnapshot(
  allocated: SkillAllocationMap,
  nodes: SkillNode[],
): Record<string, number> {
  const snapshot: Record<string, number> = {};

  const nodeById = new Map<number, SkillNode>();
  for (const n of nodes) nodeById.set(n.id, n);

  for (const [nodeId, points] of allocated) {
    if (points <= 0) continue;
    const node = nodeById.get(nodeId);
    if (!node) continue;

    for (const mod of node.statModifiers) {
      if (!mod.statId || !Number.isFinite(mod.value)) continue;
      const key = mod.type === "percent" ? `${mod.statId}%` : mod.statId;
      const scaled = mod.value * points;
      if (Number.isFinite(scaled)) {
        snapshot[key] = (snapshot[key] ?? 0) + scaled;
      }
    }
  }

  return snapshot;
}
