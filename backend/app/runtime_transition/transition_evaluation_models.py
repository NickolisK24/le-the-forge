"""Deterministic v3.9 transition evaluation intelligence models.

These models evaluate transition relationships as immutable evidence only. They
do not execute transitions, traverse orchestration graphs, route work, schedule
work, dispatch work, mutate runtime state, optimize, recommend, rank, score,
select, authorize, approve, or create callable orchestration flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_EVALUATION_PHASE_ID = "v3_9_transition_evaluation_intelligence"
V3_9_TRANSITION_EVALUATION_SCHEMA_VERSION = "v3_9.transition_evaluation_intelligence.1"
V3_9_TRANSITION_EVALUATION_REPORT_STABLE = "v3_9_transition_evaluation_intelligence_stable"
V3_9_TRANSITION_EVALUATION_REPORT_BLOCKED = "v3_9_transition_evaluation_intelligence_blocked"

EVALUATION_CLASSIFICATION_SUCCESSFUL = "successful"
EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL = "partially_successful"
EVALUATION_CLASSIFICATION_UNSUCCESSFUL = "unsuccessful"
EVALUATION_CLASSIFICATION_UNSUPPORTED = "unsupported"
EVALUATION_CLASSIFICATION_PROHIBITED = "prohibited"
EVALUATION_CLASSIFICATION_UNKNOWN = "unknown"
EVALUATION_CLASSIFICATION_INCOMPLETE = "incomplete"
EVALUATION_CLASSIFICATION_BLOCKED = "blocked"
EVALUATION_CLASSIFICATIONS: tuple[str, ...] = (
    EVALUATION_CLASSIFICATION_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUPPORTED,
    EVALUATION_CLASSIFICATION_PROHIBITED,
    EVALUATION_CLASSIFICATION_UNKNOWN,
    EVALUATION_CLASSIFICATION_INCOMPLETE,
    EVALUATION_CLASSIFICATION_BLOCKED,
)
NON_SUCCESSFUL_EVALUATION_CLASSIFICATIONS: tuple[str, ...] = (
    EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUPPORTED,
    EVALUATION_CLASSIFICATION_PROHIBITED,
    EVALUATION_CLASSIFICATION_UNKNOWN,
    EVALUATION_CLASSIFICATION_INCOMPLETE,
    EVALUATION_CLASSIFICATION_BLOCKED,
)

EVALUATION_FINDING_COMPATIBILITY = "compatibility"
EVALUATION_FINDING_CONTINUITY = "continuity"
EVALUATION_FINDING_PROVENANCE = "provenance"
EVALUATION_FINDING_EXPLAINABILITY = "explainability"
EVALUATION_FINDING_GOVERNANCE = "governance"
EVALUATION_FINDING_INTEGRITY = "integrity"
EVALUATION_FINDING_UNSUPPORTED = "unsupported"
EVALUATION_FINDING_PROHIBITED = "prohibited"
EVALUATION_FINDING_MISSING_EVIDENCE = "missing_evidence"
EVALUATION_FINDING_UNCERTAINTY = "uncertainty"
EVALUATION_FINDING_CATEGORIES: tuple[str, ...] = (
    EVALUATION_FINDING_COMPATIBILITY,
    EVALUATION_FINDING_CONTINUITY,
    EVALUATION_FINDING_PROVENANCE,
    EVALUATION_FINDING_EXPLAINABILITY,
    EVALUATION_FINDING_GOVERNANCE,
    EVALUATION_FINDING_INTEGRITY,
    EVALUATION_FINDING_UNSUPPORTED,
    EVALUATION_FINDING_PROHIBITED,
    EVALUATION_FINDING_MISSING_EVIDENCE,
    EVALUATION_FINDING_UNCERTAINTY,
)

EVALUATION_VISIBILITY_VISIBLE = "visible"
EVALUATION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
EVALUATION_SEVERITY_INFO = "info"
EVALUATION_SEVERITY_WARNING = "warning"
EVALUATION_SEVERITY_BLOCKED = "blocked"

SUPPORTED_EVALUATION_CAPABILITIES: tuple[str, ...] = (
    "deterministic_transition_evaluation",
    "transition_compatibility_reference",
    "transition_provenance_reference",
    "transition_continuity_reference",
    "transition_evidence_reference",
    "transition_explainability_reference",
)
PROHIBITED_EVALUATION_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "transition_execution",
    "orchestration_traversal",
    "runtime_orchestration_engine",
    "routing",
    "scheduling",
    "dispatch",
    "runtime_mutation",
    "approval",
    "authorization",
    "optimization",
    "recommendation",
    "ranking",
    "scoring",
    "selection",
    "autonomous_orchestration_behavior",
    "transition_handler",
    "orchestration_evaluator",
    "runtime_state_machine",
    "callable_orchestration_flow",
    "production_execution_pathway",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionEvaluationInput:
    input_id: str
    source_transition_state_id: str
    destination_transition_state_id: str
    compatibility_classification: str
    compatibility_conflict_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    evaluation_evidence_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    partial_success_markers: tuple[str, ...] = ()
    partial_failure_markers: tuple[str, ...] = ()
    unsuccessful_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    governance_policy_ids: tuple[str, ...] = ()
    integrity_policy_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    non_executable_evaluation: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "compatibility_conflict_ids",
            "provenance_reference_ids",
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "evaluation_evidence_ids",
            "requested_capabilities",
            "partial_success_markers",
            "partial_failure_markers",
            "unsuccessful_markers",
            "unsupported_markers",
            "prohibited_markers",
            "unknown_markers",
            "incomplete_markers",
            "blocked_markers",
            "governance_policy_ids",
            "integrity_policy_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionEvaluationContinuity:
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
class TransitionEvaluationEvidence:
    evidence_id: str
    input_id: str
    evaluation_evidence_ids: tuple[str, ...]
    compatibility_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_evaluation_reasoning_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    execution_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_evidence_ids",
            "compatibility_reference_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
            "finding_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionEvaluationVisibility:
    visibility_id: str
    input_id: str
    classification: str
    visibility_status: str
    reason: str
    deterministic_evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    fail_visible: bool = True
    hidden: bool = False
    uncertainty_visible: bool = True


@dataclass(frozen=True)
class TransitionEvaluationFinding:
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
    uncertainty_visible: bool = False
    execution_boundary_violation_detected: bool = False
    non_execution_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True


@dataclass(frozen=True)
class TransitionEvaluationSummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    finding_category_counts: Mapping[str, int]
    successful_count: int
    partially_successful_count: int
    unsuccessful_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    incomplete_count: int
    blocked_count: int
    evaluation_finding_count: int
    governance_finding_count: int
    uncertainty_finding_count: int
    missing_evidence_finding_count: int
    execution_boundary_violation_count: int
    hidden_finding_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "finding_category_counts", dict(sorted(self.finding_category_counts.items())))


@dataclass(frozen=True)
class TransitionEvaluationReport:
    report_id: str
    report_status: str
    source_foundation_id: str
    source_boundary_report_id: str
    source_compatibility_report_id: str
    evaluation_inputs: tuple[TransitionEvaluationInput, ...]
    findings: tuple[TransitionEvaluationFinding, ...]
    evidence_records: tuple[TransitionEvaluationEvidence, ...]
    continuities: tuple[TransitionEvaluationContinuity, ...]
    visibilities: tuple[TransitionEvaluationVisibility, ...]
    summary: TransitionEvaluationSummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_evaluation_hash: str = ""
    non_executable: bool = True
    transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    runtime_orchestration_engine_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    runtime_mutation_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    autonomous_orchestration_behavior_enabled: bool = False
    transition_handler_enabled: bool = False
    orchestration_evaluator_enabled: bool = False
    runtime_state_machine_enabled: bool = False
    callable_orchestration_flow_enabled: bool = False
    production_execution_pathway_enabled: bool = False
    hidden_fallback_enabled: bool = False
    silent_correction_enabled: bool = False
    implicit_approval_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("evaluation_inputs", "findings", "evidence_records", "continuities", "visibilities"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_evaluation_finding_id(input_id: str, finding_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_evaluation_{input_id}_{finding_category}_{safe_marker}"


def export_transition_evaluation_input(source: TransitionEvaluationInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "compatibility_conflict_ids",
        "provenance_reference_ids",
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "evaluation_evidence_ids",
        "requested_capabilities",
        "partial_success_markers",
        "partial_failure_markers",
        "unsuccessful_markers",
        "unsupported_markers",
        "prohibited_markers",
        "unknown_markers",
        "incomplete_markers",
        "blocked_markers",
        "governance_policy_ids",
        "integrity_policy_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_evaluation_continuity(continuity: TransitionEvaluationContinuity) -> dict[str, Any]:
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


def export_transition_evaluation_evidence(evidence: TransitionEvaluationEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evaluation_evidence_ids",
        "compatibility_reference_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
        "finding_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_evaluation_visibility(visibility: TransitionEvaluationVisibility) -> dict[str, Any]:
    return asdict(visibility)


def export_transition_evaluation_finding(finding: TransitionEvaluationFinding) -> dict[str, Any]:
    return asdict(finding)


def export_transition_evaluation_summary(summary: TransitionEvaluationSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["finding_category_counts"] = dict(sorted(summary.finding_category_counts.items()))
    return data


def export_transition_evaluation_report(report: TransitionEvaluationReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_foundation_id": report.source_foundation_id,
        "source_boundary_report_id": report.source_boundary_report_id,
        "source_compatibility_report_id": report.source_compatibility_report_id,
        "evaluation_inputs": [
            export_transition_evaluation_input(source)
            for source in sorted(report.evaluation_inputs, key=lambda item: item.input_id)
        ],
        "findings": [
            export_transition_evaluation_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "evidence_records": [
            export_transition_evaluation_evidence(evidence)
            for evidence in sorted(report.evidence_records, key=lambda item: item.evidence_id)
        ],
        "continuities": [
            export_transition_evaluation_continuity(continuity)
            for continuity in sorted(report.continuities, key=lambda item: item.continuity_id)
        ],
        "visibilities": [
            export_transition_evaluation_visibility(visibility)
            for visibility in sorted(report.visibilities, key=lambda item: item.visibility_id)
        ],
        "summary": export_transition_evaluation_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_evaluation_hash": report.deterministic_evaluation_hash,
        "non_executable": report.non_executable,
        "transition_execution_enabled": report.transition_execution_enabled,
        "orchestration_execution_enabled": report.orchestration_execution_enabled,
        "orchestration_traversal_enabled": report.orchestration_traversal_enabled,
        "runtime_orchestration_engine_enabled": report.runtime_orchestration_engine_enabled,
        "routing_enabled": report.routing_enabled,
        "scheduling_enabled": report.scheduling_enabled,
        "dispatch_enabled": report.dispatch_enabled,
        "runtime_mutation_enabled": report.runtime_mutation_enabled,
        "approval_enabled": report.approval_enabled,
        "authorization_enabled": report.authorization_enabled,
        "optimization_enabled": report.optimization_enabled,
        "recommendation_enabled": report.recommendation_enabled,
        "ranking_enabled": report.ranking_enabled,
        "scoring_enabled": report.scoring_enabled,
        "selection_enabled": report.selection_enabled,
        "autonomous_orchestration_behavior_enabled": report.autonomous_orchestration_behavior_enabled,
        "transition_handler_enabled": report.transition_handler_enabled,
        "orchestration_evaluator_enabled": report.orchestration_evaluator_enabled,
        "runtime_state_machine_enabled": report.runtime_state_machine_enabled,
        "callable_orchestration_flow_enabled": report.callable_orchestration_flow_enabled,
        "production_execution_pathway_enabled": report.production_execution_pathway_enabled,
        "hidden_fallback_enabled": report.hidden_fallback_enabled,
        "silent_correction_enabled": report.silent_correction_enabled,
        "implicit_approval_enabled": report.implicit_approval_enabled,
    }
