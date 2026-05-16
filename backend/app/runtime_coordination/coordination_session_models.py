"""Deterministic coordination session reasoning models for v3.8.

These models group coordination evidence into immutable planning session records
only. They do not execute coordination, route work, schedule work, dispatch
work, traverse graphs, mutate runtime state, optimize, recommend, authorize, or
create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_SESSION_PHASE_ID = "v3_8_coordination_session_reasoning"
V3_8_COORDINATION_SESSION_SCHEMA_VERSION = "v3_8.coordination_session_reasoning.1"
V3_8_SESSION_AUDIT_STABLE = "v3_8_coordination_session_reasoning_stable"
V3_8_SESSION_AUDIT_BLOCKED = "v3_8_coordination_session_reasoning_blocked"

SESSION_STATE_COMPLETE = "complete"
SESSION_STATE_INCOMPLETE = "incomplete"
SESSION_STATE_BLOCKED = "blocked"
SESSION_STATE_UNSUPPORTED = "unsupported"
SESSION_STATE_PROHIBITED = "prohibited"
SESSION_STATE_UNKNOWN = "unknown"
SESSION_STATE_EXPERIMENTAL = "experimental"
SESSION_STATE_PLANNING_ONLY = "planning_only"
SESSION_STATE_NON_EXECUTABLE = "non_executable"
SESSION_STATES: tuple[str, ...] = (
    SESSION_STATE_COMPLETE,
    SESSION_STATE_INCOMPLETE,
    SESSION_STATE_BLOCKED,
    SESSION_STATE_UNSUPPORTED,
    SESSION_STATE_PROHIBITED,
    SESSION_STATE_UNKNOWN,
    SESSION_STATE_EXPERIMENTAL,
    SESSION_STATE_PLANNING_ONLY,
    SESSION_STATE_NON_EXECUTABLE,
)
NON_COMPLETE_SESSION_STATES: tuple[str, ...] = tuple(
    state for state in SESSION_STATES if state != SESSION_STATE_COMPLETE
)

SESSION_VISIBILITY_VISIBLE = "visible"
SESSION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
SESSION_SEVERITY_INFO = "info"
SESSION_SEVERITY_WARNING = "warning"
SESSION_SEVERITY_BLOCKED = "blocked"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class V38CoordinationSessionEvidence:
    evidence_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    provenance_reference: str
    replay_evidence_references: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    evidence_scope: str = "coordination_session_reasoning_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    boundary_context_preserved: bool = True
    compatibility_context_preserved: bool = True
    evaluation_context_preserved: bool = True
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
    non_executable: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "replay_evidence_references",
            "rollback_evidence_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationSessionResult:
    session_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_state: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    evidence: V38CoordinationSessionEvidence
    fail_visible: bool = True
    hidden: bool = False
    hidden_risk: bool = False
    experimental_label_explicit: bool = False
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
    execution_behavior_detected: bool = False
    callable_execution_path_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "replay_safe_evidence",
            "rollback_safe_evidence",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationSessionAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    source_boundary_audit_id: str
    source_compatibility_audit_id: str
    source_evaluation_audit_id: str
    session_results: tuple[V38CoordinationSessionResult, ...]
    state_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_session_hash: str = ""
    immutable_evidence_records: bool = True
    non_executable: bool = True
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_execution_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    execution_authorization_enabled: bool = False
    runtime_engine_enabled: bool = False
    state_machine_enabled: bool = False
    session_runtime_state_machine_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_results", tuple(self.session_results or ()))


def session_id(state: str, subject_id: str) -> str:
    return f"v3_8_session_{state}_{subject_id}"


def export_v3_8_session_evidence(evidence: V38CoordinationSessionEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_coordination_references",
        "boundary_context_ids",
        "compatibility_context_ids",
        "evaluation_context_ids",
        "replay_evidence_references",
        "rollback_evidence_references",
        "deterministic_hash_references",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_8_session_result(result: V38CoordinationSessionResult) -> dict[str, Any]:
    return {
        "session_id": result.session_id,
        "source_coordination_references": _sorted_entries(result.source_coordination_references),
        "boundary_context_ids": _sorted_entries(result.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(result.compatibility_context_ids),
        "evaluation_context_ids": _sorted_entries(result.evaluation_context_ids),
        "session_state": result.session_state,
        "severity": result.severity,
        "explanation": result.explanation,
        "provenance_reference": result.provenance_reference,
        "replay_safe_evidence": _sorted_entries(result.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(result.rollback_safe_evidence),
        "deterministic_visibility_status": result.deterministic_visibility_status,
        "non_execution_confirmation": result.non_execution_confirmation,
        "evidence": export_v3_8_session_evidence(result.evidence),
        "fail_visible": result.fail_visible,
        "hidden": result.hidden,
        "hidden_risk": result.hidden_risk,
        "experimental_label_explicit": result.experimental_label_explicit,
        "immutable_evidence_record": result.immutable_evidence_record,
        "runtime_state_machine": result.runtime_state_machine,
        "execution_behavior_detected": result.execution_behavior_detected,
        "callable_execution_path_enabled": result.callable_execution_path_enabled,
    }


def export_v3_8_session_audit(audit: V38CoordinationSessionAudit) -> dict[str, Any]:
    return {
        "audit_id": audit.audit_id,
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "session_results": [
            export_v3_8_session_result(result)
            for result in sorted(
                audit.session_results,
                key=lambda item: (item.session_state, item.session_id),
            )
        ],
        "state_counts": dict(sorted(audit.state_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_session_hash": audit.deterministic_session_hash,
        "immutable_evidence_records": audit.immutable_evidence_records,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "session_runtime_state_machine_enabled": audit.session_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_session_audit(audit: V38CoordinationSessionAudit) -> str:
    return stable_serialize(export_v3_8_session_audit(audit))


def hash_v3_8_session_audit(audit: V38CoordinationSessionAudit) -> str:
    data = export_v3_8_session_audit(audit)
    data.pop("deterministic_session_hash", None)
    return deterministic_hash(data)


def validate_v3_8_session_serialization_stability(
    audit: V38CoordinationSessionAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_session_audit(audit)
    second = serialize_v3_8_session_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_session_reasoning",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_session_hash_stability(
    audit: V38CoordinationSessionAudit,
) -> dict[str, Any]:
    first = hash_v3_8_session_audit(audit)
    second = hash_v3_8_session_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_session_reasoning",
    }
