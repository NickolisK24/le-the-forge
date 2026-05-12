import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalSkill extends CanonicalRecord {
  owner_class_ids: string[];
  owner_mastery_ids: string[];
  skill_tree_id?: string | null;
  tags: string[];
  damage_types: string[];
}

export interface CanonicalSkillTreeNode extends CanonicalRecord {
  skill_tree_id?: string | null;
  max_points?: number | null;
  required_points?: number | null;
  position: Record<string, number>;
  modifier_references: CanonicalModifierReference[];
  text_effects: string[];
}

export interface CanonicalSkillTree extends CanonicalRecord {
  skill_id?: string | null;
  node_ids: string[];
  edges: Array<[string, string]>;
}
