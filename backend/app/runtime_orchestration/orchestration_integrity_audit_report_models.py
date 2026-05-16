"""Stable report models for v3.5 orchestration integrity audits."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_integrity_audit_models import OrchestrationIntegritySummary, export_integrity_summary


@dataclass(frozen=True)
class OrchestrationIntegrityAuditResult:
    integrity_audit_id: str
    integrity_audit_status: str
    planning_only: bool
    governance_integrity: OrchestrationIntegritySummary
    readiness_integrity: OrchestrationIntegritySummary
    dependency_integrity: OrchestrationIntegritySummary
    coordination_integrity: OrchestrationIntegritySummary
    visibility_integrity: OrchestrationIntegritySummary
    snapshot_integrity: OrchestrationIntegritySummary
    diff_drift_integrity: OrchestrationIntegritySummary
    audit_chain_integrity: OrchestrationIntegritySummary
    replay_integrity: OrchestrationIntegritySummary
    rollback_integrity: OrchestrationIntegritySummary
    lineage_integrity: OrchestrationIntegritySummary
    deterministic_serialization_integrity: OrchestrationIntegritySummary
    deterministic_hash_stability: OrchestrationIntegritySummary
    failure_classification_summary: tuple[str, ...]
    blocker_summary: tuple[str, ...]
    unsupported_prohibited_summary: tuple[str, ...]
    limitation_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_integrity_hash: str
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


def export_integrity_audit_result(result: OrchestrationIntegrityAuditResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "governance_integrity",
        "readiness_integrity",
        "dependency_integrity",
        "coordination_integrity",
        "visibility_integrity",
        "snapshot_integrity",
        "diff_drift_integrity",
        "audit_chain_integrity",
        "replay_integrity",
        "rollback_integrity",
        "lineage_integrity",
        "deterministic_serialization_integrity",
        "deterministic_hash_stability",
    ):
        data[field] = export_integrity_summary(getattr(result, field))
    for field in (
        "failure_classification_summary",
        "blocker_summary",
        "unsupported_prohibited_summary",
        "limitation_summary",
        "manual_review_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_hash"] = hash_integrity_audit_result(result)
    return data


def serialize_integrity_audit_result(result: OrchestrationIntegrityAuditResult) -> str:
    return stable_serialize(export_integrity_audit_result(result))


def hash_integrity_audit_result(result: OrchestrationIntegrityAuditResult) -> str:
    payload = asdict(result)
    for field in (
        "governance_integrity",
        "readiness_integrity",
        "dependency_integrity",
        "coordination_integrity",
        "visibility_integrity",
        "snapshot_integrity",
        "diff_drift_integrity",
        "audit_chain_integrity",
        "replay_integrity",
        "rollback_integrity",
        "lineage_integrity",
        "deterministic_serialization_integrity",
        "deterministic_hash_stability",
    ):
        payload[field] = export_integrity_summary(getattr(result, field))
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
