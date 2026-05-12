import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalAffix extends CanonicalRecord {
  affix_type?: string | null;
  tier_count?: number | null;
  item_applicability: string[];
  class_restrictions: string[];
  modifier_references: CanonicalModifierReference[];
}
