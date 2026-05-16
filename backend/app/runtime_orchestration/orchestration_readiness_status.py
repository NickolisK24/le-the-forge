"""Deterministic readiness statuses for v3.5 orchestration planning."""

from __future__ import annotations


READY_FOR_FUTURE_ORCHESTRATION_PLANNING = "ready_for_future_orchestration_planning"
BLOCKED_BY_GOVERNANCE_DEPENDENCY = "blocked_by_governance_dependency"
BLOCKED_BY_AUTHORIZATION_FAILURE = "blocked_by_authorization_failure"
BLOCKED_BY_REPLAY_LINEAGE_GAP = "blocked_by_replay_lineage_gap"
BLOCKED_BY_ROLLBACK_LINEAGE_GAP = "blocked_by_rollback_lineage_gap"
BLOCKED_BY_ENVIRONMENT_FAILURE = "blocked_by_environment_failure"
BLOCKED_BY_COMPATIBILITY_FAILURE = "blocked_by_compatibility_failure"
UNSUPPORTED_ORCHESTRATION_REQUEST = "unsupported_orchestration_request"
PROHIBITED_ORCHESTRATION_REQUEST = "prohibited_orchestration_request"
MANUAL_REVIEW_REQUIRED = "manual_review_required"

READINESS_STATUS_PRIORITY: tuple[str, ...] = (
    PROHIBITED_ORCHESTRATION_REQUEST,
    BLOCKED_BY_GOVERNANCE_DEPENDENCY,
    BLOCKED_BY_AUTHORIZATION_FAILURE,
    BLOCKED_BY_REPLAY_LINEAGE_GAP,
    BLOCKED_BY_ROLLBACK_LINEAGE_GAP,
    BLOCKED_BY_ENVIRONMENT_FAILURE,
    BLOCKED_BY_COMPATIBILITY_FAILURE,
    UNSUPPORTED_ORCHESTRATION_REQUEST,
    MANUAL_REVIEW_REQUIRED,
    READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
)

READINESS_STATUSES: tuple[str, ...] = READINESS_STATUS_PRIORITY


def classify_readiness_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    """Select the highest-priority deterministic readiness status."""

    if not candidate_statuses:
        return READY_FOR_FUTURE_ORCHESTRATION_PLANNING
    candidate_set = set(candidate_statuses)
    for status in READINESS_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return BLOCKED_BY_COMPATIBILITY_FAILURE


def export_readiness_statuses() -> list[str]:
    return list(READINESS_STATUSES)
