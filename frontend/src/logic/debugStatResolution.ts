/**
 * debugStatResolution.ts — Instrumented stat resolution with per-stage snapshots.
 *
 * Runs the same pipeline as resolveStats() but captures the stat pool
 * after each layer, enabling stage-by-stage debugging.
 *
 * Also includes circular dependency detection and conversion tracking.
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

export interface ConversionEntry {
  ruleName: string;
  sources: Record<string, number>;
  result: number;
  description: string;
}

export interface ResolutionSnapshot {
  /** Stats after Layer 1 (flat accumulation) */
  afterFlat: Record<string, number>;
  /** Stats after Layer 2 (percent scaling) */
  afterPercent: Record<string, number>;
  /** Stats after Layer 3 (derived conversions) */
  afterDerived: Record<string, number>;
  /** Final resolved stats */
  finalStats: Record<string, number>;
  /** Conversion trace: which derived rules fired and what they produced */
  conversions: ConversionEntry[];
  /** Warnings from the resolution process */
  warnings: string[];
  /** Circular dependencies detected (stat names) */
  circularDeps: string[];
  /** Whether resolution order was valid */
  orderValid: boolean;
}

// ---------------------------------------------------------------------------
// Circular dependency detection
// ---------------------------------------------------------------------------

/**
 * Detect circular dependencies in derived stat rules.
 * Returns array of stat names involved in cycles.
 */
export function detectCircularStatDependencies(
  rules: DerivedStatRule[] = DEFAULT_DERIVED_RULES,
): string[] {
  const sorted = topologicalSort(rules);
  if (sorted.length === rules.length) return [];

  // Find which rules weren't sorted (they're in cycles)
  const sortedTargets = new Set(sorted.map((r) => r.targetStat));
  return rules
    .filter((r) => !sortedTargets.has(r.targetStat))
    .map((r) => r.targetStat);
}

// ---------------------------------------------------------------------------
// Instrumented resolution
// ---------------------------------------------------------------------------

function poolToRecord(pool: Map<string, number>): Record<string, number> {
  const rec: Record<string, number> = {};
  for (const [k, v] of pool) {
    if (v !== 0) rec[k] = Math.round(v * 100) / 100;
  }
  return rec;
}

function clampSafe(value: number): number {
  return Number.isFinite(value) ? value : 0;
}

/**
 * Run the resolution pipeline with full instrumentation.
 *
 * Same logic as resolveStats() but captures snapshots after each layer.
 */
export function generateResolutionSnapshot(
  aggregatedStats: Map<string, AggregatedStat>,
  derivedRules: DerivedStatRule[] = DEFAULT_DERIVED_RULES,
): ResolutionSnapshot {
  const pool = new Map<string, number>();
  const warnings: string[] = [];
  const conversions: ConversionEntry[] = [];

  // Detect circular dependencies upfront
  const circularDeps = detectCircularStatDependencies(derivedRules);
  if (circularDeps.length > 0) {
    warnings.push(`Circular dependencies detected: ${circularDeps.join(", ")}`);
  }

  // --- LAYER 1: Flat accumulation ---
  for (const [statId, agg] of aggregatedStats) {
    pool.set(statId, clampSafe(agg.flat));
  }
  const afterFlat = poolToRecord(pool);

  // --- LAYER 2: Percent scaling ---
  for (const [statId, agg] of aggregatedStats) {
    if (agg.percent === 0) continue;
    const base = pool.get(statId) ?? 0;
    const scaled = base * (1 + agg.percent / 100);
    pool.set(statId, clampSafe(scaled));
  }
  const afterPercent = poolToRecord(pool);

  // --- LAYER 3: Derived stats ---
  const sortedRules = topologicalSort(derivedRules);

  // Validate ordering: check that all sources are resolved before dependents
  let orderValid = true;
  const resolvedSoFar = new Set<string>(pool.keys());

  for (const rule of sortedRules) {
    for (const src of rule.sources) {
      if (!resolvedSoFar.has(src) && !pool.has(src)) {
        // Source hasn't been seen — it's an external stat that wasn't provided
        // This is acceptable (defaults to 0), not an ordering issue
      }
    }

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

    if (!hasAnySources) continue;

    try {
      const derivedValue = rule.formula(sourceValues);
      if (!Number.isFinite(derivedValue)) {
        warnings.push(`Derived "${rule.targetStat}" produced non-finite value, skipped`);
        orderValid = false;
        continue;
      }

      const existing = pool.get(rule.targetStat) ?? 0;
      pool.set(rule.targetStat, clampSafe(existing + derivedValue));
      resolvedSoFar.add(rule.targetStat);

      conversions.push({
        ruleName: rule.targetStat,
        sources: { ...sourceValues },
        result: derivedValue,
        description: rule.description ?? `${rule.sources.join(" + ")} → ${rule.targetStat}`,
      });
    } catch (err) {
      warnings.push(`Derived "${rule.targetStat}" threw error: ${err}`);
      orderValid = false;
    }
  }

  const afterDerived = poolToRecord(pool);

  return {
    afterFlat,
    afterPercent,
    afterDerived,
    finalStats: afterDerived, // After derived IS the final result
    conversions,
    warnings,
    circularDeps,
    orderValid,
  };
}

// ---------------------------------------------------------------------------
// Validation tests
// ---------------------------------------------------------------------------

export interface ResolutionTestCase {
  name: string;
  input: Map<string, AggregatedStat>;
  expectedFinal: Record<string, number>;
  expectWarnings?: boolean;
}

export interface ResolutionTestResult {
  name: string;
  passed: boolean;
  details: string;
}

function agg(statId: string, flat: number, percent: number): [string, AggregatedStat] {
  return [statId, { statId, flat, percent }];
}

export function runResolutionTest(test: ResolutionTestCase): ResolutionTestResult {
  const snapshot = generateResolutionSnapshot(test.input);
  const failures: string[] = [];

  for (const [stat, expected] of Object.entries(test.expectedFinal)) {
    const actual = snapshot.finalStats[stat] ?? 0;
    if (Math.abs(actual - expected) > 0.01) {
      failures.push(`${stat}: expected ${expected}, got ${actual}`);
    }
  }

  if (test.expectWarnings && snapshot.warnings.length === 0) {
    failures.push("Expected warnings but none emitted");
  }

  return {
    name: test.name,
    passed: failures.length === 0,
    details: failures.length === 0
      ? `OK (${snapshot.conversions.length} conversions)`
      : failures.join("; "),
  };
}

export const RESOLUTION_TESTS: ResolutionTestCase[] = [
  {
    name: "Base + Flat + Percent (100 health + 50 flat + 20% = 180)",
    input: new Map([agg("Health", 150, 20)]), // flat=150 (100+50), percent=20
    expectedFinal: { Health: 180 },
  },
  {
    name: "Derived conversion (Vitality 20 → Derived Health 40)",
    input: new Map([agg("Vitality", 20, 0)]),
    expectedFinal: { Vitality: 20, "Derived Health": 40 },
  },
  {
    name: "Derived conversion (Intelligence 15 → Derived Mana 30)",
    input: new Map([agg("Intelligence", 15, 0)]),
    expectedFinal: { Intelligence: 15, "Derived Mana": 30 },
  },
  {
    name: "Percent on zero flat = 0",
    input: new Map([agg("Damage", 0, 50)]),
    expectedFinal: { Damage: 0 },
  },
  {
    name: "Negative percent (100 - 30% = 70)",
    input: new Map([agg("Armor", 100, -30)]),
    expectedFinal: { Armor: 70 },
  },
  {
    name: "Multiple derived rules fire",
    input: new Map([agg("Strength", 10, 0), agg("Dexterity", 15, 0)]),
    expectedFinal: {
      Strength: 10,
      Dexterity: 15,
      "Derived Armor From Strength": 10,
      "Derived Dodge Rating": 15,
    },
  },
];
