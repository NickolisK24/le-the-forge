"""Declarative snapshot diff input models for v3.5 orchestration planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_planning_snapshot_report_models import OrchestrationPlanningSnapshotResult


@dataclass(frozen=True)
class OrchestrationSnapshotDiffInput:
    diff_analysis_id: str
    source_snapshot: OrchestrationPlanningSnapshotResult
    target_snapshot: OrchestrationPlanningSnapshotResult
    replay_stability_verified: bool
    deterministic_serialization_verified: bool
    expected_source_snapshot_hash: str
    expected_target_snapshot_hash: str
    manual_review_reasons: tuple[str, ...]
    limitation_summary: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationSnapshotFieldDiff:
    diff_type: str
    source_values: tuple[str, ...]
    target_values: tuple[str, ...]
    added_values: tuple[str, ...]
    removed_values: tuple[str, ...]


def export_snapshot_field_diff(diff: OrchestrationSnapshotFieldDiff) -> dict[str, Any]:
    data = asdict(diff)
    for field in ("source_values", "target_values", "added_values", "removed_values"):
        data[field] = sorted(data[field])
    return data


def serialize_snapshot_field_diff(diff: OrchestrationSnapshotFieldDiff) -> str:
    return stable_serialize(export_snapshot_field_diff(diff))


def hash_snapshot_field_diff(diff: OrchestrationSnapshotFieldDiff) -> str:
    return deterministic_hash(export_snapshot_field_diff(diff))
