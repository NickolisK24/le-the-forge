/**
 * debugStatSnapshot.ts — Create a flat stat dictionary from allocated passive nodes.
 *
 * Produces the RAW PASSIVE OUTPUT — a simple Record<string, number>
 * where each stat is the total from all allocated nodes × points.
 *
 * This is the input to the derived stat resolver.
 */

import type { PassiveNode } from "@/services/passiveTreeService";
import { parseStatValue } from "@/types/passiveEffects";

/**
 * Create a flat snapshot of all passive stat contributions.
 *
 * For each allocated node, parses its stats and multiplies by allocated points.
 * Returns a flat dictionary (not split by flat/percent — combined for display).
 *
 * Format: { "Strength": 25, "Increased Damage%": 48, ... }
 * Percent stats are suffixed with "%" to distinguish them.
 */
export function createPassiveStatSnapshot(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): Record<string, number> {
  const snapshot: Record<string, number> = {};

  for (const [nodeId, points] of allocatedPoints) {
    if (points <= 0 || !Number.isFinite(points)) continue;

    const node = nodeById.get(nodeId);
    if (!node?.stats?.length) continue;

    for (const stat of node.stats) {
      const mod = parseStatValue(stat.key, stat.value);
      if (!mod) continue;

      const key = mod.type === "percent" ? `${mod.statId}%` : mod.statId;
      const scaled = mod.value * points;

      if (!Number.isFinite(scaled)) continue;

      snapshot[key] = (snapshot[key] ?? 0) + scaled;
    }
  }

  return snapshot;
}
