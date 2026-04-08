/**
 * skillTree.ts — Type definitions for skill tree data and allocation.
 *
 * Skill trees are independent graph structures attached to individual skills.
 * Each skill has its own tree with unique nodes, connections, and stat modifiers.
 *
 * Key differences from passive trees:
 *   - Requirements can specify minimum points in a parent (not just allocated)
 *   - Max 20 points per skill tree
 *   - Node 0 is always the root (the skill itself)
 *   - Stats can have "downside" flag (negative effects)
 */

import type { PassiveStatModifier } from "@/types/passiveEffects";

export type SkillNodeId = string;

/** A requirement to allocate a skill node: parent must have >= N points */
export interface SkillNodeRequirement {
  /** Parent node ID */
  node: number;
  /** Minimum points the parent must have */
  requirement: number;
}

/** A single node in a skill tree */
export interface SkillNode {
  id: number;
  name: string;
  description: string;
  maxPoints: number;
  /** Parent node requirements: [{node, requirement}] */
  requirements: SkillNodeRequirement[];
  /** Stat modifiers applied per point */
  statModifiers: PassiveStatModifier[];
  /** Position in the tree canvas */
  x: number;
  y: number;
  /** Icon asset ID */
  icon: number | string | null;
  /** Whether this is a transformation/ability-granting node */
  abilityGrantedByNode: string | null;
  /** Mastery gate (0 = base, 1+ = mastery-specific) */
  mastery: number;
  masteryRequirement: number;
}

/** A complete skill tree for one skill */
export interface SkillTree {
  /** Skill tree identifier code */
  skillId: string;
  /** Display name of the skill */
  skillName: string;
  /** All nodes in this tree */
  nodes: SkillNode[];
  /** Root node ID (always 0) */
  startNodeId: number;
}

/** Maximum points allocatable per skill tree */
export const MAX_SKILL_POINTS = 20;

/** Allocation state for a single skill tree */
export type SkillAllocationMap = Map<number, number>;
