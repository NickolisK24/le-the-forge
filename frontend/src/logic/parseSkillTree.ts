/**
 * parseSkillTree.ts — Convert community skill tree JSON into typed SkillTree objects.
 *
 * The community_skill_trees.json format differs from our SkillNode type.
 * This parser normalizes the data for use by the skill allocation engine.
 */

import type { SkillTree, SkillNode, SkillNodeRequirement } from "@/types/skillTree";
import type { PassiveStatModifier } from "@/types/passiveEffects";
import { parseStatValue } from "@/types/passiveEffects";

interface RawCommunityNode {
  id: number;
  name: string;
  description: string;
  maxPoints: number;
  mastery: number;
  masteryRequirement: number;
  stats: Array<{ statName: string; value: string; downside?: boolean }>;
  requirements: Array<{ node: number; requirement: number }>;
  transform: { x: number; y: number };
  icon: number | null;
  abilityGrantedByNode: string | null;
}

interface RawCommunityTree {
  id: string;
  ability: string;
  nodes: RawCommunityNode[];
}

/**
 * Parse a raw community skill tree into our typed SkillTree format.
 */
export function parseCommunitySkillTree(raw: RawCommunityTree): SkillTree {
  const nodes: SkillNode[] = raw.nodes.map((n) => ({
    id: n.id,
    name: n.name,
    description: n.description,
    maxPoints: n.maxPoints,
    requirements: n.requirements.map((r): SkillNodeRequirement => ({
      node: r.node,
      requirement: r.requirement,
    })),
    statModifiers: parseNodeStats(n.stats),
    x: n.transform?.x ?? 0,
    y: n.transform?.y ?? 0,
    icon: n.icon,
    abilityGrantedByNode: n.abilityGrantedByNode,
    mastery: n.mastery,
    masteryRequirement: n.masteryRequirement,
  }));

  return {
    skillId: raw.id,
    skillName: raw.nodes[0]?.name ?? raw.ability,
    nodes,
    startNodeId: 0,
  };
}

/**
 * Parse stat array from community format into PassiveStatModifier[].
 */
function parseNodeStats(
  stats: Array<{ statName: string; value: string; downside?: boolean }>,
): PassiveStatModifier[] {
  const mods: PassiveStatModifier[] = [];
  for (const stat of stats) {
    const mod = parseStatValue(stat.statName, stat.value);
    if (mod) {
      // Downside stats have their value negated
      if (stat.downside && mod.value > 0) {
        mod.value = -mod.value;
      }
      mods.push(mod);
    }
  }
  return mods;
}

/**
 * Parse all community skill trees from the JSON data.
 */
export function parseAllCommunitySkillTrees(
  rawTrees: RawCommunityTree[],
): Map<string, SkillTree> {
  const map = new Map<string, SkillTree>();
  for (const raw of rawTrees) {
    const tree = parseCommunitySkillTree(raw);
    map.set(tree.skillId, tree);
  }
  return map;
}
