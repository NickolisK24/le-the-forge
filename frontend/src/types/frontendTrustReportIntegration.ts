export type TrustReportSourceStatus =
  | "report_backed"
  | "fallback_active"
  | "report_unavailable"
  | "report_malformed"
  | "unknown";

export type TrustReportDiagnosticState = "ok" | "warning" | "blocker" | "unsupported";

export interface TrustReportMetadata {
  readonly reportName: string;
  readonly reportPath: string;
  readonly reportHash: string;
  readonly certificationStatus: string;
  readonly generatedAt: string;
  readonly readinessClassifications: readonly string[];
  readonly descriptiveOnlyGuaranteeText: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustReportSourceVisibility {
  readonly generatedReportPath: string;
  readonly staticFallbackSource: string;
  readonly reportBackedSourceStatus: TrustReportSourceStatus;
  readonly unavailableReportSourceStatus: TrustReportSourceStatus;
  readonly sourceVisibilityNote: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustReportFallbackState {
  readonly fallbackActive: boolean;
  readonly fallbackLabel: string;
  readonly fallbackSource: string;
  readonly fallbackReason: string;
  readonly fallbackVisibilityNote: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustReportCertificationSummary {
  readonly id: string;
  readonly label: string;
  readonly values: readonly string[];
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustReportDiagnostic {
  readonly id: string;
  readonly label: string;
  readonly state: TrustReportDiagnosticState;
  readonly message: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface FrontendTrustReportIntegrationData {
  readonly integrationId: string;
  readonly sourceStatus: TrustReportSourceStatus;
  readonly metadata: TrustReportMetadata;
  readonly sourceVisibility: TrustReportSourceVisibility;
  readonly fallbackState: TrustReportFallbackState;
  readonly certificationSummaries: readonly TrustReportCertificationSummary[];
  readonly diagnostics: readonly TrustReportDiagnostic[];
  readonly repositoryRemains: readonly string[];
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}
