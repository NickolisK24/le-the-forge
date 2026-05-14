import type { CanonicalItemBase } from "./canonicalItem";
import type { CanonicalModifierReference } from "./canonicalModifier";

export type UniqueSetSpecialMechanicClassification =
  | "trusted_modifier"
  | "partial_modifier"
  | "text_only_effect"
  | "scripted_runtime_behavior"
  | "unsupported_special_behavior"
  | "unknown";

export interface CanonicalUnique extends CanonicalItemBase {
  base_item_id?: string | null;
  unique_effect_text: string[];
  modifier_references: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  tooltip_text?: string[];
  special_mechanic_classification?: UniqueSetSpecialMechanicClassification;
  stable_calculable?: boolean;
  legendary_type?: string | null;
  implicit_links?: Array<Record<string, unknown>>;
}
