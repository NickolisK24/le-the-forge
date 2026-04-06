/**
 * mergeCharacterStats.ts — Merge passive and skill stats into a unified pipeline.
 *
 * Combines two stat sources into one, then resolves through the standard pipeline.
 * Handles negative values (skill downsides) correctly.
 */

import type { AggregatedStat } from "@/types/passiveEffects";
import { resolveStats, type StatPool } from "@/logic/statResolutionPipeline";

// ---------------------------------------------------------------------------
// Snapshot merge (flat dictionaries)
// ---------------------------------------------------------------------------

/**
 * Merge two flat stat snapshots by summing identical stat IDs.
 * Preserves negative values (downsides from skills).
 */
export function mergeStatSnapshots(
  passiveStats: Record<string, number>,
  skillStats: Record<string, number>,
): Record<string, number> {
  const merged: Record<string, number> = {};

  for (const [key, val] of Object.entries(passiveStats)) {
    if (Number.isFinite(val)) merged[key] = (merged[key] ?? 0) + val;
  }
  for (const [key, val] of Object.entries(skillStats)) {
    if (Number.isFinite(val)) merged[key] = (merged[key] ?? 0) + val;
  }

  return merged;
}

// ---------------------------------------------------------------------------
// AggregatedStat merge (flat + percent maps)
// ---------------------------------------------------------------------------

/**
 * Merge two AggregatedStat maps by summing flat and percent for each statId.
 */
export function mergeAggregatedStats(
  a: Map<string, AggregatedStat>,
  b: Map<string, AggregatedStat>,
): Map<string, AggregatedStat> {
  const merged = new Map<string, AggregatedStat>();

  // Copy all from A
  for (const [key, stat] of a) {
    merged.set(key, { statId: key, flat: stat.flat, percent: stat.percent });
  }

  // Add B into merged
  for (const [key, stat] of b) {
    const existing = merged.get(key);
    if (existing) {
      existing.flat += stat.flat;
      existing.percent += stat.percent;
    } else {
      merged.set(key, { statId: key, flat: stat.flat, percent: stat.percent });
    }
  }

  return merged;
}

// ---------------------------------------------------------------------------
// Unified resolution
// ---------------------------------------------------------------------------

/** Default base character stats before any passives or skills */
const DEFAULT_BASE_STATS: Map<string, AggregatedStat> = new Map([
  ["Base Health", { statId: "Base Health", flat: 100, percent: 0 }],
  ["Base Mana", { statId: "Base Mana", flat: 50, percent: 0 }],
]);

/**
 * Resolve unified character stats from passive + skill sources.
 *
 * Flow:
 *   1. Merge passive AggregatedStats + skill AggregatedStats
 *   2. Merge in base stats
 *   3. Run through resolveStats pipeline (flat → percent → derived)
 *   4. Return final StatPool
 */
export function resolveCharacterStatsUnified(
  passiveStats: Map<string, AggregatedStat>,
  skillStats: Map<string, AggregatedStat>,
  baseStats: Map<string, AggregatedStat> = DEFAULT_BASE_STATS,
): StatPool {
  // Step 1: merge passive + skill
  const combined = mergeAggregatedStats(passiveStats, skillStats);

  // Step 2: merge in base stats
  const withBase = mergeAggregatedStats(combined, baseStats);

  // Step 3: resolve through pipeline
  return resolveStats(withBase);
}

// ---------------------------------------------------------------------------
// Validation tests
// ---------------------------------------------------------------------------

export interface MergeTestCase {
  name: string;
  passiveStats: Map<string, AggregatedStat>;
  skillStats: Map<string, AggregatedStat>;
  expectedStats: Record<string, number>;
}

export interface MergeTestResult {
  name: string;
  passed: boolean;
  details: string;
}

export function runMergeTest(test: MergeTestCase): MergeTestResult {
  const merged = mergeAggregatedStats(test.passiveStats, test.skillStats);
  const resolved = resolveStats(merged);

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

function agg(statId: string, flat: number, percent: number): [string, AggregatedStat] {
  return [statId, { statId, flat, percent }];
}

export const MERGE_VALIDATION_TESTS: MergeTestCase[] = [
  {
    name: "Passive + Skill flat stacking (Health +50 + +20 = 70)",
    passiveStats: new Map([agg("Health", 50, 0)]),
    skillStats: new Map([agg("Health", 20, 0)]),
    expectedStats: { Health: 70 },
  },
  {
    name: "Passive flat + Skill percent (Armor 100 + -20% = 80)",
    passiveStats: new Map([agg("Armor", 100, 0)]),
    skillStats: new Map([agg("Armor", 0, -20)]),
    expectedStats: { Armor: 80 },
  },
  {
    name: "Both flat + both percent (Damage 50 +30% + 20 +10% = 98)",
    passiveStats: new Map([agg("Damage", 50, 30)]),
    skillStats: new Map([agg("Damage", 20, 10)]),
    expectedStats: { Damage: 98 }, // (50+20) * (1 + (30+10)/100) = 70 * 1.4 = 98
  },
  {
    name: "Skill downside (Damage 100 + skill -30% = 70)",
    passiveStats: new Map([agg("Damage", 100, 0)]),
    skillStats: new Map([agg("Damage", 0, -30)]),
    expectedStats: { Damage: 70 },
  },
  {
    name: "Independent stats don't interact",
    passiveStats: new Map([agg("Strength", 20, 0)]),
    skillStats: new Map([agg("Mana Efficiency", 0, 15)]),
    expectedStats: { Strength: 20, "Mana Efficiency": 0 }, // percent on 0 flat = 0
  },
  {
    name: "Derived stat from merged source (Int 10 passive + 5 skill → Derived Mana 30)",
    passiveStats: new Map([agg("Intelligence", 10, 0)]),
    skillStats: new Map([agg("Intelligence", 5, 0)]),
    expectedStats: { Intelligence: 15, "Derived Mana": 30 },
  },
];
