"""Deterministic integrity-audit statuses for v3.5 orchestration planning."""

from __future__ import annotations


INTEGRITY_AUDIT_STABLE = "integrity_audit_stable"
INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE = "integrity_audit_blocked_by_governance_failure"
INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE = "integrity_audit_blocked_by_dependency_failure"
INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE = "integrity_audit_blocked_by_coordination_failure"
INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE = "integrity_audit_blocked_by_visibility_failure"
INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE = "integrity_audit_blocked_by_snapshot_failure"
INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE = "integrity_audit_blocked_by_diff_failure"
INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE = "integrity_audit_blocked_by_audit_chain_failure"
INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY = "integrity_audit_blocked_by_hash_instability"
INTEGRITY_AUDIT_REQUIRES_MANUAL_REVIEW = "integrity_audit_requires_manual_review"
INTEGRITY_AUDIT_UNSUPPORTED = "integrity_audit_unsupported"
INTEGRITY_AUDIT_PROHIBITED = "integrity_audit_prohibited"
INTEGRITY_AUDIT_INTEGRITY_COMPROMISED = "integrity_audit_integrity_compromised"

INTEGRITY_AUDIT_STATUS_PRIORITY: tuple[str, ...] = (
    INTEGRITY_AUDIT_PROHIBITED,
    INTEGRITY_AUDIT_UNSUPPORTED,
    INTEGRITY_AUDIT_INTEGRITY_COMPROMISED,
    INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY,
    INTEGRITY_AUDIT_REQUIRES_MANUAL_REVIEW,
    INTEGRITY_AUDIT_STABLE,
)

INTEGRITY_AUDIT_STATUSES: tuple[str, ...] = INTEGRITY_AUDIT_STATUS_PRIORITY


def classify_integrity_audit_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return INTEGRITY_AUDIT_STABLE
    candidate_set = set(candidate_statuses)
    for status in INTEGRITY_AUDIT_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return INTEGRITY_AUDIT_INTEGRITY_COMPROMISED


def export_integrity_audit_statuses() -> list[str]:
    return list(INTEGRITY_AUDIT_STATUSES)


def export_integrity_audit_priority_order() -> list[str]:
    return list(INTEGRITY_AUDIT_STATUS_PRIORITY)
