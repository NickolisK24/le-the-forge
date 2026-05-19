export type BackendTrustFetchStatus =
  | "pending"
  | "endpoint_visible"
  | "fetch_failed"
  | "http_error"
  | "malformed_payload"
  | "missing_schema_version";

export type FrontendBackendAlignmentStatus =
  | "frontend_backend_alignment_endpoint_visible"
  | "frontend_backend_alignment_fetch_attempted_with_fail_visible_fallback";

export interface BackendTrustEndpointContract {
  readonly endpoint_contract_id?: string;
  readonly endpoint_route?: string;
  readonly schema_version?: string;
  readonly methods?: readonly string[];
  readonly read_only?: boolean;
  readonly descriptive_only?: boolean;
  readonly non_mutating?: boolean;
}

export interface BackendTrustReportReference {
  readonly report_reference_id?: string;
  readonly name?: string;
  readonly path?: string;
  readonly hash?: string;
  readonly available?: boolean;
  readonly status?: string;
  readonly phase_id?: string;
}

export interface BackendTrustReflection {
  readonly status?: string;
  readonly backend_reflection_status_id?: string;
  readonly health_endpoint?: string;
  readonly trust_endpoint?: string;
  readonly alignment_status?: string;
  readonly frontend_alignment_status_id?: string;
}

export interface BackendTrustFrontendAlignment {
  readonly status?: string;
  readonly live_frontend_fetch?: boolean;
  readonly integration_readiness?: string;
}

export interface BackendTrustDiagnosticPayload {
  readonly id?: string;
  readonly severity?: string;
  readonly message?: string;
}

export interface BackendTrustVisibilityPayload {
  readonly schema_version: string;
  readonly status?: string;
  readonly endpoint_contract?: BackendTrustEndpointContract;
  readonly source_type?: string;
  readonly source_status?: Record<string, unknown>;
  readonly report_reference?: BackendTrustReportReference;
  readonly backend_reflection?: BackendTrustReflection;
  readonly frontend_alignment?: BackendTrustFrontendAlignment;
  readonly guarantees?: readonly string[];
  readonly prohibitions?: readonly string[];
  readonly diagnostics?: readonly BackendTrustDiagnosticPayload[];
  readonly payload_hash?: string;
}

export interface BackendTrustVisibilityDiagnostic {
  readonly id: string;
  readonly severity: "informational" | "warning" | "blocker";
  readonly message: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface BackendTrustVisibilityState {
  readonly endpointRoute: string;
  readonly endpointAvailable: boolean;
  readonly fetchStatus: BackendTrustFetchStatus;
  readonly schemaVersion: string;
  readonly sourceType: string;
  readonly backendReflectionStatus: string;
  readonly frontendBackendAlignmentStatus: FrontendBackendAlignmentStatus;
  readonly endpointAlignmentStatus: string;
  readonly healthEndpoint: string;
  readonly trustEndpoint: string;
  readonly reportReference: {
    readonly name: string;
    readonly path: string;
    readonly hash: string;
    readonly available: boolean;
    readonly status: string;
  };
  readonly diagnostics: readonly BackendTrustVisibilityDiagnostic[];
  readonly fallbackActive: boolean;
  readonly fallbackLabel: string;
  readonly fallbackReason: string;
  readonly payloadHash: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}
