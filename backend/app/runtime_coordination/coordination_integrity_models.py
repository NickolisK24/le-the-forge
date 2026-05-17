"""Deterministic coordination integrity enforcement models for v3.8.

These models audit coordination evidence integrity as immutable audit records.
They do not execute coordination, enforce runtime behavior, route work,
schedule work, dispatch work, traverse graphs, mutate runtime state, optimize,
recommend, rank choices, score choices, select choices, authorize execution,
or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_INTEGRITY_PHASE_ID = "v3_8_coordination_integrity_enforcement"
V3_8_COORDINATION_INTEGRITY_SCHEMA_VERSION = "v3_8.coordination_integrity_enforcement.1"
V3_8_INTEGRITY_AUDIT_STABLE = "v3_8_coordination_integrity_enforcement_stable"
V3_8_INTEGRITY_AUDIT_BLOCKED = "v3_8_coordination_integrity_enforcement_blocked"

INTEGRITY_STATE_SATISFIED = "satisfied"
INTEGRITY_STATE_VIOLATED = "violated"
INTEGRITY_STATE_BLOCKED = "blocked"
INTEGRITY_STATE_UNSUPPORTED = "unsupported"
INTEGRITY_STATE_PROHIBITED = "prohibited"
INTEGRITY_STATE_UNKNOWN = "unknown"
INTEGRITY_STATE_EXPERIMENTAL = "experimental"
INTEGRITY_STATE_PLANNING_ONLY = "planning_only"
INTEGRITY_STATE_NON_EXECUTABLE = "non_executable"
INTEGRITY_STATES: tuple[str, ...] = (
    INTEGRITY_STATE_SATISFIED,
    INTEGRITY_STATE_VIOLATED,
    INTEGRITY_STATE_BLOCKED,
    INTEGRITY_STATE_UNSUPPORTED,
    INTEGRITY_STATE_PROHIBITED,
    INTEGRITY_STATE_UNKNOWN,
    INTEGRITY_STATE_EXPERIMENTAL,
    INTEGRITY_STATE_PLANNING_ONLY,
    INTEGRITY_STATE_NON_EXECUTABLE,
)
NON_SATISFIED_INTEGRITY_STATES: tuple[str, ...] = tuple(
    state for state in INTEGRITY_STATES if state != INTEGRITY_STATE_SATISFIED
)

INTEGRITY_VISIBILITY_VISIBLE = "visible"
INTEGRITY_VISIBILITY_FAIL_VISIBLE = "fail_visible"
INTEGRITY_SEVERITY_INFO = "info"
INTEGRITY_SEVERITY_WARNING = "warning"
INTEGRITY_SEVERITY_BLOCKED = "blocked"

INTEGRITY_RECOMMENDATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "best",
    "chosen",
    "choose",
    "choice",
    "recommendation",
    "recommended",
)
INTEGRITY_OPTIMIZATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "optimal",
    "optimize",
    "optimized",
    "optimization",
)
INTEGRITY_RANKING_LANGUAGE_TERMS: tuple[str, ...] = (
    "rank",
    "ranking",
)
INTEGRITY_SCORING_LANGUAGE_TERMS: tuple[str, ...] = (
    "score",
    "scoring",
)
INTEGRITY_SELECTION_LANGUAGE_TERMS: tuple[str, ...] = (
    "select",
    "selected",
    "selection",
)
INTEGRITY_EXECUTION_LANGUAGE_TERMS: tuple[str, ...] = (
    "dispatch",
    "execute",
    "route",
    "schedule",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class V38CoordinationIntegrityEvidence:
    evidence_id: str
    source_coordination_references: tuple[str, ...]
    foundation_context_ids: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_context_ids: tuple[str, ...]
    aggregation_context_ids: tuple[str, ...]
    provenance_reference: str
    replay_evidence_references: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    violation_codes: tuple[str, ...]
    evidence_scope: str = "coordination_integrity_enforcement_audit_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    foundation_context_preserved: bool = True
    boundary_context_preserved: bool = True
    compatibility_context_preserved: bool = True
    evaluation_context_preserved: bool = True
    session_context_preserved: bool = True
    scenario_context_preserved: bool = True
    aggregation_context_preserved: bool = True
    immutable_audit_evidence_record: bool = True
    runtime_enforcement_state_machine: bool = False
    non_executable: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "foundation_context_ids",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "session_context_ids",
            "scenario_context_ids",
            "aggregation_context_ids",
            "replay_evidence_references",
            "rollback_evidence_references",
            "deterministic_hash_references",
            "violation_codes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationIntegrityResult:
    integrity_id: str
    source_coordination_references: tuple[str, ...]
    foundation_context_ids: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_context_ids: tuple[str, ...]
    aggregation_context_ids: tuple[str, ...]
    integrity_state: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    evidence: V38CoordinationIntegrityEvidence
    violation_codes: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False
    hidden_risk: bool = False
    experimental_label_explicit: bool = False
    immutable_audit_evidence_record: bool = True
    runtime_enforcement_state_machine: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    ranking_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    selection_behavior_enabled: bool = False
    execution_behavior_detected: bool = False
    callable_execution_path_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "foundation_context_ids",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "session_context_ids",
            "scenario_context_ids",
            "aggregation_context_ids",
            "replay_safe_evidence",
            "rollback_safe_evidence",
            "violation_codes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationIntegrityAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    source_boundary_audit_id: str
    source_compatibility_audit_id: str
    source_evaluation_audit_id: str
    source_session_audit_id: str
    source_scenario_audit_id: str
    source_aggregation_audit_id: str
    integrity_results: tuple[V38CoordinationIntegrityResult, ...]
    state_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_integrity_hash: str = ""
    immutable_audit_evidence_records: bool = True
    non_executable: bool = True
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_enforcement_engine_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_execution_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    execution_authorization_enabled: bool = False
    runtime_engine_enabled: bool = False
    state_machine_enabled: bool = False
    integrity_runtime_state_machine_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "integrity_results", tuple(self.integrity_results or ()))


def integrity_id(state: str, subject_id: str) -> str:
    return f"v3_8_integrity_{state}_{subject_id}"


def export_v3_8_integrity_evidence(evidence: V38CoordinationIntegrityEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_coordination_references",
        "foundation_context_ids",
        "boundary_context_ids",
        "compatibility_context_ids",
        "evaluation_context_ids",
        "session_context_ids",
        "scenario_context_ids",
        "aggregation_context_ids",
        "replay_evidence_references",
        "rollback_evidence_references",
        "deterministic_hash_references",
        "violation_codes",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_8_integrity_result(result: V38CoordinationIntegrityResult) -> dict[str, Any]:
    return {
        "integrity_id": result.integrity_id,
        "source_coordination_references": _sorted_entries(result.source_coordination_references),
        "foundation_context_ids": _sorted_entries(result.foundation_context_ids),
        "boundary_context_ids": _sorted_entries(result.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(result.compatibility_context_ids),
        "evaluation_context_ids": _sorted_entries(result.evaluation_context_ids),
        "session_context_ids": _sorted_entries(result.session_context_ids),
        "scenario_context_ids": _sorted_entries(result.scenario_context_ids),
        "aggregation_context_ids": _sorted_entries(result.aggregation_context_ids),
        "integrity_state": result.integrity_state,
        "severity": result.severity,
        "explanation": result.explanation,
        "provenance_reference": result.provenance_reference,
        "replay_safe_evidence": _sorted_entries(result.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(result.rollback_safe_evidence),
        "deterministic_visibility_status": result.deterministic_visibility_status,
        "non_execution_confirmation": result.non_execution_confirmation,
        "evidence": export_v3_8_integrity_evidence(result.evidence),
        "violation_codes": _sorted_entries(result.violation_codes),
        "fail_visible": result.fail_visible,
        "hidden": result.hidden,
        "hidden_risk": result.hidden_risk,
        "experimental_label_explicit": result.experimental_label_explicit,
        "immutable_audit_evidence_record": result.immutable_audit_evidence_record,
        "runtime_enforcement_state_machine": result.runtime_enforcement_state_machine,
        "recommendation_behavior_enabled": result.recommendation_behavior_enabled,
        "optimization_behavior_enabled": result.optimization_behavior_enabled,
        "ranking_behavior_enabled": result.ranking_behavior_enabled,
        "scoring_behavior_enabled": result.scoring_behavior_enabled,
        "selection_behavior_enabled": result.selection_behavior_enabled,
        "execution_behavior_detected": result.execution_behavior_detected,
        "callable_execution_path_enabled": result.callable_execution_path_enabled,
    }


def export_v3_8_integrity_audit(audit: V38CoordinationIntegrityAudit) -> dict[str, Any]:
    return {
        "audit_id": audit.audit_id,
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "source_scenario_audit_id": audit.source_scenario_audit_id,
        "source_aggregation_audit_id": audit.source_aggregation_audit_id,
        "integrity_results": [
            export_v3_8_integrity_result(result)
            for result in sorted(
                audit.integrity_results,
                key=lambda item: (item.integrity_state, item.integrity_id),
            )
        ],
        "state_counts": dict(sorted(audit.state_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_integrity_hash": audit.deterministic_integrity_hash,
        "immutable_audit_evidence_records": audit.immutable_audit_evidence_records,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "runtime_enforcement_engine_enabled": audit.runtime_enforcement_engine_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "ranking_enabled": audit.ranking_enabled,
        "scoring_enabled": audit.scoring_enabled,
        "selection_enabled": audit.selection_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "integrity_runtime_state_machine_enabled": audit.integrity_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_integrity_audit(audit: V38CoordinationIntegrityAudit) -> str:
    return stable_serialize(export_v3_8_integrity_audit(audit))


def hash_v3_8_integrity_audit(audit: V38CoordinationIntegrityAudit) -> str:
    data = export_v3_8_integrity_audit(audit)
    data.pop("deterministic_integrity_hash", None)
    return deterministic_hash(data)


def validate_v3_8_integrity_serialization_stability(
    audit: V38CoordinationIntegrityAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_integrity_audit(audit)
    second = serialize_v3_8_integrity_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_integrity_enforcement",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_integrity_hash_stability(
    audit: V38CoordinationIntegrityAudit,
) -> dict[str, Any]:
    first = hash_v3_8_integrity_audit(audit)
    second = hash_v3_8_integrity_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_integrity_enforcement",
    }
