import type {
  FrontendTrustReportIntegrationData,
  TrustReportDiagnostic,
  TrustReportSourceStatus,
} from "@/types/frontendTrustReportIntegration";
import {
  FRONTEND_TRUST_SURFACE_NON_AUTHORITY_STATEMENT,
  FRONTEND_TRUST_SURFACE_REPOSITORY_REMAINS,
} from "@/lib/frontendTrustSurfaceData";

export const FRONTEND_TRUST_REPORT_INTEGRATION_ID =
  "v4_5c_2_frontend_trust_report_integration";

export const FRONTEND_TRUST_REPORT_PATH =
  "docs/generated/v4_5c_1_frontend_trust_surface_foundations_report.json";

export const FRONTEND_TRUST_REPORT_HASH =
  "fe46403f3bc8d50346f3b154e737aff7c8b5171e820c176411cfa7635f8433cb";

export const FRONTEND_TRUST_REPORT_REPOSITORY_REMAINS = [
  ...FRONTEND_TRUST_SURFACE_REPOSITORY_REMAINS,
  "NON-triaging",
] as const;

const PRESERVED_PROHIBITIONS = [
  "planner execution",
  "planner recommendations",
  "planner ranking",
  "trust scoring",
  "evidence scoring",
  "confidence scoring",
  "authorization semantics",
  "approval semantics",
  "production enablement",
  "runtime mutation",
  "operational mutation",
  "report-driven planner behavior",
] as const;

const DESCRIPTIVE_GUARANTEES = [
  "deterministic",
  "read-only",
  "governance-safe",
  "fail-visible",
  "descriptive-only",
  "publicly transparent",
] as const;

const UNSUPPORTED_OPERATIONAL_STATES = [
  "planner authority",
  "execution safety",
  "correctness guarantee",
  "operational readiness",
  "recommendation quality",
  "ranking quality",
  "scoring quality",
  "production enablement",
] as const;

const REPORT_BACKED_DIAGNOSTICS: readonly TrustReportDiagnostic[] = [
  {
    id: "report-metadata-present",
    label: "Report metadata present",
    state: "ok",
    message: "Generated trust report metadata is visible and read-only.",
    readOnly: true,
    descriptiveOnly: true,
  },
  {
    id: "report-hash-present",
    label: "Report hash visible",
    state: "ok",
    message: "The deterministic report hash is shown as evidence, not as a score.",
    readOnly: true,
    descriptiveOnly: true,
  },
  {
    id: "fallback-inactive",
    label: "Fallback data inactive",
    state: "ok",
    message: "Static fallback data remains available but is not masking report metadata.",
    readOnly: true,
    descriptiveOnly: true,
  },
  {
    id: "unsupported-states-visible",
    label: "Unsupported states visible",
    state: "ok",
    message: "Unsupported states remain visible in report-backed and fallback views.",
    readOnly: true,
    descriptiveOnly: true,
  },
];

export const FRONTEND_TRUST_REPORT_INTEGRATION_DATA: FrontendTrustReportIntegrationData = {
  integrationId: FRONTEND_TRUST_REPORT_INTEGRATION_ID,
  sourceStatus: "report_backed",
  metadata: {
    reportName: "v4.5C.1 frontend trust surface foundations report",
    reportPath: FRONTEND_TRUST_REPORT_PATH,
    reportHash: FRONTEND_TRUST_REPORT_HASH,
    certificationStatus: "read_only_descriptive_frontend_trust_surface_certified",
    generatedAt: "2026-05-18T00:00:00+00:00",
    readinessClassifications: [
      "frontend trust surface foundation ready for read-only report integration",
    ],
    descriptiveOnlyGuaranteeText: FRONTEND_TRUST_SURFACE_NON_AUTHORITY_STATEMENT,
    readOnly: true,
    descriptiveOnly: true,
  },
  sourceVisibility: {
    generatedReportPath: FRONTEND_TRUST_REPORT_PATH,
    staticFallbackSource: "frontend/src/lib/frontendTrustSurfaceData.ts",
    reportBackedSourceStatus: "report_backed",
    unavailableReportSourceStatus: "report_unavailable",
    sourceVisibilityNote:
      "Report-backed metadata is visible while deterministic fallback data remains explicit.",
    readOnly: true,
    descriptiveOnly: true,
  },
  fallbackState: {
    fallbackActive: false,
    fallbackLabel: "Report-backed trust metadata active",
    fallbackSource: "frontend/src/lib/frontendTrustSurfaceData.ts",
    fallbackReason:
      "Fallback data is preserved for deterministic read-only rendering if report metadata is unavailable.",
    fallbackVisibilityNote:
      "Fallback is never silent; active fallback state is shown with diagnostics.",
    readOnly: true,
    descriptiveOnly: true,
  },
  certificationSummaries: [
    {
      id: "repository-remains",
      label: "Repository remains",
      values: FRONTEND_TRUST_REPORT_REPOSITORY_REMAINS,
      readOnly: true,
      descriptiveOnly: true,
    },
    {
      id: "preserved-prohibitions",
      label: "Preserved prohibitions",
      values: PRESERVED_PROHIBITIONS,
      readOnly: true,
      descriptiveOnly: true,
    },
    {
      id: "descriptive-guarantees",
      label: "Descriptive-only guarantees",
      values: DESCRIPTIVE_GUARANTEES,
      readOnly: true,
      descriptiveOnly: true,
    },
    {
      id: "unsupported-operational-states",
      label: "Unsupported operational states",
      values: UNSUPPORTED_OPERATIONAL_STATES,
      readOnly: true,
      descriptiveOnly: true,
    },
  ],
  diagnostics: REPORT_BACKED_DIAGNOSTICS,
  repositoryRemains: FRONTEND_TRUST_REPORT_REPOSITORY_REMAINS,
  readOnly: true,
  descriptiveOnly: true,
} as const;

export function buildFallbackTrustReportIntegration(
  sourceStatus: TrustReportSourceStatus = "report_unavailable",
): FrontendTrustReportIntegrationData {
  return {
    ...FRONTEND_TRUST_REPORT_INTEGRATION_DATA,
    sourceStatus,
    sourceVisibility: {
      ...FRONTEND_TRUST_REPORT_INTEGRATION_DATA.sourceVisibility,
      reportBackedSourceStatus: sourceStatus,
      sourceVisibilityNote:
        "Generated report metadata is unavailable; deterministic fallback data is active and visible.",
    },
    fallbackState: {
      ...FRONTEND_TRUST_REPORT_INTEGRATION_DATA.fallbackState,
      fallbackActive: true,
      fallbackLabel: "Fallback deterministic trust data active",
      fallbackReason:
        "Generated report metadata is unavailable, malformed, or missing required fields.",
      fallbackVisibilityNote:
        "Fallback data is being shown explicitly and remains read-only.",
    },
    diagnostics: [
      {
        id: "report-unavailable",
        label: "Report unavailable",
        state: "warning",
        message: "Generated trust report metadata is unavailable; fallback data is visible.",
        readOnly: true,
        descriptiveOnly: true,
      },
      {
        id: "fallback-data-active",
        label: "Fallback data active",
        state: "warning",
        message: "Deterministic fallback trust data is active and explicitly labeled.",
        readOnly: true,
        descriptiveOnly: true,
      },
      {
        id: "metadata-missing",
        label: "Report metadata missing",
        state: "blocker",
        message: "Missing report metadata remains fail-visible and does not trigger recovery.",
        readOnly: true,
        descriptiveOnly: true,
      },
      {
        id: "unsupported-states-preserved",
        label: "Unsupported states preserved",
        state: "ok",
        message: "Unsupported-state visibility is preserved while fallback data is active.",
        readOnly: true,
        descriptiveOnly: true,
      },
    ],
  };
}

export function getFrontendTrustReportIntegrationData(): FrontendTrustReportIntegrationData {
  return FRONTEND_TRUST_REPORT_INTEGRATION_DATA;
}

export function isFrontendTrustReportIntegrationReadOnly(
  data: FrontendTrustReportIntegrationData = FRONTEND_TRUST_REPORT_INTEGRATION_DATA,
): boolean {
  return (
    data.readOnly &&
    data.descriptiveOnly &&
    data.metadata.readOnly &&
    data.metadata.descriptiveOnly &&
    data.sourceVisibility.readOnly &&
    data.sourceVisibility.descriptiveOnly &&
    data.fallbackState.readOnly &&
    data.fallbackState.descriptiveOnly &&
    data.certificationSummaries.every((item) => item.readOnly && item.descriptiveOnly) &&
    data.diagnostics.every((item) => item.readOnly && item.descriptiveOnly)
  );
}
