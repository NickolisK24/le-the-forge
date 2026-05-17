"""Deterministic coordination scenario reasoning models for v3.8.

These models group hypothetical planning-only coordination alternatives into
immutable evidence records. They do not execute coordination, route work,
schedule work, dispatch work, traverse graphs, mutate runtime state, optimize,
recommend, authorize, rank executable choices, or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_SCENARIO_PHASE_ID = "v3_8_coordination_scenario_reasoning"
V3_8_COORDINATION_SCENARIO_SCHEMA_VERSION = "v3_8.coordination_scenario_reasoning.1"
V3_8_SCENARIO_AUDIT_STABLE = "v3_8_coordination_scenario_reasoning_stable"
V3_8_SCENARIO_AUDIT_BLOCKED = "v3_8_coordination_scenario_reasoning_blocked"

SCENARIO_STATE_MODELED = "modeled"
SCENARIO_STATE_UNMODELED = "unmodeled"
SCENARIO_STATE_BLOCKED = "blocked"
SCENARIO_STATE_UNSUPPORTED = "unsupported"
SCENARIO_STATE_PROHIBITED = "prohibited"
SCENARIO_STATE_UNKNOWN = "unknown"
SCENARIO_STATE_EXPERIMENTAL = "experimental"
SCENARIO_STATE_PLANNING_ONLY = "planning_only"
SCENARIO_STATE_NON_EXECUTABLE = "non_executable"
SCENARIO_STATES: tuple[str, ...] = (
    SCENARIO_STATE_MODELED,
    SCENARIO_STATE_UNMODELED,
    SCENARIO_STATE_BLOCKED,
    SCENARIO_STATE_UNSUPPORTED,
    SCENARIO_STATE_PROHIBITED,
    SCENARIO_STATE_UNKNOWN,
    SCENARIO_STATE_EXPERIMENTAL,
    SCENARIO_STATE_PLANNING_ONLY,
    SCENARIO_STATE_NON_EXECUTABLE,
)
NON_MODELED_SCENARIO_STATES: tuple[str, ...] = tuple(
    state for state in SCENARIO_STATES if state != SCENARIO_STATE_MODELED
)

SCENARIO_VISIBILITY_VISIBLE = "visible"
SCENARIO_VISIBILITY_FAIL_VISIBLE = "fail_visible"
SCENARIO_SEVERITY_INFO = "info"
SCENARIO_SEVERITY_WARNING = "warning"
SCENARIO_SEVERITY_BLOCKED = "blocked"

COMPARISON_ALLOWED_LANGUAGE: tuple[str, ...] = (
    "comparison",
    "difference",
    "delta",
    "visibility",
    "evidence",
    "hypothetical",
    "planning-only",
)
COMPARISON_RECOMMENDATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "best",
    "chosen",
    "choose",
    "choice",
    "recommendation",
    "recommended",
    "select",
    "selected",
)
COMPARISON_OPTIMIZATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "optimal",
    "optimize",
    "optimized",
    "optimization",
    "rank",
    "ranking",
    "score",
    "scoring",
)
COMPARISON_EXECUTION_LANGUAGE_TERMS: tuple[str, ...] = (
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
class V38CoordinationScenarioEvidence:
    evidence_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    provenance_reference: str
    replay_evidence_references: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    evidence_scope: str = "coordination_scenario_reasoning_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    boundary_context_preserved: bool = True
    compatibility_context_preserved: bool = True
    evaluation_context_preserved: bool = True
    session_context_preserved: bool = True
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
    non_executable: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "session_context_ids",
            "replay_evidence_references",
            "rollback_evidence_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationScenarioResult:
    scenario_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_state: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    evidence: V38CoordinationScenarioEvidence
    fail_visible: bool = True
    hidden: bool = False
    hidden_risk: bool = False
    experimental_label_explicit: bool = False
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    execution_behavior_detected: bool = False
    callable_execution_path_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_coordination_references",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "session_context_ids",
            "replay_safe_evidence",
            "rollback_safe_evidence",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationScenarioComparison:
    comparison_id: str
    compared_scenario_ids: tuple[str, ...]
    comparison_scope: str
    comparison_summary: str
    difference_summary: str
    visibility_status: str
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    provenance_references: tuple[str, ...]
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    non_execution_confirmation: bool
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    execution_behavior_detected: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "compared_scenario_ids",
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "session_context_ids",
            "provenance_references",
            "replay_safe_evidence",
            "rollback_safe_evidence",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationScenarioAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    source_boundary_audit_id: str
    source_compatibility_audit_id: str
    source_evaluation_audit_id: str
    source_session_audit_id: str
    scenario_results: tuple[V38CoordinationScenarioResult, ...]
    scenario_comparisons: tuple[V38CoordinationScenarioComparison, ...]
    state_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_scenario_hash: str = ""
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
    scoring_decision_system_enabled: bool = False
    execution_authorization_enabled: bool = False
    runtime_engine_enabled: bool = False
    state_machine_enabled: bool = False
    scenario_runtime_state_machine_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "scenario_results", tuple(self.scenario_results or ()))
        object.__setattr__(self, "scenario_comparisons", tuple(self.scenario_comparisons or ()))


def scenario_id(state: str, subject_id: str) -> str:
    return f"v3_8_scenario_{state}_{subject_id}"


def scenario_comparison_id(subject_id: str) -> str:
    return f"v3_8_scenario_comparison_{subject_id}"


def export_v3_8_scenario_evidence(evidence: V38CoordinationScenarioEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_coordination_references",
        "boundary_context_ids",
        "compatibility_context_ids",
        "evaluation_context_ids",
        "session_context_ids",
        "replay_evidence_references",
        "rollback_evidence_references",
        "deterministic_hash_references",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_8_scenario_result(result: V38CoordinationScenarioResult) -> dict[str, Any]:
    return {
        "scenario_id": result.scenario_id,
        "source_coordination_references": _sorted_entries(result.source_coordination_references),
        "boundary_context_ids": _sorted_entries(result.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(result.compatibility_context_ids),
        "evaluation_context_ids": _sorted_entries(result.evaluation_context_ids),
        "session_context_ids": _sorted_entries(result.session_context_ids),
        "scenario_state": result.scenario_state,
        "severity": result.severity,
        "explanation": result.explanation,
        "provenance_reference": result.provenance_reference,
        "replay_safe_evidence": _sorted_entries(result.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(result.rollback_safe_evidence),
        "deterministic_visibility_status": result.deterministic_visibility_status,
        "non_execution_confirmation": result.non_execution_confirmation,
        "evidence": export_v3_8_scenario_evidence(result.evidence),
        "fail_visible": result.fail_visible,
        "hidden": result.hidden,
        "hidden_risk": result.hidden_risk,
        "experimental_label_explicit": result.experimental_label_explicit,
        "immutable_evidence_record": result.immutable_evidence_record,
        "runtime_state_machine": result.runtime_state_machine,
        "recommendation_behavior_enabled": result.recommendation_behavior_enabled,
        "optimization_behavior_enabled": result.optimization_behavior_enabled,
        "scoring_behavior_enabled": result.scoring_behavior_enabled,
        "execution_behavior_detected": result.execution_behavior_detected,
        "callable_execution_path_enabled": result.callable_execution_path_enabled,
    }


def export_v3_8_scenario_comparison(
    comparison: V38CoordinationScenarioComparison,
) -> dict[str, Any]:
    return {
        "comparison_id": comparison.comparison_id,
        "compared_scenario_ids": _sorted_entries(comparison.compared_scenario_ids),
        "comparison_scope": comparison.comparison_scope,
        "comparison_summary": comparison.comparison_summary,
        "difference_summary": comparison.difference_summary,
        "visibility_status": comparison.visibility_status,
        "boundary_context_ids": _sorted_entries(comparison.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(comparison.compatibility_context_ids),
        "evaluation_context_ids": _sorted_entries(comparison.evaluation_context_ids),
        "session_context_ids": _sorted_entries(comparison.session_context_ids),
        "provenance_references": _sorted_entries(comparison.provenance_references),
        "replay_safe_evidence": _sorted_entries(comparison.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(comparison.rollback_safe_evidence),
        "non_execution_confirmation": comparison.non_execution_confirmation,
        "immutable_evidence_record": comparison.immutable_evidence_record,
        "runtime_state_machine": comparison.runtime_state_machine,
        "recommendation_behavior_enabled": comparison.recommendation_behavior_enabled,
        "optimization_behavior_enabled": comparison.optimization_behavior_enabled,
        "scoring_behavior_enabled": comparison.scoring_behavior_enabled,
        "execution_behavior_detected": comparison.execution_behavior_detected,
    }


def export_v3_8_scenario_audit(audit: V38CoordinationScenarioAudit) -> dict[str, Any]:
    return {
        "audit_id": audit.audit_id,
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "scenario_results": [
            export_v3_8_scenario_result(result)
            for result in sorted(
                audit.scenario_results,
                key=lambda item: (item.scenario_state, item.scenario_id),
            )
        ],
        "scenario_comparisons": [
            export_v3_8_scenario_comparison(comparison)
            for comparison in sorted(audit.scenario_comparisons, key=lambda item: item.comparison_id)
        ],
        "state_counts": dict(sorted(audit.state_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_scenario_hash": audit.deterministic_scenario_hash,
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
        "scoring_decision_system_enabled": audit.scoring_decision_system_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "scenario_runtime_state_machine_enabled": audit.scenario_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_scenario_audit(audit: V38CoordinationScenarioAudit) -> str:
    return stable_serialize(export_v3_8_scenario_audit(audit))


def hash_v3_8_scenario_audit(audit: V38CoordinationScenarioAudit) -> str:
    data = export_v3_8_scenario_audit(audit)
    data.pop("deterministic_scenario_hash", None)
    return deterministic_hash(data)


def validate_v3_8_scenario_serialization_stability(
    audit: V38CoordinationScenarioAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_scenario_audit(audit)
    second = serialize_v3_8_scenario_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_scenario_reasoning",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_scenario_hash_stability(
    audit: V38CoordinationScenarioAudit,
) -> dict[str, Any]:
    first = hash_v3_8_scenario_audit(audit)
    second = hash_v3_8_scenario_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_scenario_reasoning",
    }
