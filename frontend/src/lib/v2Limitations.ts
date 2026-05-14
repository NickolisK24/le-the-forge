import type { V2ApiEnvelope } from "@/lib/v2ApiEnvelope";
import { getV2Summary, isRecord } from "@/lib/v2ApiEnvelope";

export type V2LimitationCode =
  | "display_only"
  | "audit_only_value_normalization"
  | "not_planner_calculable"
  | "unsupported_mechanics"
  | "partial_support"
  | "unresolved_skill_identity"
  | "missing_provenance"
  | "experimental_only"
  | "stable_calculable_unavailable"
  | "production_not_consuming_v2"
  | "unknown_limitation";

export interface V2LimitationCopy {
  code: V2LimitationCode;
  label: string;
  compact: string;
  full: string;
}

export const V2_LIMITATION_COPY: Record<V2LimitationCode, V2LimitationCopy> = {
  display_only: {
    code: "display_only",
    label: "Display-only data",
    compact: "This data is display-only and is not used for planner calculations.",
    full:
      "This trusted data can help identify, inspect, or explain records, but it is not used for damage, defense, crafting, or build calculations.",
  },
  audit_only_value_normalization: {
    code: "audit_only_value_normalization",
    label: "Audit-only value normalization",
    compact: "Value normalization is still audit-only.",
    full:
      "Source values are still being audited. They must not be treated as planner-normalized stat values until explicit scale evidence and tests exist.",
  },
  not_planner_calculable: {
    code: "not_planner_calculable",
    label: "Not planner-calculable",
    compact: "This mechanic is not currently planner-calculable.",
    full:
      "The record can be visible as trusted metadata, but it is blocked from planner math until every safety gate passes.",
  },
  unsupported_mechanics: {
    code: "unsupported_mechanics",
    label: "Unsupported mechanics",
    compact: "Some mechanics are unsupported and remain visible for inspection only.",
    full:
      "Unsupported mechanics are shown so limitations are visible, not because their behavior has been implemented or inferred.",
  },
  partial_support: {
    code: "partial_support",
    label: "Partial support",
    compact: "This data has partial support.",
    full:
      "Some parts of this data are available for display or audit, while mechanical behavior can still be blocked.",
  },
  unresolved_skill_identity: {
    code: "unresolved_skill_identity",
    label: "Unresolved skill identity",
    compact: "Some skill identity references are unresolved.",
    full:
      "Some skill ownership references remain unresolved or ambiguous. No bridge is assumed from display names, nested evidence, or tooltip text.",
  },
  missing_provenance: {
    code: "missing_provenance",
    label: "Missing provenance",
    compact: "No provenance summary is available.",
    full:
      "This response does not include a concise source or validation summary, so it should stay inspectable and cautious.",
  },
  experimental_only: {
    code: "experimental_only",
    label: "Experimental-only",
    compact: "This surface is experimental and read-only.",
    full:
      "Experimental v2 surfaces are intended for inspection and trust review. They are not production planner integration points.",
  },
  stable_calculable_unavailable: {
    code: "stable_calculable_unavailable",
    label: "Stable calculation unavailable",
    compact: "Stable-calculable planner support is unavailable for this data.",
    full:
      "Stable-calculable status is controlled by backend safety policy and currently remains unavailable for this data.",
  },
  production_not_consuming_v2: {
    code: "production_not_consuming_v2",
    label: "Production planner unchanged",
    compact: "Production planner calculations do not consume v2 data yet.",
    full:
      "The current planner output remains based on existing production paths. v2 trusted data is not used for production calculations.",
  },
  unknown_limitation: {
    code: "unknown_limitation",
    label: "Unknown limitation",
    compact: "A limitation exists, but this UI does not recognize its specific type.",
    full:
      "This data should be treated cautiously until its trust, provenance, and planner eligibility are clearer.",
  },
};

export function normalizeV2LimitationCode(code: unknown): V2LimitationCode {
  if (typeof code !== "string") return "unknown_limitation";
  const normalized = code.trim().toLowerCase().replace(/[\s-]+/g, "_");
  if (normalized in V2_LIMITATION_COPY) return normalized as V2LimitationCode;
  if (normalized === "audit_only") return "audit_only_value_normalization";
  if (normalized === "display_only_metadata" || normalized === "identity_only_metadata") return "display_only";
  if (normalized === "not_stable_calculable") return "stable_calculable_unavailable";
  if (normalized === "unsupported" || normalized === "unsupported_behavior") return "unsupported_mechanics";
  if (normalized === "unresolved_identity" || normalized === "unresolved_skill_reference") return "unresolved_skill_identity";
  return "unknown_limitation";
}

export function getV2LimitationCopy(code: unknown): V2LimitationCopy {
  return V2_LIMITATION_COPY[normalizeV2LimitationCode(code)];
}

export function getV2LimitationCodes(response: V2ApiEnvelope | null | undefined): V2LimitationCode[] {
  if (!response) return ["unknown_limitation"];

  const summary = getV2Summary(response);
  const codes = new Set<V2LimitationCode>();
  const supportSummary = response.support_summary;

  if (response.read_only === true || response.meta?.read_only === true || response.debug?.read_only === true) {
    codes.add("display_only");
  }
  if (response.experimental === true || response.meta?.experimental === true) {
    codes.add("experimental_only");
  }
  if (hasAuditOnly(response, summary)) {
    codes.add("audit_only_value_normalization");
  }
  if (hasPlannerBlocked(response, summary)) {
    codes.add("not_planner_calculable");
  }
  if (hasStableCalculableZero(response, summary)) {
    codes.add("stable_calculable_unavailable");
  }
  if (hasPositiveKey(supportSummary, "unsupported") || hasPositiveKey(summary?.support_status_counts, "unsupported")) {
    codes.add("unsupported_mechanics");
  }
  if (hasPositiveKey(supportSummary, "partial") || hasPositiveKey(summary?.support_status_counts, "partial")) {
    codes.add("partial_support");
  }
  if (hasSkillIdentityGap(response, summary)) {
    codes.add("unresolved_skill_identity");
  }
  if (!hasProvenance(response)) {
    codes.add("missing_provenance");
  }
  if (productionV2ConsumptionIsFalse(response, summary)) {
    codes.add("production_not_consuming_v2");
  }

  return Array.from(codes);
}

function hasAuditOnly(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.meta?.value_normalization_status === "audit_only" ||
    response.debug?.value_normalization_status === "audit_only" ||
    summary?.value_normalization_status === "audit_only"
  );
}

function hasPlannerBlocked(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.debug?.planner_calculable_count === 0 ||
    response.debug?.planner_calculable === false ||
    summary?.planner_calculable_count === 0 ||
    summary?.planner_calculable === false ||
    hasStableCalculableZero(response, summary)
  );
}

function hasStableCalculableZero(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.support_summary?.stable_calculable === 0 ||
    summary?.stable_calculable_count === 0 ||
    summary?.stable_calculable === 0
  );
}

function hasSkillIdentityGap(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    hasPositiveKey(response.meta, "unresolved_skill_reference_count") ||
    hasPositiveKey(response.debug, "unresolved_skill_reference_count") ||
    hasPositiveKey(summary, "unresolved_skill_reference_count") ||
    hasPositiveKey(summary, "ambiguous_skill_reference_count")
  );
}

function hasProvenance(response: V2ApiEnvelope): boolean {
  return Boolean(response.provenance && Object.keys(response.provenance).length > 0);
}

function productionV2ConsumptionIsFalse(response: V2ApiEnvelope, summary: Record<string, unknown> | undefined): boolean {
  return (
    response.meta?.production_consumed === false ||
    response.debug?.production_consumed === false ||
    summary?.production_consumed === false ||
    summary?.production_consumption_status === "false"
  );
}

function hasPositiveKey(value: unknown, key: string): boolean {
  if (!isRecord(value)) return false;
  const count = value[key];
  return count === true || (typeof count === "number" && count > 0);
}
