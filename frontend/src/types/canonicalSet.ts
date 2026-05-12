import type { CanonicalItemBase } from "./canonicalItem";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalSetItem extends CanonicalItemBase {
  set_id?: string | null;
  base_item_id?: string | null;
  modifier_references: CanonicalModifierReference[];
}

export interface CanonicalSet extends CanonicalItemBase {
  item_ids: string[];
  bonus_modifier_references: CanonicalModifierReference[];
  bonus_text: string[];
}
