export interface SourceProvenance {
  source_path: string;
  source_type: string;
  extraction_method: string;
  patch_version?: string | null;
  source_id?: string | null;
  schema_version: string;
  notes: string[];
  raw_reference: Record<string, unknown>;
}
