"""Deterministic aggregate visibility statuses for v3.5 orchestration planning."""

from __future__ import annotations


VISIBILITY_READY_FOR_PLANNING = "visibility_ready_for_planning"
VISIBILITY_BLOCKED_BY_READINESS = "visibility_blocked_by_readiness"
VISIBILITY_BLOCKED_BY_DEPENDENCY = "visibility_blocked_by_dependency"
VISIBILITY_BLOCKED_BY_COORDINATION = "visibility_blocked_by_coordination"
VISIBILITY_BLOCKED_BY_LINEAGE_GAP = "visibility_blocked_by_lineage_gap"
VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH = "visibility_blocked_by_environment_mismatch"
VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE = "visibility_blocked_by_compatibility_failure"
VISIBILITY_REQUIRES_MANUAL_REVIEW = "visibility_requires_manual_review"
VISIBILITY_UNSUPPORTED = "visibility_unsupported"
VISIBILITY_PROHIBITED = "visibility_prohibited"

VISIBILITY_STATUS_PRIORITY: tuple[str, ...] = (
    VISIBILITY_PROHIBITED,
    VISIBILITY_UNSUPPORTED,
    VISIBILITY_BLOCKED_BY_READINESS,
    VISIBILITY_BLOCKED_BY_DEPENDENCY,
    VISIBILITY_BLOCKED_BY_COORDINATION,
    VISIBILITY_BLOCKED_BY_LINEAGE_GAP,
    VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE,
    VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    VISIBILITY_REQUIRES_MANUAL_REVIEW,
    VISIBILITY_READY_FOR_PLANNING,
)

VISIBILITY_STATUSES: tuple[str, ...] = VISIBILITY_STATUS_PRIORITY


def classify_visibility_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return VISIBILITY_READY_FOR_PLANNING
    candidate_set = set(candidate_statuses)
    for status in VISIBILITY_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE


def export_visibility_statuses() -> list[str]:
    return list(VISIBILITY_STATUSES)


def export_visibility_priority_order() -> list[str]:
    return list(VISIBILITY_STATUS_PRIORITY)
