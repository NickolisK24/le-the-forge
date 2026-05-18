export type TrustSurfaceSupportStatus =
  | "supported"
  | "partially_supported"
  | "unsupported"
  | "experimental"
  | "deprecated"
  | "blocked"
  | "unknown";

export type TrustSurfaceTone =
  | "green"
  | "blue"
  | "amber"
  | "red"
  | "purple"
  | "gray"
  | "slate";

export interface TrustSurfaceBadgeDefinition {
  readonly status: TrustSurfaceSupportStatus;
  readonly label: string;
  readonly description: string;
  readonly tone: TrustSurfaceTone;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustStatusCardData {
  readonly id: string;
  readonly title: string;
  readonly status: TrustSurfaceSupportStatus;
  readonly summary: string;
  readonly limitation: string;
  readonly deterministicOrder: number;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustExplanationPanelData {
  readonly id: string;
  readonly title: string;
  readonly explanationType:
    | "support"
    | "limitation"
    | "unsupported_state"
    | "continuity"
    | "trust"
    | "diagnostics";
  readonly summary: string;
  readonly details: readonly string[];
  readonly deterministicOrder: number;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustEvidenceItemData {
  readonly id: string;
  readonly label: string;
  readonly source: string;
  readonly freshness: "current" | "stale" | "unknown" | "missing" | "unsupported";
  readonly provenance: string;
  readonly lineage: string;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustEvidencePanelData {
  readonly id: string;
  readonly title: string;
  readonly group:
    | "trust_summary"
    | "support_status"
    | "explainability"
    | "provenance"
    | "lineage"
    | "limitations"
    | "unsupported_state"
    | "diagnostics";
  readonly items: readonly TrustEvidenceItemData[];
  readonly deterministicOrder: number;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustProvenanceLineageData {
  readonly id: string;
  readonly title: string;
  readonly sourceReference: string;
  readonly evidenceOrigin: string;
  readonly provenanceState: "available" | "stale" | "unknown" | "unsupported";
  readonly lineageState: "continuous" | "incomplete" | "unknown" | "unsupported";
  readonly visibilityNote: string;
  readonly deterministicOrder: number;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustMetricSummaryData {
  readonly id: string;
  readonly label: string;
  readonly state: string;
  readonly visibilityNote: string;
  readonly deterministicOrder: number;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface TrustDiagnosticsSummaryData {
  readonly id: string;
  readonly label: string;
  readonly state: "warning" | "blocker" | "unsupported" | "gap";
  readonly message: string;
  readonly deterministicOrder: number;
  readonly readOnly: true;
  readonly descriptiveOnly: true;
}

export interface FrontendTrustSurfaceData {
  readonly phaseId: string;
  readonly generatedAt: string;
  readonly trustStatusCards: readonly TrustStatusCardData[];
  readonly supportBadges: readonly TrustSurfaceBadgeDefinition[];
  readonly explainabilityPanels: readonly TrustExplanationPanelData[];
  readonly evidencePanels: readonly TrustEvidencePanelData[];
  readonly provenanceLineagePanels: readonly TrustProvenanceLineageData[];
  readonly coverageSummaries: readonly TrustMetricSummaryData[];
  readonly confidenceSummaries: readonly TrustMetricSummaryData[];
  readonly diagnosticsSummaries: readonly TrustDiagnosticsSummaryData[];
  readonly guarantees: readonly string[];
  readonly prohibitions: readonly string[];
  readonly nonAuthorityStatement: string;
  readonly repositoryRemains: readonly string[];
}
