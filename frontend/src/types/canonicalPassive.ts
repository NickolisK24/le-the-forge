import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalPassiveNode extends CanonicalRecord {
  tree_id?: string | null;
  max_points?: number | null;
  required_points?: number | null;
  position: Record<string, number>;
  modifier_references: CanonicalModifierReference[];
  text_effects: string[];
}

export interface CanonicalPassiveTree extends CanonicalRecord {
  owner_class_id?: string | null;
  owner_mastery_id?: string | null;
  node_ids: string[];
  edges: Array<[string, string]>;
}
