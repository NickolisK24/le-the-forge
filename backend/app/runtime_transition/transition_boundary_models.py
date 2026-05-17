"""Deterministic v3.9 transition boundary intelligence models.

These models classify coordination transition boundaries as immutable evidence.
They do not execute transitions, traverse graphs, route work, schedule work,
dispatch work, mutate runtime state, optimize, recommend, rank, score, select,
authorize, approve, or create callable orchestration flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_BOUNDARY_PHASE_ID = "v3_9_transition_boundary_intelligence"
V3_9_TRANSITION_BOUNDARY_SCHEMA_VERSION = "v3_9.transition_boundary_intelligence.1"
V3_9_TRANSITION_BOUNDARY_REPORT_STABLE = "v3_9_transition_boundary_intelligence_stable"
V3_9_TRANSITION_BOUNDARY_REPORT_BLOCKED = "v3_9_transition_boundary_intelligence_blocked"

BOUNDARY_CLASSIFICATION_SAFE = "safe"
BOUNDARY_CLASSIFICATION_UNSUPPORTED = "unsupported"
BOUNDARY_CLASSIFICATION_PROHIBITED = "prohibited"
BOUNDARY_CLASSIFICATION_UNKNOWN = "unknown"
BOUNDARY_CLASSIFICATION_INCOMPLETE = "incomplete"
BOUNDARY_CLASSIFICATION_BLOCKED = "blocked"
BOUNDARY_CLASSIFICATIONS: tuple[str, ...] = (
    BOUNDARY_CLASSIFICATION_SAFE,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_INCOMPLETE,
    BOUNDARY_CLASSIFICATION_BLOCKED,
)
NON_SAFE_BOUNDARY_CLASSIFICATIONS: tuple[str, ...] = (
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_INCOMPLETE,
    BOUNDARY_CLASSIFICATION_BLOCKED,
)

BOUNDARY_VISIBILITY_VISIBLE = "visible"
BOUNDARY_VISIBILITY_FAIL_VISIBLE = "fail_visible"
BOUNDARY_SEVERITY_INFO = "info"
BOUNDARY_SEVERITY_WARNING = "warning"
BOUNDARY_SEVERITY_BLOCKED = "blocked"

SUPPORTED_BOUNDARY_CAPABILITIES: tuple[str, ...] = (
    "deterministic_boundary_classification",
    "transition_identity_reference",
    "transition_provenance_reference",
    "transition_continuity_reference",
    "transition_evidence_reference",
)
PROHIBITED_BOUNDARY_CAPABILITIES: tuple[str, ...] = (
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
    "state_machine",
    "production_behavior",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionBoundaryInput:
    input_id: str
    source_state_id: str
    destination_state_id: str
    transition_identity_id: str
    transition_domain: str
    transition_intent: str
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    evidence_reference_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    governance_blockers: tuple[str, ...] = ()
    boundary_policy_violation_ids: tuple[str, ...] = ()
    integrity_precondition_failures: tuple[str, ...] = ()
    explainability_context: str = ""
    non_executable_boundary: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "evidence_reference_ids",
            "requested_capabilities",
            "unsupported_markers",
            "prohibited_markers",
            "unknown_markers",
            "incomplete_markers",
            "blocked_markers",
            "governance_blockers",
            "boundary_policy_violation_ids",
            "integrity_precondition_failures",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionBoundaryEvidence:
    evidence_id: str
    input_id: str
    source_state_id: str
    destination_state_id: str
    transition_identity_id: str
    evidence_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_boundary_classification_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    execution_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_reference_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionBoundaryClassification:
    classification: str
    severity: str
    visibility_status: str
    reason: str
    deterministic_evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    fail_visible: bool = True
    hidden: bool = False


@dataclass(frozen=True)
class TransitionBoundaryFinding:
    finding_id: str
    input_id: str
    classification: str
    severity: str
    reason: str
    deterministic_evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    evidence: TransitionBoundaryEvidence
    marker_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    non_safe_state: bool = True
    execution_boundary_violation_detected: bool = False
    non_execution_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True

    def __post_init__(self) -> None:
        for field_name in ("marker_ids", "requested_capabilities"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionBoundaryReport:
    boundary_report_id: str
    report_status: str
    source_foundation_id: str
    boundary_inputs: tuple[TransitionBoundaryInput, ...]
    classifications: tuple[TransitionBoundaryClassification, ...]
    findings: tuple[TransitionBoundaryFinding, ...]
    classification_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_boundary_hash: str = ""
    non_executable: bool = True
    transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
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
    state_machine_enabled: bool = False
    production_behavior_enabled: bool = False
    hidden_fallback_enabled: bool = False
    silent_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("boundary_inputs", "classifications", "findings"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def transition_boundary_finding_id(classification: str, input_id: str) -> str:
    return f"v3_9_transition_boundary_{classification}_{input_id}"


def export_transition_boundary_input(source: TransitionBoundaryInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "provenance_reference_ids",
        "continuity_reference_ids",
        "evidence_reference_ids",
        "requested_capabilities",
        "unsupported_markers",
        "prohibited_markers",
        "unknown_markers",
        "incomplete_markers",
        "blocked_markers",
        "governance_blockers",
        "boundary_policy_violation_ids",
        "integrity_precondition_failures",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_boundary_evidence(evidence: TransitionBoundaryEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evidence_reference_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_boundary_classification(
    classification: TransitionBoundaryClassification,
) -> dict[str, Any]:
    return asdict(classification)


def export_transition_boundary_finding(finding: TransitionBoundaryFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence"] = export_transition_boundary_evidence(finding.evidence)
    data["marker_ids"] = sorted_entries(data["marker_ids"])
    data["requested_capabilities"] = sorted_entries(data["requested_capabilities"])
    return data


def export_transition_boundary_report(report: TransitionBoundaryReport) -> dict[str, Any]:
    return {
        "boundary_report_id": report.boundary_report_id,
        "report_status": report.report_status,
        "source_foundation_id": report.source_foundation_id,
        "boundary_inputs": [
            export_transition_boundary_input(source)
            for source in sorted(report.boundary_inputs, key=lambda item: item.input_id)
        ],
        "classifications": [
            export_transition_boundary_classification(classification)
            for classification in sorted(
                report.classifications,
                key=lambda item: (_classification_order(item.classification), item.reason),
            )
        ],
        "findings": [
            export_transition_boundary_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "classification_counts": dict(sorted(report.classification_counts.items())),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_boundary_hash": report.deterministic_boundary_hash,
        "non_executable": report.non_executable,
        "transition_execution_enabled": report.transition_execution_enabled,
        "orchestration_execution_enabled": report.orchestration_execution_enabled,
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
        "state_machine_enabled": report.state_machine_enabled,
        "production_behavior_enabled": report.production_behavior_enabled,
        "hidden_fallback_enabled": report.hidden_fallback_enabled,
        "silent_correction_enabled": report.silent_correction_enabled,
    }


def _classification_order(classification: str) -> int:
    try:
        return BOUNDARY_CLASSIFICATIONS.index(classification)
    except ValueError:
        return len(BOUNDARY_CLASSIFICATIONS)
