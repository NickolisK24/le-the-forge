"""Stable report models for v3.5 orchestration planning snapshots."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_planning_snapshot_models import (
    OrchestrationPlanningStateReference,
    export_planning_state_reference,
)


@dataclass(frozen=True)
class OrchestrationPlanningSnapshotResult:
    snapshot_id: str
    orchestration_planning_graph_id: str
    snapshot_status: str
    planning_only: bool
    readiness_state_reference: OrchestrationPlanningStateReference | None
    dependency_state_reference: OrchestrationPlanningStateReference | None
    coordination_state_reference: OrchestrationPlanningStateReference | None
    visibility_aggregation_reference: OrchestrationPlanningStateReference | None
    blocker_summary: tuple[str, ...]
    unsupported_state_summary: tuple[str, ...]
    prohibited_state_summary: tuple[str, ...]
    lineage_summary: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    compatibility_references: tuple[str, ...]
    environment_references: tuple[str, ...]
    limitation_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_snapshot_hash: str
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
    runtime_trace_capture_enabled: bool
    production_state_reads_enabled: bool


def export_snapshot_result(result: OrchestrationPlanningSnapshotResult) -> dict[str, Any]:
    data = asdict(result)
    data["readiness_state_reference"] = _export_optional_reference(result.readiness_state_reference)
    data["dependency_state_reference"] = _export_optional_reference(result.dependency_state_reference)
    data["coordination_state_reference"] = _export_optional_reference(result.coordination_state_reference)
    data["visibility_aggregation_reference"] = _export_optional_reference(result.visibility_aggregation_reference)
    for field in (
        "blocker_summary",
        "unsupported_state_summary",
        "prohibited_state_summary",
        "lineage_summary",
        "replay_lineage_references",
        "rollback_lineage_references",
        "compatibility_references",
        "environment_references",
        "limitation_summary",
        "manual_review_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_hash"] = hash_snapshot_result(result)
    return data


def serialize_snapshot_result(result: OrchestrationPlanningSnapshotResult) -> str:
    return stable_serialize(export_snapshot_result(result))


def hash_snapshot_result(result: OrchestrationPlanningSnapshotResult) -> str:
    payload = asdict(result)
    payload["readiness_state_reference"] = _export_optional_reference(result.readiness_state_reference)
    payload["dependency_state_reference"] = _export_optional_reference(result.dependency_state_reference)
    payload["coordination_state_reference"] = _export_optional_reference(result.coordination_state_reference)
    payload["visibility_aggregation_reference"] = _export_optional_reference(result.visibility_aggregation_reference)
    return deterministic_hash(_without_hash(payload))


def _export_optional_reference(reference: OrchestrationPlanningStateReference | None) -> dict[str, Any] | None:
    if reference is None:
        return None
    return export_planning_state_reference(reference)


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
