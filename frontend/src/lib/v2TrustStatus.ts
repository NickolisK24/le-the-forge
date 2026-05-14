import type { V2ApiEnvelope } from "@/lib/v2ApiEnvelope";
import { getV2Summary, isRecord } from "@/lib/v2ApiEnvelope";

export type V2BadgeTone = "green" | "blue" | "amber" | "red" | "purple" | "gray" | "slate";

export interface V2BadgeDefinition {
  key: string;
  label: string;
  title: string;
  tone: V2BadgeTone;
}

const SUPPORT_BADGES: Record<string, V2BadgeDefinition> = {
  trusted: {
    key: "trusted",
    label: "Trusted Data",
    title: "This data is trusted by the current v2 support policy.",
    tone: "green",
  },
  supported: {
    key: "supported",
    label: "Supported",
    title: "This data is supported for its current trusted-data use.",
    tone: "green",
  },
  partial: {
    key: "partial",
    label: "Partial Support",
    title: "This data is available, but some mechanics or calculations are not supported.",
    tone: "amber",
  },
  unsupported: {
    key: "unsupported",
    label: "Unsupported",
    title: "This data is visible for inspection but is not mechanically supported.",
    tone: "red",
  },
  "audit-only": {
    key: "audit-only",
    label: "Audit Only",
    title: "This data is available for audit and explanation, not planner math.",
    tone: "purple",
  },
  "display-only": {
    key: "display-only",
    label: "Display Only",
    title: "This data may be shown as metadata but must not be used for calculations.",
    tone: "blue",
  },
  experimental: {
    key: "experimental",
    label: "Experimental",
    title: "This route or data surface is experimental and read-only.",
    tone: "purple",
  },
  "not-planner-calculable": {
    key: "not-planner-calculable",
    label: "Not Planner-Calculable",
    title: "This data is not eligible for production planner calculations.",
    tone: "slate",
  },
  unknown: {
    key: "unknown",
    label: "Unknown Status",
    title: "No recognized support status was provided.",
    tone: "gray",
  },
};

const TRUST_BADGES: Record<string, V2BadgeDefinition> = {
  trusted: {
    key: "trusted",
    label: "Trusted Data",
    title: "The record is trusted by the current v2 policy for its supported use.",
    tone: "green",
  },
  generated: {
    key: "generated",
    label: "Generated",
    title: "The record was generated from source data.",
    tone: "blue",
  },
  validated: {
    key: "validated",
    label: "Validated",
    title: "The record has validation evidence in the v2 report pipeline.",
    tone: "green",
  },
  "provenance-available": {
    key: "provenance-available",
    label: "Provenance Available",
    title: "Source or extraction provenance is available for inspection.",
    tone: "blue",
  },
  blocked: {
    key: "blocked",
    label: "Blocked",
    title: "The record is blocked from planner-safe calculation by current policy.",
    tone: "red",
  },
  warning: {
    key: "warning",
    label: "Warning",
    title: "The record has warnings or limitations that should remain visible.",
    tone: "amber",
  },
  unknown: {
    key: "unknown",
    label: "Unknown Trust",
    title: "No recognized trust status was provided.",
    tone: "gray",
  },
};

export function getSupportBadge(status: unknown): V2BadgeDefinition {
  return SUPPORT_BADGES[normalizeSupportStatus(status)] ?? SUPPORT_BADGES.unknown;
}

export function getTrustBadge(status: unknown): V2BadgeDefinition {
  return TRUST_BADGES[normalizeTrustStatus(status)] ?? TRUST_BADGES.unknown;
}

export function normalizeSupportStatus(status: unknown): string {
  const value = normalizeKey(status);
  if (!value) return "unknown";
  if (["trusted", "trustworthy"].includes(value)) return "trusted";
  if (["supported", "support"].includes(value)) return "supported";
  if (["partial", "partially_supported", "partial_support"].includes(value)) return "partial";
  if (["unsupported", "not_supported"].includes(value)) return "unsupported";
  if (["audit_only", "audit-only", "audit"].includes(value)) return "audit-only";
  if (["display_only", "display-only", "metadata_only", "identity_only_metadata"].includes(value)) return "display-only";
  if (["experimental", "exp"].includes(value)) return "experimental";
  if (["not_planner_calculable", "not-planner-calculable", "planner_calculable_false"].includes(value)) {
    return "not-planner-calculable";
  }
  return "unknown";
}

export function normalizeTrustStatus(status: unknown): string {
  const value = normalizeKey(status);
  if (!value) return "unknown";
  if (["trusted", "trusted_data"].includes(value)) return "trusted";
  if (["generated", "generated_from_game_data"].includes(value)) return "generated";
  if (["validated", "valid"].includes(value)) return "validated";
  if (["provenance", "provenance_available", "source_path"].includes(value)) return "provenance-available";
  if (["blocked", "not_stable_calculable", "not_planner_calculable"].includes(value)) return "blocked";
  if (["warning", "warnings"].includes(value)) return "warning";
  return "unknown";
}

export function getV2EnvelopeBadges(response: V2ApiEnvelope | null | undefined): V2BadgeDefinition[] {
  if (!response) return [getSupportBadge("unknown")];

  const summary = getV2Summary(response);
  const badges = new Map<string, V2BadgeDefinition>();
  for (const status of collectStatusKeys(response.support_summary)) addBadge(badges, getSupportBadge(status));
  for (const status of collectStatusKeys(summary?.support_status_counts)) addBadge(badges, getSupportBadge(status));
  for (const status of collectStatusKeys(summary?.trust_level_counts)) addBadge(badges, getTrustBadge(status));

  if (response.meta?.experimental === true || response.experimental === true) addBadge(badges, getSupportBadge("experimental"));
  if (response.read_only === true || response.meta?.read_only === true) addBadge(badges, getSupportBadge("display-only"));
  if (hasProvenance(response)) addBadge(badges, getTrustBadge("provenance"));
  if (hasWarnings(response)) addBadge(badges, getTrustBadge("warning"));
  if (hasAuditOnlyStatus(response, summary)) addBadge(badges, getSupportBadge("audit-only"));
  if (stableCalculableIsZero(response, summary)) addBadge(badges, getSupportBadge("not-planner-calculable"));

  if (!badges.size) addBadge(badges, getSupportBadge("unknown"));
  return Array.from(badges.values());
}

function addBadge(badges: Map<string, V2BadgeDefinition>, badge: V2BadgeDefinition) {
  badges.set(badge.key, badge);
}

function collectStatusKeys(value: unknown): string[] {
  if (!isRecord(value)) return [];
  return Object.entries(value)
    .filter(([, count]) => count !== undefined && count !== null && count !== 0)
    .map(([key]) => key);
}

function hasProvenance(response: V2ApiEnvelope): boolean {
  return Boolean(response.provenance && Object.keys(response.provenance).length > 0);
}

function hasWarnings(response: V2ApiEnvelope): boolean {
  return Array.isArray(response.warnings) && response.warnings.length > 0;
}

function hasAuditOnlyStatus(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.meta?.value_normalization_status === "audit_only" ||
    summary?.value_normalization_status === "audit_only" ||
    response.debug?.value_normalization_status === "audit_only"
  );
}

function stableCalculableIsZero(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.support_summary?.stable_calculable === 0 ||
    summary?.stable_calculable_count === 0 ||
    summary?.stable_calculable === 0
  );
}

function normalizeKey(status: unknown): string {
  if (typeof status !== "string") return "";
  return status.trim().toLowerCase().replace(/\s+/g, "_");
}
