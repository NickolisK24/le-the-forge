/**
 * statResolutionPipeline.ts — Deterministic multi-layer stat resolution engine.
 *
 * Converts raw aggregated stats (flat + percent per stat) into final resolved values.
 *
 * Pipeline layers execute in fixed order:
 *   Layer 1 — Base flat accumulation:    value = flat
 *   Layer 2 — Percent scaling:           value = value × (1 + percent/100)
 *   Layer 3 — Derived stat generation:   value += formula(resolved sources)
 *
 * Derived stats use topological ordering to respect dependencies.
 * The pipeline is pure, deterministic, and produces a StatPool (Map<string, number>).
 *
 * Future extensions (not yet implemented):
 *   - Stat conversion chains (e.g. Strength → Armor at a ratio)
 *   - Conditional modifiers (e.g. "while dual wielding")
 *   - Tag-based scaling (e.g. "fire damage" tag)
 *   - Skill-specific stat overrides
 */

import type { AggregatedStat } from "@/types/passiveEffects";
import {
  type DerivedStatRule,
  DEFAULT_DERIVED_RULES,
  topologicalSort,
} from "@/logic/derivedStatRules";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Final resolved stat values — one number per stat */
export type StatPool = Map<string, number>;

/** Input: aggregated raw stats from computePassiveStats */
export type AggregatedStatMap = Map<string, AggregatedStat>;

// ---------------------------------------------------------------------------
// Pipeline
// ---------------------------------------------------------------------------

/**
 * Resolve aggregated stats into final stat values.
 *
 * @param aggregatedStats — raw flat + percent from computePassiveStats
 * @param derivedRules — optional custom rules (defaults to DEFAULT_DERIVED_RULES)
 * @returns StatPool with final resolved values for every stat
 */
export function resolveStats(
  aggregatedStats: AggregatedStatMap,
  derivedRules: DerivedStatRule[] = DEFAULT_DERIVED_RULES,
): StatPool {
  const pool: StatPool = new Map();

  // -----------------------------------------------------------------------
  // LAYER 1 — Base flat accumulation
  // -----------------------------------------------------------------------
  for (const [statId, agg] of aggregatedStats) {
    pool.set(statId, clampSafe(agg.flat));
  }

  // -----------------------------------------------------------------------
  // LAYER 2 — Percent scaling
  // -----------------------------------------------------------------------
  for (const [statId, agg] of aggregatedStats) {
    if (agg.percent === 0) continue;

    const base = pool.get(statId) ?? 0;
    const scaled = base * (1 + agg.percent / 100);
    pool.set(statId, clampSafe(scaled));
  }

  // -----------------------------------------------------------------------
  // LAYER 3 — Derived stats (topological order)
  // -----------------------------------------------------------------------
  const sortedRules = topologicalSort(derivedRules);

  for (const rule of sortedRules) {
    // Gather source values — skip rule if any source is missing
    const sourceValues: Record<string, number> = {};
    let hasAnySources = false;

    for (const src of rule.sources) {
      const val = pool.get(src);
      if (val !== undefined && val !== 0) {
        sourceValues[src] = val;
        hasAnySources = true;
      } else {
        sourceValues[src] = 0;
      }
    }

    // Only compute derived stat if at least one source has a value
    if (!hasAnySources) continue;

    try {
      const derivedValue = rule.formula(sourceValues);
      if (!Number.isFinite(derivedValue)) {
        if (process.env.NODE_ENV !== "production") {
          console.warn(
            `[StatPipeline] Derived stat "${rule.targetStat}" produced non-finite value, skipping`,
          );
        }
        continue;
      }

      // Add to existing value (derived stats accumulate on top of direct bonuses)
      const existing = pool.get(rule.targetStat) ?? 0;
      pool.set(rule.targetStat, clampSafe(existing + derivedValue));
    } catch (err) {
      if (process.env.NODE_ENV !== "production") {
        console.error(
          `[StatPipeline] Error in derived stat rule "${rule.targetStat}":`,
          err,
        );
      }
    }
  }

  return pool;
}

// ---------------------------------------------------------------------------
// Safety
// ---------------------------------------------------------------------------

/** Clamp a value to a safe finite number, replacing NaN/Infinity with 0 */
function clampSafe(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return value;
}
