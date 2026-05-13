import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalPassiveNode extends CanonicalRecord {
  tree_id?: string | null;
  owner_class_id?: string | null;
  owner_mastery_id?: string | null;
  source_tree_id?: string | null;
  source_node_id?: number | string | null;
  mastery_index?: number | null;
  mastery_name?: string | null;
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

export interface CanonicalPassiveTree extends CanonicalRecord {
  owner_class_id?: string | null;
  owner_mastery_id?: string | null;
  source_tree_id?: string | null;
  node_ids: string[];
  edges: Array<[string, string]>;
  stable_calculable?: boolean;
}
