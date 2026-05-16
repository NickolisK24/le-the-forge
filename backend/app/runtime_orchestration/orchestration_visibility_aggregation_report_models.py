"""Stable report models for v3.5 orchestration visibility aggregation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_visibility_aggregation_models import (
    OrchestrationVisibilitySummary,
    export_visibility_summary,
)


@dataclass(frozen=True)
class OrchestrationVisibilityAggregationResult:
    visibility_aggregation_id: str
    orchestration_planning_graph_id: str
    aggregate_visibility_status: str
    planning_only: bool
    readiness_summary: OrchestrationVisibilitySummary
    dependency_summary: OrchestrationVisibilitySummary
    coordination_summary: OrchestrationVisibilitySummary
    blocker_summary: tuple[str, ...]
    unsupported_state_summary: tuple[str, ...]
    prohibited_state_summary: tuple[str, ...]
    lineage_gap_summary: tuple[str, ...]
    compatibility_failure_summary: tuple[str, ...]
    environment_mismatch_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    limitation_summary: tuple[str, ...]
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
    auto_approval_behavior_enabled: bool


def export_visibility_aggregation_result(result: OrchestrationVisibilityAggregationResult) -> dict[str, Any]:
    data = asdict(result)
    data["readiness_summary"] = export_visibility_summary(result.readiness_summary)
    data["dependency_summary"] = export_visibility_summary(result.dependency_summary)
    data["coordination_summary"] = export_visibility_summary(result.coordination_summary)
    for field in (
        "blocker_summary",
        "unsupported_state_summary",
        "prohibited_state_summary",
        "lineage_gap_summary",
        "compatibility_failure_summary",
        "environment_mismatch_summary",
        "manual_review_summary",
        "limitation_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_hash"] = hash_visibility_aggregation_result(result)
    return data


def serialize_visibility_aggregation_result(result: OrchestrationVisibilityAggregationResult) -> str:
    return stable_serialize(export_visibility_aggregation_result(result))


def hash_visibility_aggregation_result(result: OrchestrationVisibilityAggregationResult) -> str:
    payload = asdict(result)
    payload["readiness_summary"] = export_visibility_summary(result.readiness_summary)
    payload["dependency_summary"] = export_visibility_summary(result.dependency_summary)
    payload["coordination_summary"] = export_visibility_summary(result.coordination_summary)
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
