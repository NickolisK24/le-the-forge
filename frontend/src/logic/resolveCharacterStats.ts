/**
 * resolveCharacterStats.ts — Resolve raw passive stats into final character stats.
 *
 * Takes raw passive output + optional base stats, applies derived rules,
 * and produces the final character stat sheet.
 *
 * This wraps the existing resolveStats pipeline with a simpler interface
 * for the debug comparison panel.
 */

import type { AggregatedStat } from "@/types/passiveEffects";
import { resolveStats, type StatPool } from "@/logic/statResolutionPipeline";

/** Default base stats for a fresh character (before passives) */
const DEFAULT_BASE_STATS: Record<string, number> = {
  "Base Health": 100,
  "Base Mana": 50,
  "Base Armor": 0,
  "Base Dodge Rating": 0,
};

/**
 * Resolve raw passive stats into final character stats.
 *
 * @param passiveStats — aggregated flat + percent from computePassiveStats
 * @param baseStats — optional base character stats (defaults provided)
 * @returns flat Record<string, number> of final resolved stats
 */
export function resolveCharacterStats(
  passiveStats: Map<string, AggregatedStat>,
  baseStats: Record<string, number> = DEFAULT_BASE_STATS,
): Record<string, number> {
  // Merge base stats into the aggregation as flat contributions
  const merged = new Map(passiveStats);
  for (const [statId, value] of Object.entries(baseStats)) {
    const existing = merged.get(statId);
    if (existing) {
      merged.set(statId, { ...existing, flat: existing.flat + value });
    } else {
      merged.set(statId, { statId, flat: value, percent: 0 });
    }
  }

  // Run through the resolution pipeline
  const resolved: StatPool = resolveStats(merged);

  // Convert to plain Record for display
  const result: Record<string, number> = {};
  for (const [key, val] of resolved) {
    if (val === 0) continue;
    const rounded = Math.round(val * 100) / 100;
    if (!Number.isFinite(rounded)) continue;
    result[key] = rounded;
  }

  return result;
}

/**
 * Run a validation test case and return pass/fail with details.
 */
export interface StatTestCase {
  name: string;
  allocations: Array<{ statId: string; flat: number; percent: number }>;
  expectedStats: Record<string, number>;
}

export interface StatTestResult {
  name: string;
  passed: boolean;
  details: string;
}

export function runStatTest(test: StatTestCase): StatTestResult {
  const input = new Map<string, AggregatedStat>();
  for (const alloc of test.allocations) {
    const existing = input.get(alloc.statId);
    if (existing) {
      input.set(alloc.statId, {
        statId: alloc.statId,
        flat: existing.flat + alloc.flat,
        percent: existing.percent + alloc.percent,
      });
    } else {
      input.set(alloc.statId, {
        statId: alloc.statId,
        flat: alloc.flat,
        percent: alloc.percent,
      });
    }
  }

  const resolved = resolveStats(input);
  const failures: string[] = [];

  for (const [stat, expected] of Object.entries(test.expectedStats)) {
    const actual = Math.round((resolved.get(stat) ?? 0) * 100) / 100;
    if (Math.abs(actual - expected) > 0.01) {
      failures.push(`${stat}: expected ${expected}, got ${actual}`);
    }
  }

  return {
    name: test.name,
    passed: failures.length === 0,
    details: failures.length === 0 ? "All stats match" : failures.join("; "),
  };
}

/** Built-in validation test cases */
export const VALIDATION_TESTS: StatTestCase[] = [
  {
    name: "Single flat stat (Strength +10)",
    allocations: [{ statId: "Strength", flat: 10, percent: 0 }],
    expectedStats: { "Strength": 10 },
  },
  {
    name: "Stacking flat stats (Strength +10 + +15)",
    allocations: [
      { statId: "Strength", flat: 10, percent: 0 },
      { statId: "Strength", flat: 15, percent: 0 },
    ],
    expectedStats: { "Strength": 25 },
  },
  {
    name: "Flat + percent scaling (Armor 100 + 50%)",
    allocations: [{ statId: "Armor", flat: 100, percent: 50 }],
    expectedStats: { "Armor": 150 },
  },
  {
    name: "Derived stat (Intelligence 10 → Derived Mana 20)",
    allocations: [{ statId: "Intelligence", flat: 10, percent: 0 }],
    expectedStats: { "Intelligence": 10, "Derived Mana": 20 },
  },
  {
    name: "Derived stat (Vitality 5 → Derived Health 10)",
    allocations: [{ statId: "Vitality", flat: 5, percent: 0 }],
    expectedStats: { "Vitality": 5, "Derived Health": 10 },
  },
  {
    name: "Mixed types (Str + Dex + Health%)",
    allocations: [
      { statId: "Strength", flat: 20, percent: 0 },
      { statId: "Dexterity", flat: 15, percent: 0 },
      { statId: "Health", flat: 100, percent: 25 },
    ],
    expectedStats: { "Strength": 20, "Dexterity": 15, "Health": 125 },
  },
  {
    name: "Percent-only stat (no base → 0)",
    allocations: [{ statId: "Damage", flat: 0, percent: 50 }],
    expectedStats: { "Damage": 0 },
  },
];
