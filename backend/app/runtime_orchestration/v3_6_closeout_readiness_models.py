"""Deterministic v3.6 closeout and v3.7 readiness models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING = "v3_6_closed_out_ready_for_v3_7_planning"
V3_6_BLOCKED_FOR_V3_7_PLANNING = "v3_6_blocked_for_v3_7_planning"
V3_7_READINESS_CLASSIFICATIONS: tuple[str, ...] = (
    V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING,
    V3_6_BLOCKED_FOR_V3_7_PLANNING,
)

V3_6_BLOCKED_BY_MISSING_PHASE_REPORT = "v3_6_blocked_by_missing_phase_report"
V3_6_BLOCKED_BY_MISSING_DOCUMENTATION = "v3_6_blocked_by_missing_documentation"
V3_6_BLOCKED_BY_MISSING_DETERMINISTIC_HASH = "v3_6_blocked_by_missing_deterministic_hash"
V3_6_BLOCKED_BY_MISSING_SCENARIO_COVERAGE = "v3_6_blocked_by_missing_scenario_coverage"
V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE = "v3_6_blocked_by_missing_continuity_evidence"
V3_6_BLOCKED_BY_REPLAY_CONTINUITY_FAILURE = "v3_6_blocked_by_replay_continuity_failure"
V3_6_BLOCKED_BY_ROLLBACK_CONTINUITY_FAILURE = "v3_6_blocked_by_rollback_continuity_failure"
V3_6_BLOCKED_BY_PROVENANCE_FAILURE = "v3_6_blocked_by_provenance_failure"
V3_6_BLOCKED_BY_EXPLAINABILITY_FAILURE = "v3_6_blocked_by_explainability_failure"
V3_6_BLOCKED_BY_INTEGRITY_FAILURE = "v3_6_blocked_by_integrity_failure"
V3_6_BLOCKED_BY_BLOCKER_VISIBILITY_FAILURE = "v3_6_blocked_by_blocker_visibility_failure"
V3_6_BLOCKED_BY_UNSUPPORTED_PROHIBITED_VISIBILITY_FAILURE = "v3_6_blocked_by_unsupported_prohibited_visibility_failure"
V3_6_BLOCKED_BY_EXECUTION_LEAKAGE = "v3_6_blocked_by_execution_leakage"
V3_6_BLOCKED_BY_PROHIBITED_RUNTIME_BEHAVIOR = "v3_6_blocked_by_prohibited_runtime_behavior"
V3_6_BLOCKED_BY_PHASE_CHAIN_DISCONTINUITY = "v3_6_blocked_by_phase_chain_discontinuity"
V3_6_REQUIRES_MANUAL_REVIEW = "v3_6_requires_manual_review"

V3_6_CLOSEOUT_BLOCKER_PRIORITY: tuple[str, ...] = (
    V3_6_BLOCKED_BY_MISSING_PHASE_REPORT,
    V3_6_BLOCKED_BY_MISSING_DOCUMENTATION,
    V3_6_BLOCKED_BY_MISSING_DETERMINISTIC_HASH,
    V3_6_BLOCKED_BY_MISSING_SCENARIO_COVERAGE,
    V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE,
    V3_6_BLOCKED_BY_REPLAY_CONTINUITY_FAILURE,
    V3_6_BLOCKED_BY_ROLLBACK_CONTINUITY_FAILURE,
    V3_6_BLOCKED_BY_PROVENANCE_FAILURE,
    V3_6_BLOCKED_BY_EXPLAINABILITY_FAILURE,
    V3_6_BLOCKED_BY_INTEGRITY_FAILURE,
    V3_6_BLOCKED_BY_BLOCKER_VISIBILITY_FAILURE,
    V3_6_BLOCKED_BY_UNSUPPORTED_PROHIBITED_VISIBILITY_FAILURE,
    V3_6_BLOCKED_BY_EXECUTION_LEAKAGE,
    V3_6_BLOCKED_BY_PROHIBITED_RUNTIME_BEHAVIOR,
    V3_6_BLOCKED_BY_PHASE_CHAIN_DISCONTINUITY,
    V3_6_REQUIRES_MANUAL_REVIEW,
)

V3_6_CONTINUITY_PRESERVED = "v3_6_closeout_continuity_preserved"
V3_6_CONTINUITY_BLOCKED = "v3_6_closeout_continuity_blocked"
V3_6_VALIDATION_STABLE = "deterministic_validation_stable"
V3_6_VALIDATION_BLOCKED = "deterministic_validation_blocked"


@dataclass(frozen=True)
class V36StatusExpectation:
    field_name: str
    expected_value: str


@dataclass(frozen=True)
class V36PhaseCloseoutSpec:
    phase_id: str
    phase_order: int
    phase_name: str
    report_path: str
    documentation_path: str
    status_expectations: tuple[V36StatusExpectation, ...]
    hash_fields: tuple[str, ...]


@dataclass(frozen=True)
class V36CloseoutReadinessInput:
    repo_root: Path
    phase_reports: Mapping[str, dict[str, Any] | None] | None = None
    phase_documentation_present: Mapping[str, bool] | None = None
    phase_chain_connected: bool = True
    manual_review_reasons: tuple[str, ...] = ()
    limitation_summary: tuple[str, ...] = ()


@dataclass(frozen=True)
class V36PhaseCloseoutResult:
    phase_id: str
    phase_order: int
    phase_name: str
    report_path: str
    documentation_path: str
    report_present: bool
    documentation_present: bool
    status_results: Mapping[str, str | None]
    expected_status_results: Mapping[str, str]
    status_valid: bool
    deterministic_hash_present: bool
    deterministic_hashes: tuple[str, ...]
    scenario_coverage_present: bool
    continuity_statuses: Mapping[str, str]
    continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    integrity_continuity_preserved: bool
    blocker_visibility_preserved: bool
    unsupported_prohibited_visibility_preserved: bool
    execution_leakage_detected: bool
    prohibited_runtime_behavior_detected: bool


@dataclass(frozen=True)
class V36CloseoutReadinessResult:
    closeout_status: str
    v3_7_readiness_classification: str
    planning_only: bool
    phase_results: tuple[V36PhaseCloseoutResult, ...]
    phase_coverage_summary: Mapping[str, int]
    missing_report_list: tuple[str, ...]
    missing_documentation_list: tuple[str, ...]
    invalid_phase_status_list: tuple[str, ...]
    missing_deterministic_hash_list: tuple[str, ...]
    missing_scenario_coverage_list: tuple[str, ...]
    missing_continuity_evidence_list: tuple[str, ...]
    replay_continuity_failure_list: tuple[str, ...]
    rollback_continuity_failure_list: tuple[str, ...]
    provenance_failure_list: tuple[str, ...]
    explainability_failure_list: tuple[str, ...]
    integrity_failure_list: tuple[str, ...]
    blocker_visibility_failure_list: tuple[str, ...]
    unsupported_prohibited_visibility_failure_list: tuple[str, ...]
    execution_leakage_list: tuple[str, ...]
    prohibited_runtime_behavior_list: tuple[str, ...]
    phase_chain_blocker_summary: tuple[str, ...]
    readiness_blocker_summary: tuple[str, ...]
    prohibition_preservation_summary: tuple[str, ...]
    deterministic_guarantee_summary: tuple[str, ...]
    limitation_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_closeout_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool
    orchestration_execution_enabled: bool
    routing_behavior_enabled: bool
    mutation_behavior_enabled: bool
    persistent_write_enabled: bool
    production_runtime_behavior_enabled: bool
    production_state_reads_enabled: bool
    live_runtime_reads_enabled: bool
    background_execution_enabled: bool
    scheduling_behavior_enabled: bool
    recommendation_behavior_enabled: bool
    optimization_behavior_enabled: bool
    autonomous_behavior_enabled: bool
    graph_execution_enabled: bool
    execution_planning_enabled: bool
    orchestration_dispatch_enabled: bool


def classify_v3_6_closeout_readiness(blocker_statuses: tuple[str, ...] | list[str]) -> str:
    if not blocker_statuses:
        return V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING
    return V3_6_BLOCKED_FOR_V3_7_PLANNING


def export_phase_closeout_result(result: V36PhaseCloseoutResult) -> dict[str, Any]:
    data = asdict(result)
    data["status_results"] = dict(sorted(data["status_results"].items()))
    data["expected_status_results"] = dict(sorted(data["expected_status_results"].items()))
    data["deterministic_hashes"] = sorted(data["deterministic_hashes"])
    data["continuity_statuses"] = dict(sorted(data["continuity_statuses"].items()))
    return data


def export_v3_6_closeout_result(result: V36CloseoutReadinessResult) -> dict[str, Any]:
    data = asdict(result)
    data["phase_results"] = [
        export_phase_closeout_result(item)
        for item in sorted(result.phase_results, key=lambda item: item.phase_order)
    ]
    data["phase_coverage_summary"] = dict(sorted(data["phase_coverage_summary"].items()))
    for field in (
        "missing_report_list",
        "missing_documentation_list",
        "invalid_phase_status_list",
        "missing_deterministic_hash_list",
        "missing_scenario_coverage_list",
        "missing_continuity_evidence_list",
        "replay_continuity_failure_list",
        "rollback_continuity_failure_list",
        "provenance_failure_list",
        "explainability_failure_list",
        "integrity_failure_list",
        "blocker_visibility_failure_list",
        "unsupported_prohibited_visibility_failure_list",
        "execution_leakage_list",
        "prohibited_runtime_behavior_list",
        "phase_chain_blocker_summary",
        "readiness_blocker_summary",
        "prohibition_preservation_summary",
        "deterministic_guarantee_summary",
        "limitation_summary",
        "manual_review_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_hash"] = hash_v3_6_closeout_result(result)
    return data


def serialize_v3_6_closeout_result(result: V36CloseoutReadinessResult) -> str:
    return stable_serialize(export_v3_6_closeout_result(result))


def hash_v3_6_closeout_result(result: V36CloseoutReadinessResult) -> str:
    data = asdict(result)
    data["phase_results"] = [
        export_phase_closeout_result(item)
        for item in sorted(result.phase_results, key=lambda item: item.phase_order)
    ]
    data["phase_coverage_summary"] = dict(sorted(data["phase_coverage_summary"].items()))
    data.pop("deterministic_closeout_hash", None)
    return deterministic_hash(data)


def export_v3_7_readiness_classifications() -> list[str]:
    return list(V3_7_READINESS_CLASSIFICATIONS)


def export_v3_6_closeout_blocker_statuses() -> list[str]:
    return list(V3_6_CLOSEOUT_BLOCKER_PRIORITY)
