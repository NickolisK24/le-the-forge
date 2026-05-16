"""Deterministic coordination evaluation reasoning models for v3.8.

These models evaluate coordination evidence only. They do not execute
coordination, route work, schedule work, dispatch work, traverse graphs, mutate
runtime state, optimize, recommend, authorize, or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_EVALUATION_PHASE_ID = "v3_8_coordination_evaluation_reasoning"
V3_8_COORDINATION_EVALUATION_SCHEMA_VERSION = "v3_8.coordination_evaluation_reasoning.1"
V3_8_EVALUATION_AUDIT_STABLE = "v3_8_coordination_evaluation_reasoning_stable"
V3_8_EVALUATION_AUDIT_BLOCKED = "v3_8_coordination_evaluation_reasoning_blocked"

EVALUATION_STATE_VALID = "valid"
EVALUATION_STATE_INVALID = "invalid"
EVALUATION_STATE_BLOCKED = "blocked"
EVALUATION_STATE_UNSUPPORTED = "unsupported"
EVALUATION_STATE_PROHIBITED = "prohibited"
EVALUATION_STATE_UNKNOWN = "unknown"
EVALUATION_STATE_EXPERIMENTAL = "experimental"
EVALUATION_STATE_PLANNING_ONLY = "planning_only"
EVALUATION_STATE_NON_EXECUTABLE = "non_executable"
EVALUATION_STATES: tuple[str, ...] = (
    EVALUATION_STATE_VALID,
    EVALUATION_STATE_INVALID,
    EVALUATION_STATE_BLOCKED,
    EVALUATION_STATE_UNSUPPORTED,
    EVALUATION_STATE_PROHIBITED,
    EVALUATION_STATE_UNKNOWN,
    EVALUATION_STATE_EXPERIMENTAL,
    EVALUATION_STATE_PLANNING_ONLY,
    EVALUATION_STATE_NON_EXECUTABLE,
)
NON_VALID_EVALUATION_STATES: tuple[str, ...] = tuple(
    state for state in EVALUATION_STATES if state != EVALUATION_STATE_VALID
)

EVALUATION_VISIBILITY_VISIBLE = "visible"
EVALUATION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
EVALUATION_SEVERITY_INFO = "info"
EVALUATION_SEVERITY_WARNING = "warning"
EVALUATION_SEVERITY_BLOCKED = "blocked"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class V38CoordinationEvaluationEvidence:
    evidence_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    provenance_reference: str
    replay_evidence_references: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    evidence_scope: str = "coordination_evaluation_reasoning_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    boundary_context_preserved: bool = True
    compatibility_context_preserved: bool = True
    non_executable: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "boundary_context_ids",
            "compatibility_context_ids",
            "replay_evidence_references",
            "rollback_evidence_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationEvaluationResult:
    evaluation_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_state: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    evidence: V38CoordinationEvaluationEvidence
    fail_visible: bool = True
    hidden: bool = False
    hidden_risk: bool = False
    experimental_label_explicit: bool = False
    execution_behavior_detected: bool = False
    callable_execution_path_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "boundary_context_ids",
            "compatibility_context_ids",
            "replay_safe_evidence",
            "rollback_safe_evidence",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationEvaluationAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    source_boundary_audit_id: str
    source_compatibility_audit_id: str
    evaluation_results: tuple[V38CoordinationEvaluationResult, ...]
    state_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_evaluation_hash: str = ""
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
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "evaluation_results", tuple(self.evaluation_results or ()))


def evaluation_id(state: str, subject_id: str) -> str:
    return f"v3_8_evaluation_{state}_{subject_id}"


def export_v3_8_evaluation_evidence(evidence: V38CoordinationEvaluationEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_coordination_references",
        "boundary_context_ids",
        "compatibility_context_ids",
        "replay_evidence_references",
        "rollback_evidence_references",
        "deterministic_hash_references",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_8_evaluation_result(result: V38CoordinationEvaluationResult) -> dict[str, Any]:
    return {
        "evaluation_id": result.evaluation_id,
        "source_coordination_references": _sorted_entries(result.source_coordination_references),
        "boundary_context_ids": _sorted_entries(result.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(result.compatibility_context_ids),
        "evaluation_state": result.evaluation_state,
        "severity": result.severity,
        "explanation": result.explanation,
        "provenance_reference": result.provenance_reference,
        "replay_safe_evidence": _sorted_entries(result.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(result.rollback_safe_evidence),
        "deterministic_visibility_status": result.deterministic_visibility_status,
        "non_execution_confirmation": result.non_execution_confirmation,
        "evidence": export_v3_8_evaluation_evidence(result.evidence),
        "fail_visible": result.fail_visible,
        "hidden": result.hidden,
        "hidden_risk": result.hidden_risk,
        "experimental_label_explicit": result.experimental_label_explicit,
        "execution_behavior_detected": result.execution_behavior_detected,
        "callable_execution_path_enabled": result.callable_execution_path_enabled,
    }


def export_v3_8_evaluation_audit(audit: V38CoordinationEvaluationAudit) -> dict[str, Any]:
    return {
        "audit_id": audit.audit_id,
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "evaluation_results": [
            export_v3_8_evaluation_result(result)
            for result in sorted(
                audit.evaluation_results,
                key=lambda item: (item.evaluation_state, item.evaluation_id),
            )
        ],
        "state_counts": dict(sorted(audit.state_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_evaluation_hash": audit.deterministic_evaluation_hash,
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
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_evaluation_audit(audit: V38CoordinationEvaluationAudit) -> str:
    return stable_serialize(export_v3_8_evaluation_audit(audit))


def hash_v3_8_evaluation_audit(audit: V38CoordinationEvaluationAudit) -> str:
    data = export_v3_8_evaluation_audit(audit)
    data.pop("deterministic_evaluation_hash", None)
    return deterministic_hash(data)


def validate_v3_8_evaluation_serialization_stability(
    audit: V38CoordinationEvaluationAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_evaluation_audit(audit)
    second = serialize_v3_8_evaluation_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_evaluation_reasoning",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_evaluation_hash_stability(
    audit: V38CoordinationEvaluationAudit,
) -> dict[str, Any]:
    first = hash_v3_8_evaluation_audit(audit)
    second = hash_v3_8_evaluation_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_evaluation_reasoning",
    }
