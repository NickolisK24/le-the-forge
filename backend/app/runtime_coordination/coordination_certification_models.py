"""Deterministic coordination continuity certification models for v3.8.

These models certify coordination continuity as immutable evidence records.
They do not execute coordination, enforce runtime behavior, route work,
schedule work, dispatch work, traverse graphs, mutate runtime state, optimize,
recommend, rank choices, score choices, select choices, authorize execution,
or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_CERTIFICATION_PHASE_ID = "v3_8_coordination_continuity_certification"
V3_8_COORDINATION_CERTIFICATION_SCHEMA_VERSION = "v3_8.coordination_continuity_certification.1"
V3_8_CERTIFICATION_AUDIT_STABLE = "v3_8_coordination_continuity_certification_stable"
V3_8_CERTIFICATION_AUDIT_BLOCKED = "v3_8_coordination_continuity_certification_blocked"

CERTIFICATION_STATE_CERTIFIED = "certified"
CERTIFICATION_STATE_UNCERTIFIED = "uncertified"
CERTIFICATION_STATE_BLOCKED = "blocked"
CERTIFICATION_STATE_UNSUPPORTED = "unsupported"
CERTIFICATION_STATE_PROHIBITED = "prohibited"
CERTIFICATION_STATE_UNKNOWN = "unknown"
CERTIFICATION_STATE_EXPERIMENTAL = "experimental"
CERTIFICATION_STATE_PLANNING_ONLY = "planning_only"
CERTIFICATION_STATE_NON_EXECUTABLE = "non_executable"
CERTIFICATION_STATES: tuple[str, ...] = (
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_BLOCKED,
    CERTIFICATION_STATE_UNSUPPORTED,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_UNKNOWN,
    CERTIFICATION_STATE_EXPERIMENTAL,
    CERTIFICATION_STATE_PLANNING_ONLY,
    CERTIFICATION_STATE_NON_EXECUTABLE,
)
NON_CERTIFIED_STATES: tuple[str, ...] = tuple(
    state for state in CERTIFICATION_STATES if state != CERTIFICATION_STATE_CERTIFIED
)

CERTIFICATION_VISIBILITY_VISIBLE = "visible"
CERTIFICATION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
CERTIFICATION_SEVERITY_INFO = "info"
CERTIFICATION_SEVERITY_WARNING = "warning"
CERTIFICATION_SEVERITY_BLOCKED = "blocked"

CERTIFICATION_RECOMMENDATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "best",
    "chosen",
    "choose",
    "choice",
    "recommendation",
    "recommended",
)
CERTIFICATION_OPTIMIZATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "optimal",
    "optimize",
    "optimized",
    "optimization",
)
CERTIFICATION_RANKING_LANGUAGE_TERMS: tuple[str, ...] = (
    "rank",
    "ranking",
)
CERTIFICATION_SCORING_LANGUAGE_TERMS: tuple[str, ...] = (
    "score",
    "scoring",
)
CERTIFICATION_SELECTION_LANGUAGE_TERMS: tuple[str, ...] = (
    "select",
    "selected",
    "selection",
)
CERTIFICATION_EXECUTION_LANGUAGE_TERMS: tuple[str, ...] = (
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
class V38CoordinationCertificationEvidence:
    evidence_id: str
    source_coordination_references: tuple[str, ...]
    foundation_context_ids: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_context_ids: tuple[str, ...]
    aggregation_context_ids: tuple[str, ...]
    integrity_context_ids: tuple[str, ...]
    provenance_reference: str
    replay_evidence_references: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    certification_failure_codes: tuple[str, ...]
    evidence_scope: str = "coordination_continuity_certification_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_certified: bool = True
    foundation_continuity_certified: bool = True
    boundary_continuity_certified: bool = True
    compatibility_continuity_certified: bool = True
    evaluation_continuity_certified: bool = True
    session_continuity_certified: bool = True
    scenario_continuity_certified: bool = True
    aggregation_continuity_certified: bool = True
    integrity_continuity_certified: bool = True
    explainability_continuity_certified: bool = True
    non_execution_continuity_certified: bool = True
    fail_visible_state_continuity_certified: bool = True
    immutable_certification_evidence_record: bool = True
    runtime_certification_state_machine: bool = False
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
            "integrity_context_ids",
            "replay_evidence_references",
            "rollback_evidence_references",
            "deterministic_hash_references",
            "certification_failure_codes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationCertificationResult:
    certification_id: str
    source_coordination_references: tuple[str, ...]
    foundation_context_ids: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_context_ids: tuple[str, ...]
    aggregation_context_ids: tuple[str, ...]
    integrity_context_ids: tuple[str, ...]
    certification_state: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    evidence: V38CoordinationCertificationEvidence
    certification_failure_codes: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False
    hidden_risk: bool = False
    experimental_label_explicit: bool = False
    immutable_certification_evidence_record: bool = True
    runtime_certification_state_machine: bool = False
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
            "integrity_context_ids",
            "replay_safe_evidence",
            "rollback_safe_evidence",
            "certification_failure_codes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationCertificationAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    source_boundary_audit_id: str
    source_compatibility_audit_id: str
    source_evaluation_audit_id: str
    source_session_audit_id: str
    source_scenario_audit_id: str
    source_aggregation_audit_id: str
    source_integrity_audit_id: str
    certification_results: tuple[V38CoordinationCertificationResult, ...]
    state_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_certification_hash: str = ""
    immutable_certification_evidence_records: bool = True
    non_executable: bool = True
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_certification_engine_enabled: bool = False
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
    certification_runtime_state_machine_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "certification_results", tuple(self.certification_results or ()))


def certification_id(state: str, subject_id: str) -> str:
    return f"v3_8_certification_{state}_{subject_id}"


def export_v3_8_certification_evidence(
    evidence: V38CoordinationCertificationEvidence,
) -> dict[str, Any]:
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
        "integrity_context_ids",
        "replay_evidence_references",
        "rollback_evidence_references",
        "deterministic_hash_references",
        "certification_failure_codes",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_8_certification_result(
    result: V38CoordinationCertificationResult,
) -> dict[str, Any]:
    return {
        "certification_id": result.certification_id,
        "source_coordination_references": _sorted_entries(result.source_coordination_references),
        "foundation_context_ids": _sorted_entries(result.foundation_context_ids),
        "boundary_context_ids": _sorted_entries(result.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(result.compatibility_context_ids),
        "evaluation_context_ids": _sorted_entries(result.evaluation_context_ids),
        "session_context_ids": _sorted_entries(result.session_context_ids),
        "scenario_context_ids": _sorted_entries(result.scenario_context_ids),
        "aggregation_context_ids": _sorted_entries(result.aggregation_context_ids),
        "integrity_context_ids": _sorted_entries(result.integrity_context_ids),
        "certification_state": result.certification_state,
        "severity": result.severity,
        "explanation": result.explanation,
        "provenance_reference": result.provenance_reference,
        "replay_safe_evidence": _sorted_entries(result.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(result.rollback_safe_evidence),
        "deterministic_visibility_status": result.deterministic_visibility_status,
        "non_execution_confirmation": result.non_execution_confirmation,
        "evidence": export_v3_8_certification_evidence(result.evidence),
        "certification_failure_codes": _sorted_entries(result.certification_failure_codes),
        "fail_visible": result.fail_visible,
        "hidden": result.hidden,
        "hidden_risk": result.hidden_risk,
        "experimental_label_explicit": result.experimental_label_explicit,
        "immutable_certification_evidence_record": result.immutable_certification_evidence_record,
        "runtime_certification_state_machine": result.runtime_certification_state_machine,
        "recommendation_behavior_enabled": result.recommendation_behavior_enabled,
        "optimization_behavior_enabled": result.optimization_behavior_enabled,
        "ranking_behavior_enabled": result.ranking_behavior_enabled,
        "scoring_behavior_enabled": result.scoring_behavior_enabled,
        "selection_behavior_enabled": result.selection_behavior_enabled,
        "execution_behavior_detected": result.execution_behavior_detected,
        "callable_execution_path_enabled": result.callable_execution_path_enabled,
    }


def export_v3_8_certification_audit(audit: V38CoordinationCertificationAudit) -> dict[str, Any]:
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
        "source_integrity_audit_id": audit.source_integrity_audit_id,
        "certification_results": [
            export_v3_8_certification_result(result)
            for result in sorted(
                audit.certification_results,
                key=lambda item: (item.certification_state, item.certification_id),
            )
        ],
        "state_counts": dict(sorted(audit.state_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_certification_hash": audit.deterministic_certification_hash,
        "immutable_certification_evidence_records": audit.immutable_certification_evidence_records,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "runtime_certification_engine_enabled": audit.runtime_certification_engine_enabled,
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
        "certification_runtime_state_machine_enabled": audit.certification_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_certification_audit(audit: V38CoordinationCertificationAudit) -> str:
    return stable_serialize(export_v3_8_certification_audit(audit))


def hash_v3_8_certification_audit(audit: V38CoordinationCertificationAudit) -> str:
    data = export_v3_8_certification_audit(audit)
    data.pop("deterministic_certification_hash", None)
    return deterministic_hash(data)


def validate_v3_8_certification_serialization_stability(
    audit: V38CoordinationCertificationAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_certification_audit(audit)
    second = serialize_v3_8_certification_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_continuity_certification",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_certification_hash_stability(
    audit: V38CoordinationCertificationAudit,
) -> dict[str, Any]:
    first = hash_v3_8_certification_audit(audit)
    second = hash_v3_8_certification_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_continuity_certification",
    }
