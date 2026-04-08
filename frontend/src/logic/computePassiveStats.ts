/**
 * computePassiveStats.ts — Aggregation engine for passive tree stat bonuses.
 *
 * Takes allocated node map + node data, produces aggregated stat totals.
 *
 * Design principles:
 *   - No hardcoded stat names — fully data-driven
 *   - Flat and percent tracked separately (not combined here)
 *   - Multi-point scaling: each modifier × allocated points
 *   - Defensive: skips nodes with no effects, clamps NaN, ignores invalid data
 *   - Pure function: no side effects, no mutation
 *
 * Future layers will handle:
 *   - Percent application (flat × (1 + percent/100))
 *   - Derived stats (e.g. health from vitality)
 *   - Conditional stats (e.g. "while dual wielding")
 *   - Tag-based filtering
 *   - Stat conversion chains
 */

import type { PassiveNode } from "@/services/passiveTreeService";
import type { AggregatedStat } from "@/types/passiveEffects";
import { extractNodeEffects } from "@/types/passiveEffects";

// ---------------------------------------------------------------------------
// Core aggregation
// ---------------------------------------------------------------------------

/**
 * Compute aggregated passive stats from allocated nodes.
 *
 * @param allocatedPoints - Map of nodeId → allocated point count
 * @param nodeById - Map of nodeId → full PassiveNode data
 * @returns Map of statId → AggregatedStat with flat and percent totals
 */
export function computePassiveStats(
  allocatedPoints: Map<string, number>,
  nodeById: Map<string, PassiveNode>,
): Map<string, AggregatedStat> {
  const stats = new Map<string, AggregatedStat>();

  for (const [nodeId, points] of allocatedPoints) {
    // Part 6: Skip invalid allocation counts
    if (points <= 0) continue;
    if (!Number.isFinite(points)) continue;

    const node = nodeById.get(nodeId);
    if (!node) continue;

    // Part 6: Skip nodes with no stats
    if (!node.stats || node.stats.length === 0) continue;

    // Extract typed effects from raw stat strings
    const effects = extractNodeEffects(node.stats);
    if (!effects) continue;

    // Part 2: Multi-point scaling — each modifier × allocated points
    for (const mod of effects.modifiers) {
      // Part 6: Skip invalid modifiers
      if (!mod.statId) continue;
      if (!Number.isFinite(mod.value)) continue;

      const scaledValue = mod.value * points;

      // Part 6: Clamp NaN after multiplication
      if (!Number.isFinite(scaledValue)) continue;

      let entry = stats.get(mod.statId);
      if (!entry) {
        entry = { statId: mod.statId, flat: 0, percent: 0 };
        stats.set(mod.statId, entry);
      }

      if (mod.type === "flat") {
        entry.flat += scaledValue;
      } else {
        entry.percent += scaledValue;
      }
    }
  }

  return stats;
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

/**
 * Format an aggregated stat for display.
 *
 * Examples:
 *   { statId: "Armor", flat: 60, percent: 0 }  →  "+60"
 *   { statId: "Health", flat: 0, percent: 15 }  →  "+15%"
 *   { statId: "Damage", flat: 10, percent: 20 } →  "+10, +20%"
 */
export function formatStat(stat: AggregatedStat): string {
  const parts: string[] = [];
  if (stat.flat !== 0) {
    parts.push(stat.flat > 0 ? `+${stat.flat}` : `${stat.flat}`);
  }
  if (stat.percent !== 0) {
    parts.push(stat.percent > 0 ? `+${stat.percent}%` : `${stat.percent}%`);
  }
  return parts.join(", ") || "0";
}

/**
 * Sort stats for display — alphabetical by statId.
 */
export function sortedStats(stats: Map<string, AggregatedStat>): AggregatedStat[] {
  return Array.from(stats.values()).sort((a, b) => a.statId.localeCompare(b.statId));
}
