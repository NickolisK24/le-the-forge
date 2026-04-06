/**
 * conditionalStatEngine.ts — Evaluates conditional stat modifiers.
 *
 * Inserted as Layer 2.5 in the resolution pipeline (between percent and derived).
 * Pure, deterministic, safe — invalid conditions log warnings and skip.
 */

import type {
  ConditionDefinition,
  ConditionalStatModifier,
  ConditionalEvalResult,
  BuildContext,
  ComparisonOperator,
} from "@/types/conditionalStats";

// ---------------------------------------------------------------------------
// Condition evaluation
// ---------------------------------------------------------------------------

/**
 * Evaluate a single condition against the build context.
 * Returns { passed: boolean, reason: string }.
 */
export function evaluateCondition(
  condition: ConditionDefinition,
  context: BuildContext,
): { passed: boolean; reason: string } {
  switch (condition.type) {
    case "stat_threshold": {
      const actual = context.statPool.get(condition.statId) ?? 0;
      const passed = compare(actual, condition.operator, condition.value);
      return {
        passed,
        reason: `${condition.statId} ${actual} ${condition.operator} ${condition.value} → ${passed}`,
      };
    }

    case "item_equipped": {
      const has = context.equippedItems.includes(condition.itemType);
      return {
        passed: has,
        reason: `item "${condition.itemType}" equipped: ${has}`,
      };
    }

    case "skill_allocated": {
      const pts = context.allocatedSkills.get(condition.skillId) ?? 0;
      const minPts = condition.minPoints ?? 1;
      const passed = pts >= minPts;
      return {
        passed,
        reason: `skill "${condition.skillId}" points ${pts} >= ${minPts}: ${passed}`,
      };
    }

    case "tag_present": {
      const has = context.tags.has(condition.tag);
      return {
        passed: has,
        reason: `tag "${condition.tag}" present: ${has}`,
      };
    }

    default: {
      return { passed: false, reason: `Unknown condition type: ${(condition as any).type}` };
    }
  }
}

function compare(a: number, op: ComparisonOperator, b: number): boolean {
  switch (op) {
    case "<": return a < b;
    case "<=": return a <= b;
    case ">": return a > b;
    case ">=": return a >= b;
    case "==": return Math.abs(a - b) < 0.001;
    case "!=": return Math.abs(a - b) >= 0.001;
    default: return false;
  }
}

// ---------------------------------------------------------------------------
// Batch evaluation
// ---------------------------------------------------------------------------

/**
 * Evaluate all conditional modifiers against the build context.
 * Returns results sorted by statId then source for determinism.
 */
export function evaluateConditionalModifiers(
  modifiers: ConditionalStatModifier[],
  context: BuildContext,
): ConditionalEvalResult[] {
  // Sort for deterministic ordering
  const sorted = [...modifiers].sort((a, b) => {
    const statCmp = a.statId.localeCompare(b.statId);
    if (statCmp !== 0) return statCmp;
    return a.source.localeCompare(b.source);
  });

  const results: ConditionalEvalResult[] = [];

  for (const mod of sorted) {
    try {
      const { passed, reason } = evaluateCondition(mod.condition, context);
      results.push({
        modifier: mod,
        conditionMet: passed,
        appliedFlat: passed ? mod.flat : 0,
        appliedPercent: passed ? mod.percent : 0,
        reason,
      });
    } catch (err) {
      // Safe failure: log and skip
      if (process.env.NODE_ENV !== "production") {
        console.warn(`[ConditionalStats] Error evaluating "${mod.description}":`, err);
      }
      results.push({
        modifier: mod,
        conditionMet: false,
        appliedFlat: 0,
        appliedPercent: 0,
        reason: `Error: ${err}`,
      });
    }
  }

  return results;
}

/**
 * Apply evaluated conditional results to a stat pool.
 * Only applies modifiers where conditionMet === true.
 * Returns a new pool (does not mutate input).
 */
export function applyConditionalResults(
  pool: Map<string, number>,
  results: ConditionalEvalResult[],
): Map<string, number> {
  const next = new Map(pool);

  for (const r of results) {
    if (!r.conditionMet) continue;

    const statId = r.modifier.statId;
    const current = next.get(statId) ?? 0;

    // Apply flat addition
    if (r.appliedFlat !== 0 && Number.isFinite(r.appliedFlat)) {
      next.set(statId, current + r.appliedFlat);
    }

    // Apply percent scaling on current value
    if (r.appliedPercent !== 0 && Number.isFinite(r.appliedPercent)) {
      const afterFlat = next.get(statId) ?? 0;
      next.set(statId, afterFlat * (1 + r.appliedPercent / 100));
    }
  }

  return next;
}

// ---------------------------------------------------------------------------
// Default empty context
// ---------------------------------------------------------------------------

export function createEmptyBuildContext(statPool: Map<string, number> = new Map()): BuildContext {
  return {
    statPool,
    equippedItems: [],
    allocatedSkills: new Map(),
    tags: new Set(),
  };
}

// ---------------------------------------------------------------------------
// Example conditional modifiers (for testing)
// ---------------------------------------------------------------------------

export const EXAMPLE_CONDITIONAL_MODIFIERS: ConditionalStatModifier[] = [
  {
    statId: "Health Bonus",
    flat: 50,
    percent: 0,
    condition: { type: "stat_threshold", statId: "Health", operator: "<=", value: 200 },
    description: "+50 Health when Health ≤ 200",
    source: "Test: Low Health Bonus",
  },
  {
    statId: "Armor Bonus",
    flat: 30,
    percent: 0,
    condition: { type: "item_equipped", itemType: "shield" },
    description: "+30 Armor when Shield equipped",
    source: "Test: Shield Bonus",
  },
  {
    statId: "Damage Bonus",
    flat: 0,
    percent: 25,
    condition: { type: "tag_present", tag: "melee" },
    description: "+25% Damage when melee build",
    source: "Test: Melee Bonus",
  },
];

// ---------------------------------------------------------------------------
// Validation tests
// ---------------------------------------------------------------------------

export interface ConditionalTestCase {
  name: string;
  modifiers: ConditionalStatModifier[];
  context: BuildContext;
  expectedResults: Array<{ description: string; shouldPass: boolean }>;
}

export interface ConditionalTestResult {
  name: string;
  passed: boolean;
  details: string;
}

export function runConditionalTest(test: ConditionalTestCase): ConditionalTestResult {
  const results = evaluateConditionalModifiers(test.modifiers, test.context);
  const failures: string[] = [];

  for (const expected of test.expectedResults) {
    const result = results.find((r) => r.modifier.description === expected.description);
    if (!result) {
      failures.push(`"${expected.description}" not found in results`);
      continue;
    }
    if (result.conditionMet !== expected.shouldPass) {
      failures.push(
        `"${expected.description}": expected ${expected.shouldPass ? "PASS" : "FAIL"}, got ${result.conditionMet ? "PASS" : "FAIL"} (${result.reason})`,
      );
    }
  }

  return {
    name: test.name,
    passed: failures.length === 0,
    details: failures.length === 0 ? "All conditions evaluated correctly" : failures.join("; "),
  };
}

export const CONDITIONAL_TESTS: ConditionalTestCase[] = [
  {
    name: "Health ≤ 200: condition passes (health=150)",
    modifiers: [EXAMPLE_CONDITIONAL_MODIFIERS[0]],
    context: {
      statPool: new Map([["Health", 150]]),
      equippedItems: [],
      allocatedSkills: new Map(),
      tags: new Set(),
    },
    expectedResults: [{ description: "+50 Health when Health ≤ 200", shouldPass: true }],
  },
  {
    name: "Health ≤ 200: condition fails (health=300)",
    modifiers: [EXAMPLE_CONDITIONAL_MODIFIERS[0]],
    context: {
      statPool: new Map([["Health", 300]]),
      equippedItems: [],
      allocatedSkills: new Map(),
      tags: new Set(),
    },
    expectedResults: [{ description: "+50 Health when Health ≤ 200", shouldPass: false }],
  },
  {
    name: "Multiple conditions: independent evaluation",
    modifiers: EXAMPLE_CONDITIONAL_MODIFIERS,
    context: {
      statPool: new Map([["Health", 150]]),
      equippedItems: ["sword"],
      allocatedSkills: new Map(),
      tags: new Set(["melee"]),
    },
    expectedResults: [
      { description: "+50 Health when Health ≤ 200", shouldPass: true },
      { description: "+30 Armor when Shield equipped", shouldPass: false },
      { description: "+25% Damage when melee build", shouldPass: true },
    ],
  },
];
