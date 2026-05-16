"""Declarative audit-chain input models for v3.5 orchestration planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_planning_snapshot_report_models import OrchestrationPlanningSnapshotResult
from .orchestration_snapshot_diff_report_models import OrchestrationSnapshotDiffResult


@dataclass(frozen=True)
class OrchestrationAuditChainInput:
    audit_chain_id: str
    chain_root_snapshot_id: str
    snapshot_sequence: tuple[OrchestrationPlanningSnapshotResult | None, ...]
    diff_analysis_sequence: tuple[OrchestrationSnapshotDiffResult | None, ...]
    chain_lineage_references: tuple[str, ...]
    replay_continuity_references: tuple[str, ...]
    rollback_continuity_references: tuple[str, ...]
    governance_continuity_references: tuple[str, ...]
    blocker_continuity_references: tuple[str, ...]
    compatibility_continuity_references: tuple[str, ...]
    environment_continuity_references: tuple[str, ...]
    deterministic_serialization_verified: bool
    expected_audit_chain_hash: str | None
    manual_review_reasons: tuple[str, ...]
    unsupported_reasons: tuple[str, ...]
    prohibited_reasons: tuple[str, ...]
    limitation_summary: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationAuditContinuitySummary:
    continuity_type: str
    references: tuple[str, ...]
    gaps: tuple[str, ...]


def export_audit_continuity_summary(summary: OrchestrationAuditContinuitySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["gaps"] = sorted(data["gaps"])
    return data


def serialize_audit_continuity_summary(summary: OrchestrationAuditContinuitySummary) -> str:
    return stable_serialize(export_audit_continuity_summary(summary))


def hash_audit_continuity_summary(summary: OrchestrationAuditContinuitySummary) -> str:
    return deterministic_hash(export_audit_continuity_summary(summary))
