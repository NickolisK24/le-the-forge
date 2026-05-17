"""Deterministic v3.9 transition session intelligence models.

These models package transition evaluations as immutable session evidence. They
do not execute transitions, authorize transitions, traverse graphs, route,
schedule, dispatch, mutate runtime state, optimize, recommend, rank, score,
select, approve, or create callable orchestration flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_SESSION_PHASE_ID = "v3_9_transition_session_intelligence"
V3_9_TRANSITION_SESSION_SCHEMA_VERSION = "v3_9.transition_session_intelligence.1"
V3_9_TRANSITION_SESSION_REPORT_STABLE = "v3_9_transition_session_intelligence_stable"
V3_9_TRANSITION_SESSION_REPORT_BLOCKED = "v3_9_transition_session_intelligence_blocked"

SESSION_CLASSIFICATION_COMPLETE = "complete"
SESSION_CLASSIFICATION_PARTIALLY_COMPLETE = "partially_complete"
SESSION_CLASSIFICATION_INCOMPLETE = "incomplete"
SESSION_CLASSIFICATION_BLOCKED = "blocked"
SESSION_CLASSIFICATION_UNSUPPORTED = "unsupported"
SESSION_CLASSIFICATION_PROHIBITED = "prohibited"
SESSION_CLASSIFICATION_UNKNOWN = "unknown"
SESSION_CLASSIFICATIONS: tuple[str, ...] = (
    SESSION_CLASSIFICATION_COMPLETE,
    SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
    SESSION_CLASSIFICATION_INCOMPLETE,
    SESSION_CLASSIFICATION_BLOCKED,
    SESSION_CLASSIFICATION_UNSUPPORTED,
    SESSION_CLASSIFICATION_PROHIBITED,
    SESSION_CLASSIFICATION_UNKNOWN,
)
NON_COMPLETE_SESSION_CLASSIFICATIONS: tuple[str, ...] = (
    SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
    SESSION_CLASSIFICATION_INCOMPLETE,
    SESSION_CLASSIFICATION_BLOCKED,
    SESSION_CLASSIFICATION_UNSUPPORTED,
    SESSION_CLASSIFICATION_PROHIBITED,
    SESSION_CLASSIFICATION_UNKNOWN,
)

SESSION_FINDING_EVALUATION = "evaluation"
SESSION_FINDING_CONTINUITY = "continuity"
SESSION_FINDING_PROVENANCE = "provenance"
SESSION_FINDING_EXPLAINABILITY = "explainability"
SESSION_FINDING_GOVERNANCE = "governance"
SESSION_FINDING_INTEGRITY = "integrity"
SESSION_FINDING_UNSUPPORTED = "unsupported"
SESSION_FINDING_PROHIBITED = "prohibited"
SESSION_FINDING_MISSING_EVIDENCE = "missing_evidence"
SESSION_FINDING_UNCERTAINTY = "uncertainty"
SESSION_FINDING_COMPLETENESS = "session_completeness"
SESSION_FINDING_CATEGORIES: tuple[str, ...] = (
    SESSION_FINDING_EVALUATION,
    SESSION_FINDING_CONTINUITY,
    SESSION_FINDING_PROVENANCE,
    SESSION_FINDING_EXPLAINABILITY,
    SESSION_FINDING_GOVERNANCE,
    SESSION_FINDING_INTEGRITY,
    SESSION_FINDING_UNSUPPORTED,
    SESSION_FINDING_PROHIBITED,
    SESSION_FINDING_MISSING_EVIDENCE,
    SESSION_FINDING_UNCERTAINTY,
    SESSION_FINDING_COMPLETENESS,
)

SESSION_VISIBILITY_VISIBLE = "visible"
SESSION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
SESSION_SEVERITY_INFO = "info"
SESSION_SEVERITY_WARNING = "warning"
SESSION_SEVERITY_BLOCKED = "blocked"

SUPPORTED_SESSION_CAPABILITIES: tuple[str, ...] = (
    "deterministic_transition_session_recording",
    "transition_evaluation_reference",
    "transition_provenance_reference",
    "transition_continuity_reference",
    "transition_evidence_reference",
    "transition_explainability_reference",
)
PROHIBITED_SESSION_CAPABILITIES: tuple[str, ...] = (
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


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionSessionInput:
    input_id: str
    session_id: str
    session_domain: str
    evaluation_record_ids: tuple[str, ...]
    complete_evaluation_record_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    session_evidence_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    partial_success_markers: tuple[str, ...] = ()
    partial_failure_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    governance_policy_ids: tuple[str, ...] = ()
    integrity_policy_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    non_executable_session: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_record_ids",
            "complete_evaluation_record_ids",
            "provenance_reference_ids",
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "session_evidence_ids",
            "requested_capabilities",
            "partial_success_markers",
            "partial_failure_markers",
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
class TransitionSessionEntry:
    entry_id: str
    input_id: str
    evaluation_record_id: str
    entry_status: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    immutable_entry: bool = True
    hidden: bool = False


@dataclass(frozen=True)
class TransitionSessionContinuity:
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
class TransitionSessionFinding:
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
    non_execution_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True


@dataclass(frozen=True)
class TransitionSessionEvidence:
    evidence_id: str
    input_id: str
    session_id: str
    session_evidence_ids: tuple[str, ...]
    evaluation_entry_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_session_evidence_record_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    execution_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "session_evidence_ids",
            "evaluation_entry_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
            "finding_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionSessionVisibility:
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
    session_state_visible: bool = True


@dataclass(frozen=True)
class TransitionSessionRecord:
    record_id: str
    input_id: str
    session_id: str
    classification: str
    entries: tuple[TransitionSessionEntry, ...]
    evidence: TransitionSessionEvidence
    continuity: TransitionSessionContinuity
    visibility: TransitionSessionVisibility
    deterministic_order: int
    immutable_record: bool = True
    non_executable: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", tuple(self.entries or ()))


@dataclass(frozen=True)
class TransitionSessionSummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    finding_category_counts: Mapping[str, int]
    complete_count: int
    partially_complete_count: int
    incomplete_count: int
    blocked_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    session_finding_count: int
    evaluation_entry_count: int
    governance_finding_count: int
    uncertainty_finding_count: int
    missing_evidence_finding_count: int
    hidden_session_finding_count: int
    execution_boundary_violation_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "finding_category_counts", dict(sorted(self.finding_category_counts.items())))


@dataclass(frozen=True)
class TransitionSessionReport:
    report_id: str
    report_status: str
    source_foundation_id: str
    source_boundary_report_id: str
    source_compatibility_report_id: str
    source_evaluation_report_id: str
    session_inputs: tuple[TransitionSessionInput, ...]
    session_records: tuple[TransitionSessionRecord, ...]
    entries: tuple[TransitionSessionEntry, ...]
    findings: tuple[TransitionSessionFinding, ...]
    evidence_records: tuple[TransitionSessionEvidence, ...]
    continuities: tuple[TransitionSessionContinuity, ...]
    visibilities: tuple[TransitionSessionVisibility, ...]
    summary: TransitionSessionSummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_session_hash: str = ""
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

    def __post_init__(self) -> None:
        for field_name in (
            "session_inputs",
            "session_records",
            "entries",
            "findings",
            "evidence_records",
            "continuities",
            "visibilities",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_session_finding_id(input_id: str, finding_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_session_{input_id}_{finding_category}_{safe_marker}"


def export_transition_session_input(source: TransitionSessionInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "evaluation_record_ids",
        "complete_evaluation_record_ids",
        "provenance_reference_ids",
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "session_evidence_ids",
        "requested_capabilities",
        "partial_success_markers",
        "partial_failure_markers",
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


def export_transition_session_entry(entry: TransitionSessionEntry) -> dict[str, Any]:
    return asdict(entry)


def export_transition_session_continuity(continuity: TransitionSessionContinuity) -> dict[str, Any]:
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


def export_transition_session_finding(finding: TransitionSessionFinding) -> dict[str, Any]:
    return asdict(finding)


def export_transition_session_evidence(evidence: TransitionSessionEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "session_evidence_ids",
        "evaluation_entry_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
        "finding_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_session_visibility(visibility: TransitionSessionVisibility) -> dict[str, Any]:
    return asdict(visibility)


def export_transition_session_record(record: TransitionSessionRecord) -> dict[str, Any]:
    return {
        "record_id": record.record_id,
        "input_id": record.input_id,
        "session_id": record.session_id,
        "classification": record.classification,
        "entries": [
            export_transition_session_entry(entry)
            for entry in sorted(record.entries, key=lambda item: (item.deterministic_order, item.entry_id))
        ],
        "evidence": export_transition_session_evidence(record.evidence),
        "continuity": export_transition_session_continuity(record.continuity),
        "visibility": export_transition_session_visibility(record.visibility),
        "deterministic_order": record.deterministic_order,
        "immutable_record": record.immutable_record,
        "non_executable": record.non_executable,
    }


def export_transition_session_summary(summary: TransitionSessionSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["finding_category_counts"] = dict(sorted(summary.finding_category_counts.items()))
    return data


def export_transition_session_report(report: TransitionSessionReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_foundation_id": report.source_foundation_id,
        "source_boundary_report_id": report.source_boundary_report_id,
        "source_compatibility_report_id": report.source_compatibility_report_id,
        "source_evaluation_report_id": report.source_evaluation_report_id,
        "session_inputs": [
            export_transition_session_input(source)
            for source in sorted(report.session_inputs, key=lambda item: item.input_id)
        ],
        "session_records": [
            export_transition_session_record(record)
            for record in sorted(report.session_records, key=lambda item: (item.deterministic_order, item.record_id))
        ],
        "entries": [
            export_transition_session_entry(entry)
            for entry in sorted(report.entries, key=lambda item: (item.deterministic_order, item.entry_id))
        ],
        "findings": [
            export_transition_session_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "evidence_records": [
            export_transition_session_evidence(evidence)
            for evidence in sorted(report.evidence_records, key=lambda item: item.evidence_id)
        ],
        "continuities": [
            export_transition_session_continuity(continuity)
            for continuity in sorted(report.continuities, key=lambda item: item.continuity_id)
        ],
        "visibilities": [
            export_transition_session_visibility(visibility)
            for visibility in sorted(report.visibilities, key=lambda item: item.visibility_id)
        ],
        "summary": export_transition_session_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_session_hash": report.deterministic_session_hash,
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
    }
