"""Deterministic v3.5 closeout and v3.6 readiness models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING = "v3_5_closed_out_ready_for_v3_6_planning"
V3_5_BLOCKED_BY_MISSING_PHASE_REPORT = "v3_5_blocked_by_missing_phase_report"
V3_5_BLOCKED_BY_INVALID_PHASE_STATUS = "v3_5_blocked_by_invalid_phase_status"
V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH = "v3_5_blocked_by_missing_deterministic_hash"
V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE = "v3_5_blocked_by_missing_scenario_coverage"
V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY = "v3_5_blocked_by_phase_chain_incompatibility"
V3_5_BLOCKED_BY_MISSING_DOCUMENTATION = "v3_5_blocked_by_missing_documentation"
V3_5_BLOCKED_BY_EXECUTION_LEAK = "v3_5_blocked_by_execution_leak"
V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK = "v3_5_blocked_by_production_consumption_leak"
V3_5_REQUIRES_MANUAL_REVIEW = "v3_5_requires_manual_review"

V3_5_CLOSEOUT_STATUS_PRIORITY: tuple[str, ...] = (
    V3_5_BLOCKED_BY_MISSING_PHASE_REPORT,
    V3_5_BLOCKED_BY_INVALID_PHASE_STATUS,
    V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH,
    V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE,
    V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY,
    V3_5_BLOCKED_BY_MISSING_DOCUMENTATION,
    V3_5_BLOCKED_BY_EXECUTION_LEAK,
    V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK,
    V3_5_REQUIRES_MANUAL_REVIEW,
    V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING,
)

V3_5_CLOSEOUT_STATUSES: tuple[str, ...] = V3_5_CLOSEOUT_STATUS_PRIORITY

V3_6_PLANNING_ALLOWED = "v3_6_planning_allowed"
V3_6_PLANNING_BLOCKED = "v3_6_planning_blocked"
V3_6_PLANNING_REQUIRES_MANUAL_REVIEW = "v3_6_planning_requires_manual_review"
V3_6_PLANNING_CLASSIFICATIONS: tuple[str, ...] = (
    V3_6_PLANNING_ALLOWED,
    V3_6_PLANNING_BLOCKED,
    V3_6_PLANNING_REQUIRES_MANUAL_REVIEW,
)


@dataclass(frozen=True)
class V35PhaseCloseoutSpec:
    phase_id: str
    phase_name: str
    report_path: str
    documentation_path: str
    status_field: str
    expected_status: str
    hash_fields: tuple[str, ...]


@dataclass(frozen=True)
class V35CloseoutReadinessInput:
    repo_root: Path
    phase_reports: Mapping[str, dict[str, Any] | None] | None = None
    phase_documentation_present: Mapping[str, bool] | None = None
    phase_chain_compatible: bool = True
    manual_review_reasons: tuple[str, ...] = ()
    limitation_summary: tuple[str, ...] = ()


@dataclass(frozen=True)
class V35PhaseCloseoutResult:
    phase_id: str
    phase_name: str
    report_path: str
    documentation_path: str
    report_present: bool
    documentation_present: bool
    status_field: str
    phase_status: str | None
    expected_status: str
    status_valid: bool
    deterministic_hash_present: bool
    scenario_coverage_present: bool
    execution_leak_detected: bool
    production_consumption_leak_detected: bool
    deterministic_hashes: tuple[str, ...]


@dataclass(frozen=True)
class V35CloseoutReadinessResult:
    closeout_status: str
    v3_6_planning_readiness: str
    planning_only: bool
    phase_results: tuple[V35PhaseCloseoutResult, ...]
    phase_coverage_summary: dict[str, int]
    missing_report_list: tuple[str, ...]
    missing_documentation_list: tuple[str, ...]
    invalid_phase_status_list: tuple[str, ...]
    missing_deterministic_hash_list: tuple[str, ...]
    missing_scenario_coverage_list: tuple[str, ...]
    compatibility_blocker_summary: tuple[str, ...]
    prohibition_preservation_summary: tuple[str, ...]
    v3_6_readiness_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    limitation_summary: tuple[str, ...]
    deterministic_closeout_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool
    orchestration_execution_enabled: bool
    routing_behavior_enabled: bool
    mutation_behavior_enabled: bool
    audit_log_writing_enabled: bool
    production_consumption_enabled: bool
    graph_execution_enabled: bool
    graph_traversal_behavior_enabled: bool
    scheduling_behavior_enabled: bool
    orchestration_dispatch_enabled: bool
    runtime_trace_capture_enabled: bool
    production_state_reads_enabled: bool
    live_replay_enabled: bool
    persistent_audit_storage_enabled: bool
    v3_6_behavior_enabled: bool


def classify_v3_5_closeout_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING
    candidate_set = set(candidate_statuses)
    for status in V3_5_CLOSEOUT_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY


def classify_v3_6_planning_readiness(closeout_status: str) -> str:
    if closeout_status == V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING:
        return V3_6_PLANNING_ALLOWED
    if closeout_status == V3_5_REQUIRES_MANUAL_REVIEW:
        return V3_6_PLANNING_REQUIRES_MANUAL_REVIEW
    return V3_6_PLANNING_BLOCKED


def export_phase_closeout_result(result: V35PhaseCloseoutResult) -> dict[str, Any]:
    data = asdict(result)
    data["deterministic_hashes"] = sorted(data["deterministic_hashes"])
    return data


def export_v3_5_closeout_result(result: V35CloseoutReadinessResult) -> dict[str, Any]:
    data = asdict(result)
    data["phase_results"] = [export_phase_closeout_result(item) for item in sorted(result.phase_results, key=lambda item: item.phase_id)]
    for field in (
        "missing_report_list",
        "missing_documentation_list",
        "invalid_phase_status_list",
        "missing_deterministic_hash_list",
        "missing_scenario_coverage_list",
        "compatibility_blocker_summary",
        "prohibition_preservation_summary",
        "v3_6_readiness_summary",
        "manual_review_summary",
        "limitation_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_hash"] = hash_v3_5_closeout_result(result)
    return data


def serialize_v3_5_closeout_result(result: V35CloseoutReadinessResult) -> str:
    return stable_serialize(export_v3_5_closeout_result(result))


def hash_v3_5_closeout_result(result: V35CloseoutReadinessResult) -> str:
    payload = asdict(result)
    payload["phase_results"] = [export_phase_closeout_result(item) for item in sorted(result.phase_results, key=lambda item: item.phase_id)]
    payload.pop("deterministic_hash", None)
    return deterministic_hash(payload)


def export_v3_5_closeout_statuses() -> list[str]:
    return list(V3_5_CLOSEOUT_STATUSES)


def export_v3_6_planning_classifications() -> list[str]:
    return list(V3_6_PLANNING_CLASSIFICATIONS)
