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
import type { RuntimeContext } from "@/types/runtimeContext";
import { getHealthPercent } from "@/types/runtimeContext";

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
  runtimeCtx?: RuntimeContext,
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
      return { passed: has, reason: `item "${condition.itemType}" equipped: ${has}` };
    }

    case "skill_allocated": {
      const pts = context.allocatedSkills.get(condition.skillId) ?? 0;
      const minPts = condition.minPoints ?? 1;
      const passed = pts >= minPts;
      return { passed, reason: `skill "${condition.skillId}" ${pts} >= ${minPts}: ${passed}` };
    }

    case "tag_present": {
      // Check both build context tags and runtime context tags
      const has = context.tags.has(condition.tag) || (runtimeCtx?.activeTags.has(condition.tag) ?? false);
      return { passed: has, reason: `tag "${condition.tag}" present: ${has}` };
    }

    // --- Context-based conditions (require RuntimeContext) ---

    case "health_percentage_threshold": {
      if (!runtimeCtx) return { passed: false, reason: "No runtime context (health% unavailable)" };
      const pct = Math.round(getHealthPercent(runtimeCtx) * 100) / 100;
      const passed = compare(pct, condition.operator, condition.value);
      return { passed, reason: `health% ${pct} ${condition.operator} ${condition.value} → ${passed}` };
    }

    case "enemy_type": {
      if (!runtimeCtx) return { passed: false, reason: "No runtime context (enemy type unavailable)" };
      const passed = runtimeCtx.enemyType === condition.enemyType;
      return { passed, reason: `enemy "${runtimeCtx.enemyType}" == "${condition.enemyType}": ${passed}` };
    }

    case "minion_count": {
      if (!runtimeCtx) return { passed: false, reason: "No runtime context (minion count unavailable)" };
      const passed = compare(runtimeCtx.minionCount, condition.operator, condition.value);
      return { passed, reason: `minions ${runtimeCtx.minionCount} ${condition.operator} ${condition.value}: ${passed}` };
    }

    case "movement_state": {
      if (!runtimeCtx) return { passed: false, reason: "No runtime context (movement unavailable)" };
      const passed = runtimeCtx.isMoving === condition.isMoving;
      return { passed, reason: `moving=${runtimeCtx.isMoving}, want=${condition.isMoving}: ${passed}` };
    }

    case "buff_active": {
      if (!runtimeCtx) return { passed: false, reason: "No runtime context (buffs unavailable)" };
      const allBuffs = [...runtimeCtx.activeBuffIds, ...runtimeCtx.activeDebuffIds];
      const passed = allBuffs.includes(condition.buffId);
      return { passed, reason: `buff "${condition.buffId}" active: ${passed}` };
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
  runtimeCtx?: RuntimeContext,
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
      const { passed, reason } = evaluateCondition(mod.condition, context, runtimeCtx);
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

/** Context-based conditional modifiers (require RuntimeContext) */
export const CONTEXT_CONDITIONAL_MODIFIERS: ConditionalStatModifier[] = [
  {
    statId: "Low Life Bonus",
    flat: 100,
    percent: 0,
    condition: { type: "health_percentage_threshold", operator: "<=", value: 50 },
    description: "+100 when health ≤ 50%",
    source: "Context: Low Life",
  },
  {
    statId: "Boss Damage",
    flat: 0,
    percent: 40,
    condition: { type: "enemy_type", enemyType: "boss" },
    description: "+40% vs Boss",
    source: "Context: Boss Damage",
  },
  {
    statId: "Minion Army Bonus",
    flat: 20,
    percent: 0,
    condition: { type: "minion_count", operator: ">=", value: 3 },
    description: "+20 when ≥3 minions",
    source: "Context: Minion Army",
  },
  {
    statId: "Standing Still Bonus",
    flat: 0,
    percent: 15,
    condition: { type: "movement_state", isMoving: false },
    description: "+15% when stationary",
    source: "Context: Stationary",
  },
];

// ---------------------------------------------------------------------------
// Validation tests
// ---------------------------------------------------------------------------

export interface ConditionalTestCase {
  name: string;
  modifiers: ConditionalStatModifier[];
  context: BuildContext;
  runtimeCtx?: RuntimeContext;
  expectedResults: Array<{ description: string; shouldPass: boolean }>;
}

export interface ConditionalTestResult {
  name: string;
  passed: boolean;
  details: string;
}

export function runConditionalTest(test: ConditionalTestCase): ConditionalTestResult {
  const results = evaluateConditionalModifiers(test.modifiers, test.context, test.runtimeCtx);
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
  // --- Context-based tests ---
  {
    name: "Health% ≤ 50: passes (40%)",
    modifiers: [CONTEXT_CONDITIONAL_MODIFIERS[0]],
    context: { statPool: new Map(), equippedItems: [], allocatedSkills: new Map(), tags: new Set() },
    runtimeCtx: { currentHealth: 400, maxHealth: 1000, currentMana: 200, maxMana: 200, isMoving: false, wasHitRecently: false, isChanneling: false, enemyType: "boss", enemyCount: 1, minionCount: 0, activeTags: new Set(), currentWard: 0 },
    expectedResults: [{ description: "+100 when health ≤ 50%", shouldPass: true }],
  },
  {
    name: "Enemy type = boss: passes",
    modifiers: [CONTEXT_CONDITIONAL_MODIFIERS[1]],
    context: { statPool: new Map(), equippedItems: [], allocatedSkills: new Map(), tags: new Set() },
    runtimeCtx: { currentHealth: 1000, maxHealth: 1000, currentMana: 200, maxMana: 200, isMoving: false, wasHitRecently: false, isChanneling: false, enemyType: "boss", enemyCount: 1, minionCount: 0, activeTags: new Set(), currentWard: 0 },
    expectedResults: [{ description: "+40% vs Boss", shouldPass: true }],
  },
  {
    name: "Minions ≥ 3: fails (have 2)",
    modifiers: [CONTEXT_CONDITIONAL_MODIFIERS[2]],
    context: { statPool: new Map(), equippedItems: [], allocatedSkills: new Map(), tags: new Set() },
    runtimeCtx: { currentHealth: 1000, maxHealth: 1000, currentMana: 200, maxMana: 200, isMoving: false, wasHitRecently: false, isChanneling: false, enemyType: "normal", enemyCount: 1, minionCount: 2, activeTags: new Set(), currentWard: 0 },
    expectedResults: [{ description: "+20 when ≥3 minions", shouldPass: false }],
  },
];
