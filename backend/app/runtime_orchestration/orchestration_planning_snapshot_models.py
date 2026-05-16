"""Declarative orchestration planning snapshot models for v3.5."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .governance_dependency_report_models import GovernanceDependencyResolutionResult
from .orchestration_coordination_report_models import OrchestrationCoordinationPlanningResult
from .orchestration_readiness_report_models import OrchestrationReadinessResult
from .orchestration_visibility_aggregation_report_models import OrchestrationVisibilityAggregationResult


@dataclass(frozen=True)
class OrchestrationPlanningSnapshotInput:
    snapshot_id: str
    orchestration_planning_graph_id: str
    readiness_result: OrchestrationReadinessResult | None
    dependency_result: GovernanceDependencyResolutionResult | None
    coordination_result: OrchestrationCoordinationPlanningResult | None
    visibility_result: OrchestrationVisibilityAggregationResult | None
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    compatibility_references: tuple[str, ...]
    environment_references: tuple[str, ...]
    limitation_summary: tuple[str, ...]
    manual_review_reasons: tuple[str, ...]
    hash_stability_verified: bool


@dataclass(frozen=True)
class OrchestrationPlanningStateReference:
    reference_type: str
    reference_id: str
    reference_status: str
    deterministic_hash: str


def export_planning_state_reference(reference: OrchestrationPlanningStateReference) -> dict[str, Any]:
    return asdict(reference)


def serialize_planning_state_reference(reference: OrchestrationPlanningStateReference) -> str:
    return stable_serialize(export_planning_state_reference(reference))


def hash_planning_state_reference(reference: OrchestrationPlanningStateReference) -> str:
    return deterministic_hash(export_planning_state_reference(reference))
