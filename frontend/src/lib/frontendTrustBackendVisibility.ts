import type {
  BackendTrustDiagnosticPayload,
  BackendTrustFetchStatus,
  BackendTrustVisibilityPayload,
  BackendTrustVisibilityState,
  FrontendBackendAlignmentStatus,
} from "@/types/frontendTrustBackendVisibility";

export const BACKEND_TRUST_VISIBILITY_ENDPOINT = "/api/trust/visibility";
export const BACKEND_TRUST_VISIBILITY_SCHEMA_VERSION = "v4.5d.1";
export const FRONTEND_BACKEND_ALIGNMENT_ENDPOINT_VISIBLE =
  "frontend_backend_alignment_endpoint_visible" as const;
export const FRONTEND_BACKEND_ALIGNMENT_FETCH_FALLBACK =
  "frontend_backend_alignment_fetch_attempted_with_fail_visible_fallback" as const;

type BackendTrustFetch = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Pick<Response, "ok" | "status" | "json">>;

const FALLBACK_REPORT_REFERENCE = {
  name: "backend_trust_visibility_report_unavailable",
  path: "docs/generated/v4_5d_1_backend_trust_visibility_endpoint_contract_report.json",
  hash: "missing",
  available: false,
  status: "unavailable",
} as const;

const READ_ONLY_DIAGNOSTIC_FLAGS = {
  readOnly: true,
  descriptiveOnly: true,
} as const;

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
    sourceType: payload.source_type || "backend_report_backed_visibility",
    backendReflectionStatus:
      reflection.status || reflection.backend_reflection_status_id || "backend_reflection_contract_defined",
    frontendBackendAlignmentStatus: FRONTEND_BACKEND_ALIGNMENT_ENDPOINT_VISIBLE,
    endpointAlignmentStatus:
      alignment.status ||
      reflection.alignment_status ||
      "backend_contract_ready_frontend_fetch_deferred",
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
      ...diagnostics,
    ],
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
