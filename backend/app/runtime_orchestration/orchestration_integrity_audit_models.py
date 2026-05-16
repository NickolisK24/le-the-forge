"""Declarative integrity-audit input models for v3.5 orchestration planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .governance_dependency_report_models import GovernanceDependencyResolutionResult
from .orchestration_audit_chain_report_models import OrchestrationAuditChainResult
from .orchestration_coordination_report_models import OrchestrationCoordinationPlanningResult
from .orchestration_planning_snapshot_report_models import OrchestrationPlanningSnapshotResult
from .orchestration_readiness_report_models import OrchestrationReadinessResult
from .orchestration_snapshot_diff_report_models import OrchestrationSnapshotDiffResult
from .orchestration_visibility_aggregation_report_models import OrchestrationVisibilityAggregationResult


@dataclass(frozen=True)
class OrchestrationIntegrityAuditInput:
    integrity_audit_id: str
    governance_integrity_references: tuple[str, ...]
    readiness_result: OrchestrationReadinessResult | None
    dependency_result: GovernanceDependencyResolutionResult | None
    coordination_result: OrchestrationCoordinationPlanningResult | None
    visibility_result: OrchestrationVisibilityAggregationResult | None
    snapshot_result: OrchestrationPlanningSnapshotResult | None
    diff_result: OrchestrationSnapshotDiffResult | None
    audit_chain_result: OrchestrationAuditChainResult | None
    replay_integrity_references: tuple[str, ...]
    rollback_integrity_references: tuple[str, ...]
    lineage_integrity_references: tuple[str, ...]
    deterministic_serialization_verified: bool
    expected_integrity_hash: str | None
    manual_review_reasons: tuple[str, ...]
    unsupported_reasons: tuple[str, ...]
    prohibited_reasons: tuple[str, ...]
    limitation_summary: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


def export_integrity_summary(summary: OrchestrationIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def serialize_integrity_summary(summary: OrchestrationIntegritySummary) -> str:
    return stable_serialize(export_integrity_summary(summary))


def hash_integrity_summary(summary: OrchestrationIntegritySummary) -> str:
    return deterministic_hash(export_integrity_summary(summary))
