"""Stable report models for v3.5 orchestration audit chains."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_audit_chain_models import (
    OrchestrationAuditContinuitySummary,
    export_audit_continuity_summary,
)


@dataclass(frozen=True)
class OrchestrationAuditChainResult:
    audit_chain_id: str
    chain_root_snapshot_id: str
    audit_chain_status: str
    planning_only: bool
    chain_snapshot_sequence: tuple[str, ...]
    chain_diff_analysis_sequence: tuple[str, ...]
    lineage_continuity: OrchestrationAuditContinuitySummary
    replay_continuity: OrchestrationAuditContinuitySummary
    rollback_continuity: OrchestrationAuditContinuitySummary
    governance_continuity: OrchestrationAuditContinuitySummary
    blocker_continuity: OrchestrationAuditContinuitySummary
    compatibility_continuity: OrchestrationAuditContinuitySummary
    environment_continuity: OrchestrationAuditContinuitySummary
    lineage_gap_summary: tuple[str, ...]
    replay_gap_summary: tuple[str, ...]
    snapshot_gap_summary: tuple[str, ...]
    diff_analysis_gap_summary: tuple[str, ...]
    integrity_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    limitation_summary: tuple[str, ...]
    deterministic_audit_chain_hash: str
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


def export_audit_chain_result(result: OrchestrationAuditChainResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "lineage_continuity",
        "replay_continuity",
        "rollback_continuity",
        "governance_continuity",
        "blocker_continuity",
        "compatibility_continuity",
        "environment_continuity",
    ):
        data[field] = export_audit_continuity_summary(getattr(result, field))
    for field in (
        "chain_snapshot_sequence",
        "chain_diff_analysis_sequence",
        "lineage_gap_summary",
        "replay_gap_summary",
        "snapshot_gap_summary",
        "diff_analysis_gap_summary",
        "integrity_summary",
        "manual_review_summary",
        "limitation_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_hash"] = hash_audit_chain_result(result)
    return data


def serialize_audit_chain_result(result: OrchestrationAuditChainResult) -> str:
    return stable_serialize(export_audit_chain_result(result))


def hash_audit_chain_result(result: OrchestrationAuditChainResult) -> str:
    payload = asdict(result)
    for field in (
        "lineage_continuity",
        "replay_continuity",
        "rollback_continuity",
        "governance_continuity",
        "blocker_continuity",
        "compatibility_continuity",
        "environment_continuity",
    ):
        payload[field] = export_audit_continuity_summary(getattr(result, field))
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
