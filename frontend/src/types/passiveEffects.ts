/**
 * passiveEffects.ts — Type definitions for passive node stat effects.
 *
 * Designed for future extensibility:
 *   - Flat and percent modifiers
 *   - Tag-based filtering (future)
 *   - Conditional application (future)
 *   - Stat conversion chains (future)
 *   - Skill-specific scaling (future)
 *
 * Stat names are never hardcoded — all driven by data.
 */

// ---------------------------------------------------------------------------
// Core modifier types
// ---------------------------------------------------------------------------

/** A single stat modification applied by a passive node per allocated point. */
export interface PassiveStatModifier {
  /** Internal stat identifier (e.g. "Armor", "Intelligence", "Necrotic Resistance") */
  statId: string;
  /** Whether this is a flat addition or a percentage modifier */
  type: "flat" | "percent";
  /** Numeric value per point (always positive — direction is implicit in the stat) */
  value: number;
}

/** The complete set of effects produced by a passive node. */
export interface PassiveNodeEffect {
  /** Stat modifiers applied per allocated point */
  modifiers: PassiveStatModifier[];
}

// ---------------------------------------------------------------------------
// Aggregated stat result
// ---------------------------------------------------------------------------

/** A single aggregated stat entry after summing all allocated node contributions. */
export interface AggregatedStat {
  /** Display name of the stat */
  statId: string;
  /** Total flat bonus (sum of all flat modifiers × points) */
  flat: number;
  /** Total percent bonus (sum of all percent modifiers × points) */
  percent: number;
}

// ---------------------------------------------------------------------------
// Parsing utility
// ---------------------------------------------------------------------------

/**
 * Parse a raw stat value string from the API into a typed modifier.
 *
 * Examples:
 *   "+20"     → { type: "flat", value: 20 }
 *   "+5%"     → { type: "percent", value: 5 }
 *   "6%"      → { type: "percent", value: 6 }
 *   "+1"      → { type: "flat", value: 1 }
 *   "13"      → { type: "flat", value: 13 }
 *   ""        → null (skip)
 *   "12s"     → null (non-numeric, skip)
 */
export function parseStatValue(
  key: string,
  rawValue: string | number,
): PassiveStatModifier | null {
  if (rawValue === "" || rawValue === null || rawValue === undefined) return null;

  const str = String(rawValue).trim();
  if (!str) return null;

  const isPercent = str.endsWith("%");
  const cleaned = str.replace(/[+%]/g, "").trim();
  const num = parseFloat(cleaned);

  if (isNaN(num) || !isFinite(num)) return null;

  return {
    statId: key,
    type: isPercent ? "percent" : "flat",
    value: num,
  };
}

/**
 * Extract effects from a passive node's stats array.
 * Returns null if the node has no parseable stat modifiers.
 */
export function extractNodeEffects(
  stats: Array<{ key: string; value: string | number }>,
): PassiveNodeEffect | null {
  const modifiers: PassiveStatModifier[] = [];

  for (const stat of stats) {
    const mod = parseStatValue(stat.key, stat.value);
    if (mod) modifiers.push(mod);
  }

  return modifiers.length > 0 ? { modifiers } : null;
}
