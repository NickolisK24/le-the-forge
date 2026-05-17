"""Deterministic v3.8 closeout and v3.9 readiness audit models.

These models are closeout evidence only. They do not execute coordination,
route work, schedule work, dispatch work, traverse graphs, mutate runtime
state, optimize, recommend, rank choices, score choices, select choices,
authorize execution, or create callable flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_CLOSEOUT_PHASE_ID = "v3_8_closeout_and_v3_9_readiness"
V3_8_CLOSEOUT_ID = "v3_8_closeout_and_v3_9_readiness_audit"
V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING = "closed_out_ready_for_v3_9_planning"
V3_8_CLOSEOUT_BLOCKED = "blocked"
V3_8_CLOSEOUT_INCOMPLETE = "incomplete"
V3_8_CLOSEOUT_UNSUPPORTED = "unsupported"
V3_8_CLOSEOUT_PROHIBITED = "prohibited"
V3_8_CLOSEOUT_UNKNOWN = "unknown"
V3_8_CLOSEOUT_NON_EXECUTABLE = "non_executable"
V3_8_CLOSEOUT_STATES: tuple[str, ...] = (
    V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING,
    V3_8_CLOSEOUT_BLOCKED,
    V3_8_CLOSEOUT_INCOMPLETE,
    V3_8_CLOSEOUT_UNSUPPORTED,
    V3_8_CLOSEOUT_PROHIBITED,
    V3_8_CLOSEOUT_UNKNOWN,
    V3_8_CLOSEOUT_NON_EXECUTABLE,
)

V3_9_PLANNING_READY = "v3_9_planning_ready"
V3_9_PLANNING_BLOCKED = "v3_9_planning_blocked"

V3_8_CLOSEOUT_VISIBILITY_VISIBLE = "visible"
V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE = "fail_visible"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class V38CloseoutReadinessInput:
    repo_root: str = ""
    omitted_phase_ids: tuple[str, ...] = ()
    omitted_report_paths: tuple[str, ...] = ()
    omitted_migration_doc_paths: tuple[str, ...] = ()
    manual_blockers: tuple[str, ...] = ()
    force_hidden_risk_count: int = 0
    force_recommendation_language_violation_count: int = 0
    force_optimization_language_violation_count: int = 0
    force_ranking_language_violation_count: int = 0
    force_scoring_behavior_violation_count: int = 0
    force_selection_behavior_violation_count: int = 0
    force_execution_boundary_violation_count: int = 0
    force_unsupported_state: bool = False
    force_prohibited_state: bool = False
    force_unknown_state: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "omitted_phase_ids",
            "omitted_report_paths",
            "omitted_migration_doc_paths",
            "manual_blockers",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CloseoutPhaseEvidence:
    phase_order: int
    phase_id: str
    phase_name: str
    module_paths: tuple[str, ...]
    report_path: str
    migration_doc_path: str
    script_path: str
    test_path: str
    report_hash: str
    report_exists: bool
    migration_doc_exists: bool
    module_paths_exist: bool
    script_exists: bool
    test_exists: bool
    deterministic_evidence_present: bool
    replay_evidence_visible: bool
    rollback_evidence_visible: bool
    provenance_continuity_visible: bool
    non_executable_verified: bool
    orchestration_boundaries_enforced: bool
    unsupported_visibility: bool
    prohibited_visibility: bool
    unknown_visibility: bool
    fail_visible_state_count: int
    hidden_risk_count: int
    recommendation_language_violation_count: int
    optimization_language_violation_count: int
    ranking_language_violation_count: int
    scoring_behavior_violation_count: int
    selection_behavior_violation_count: int
    execution_boundary_violation_count: int

    def __post_init__(self) -> None:
        _set_tuple_field(self, "module_paths")


@dataclass(frozen=True)
class V38CloseoutReadinessResult:
    closeout_id: str
    audited_phase_list: tuple[V38CloseoutPhaseEvidence, ...]
    generated_report_list: tuple[str, ...]
    migration_doc_list: tuple[str, ...]
    closeout_state: str
    v3_9_readiness_state: str
    explanation: str
    blocker_list: tuple[str, ...]
    warning_list: tuple[str, ...]
    provenance_continuity_summary: Mapping[str, int | bool | str]
    replay_evidence_summary: Mapping[str, int | bool | str]
    rollback_evidence_summary: Mapping[str, int | bool | str]
    deterministic_visibility_summary: Mapping[str, int | bool | str]
    validation_totals: Mapping[str, int | bool | str]
    suggested_v3_9_planning_themes: tuple[str, ...]
    deterministic_closeout_hash: str = ""
    non_execution_confirmation: bool = True
    prohibited_behavior_confirmation: bool = True
    closeout_visibility_status: str = V3_8_CLOSEOUT_VISIBILITY_VISIBLE
    fail_visible: bool = True
    hidden: bool = False
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    execution_authorization_enabled: bool = False
    runtime_mutation_enabled: bool = False
    runtime_engine_enabled: bool = False
    state_machine_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False
    production_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "audited_phase_list",
            "generated_report_list",
            "migration_doc_list",
            "blocker_list",
            "warning_list",
            "suggested_v3_9_planning_themes",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_8_closeout_phase_evidence(evidence: V38CloseoutPhaseEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    data["module_paths"] = _sorted_entries(data["module_paths"])
    return data


def export_v3_8_closeout_readiness_result(result: V38CloseoutReadinessResult) -> dict[str, Any]:
    data = asdict(result)
    data["audited_phase_list"] = [
        export_v3_8_closeout_phase_evidence(evidence)
        for evidence in sorted(result.audited_phase_list, key=lambda item: item.phase_order)
    ]
    for field_name in (
        "generated_report_list",
        "migration_doc_list",
        "blocker_list",
        "warning_list",
        "suggested_v3_9_planning_themes",
    ):
        data[field_name] = sorted(data[field_name])
    for field_name in (
        "provenance_continuity_summary",
        "replay_evidence_summary",
        "rollback_evidence_summary",
        "deterministic_visibility_summary",
        "validation_totals",
    ):
        data[field_name] = dict(sorted(data[field_name].items()))
    return data


def serialize_v3_8_closeout_readiness_result(result: V38CloseoutReadinessResult) -> str:
    return stable_serialize(export_v3_8_closeout_readiness_result(result))


def hash_v3_8_closeout_readiness_result(result: V38CloseoutReadinessResult) -> str:
    data = export_v3_8_closeout_readiness_result(result)
    data.pop("deterministic_closeout_hash", None)
    return deterministic_hash(data)


def validate_v3_8_closeout_serialization_stability(
    result: V38CloseoutReadinessResult,
) -> dict[str, Any]:
    first = serialize_v3_8_closeout_readiness_result(result)
    second = serialize_v3_8_closeout_readiness_result(result)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_closeout_readiness",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_closeout_hash_stability(result: V38CloseoutReadinessResult) -> dict[str, Any]:
    first = hash_v3_8_closeout_readiness_result(result)
    second = hash_v3_8_closeout_readiness_result(result)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_closeout_readiness",
    }
