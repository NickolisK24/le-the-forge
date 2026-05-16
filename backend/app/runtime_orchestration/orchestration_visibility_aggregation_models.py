"""Declarative visibility aggregation models for v3.5 orchestration planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .governance_dependency_report_models import GovernanceDependencyResolutionResult
from .orchestration_coordination_report_models import OrchestrationCoordinationPlanningResult
from .orchestration_readiness_report_models import OrchestrationReadinessResult


@dataclass(frozen=True)
class OrchestrationVisibilityAggregationInput:
    visibility_aggregation_id: str
    orchestration_planning_graph_id: str
    readiness_result: OrchestrationReadinessResult
    dependency_result: GovernanceDependencyResolutionResult
    coordination_result: OrchestrationCoordinationPlanningResult
    limitation_summary: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationVisibilitySummary:
    source_id: str
    source_status: str
    blocker_ids: tuple[str, ...]
    unsupported_entries: tuple[str, ...]
    prohibited_entries: tuple[str, ...]
    lineage_gap_entries: tuple[str, ...]
    compatibility_failure_entries: tuple[str, ...]
    environment_mismatch_entries: tuple[str, ...]
    manual_review_entries: tuple[str, ...]
    limitation_entries: tuple[str, ...]


def export_visibility_summary(summary: OrchestrationVisibilitySummary) -> dict[str, Any]:
    data = asdict(summary)
    for field in (
        "blocker_ids",
        "unsupported_entries",
        "prohibited_entries",
        "lineage_gap_entries",
        "compatibility_failure_entries",
        "environment_mismatch_entries",
        "manual_review_entries",
        "limitation_entries",
    ):
        data[field] = sorted(data[field])
    return data


def serialize_visibility_summary(summary: OrchestrationVisibilitySummary) -> str:
    return stable_serialize(export_visibility_summary(summary))


def hash_visibility_summary(summary: OrchestrationVisibilitySummary) -> str:
    return deterministic_hash(export_visibility_summary(summary))
