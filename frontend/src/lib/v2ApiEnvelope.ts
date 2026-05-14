export interface V2ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface V2ApiEnvelope<TRecord = unknown> {
  success?: boolean;
  data?: {
    records?: TRecord[];
    sample_records?: TRecord[];
    record?: TRecord;
    debug_summary?: Record<string, unknown>;
    [key: string]: unknown;
  };
  meta?: Record<string, unknown>;
  support_summary?: Record<string, unknown>;
  warnings?: unknown[];
  provenance?: Record<string, unknown>;
  debug?: Record<string, unknown>;
  records?: TRecord[];
  sample_records?: TRecord[];
  record?: TRecord;
  debug_summary?: Record<string, unknown>;
  summary?: Record<string, unknown>;
  source_path?: string;
  data_source?: string;
  read_only?: boolean;
  production_consumer?: boolean;
  error?: string | V2ApiError;
  message?: string;
  [key: string]: unknown;
}

export function getV2Records<TRecord>(response: V2ApiEnvelope<TRecord> | null | undefined): TRecord[] {
  if (!response) return [];
  return response.records ?? response.sample_records ?? response.data?.records ?? response.data?.sample_records ?? [];
}

export function getV2Summary(response: V2ApiEnvelope | null | undefined): Record<string, unknown> | undefined {
  if (!response) return undefined;
  if (response.summary) return response.summary;
  const debugSummary = response.debug_summary ?? response.data?.debug_summary;
  if (isRecord(debugSummary) && isRecord(debugSummary.summary)) return debugSummary.summary;
  return undefined;
}

export function getV2SourcePath(response: V2ApiEnvelope | null | undefined): string {
  if (!response) return "n/a";
  const sourcePath = response.source_path ?? response.provenance?.source_path;
  return typeof sourcePath === "string" && sourcePath ? sourcePath : "n/a";
}

export function getV2ErrorMessage(response: V2ApiEnvelope | null | undefined, fallback = "Debug endpoint returned an error."): string {
  if (!response) return fallback;
  if (typeof response.error === "string") return response.message || response.error;
  if (isRecord(response.error)) {
    const message = response.error.message;
    const code = response.error.code;
    if (typeof message === "string" && message) return message;
    if (typeof code === "string" && code) return code;
  }
  return response.message || fallback;
}

export function summarizeV2Support(response: V2ApiEnvelope | null | undefined): string {
  if (response?.support_summary && Object.keys(response.support_summary).length > 0) {
    return summarizeObject(response.support_summary);
  }
  return summarizeMap(getV2Summary(response), "support_status_counts");
}

export function summarizeMap(summary: Record<string, unknown> | undefined, key: string): string {
  const value = summary?.[key];
  if (!isRecord(value)) return "n/a";
  return summarizeObject(value);
}

export function summarizeObject(value: Record<string, unknown> | undefined): string {
  if (!value) return "n/a";
  const entries = Object.entries(value).filter(([, entryValue]) => entryValue !== undefined && entryValue !== null);
  if (!entries.length) return "n/a";
  return entries.map(([name, count]) => `${name}: ${String(count)}`).join(", ");
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
