"""Deterministic coordination intelligence aggregation models for v3.8.

These models aggregate coordination evidence into immutable planning-only
summary records. They do not execute coordination, route work, schedule work,
dispatch work, traverse graphs, mutate runtime state, optimize, recommend,
authorize, rank choices, score choices, select choices, or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_AGGREGATION_PHASE_ID = "v3_8_coordination_intelligence_aggregation"
V3_8_COORDINATION_AGGREGATION_SCHEMA_VERSION = "v3_8.coordination_intelligence_aggregation.1"
V3_8_AGGREGATION_AUDIT_STABLE = "v3_8_coordination_intelligence_aggregation_stable"
V3_8_AGGREGATION_AUDIT_BLOCKED = "v3_8_coordination_intelligence_aggregation_blocked"

AGGREGATION_STATE_AGGREGATED = "aggregated"
AGGREGATION_STATE_PARTIAL = "partial"
AGGREGATION_STATE_BLOCKED = "blocked"
AGGREGATION_STATE_UNSUPPORTED = "unsupported"
AGGREGATION_STATE_PROHIBITED = "prohibited"
AGGREGATION_STATE_UNKNOWN = "unknown"
AGGREGATION_STATE_EXPERIMENTAL = "experimental"
AGGREGATION_STATE_PLANNING_ONLY = "planning_only"
AGGREGATION_STATE_NON_EXECUTABLE = "non_executable"
AGGREGATION_STATES: tuple[str, ...] = (
    AGGREGATION_STATE_AGGREGATED,
    AGGREGATION_STATE_PARTIAL,
    AGGREGATION_STATE_BLOCKED,
    AGGREGATION_STATE_UNSUPPORTED,
    AGGREGATION_STATE_PROHIBITED,
    AGGREGATION_STATE_UNKNOWN,
    AGGREGATION_STATE_EXPERIMENTAL,
    AGGREGATION_STATE_PLANNING_ONLY,
    AGGREGATION_STATE_NON_EXECUTABLE,
)
NON_AGGREGATED_STATES: tuple[str, ...] = tuple(
    state for state in AGGREGATION_STATES if state != AGGREGATION_STATE_AGGREGATED
)

AGGREGATION_VISIBILITY_VISIBLE = "visible"
AGGREGATION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
AGGREGATION_SEVERITY_INFO = "info"
AGGREGATION_SEVERITY_WARNING = "warning"
AGGREGATION_SEVERITY_BLOCKED = "blocked"

SUMMARY_ALLOWED_LANGUAGE: tuple[str, ...] = (
    "summary",
    "aggregation",
    "visibility",
    "evidence",
    "coverage",
    "context",
    "delta",
    "comparison",
    "planning-only",
    "non-executable",
)
SUMMARY_RECOMMENDATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "best",
    "chosen",
    "choose",
    "choice",
    "recommendation",
    "recommended",
)
SUMMARY_OPTIMIZATION_LANGUAGE_TERMS: tuple[str, ...] = (
    "optimal",
    "optimize",
    "optimized",
    "optimization",
)
SUMMARY_RANKING_LANGUAGE_TERMS: tuple[str, ...] = (
    "rank",
    "ranking",
)
SUMMARY_SCORING_LANGUAGE_TERMS: tuple[str, ...] = (
    "score",
    "scoring",
)
SUMMARY_SELECTION_LANGUAGE_TERMS: tuple[str, ...] = (
    "select",
    "selected",
    "selection",
)
SUMMARY_EXECUTION_LANGUAGE_TERMS: tuple[str, ...] = (
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
class V38CoordinationAggregationEvidence:
    evidence_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_context_ids: tuple[str, ...]
    provenance_reference: str
    replay_evidence_references: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    evidence_scope: str = "coordination_intelligence_aggregation_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    boundary_context_preserved: bool = True
    compatibility_context_preserved: bool = True
    evaluation_context_preserved: bool = True
    session_context_preserved: bool = True
    scenario_context_preserved: bool = True
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
            "scenario_context_ids",
            "replay_evidence_references",
            "rollback_evidence_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationAggregationResult:
    aggregation_id: str
    source_coordination_references: tuple[str, ...]
    boundary_context_ids: tuple[str, ...]
    compatibility_context_ids: tuple[str, ...]
    evaluation_context_ids: tuple[str, ...]
    session_context_ids: tuple[str, ...]
    scenario_context_ids: tuple[str, ...]
    aggregation_state: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    evidence: V38CoordinationAggregationEvidence
    fail_visible: bool = True
    hidden: bool = False
    hidden_risk: bool = False
    experimental_label_explicit: bool = False
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
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
            "boundary_context_ids",
            "compatibility_context_ids",
            "evaluation_context_ids",
            "session_context_ids",
            "scenario_context_ids",
            "replay_safe_evidence",
            "rollback_safe_evidence",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationIntelligenceSummary:
    summary_id: str
    summary_scope: str
    summary_statement: str
    total_coordination_record_count: int
    supported_visibility_count: int
    unsupported_visibility_count: int
    prohibited_visibility_count: int
    unknown_visibility_count: int
    compatibility_visibility_count: int
    evaluation_visibility_count: int
    session_visibility_count: int
    scenario_visibility_count: int
    fail_visible_finding_count: int
    provenance_continuity_count: int
    replay_evidence_count: int
    rollback_evidence_count: int
    non_execution_confirmation_count: int
    visibility_status: str
    non_execution_confirmation: bool
    immutable_evidence_record: bool = True
    runtime_state_machine: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    ranking_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    selection_behavior_enabled: bool = False
    execution_behavior_detected: bool = False
    hidden: bool = False
    hidden_risk: bool = False


@dataclass(frozen=True)
class V38CoordinationAggregationAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    source_boundary_audit_id: str
    source_compatibility_audit_id: str
    source_evaluation_audit_id: str
    source_session_audit_id: str
    source_scenario_audit_id: str
    aggregation_results: tuple[V38CoordinationAggregationResult, ...]
    intelligence_summaries: tuple[V38CoordinationIntelligenceSummary, ...]
    state_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_aggregation_hash: str = ""
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
    ranking_enabled: bool = False
    scoring_choice_system_enabled: bool = False
    selection_engine_enabled: bool = False
    execution_authorization_enabled: bool = False
    runtime_engine_enabled: bool = False
    state_machine_enabled: bool = False
    aggregation_runtime_state_machine_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "aggregation_results", tuple(self.aggregation_results or ()))
        object.__setattr__(self, "intelligence_summaries", tuple(self.intelligence_summaries or ()))


def aggregation_id(state: str, subject_id: str) -> str:
    return f"v3_8_aggregation_{state}_{subject_id}"


def aggregation_summary_id(subject_id: str) -> str:
    return f"v3_8_aggregation_summary_{subject_id}"


def export_v3_8_aggregation_evidence(
    evidence: V38CoordinationAggregationEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_coordination_references",
        "boundary_context_ids",
        "compatibility_context_ids",
        "evaluation_context_ids",
        "session_context_ids",
        "scenario_context_ids",
        "replay_evidence_references",
        "rollback_evidence_references",
        "deterministic_hash_references",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_8_aggregation_result(
    result: V38CoordinationAggregationResult,
) -> dict[str, Any]:
    return {
        "aggregation_id": result.aggregation_id,
        "source_coordination_references": _sorted_entries(result.source_coordination_references),
        "boundary_context_ids": _sorted_entries(result.boundary_context_ids),
        "compatibility_context_ids": _sorted_entries(result.compatibility_context_ids),
        "evaluation_context_ids": _sorted_entries(result.evaluation_context_ids),
        "session_context_ids": _sorted_entries(result.session_context_ids),
        "scenario_context_ids": _sorted_entries(result.scenario_context_ids),
        "aggregation_state": result.aggregation_state,
        "severity": result.severity,
        "explanation": result.explanation,
        "provenance_reference": result.provenance_reference,
        "replay_safe_evidence": _sorted_entries(result.replay_safe_evidence),
        "rollback_safe_evidence": _sorted_entries(result.rollback_safe_evidence),
        "deterministic_visibility_status": result.deterministic_visibility_status,
        "non_execution_confirmation": result.non_execution_confirmation,
        "evidence": export_v3_8_aggregation_evidence(result.evidence),
        "fail_visible": result.fail_visible,
        "hidden": result.hidden,
        "hidden_risk": result.hidden_risk,
        "experimental_label_explicit": result.experimental_label_explicit,
        "immutable_evidence_record": result.immutable_evidence_record,
        "runtime_state_machine": result.runtime_state_machine,
        "recommendation_behavior_enabled": result.recommendation_behavior_enabled,
        "optimization_behavior_enabled": result.optimization_behavior_enabled,
        "ranking_behavior_enabled": result.ranking_behavior_enabled,
        "scoring_behavior_enabled": result.scoring_behavior_enabled,
        "selection_behavior_enabled": result.selection_behavior_enabled,
        "execution_behavior_detected": result.execution_behavior_detected,
        "callable_execution_path_enabled": result.callable_execution_path_enabled,
    }


def export_v3_8_intelligence_summary(
    summary: V38CoordinationIntelligenceSummary,
) -> dict[str, Any]:
    return {
        "summary_id": summary.summary_id,
        "summary_scope": summary.summary_scope,
        "summary_statement": summary.summary_statement,
        "total_coordination_record_count": summary.total_coordination_record_count,
        "supported_visibility_count": summary.supported_visibility_count,
        "unsupported_visibility_count": summary.unsupported_visibility_count,
        "prohibited_visibility_count": summary.prohibited_visibility_count,
        "unknown_visibility_count": summary.unknown_visibility_count,
        "compatibility_visibility_count": summary.compatibility_visibility_count,
        "evaluation_visibility_count": summary.evaluation_visibility_count,
        "session_visibility_count": summary.session_visibility_count,
        "scenario_visibility_count": summary.scenario_visibility_count,
        "fail_visible_finding_count": summary.fail_visible_finding_count,
        "provenance_continuity_count": summary.provenance_continuity_count,
        "replay_evidence_count": summary.replay_evidence_count,
        "rollback_evidence_count": summary.rollback_evidence_count,
        "non_execution_confirmation_count": summary.non_execution_confirmation_count,
        "visibility_status": summary.visibility_status,
        "non_execution_confirmation": summary.non_execution_confirmation,
        "immutable_evidence_record": summary.immutable_evidence_record,
        "runtime_state_machine": summary.runtime_state_machine,
        "recommendation_behavior_enabled": summary.recommendation_behavior_enabled,
        "optimization_behavior_enabled": summary.optimization_behavior_enabled,
        "ranking_behavior_enabled": summary.ranking_behavior_enabled,
        "scoring_behavior_enabled": summary.scoring_behavior_enabled,
        "selection_behavior_enabled": summary.selection_behavior_enabled,
        "execution_behavior_detected": summary.execution_behavior_detected,
        "hidden": summary.hidden,
        "hidden_risk": summary.hidden_risk,
    }


def export_v3_8_aggregation_audit(audit: V38CoordinationAggregationAudit) -> dict[str, Any]:
    return {
        "audit_id": audit.audit_id,
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "source_scenario_audit_id": audit.source_scenario_audit_id,
        "aggregation_results": [
            export_v3_8_aggregation_result(result)
            for result in sorted(
                audit.aggregation_results,
                key=lambda item: (item.aggregation_state, item.aggregation_id),
            )
        ],
        "intelligence_summaries": [
            export_v3_8_intelligence_summary(summary)
            for summary in sorted(audit.intelligence_summaries, key=lambda item: item.summary_id)
        ],
        "state_counts": dict(sorted(audit.state_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_aggregation_hash": audit.deterministic_aggregation_hash,
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
        "ranking_enabled": audit.ranking_enabled,
        "scoring_choice_system_enabled": audit.scoring_choice_system_enabled,
        "selection_engine_enabled": audit.selection_engine_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "aggregation_runtime_state_machine_enabled": audit.aggregation_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_aggregation_audit(audit: V38CoordinationAggregationAudit) -> str:
    return stable_serialize(export_v3_8_aggregation_audit(audit))


def hash_v3_8_aggregation_audit(audit: V38CoordinationAggregationAudit) -> str:
    data = export_v3_8_aggregation_audit(audit)
    data.pop("deterministic_aggregation_hash", None)
    return deterministic_hash(data)


def validate_v3_8_aggregation_serialization_stability(
    audit: V38CoordinationAggregationAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_aggregation_audit(audit)
    second = serialize_v3_8_aggregation_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_intelligence_aggregation",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_aggregation_hash_stability(
    audit: V38CoordinationAggregationAudit,
) -> dict[str, Any]:
    first = hash_v3_8_aggregation_audit(audit)
    second = hash_v3_8_aggregation_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_intelligence_aggregation",
    }
