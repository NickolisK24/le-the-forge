import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalImplicit extends CanonicalRecord {
  item_base_id?: string | null;
  item_type?: string | null;
  modifier_references: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  value_range?: {
    min?: number | null;
    max?: number | null;
    value_scale?: string | null;
    polarity?: string | null;
  };
  stable_calculable?: boolean;
}

export interface CanonicalItemBase extends CanonicalRecord {
  item_category?: string | null;
  item_type?: string | null;
  equipment_slot?: string | null;
  slot?: string | null;
  subtype?: string | null;
  classification?: "weapon" | "armor" | "accessory" | "idol" | "unknown" | string;
  level_requirement?: number | null;
  attribute_requirements?: Record<string, number>;
  requirements?: Record<string, unknown>;
  class_restrictions: string[];
  mastery_restrictions?: string[];
  implicit_ids: string[];
  base_stats?: Record<string, unknown>;
  stable_calculable?: boolean;
}
