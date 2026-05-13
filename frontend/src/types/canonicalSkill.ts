import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalSkill extends CanonicalRecord {
  owner_class_ids: string[];
  owner_mastery_ids: string[];
  source_skill_id?: string | null;
  skill_tree_id?: string | null;
  skill_tags: string[];
  damage_types: string[];
  scaling_tags: string[];
  cost?: Record<string, unknown>;
  cast_data?: Record<string, unknown>;
  cooldown?: Record<string, unknown>;
  requirements?: Record<string, unknown>;
  behavior_flags?: Record<string, unknown>;
  description_text?: string | null;
  tooltip_text?: string | null;
  text_effects: string[];
  special_behavior_classification?: string;
  damage_source_status?: string | null;
  stable_calculable?: boolean;
}

export interface CanonicalSkillTreeNode extends CanonicalRecord {
  skill_tree_id?: string | null;
  skill_id?: string | null;
  owner_class_ids?: string[];
  owner_mastery_ids?: string[];
  source_tree_id?: string | null;
  source_node_id?: number | string | null;
  max_points?: number | null;
  required_points?: number | null;
  position: Record<string, number>;
  connections?: string[];
  edge_requirements?: Array<{ node_id: string; points: number }>;
  node_type?: string | null;
  modifier_references: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  description_text?: string | null;
  tooltip_text?: string | null;
  text_effects: string[];
  special_behavior_classification?: string;
  effect_hint_classifications?: string[];
  stable_calculable?: boolean;
}

export interface CanonicalSkillTree extends CanonicalRecord {
  skill_id?: string | null;
  owner_class_ids?: string[];
  owner_mastery_ids?: string[];
  source_tree_id?: string | null;
  source_tree_class_name?: string | null;
  node_ids: string[];
  edges: Array<[string, string]>;
  stable_calculable?: boolean;
}
