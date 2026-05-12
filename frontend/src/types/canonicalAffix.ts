import type { CanonicalRecord } from "./canonicalBase";
import type { CanonicalModifierReference } from "./canonicalModifier";

export interface CanonicalAffixTierRange {
  tier: number | string | null;
  min_value: number | null;
  max_value: number | null;
  tier_group?: string | null;
  value_scale?: string | null;
  polarity?: "positive" | "negative" | "mixed" | "unknown" | string;
}

export interface CanonicalAffix extends CanonicalRecord {
  affix_type?: string | null;
  prefix_suffix?: string | null;
  source_type?: string | null;
  affix_domain: "equipment" | "idol" | "unknown";
  tier_count?: number | null;
  item_applicability: string[];
  slot_restrictions: string[];
  item_type_restrictions: string[];
  class_restrictions: string[];
  mastery_restrictions: string[];
  tier_ranges: CanonicalAffixTierRange[];
  modifier_references: CanonicalModifierReference[];
  modifier_reference_count?: number | null;
  value_scale_policy: string;
  polarity_policy: string;
  stable_calculable: boolean;
}
