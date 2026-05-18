"""Deterministic v4.5A.6 drift diagnostics aggregation models.

The v4.5A.6 Track A layer aggregates drift diagnostics across prior governance
intelligence phases without enabling remediation, repair, mitigation, automated
correction, prioritization, triage, ranking, recommendation, orchestration
response, planner execution, production consumption, runtime mutation, or
operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PHASE_ID = (
    "v4_5a_6_drift_diagnostics_aggregation"
)
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_SCHEMA_VERSION = (
    "v4_5a_6.drift_diagnostics_aggregation.1"
)
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_SCHEMA_VERSION = (
    "v4_5a_6.drift_diagnostics_aggregation_report.1"
)
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_STABLE = (
    "v4_5a_6_drift_diagnostics_aggregation_stable"
)
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_BLOCKED = (
    "v4_5a_6_drift_diagnostics_aggregation_blocked"
)
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PURPOSE = (
    "deterministic_governance_safe_drift_diagnostics_aggregation_descriptive_only"
)
V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_CLASSIFICATION = (
    "governance_safe_descriptive_drift_diagnostics_aggregation"
)

V4_5A_1_DRIFT_FOUNDATION_REPORT_REFERENCE = (
    "docs/generated/v4_5a_1_drift_foundations_report.json"
)
V4_5A_1_DRIFT_FOUNDATION_REPORT_HASH_REFERENCE = (
    "5aa8494f9d2e323de50df02759d1fef24cabaa5a741e6ddfa289de27d747a087"
)
V4_5A_2_DRIFT_PROPAGATION_REPORT_REFERENCE = (
    "docs/generated/v4_5a_2_drift_propagation_intelligence_report.json"
)
V4_5A_2_DRIFT_PROPAGATION_REPORT_HASH_REFERENCE = (
    "8752e48ec0e3c8c36ee4005aac59186076c4e7e33e08263c62408e4fe3cd9b7b"
)
V4_5A_3_INTEGRITY_DEGRADATION_REPORT_REFERENCE = (
    "docs/generated/v4_5a_3_integrity_degradation_intelligence_report.json"
)
V4_5A_3_INTEGRITY_DEGRADATION_REPORT_HASH_REFERENCE = (
    "70c374bc09a9e72e8ec0aaffd6f4ca34971b9888c03d8f03746c5c4a450cadfb"
)
V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_REFERENCE = (
    "docs/generated/v4_5a_4_drift_explainability_intelligence_report.json"
)
V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_HASH_REFERENCE = (
    "d366b07d03a5534cbdf41375b0ed75a2e858ec9cd0575373840a912da4b452e2"
)
V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE = (
    "docs/generated/v4_5a_5_cross_boundary_drift_continuity_report.json"
)
V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE = (
    "f012e5aa6bc83878b0b1848d81f6b1c823ca9a534748c529c4da7feba14e721f"
)

DIAGNOSTIC_SOURCE_DRIFT_FOUNDATION = "drift_foundation_diagnostics"
DIAGNOSTIC_SOURCE_PROPAGATION = "propagation_diagnostics"
DIAGNOSTIC_SOURCE_DEGRADATION = "integrity_degradation_diagnostics"
DIAGNOSTIC_SOURCE_EXPLAINABILITY = "drift_explainability_diagnostics"
DIAGNOSTIC_SOURCE_CROSS_BOUNDARY = "cross_boundary_continuity_diagnostics"
DIAGNOSTIC_SOURCE_UNSUPPORTED_STATE = "unsupported_state_diagnostics"
DIAGNOSTIC_SOURCE_INHERITED_PROHIBITION = "inherited_prohibition_diagnostics"
DIAGNOSTIC_SOURCE_INHERITED_CONSTRAINT = "inherited_constraint_diagnostics"
DIAGNOSTIC_SOURCE_TYPES: tuple[str, ...] = (
    DIAGNOSTIC_SOURCE_DRIFT_FOUNDATION,
    DIAGNOSTIC_SOURCE_PROPAGATION,
    DIAGNOSTIC_SOURCE_DEGRADATION,
    DIAGNOSTIC_SOURCE_EXPLAINABILITY,
    DIAGNOSTIC_SOURCE_CROSS_BOUNDARY,
    DIAGNOSTIC_SOURCE_UNSUPPORTED_STATE,
    DIAGNOSTIC_SOURCE_INHERITED_PROHIBITION,
    DIAGNOSTIC_SOURCE_INHERITED_CONSTRAINT,
)

UNSUPPORTED_SUMMARY_DRIFT = "unsupported_drift_states"
UNSUPPORTED_SUMMARY_PROPAGATION = "unsupported_propagation_states"
UNSUPPORTED_SUMMARY_DEGRADATION = "unsupported_degradation_states"
UNSUPPORTED_SUMMARY_EXPLANATION = "unsupported_explanation_states"
UNSUPPORTED_SUMMARY_CROSS_BOUNDARY = "unsupported_cross_boundary_states"
UNSUPPORTED_SUMMARY_OPERATIONAL = "unsupported_operational_states"
UNSUPPORTED_SUMMARY_EVIDENCE = "unsupported_evidence_states"
UNSUPPORTED_SUMMARY_CONTINUITY = "unsupported_continuity_states"
UNSUPPORTED_STATE_SUMMARY_TYPES: tuple[str, ...] = (
    UNSUPPORTED_SUMMARY_DRIFT,
    UNSUPPORTED_SUMMARY_PROPAGATION,
    UNSUPPORTED_SUMMARY_DEGRADATION,
    UNSUPPORTED_SUMMARY_EXPLANATION,
    UNSUPPORTED_SUMMARY_CROSS_BOUNDARY,
    UNSUPPORTED_SUMMARY_OPERATIONAL,
    UNSUPPORTED_SUMMARY_EVIDENCE,
    UNSUPPORTED_SUMMARY_CONTINUITY,
)

EVIDENCE_GAP_DRIFT = "missing_drift_evidence"
EVIDENCE_GAP_PROPAGATION = "missing_propagation_evidence"
EVIDENCE_GAP_DEGRADATION = "missing_degradation_evidence"
EVIDENCE_GAP_EXPLANATION = "missing_explanation_evidence"
EVIDENCE_GAP_CROSS_BOUNDARY = "missing_cross_boundary_evidence"
EVIDENCE_GAP_LINEAGE = "lineage_evidence_gaps"
EVIDENCE_GAP_PROVENANCE = "provenance_evidence_gaps"
EVIDENCE_GAP_BLOCKER = "blocker_evidence_gaps"
EVIDENCE_GAP_WARNING = "warning_evidence_gaps"
EVIDENCE_GAP_SUMMARY_TYPES: tuple[str, ...] = (
    EVIDENCE_GAP_DRIFT,
    EVIDENCE_GAP_PROPAGATION,
    EVIDENCE_GAP_DEGRADATION,
    EVIDENCE_GAP_EXPLANATION,
    EVIDENCE_GAP_CROSS_BOUNDARY,
    EVIDENCE_GAP_LINEAGE,
    EVIDENCE_GAP_PROVENANCE,
    EVIDENCE_GAP_BLOCKER,
    EVIDENCE_GAP_WARNING,
)

CONTINUITY_GAP_DRIFT = "drift_continuity_gaps"
CONTINUITY_GAP_PROPAGATION = "propagation_continuity_gaps"
CONTINUITY_GAP_DEGRADATION = "degradation_continuity_gaps"
CONTINUITY_GAP_EXPLANATION = "explanation_continuity_gaps"
CONTINUITY_GAP_CROSS_BOUNDARY = "cross_boundary_continuity_gaps"
CONTINUITY_GAP_LINEAGE = "lineage_continuity_gaps"
CONTINUITY_GAP_PROVENANCE = "provenance_continuity_gaps"
CONTINUITY_GAP_INTEGRITY = "integrity_continuity_gaps"
CONTINUITY_GAP_SUMMARY_TYPES: tuple[str, ...] = (
    CONTINUITY_GAP_DRIFT,
    CONTINUITY_GAP_PROPAGATION,
    CONTINUITY_GAP_DEGRADATION,
    CONTINUITY_GAP_EXPLANATION,
    CONTINUITY_GAP_CROSS_BOUNDARY,
    CONTINUITY_GAP_LINEAGE,
    CONTINUITY_GAP_PROVENANCE,
    CONTINUITY_GAP_INTEGRITY,
)

SEVERITY_INFORMATIONAL = "informational_diagnostics"
SEVERITY_LOW_VISIBILITY = "low_visibility_diagnostics"
SEVERITY_MODERATE_VISIBILITY = "moderate_visibility_diagnostics"
SEVERITY_HIGH_VISIBILITY = "high_visibility_diagnostics"
SEVERITY_CRITICAL_VISIBILITY = "critical_visibility_diagnostics"
DIAGNOSTIC_SEVERITY_SUMMARY_TYPES: tuple[str, ...] = (
    SEVERITY_INFORMATIONAL,
    SEVERITY_LOW_VISIBILITY,
    SEVERITY_MODERATE_VISIBILITY,
    SEVERITY_HIGH_VISIBILITY,
    SEVERITY_CRITICAL_VISIBILITY,
)

BLOCKER_WARNING_INHERITED_BLOCKER = "inherited_blockers"
BLOCKER_WARNING_INHERITED_WARNING = "inherited_warnings"
BLOCKER_WARNING_DRIFT_BLOCKER = "drift_blockers"
BLOCKER_WARNING_PROPAGATION_BLOCKER = "propagation_blockers"
BLOCKER_WARNING_DEGRADATION_BLOCKER = "degradation_blockers"
BLOCKER_WARNING_EXPLANATION_BLOCKER = "explanation_blockers"
BLOCKER_WARNING_CROSS_BOUNDARY_BLOCKER = "cross_boundary_blockers"
BLOCKER_WARNING_UNSUPPORTED_STATE_BLOCKER = "unsupported_state_blockers"
BLOCKER_WARNING_EVIDENCE_GAP_WARNING = "evidence_gap_warnings"
BLOCKER_WARNING_CONTINUITY_GAP_WARNING = "continuity_gap_warnings"
BLOCKER_WARNING_SUMMARY_TYPES: tuple[str, ...] = (
    BLOCKER_WARNING_INHERITED_BLOCKER,
    BLOCKER_WARNING_INHERITED_WARNING,
    BLOCKER_WARNING_DRIFT_BLOCKER,
    BLOCKER_WARNING_PROPAGATION_BLOCKER,
    BLOCKER_WARNING_DEGRADATION_BLOCKER,
    BLOCKER_WARNING_EXPLANATION_BLOCKER,
    BLOCKER_WARNING_CROSS_BOUNDARY_BLOCKER,
    BLOCKER_WARNING_UNSUPPORTED_STATE_BLOCKER,
    BLOCKER_WARNING_EVIDENCE_GAP_WARNING,
    BLOCKER_WARNING_CONTINUITY_GAP_WARNING,
)

AGGREGATED_DIAGNOSTIC_UNRESOLVED_DRIFT = "unresolved_drift_diagnostic_chains"
AGGREGATED_DIAGNOSTIC_UNRESOLVED_PROPAGATION = (
    "unresolved_propagation_diagnostic_chains"
)
AGGREGATED_DIAGNOSTIC_UNRESOLVED_DEGRADATION = (
    "unresolved_degradation_diagnostic_chains"
)
AGGREGATED_DIAGNOSTIC_UNRESOLVED_EXPLANATION = (
    "unresolved_explanation_diagnostic_chains"
)
AGGREGATED_DIAGNOSTIC_UNRESOLVED_CROSS_BOUNDARY = (
    "unresolved_cross_boundary_diagnostic_chains"
)
AGGREGATED_DIAGNOSTIC_MIXED_EVIDENCE_GAPS = "mixed_evidence_gaps"
AGGREGATED_DIAGNOSTIC_MIXED_CONTINUITY_GAPS = "mixed_continuity_gaps"
AGGREGATED_DIAGNOSTIC_UNSUPPORTED_STATE = "unsupported_aggregated_states"
AGGREGATED_DIAGNOSTIC_INHERITED_PROHIBITION_CONFLICT = (
    "inherited_prohibition_conflicts"
)
AGGREGATED_DIAGNOSTIC_INHERITED_CONSTRAINT_CONFLICT = "inherited_constraint_conflicts"
AGGREGATED_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    AGGREGATED_DIAGNOSTIC_UNRESOLVED_DRIFT,
    AGGREGATED_DIAGNOSTIC_UNRESOLVED_PROPAGATION,
    AGGREGATED_DIAGNOSTIC_UNRESOLVED_DEGRADATION,
    AGGREGATED_DIAGNOSTIC_UNRESOLVED_EXPLANATION,
    AGGREGATED_DIAGNOSTIC_UNRESOLVED_CROSS_BOUNDARY,
    AGGREGATED_DIAGNOSTIC_MIXED_EVIDENCE_GAPS,
    AGGREGATED_DIAGNOSTIC_MIXED_CONTINUITY_GAPS,
    AGGREGATED_DIAGNOSTIC_UNSUPPORTED_STATE,
    AGGREGATED_DIAGNOSTIC_INHERITED_PROHIBITION_CONFLICT,
    AGGREGATED_DIAGNOSTIC_INHERITED_CONSTRAINT_CONFLICT,
)

AGGREGATION_VISIBILITY_VISIBLE = "diagnostics_aggregation_visible"
AGGREGATION_VISIBILITY_SOURCE_VISIBLE = "diagnostic_source_visible"
AGGREGATION_VISIBILITY_UNSUPPORTED_VISIBLE = "unsupported_state_summary_visible"
AGGREGATION_VISIBILITY_EVIDENCE_GAP_VISIBLE = "evidence_gap_summary_visible"
AGGREGATION_VISIBILITY_CONTINUITY_GAP_VISIBLE = "continuity_gap_summary_visible"
AGGREGATION_VISIBILITY_SEVERITY_VISIBLE = "severity_summary_visible"
AGGREGATION_VISIBILITY_BLOCKER_WARNING_VISIBLE = "blocker_warning_summary_visible"
AGGREGATION_VISIBILITY_DIAGNOSTIC_VISIBLE = "aggregated_diagnostic_visible"

UNSUPPORTED_AGGREGATION_ORCHESTRATION_EXECUTION = "orchestration_execution"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_AUTHORIZATION = "orchestration_authorization"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_APPROVAL = "orchestration_approval"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_DISPATCH = "orchestration_dispatch"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_ROUTING = "orchestration_routing"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_TRAVERSAL = "orchestration_traversal"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_SCHEDULING = "orchestration_scheduling"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_SEQUENCING = "orchestration_sequencing"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_DECISION = "orchestration_decision"
UNSUPPORTED_AGGREGATION_ORCHESTRATION_RECOMMENDATION = "orchestration_recommendation"
UNSUPPORTED_AGGREGATION_AUTOMATED_PRIORITIZATION = "automated_prioritization"
UNSUPPORTED_AGGREGATION_AUTOMATED_TRIAGE = "automated_triage"
UNSUPPORTED_AGGREGATION_RANKING_BEHAVIOR = "ranking_driven_behavior"
UNSUPPORTED_AGGREGATION_RECOMMENDATION_BEHAVIOR = "recommendation_driven_behavior"
UNSUPPORTED_AGGREGATION_REMEDIATION = "remediation"
UNSUPPORTED_AGGREGATION_REPAIR = "repair"
UNSUPPORTED_AGGREGATION_MITIGATION = "mitigation"
UNSUPPORTED_AGGREGATION_AUTOMATED_CORRECTION = "automated_correction"
UNSUPPORTED_AGGREGATION_CONTINUITY_RESTORATION = "continuity_restoration"
UNSUPPORTED_AGGREGATION_RUNTIME_MUTATION = "runtime_mutation"
UNSUPPORTED_AGGREGATION_OPERATIONAL_MUTATION = "operational_mutation"
UNSUPPORTED_AGGREGATION_PLANNER_INTEGRATION = "planner_integration"
UNSUPPORTED_AGGREGATION_PRODUCTION_CONSUMPTION = "production_consumption"
UNSUPPORTED_AGGREGATION_OPERATIONAL_BEHAVIOR = "implicit_operational_behavior"
UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES: tuple[str, ...] = (
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_EXECUTION,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_AUTHORIZATION,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_APPROVAL,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_DISPATCH,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_ROUTING,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_TRAVERSAL,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_SCHEDULING,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_SEQUENCING,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_DECISION,
    UNSUPPORTED_AGGREGATION_ORCHESTRATION_RECOMMENDATION,
    UNSUPPORTED_AGGREGATION_AUTOMATED_PRIORITIZATION,
    UNSUPPORTED_AGGREGATION_AUTOMATED_TRIAGE,
    UNSUPPORTED_AGGREGATION_RANKING_BEHAVIOR,
    UNSUPPORTED_AGGREGATION_RECOMMENDATION_BEHAVIOR,
    UNSUPPORTED_AGGREGATION_REMEDIATION,
    UNSUPPORTED_AGGREGATION_REPAIR,
    UNSUPPORTED_AGGREGATION_MITIGATION,
    UNSUPPORTED_AGGREGATION_AUTOMATED_CORRECTION,
    UNSUPPORTED_AGGREGATION_CONTINUITY_RESTORATION,
    UNSUPPORTED_AGGREGATION_RUNTIME_MUTATION,
    UNSUPPORTED_AGGREGATION_OPERATIONAL_MUTATION,
    UNSUPPORTED_AGGREGATION_PLANNER_INTEGRATION,
    UNSUPPORTED_AGGREGATION_PRODUCTION_CONSUMPTION,
    UNSUPPORTED_AGGREGATION_OPERATIONAL_BEHAVIOR,
)

V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_orchestration_dispatch_count",
    "enabled_orchestration_routing_count",
    "enabled_orchestration_traversal_count",
    "enabled_orchestration_scheduling_count",
    "enabled_orchestration_sequencing_count",
    "enabled_orchestration_decision_count",
    "enabled_orchestration_recommendation_count",
    "enabled_automated_prioritization_count",
    "enabled_automated_triage_count",
    "enabled_ranking_count",
    "enabled_recommendation_count",
    "enabled_prioritization_action_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_mitigation_count",
    "enabled_auto_correction_count",
    "enabled_continuity_restoration_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
)

V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_aggregation_identity",
    "deterministic_source_diagnostic_aggregation",
    "deterministic_unsupported_state_summary_visibility",
    "deterministic_evidence_gap_summary_visibility",
    "deterministic_continuity_gap_summary_visibility",
    "deterministic_severity_summary_visibility",
    "deterministic_blocker_warning_summary_visibility",
    "deterministic_fail_visible_aggregated_diagnostics",
    "stable_replay_safe_serialization",
    "stable_replay_safe_hashing",
    "lineage_continuity_preserved",
    "provenance_continuity_preserved",
    "descriptive_only_no_ranking_recommendation_or_triage",
)

V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_INHERITED_PROHIBITIONS: tuple[str, ...] = (
    "orchestration_execution_prohibited",
    "orchestration_authorization_prohibited",
    "orchestration_approval_prohibited",
    "orchestration_dispatch_prohibited",
    "orchestration_routing_prohibited",
    "orchestration_traversal_prohibited",
    "orchestration_scheduling_prohibited",
    "orchestration_sequencing_prohibited",
    "orchestration_decisions_prohibited",
    "orchestration_recommendations_prohibited",
    "automated_prioritization_prohibited",
    "automated_triage_prohibited",
    "ranking_driven_behavior_prohibited",
    "recommendation_driven_behavior_prohibited",
    "remediation_prohibited",
    "repair_prohibited",
    "mitigation_prohibited",
    "automated_correction_prohibited",
    "continuity_restoration_prohibited",
    "runtime_mutation_prohibited",
    "operational_mutation_prohibited",
    "planner_integration_prohibited",
    "production_consumption_prohibited",
    "implicit_operational_behavior_prohibited",
)

V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_INHERITED_CONSTRAINTS: tuple[str, ...] = (
    "deterministic",
    "governance-safe",
    "replay-safe",
    "rollback-safe",
    "lineage-safe",
    "provenance-safe",
    "integrity-safe",
    "explainability-first",
    "fail-visible",
    "descriptive-only",
    "NON-operational",
    "NON-authorizing",
    "NON-executing",
    "NON-remediating",
    "NON-runtime-mutating",
    "NON-ranking",
    "NON-recommending",
)

V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "does_not_remediate_diagnostics",
    "does_not_repair_evidence_or_continuity_gaps",
    "does_not_mitigate_degradation",
    "does_not_backfill_evidence",
    "does_not_restore_continuity",
    "does_not_prioritize_or_triage",
    "does_not_rank_diagnostics",
    "does_not_recommend_actions",
    "does_not_authorize_or_execute",
    "does_not_integrate_planners",
    "does_not_mutate_runtime_state",
    "does_not_consume_production_runtime_paths",
)


def _set_tuple_field(instance: object, field_name: str) -> None:
    object.__setattr__(instance, field_name, tuple(getattr(instance, field_name)))


@dataclass(frozen=True)
class DriftDiagnosticsAggregationIdentity:
    aggregation_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_cross_boundary_report_reference: str
    source_cross_boundary_hash_reference: str


@dataclass(frozen=True)
class DiagnosticAggregationRecord:
    aggregation_record_id: str
    diagnostic_aggregation_id: str
    source_drift_id: str
    propagation_chain_id: str
    degradation_chain_id: str
    explanation_chain_id: str
    cross_boundary_continuity_id: str
    evidence_chain_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    continuity_reference_id: str
    source_diagnostic_type: str
    source_report_reference: str
    source_hash_reference: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    automated_prioritization_enabled: bool = False
    automated_triage_enabled: bool = False
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DiagnosticSourceAggregation:
    source_aggregation_id: str
    aggregation_record_id: str
    source_type: str
    source_report_reference: str
    source_hash_reference: str
    diagnostic_count: int
    unsupported_state_count: int
    evidence_gap_count: int
    continuity_gap_count: int
    inherited_prohibition_count: int
    inherited_constraint_count: int
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    no_triage: bool = True
    no_prioritization: bool = True
    no_ranking: bool = True
    no_recommendation: bool = True
    automated_triage_enabled: bool = False
    automated_prioritization_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False


@dataclass(frozen=True)
class UnsupportedStateSummaryVisibility:
    unsupported_summary_id: str
    aggregation_record_id: str
    unsupported_summary_type: str
    source_reference: str
    source_hash_reference: str
    state_count: int
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_response_enabled: bool = False
    remediation_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceGapSummaryVisibility:
    evidence_gap_id: str
    aggregation_record_id: str
    evidence_gap_type: str
    source_reference: str
    source_hash_reference: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    descriptive_only: bool = True
    evidence_repair_enabled: bool = False
    backfill_enabled: bool = False
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ContinuityGapSummaryVisibility:
    continuity_gap_id: str
    aggregation_record_id: str
    continuity_gap_type: str
    continuity_reference_id: str
    source_reference: str
    source_hash_reference: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    continuity_restoration_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DiagnosticSeveritySummaryVisibility:
    severity_summary_id: str
    aggregation_record_id: str
    severity_type: str
    diagnostic_count: int
    visibility_reason: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    non_ranking: bool = True
    non_recommending: bool = True
    non_authorizing: bool = True
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    authorization_enabled: bool = False
    automated_triage_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class BlockerWarningSummaryVisibility:
    blocker_warning_id: str
    aggregation_record_id: str
    blocker_warning_type: str
    visibility_category: str
    source_reference: str
    source_hash_reference: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    action_logic_enabled: bool = False
    prioritization_enabled: bool = False
    recommendation_enabled: bool = False
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class AggregatedDiagnosticRecord:
    aggregated_diagnostic_id: str
    aggregation_record_id: str
    diagnostic_type: str
    source_reference: str
    source_hash_reference: str
    continuity_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    message: str
    visibility_state: str
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    silent_fallback_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    automated_triage_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    orchestration_response_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedAggregationVisibility:
    state_id: str
    unsupported_state: str
    visibility_state: str
    explicit_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    operational_enabled: bool = False
    authorization_enabled: bool = False
    automated_prioritization_enabled: bool = False
    automated_triage_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    automated_correction_enabled: bool = False
    continuity_restoration_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DriftDiagnosticsAggregationIntelligence:
    aggregation_identity: DriftDiagnosticsAggregationIdentity
    diagnostic_aggregation_records: tuple[DiagnosticAggregationRecord, ...]
    diagnostic_source_aggregation: tuple[DiagnosticSourceAggregation, ...]
    unsupported_state_summaries: tuple[UnsupportedStateSummaryVisibility, ...]
    evidence_gap_summaries: tuple[EvidenceGapSummaryVisibility, ...]
    continuity_gap_summaries: tuple[ContinuityGapSummaryVisibility, ...]
    severity_summaries: tuple[DiagnosticSeveritySummaryVisibility, ...]
    blocker_warning_summaries: tuple[BlockerWarningSummaryVisibility, ...]
    aggregated_diagnostics: tuple[AggregatedDiagnosticRecord, ...]
    unsupported_aggregation_visibility: tuple[UnsupportedAggregationVisibility, ...]
    deterministic_guarantees: tuple[str, ...]
    inherited_prohibitions: tuple[str, ...]
    inherited_constraints: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_executing: bool = True
    non_authorizing: bool = True
    non_remediating: bool = True
    non_runtime_mutating: bool = True
    non_operational_mutating: bool = True
    non_routing: bool = True
    non_dispatching: bool = True
    non_traversing: bool = True
    non_scheduling: bool = True
    non_sequencing: bool = True
    non_deciding: bool = True
    non_ranking: bool = True
    non_recommending: bool = True
    non_triaging: bool = True
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    orchestration_scheduling_enabled: bool = False
    orchestration_sequencing_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    automated_prioritization_enabled: bool = False
    automated_triage_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    prioritization_action_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    continuity_restoration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_aggregation_records",
            "diagnostic_source_aggregation",
            "unsupported_state_summaries",
            "evidence_gap_summaries",
            "continuity_gap_summaries",
            "severity_summaries",
            "blocker_warning_summaries",
            "aggregated_diagnostics",
            "unsupported_aggregation_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


SOURCE_REPORTS: dict[str, tuple[str, str]] = {
    DIAGNOSTIC_SOURCE_DRIFT_FOUNDATION: (
        V4_5A_1_DRIFT_FOUNDATION_REPORT_REFERENCE,
        V4_5A_1_DRIFT_FOUNDATION_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_PROPAGATION: (
        V4_5A_2_DRIFT_PROPAGATION_REPORT_REFERENCE,
        V4_5A_2_DRIFT_PROPAGATION_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_DEGRADATION: (
        V4_5A_3_INTEGRITY_DEGRADATION_REPORT_REFERENCE,
        V4_5A_3_INTEGRITY_DEGRADATION_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_EXPLAINABILITY: (
        V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_REFERENCE,
        V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_CROSS_BOUNDARY: (
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE,
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_UNSUPPORTED_STATE: (
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE,
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_INHERITED_PROHIBITION: (
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE,
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE,
    ),
    DIAGNOSTIC_SOURCE_INHERITED_CONSTRAINT: (
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE,
        V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE,
    ),
}


def default_drift_diagnostics_aggregation_identity() -> (
    DriftDiagnosticsAggregationIdentity
):
    return DriftDiagnosticsAggregationIdentity(
        aggregation_id="v4_5a_6_governance_safe_drift_diagnostics_aggregation",
        phase_id=V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PHASE_ID,
        schema_version=V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_SCHEMA_VERSION,
        generated_at=V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_GENERATED_AT,
        classification=V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_CLASSIFICATION,
        source_cross_boundary_report_reference=(
            V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE
        ),
        source_cross_boundary_hash_reference=(
            V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE
        ),
    )


def default_diagnostic_aggregation_records() -> tuple[DiagnosticAggregationRecord, ...]:
    definitions = (
        (DIAGNOSTIC_SOURCE_DRIFT_FOUNDATION, "drift_identity_foundation", "propagation_chain_direct", "degradation_chain_continuity", "explanation_chain_continuity_drift", "cross_boundary_continuity_direct", "evidence_chain_drift_continuity", "lineage::v4_5a_1.diagnostics", "provenance::v4_5a_1.diagnostics", "continuity_reference_direct", ("evidence_gap_missing_drift_evidence",), 1),
        (DIAGNOSTIC_SOURCE_PROPAGATION, "drift_segmentation_boundary_visibility", "propagation_chain_cross_boundary", "degradation_chain_propagation_amplified", "explanation_chain_segmentation_drift", "cross_boundary_continuity_segmentation", "evidence_chain_propagation_continuity", "lineage::v4_5a_2.diagnostics", "provenance::v4_5a_2.diagnostics", "continuity_reference_segmentation", ("evidence_gap_missing_propagation_evidence",), 2),
        (DIAGNOSTIC_SOURCE_DEGRADATION, "drift_compatibility_boundary_visibility", "propagation_chain_compatibility", "degradation_chain_integrity_visibility", "explanation_chain_compatibility_drift", "cross_boundary_continuity_compatibility", "evidence_chain_degradation_continuity", "lineage::v4_5a_3.diagnostics", "provenance::v4_5a_3.diagnostics", "continuity_reference_compatibility", ("evidence_gap_missing_degradation_evidence",), 3),
        (DIAGNOSTIC_SOURCE_EXPLAINABILITY, "drift_explainability_boundary_visibility", "propagation_chain_explainability", "degradation_chain_explainability", "explanation_chain_evidence_gap_drift", "cross_boundary_continuity_governance_scope", "evidence_chain_explanation_continuity", "lineage::v4_5a_4.diagnostics", "provenance::v4_5a_4.diagnostics", "continuity_reference_governance_scope", ("evidence_gap_missing_explanation_evidence",), 4),
        (DIAGNOSTIC_SOURCE_CROSS_BOUNDARY, "drift_chain_unsupported", "propagation_chain_cross_boundary", "degradation_chain_unsupported_integrity_state", "explanation_chain_unsupported_drift", "cross_boundary_continuity_unsupported", "evidence_chain_blocker_continuity", "lineage::v4_5a_5.diagnostics", "provenance::v4_5a_5.diagnostics", "continuity_reference_unsupported", ("evidence_gap_missing_cross_boundary_evidence",), 5),
        (DIAGNOSTIC_SOURCE_UNSUPPORTED_STATE, "drift_chain_unsupported", "propagation_chain_cross_boundary", "degradation_chain_unsupported_integrity_state", "explanation_chain_unsupported_drift", "cross_boundary_continuity_unsupported", "evidence_chain_blocker_continuity", "lineage::v4_5a_5.unsupported", "provenance::v4_5a_5.unsupported", "continuity_reference_unsupported", ("unsupported_summary_unsupported_operational_states",), 6),
        (DIAGNOSTIC_SOURCE_INHERITED_PROHIBITION, "drift_chain_governance", "propagation_chain_continuity", "degradation_chain_provenance", "explanation_chain_scope_drift", "cross_boundary_continuity_governance_scope", "evidence_chain_provenance_continuity", "lineage::v4_5a_5.prohibitions", "provenance::v4_5a_5.prohibitions", "continuity_reference_governance_scope", ("blocker_warning_inherited_blockers",), 7),
        (DIAGNOSTIC_SOURCE_INHERITED_CONSTRAINT, "drift_chain_governance", "propagation_chain_continuity", "degradation_chain_provenance", "explanation_chain_scope_drift", "cross_boundary_continuity_governance_scope", "evidence_chain_lineage_continuity", "lineage::v4_5a_5.constraints", "provenance::v4_5a_5.constraints", "continuity_reference_governance_scope", ("blocker_warning_inherited_warnings",), 8),
    )
    return tuple(
        DiagnosticAggregationRecord(
            aggregation_record_id=f"diagnostic_aggregation_record_{source_type}",
            diagnostic_aggregation_id=f"diagnostic_aggregation_{source_type}",
            source_drift_id=source_drift_id,
            propagation_chain_id=propagation_chain_id,
            degradation_chain_id=degradation_chain_id,
            explanation_chain_id=explanation_chain_id,
            cross_boundary_continuity_id=cross_boundary_continuity_id,
            evidence_chain_id=evidence_chain_id,
            lineage_reference_id=lineage_reference_id,
            provenance_reference_id=provenance_reference_id,
            continuity_reference_id=continuity_reference_id,
            source_diagnostic_type=source_type,
            source_report_reference=SOURCE_REPORTS[source_type][0],
            source_hash_reference=SOURCE_REPORTS[source_type][1],
            evidence_reference_ids=evidence_reference_ids,
            visibility_state=AGGREGATION_VISIBILITY_VISIBLE,
            deterministic_order=order,
        )
        for (
            source_type,
            source_drift_id,
            propagation_chain_id,
            degradation_chain_id,
            explanation_chain_id,
            cross_boundary_continuity_id,
            evidence_chain_id,
            lineage_reference_id,
            provenance_reference_id,
            continuity_reference_id,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_diagnostic_source_aggregation() -> tuple[DiagnosticSourceAggregation, ...]:
    counts = {
        DIAGNOSTIC_SOURCE_DRIFT_FOUNDATION: (7, 17, 2, 3, 20, 14),
        DIAGNOSTIC_SOURCE_PROPAGATION: (8, 20, 3, 4, 20, 14),
        DIAGNOSTIC_SOURCE_DEGRADATION: (8, 21, 4, 5, 20, 14),
        DIAGNOSTIC_SOURCE_EXPLAINABILITY: (8, 24, 4, 5, 23, 15),
        DIAGNOSTIC_SOURCE_CROSS_BOUNDARY: (9, 21, 5, 8, 21, 15),
        DIAGNOSTIC_SOURCE_UNSUPPORTED_STATE: (24, 24, 0, 0, 24, 17),
        DIAGNOSTIC_SOURCE_INHERITED_PROHIBITION: (24, 0, 0, 0, 24, 17),
        DIAGNOSTIC_SOURCE_INHERITED_CONSTRAINT: (17, 0, 0, 0, 24, 17),
    }
    records = default_diagnostic_aggregation_records()
    return tuple(
        DiagnosticSourceAggregation(
            source_aggregation_id=f"diagnostic_source_{record.source_diagnostic_type}",
            aggregation_record_id=record.aggregation_record_id,
            source_type=record.source_diagnostic_type,
            source_report_reference=record.source_report_reference,
            source_hash_reference=record.source_hash_reference,
            diagnostic_count=counts[record.source_diagnostic_type][0],
            unsupported_state_count=counts[record.source_diagnostic_type][1],
            evidence_gap_count=counts[record.source_diagnostic_type][2],
            continuity_gap_count=counts[record.source_diagnostic_type][3],
            inherited_prohibition_count=counts[record.source_diagnostic_type][4],
            inherited_constraint_count=counts[record.source_diagnostic_type][5],
            visibility_state=AGGREGATION_VISIBILITY_SOURCE_VISIBLE,
            deterministic_order=record.deterministic_order,
        )
        for record in records
    )


def default_unsupported_state_summaries() -> tuple[UnsupportedStateSummaryVisibility, ...]:
    count_by_type = {
        UNSUPPORTED_SUMMARY_DRIFT: 17,
        UNSUPPORTED_SUMMARY_PROPAGATION: 20,
        UNSUPPORTED_SUMMARY_DEGRADATION: 21,
        UNSUPPORTED_SUMMARY_EXPLANATION: 24,
        UNSUPPORTED_SUMMARY_CROSS_BOUNDARY: 21,
        UNSUPPORTED_SUMMARY_OPERATIONAL: 24,
        UNSUPPORTED_SUMMARY_EVIDENCE: 8,
        UNSUPPORTED_SUMMARY_CONTINUITY: 8,
    }
    records = default_diagnostic_aggregation_records()
    return tuple(
        UnsupportedStateSummaryVisibility(
            unsupported_summary_id=f"unsupported_summary_{summary_type}",
            aggregation_record_id=records[index].aggregation_record_id,
            unsupported_summary_type=summary_type,
            source_reference=f"{records[index].source_report_reference}#{summary_type}",
            source_hash_reference=records[index].source_hash_reference,
            state_count=count_by_type[summary_type],
            evidence_reference_ids=(f"unsupported_summary_{summary_type}",),
            visibility_state=AGGREGATION_VISIBILITY_UNSUPPORTED_VISIBLE,
            deterministic_order=index + 1,
        )
        for index, summary_type in enumerate(UNSUPPORTED_STATE_SUMMARY_TYPES)
    )


def default_evidence_gap_summaries() -> tuple[EvidenceGapSummaryVisibility, ...]:
    records = default_diagnostic_aggregation_records()
    return tuple(
        EvidenceGapSummaryVisibility(
            evidence_gap_id=f"evidence_gap_{gap_type}",
            aggregation_record_id=records[index % len(records)].aggregation_record_id,
            evidence_gap_type=gap_type,
            source_reference=f"{records[index % len(records)].source_report_reference}#{gap_type}",
            source_hash_reference=records[index % len(records)].source_hash_reference,
            evidence_reference_ids=(f"evidence_gap_{gap_type}",),
            visibility_state=AGGREGATION_VISIBILITY_EVIDENCE_GAP_VISIBLE,
            deterministic_order=index + 1,
        )
        for index, gap_type in enumerate(EVIDENCE_GAP_SUMMARY_TYPES)
    )


def default_continuity_gap_summaries() -> tuple[ContinuityGapSummaryVisibility, ...]:
    records = default_diagnostic_aggregation_records()
    return tuple(
        ContinuityGapSummaryVisibility(
            continuity_gap_id=f"continuity_gap_{gap_type}",
            aggregation_record_id=records[index].aggregation_record_id,
            continuity_gap_type=gap_type,
            continuity_reference_id=records[index].continuity_reference_id,
            source_reference=f"{records[index].source_report_reference}#{gap_type}",
            source_hash_reference=records[index].source_hash_reference,
            evidence_reference_ids=(f"continuity_gap_{gap_type}",),
            visibility_state=AGGREGATION_VISIBILITY_CONTINUITY_GAP_VISIBLE,
            deterministic_order=index + 1,
        )
        for index, gap_type in enumerate(CONTINUITY_GAP_SUMMARY_TYPES)
    )


def default_severity_summaries() -> tuple[DiagnosticSeveritySummaryVisibility, ...]:
    records = default_diagnostic_aggregation_records()
    counts = (8, 9, 10, 7, 5)
    return tuple(
        DiagnosticSeveritySummaryVisibility(
            severity_summary_id=f"severity_summary_{severity_type}",
            aggregation_record_id=records[index].aggregation_record_id,
            severity_type=severity_type,
            diagnostic_count=counts[index],
            visibility_reason=(
                f"{severity_type} is descriptive visibility only and is not ranking, "
                "recommendation, authorization, execution, or triage automation."
            ),
            evidence_reference_ids=(f"severity_summary_{severity_type}",),
            visibility_state=AGGREGATION_VISIBILITY_SEVERITY_VISIBLE,
            deterministic_order=index + 1,
        )
        for index, severity_type in enumerate(DIAGNOSTIC_SEVERITY_SUMMARY_TYPES)
    )


def default_blocker_warning_summaries() -> tuple[BlockerWarningSummaryVisibility, ...]:
    records = default_diagnostic_aggregation_records()
    return tuple(
        BlockerWarningSummaryVisibility(
            blocker_warning_id=f"blocker_warning_{summary_type}",
            aggregation_record_id=records[index % len(records)].aggregation_record_id,
            blocker_warning_type=summary_type,
            visibility_category="blocker" if "blocker" in summary_type else "warning",
            source_reference=f"{records[index % len(records)].source_report_reference}#{summary_type}",
            source_hash_reference=records[index % len(records)].source_hash_reference,
            evidence_reference_ids=(f"blocker_warning_{summary_type}",),
            visibility_state=AGGREGATION_VISIBILITY_BLOCKER_WARNING_VISIBLE,
            deterministic_order=index + 1,
        )
        for index, summary_type in enumerate(BLOCKER_WARNING_SUMMARY_TYPES)
    )


def default_aggregated_diagnostics() -> tuple[AggregatedDiagnosticRecord, ...]:
    records = default_diagnostic_aggregation_records()
    return tuple(
        AggregatedDiagnosticRecord(
            aggregated_diagnostic_id=f"aggregated_diagnostic_{diagnostic_type}",
            aggregation_record_id=records[index % len(records)].aggregation_record_id,
            diagnostic_type=diagnostic_type,
            source_reference=f"{records[index % len(records)].source_report_reference}#{diagnostic_type}",
            source_hash_reference=records[index % len(records)].source_hash_reference,
            continuity_reference_id=records[index % len(records)].continuity_reference_id,
            evidence_reference_ids=(f"aggregated_diagnostic_{diagnostic_type}",),
            message=f"{diagnostic_type} remains explicit, fail-visible, and descriptive-only.",
            visibility_state=AGGREGATION_VISIBILITY_DIAGNOSTIC_VISIBLE,
            deterministic_order=index + 1,
        )
        for index, diagnostic_type in enumerate(AGGREGATED_DIAGNOSTIC_TYPES)
    )


def default_unsupported_aggregation_visibility() -> tuple[UnsupportedAggregationVisibility, ...]:
    return tuple(
        UnsupportedAggregationVisibility(
            state_id=f"unsupported_aggregation_state_{unsupported_state}",
            unsupported_state=unsupported_state,
            visibility_state=AGGREGATION_VISIBILITY_UNSUPPORTED_VISIBLE,
            explicit_reason=(
                f"{unsupported_state} remains unsupported for v4.5A.6 drift "
                "diagnostics aggregation."
            ),
            evidence_reference_ids=("unsupported_summary_unsupported_operational_states",),
            deterministic_order=order,
        )
        for order, unsupported_state in enumerate(
            UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5a_6_drift_diagnostics_aggregation() -> (
    DriftDiagnosticsAggregationIntelligence
):
    return DriftDiagnosticsAggregationIntelligence(
        aggregation_identity=default_drift_diagnostics_aggregation_identity(),
        diagnostic_aggregation_records=default_diagnostic_aggregation_records(),
        diagnostic_source_aggregation=default_diagnostic_source_aggregation(),
        unsupported_state_summaries=default_unsupported_state_summaries(),
        evidence_gap_summaries=default_evidence_gap_summaries(),
        continuity_gap_summaries=default_continuity_gap_summaries(),
        severity_summaries=default_severity_summaries(),
        blocker_warning_summaries=default_blocker_warning_summaries(),
        aggregated_diagnostics=default_aggregated_diagnostics(),
        unsupported_aggregation_visibility=default_unsupported_aggregation_visibility(),
        deterministic_guarantees=(
            V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_DETERMINISTIC_GUARANTEES
        ),
        inherited_prohibitions=(
            V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_INHERITED_PROHIBITIONS
        ),
        inherited_constraints=(
            V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_INHERITED_CONSTRAINTS
        ),
        explicit_limitations=(
            V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_EXPLICIT_LIMITATIONS
        ),
    )
