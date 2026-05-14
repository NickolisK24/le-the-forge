import type { CanonicalRecord } from "./canonicalBase";

export interface CanonicalClass extends CanonicalRecord {
  source_class_id?: number | string | null;
  source_tree_id?: string | null;
  mastery_ids: string[];
  passive_tree_ids: string[];
  skill_ids: string[];
  linked_skill_source_ids?: string[];
  linked_passive_tree_source_ids?: string[];
  known_restriction_labels?: string[];
  base_stats?: Record<string, unknown>;
  stable_calculable?: boolean;
  manual_bridge?: boolean;
}

export interface CanonicalMastery extends CanonicalRecord {
  source_class_id?: number | string | null;
  source_mastery_index?: number | null;
  source_mastery_id?: string | null;
  class_id?: string | null;
  passive_tree_ids: string[];
  skill_ids: string[];
  linked_skill_source_ids?: string[];
  linked_passive_tree_source_ids?: string[];
  known_restriction_labels?: string[];
  stable_calculable?: boolean;
  manual_bridge?: boolean;
}
