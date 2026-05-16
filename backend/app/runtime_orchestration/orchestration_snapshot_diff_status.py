"""Deterministic snapshot diff and drift statuses for v3.5 orchestration planning."""

from __future__ import annotations


SNAPSHOT_DIFF_STABLE = "snapshot_diff_stable"
SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT = "snapshot_diff_changed_without_drift"
SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE = "snapshot_diff_blocked_by_lineage_change"
SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY = "snapshot_diff_blocked_by_replay_instability"
SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH = "snapshot_diff_blocked_by_hash_mismatch"
SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW = "snapshot_diff_requires_manual_review"
SNAPSHOT_DIFF_UNSUPPORTED = "snapshot_diff_unsupported"
SNAPSHOT_DIFF_PROHIBITED = "snapshot_diff_prohibited"
SNAPSHOT_DIFF_DRIFT_DETECTED = "snapshot_diff_drift_detected"
SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED = "snapshot_diff_replay_safety_compromised"

SNAPSHOT_DIFF_STATUS_PRIORITY: tuple[str, ...] = (
    SNAPSHOT_DIFF_PROHIBITED,
    SNAPSHOT_DIFF_UNSUPPORTED,
    SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED,
    SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE,
    SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY,
    SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT,
    SNAPSHOT_DIFF_STABLE,
)

SNAPSHOT_DIFF_STATUSES: tuple[str, ...] = SNAPSHOT_DIFF_STATUS_PRIORITY


def classify_snapshot_diff_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return SNAPSHOT_DIFF_STABLE
    candidate_set = set(candidate_statuses)
    for status in SNAPSHOT_DIFF_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return SNAPSHOT_DIFF_DRIFT_DETECTED


def export_snapshot_diff_statuses() -> list[str]:
    return list(SNAPSHOT_DIFF_STATUSES)


def export_snapshot_diff_priority_order() -> list[str]:
    return list(SNAPSHOT_DIFF_STATUS_PRIORITY)
