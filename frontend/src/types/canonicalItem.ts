import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalImplicit extends CanonicalRecord {
  modifier_references: CanonicalModifierReference[];
}

export interface CanonicalItemBase extends CanonicalRecord {
  item_type?: string | null;
  slot?: string | null;
  subtype?: string | null;
  level_requirement?: number | null;
  class_restrictions: string[];
  implicit_ids: string[];
}
