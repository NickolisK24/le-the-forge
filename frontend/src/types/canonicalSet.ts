import type { CanonicalItemBase } from "./canonicalItem";
import type { CanonicalModifierReference } from "./canonicalModifier";
import type { UniqueSetSpecialMechanicClassification } from "./canonicalUnique";

export interface CanonicalSetItem extends CanonicalItemBase {
  set_id?: string | null;
  set_group_id?: string | null;
  set_group_display_name?: string | null;
  base_item_id?: string | null;
  modifier_references: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  tooltip_text?: string[];
  special_mechanic_classification?: UniqueSetSpecialMechanicClassification;
  stable_calculable?: boolean;
}

export interface CanonicalSet extends CanonicalItemBase {
  set_group_id?: string | null;
  set_group_display_name?: string | null;
  item_ids: string[];
  bonus_ids?: string[];
  bonus_modifier_references: CanonicalModifierReference[];
  bonus_text: string[];
  special_mechanic_classification?: UniqueSetSpecialMechanicClassification;
  stable_calculable?: boolean;
}

export interface CanonicalSetBonus {
  canonical_id: string;
  display_name: string;
  set_group_id: string;
  set_group_display_name?: string | null;
  required_pieces?: number | null;
  support_status: string;
  trust_level: string;
  description_text: string[];
  modifier_references: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  special_mechanic_classification: UniqueSetSpecialMechanicClassification;
  stable_calculable?: boolean;
}
