import type { CanonicalRecord } from "./canonicalBase";

export interface CanonicalClass extends CanonicalRecord {
  mastery_ids: string[];
  passive_tree_ids: string[];
  skill_ids: string[];
}

export interface CanonicalMastery extends CanonicalRecord {
  class_id?: string | null;
  passive_tree_ids: string[];
  skill_ids: string[];
}
