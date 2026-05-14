import type { SourceProvenance } from "./sourceProvenance";
import type { SupportStatus, TrustLevel } from "./trustStatus";

export interface CanonicalRecord {
  canonical_id: string;
  display_name: string;
  support_status: SupportStatus;
  trust_level: TrustLevel;
  provenance: SourceProvenance;
  source_id?: string | null;
  source_file?: string | null;
  patch_version?: string | null;
  warnings: string[];
  raw_reference: Record<string, unknown>;
  normalized_fields: Record<string, unknown>;
  consumer_safe_fields: Record<string, unknown>;
}
