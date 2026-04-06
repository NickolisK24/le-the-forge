/**
 * conditionalStats.ts — Type definitions for conditional stat modifiers.
 *
 * Conditional modifiers only apply when their condition evaluates to true
 * against the current stat pool or build state.
 *
 * Supported condition types:
 *   - stat_threshold: compare a stat value against a threshold
 *   - item_equipped: check if a specific item type is equipped
 *   - skill_allocated: check if a skill node is allocated
 *   - tag_present: check if a tag exists in the build
 */

// ---------------------------------------------------------------------------
// Condition definitions
// ---------------------------------------------------------------------------

export type ComparisonOperator = "<" | "<=" | ">" | ">=" | "==" | "!=";

export interface StatThresholdCondition {
  type: "stat_threshold";
  statId: string;
  operator: ComparisonOperator;
  value: number;
}

export interface ItemEquippedCondition {
  type: "item_equipped";
  itemType: string;
}

export interface SkillAllocatedCondition {
  type: "skill_allocated";
  skillId: string;
  minPoints?: number;
}

export interface TagPresentCondition {
  type: "tag_present";
  tag: string;
}

export type ConditionDefinition =
  | StatThresholdCondition
  | ItemEquippedCondition
  | SkillAllocatedCondition
  | TagPresentCondition;

// ---------------------------------------------------------------------------
// Conditional modifier
// ---------------------------------------------------------------------------

export interface ConditionalStatModifier {
  /** Target stat to modify */
  statId: string;
  /** Flat value to add (if condition passes) */
  flat: number;
  /** Percent value to add (if condition passes) */
  percent: number;
  /** Condition that must be true for this modifier to apply */
  condition: ConditionDefinition;
  /** Human-readable description */
  description: string;
  /** Source of this modifier (e.g. "Passive: Bone Aura", "Skill: Fireball") */
  source: string;
}

// ---------------------------------------------------------------------------
// Build context for condition evaluation
// ---------------------------------------------------------------------------

export interface BuildContext {
  /** Current resolved stat values */
  statPool: Map<string, number>;
  /** Equipped item types (e.g. ["sword", "shield"]) */
  equippedItems: string[];
  /** Allocated skill IDs with point counts */
  allocatedSkills: Map<string, number>;
  /** Active build tags (e.g. ["melee", "fire", "dual_wield"]) */
  tags: Set<string>;
}

// ---------------------------------------------------------------------------
// Evaluation result
// ---------------------------------------------------------------------------

export interface ConditionalEvalResult {
  modifier: ConditionalStatModifier;
  conditionMet: boolean;
  appliedFlat: number;
  appliedPercent: number;
  reason: string;
}
