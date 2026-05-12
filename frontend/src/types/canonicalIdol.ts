import type { CanonicalItemBase } from "./canonicalItem";

export interface CanonicalIdol extends CanonicalItemBase {
  idol_size?: string | null;
  idol_shape?: string | null;
  allowed_affix_ids: string[];
}
