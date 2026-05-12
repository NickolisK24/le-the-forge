import type { CanonicalItemBase } from "./canonicalItem";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalUnique extends CanonicalItemBase {
  base_item_id?: string | null;
  unique_effect_text: string[];
  modifier_references: CanonicalModifierReference[];
}
