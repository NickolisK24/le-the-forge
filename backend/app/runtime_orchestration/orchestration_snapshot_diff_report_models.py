"""Stable report models for v3.5 snapshot diff and drift analysis."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_snapshot_diff_models import (
    OrchestrationSnapshotFieldDiff,
    export_snapshot_field_diff,
)


@dataclass(frozen=True)
class OrchestrationSnapshotDiffResult:
    diff_analysis_id: str
    source_snapshot_id: str
    target_snapshot_id: str
    source_snapshot_hash: str
    target_snapshot_hash: str
    diff_status: str
    planning_only: bool
    readiness_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    dependency_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    coordination_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    visibility_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    blocker_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    unsupported_prohibited_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    lineage_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    compatibility_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    environment_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    replay_safety_diffs: tuple[str, ...]
    manual_review_diffs: tuple[str, ...]
    limitation_diffs: tuple[OrchestrationSnapshotFieldDiff, ...]
    drift_classifications: tuple[str, ...]
    deterministic_drift_summary: tuple[str, ...]
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


def export_snapshot_diff_result(result: OrchestrationSnapshotDiffResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "readiness_diffs",
        "dependency_diffs",
        "coordination_diffs",
        "visibility_diffs",
        "blocker_diffs",
        "unsupported_prohibited_diffs",
        "lineage_diffs",
        "compatibility_diffs",
        "environment_diffs",
        "limitation_diffs",
    ):
        data[field] = [export_snapshot_field_diff(diff) for diff in getattr(result, field)]
    for field in (
        "replay_safety_diffs",
        "manual_review_diffs",
        "drift_classifications",
        "deterministic_drift_summary",
    ):
        data[field] = sorted(data[field])
    data["deterministic_diff_hash"] = hash_snapshot_diff_result(result)
    return data


def serialize_snapshot_diff_result(result: OrchestrationSnapshotDiffResult) -> str:
    return stable_serialize(export_snapshot_diff_result(result))


def hash_snapshot_diff_result(result: OrchestrationSnapshotDiffResult) -> str:
    payload = asdict(result)
    for field in (
        "readiness_diffs",
        "dependency_diffs",
        "coordination_diffs",
        "visibility_diffs",
        "blocker_diffs",
        "unsupported_prohibited_diffs",
        "lineage_diffs",
        "compatibility_diffs",
        "environment_diffs",
        "limitation_diffs",
    ):
        payload[field] = [export_snapshot_field_diff(diff) for diff in getattr(result, field)]
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_diff_hash", None)
    return stable
