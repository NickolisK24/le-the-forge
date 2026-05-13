import type { CanonicalItemBase } from "./canonicalItem";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalIdol extends CanonicalItemBase {
  idol_size?: string | null;
  idol_shape?: string | null;
  dimensions?: { width: number; height: number };
  allowed_affix_ids: string[];
  modifier_references?: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  stable_calculable?: boolean;
}

export interface CanonicalIdolAffix {
  canonical_id: string;
  display_name: string;
  source_id?: string | null;
  source_file?: string | null;
  support_status: string;
  trust_level: string;
  provenance: Record<string, unknown>;
  affix_domain: "idol";
  prefix_suffix?: string | null;
  idol_type_restrictions: string[];
  class_restrictions?: string[];
  mastery_restrictions?: string[];
  tier_ranges: Array<Record<string, unknown>>;
  modifier_references: CanonicalModifierReference[];
  modifier_rows?: Array<Record<string, unknown>>;
  stable_calculable?: boolean;
  warnings?: string[];
}
