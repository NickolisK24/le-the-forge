"""Deterministic v4.1 refresh diagnostics and explainability models.

Diagnostics and explanations are descriptive governance evidence only. They do
not remediate, correct, repair, recommend, rank, score, select, approve,
authorize, execute refreshes, orchestrate work, sequence work, migrate schemas,
roll back state, recover state, consume production bundles, integrate with
planners, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID = "v4_1_refresh_diagnostics_explainability"
V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_SCHEMA_VERSION = "v4_1.refresh_diagnostics_explainability.1"
V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_REPORT_SCHEMA_VERSION = (
    "v4_1.refresh_diagnostics_explainability_report.1"
)
V4_1_UNIFIED_REFRESH_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "v4_1.unified_refresh_diagnostics_report.1"
V4_1_UNIFIED_REFRESH_EXPLAINABILITY_REPORT_SCHEMA_VERSION = "v4_1.unified_refresh_explainability_report.1"
V4_1_REFRESH_DIAGNOSTICS_CONTINUITY_REPORT_SCHEMA_VERSION = (
    "v4_1.refresh_diagnostics_continuity_report.1"
)
V4_1_REFRESH_DIAGNOSTICS_INTEGRITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_diagnostics_integrity_report.1"
V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_STABLE = "v4_1_refresh_diagnostics_explainability_stable"
V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_BLOCKED = "v4_1_refresh_diagnostics_explainability_blocked"
V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PURPOSE = (
    "deterministic_refresh_diagnostics_explainability_governance_only"
)

DIAGNOSTIC_LAYER_MANIFEST = "manifest"
DIAGNOSTIC_LAYER_DEPENDENCY = "dependency"
DIAGNOSTIC_LAYER_LINEAGE = "lineage"
DIAGNOSTIC_LAYER_SCHEMA = "schema"
DIAGNOSTIC_LAYER_SEQUENCING = "sequencing"
DIAGNOSTIC_LAYER_DRIFT = "drift"
DIAGNOSTIC_LAYER_REPLAY = "replay"
DIAGNOSTIC_LAYER_ROLLBACK = "rollback"
DIAGNOSTIC_LAYERS: tuple[str, ...] = (
    DIAGNOSTIC_LAYER_MANIFEST,
    DIAGNOSTIC_LAYER_DEPENDENCY,
    DIAGNOSTIC_LAYER_LINEAGE,
    DIAGNOSTIC_LAYER_SCHEMA,
    DIAGNOSTIC_LAYER_SEQUENCING,
    DIAGNOSTIC_LAYER_DRIFT,
    DIAGNOSTIC_LAYER_REPLAY,
    DIAGNOSTIC_LAYER_ROLLBACK,
)

DIAGNOSTIC_STATE_VISIBLE = "visible"
DIAGNOSTIC_STATE_MISSING_COVERAGE = "missing_diagnostic_coverage"
DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY = "inconsistent_diagnostic_severity"
DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER = "unsupported_diagnostic_provider"
DIAGNOSTIC_STATE_PROHIBITED_DOMAIN = "prohibited_diagnostic_domain"
DIAGNOSTIC_STATE_BLOCKED = "blocked_diagnostic_state"
DIAGNOSTIC_STATE_STALE = "stale_diagnostic_evidence"
DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT = "cross_layer_diagnostic_conflict"
DIAGNOSTIC_STATES: tuple[str, ...] = (
    DIAGNOSTIC_STATE_VISIBLE,
    DIAGNOSTIC_STATE_MISSING_COVERAGE,
    DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY,
    DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER,
    DIAGNOSTIC_STATE_PROHIBITED_DOMAIN,
    DIAGNOSTIC_STATE_BLOCKED,
    DIAGNOSTIC_STATE_STALE,
    DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT,
)

EXPLANATION_STATE_VISIBLE = "visible"
EXPLANATION_STATE_MISSING_COVERAGE = "missing_explanation_coverage"
EXPLANATION_STATE_INCONSISTENT_CATEGORY = "inconsistent_explanation_category"
EXPLANATION_STATE_UNSUPPORTED_PROVIDER = "unsupported_explanation_provider"
EXPLANATION_STATE_PROHIBITED_DOMAIN = "prohibited_explanation_domain"
EXPLANATION_STATE_BLOCKED = "blocked_explanation_state"
EXPLANATION_STATE_STALE = "stale_explanation_evidence"
EXPLANATION_STATE_CROSS_LAYER_CONFLICT = "cross_layer_explanation_conflict"
EXPLANATION_STATES: tuple[str, ...] = (
    EXPLANATION_STATE_VISIBLE,
    EXPLANATION_STATE_MISSING_COVERAGE,
    EXPLANATION_STATE_INCONSISTENT_CATEGORY,
    EXPLANATION_STATE_UNSUPPORTED_PROVIDER,
    EXPLANATION_STATE_PROHIBITED_DOMAIN,
    EXPLANATION_STATE_BLOCKED,
    EXPLANATION_STATE_STALE,
    EXPLANATION_STATE_CROSS_LAYER_CONFLICT,
)

FAIL_VISIBLE_DIAGNOSTIC_STATES: tuple[str, ...] = tuple(
    state for state in DIAGNOSTIC_STATES if state != DIAGNOSTIC_STATE_VISIBLE
)
FAIL_VISIBLE_EXPLANATION_STATES: tuple[str, ...] = tuple(
    state for state in EXPLANATION_STATES if state != EXPLANATION_STATE_VISIBLE
)

DIAGNOSTIC_SEVERITY_INFO = "info"
DIAGNOSTIC_SEVERITY_WARNING = "warning"
DIAGNOSTIC_SEVERITY_BLOCKED = "blocked"
DIAGNOSTIC_SEVERITY_PROHIBITED = "prohibited"

EXPLANATION_CATEGORY_DIAGNOSTIC_SUMMARY = "diagnostic_summary"
EXPLANATION_CATEGORY_UNSUPPORTED_STATE = "unsupported_state"
EXPLANATION_CATEGORY_BLOCKED_STATE = "blocked_state"
EXPLANATION_CATEGORY_PROHIBITED_STATE = "prohibited_state"
EXPLANATION_CATEGORY_LIMITATION = "limitation"
EXPLANATION_CATEGORY_CROSS_LAYER_SUMMARY = "cross_layer_summary"
EXPLANATION_CATEGORY_PROVENANCE_CONTINUITY = "provenance_continuity"
EXPLANATION_CATEGORY_LINEAGE_CONTINUITY = "lineage_continuity"
EXPLANATION_CATEGORY_REPLAY_CONTINUITY = "replay_continuity"
EXPLANATION_CATEGORY_ROLLBACK_CONTINUITY = "rollback_continuity"
EXPLANATION_CATEGORIES: tuple[str, ...] = (
    EXPLANATION_CATEGORY_DIAGNOSTIC_SUMMARY,
    EXPLANATION_CATEGORY_UNSUPPORTED_STATE,
    EXPLANATION_CATEGORY_BLOCKED_STATE,
    EXPLANATION_CATEGORY_PROHIBITED_STATE,
    EXPLANATION_CATEGORY_LIMITATION,
    EXPLANATION_CATEGORY_CROSS_LAYER_SUMMARY,
    EXPLANATION_CATEGORY_PROVENANCE_CONTINUITY,
    EXPLANATION_CATEGORY_LINEAGE_CONTINUITY,
    EXPLANATION_CATEGORY_REPLAY_CONTINUITY,
    EXPLANATION_CATEGORY_ROLLBACK_CONTINUITY,
)

PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS: tuple[str, ...] = (
    "remediation",
    "automatic_correction",
    "automatic_repair",
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "dependency_resolution",
    "schema_migration_execution",
    "automatic_migration",
    "rollback_execution",
    "recovery_execution",
    "planner_integration",
    "production_bundle_consumption",
    "recommendation_systems",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "optimization_systems",
    "authorization_systems",
    "approval_systems",
    "runtime_mutation",
    "hidden_remediation_behavior",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_DIAGNOSTICS_EXPLAINABILITY_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 8 creates deterministic diagnostics and explainability metadata only.",
    "v4.1 Phase 8 does not enable remediation.",
    "v4.1 Phase 8 does not enable automatic correction.",
    "v4.1 Phase 8 does not enable recommendation ranking scoring or selection.",
    "v4.1 Phase 8 does not enable approval or authorization.",
    "v4.1 Phase 8 does not enable orchestration execution.",
    "v4.1 Phase 8 does not enable automatic sequencing.",
    "v4.1 Phase 8 does not enable refresh execution.",
    "v4.1 Phase 8 does not enable migration execution.",
    "v4.1 Phase 8 does not enable recovery execution.",
    "v4.1 Phase 8 does not enable rollback execution.",
    "v4.1 Phase 8 does not enable planner integration.",
    "v4.1 Phase 8 does not enable production consumption.",
    "v4.1 Phase 8 does not enable mutation behavior.",
)

EXPLICIT_DIAGNOSTICS_EXPLAINABILITY_PROHIBITIONS: tuple[str, ...] = (
    "No remediation exists.",
    "No automatic correction exists.",
    "No recommendation ranking scoring or selection exists.",
    "No approval or authorization exists.",
    "No orchestration execution exists.",
    "No automatic sequencing exists.",
    "No refresh execution exists.",
    "No migration execution exists.",
    "No recovery execution exists.",
    "No rollback execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No mutation behavior exists.",
    "No diagnostic becomes an action.",
    "No explanation becomes a recommendation ranking scoring or selection system.",
    "No summary implies authorization or approval.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshDiagnosticsExplainabilityIdentity:
    diagnostics_id: str
    explanation_id: str
    refresh_cycle_id: str
    diagnostics_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    source_lineage_certification_reference: str
    source_schema_governance_reference: str
    source_sequencing_reference: str
    source_drift_certification_reference: str
    source_replay_rollback_reference: str
    schema_version: str
    generated_at: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    governance_scope: str = "refresh_diagnostics_explainability_descriptive_only"
    governance_purpose: str = V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    recommendation_enabled: bool = False
    approval_enabled: bool = False
    execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshDiagnosticSummary:
    diagnostic_id: str
    source_layer: str
    source_reference: str
    state: str
    severity: str
    summary: str
    lineage_reference: str
    provenance_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class RefreshExplanationSummary:
    explanation_id: str
    source_layer: str
    source_reference: str
    category: str
    state: str
    severity: str
    explanation: str
    related_diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "related_diagnostic_ids")


@dataclass(frozen=True)
class CrossLayerDiagnosticAggregation:
    aggregation_id: str
    manifest_diagnostic_ids: tuple[str, ...]
    dependency_diagnostic_ids: tuple[str, ...]
    lineage_diagnostic_ids: tuple[str, ...]
    schema_diagnostic_ids: tuple[str, ...]
    sequencing_diagnostic_ids: tuple[str, ...]
    drift_diagnostic_ids: tuple[str, ...]
    replay_diagnostic_ids: tuple[str, ...]
    rollback_diagnostic_ids: tuple[str, ...]
    missing_diagnostic_coverage_ids: tuple[str, ...]
    inconsistent_severity_ids: tuple[str, ...]
    unsupported_diagnostic_provider_ids: tuple[str, ...]
    prohibited_diagnostic_domain_ids: tuple[str, ...]
    blocked_diagnostic_ids: tuple[str, ...]
    stale_diagnostic_ids: tuple[str, ...]
    cross_layer_conflict_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "manifest_diagnostic_ids",
            "dependency_diagnostic_ids",
            "lineage_diagnostic_ids",
            "schema_diagnostic_ids",
            "sequencing_diagnostic_ids",
            "drift_diagnostic_ids",
            "replay_diagnostic_ids",
            "rollback_diagnostic_ids",
            "missing_diagnostic_coverage_ids",
            "inconsistent_severity_ids",
            "unsupported_diagnostic_provider_ids",
            "prohibited_diagnostic_domain_ids",
            "blocked_diagnostic_ids",
            "stale_diagnostic_ids",
            "cross_layer_conflict_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CrossLayerExplanationAggregation:
    aggregation_id: str
    explanation_ids: tuple[str, ...]
    unsupported_explanation_ids: tuple[str, ...]
    blocked_explanation_ids: tuple[str, ...]
    prohibited_explanation_ids: tuple[str, ...]
    limitation_explanation_ids: tuple[str, ...]
    missing_explanation_coverage_ids: tuple[str, ...]
    inconsistent_category_ids: tuple[str, ...]
    unsupported_explanation_provider_ids: tuple[str, ...]
    prohibited_explanation_domain_ids: tuple[str, ...]
    stale_explanation_ids: tuple[str, ...]
    cross_layer_conflict_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "explanation_ids",
            "unsupported_explanation_ids",
            "blocked_explanation_ids",
            "prohibited_explanation_ids",
            "limitation_explanation_ids",
            "missing_explanation_coverage_ids",
            "inconsistent_category_ids",
            "unsupported_explanation_provider_ids",
            "prohibited_explanation_domain_ids",
            "stale_explanation_ids",
            "cross_layer_conflict_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDiagnosticsContinuityMetadata:
    continuity_id: str
    diagnostic_references: tuple[str, ...]
    explanation_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    lineage_references: tuple[str, ...]
    replay_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    dependency_references: tuple[str, ...]
    schema_references: tuple[str, ...]
    sequencing_references: tuple[str, ...]
    drift_references: tuple[str, ...]
    deterministic_order: int
    diagnostics_continuity_preserved: bool = True
    explanation_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "explanation_references",
            "provenance_references",
            "lineage_references",
            "replay_references",
            "rollback_references",
            "dependency_references",
            "schema_references",
            "sequencing_references",
            "drift_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDiagnosticsIntegrityBoundary:
    boundary_id: str
    prohibited_diagnostic_domains: tuple[str, ...]
    prohibited_explanation_domains: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_correction_leakage: tuple[str, ...]
    prohibited_recommendation_leakage: tuple[str, ...]
    prohibited_ranking_leakage: tuple[str, ...]
    prohibited_scoring_leakage: tuple[str, ...]
    prohibited_selection_leakage: tuple[str, ...]
    prohibited_approval_leakage: tuple[str, ...]
    prohibited_authorization_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_diagnostic_domains",
            "prohibited_explanation_domains",
            "prohibited_remediation_leakage",
            "prohibited_correction_leakage",
            "prohibited_recommendation_leakage",
            "prohibited_ranking_leakage",
            "prohibited_scoring_leakage",
            "prohibited_selection_leakage",
            "prohibited_approval_leakage",
            "prohibited_authorization_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_execution_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDiagnosticsExplainabilityGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_safe: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDiagnosticsExplainability:
    identity: RefreshDiagnosticsExplainabilityIdentity
    diagnostic_summaries: tuple[RefreshDiagnosticSummary, ...]
    explanation_summaries: tuple[RefreshExplanationSummary, ...]
    diagnostic_aggregation: CrossLayerDiagnosticAggregation
    explanation_aggregation: CrossLayerExplanationAggregation
    continuity_metadata: RefreshDiagnosticsContinuityMetadata
    integrity_boundary: RefreshDiagnosticsIntegrityBoundary
    governance: RefreshDiagnosticsExplainabilityGovernance
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    dependency_resolution_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_remediation_behavior_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_summaries")
        _set_tuple_field(self, "explanation_summaries")


def default_refresh_diagnostics_explainability_identity() -> RefreshDiagnosticsExplainabilityIdentity:
    return RefreshDiagnosticsExplainabilityIdentity(
        diagnostics_id="v4_1_refresh_diagnostics_explainability_primary",
        explanation_id="v4_1_refresh_explainability_primary",
        refresh_cycle_id="v4_1_phase_8_refresh_diagnostics_explainability",
        diagnostics_version="v4.1.0-phase-8",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        source_lineage_certification_reference="v4_1_refresh_lineage_certification_primary",
        source_schema_governance_reference="v4_1_schema_evolution_governance_primary",
        source_sequencing_reference="v4_1_refresh_sequencing_visibility_primary",
        source_drift_certification_reference="v4_1_refresh_drift_certification_primary",
        source_replay_rollback_reference="v4_1_refresh_replay_rollback_visibility_primary",
        schema_version=V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
        lineage_reference="v4_1_refresh_diagnostics_explainability_lineage_primary",
        provenance_reference="v4_1_refresh_diagnostics_explainability_provenance_primary",
        continuity_reference="v4_1_refresh_diagnostics_explainability_continuity_primary",
        integrity_reference="v4_1_refresh_diagnostics_explainability_integrity_primary",
        governance_reference="v4_1_refresh_diagnostics_explainability_boundary_primary",
    )


def _diagnostic(
    diagnostic_id: str,
    source_layer: str,
    state: str,
    severity: str,
    summary: str,
    deterministic_order: int,
) -> RefreshDiagnosticSummary:
    return RefreshDiagnosticSummary(
        diagnostic_id=diagnostic_id,
        source_layer=source_layer,
        source_reference=f"v4_1_{source_layer}_diagnostic_reference",
        state=state,
        severity=severity,
        summary=summary,
        lineage_reference=f"v4_1_{diagnostic_id}_lineage",
        provenance_reference=f"v4_1_{diagnostic_id}_provenance",
        deterministic_order=deterministic_order,
        fail_visible=state != DIAGNOSTIC_STATE_VISIBLE,
    )


def _explanation(
    explanation_id: str,
    source_layer: str,
    category: str,
    state: str,
    severity: str,
    explanation: str,
    related_diagnostic_ids: tuple[str, ...],
    deterministic_order: int,
) -> RefreshExplanationSummary:
    return RefreshExplanationSummary(
        explanation_id=explanation_id,
        source_layer=source_layer,
        source_reference=f"v4_1_{source_layer}_explanation_reference",
        category=category,
        state=state,
        severity=severity,
        explanation=explanation,
        related_diagnostic_ids=related_diagnostic_ids,
        deterministic_order=deterministic_order,
        fail_visible=state != EXPLANATION_STATE_VISIBLE,
    )


def default_refresh_diagnostic_summaries() -> tuple[RefreshDiagnosticSummary, ...]:
    visible = tuple(
        _diagnostic(
            diagnostic_id=f"v4_1_{layer}_diagnostics_visible",
            source_layer=layer,
            state=DIAGNOSTIC_STATE_VISIBLE,
            severity=DIAGNOSTIC_SEVERITY_INFO,
            summary=f"{layer} diagnostics are aggregated as descriptive governance evidence.",
            deterministic_order=(index + 1) * 10,
        )
        for index, layer in enumerate(DIAGNOSTIC_LAYERS)
    )
    return (
        *visible,
        _diagnostic("v4_1_missing_diagnostic_coverage", "cross_layer", DIAGNOSTIC_STATE_MISSING_COVERAGE, DIAGNOSTIC_SEVERITY_BLOCKED, "Missing diagnostic coverage is visible and not inferred.", 90),
        _diagnostic("v4_1_inconsistent_diagnostic_severity", "cross_layer", DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY, DIAGNOSTIC_SEVERITY_WARNING, "Inconsistent diagnostic severity is visible and not normalized.", 100),
        _diagnostic("v4_1_unsupported_diagnostic_provider", "unsupported", DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER, DIAGNOSTIC_SEVERITY_WARNING, "Unsupported diagnostic provider remains fail-visible.", 110),
        _diagnostic("v4_1_prohibited_diagnostic_domain", "prohibited", DIAGNOSTIC_STATE_PROHIBITED_DOMAIN, DIAGNOSTIC_SEVERITY_PROHIBITED, "Prohibited diagnostic domain remains visible and inactive.", 120),
        _diagnostic("v4_1_blocked_diagnostic_state", "blocked", DIAGNOSTIC_STATE_BLOCKED, DIAGNOSTIC_SEVERITY_BLOCKED, "Blocked diagnostic state is visible and not remediated.", 130),
        _diagnostic("v4_1_stale_diagnostic_evidence", "stale", DIAGNOSTIC_STATE_STALE, DIAGNOSTIC_SEVERITY_WARNING, "Stale diagnostic evidence is visible and not suppressed.", 140),
        _diagnostic("v4_1_cross_layer_diagnostic_conflict", "cross_layer", DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT, DIAGNOSTIC_SEVERITY_BLOCKED, "Cross-layer diagnostic conflict is visible and not resolved.", 150),
    )


def default_refresh_explanation_summaries() -> tuple[RefreshExplanationSummary, ...]:
    return (
        _explanation("v4_1_diagnostic_summary_explanation", "cross_layer", EXPLANATION_CATEGORY_DIAGNOSTIC_SUMMARY, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Cross-layer diagnostics summarize observed governance evidence without action.", ("v4_1_manifest_diagnostics_visible",), 10),
        _explanation("v4_1_unsupported_state_explanation", "unsupported", EXPLANATION_CATEGORY_UNSUPPORTED_STATE, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_WARNING, "Unsupported states remain visible and are not normalized.", ("v4_1_unsupported_diagnostic_provider",), 20),
        _explanation("v4_1_blocked_state_explanation", "blocked", EXPLANATION_CATEGORY_BLOCKED_STATE, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_BLOCKED, "Blocked states remain visible and are not remediated.", ("v4_1_blocked_diagnostic_state",), 30),
        _explanation("v4_1_prohibited_state_explanation", "prohibited", EXPLANATION_CATEGORY_PROHIBITED_STATE, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_PROHIBITED, "Prohibited states remain visible and inactive.", ("v4_1_prohibited_diagnostic_domain",), 40),
        _explanation("v4_1_limitation_explanation", "governance", EXPLANATION_CATEGORY_LIMITATION, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Limitations state what the diagnostics layer cannot execute or authorize.", ("v4_1_missing_diagnostic_coverage",), 50),
        _explanation("v4_1_cross_layer_summary_explanation", "cross_layer", EXPLANATION_CATEGORY_CROSS_LAYER_SUMMARY, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Cross-layer summaries describe evidence relationships without recommending actions.", ("v4_1_cross_layer_diagnostic_conflict",), 60),
        _explanation("v4_1_provenance_continuity_explanation", "provenance", EXPLANATION_CATEGORY_PROVENANCE_CONTINUITY, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Provenance continuity remains descriptive and explicit.", ("v4_1_dependency_diagnostics_visible",), 70),
        _explanation("v4_1_lineage_continuity_explanation", "lineage", EXPLANATION_CATEGORY_LINEAGE_CONTINUITY, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Lineage continuity remains descriptive and explicit.", ("v4_1_lineage_diagnostics_visible",), 80),
        _explanation("v4_1_replay_continuity_explanation", "replay", EXPLANATION_CATEGORY_REPLAY_CONTINUITY, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Replay continuity is explained without replay execution.", ("v4_1_replay_diagnostics_visible",), 90),
        _explanation("v4_1_rollback_continuity_explanation", "rollback", EXPLANATION_CATEGORY_ROLLBACK_CONTINUITY, EXPLANATION_STATE_VISIBLE, DIAGNOSTIC_SEVERITY_INFO, "Rollback continuity is explained without rollback execution.", ("v4_1_rollback_diagnostics_visible",), 100),
        _explanation("v4_1_missing_explanation_coverage", "cross_layer", EXPLANATION_CATEGORY_DIAGNOSTIC_SUMMARY, EXPLANATION_STATE_MISSING_COVERAGE, DIAGNOSTIC_SEVERITY_BLOCKED, "Missing explanation coverage is visible and not inferred.", ("v4_1_missing_diagnostic_coverage",), 110),
        _explanation("v4_1_inconsistent_explanation_category", "cross_layer", EXPLANATION_CATEGORY_CROSS_LAYER_SUMMARY, EXPLANATION_STATE_INCONSISTENT_CATEGORY, DIAGNOSTIC_SEVERITY_WARNING, "Inconsistent explanation category is visible and not normalized.", ("v4_1_inconsistent_diagnostic_severity",), 120),
        _explanation("v4_1_unsupported_explanation_provider", "unsupported", EXPLANATION_CATEGORY_UNSUPPORTED_STATE, EXPLANATION_STATE_UNSUPPORTED_PROVIDER, DIAGNOSTIC_SEVERITY_WARNING, "Unsupported explanation provider remains fail-visible.", ("v4_1_unsupported_diagnostic_provider",), 130),
        _explanation("v4_1_prohibited_explanation_domain", "prohibited", EXPLANATION_CATEGORY_PROHIBITED_STATE, EXPLANATION_STATE_PROHIBITED_DOMAIN, DIAGNOSTIC_SEVERITY_PROHIBITED, "Prohibited explanation domain remains visible and inactive.", ("v4_1_prohibited_diagnostic_domain",), 140),
        _explanation("v4_1_blocked_explanation_state", "blocked", EXPLANATION_CATEGORY_BLOCKED_STATE, EXPLANATION_STATE_BLOCKED, DIAGNOSTIC_SEVERITY_BLOCKED, "Blocked explanation state is visible and not remediated.", ("v4_1_blocked_diagnostic_state",), 150),
        _explanation("v4_1_stale_explanation_evidence", "stale", EXPLANATION_CATEGORY_LIMITATION, EXPLANATION_STATE_STALE, DIAGNOSTIC_SEVERITY_WARNING, "Stale explanation evidence is visible and not suppressed.", ("v4_1_stale_diagnostic_evidence",), 160),
        _explanation("v4_1_cross_layer_explanation_conflict", "cross_layer", EXPLANATION_CATEGORY_CROSS_LAYER_SUMMARY, EXPLANATION_STATE_CROSS_LAYER_CONFLICT, DIAGNOSTIC_SEVERITY_BLOCKED, "Cross-layer explanation conflict is visible and not resolved.", ("v4_1_cross_layer_diagnostic_conflict",), 170),
    )


def default_refresh_diagnostics_explainability() -> RefreshDiagnosticsExplainability:
    identity = default_refresh_diagnostics_explainability_identity()
    diagnostics = default_refresh_diagnostic_summaries()
    explanations = default_refresh_explanation_summaries()
    return RefreshDiagnosticsExplainability(
        identity=identity,
        diagnostic_summaries=diagnostics,
        explanation_summaries=explanations,
        diagnostic_aggregation=CrossLayerDiagnosticAggregation(
            aggregation_id="v4_1_cross_layer_diagnostic_aggregation_primary",
            manifest_diagnostic_ids=("v4_1_manifest_diagnostics_visible",),
            dependency_diagnostic_ids=("v4_1_dependency_diagnostics_visible",),
            lineage_diagnostic_ids=("v4_1_lineage_diagnostics_visible",),
            schema_diagnostic_ids=("v4_1_schema_diagnostics_visible",),
            sequencing_diagnostic_ids=("v4_1_sequencing_diagnostics_visible",),
            drift_diagnostic_ids=("v4_1_drift_diagnostics_visible",),
            replay_diagnostic_ids=("v4_1_replay_diagnostics_visible",),
            rollback_diagnostic_ids=("v4_1_rollback_diagnostics_visible",),
            missing_diagnostic_coverage_ids=("v4_1_missing_diagnostic_coverage",),
            inconsistent_severity_ids=("v4_1_inconsistent_diagnostic_severity",),
            unsupported_diagnostic_provider_ids=("v4_1_unsupported_diagnostic_provider",),
            prohibited_diagnostic_domain_ids=("v4_1_prohibited_diagnostic_domain",),
            blocked_diagnostic_ids=("v4_1_blocked_diagnostic_state",),
            stale_diagnostic_ids=("v4_1_stale_diagnostic_evidence",),
            cross_layer_conflict_ids=("v4_1_cross_layer_diagnostic_conflict",),
            deterministic_order=10,
        ),
        explanation_aggregation=CrossLayerExplanationAggregation(
            aggregation_id="v4_1_cross_layer_explanation_aggregation_primary",
            explanation_ids=tuple(explanation.explanation_id for explanation in explanations),
            unsupported_explanation_ids=("v4_1_unsupported_state_explanation", "v4_1_unsupported_explanation_provider"),
            blocked_explanation_ids=("v4_1_blocked_state_explanation", "v4_1_blocked_explanation_state"),
            prohibited_explanation_ids=("v4_1_prohibited_state_explanation", "v4_1_prohibited_explanation_domain"),
            limitation_explanation_ids=("v4_1_limitation_explanation",),
            missing_explanation_coverage_ids=("v4_1_missing_explanation_coverage",),
            inconsistent_category_ids=("v4_1_inconsistent_explanation_category",),
            unsupported_explanation_provider_ids=("v4_1_unsupported_explanation_provider",),
            prohibited_explanation_domain_ids=("v4_1_prohibited_explanation_domain",),
            stale_explanation_ids=("v4_1_stale_explanation_evidence",),
            cross_layer_conflict_ids=("v4_1_cross_layer_explanation_conflict",),
            deterministic_order=20,
        ),
        continuity_metadata=RefreshDiagnosticsContinuityMetadata(
            continuity_id=identity.continuity_reference,
            diagnostic_references=(identity.diagnostics_id,),
            explanation_references=(identity.explanation_id,),
            provenance_references=(identity.provenance_reference,),
            lineage_references=(identity.lineage_reference,),
            replay_references=("v4_1_replay_visibility_primary",),
            rollback_references=("v4_1_rollback_visibility_primary",),
            dependency_references=("v4_1_refresh_dependency_graph_primary",),
            schema_references=("v4_1_schema_evolution_governance_primary",),
            sequencing_references=("v4_1_refresh_sequencing_visibility_primary",),
            drift_references=("v4_1_refresh_drift_certification_primary",),
            deterministic_order=30,
        ),
        integrity_boundary=RefreshDiagnosticsIntegrityBoundary(
            boundary_id=identity.integrity_reference,
            prohibited_diagnostic_domains=PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS,
            prohibited_explanation_domains=PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS,
            prohibited_remediation_leakage=("remediation", "hidden_remediation_behavior"),
            prohibited_correction_leakage=("automatic_correction", "automatic_repair"),
            prohibited_recommendation_leakage=("recommendation_systems",),
            prohibited_ranking_leakage=("ranking_systems",),
            prohibited_scoring_leakage=("scoring_systems",),
            prohibited_selection_leakage=("selection_systems",),
            prohibited_approval_leakage=("approval_systems",),
            prohibited_authorization_leakage=("authorization_systems",),
            prohibited_orchestration_leakage=("orchestration_execution", "automatic_sequencing"),
            prohibited_execution_leakage=("refresh_execution", "rollback_execution", "recovery_execution"),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=40,
        ),
        governance=RefreshDiagnosticsExplainabilityGovernance(
            governance_id=identity.governance_reference,
            governance_references=(identity.governance_reference, "v4_1_refresh_diagnostics_explainability_boundary_primary"),
            explicit_limitations=EXPLICIT_DIAGNOSTICS_EXPLAINABILITY_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_DIAGNOSTICS_EXPLAINABILITY_PROHIBITIONS,
            deterministic_order=50,
        ),
    )
