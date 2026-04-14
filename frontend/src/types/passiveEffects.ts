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

import {
  PASSIVE_STAT_KEY_MAP,
  ALL_ATTRIBUTE_FIELDS,
  ELEMENTAL_RES_FIELDS,
  ATTACK_AND_CAST_SPEED_FIELDS,
} from "@/constants/passiveStatMap";

// ---------------------------------------------------------------------------
// Core modifier types
// ---------------------------------------------------------------------------

/**
 * A single stat modification applied by a passive node per allocated point.
 *
 * statId is the BuildStats field name (e.g. "armour", "health_pct",
 * "necrotic_res") — NOT the raw game display string. Mapping is performed
 * by parseStatValue() via PASSIVE_STAT_KEY_MAP so the frontend stat
 * pipeline and the backend resolver agree on field names.
 */
export interface PassiveStatModifier {
  /** BuildStats field name (e.g. "armour", "health_pct") */
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
 * Parse a numeric stat value string.
 *
 * Examples:
 *   "+20"     → { isPercent: false, value: 20 }
 *   "+5%"     → { isPercent: true,  value: 5 }
 *   "6%"      → { isPercent: true,  value: 6 }
 *   "-50"     → { isPercent: false, value: -50 }
 *   ""        → null (skip)
 *   "12s"     → null (non-numeric, skip)
 */
function parseNumericValue(
  rawValue: string | number,
): { isPercent: boolean; value: number } | null {
  if (rawValue === "" || rawValue === null || rawValue === undefined) return null;

  const str = String(rawValue).trim();
  if (!str) return null;

  const isPercent = str.endsWith("%");
  const cleaned = str.replace(/[+%]/g, "").trim();
  // Preserve leading minus — the regex above strips + but not -
  const num = parseFloat(cleaned);

  if (isNaN(num) || !isFinite(num)) return null;

  return { isPercent, value: num };
}

/**
 * Parse a raw stat (key + value) into a typed modifier keyed by its
 * BuildStats field name.
 *
 * The raw `key` is translated through PASSIVE_STAT_KEY_MAP (mirrors the
 * backend passive_stat_resolver.py STAT_KEY_MAP). Unmapped keys return
 * null so the caller can route them to special-effects display instead
 * of aggregating into the stat pool.
 *
 * Composite keys that expand to multiple fields (e.g. "All Attributes",
 * "Elemental Resistance", "Attack And Cast Speed") return null here —
 * use extractNodeEffects() which performs the fan-out.
 */
export function parseStatValue(
  key: string,
  rawValue: string | number,
): PassiveStatModifier | null {
  const parsed = parseNumericValue(rawValue);
  if (!parsed) return null;

  const mappedStatId = PASSIVE_STAT_KEY_MAP[key];
  if (!mappedStatId) return null;
  // Composite sentinels must be expanded by extractNodeEffects, not here.
  if (mappedStatId.startsWith("_")) return null;

  return {
    statId: mappedStatId,
    type: parsed.isPercent ? "percent" : "flat",
    value: parsed.value,
  };
}

/**
 * Extract effects from a passive node's stats array.
 *
 * Handles composite keys by fanning out to multiple BuildStats fields —
 * mirrors the backend passive_stat_resolver.resolve_passive_stats:
 *   "All Attributes"        → strength, intelligence, dexterity, vitality, attunement
 *   "Elemental Resistance"  → fire_res, cold_res, lightning_res
 *   "Attack And Cast Speed" → attack_speed_pct, cast_speed
 *
 * Returns null if the node has no parseable stat modifiers.
 */
export function extractNodeEffects(
  stats: Array<{ key: string; value: string | number }>,
): PassiveNodeEffect | null {
  const modifiers: PassiveStatModifier[] = [];

  for (const stat of stats) {
    const mappedStatId = PASSIVE_STAT_KEY_MAP[stat.key];
    if (!mappedStatId) continue;

    const parsed = parseNumericValue(stat.value);
    if (!parsed) continue;

    const type: "percent" | "flat" = parsed.isPercent ? "percent" : "flat";

    // Composite fan-outs
    if (mappedStatId === "_all_attributes") {
      for (const field of ALL_ATTRIBUTE_FIELDS) {
        modifiers.push({ statId: field, type, value: parsed.value });
      }
    } else if (mappedStatId === "_elemental_res") {
      for (const field of ELEMENTAL_RES_FIELDS) {
        modifiers.push({ statId: field, type, value: parsed.value });
      }
    } else if (mappedStatId === "_attack_and_cast_speed") {
      for (const field of ATTACK_AND_CAST_SPEED_FIELDS) {
        modifiers.push({ statId: field, type, value: parsed.value });
      }
    } else {
      modifiers.push({ statId: mappedStatId, type, value: parsed.value });
    }
  }

  return modifiers.length > 0 ? { modifiers } : null;
}
