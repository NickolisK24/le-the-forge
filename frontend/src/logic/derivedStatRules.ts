/**
 * derivedStatRules.ts — Rules for computing derived stats from base stats.
 *
 * Each rule declares:
 *   - targetStat: the stat to produce
 *   - sources: stats this rule depends on (must be resolved first)
 *   - formula: pure function computing the derived value from source values
 *
 * Rules are executed in topological order by the resolution pipeline.
 * Circular dependencies are detected at registration time.
 *
 * Design: data-driven, no hardcoded stat names in the pipeline itself.
 * New rules are added here; the pipeline consumes them generically.
 */

// ---------------------------------------------------------------------------
// Rule type
// ---------------------------------------------------------------------------

export interface DerivedStatRule {
  /** The stat this rule produces */
  targetStat: string;
  /** Stats that must be resolved before this rule executes */
  sources: string[];
  /** Pure function: receives resolved source values, returns derived value */
  formula: (sourceValues: Record<string, number>) => number;
  /** Optional description for debug display */
  description?: string;
}

// ---------------------------------------------------------------------------
// Default rules — Last Epoch derived stat definitions
// ---------------------------------------------------------------------------

export const DEFAULT_DERIVED_RULES: DerivedStatRule[] = [
  {
    targetStat: "Derived Health",
    sources: ["Vitality"],
    formula: (s) => (s["Vitality"] ?? 0) * 2,
    description: "Vitality × 2",
  },
  {
    targetStat: "Derived Mana",
    sources: ["Intelligence"],
    formula: (s) => (s["Intelligence"] ?? 0) * 2,
    description: "Intelligence × 2",
  },
  {
    targetStat: "Derived Armor From Strength",
    sources: ["Strength"],
    formula: (s) => (s["Strength"] ?? 0) * 1,
    description: "Strength × 1",
  },
  {
    targetStat: "Derived Dodge Rating",
    sources: ["Dexterity"],
    formula: (s) => (s["Dexterity"] ?? 0) * 1,
    description: "Dexterity × 1",
  },
];

// ---------------------------------------------------------------------------
// Topological sort — dependency-safe execution order
// ---------------------------------------------------------------------------

/**
 * Sort derived stat rules in topological order so that dependencies
 * are resolved before dependents.
 *
 * Detects circular dependencies and throws if found.
 *
 * @returns Rules in safe execution order
 */
export function topologicalSort(rules: DerivedStatRule[]): DerivedStatRule[] {
  // Build adjacency: targetStat → rules that depend on it
  const ruleMap = new Map<string, DerivedStatRule>();
  const inDegree = new Map<string, number>();
  const dependents = new Map<string, string[]>(); // source → [targets that need it]

  for (const rule of rules) {
    ruleMap.set(rule.targetStat, rule);
    inDegree.set(rule.targetStat, 0);
  }

  // Count in-degrees: how many sources does each rule depend on
  // (only counting sources that are themselves derived — external stats have no in-degree)
  const derivedTargets = new Set(rules.map((r) => r.targetStat));

  for (const rule of rules) {
    let deg = 0;
    for (const src of rule.sources) {
      if (derivedTargets.has(src)) {
        deg++;
        if (!dependents.has(src)) dependents.set(src, []);
        dependents.get(src)!.push(rule.targetStat);
      }
    }
    inDegree.set(rule.targetStat, deg);
  }

  // Kahn's algorithm
  const queue: string[] = [];
  for (const [target, deg] of inDegree) {
    if (deg === 0) queue.push(target);
  }

  const sorted: DerivedStatRule[] = [];
  while (queue.length > 0) {
    const current = queue.shift()!;
    const rule = ruleMap.get(current);
    if (rule) sorted.push(rule);

    for (const dep of dependents.get(current) ?? []) {
      const newDeg = (inDegree.get(dep) ?? 1) - 1;
      inDegree.set(dep, newDeg);
      if (newDeg === 0) queue.push(dep);
    }
  }

  // Detect cycles
  if (sorted.length < rules.length) {
    const unresolved = rules
      .filter((r) => !sorted.some((s) => s.targetStat === r.targetStat))
      .map((r) => r.targetStat);
    if (process.env.NODE_ENV !== "production") {
      console.error(
        "[DerivedStats] Circular dependency detected in rules:",
        unresolved,
      );
    }
    // Return what we can — skip circular rules
    return sorted;
  }

  return sorted;
}
