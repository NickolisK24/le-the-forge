"""Deterministic snapshot statuses for v3.5 orchestration planning."""

from __future__ import annotations


SNAPSHOT_READY_FOR_REPLAY_PLANNING = "snapshot_ready_for_replay_planning"
SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE = "snapshot_blocked_by_visibility_state"
SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE = "snapshot_blocked_by_missing_readiness_state"
SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE = "snapshot_blocked_by_missing_dependency_state"
SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE = "snapshot_blocked_by_missing_coordination_state"
SNAPSHOT_BLOCKED_BY_LINEAGE_GAP = "snapshot_blocked_by_lineage_gap"
SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY = "snapshot_blocked_by_hash_instability"
SNAPSHOT_REQUIRES_MANUAL_REVIEW = "snapshot_requires_manual_review"
SNAPSHOT_UNSUPPORTED = "snapshot_unsupported"
SNAPSHOT_PROHIBITED = "snapshot_prohibited"

SNAPSHOT_STATUS_PRIORITY: tuple[str, ...] = (
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_UNSUPPORTED,
    SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE,
    SNAPSHOT_BLOCKED_BY_LINEAGE_GAP,
    SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY,
    SNAPSHOT_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_READY_FOR_REPLAY_PLANNING,
)

SNAPSHOT_STATUSES: tuple[str, ...] = SNAPSHOT_STATUS_PRIORITY


def classify_snapshot_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return SNAPSHOT_READY_FOR_REPLAY_PLANNING
    candidate_set = set(candidate_statuses)
    for status in SNAPSHOT_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY


def export_snapshot_statuses() -> list[str]:
    return list(SNAPSHOT_STATUSES)


def export_snapshot_priority_order() -> list[str]:
    return list(SNAPSHOT_STATUS_PRIORITY)
