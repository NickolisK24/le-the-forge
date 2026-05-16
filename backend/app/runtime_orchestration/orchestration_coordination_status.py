"""Deterministic orchestration coordination planning statuses for v3.5."""

from __future__ import annotations


COORDINATION_READY_FOR_PLANNING = "coordination_ready_for_planning"
COORDINATION_BLOCKED_BY_DEPENDENCY = "coordination_blocked_by_dependency"
COORDINATION_BLOCKED_BY_GOVERNANCE = "coordination_blocked_by_governance"
COORDINATION_BLOCKED_BY_LINEAGE_GAP = "coordination_blocked_by_lineage_gap"
COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH = "coordination_blocked_by_environment_mismatch"
COORDINATION_REQUIRES_MANUAL_REVIEW = "coordination_requires_manual_review"
COORDINATION_UNSUPPORTED = "coordination_unsupported"
COORDINATION_PROHIBITED = "coordination_prohibited"
COORDINATION_INCOMPATIBLE = "coordination_incompatible"

COORDINATION_STATUS_PRIORITY: tuple[str, ...] = (
    COORDINATION_PROHIBITED,
    COORDINATION_BLOCKED_BY_DEPENDENCY,
    COORDINATION_BLOCKED_BY_GOVERNANCE,
    COORDINATION_BLOCKED_BY_LINEAGE_GAP,
    COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    COORDINATION_INCOMPATIBLE,
    COORDINATION_UNSUPPORTED,
    COORDINATION_REQUIRES_MANUAL_REVIEW,
    COORDINATION_READY_FOR_PLANNING,
)

COORDINATION_STATUSES: tuple[str, ...] = COORDINATION_STATUS_PRIORITY


def classify_coordination_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return COORDINATION_READY_FOR_PLANNING
    candidate_set = set(candidate_statuses)
    for status in COORDINATION_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return COORDINATION_INCOMPATIBLE


def export_coordination_statuses() -> list[str]:
    return list(COORDINATION_STATUSES)
