"""Deterministic governance dependency statuses for v3.5 orchestration planning."""

from __future__ import annotations


DEPENDENCY_SATISFIED = "dependency_satisfied"
DEPENDENCY_MISSING = "dependency_missing"
DEPENDENCY_BLOCKED = "dependency_blocked"
DEPENDENCY_UNSUPPORTED = "dependency_unsupported"
DEPENDENCY_PROHIBITED = "dependency_prohibited"
DEPENDENCY_REQUIRES_MANUAL_REVIEW = "dependency_requires_manual_review"
DEPENDENCY_INCOMPATIBLE = "dependency_incompatible"
DEPENDENCY_LINEAGE_GAP = "dependency_lineage_gap"
DEPENDENCY_ENVIRONMENT_MISMATCH = "dependency_environment_mismatch"

DEPENDENCY_STATUS_PRIORITY: tuple[str, ...] = (
    DEPENDENCY_PROHIBITED,
    DEPENDENCY_BLOCKED,
    DEPENDENCY_MISSING,
    DEPENDENCY_LINEAGE_GAP,
    DEPENDENCY_ENVIRONMENT_MISMATCH,
    DEPENDENCY_INCOMPATIBLE,
    DEPENDENCY_UNSUPPORTED,
    DEPENDENCY_REQUIRES_MANUAL_REVIEW,
    DEPENDENCY_SATISFIED,
)

DEPENDENCY_STATUSES: tuple[str, ...] = DEPENDENCY_STATUS_PRIORITY


def classify_dependency_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    """Return the highest-priority deterministic dependency status."""

    if not candidate_statuses:
        return DEPENDENCY_SATISFIED
    candidate_set = set(candidate_statuses)
    for status in DEPENDENCY_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return DEPENDENCY_INCOMPATIBLE


def export_dependency_statuses() -> list[str]:
    return list(DEPENDENCY_STATUSES)
