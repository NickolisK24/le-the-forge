import type {
  BackendTrustDiagnosticPayload,
  BackendTrustFetchStatus,
  BackendTrustFrontendDisplayReadiness,
  BackendTrustFrontendDisplayReadinessPayload,
  BackendTrustVisibilityReference,
  BackendTrustVisibilityReferencePayload,
  BackendTrustVisibilityPayload,
  BackendTrustVisibilityState,
  BackendTrustVisibilitySummary,
  BackendTrustVisibilitySummaryPayload,
  FrontendBackendAlignmentStatus,
} from "@/types/frontendTrustBackendVisibility";

export const BACKEND_TRUST_VISIBILITY_ENDPOINT = "/api/trust/visibility";
export const BACKEND_TRUST_VISIBILITY_SCHEMA_VERSION = "v4.5d.3";
export const FRONTEND_BACKEND_ALIGNMENT_ENDPOINT_VISIBLE =
  "frontend_backend_alignment_endpoint_visible" as const;
export const FRONTEND_BACKEND_ALIGNMENT_EXPANDED_VISIBLE =
  "frontend_backend_alignment_expanded_payload_visible" as const;
export const FRONTEND_BACKEND_ALIGNMENT_EXPANDED_PARTIAL =
  "frontend_backend_alignment_expanded_payload_partially_visible" as const;
export const FRONTEND_BACKEND_ALIGNMENT_FETCH_FALLBACK =
  "frontend_backend_alignment_fetch_attempted_with_fail_visible_fallback" as const;

type BackendTrustFetch = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Pick<Response, "ok" | "status" | "json">>;

const FALLBACK_REPORT_REFERENCE = {
  name: "backend_trust_visibility_report_unavailable",
  path: "docs/generated/v4_5d_3_backend_trust_payload_expansion_report.json",
  hash: "missing",
  available: false,
  status: "unavailable",
} as const;

const READ_ONLY_DIAGNOSTIC_FLAGS = {
  readOnly: true,
  descriptiveOnly: true,
} as const;

const FALLBACK_TRUST_SUMMARY: BackendTrustVisibilitySummary = {
  summaryId: "backend_trust_visibility_summary_unavailable",
  status: "unavailable",
  sourceType: "deterministic_frontend_fallback",
  schemaVersion: "unavailable",
  reportReferenceId: "missing",
  description: "Expanded backend trust summary is unavailable; deterministic fallback remains visible.",
  readOnly: true,
  descriptiveOnly: true,
};

const FALLBACK_FRONTEND_DISPLAY_READINESS: BackendTrustFrontendDisplayReadiness = {
  status: "expanded_backend_payload_unavailable",
  description: "Expanded backend payload rendering is unavailable; fallback trust visibility remains active.",
  frontendRoute: "/trusted-data/frontend-trust",
  expandedRenderingAuthorized: false,
  descriptiveOnly: true,
  readOnly: true,
};

function diagnostic(
  id: string,
  severity: BackendTrustVisibilityState["diagnostics"][number]["severity"],
  message: string,
): BackendTrustVisibilityState["diagnostics"][number] {
  return {
    id,
    severity,
    message,
    ...READ_ONLY_DIAGNOSTIC_FLAGS,
  };
}

function normalizeDiagnostic(
  item: BackendTrustDiagnosticPayload,
): BackendTrustVisibilityState["diagnostics"][number] {
  const severity =
    item.severity === "warning" || item.severity === "blocker"
      ? item.severity
      : "informational";
  return diagnostic(
    item.id || "backend-diagnostic",
    severity,
    item.message || "Backend trust endpoint diagnostic is visible.",
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeSummary(
  summary: BackendTrustVisibilitySummaryPayload | undefined,
): BackendTrustVisibilitySummary {
  if (!summary) {
    return FALLBACK_TRUST_SUMMARY;
  }
  return {
    summaryId: summary.summary_id || FALLBACK_TRUST_SUMMARY.summaryId,
    status: summary.status || FALLBACK_TRUST_SUMMARY.status,
    sourceType: summary.source_type || FALLBACK_TRUST_SUMMARY.sourceType,
    schemaVersion: summary.schema_version || FALLBACK_TRUST_SUMMARY.schemaVersion,
    reportReferenceId:
      summary.report_reference_id || FALLBACK_TRUST_SUMMARY.reportReferenceId,
    description: summary.description || FALLBACK_TRUST_SUMMARY.description,
    readOnly: true,
    descriptiveOnly: true,
  };
}

function normalizeReference(
  item: BackendTrustVisibilityReferencePayload,
): BackendTrustVisibilityReference {
  return {
    id: item.id || "backend_visibility_reference",
    status: item.status || "unknown",
    scope: item.scope || "not_specified",
    state: item.state || item.status || "not_specified",
    description: item.description || "Backend visibility reference is descriptive-only.",
    failVisible: item.fail_visible === true,
    readOnly: true,
    descriptiveOnly: true,
  };
}

function normalizeReferences(
  items: readonly BackendTrustVisibilityReferencePayload[] | undefined,
): readonly BackendTrustVisibilityReference[] {
  return items?.map(normalizeReference) ?? [];
}

function normalizeDisplayReadiness(
  readiness: BackendTrustFrontendDisplayReadinessPayload | undefined,
): BackendTrustFrontendDisplayReadiness {
  if (!readiness) {
    return FALLBACK_FRONTEND_DISPLAY_READINESS;
  }
  return {
    status: readiness.status || FALLBACK_FRONTEND_DISPLAY_READINESS.status,
    description:
      readiness.description || FALLBACK_FRONTEND_DISPLAY_READINESS.description,
    frontendRoute:
      readiness.frontend_route || FALLBACK_FRONTEND_DISPLAY_READINESS.frontendRoute,
    expandedRenderingAuthorized: readiness.expanded_rendering_authorized === true,
    descriptiveOnly: readiness.descriptive_only !== false,
    readOnly: true,
  };
}

function expandedPayloadSectionCount(payload: BackendTrustVisibilityPayload): number {
  return [
    Boolean(payload.trust_visibility),
    Boolean(payload.support_statuses?.length),
    Boolean(payload.explainability_references?.length),
    Boolean(payload.evidence_panel_references?.length),
    Boolean(payload.provenance_references?.length),
    Boolean(payload.lineage_references?.length),
    Boolean(payload.coverage_references?.length),
    Boolean(payload.confidence_references?.length),
    Boolean(payload.unsupported_states?.length),
    Boolean(payload.preserved_prohibitions?.length),
    Boolean(payload.frontend_display_readiness),
  ].filter(Boolean).length;
}

export function isBackendTrustVisibilityPayload(
  value: unknown,
): value is BackendTrustVisibilityPayload {
  return isRecord(value) && typeof value.schema_version === "string";
}

export function buildBackendTrustFetchFallback(
  fetchStatus: Exclude<BackendTrustFetchStatus, "endpoint_visible">,
  message = "Backend fetch unavailable - showing deterministic fallback.",
): BackendTrustVisibilityState {
  const frontendBackendAlignmentStatus: FrontendBackendAlignmentStatus =
    fetchStatus === "pending"
      ? FRONTEND_BACKEND_ALIGNMENT_FETCH_FALLBACK
      : FRONTEND_BACKEND_ALIGNMENT_FETCH_FALLBACK;
  return {
    endpointRoute: BACKEND_TRUST_VISIBILITY_ENDPOINT,
    endpointAvailable: false,
    fetchStatus,
    schemaVersion: "unavailable",
    sourceType: "deterministic_frontend_fallback",
    backendReflectionStatus: "backend_reflection_endpoint_unavailable",
    frontendBackendAlignmentStatus,
    endpointAlignmentStatus: "backend_endpoint_unavailable",
    healthEndpoint: "/api/health",
    trustEndpoint: BACKEND_TRUST_VISIBILITY_ENDPOINT,
    reportReference: FALLBACK_REPORT_REFERENCE,
    diagnostics: [
      diagnostic(fetchStatus, "warning", message),
      diagnostic(
        "fallback-data-active",
        "warning",
        "Frontend fallback remains visible and read-only while backend endpoint visibility is unavailable.",
      ),
      diagnostic(
        "unsupported-state-visibility-preserved",
        "informational",
        "Unsupported-state visibility is preserved while backend fetch fallback is active.",
      ),
    ],
    expandedPayloadAvailable: false,
    expandedPayloadAvailabilityLabel: "Expanded backend payload unavailable",
    trustVisibilitySummary: FALLBACK_TRUST_SUMMARY,
    supportStatuses: [],
    explainabilityReferences: [],
    evidencePanelReferences: [],
    provenanceReferences: [],
    lineageReferences: [],
    coverageReferences: [],
    confidenceReferences: [],
    unsupportedStates: [],
    preservedProhibitions: [],
    frontendDisplayReadiness: FALLBACK_FRONTEND_DISPLAY_READINESS,
    fallbackActive: true,
    fallbackLabel: "Backend fetch unavailable - showing deterministic fallback",
    fallbackReason: message,
    payloadHash: "unavailable",
    readOnly: true,
    descriptiveOnly: true,
  };
}

export function buildBackendTrustVisibilityState(
  payload: BackendTrustVisibilityPayload,
): BackendTrustVisibilityState {
  const contract = payload.endpoint_contract ?? {};
  const reflection = payload.backend_reflection ?? {};
  const alignment = payload.frontend_alignment ?? {};
  const report = payload.report_reference ?? {};
  const expandedSectionCount = expandedPayloadSectionCount(payload);
  const expandedPayloadAvailable = expandedSectionCount >= 11;
  const diagnostics = payload.diagnostics?.length
    ? payload.diagnostics.map(normalizeDiagnostic)
    : [
        diagnostic(
          "backend-diagnostics-missing",
          "warning",
          "Backend endpoint payload did not include diagnostics; fallback context remains visible.",
        ),
      ];

  return {
    endpointRoute:
      typeof contract.endpoint_route === "string"
        ? contract.endpoint_route
        : BACKEND_TRUST_VISIBILITY_ENDPOINT,
    endpointAvailable: true,
    fetchStatus: "endpoint_visible",
    schemaVersion: payload.schema_version,
    sourceType: payload.source_type || "backend_expanded_report_backed_visibility",
    backendReflectionStatus:
      reflection.status || reflection.backend_reflection_status_id || "backend_reflection_contract_defined",
    frontendBackendAlignmentStatus: expandedPayloadAvailable
      ? FRONTEND_BACKEND_ALIGNMENT_EXPANDED_VISIBLE
      : FRONTEND_BACKEND_ALIGNMENT_EXPANDED_PARTIAL,
    endpointAlignmentStatus:
      alignment.status ||
      reflection.alignment_status ||
      "frontend_backend_alignment_endpoint_visible",
    healthEndpoint: reflection.health_endpoint || "/api/health",
    trustEndpoint: reflection.trust_endpoint || BACKEND_TRUST_VISIBILITY_ENDPOINT,
    reportReference: {
      name: report.name || FALLBACK_REPORT_REFERENCE.name,
      path: report.path || FALLBACK_REPORT_REFERENCE.path,
      hash: report.hash || FALLBACK_REPORT_REFERENCE.hash,
      available: report.available === true,
      status: report.status || FALLBACK_REPORT_REFERENCE.status,
    },
    diagnostics: [
      diagnostic(
        "backend-trust-endpoint-visible",
        "informational",
        "Backend trust endpoint visible as read-only backend trust visibility.",
      ),
      ...(expandedPayloadAvailable
        ? [
            diagnostic(
              "expanded-backend-payload-visible",
              "informational",
              "Expanded backend trust payload sections are visible as read-only frontend context.",
            ),
          ]
        : [
            diagnostic(
              "expanded-backend-payload-unavailable",
              "warning",
              "Expanded backend trust payload sections are unavailable or incomplete; fallback context remains visible.",
            ),
          ]),
      ...diagnostics,
    ],
    expandedPayloadAvailable,
    expandedPayloadAvailabilityLabel: expandedPayloadAvailable
      ? "Expanded backend payload visible"
      : "Expanded backend payload unavailable",
    trustVisibilitySummary: normalizeSummary(payload.trust_visibility),
    supportStatuses: normalizeReferences(payload.support_statuses),
    explainabilityReferences: normalizeReferences(payload.explainability_references),
    evidencePanelReferences: normalizeReferences(payload.evidence_panel_references),
    provenanceReferences: normalizeReferences(payload.provenance_references),
    lineageReferences: normalizeReferences(payload.lineage_references),
    coverageReferences: normalizeReferences(payload.coverage_references),
    confidenceReferences: normalizeReferences(payload.confidence_references),
    unsupportedStates: normalizeReferences(payload.unsupported_states),
    preservedProhibitions: payload.preserved_prohibitions ?? [],
    frontendDisplayReadiness: normalizeDisplayReadiness(
      payload.frontend_display_readiness,
    ),
    fallbackActive: false,
    fallbackLabel: "Backend trust endpoint visible",
    fallbackReason: "Endpoint-backed metadata is visible; frontend fallback remains available.",
    payloadHash: payload.payload_hash || "missing",
    readOnly: true,
    descriptiveOnly: true,
  };
}

export async function fetchBackendTrustVisibility(
  fetcher: BackendTrustFetch | undefined = typeof fetch === "function" ? fetch : undefined,
): Promise<BackendTrustVisibilityState> {
  if (!fetcher) {
    return buildBackendTrustFetchFallback(
      "fetch_failed",
      "Fetch API unavailable - showing deterministic fallback.",
    );
  }

  let response: Pick<Response, "ok" | "status" | "json">;
  try {
    response = await fetcher(BACKEND_TRUST_VISIBILITY_ENDPOINT, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });
  } catch {
    return buildBackendTrustFetchFallback(
      "fetch_failed",
      "Backend fetch unavailable - showing deterministic fallback.",
    );
  }

  if (!response.ok) {
    return buildBackendTrustFetchFallback(
      "http_error",
      `Backend trust endpoint returned HTTP ${response.status}; deterministic fallback remains visible.`,
    );
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return buildBackendTrustFetchFallback(
      "malformed_payload",
      "Backend trust endpoint returned malformed JSON; deterministic fallback remains visible.",
    );
  }

  if (!isRecord(payload)) {
    return buildBackendTrustFetchFallback(
      "malformed_payload",
      "Backend trust endpoint returned a non-object payload; deterministic fallback remains visible.",
    );
  }

  if (!isBackendTrustVisibilityPayload(payload) || payload.schema_version.length === 0) {
    return buildBackendTrustFetchFallback(
      "missing_schema_version",
      "Backend trust endpoint payload is missing schema_version; deterministic fallback remains visible.",
    );
  }

  return buildBackendTrustVisibilityState(payload);
}

export function getInitialBackendTrustVisibilityState(): BackendTrustVisibilityState {
  return buildBackendTrustFetchFallback(
    "pending",
    "Backend trust endpoint fetch pending; deterministic fallback remains visible.",
  );
}

export function isBackendTrustVisibilityReadOnly(
  state: BackendTrustVisibilityState,
): boolean {
  return (
    state.readOnly &&
    state.descriptiveOnly &&
    state.diagnostics.every((item) => item.readOnly && item.descriptiveOnly)
  );
}
