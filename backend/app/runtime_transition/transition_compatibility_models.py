"""Deterministic v3.9 transition compatibility intelligence models.

These models reason about compatibility as immutable evidence only. They do
not execute orchestration, traverse graphs, route work, schedule work, dispatch
work, mutate runtime state, optimize, recommend, rank, score, select,
authorize, approve, or create callable orchestration flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_COMPATIBILITY_PHASE_ID = "v3_9_transition_compatibility_intelligence"
V3_9_TRANSITION_COMPATIBILITY_SCHEMA_VERSION = "v3_9.transition_compatibility_intelligence.1"
V3_9_TRANSITION_COMPATIBILITY_REPORT_STABLE = "v3_9_transition_compatibility_intelligence_stable"
V3_9_TRANSITION_COMPATIBILITY_REPORT_BLOCKED = "v3_9_transition_compatibility_intelligence_blocked"

COMPATIBILITY_CLASSIFICATION_COMPATIBLE = "compatible"
COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE = "incompatible"
COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE = "partially_compatible"
COMPATIBILITY_CLASSIFICATION_UNSUPPORTED = "unsupported"
COMPATIBILITY_CLASSIFICATION_PROHIBITED = "prohibited"
COMPATIBILITY_CLASSIFICATION_UNKNOWN = "unknown"
COMPATIBILITY_CLASSIFICATION_INCOMPLETE = "incomplete"
COMPATIBILITY_CLASSIFICATIONS: tuple[str, ...] = (
    COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
    COMPATIBILITY_CLASSIFICATION_PROHIBITED,
    COMPATIBILITY_CLASSIFICATION_UNKNOWN,
    COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
)
NON_COMPATIBLE_CLASSIFICATIONS: tuple[str, ...] = (
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
    COMPATIBILITY_CLASSIFICATION_PROHIBITED,
    COMPATIBILITY_CLASSIFICATION_UNKNOWN,
    COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
)

COMPATIBILITY_CONFLICT_PROVENANCE = "provenance_conflict"
COMPATIBILITY_CONFLICT_CONTINUITY = "continuity_conflict"
COMPATIBILITY_CONFLICT_BOUNDARY = "boundary_conflict"
COMPATIBILITY_CONFLICT_TRANSITION_STATE = "transition_state_conflict"
COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE = "unsupported_state_conflict"
COMPATIBILITY_CONFLICT_PROHIBITED_STATE = "prohibited_state_conflict"
COMPATIBILITY_CONFLICT_EXPLAINABILITY = "explainability_conflict"
COMPATIBILITY_CONFLICT_MISSING_EVIDENCE = "missing_evidence_conflict"
COMPATIBILITY_CONFLICT_TYPES: tuple[str, ...] = (
    COMPATIBILITY_CONFLICT_PROVENANCE,
    COMPATIBILITY_CONFLICT_CONTINUITY,
    COMPATIBILITY_CONFLICT_BOUNDARY,
    COMPATIBILITY_CONFLICT_TRANSITION_STATE,
    COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE,
    COMPATIBILITY_CONFLICT_PROHIBITED_STATE,
    COMPATIBILITY_CONFLICT_EXPLAINABILITY,
    COMPATIBILITY_CONFLICT_MISSING_EVIDENCE,
)

COMPATIBILITY_VISIBILITY_VISIBLE = "visible"
COMPATIBILITY_VISIBILITY_FAIL_VISIBLE = "fail_visible"
COMPATIBILITY_SEVERITY_INFO = "info"
COMPATIBILITY_SEVERITY_WARNING = "warning"
COMPATIBILITY_SEVERITY_BLOCKED = "blocked"

SUPPORTED_COMPATIBILITY_CAPABILITIES: tuple[str, ...] = (
    "deterministic_compatibility_reasoning",
    "transition_identity_reference",
    "transition_provenance_reference",
    "transition_continuity_reference",
    "transition_boundary_reference",
    "transition_evidence_reference",
)
PROHIBITED_COMPATIBILITY_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "orchestration_traversal",
    "transition_execution",
    "routing",
    "scheduling",
    "dispatch",
    "orchestration_engine",
    "runtime_mutation",
    "autonomous_behavior",
    "optimization",
    "recommendation",
    "ranking",
    "scoring",
    "selection",
    "approval",
    "authorization",
    "callable_orchestration_flow",
    "transition_handler",
    "orchestration_evaluator",
    "runtime_state_machine",
    "production_execution_pathway",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionCompatibilityInput:
    input_id: str
    source_transition_state_id: str
    destination_transition_state_id: str
    source_boundary_classification: str
    destination_boundary_classification: str
    source_transition_classification: str
    destination_transition_classification: str
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    compatibility_evidence_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    provenance_conflict_markers: tuple[str, ...] = ()
    continuity_conflict_markers: tuple[str, ...] = ()
    boundary_conflict_markers: tuple[str, ...] = ()
    transition_state_conflict_markers: tuple[str, ...] = ()
    unsupported_state_markers: tuple[str, ...] = ()
    prohibited_state_markers: tuple[str, ...] = ()
    explainability_conflict_markers: tuple[str, ...] = ()
    missing_evidence_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    partial_success_markers: tuple[str, ...] = ()
    partial_failure_markers: tuple[str, ...] = ()
    governance_requirement_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    non_executable_compatibility: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "compatibility_evidence_ids",
            "requested_capabilities",
            "provenance_conflict_markers",
            "continuity_conflict_markers",
            "boundary_conflict_markers",
            "transition_state_conflict_markers",
            "unsupported_state_markers",
            "prohibited_state_markers",
            "explainability_conflict_markers",
            "missing_evidence_markers",
            "unknown_markers",
            "incomplete_markers",
            "partial_success_markers",
            "partial_failure_markers",
            "governance_requirement_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionCompatibilityConflict:
    conflict_id: str
    input_id: str
    conflict_type: str
    conflict_marker: str
    severity: str
    visibility_status: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False


@dataclass(frozen=True)
class TransitionCompatibilityEvidence:
    evidence_id: str
    input_id: str
    source_transition_state_id: str
    destination_transition_state_id: str
    compatibility_evidence_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_compatibility_reasoning_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    execution_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "compatibility_evidence_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
            "conflict_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionCompatibilityFinding:
    finding_id: str
    input_id: str
    classification: str
    severity: str
    reason: str
    evidence: TransitionCompatibilityEvidence
    conflicts: tuple[TransitionCompatibilityConflict, ...]
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    compatible_state: bool = False
    execution_boundary_violation_detected: bool = False
    non_execution_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "conflicts", tuple(self.conflicts or ()))


@dataclass(frozen=True)
class TransitionCompatibilitySummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    conflict_counts: Mapping[str, int]
    compatible_count: int
    incompatible_count: int
    partially_compatible_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    incomplete_count: int
    compatibility_conflict_count: int
    provenance_conflict_count: int
    continuity_conflict_count: int
    boundary_conflict_count: int
    hidden_conflict_count: int
    execution_boundary_violation_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "conflict_counts", dict(sorted(self.conflict_counts.items())))


@dataclass(frozen=True)
class TransitionCompatibilityReport:
    report_id: str
    report_status: str
    source_foundation_id: str
    source_boundary_report_id: str
    compatibility_inputs: tuple[TransitionCompatibilityInput, ...]
    findings: tuple[TransitionCompatibilityFinding, ...]
    conflicts: tuple[TransitionCompatibilityConflict, ...]
    summary: TransitionCompatibilitySummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_compatibility_hash: str = ""
    non_executable: bool = True
    transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    orchestration_engine_enabled: bool = False
    runtime_mutation_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    callable_orchestration_flow_enabled: bool = False
    transition_handler_enabled: bool = False
    orchestration_evaluator_enabled: bool = False
    runtime_state_machine_enabled: bool = False
    production_execution_pathway_enabled: bool = False
    hidden_fallback_enabled: bool = False
    silent_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("compatibility_inputs", "findings", "conflicts"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_compatibility_finding_id(classification: str, input_id: str) -> str:
    return f"v3_9_transition_compatibility_{classification}_{input_id}"


def transition_compatibility_conflict_id(
    input_id: str,
    conflict_type: str,
    conflict_marker: str,
) -> str:
    marker = "".join(character if character.isalnum() else "_" for character in conflict_marker.lower())
    return f"v3_9_transition_compatibility_conflict_{input_id}_{conflict_type}_{marker}"


def export_transition_compatibility_input(source: TransitionCompatibilityInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "provenance_reference_ids",
        "continuity_reference_ids",
        "compatibility_evidence_ids",
        "requested_capabilities",
        "provenance_conflict_markers",
        "continuity_conflict_markers",
        "boundary_conflict_markers",
        "transition_state_conflict_markers",
        "unsupported_state_markers",
        "prohibited_state_markers",
        "explainability_conflict_markers",
        "missing_evidence_markers",
        "unknown_markers",
        "incomplete_markers",
        "partial_success_markers",
        "partial_failure_markers",
        "governance_requirement_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_compatibility_conflict(
    conflict: TransitionCompatibilityConflict,
) -> dict[str, Any]:
    return asdict(conflict)


def export_transition_compatibility_evidence(evidence: TransitionCompatibilityEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "compatibility_evidence_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
        "conflict_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_compatibility_finding(finding: TransitionCompatibilityFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence"] = export_transition_compatibility_evidence(finding.evidence)
    data["conflicts"] = [
        export_transition_compatibility_conflict(conflict)
        for conflict in sorted(
            finding.conflicts,
            key=lambda item: (item.deterministic_order, _conflict_order(item.conflict_type), item.conflict_id),
        )
    ]
    return data


def export_transition_compatibility_summary(summary: TransitionCompatibilitySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["conflict_counts"] = dict(sorted(summary.conflict_counts.items()))
    return data


def export_transition_compatibility_report(report: TransitionCompatibilityReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_foundation_id": report.source_foundation_id,
        "source_boundary_report_id": report.source_boundary_report_id,
        "compatibility_inputs": [
            export_transition_compatibility_input(source)
            for source in sorted(report.compatibility_inputs, key=lambda item: item.input_id)
        ],
        "findings": [
            export_transition_compatibility_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "conflicts": [
            export_transition_compatibility_conflict(conflict)
            for conflict in sorted(
                report.conflicts,
                key=lambda item: (item.deterministic_order, _conflict_order(item.conflict_type), item.conflict_id),
            )
        ],
        "summary": export_transition_compatibility_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_compatibility_hash": report.deterministic_compatibility_hash,
        "non_executable": report.non_executable,
        "transition_execution_enabled": report.transition_execution_enabled,
        "orchestration_execution_enabled": report.orchestration_execution_enabled,
        "orchestration_traversal_enabled": report.orchestration_traversal_enabled,
        "routing_enabled": report.routing_enabled,
        "scheduling_enabled": report.scheduling_enabled,
        "dispatch_enabled": report.dispatch_enabled,
        "orchestration_engine_enabled": report.orchestration_engine_enabled,
        "runtime_mutation_enabled": report.runtime_mutation_enabled,
        "autonomous_behavior_enabled": report.autonomous_behavior_enabled,
        "optimization_enabled": report.optimization_enabled,
        "recommendation_enabled": report.recommendation_enabled,
        "ranking_enabled": report.ranking_enabled,
        "scoring_enabled": report.scoring_enabled,
        "selection_enabled": report.selection_enabled,
        "approval_enabled": report.approval_enabled,
        "authorization_enabled": report.authorization_enabled,
        "callable_orchestration_flow_enabled": report.callable_orchestration_flow_enabled,
        "transition_handler_enabled": report.transition_handler_enabled,
        "orchestration_evaluator_enabled": report.orchestration_evaluator_enabled,
        "runtime_state_machine_enabled": report.runtime_state_machine_enabled,
        "production_execution_pathway_enabled": report.production_execution_pathway_enabled,
        "hidden_fallback_enabled": report.hidden_fallback_enabled,
        "silent_correction_enabled": report.silent_correction_enabled,
    }


def _classification_order(classification: str) -> int:
    try:
        return COMPATIBILITY_CLASSIFICATIONS.index(classification)
    except ValueError:
        return len(COMPATIBILITY_CLASSIFICATIONS)


def _conflict_order(conflict_type: str) -> int:
    try:
        return COMPATIBILITY_CONFLICT_TYPES.index(conflict_type)
    except ValueError:
        return len(COMPATIBILITY_CONFLICT_TYPES)
