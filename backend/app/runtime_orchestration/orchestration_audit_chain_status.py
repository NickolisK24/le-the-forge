"""Deterministic audit-chain statuses for v3.5 orchestration planning."""

from __future__ import annotations


AUDIT_CHAIN_STABLE = "audit_chain_stable"
AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP = "audit_chain_blocked_by_lineage_gap"
AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP = "audit_chain_blocked_by_replay_gap"
AUDIT_CHAIN_BLOCKED_BY_HASH_INSTABILITY = "audit_chain_blocked_by_hash_instability"
AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT = "audit_chain_blocked_by_missing_snapshot"
AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS = "audit_chain_blocked_by_missing_diff_analysis"
AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW = "audit_chain_requires_manual_review"
AUDIT_CHAIN_UNSUPPORTED = "audit_chain_unsupported"
AUDIT_CHAIN_PROHIBITED = "audit_chain_prohibited"
AUDIT_CHAIN_INTEGRITY_COMPROMISED = "audit_chain_integrity_compromised"

AUDIT_CHAIN_STATUS_PRIORITY: tuple[str, ...] = (
    AUDIT_CHAIN_PROHIBITED,
    AUDIT_CHAIN_UNSUPPORTED,
    AUDIT_CHAIN_INTEGRITY_COMPROMISED,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS,
    AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP,
    AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP,
    AUDIT_CHAIN_BLOCKED_BY_HASH_INSTABILITY,
    AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW,
    AUDIT_CHAIN_STABLE,
)

AUDIT_CHAIN_STATUSES: tuple[str, ...] = AUDIT_CHAIN_STATUS_PRIORITY


def classify_audit_chain_status(candidate_statuses: tuple[str, ...] | list[str]) -> str:
    if not candidate_statuses:
        return AUDIT_CHAIN_STABLE
    candidate_set = set(candidate_statuses)
    for status in AUDIT_CHAIN_STATUS_PRIORITY:
        if status in candidate_set:
            return status
    return AUDIT_CHAIN_INTEGRITY_COMPROMISED


def export_audit_chain_statuses() -> list[str]:
    return list(AUDIT_CHAIN_STATUSES)


def export_audit_chain_priority_order() -> list[str]:
    return list(AUDIT_CHAIN_STATUS_PRIORITY)
