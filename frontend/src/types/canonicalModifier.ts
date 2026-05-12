import type { CanonicalRecord } from "./canonicalBase";

export interface CanonicalModifierReference {
  modifier_id: string;
  property?: string | null;
  property_path?: string | null;
  source_record_id?: string | null;
}

export interface CanonicalModifier extends CanonicalRecord {
  source_type: string;
  source_record_id?: string | null;
  stat_id?: string | null;
  operation: string;
  value_min?: number | null;
  value_max?: number | null;
  scaling?: string | null;
  tags: string[];
  conditions: Record<string, unknown>;
}
