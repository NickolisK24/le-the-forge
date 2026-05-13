import type { V2ApiEnvelope } from "@/lib/v2ApiEnvelope";
import { getV2SourcePath, getV2Summary, isRecord, summarizeObject } from "@/lib/v2ApiEnvelope";

export interface V2ProvenanceSummary {
  hasProvenance: boolean;
  sourcePath: string;
  sourceLabel: string;
  validationStatus: string;
  provenanceDetails: string;
}

export interface V2WarningSummary {
  messages: string[];
  hasWarnings: boolean;
}

export function getV2ProvenanceSummary(response: V2ApiEnvelope | null | undefined): V2ProvenanceSummary {
  if (!response) {
    return {
      hasProvenance: false,
      sourcePath: "n/a",
      sourceLabel: "No provenance summary is available.",
      validationStatus: "Unknown validation status",
      provenanceDetails: "n/a",
    };
  }

  const sourcePath = getV2SourcePath(response);
  const provenance = response.provenance;
  const meta = response.meta;
  const debug = response.debug;
  const sourceLabel = pickString(
    provenance?.source,
    provenance?.source_type,
    provenance?.generated_artifact_source,
    meta?.domain,
    response.data_source,
    response.source_path,
  );
  const validationStatus = pickString(
    meta?.validation_status,
    debug?.validation_status,
    debug?.validation,
    response.success === true ? "available" : undefined,
  );
  const details = summarizeObject(provenance);

  return {
    hasProvenance: sourcePath !== "n/a" || details !== "n/a",
    sourcePath,
    sourceLabel: sourceLabel ? `Source information is available for ${sourceLabel}.` : "Source information is available for this data.",
    validationStatus: validationStatus ? `Validation status: ${validationStatus}` : "Validation status is not summarized.",
    provenanceDetails: details,
  };
}

export function getV2WarningSummary(response: V2ApiEnvelope | null | undefined): V2WarningSummary {
  if (!response) {
    return { hasWarnings: true, messages: ["No response data is available for trust and warning summaries."] };
  }

  const messages = new Set<string>();
  for (const warning of response.warnings ?? []) {
    if (typeof warning === "string" && warning.trim()) messages.add(warning.trim());
    else if (isRecord(warning)) {
      const message = pickString(warning.message, warning.reason, warning.code);
      if (message) messages.add(message);
    }
  }

  const summary = getV2Summary(response);
  const supportSummary = response.support_summary;
  const debug = response.debug;
  const meta = response.meta;

  if (hasPositiveKey(supportSummary, "unsupported") || hasPositiveKey(summary?.support_status_counts, "unsupported")) {
    messages.add("Some data is unsupported and remains visible for inspection only.");
  }
  if (hasAuditOnly(response, summary)) {
    messages.add("Value normalization is still audit-only.");
  }
  if (isDisplayOnly(response)) {
    messages.add("This data is display-only and is not used for planner calculations.");
  }
  if (stableCalculableUnavailable(response, summary)) {
    messages.add("This mechanic is not currently planner-calculable.");
  }
  if (hasBlockedReasons(response)) {
    messages.add(`Blocked reasons: ${summarizeObject(firstRecord(debug?.blocked_reason_counts, summary?.blocked_reason_counts))}`);
  }
  if (hasSkillIdentityGap(meta, debug, summary)) {
    messages.add("Some skill identity references are unresolved.");
  }
  if (getV2ProvenanceSummary(response).hasProvenance === false) {
    messages.add("No provenance summary is available.");
  }

  return {
    hasWarnings: messages.size > 0,
    messages: messages.size ? Array.from(messages) : ["No warnings or limitations are summarized for this response."],
  };
}

function pickString(...values: unknown[]): string {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function hasPositiveKey(value: unknown, key: string): boolean {
  if (!isRecord(value)) return false;
  const count = value[key];
  return count === true || (typeof count === "number" && count > 0);
}

function hasAuditOnly(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.meta?.value_normalization_status === "audit_only" ||
    response.debug?.value_normalization_status === "audit_only" ||
    summary?.value_normalization_status === "audit_only"
  );
}

function isDisplayOnly(response: V2ApiEnvelope): boolean {
  return response.read_only === true || response.meta?.read_only === true || response.debug?.read_only === true;
}

function stableCalculableUnavailable(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.support_summary?.stable_calculable === 0 ||
    summary?.stable_calculable_count === 0 ||
    summary?.stable_calculable === 0 ||
    response.debug?.planner_calculable_count === 0
  );
}

function hasBlockedReasons(response: V2ApiEnvelope): boolean {
  const summary = getV2Summary(response);
  return isRecord(response.debug?.blocked_reason_counts) || isRecord(summary?.blocked_reason_counts);
}

function firstRecord(...values: unknown[]): Record<string, unknown> | undefined {
  return values.find(isRecord);
}

function hasSkillIdentityGap(
  meta: Record<string, unknown> | undefined,
  debug: Record<string, unknown> | undefined,
  summary: Record<string, unknown> | undefined,
): boolean {
  return (
    hasPositiveKey(meta, "unresolved_skill_reference_count") ||
    hasPositiveKey(debug, "unresolved_skill_reference_count") ||
    hasPositiveKey(summary, "unresolved_skill_reference_count") ||
    hasPositiveKey(summary, "ambiguous_skill_reference_count")
  );
}
