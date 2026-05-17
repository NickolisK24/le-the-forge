"""Deterministic v3.9 transition intelligence aggregation models.

These models aggregate prior transition evidence into descriptive summaries.
They do not execute, traverse, route, schedule, dispatch, authorize, approve,
mutate, optimize, recommend, rank, score, select, prioritize, or expose
callable orchestration behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_AGGREGATION_PHASE_ID = "v3_9_transition_intelligence_aggregation"
V3_9_TRANSITION_AGGREGATION_SCHEMA_VERSION = "v3_9.transition_intelligence_aggregation.1"
V3_9_TRANSITION_AGGREGATION_REPORT_STABLE = "v3_9_transition_intelligence_aggregation_stable"
V3_9_TRANSITION_AGGREGATION_REPORT_BLOCKED = "v3_9_transition_intelligence_aggregation_blocked"

AGGREGATION_CLASSIFICATION_AGGREGATED = "aggregated"
AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED = "partially_aggregated"
AGGREGATION_CLASSIFICATION_UNAGGREGATED = "unaggregated"
AGGREGATION_CLASSIFICATION_BLOCKED = "blocked"
AGGREGATION_CLASSIFICATION_UNSUPPORTED = "unsupported"
AGGREGATION_CLASSIFICATION_PROHIBITED = "prohibited"
AGGREGATION_CLASSIFICATION_UNKNOWN = "unknown"
AGGREGATION_CLASSIFICATION_INCOMPLETE = "incomplete"
AGGREGATION_CLASSIFICATIONS: tuple[str, ...] = (
    AGGREGATION_CLASSIFICATION_AGGREGATED,
    AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
    AGGREGATION_CLASSIFICATION_UNAGGREGATED,
    AGGREGATION_CLASSIFICATION_BLOCKED,
    AGGREGATION_CLASSIFICATION_UNSUPPORTED,
    AGGREGATION_CLASSIFICATION_PROHIBITED,
    AGGREGATION_CLASSIFICATION_UNKNOWN,
    AGGREGATION_CLASSIFICATION_INCOMPLETE,
)
NON_AGGREGATED_CLASSIFICATIONS: tuple[str, ...] = (
    AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
    AGGREGATION_CLASSIFICATION_UNAGGREGATED,
    AGGREGATION_CLASSIFICATION_BLOCKED,
    AGGREGATION_CLASSIFICATION_UNSUPPORTED,
    AGGREGATION_CLASSIFICATION_PROHIBITED,
    AGGREGATION_CLASSIFICATION_UNKNOWN,
    AGGREGATION_CLASSIFICATION_INCOMPLETE,
)

AGGREGATION_DOMAIN_FOUNDATIONS = "foundations"
AGGREGATION_DOMAIN_BOUNDARY = "boundary_intelligence"
AGGREGATION_DOMAIN_COMPATIBILITY = "compatibility_intelligence"
AGGREGATION_DOMAIN_EVALUATION = "evaluation_intelligence"
AGGREGATION_DOMAIN_SESSION = "session_intelligence"
AGGREGATION_DOMAIN_SCENARIO = "scenario_intelligence"
REQUIRED_AGGREGATION_DOMAINS: tuple[str, ...] = (
    AGGREGATION_DOMAIN_FOUNDATIONS,
    AGGREGATION_DOMAIN_BOUNDARY,
    AGGREGATION_DOMAIN_COMPATIBILITY,
    AGGREGATION_DOMAIN_EVALUATION,
    AGGREGATION_DOMAIN_SESSION,
    AGGREGATION_DOMAIN_SCENARIO,
)

AGGREGATION_FINDING_FOUNDATION = "foundation"
AGGREGATION_FINDING_BOUNDARY = "boundary"
AGGREGATION_FINDING_COMPATIBILITY = "compatibility"
AGGREGATION_FINDING_EVALUATION = "evaluation"
AGGREGATION_FINDING_SESSION = "session"
AGGREGATION_FINDING_SCENARIO = "scenario"
AGGREGATION_FINDING_VISIBILITY = "aggregation_visibility"
AGGREGATION_FINDING_CONTINUITY = "continuity"
AGGREGATION_FINDING_PROVENANCE = "provenance"
AGGREGATION_FINDING_EXPLAINABILITY = "explainability"
AGGREGATION_FINDING_GOVERNANCE = "governance"
AGGREGATION_FINDING_INTEGRITY = "integrity"
AGGREGATION_FINDING_UNSUPPORTED = "unsupported"
AGGREGATION_FINDING_PROHIBITED = "prohibited"
AGGREGATION_FINDING_MISSING_EVIDENCE = "missing_evidence"
AGGREGATION_FINDING_UNCERTAINTY = "uncertainty"
AGGREGATION_FINDING_CATEGORIES: tuple[str, ...] = (
    AGGREGATION_FINDING_FOUNDATION,
    AGGREGATION_FINDING_BOUNDARY,
    AGGREGATION_FINDING_COMPATIBILITY,
    AGGREGATION_FINDING_EVALUATION,
    AGGREGATION_FINDING_SESSION,
    AGGREGATION_FINDING_SCENARIO,
    AGGREGATION_FINDING_VISIBILITY,
    AGGREGATION_FINDING_CONTINUITY,
    AGGREGATION_FINDING_PROVENANCE,
    AGGREGATION_FINDING_EXPLAINABILITY,
    AGGREGATION_FINDING_GOVERNANCE,
    AGGREGATION_FINDING_INTEGRITY,
    AGGREGATION_FINDING_UNSUPPORTED,
    AGGREGATION_FINDING_PROHIBITED,
    AGGREGATION_FINDING_MISSING_EVIDENCE,
    AGGREGATION_FINDING_UNCERTAINTY,
)

AGGREGATION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
AGGREGATION_VISIBILITY_UNSUPPORTED_STATE = "unsupported_state"
AGGREGATION_VISIBILITY_PROHIBITED_STATE = "prohibited_state"
AGGREGATION_VISIBILITY_UNCERTAINTY = "uncertainty"
AGGREGATION_VISIBILITY_CONTINUITY = "continuity"
AGGREGATION_VISIBILITY_PROVENANCE = "provenance"
AGGREGATION_VISIBILITY_EXPLAINABILITY = "explainability"
AGGREGATION_VISIBILITY_INTEGRITY = "integrity"
AGGREGATION_VISIBILITY_GOVERNANCE = "governance"
AGGREGATION_VISIBILITY_SCENARIO_RISK = "scenario_risk"
AGGREGATION_VISIBILITY_MISSING_EVIDENCE = "missing_evidence"
AGGREGATION_VISIBILITY_CATEGORIES: tuple[str, ...] = (
    AGGREGATION_VISIBILITY_FAIL_VISIBLE,
    AGGREGATION_VISIBILITY_UNSUPPORTED_STATE,
    AGGREGATION_VISIBILITY_PROHIBITED_STATE,
    AGGREGATION_VISIBILITY_UNCERTAINTY,
    AGGREGATION_VISIBILITY_CONTINUITY,
    AGGREGATION_VISIBILITY_PROVENANCE,
    AGGREGATION_VISIBILITY_EXPLAINABILITY,
    AGGREGATION_VISIBILITY_INTEGRITY,
    AGGREGATION_VISIBILITY_GOVERNANCE,
    AGGREGATION_VISIBILITY_SCENARIO_RISK,
    AGGREGATION_VISIBILITY_MISSING_EVIDENCE,
)

AGGREGATION_SEVERITY_INFO = "info"
AGGREGATION_SEVERITY_WARNING = "warning"
AGGREGATION_SEVERITY_BLOCKED = "blocked"

SUPPORTED_AGGREGATION_CAPABILITIES: tuple[str, ...] = (
    "deterministic_transition_intelligence_aggregation",
    "transition_foundation_reference",
    "transition_boundary_reference",
    "transition_compatibility_reference",
    "transition_evaluation_reference",
    "transition_session_reference",
    "transition_scenario_reference",
    "transition_visibility_aggregation",
    "transition_risk_visibility_aggregation",
)
PROHIBITED_AGGREGATION_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "transition_execution",
    "graph_traversal",
    "routing",
    "scheduling",
    "dispatch",
    "runtime_orchestration_engine",
    "runtime_mutation",
    "authorization",
    "approval",
    "optimization",
    "recommendation",
    "ranking",
    "scoring",
    "selection",
    "autonomous_behavior",
    "callable_orchestration_flow",
    "transition_handler",
    "runtime_state_machine",
    "production_behavior",
)
AGGREGATION_CHOICE_PROHIBITED_CAPABILITIES: tuple[str, ...] = (
    "recommendation",
    "ranking",
    "scoring",
    "selection",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionAggregationInput:
    input_id: str
    aggregation_id: str
    aggregation_domain: str
    required_domain_ids: tuple[str, ...]
    present_domain_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    risk_visibility_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    partial_success_markers: tuple[str, ...] = ()
    partial_failure_markers: tuple[str, ...] = ()
    unaggregated_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    governance_policy_ids: tuple[str, ...] = ()
    integrity_policy_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    non_executable_aggregation: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "required_domain_ids",
            "present_domain_ids",
            "evidence_ids",
            "provenance_reference_ids",
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "risk_visibility_ids",
            "requested_capabilities",
            "partial_success_markers",
            "partial_failure_markers",
            "unaggregated_markers",
            "incomplete_markers",
            "blocked_markers",
            "unsupported_markers",
            "prohibited_markers",
            "unknown_markers",
            "governance_policy_ids",
            "integrity_policy_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionAggregationFinding:
    finding_id: str
    input_id: str
    finding_category: str
    classification: str
    severity: str
    reason: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    execution_boundary_violation_detected: bool = False
    recommendation_boundary_violation_detected: bool = False
    non_execution_confirmation: bool = True
    no_recommendation_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True


@dataclass(frozen=True)
class TransitionAggregationVisibility:
    visibility_id: str
    input_id: str
    visibility_category: str
    classification: str
    reason: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    descriptive_only: bool = True
    prioritization_enabled: bool = False
    weighting_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False


@dataclass(frozen=True)
class TransitionAggregationContinuity:
    continuity_id: str
    input_id: str
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    evidence_continuity_ids: tuple[str, ...]
    deterministic_hash_reference: str
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    explainability_continuity_preserved: bool = True
    immutable_continuity: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "evidence_continuity_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionAggregationProvenance:
    provenance_id: str
    input_id: str
    provenance_reference_ids: tuple[str, ...]
    source_domain_ids: tuple[str, ...]
    evidence_reference: str
    deterministic_hash_reference: str
    provenance_preserved: bool = True
    immutable_provenance: bool = True

    def __post_init__(self) -> None:
        for field_name in ("provenance_reference_ids", "source_domain_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionAggregationRiskVisibility:
    risk_visibility_id: str
    input_id: str
    scenario_risk_visibility_ids: tuple[str, ...]
    visibility_reference_ids: tuple[str, ...]
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    hidden: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("scenario_risk_visibility_ids", "visibility_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionAggregationEvidence:
    evidence_id: str
    input_id: str
    aggregation_id: str
    source_domain_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    visibility_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    risk_visibility_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_intelligence_aggregation_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    execution_behavior_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    ranking_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    selection_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_domain_ids",
            "evidence_ids",
            "finding_ids",
            "visibility_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
            "risk_visibility_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionAggregationRecord:
    record_id: str
    input_id: str
    aggregation_id: str
    classification: str
    findings: tuple[TransitionAggregationFinding, ...]
    visibilities: tuple[TransitionAggregationVisibility, ...]
    evidence: TransitionAggregationEvidence
    continuity: TransitionAggregationContinuity
    provenance: TransitionAggregationProvenance
    risk_visibility: TransitionAggregationRiskVisibility
    deterministic_order: int
    immutable_record: bool = True
    non_executable: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("findings", "visibilities"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


@dataclass(frozen=True)
class TransitionAggregationSummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    finding_category_counts: Mapping[str, int]
    visibility_category_counts: Mapping[str, int]
    aggregated_count: int
    partially_aggregated_count: int
    unaggregated_count: int
    blocked_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    incomplete_count: int
    aggregation_finding_count: int
    aggregation_visibility_count: int
    governance_visibility_count: int
    integrity_visibility_count: int
    uncertainty_visibility_count: int
    missing_evidence_visibility_count: int
    hidden_aggregation_finding_count: int
    hidden_visibility_count: int
    execution_boundary_violation_count: int
    recommendation_ranking_scoring_selection_violation_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "finding_category_counts", dict(sorted(self.finding_category_counts.items())))
        object.__setattr__(self, "visibility_category_counts", dict(sorted(self.visibility_category_counts.items())))


@dataclass(frozen=True)
class TransitionAggregationReport:
    report_id: str
    report_status: str
    source_foundation_id: str
    source_boundary_report_id: str
    source_compatibility_report_id: str
    source_evaluation_report_id: str
    source_session_report_id: str
    source_scenario_report_id: str
    aggregation_inputs: tuple[TransitionAggregationInput, ...]
    aggregation_records: tuple[TransitionAggregationRecord, ...]
    findings: tuple[TransitionAggregationFinding, ...]
    visibilities: tuple[TransitionAggregationVisibility, ...]
    evidence_records: tuple[TransitionAggregationEvidence, ...]
    continuities: tuple[TransitionAggregationContinuity, ...]
    provenance_records: tuple[TransitionAggregationProvenance, ...]
    risk_visibility_records: tuple[TransitionAggregationRiskVisibility, ...]
    summary: TransitionAggregationSummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_aggregation_hash: str = ""
    non_executable: bool = True
    orchestration_execution_enabled: bool = False
    transition_execution_enabled: bool = False
    graph_traversal_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    runtime_orchestration_engine_enabled: bool = False
    runtime_mutation_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    callable_orchestration_flow_enabled: bool = False
    transition_handler_enabled: bool = False
    runtime_state_machine_enabled: bool = False
    production_behavior_enabled: bool = False
    hidden_fallback_enabled: bool = False
    silent_correction_enabled: bool = False
    prioritization_enabled: bool = False
    weighting_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "aggregation_inputs",
            "aggregation_records",
            "findings",
            "visibilities",
            "evidence_records",
            "continuities",
            "provenance_records",
            "risk_visibility_records",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_aggregation_finding_id(input_id: str, finding_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_aggregation_{input_id}_{finding_category}_{safe_marker}"


def export_transition_aggregation_input(source: TransitionAggregationInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "required_domain_ids",
        "present_domain_ids",
        "evidence_ids",
        "provenance_reference_ids",
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "risk_visibility_ids",
        "requested_capabilities",
        "partial_success_markers",
        "partial_failure_markers",
        "unaggregated_markers",
        "incomplete_markers",
        "blocked_markers",
        "unsupported_markers",
        "prohibited_markers",
        "unknown_markers",
        "governance_policy_ids",
        "integrity_policy_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_aggregation_finding(finding: TransitionAggregationFinding) -> dict[str, Any]:
    return asdict(finding)


def export_transition_aggregation_visibility(visibility: TransitionAggregationVisibility) -> dict[str, Any]:
    return asdict(visibility)


def export_transition_aggregation_continuity(continuity: TransitionAggregationContinuity) -> dict[str, Any]:
    data = asdict(continuity)
    for field_name in (
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "evidence_continuity_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_aggregation_provenance(provenance: TransitionAggregationProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in ("provenance_reference_ids", "source_domain_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_aggregation_risk_visibility(
    risk_visibility: TransitionAggregationRiskVisibility,
) -> dict[str, Any]:
    data = asdict(risk_visibility)
    for field_name in ("scenario_risk_visibility_ids", "visibility_reference_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_aggregation_evidence(evidence: TransitionAggregationEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_domain_ids",
        "evidence_ids",
        "finding_ids",
        "visibility_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
        "risk_visibility_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_aggregation_record(record: TransitionAggregationRecord) -> dict[str, Any]:
    return {
        "record_id": record.record_id,
        "input_id": record.input_id,
        "aggregation_id": record.aggregation_id,
        "classification": record.classification,
        "findings": [
            export_transition_aggregation_finding(finding)
            for finding in sorted(record.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "visibilities": [
            export_transition_aggregation_visibility(visibility)
            for visibility in sorted(record.visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))
        ],
        "evidence": export_transition_aggregation_evidence(record.evidence),
        "continuity": export_transition_aggregation_continuity(record.continuity),
        "provenance": export_transition_aggregation_provenance(record.provenance),
        "risk_visibility": export_transition_aggregation_risk_visibility(record.risk_visibility),
        "deterministic_order": record.deterministic_order,
        "immutable_record": record.immutable_record,
        "non_executable": record.non_executable,
        "recommendation_enabled": record.recommendation_enabled,
        "ranking_enabled": record.ranking_enabled,
        "scoring_enabled": record.scoring_enabled,
        "selection_enabled": record.selection_enabled,
    }


def export_transition_aggregation_summary(summary: TransitionAggregationSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["finding_category_counts"] = dict(sorted(summary.finding_category_counts.items()))
    data["visibility_category_counts"] = dict(sorted(summary.visibility_category_counts.items()))
    return data


def export_transition_aggregation_report(report: TransitionAggregationReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_foundation_id": report.source_foundation_id,
        "source_boundary_report_id": report.source_boundary_report_id,
        "source_compatibility_report_id": report.source_compatibility_report_id,
        "source_evaluation_report_id": report.source_evaluation_report_id,
        "source_session_report_id": report.source_session_report_id,
        "source_scenario_report_id": report.source_scenario_report_id,
        "aggregation_inputs": [
            export_transition_aggregation_input(source)
            for source in sorted(report.aggregation_inputs, key=lambda item: item.input_id)
        ],
        "aggregation_records": [
            export_transition_aggregation_record(record)
            for record in sorted(report.aggregation_records, key=lambda item: (item.deterministic_order, item.record_id))
        ],
        "findings": [
            export_transition_aggregation_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "visibilities": [
            export_transition_aggregation_visibility(visibility)
            for visibility in sorted(report.visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))
        ],
        "evidence_records": [
            export_transition_aggregation_evidence(evidence)
            for evidence in sorted(report.evidence_records, key=lambda item: item.evidence_id)
        ],
        "continuities": [
            export_transition_aggregation_continuity(continuity)
            for continuity in sorted(report.continuities, key=lambda item: item.continuity_id)
        ],
        "provenance_records": [
            export_transition_aggregation_provenance(provenance)
            for provenance in sorted(report.provenance_records, key=lambda item: item.provenance_id)
        ],
        "risk_visibility_records": [
            export_transition_aggregation_risk_visibility(risk_visibility)
            for risk_visibility in sorted(
                report.risk_visibility_records,
                key=lambda item: item.risk_visibility_id,
            )
        ],
        "summary": export_transition_aggregation_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_aggregation_hash": report.deterministic_aggregation_hash,
        "non_executable": report.non_executable,
        "orchestration_execution_enabled": report.orchestration_execution_enabled,
        "transition_execution_enabled": report.transition_execution_enabled,
        "graph_traversal_enabled": report.graph_traversal_enabled,
        "routing_enabled": report.routing_enabled,
        "scheduling_enabled": report.scheduling_enabled,
        "dispatch_enabled": report.dispatch_enabled,
        "runtime_orchestration_engine_enabled": report.runtime_orchestration_engine_enabled,
        "runtime_mutation_enabled": report.runtime_mutation_enabled,
        "authorization_enabled": report.authorization_enabled,
        "approval_enabled": report.approval_enabled,
        "optimization_enabled": report.optimization_enabled,
        "recommendation_enabled": report.recommendation_enabled,
        "ranking_enabled": report.ranking_enabled,
        "scoring_enabled": report.scoring_enabled,
        "selection_enabled": report.selection_enabled,
        "autonomous_behavior_enabled": report.autonomous_behavior_enabled,
        "callable_orchestration_flow_enabled": report.callable_orchestration_flow_enabled,
        "transition_handler_enabled": report.transition_handler_enabled,
        "runtime_state_machine_enabled": report.runtime_state_machine_enabled,
        "production_behavior_enabled": report.production_behavior_enabled,
        "hidden_fallback_enabled": report.hidden_fallback_enabled,
        "silent_correction_enabled": report.silent_correction_enabled,
        "prioritization_enabled": report.prioritization_enabled,
        "weighting_enabled": report.weighting_enabled,
    }
