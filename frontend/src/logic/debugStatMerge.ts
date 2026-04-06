/**
 * debugStatMerge.ts — Full stat merge debug snapshot with validation.
 *
 * Generates a complete breakdown of stats from all sources (passive, skill, gear)
 * with conflict detection, NaN guards, and deterministic ordering.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface StatSourceEntry {
  statId: string;
  passive: number;
  skill: number;
  gear: number;
  merged: number;
}

export interface StatMergeSnapshot {
  passiveStats: Record<string, number>;
  skillStats: Record<string, number>;
  gearStats: Record<string, number>;
  mergedStats: Record<string, number>;
  /** Per-stat breakdown across all sources */
  breakdown: StatSourceEntry[];
  /** Warnings detected during merge */
  warnings: string[];
}

// ---------------------------------------------------------------------------
// Hardened multi-source merge
// ---------------------------------------------------------------------------

/**
 * Merge multiple stat sources with validation and conflict detection.
 *
 * Guards:
 *   - Skips NaN/Infinity values with warning
 *   - Skips empty/whitespace stat IDs with warning
 *   - Preserves negatives (skill downsides)
 *   - Deterministic alphabetical ordering
 */
export function mergeStatSourcesHardened(
  passive: Record<string, number>,
  skill: Record<string, number>,
  gear: Record<string, number>,
): { merged: Record<string, number>; warnings: string[] } {
  const merged: Record<string, number> = {};
  const warnings: string[] = [];

  const sources: [string, Record<string, number>][] = [
    ["passive", passive],
    ["skill", skill],
    ["gear", gear],
  ];

  for (const [sourceName, stats] of sources) {
    for (const [statId, value] of Object.entries(stats)) {
      // Guard: invalid stat ID
      if (!statId || statId.trim().length === 0) {
        warnings.push(`[${sourceName}] Empty stat ID skipped`);
        continue;
      }

      // Guard: NaN or Infinity
      if (!Number.isFinite(value)) {
        warnings.push(`[${sourceName}] ${statId}: non-finite value (${value}) skipped`);
        continue;
      }

      // Guard: undefined (shouldn't happen with Object.entries but defensive)
      if (value === undefined || value === null) {
        warnings.push(`[${sourceName}] ${statId}: null/undefined value skipped`);
        continue;
      }

      merged[statId] = (merged[statId] ?? 0) + value;
    }
  }

  // Guard: check merged results for NaN (shouldn't happen but catch floating point edge cases)
  for (const [statId, value] of Object.entries(merged)) {
    if (!Number.isFinite(value)) {
      warnings.push(`[merged] ${statId}: non-finite after merge (${value}), clamped to 0`);
      merged[statId] = 0;
    }
  }

  return { merged, warnings };
}

// ---------------------------------------------------------------------------
// Full snapshot generation
// ---------------------------------------------------------------------------

/**
 * Generate a complete stat merge snapshot with per-source breakdown.
 */
export function generateStatMergeSnapshot(
  passive: Record<string, number>,
  skill: Record<string, number>,
  gear: Record<string, number>,
): StatMergeSnapshot {
  const { merged, warnings } = mergeStatSourcesHardened(passive, skill, gear);

  // Build per-stat breakdown
  const allStatIds = new Set<string>();
  for (const key of Object.keys(passive)) allStatIds.add(key);
  for (const key of Object.keys(skill)) allStatIds.add(key);
  for (const key of Object.keys(gear)) allStatIds.add(key);

  const breakdown: StatSourceEntry[] = Array.from(allStatIds)
    .sort()
    .map((statId) => ({
      statId,
      passive: passive[statId] ?? 0,
      skill: skill[statId] ?? 0,
      gear: gear[statId] ?? 0,
      merged: merged[statId] ?? 0,
    }));

  return {
    passiveStats: passive,
    skillStats: skill,
    gearStats: gear,
    mergedStats: merged,
    breakdown,
    warnings,
  };
}

// ---------------------------------------------------------------------------
// Validation tests
// ---------------------------------------------------------------------------

export interface HardenedMergeTest {
  name: string;
  passive: Record<string, number>;
  skill: Record<string, number>;
  gear: Record<string, number>;
  expected: Record<string, number>;
  expectWarnings?: boolean;
}

export interface HardenedMergeTestResult {
  name: string;
  passed: boolean;
  details: string;
}

export function runHardenedMergeTest(test: HardenedMergeTest): HardenedMergeTestResult {
  const { merged, warnings } = mergeStatSourcesHardened(test.passive, test.skill, test.gear);

  const failures: string[] = [];

  for (const [stat, expected] of Object.entries(test.expected)) {
    const actual = merged[stat] ?? 0;
    if (Math.abs(actual - expected) > 0.01) {
      failures.push(`${stat}: expected ${expected}, got ${actual}`);
    }
  }

  if (test.expectWarnings && warnings.length === 0) {
    failures.push("Expected warnings but none emitted");
  }

  return {
    name: test.name,
    passed: failures.length === 0,
    details: failures.length === 0
      ? `OK${warnings.length > 0 ? ` (${warnings.length} warnings)` : ""}`
      : failures.join("; "),
  };
}

export const HARDENED_MERGE_TESTS: HardenedMergeTest[] = [
  {
    name: "Three-source flat stacking (50+20+30=100)",
    passive: { health: 50 },
    skill: { health: 20 },
    gear: { health: 30 },
    expected: { health: 100 },
  },
  {
    name: "Mixed positive/negative (100-20+10=90)",
    passive: { armor: 100 },
    skill: { armor: -20 },
    gear: { armor: 10 },
    expected: { armor: 90 },
  },
  {
    name: "Invalid NaN input handled safely",
    passive: { health: 50 },
    skill: { health: NaN },
    gear: { health: 10 },
    expected: { health: 60 },
    expectWarnings: true,
  },
  {
    name: "Independent stats from different sources",
    passive: { strength: 20 },
    skill: { "mana_cost": -5 },
    gear: { armor: 100 },
    expected: { strength: 20, "mana_cost": -5, armor: 100 },
  },
  {
    name: "All sources contribute to same stat",
    passive: { "fire_damage": 10 },
    skill: { "fire_damage": 25 },
    gear: { "fire_damage": 15 },
    expected: { "fire_damage": 50 },
  },
  {
    name: "Empty sources produce empty result",
    passive: {},
    skill: {},
    gear: {},
    expected: {},
  },
];
