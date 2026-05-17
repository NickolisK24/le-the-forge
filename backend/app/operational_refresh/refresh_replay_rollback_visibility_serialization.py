"""Deterministic serialization for v4.1 replay and rollback visibility."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_replay_rollback_visibility_models import (
    RefreshReplayRollbackVisibility,
    ReplayRollbackVisibilityIdentity,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


CAPABILITY_FIELDS: tuple[str, ...] = (
    "rollback_execution_enabled",
    "replay_execution_enabled",
    "recovery_execution_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_repair_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "schema_migration_execution_enabled",
    "automatic_migration_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "runtime_mutation_enabled",
    "hidden_recovery_behavior_enabled",
    "hidden_rollback_behavior_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_replay_rollback_correction_enabled",
    "hidden_fallback_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "hidden",
    "inferred_provenance_allowed",
    "execution_enabled",
)


def _disable_capability_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELDS:
        if field_name in data:
            data[field_name] = False
    return data


def _export_record(record: object) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(record))
    for field_name, value in tuple(data.items()):
        if isinstance(value, (list, tuple)):
            data[field_name] = sorted_entries(value)
    return data


def export_replay_rollback_identity(identity: ReplayRollbackVisibilityIdentity) -> dict[str, Any]:
    return _export_record(identity)


def export_refresh_replay_rollback_visibility(visibility: RefreshReplayRollbackVisibility) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(visibility))
    data["identity"] = export_replay_rollback_identity(visibility.identity)
    data["evidence"] = [
        _export_record(evidence)
        for evidence in sorted(
            visibility.evidence,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["lineage_visibility"] = _export_record(visibility.lineage_visibility)
    data["provenance_visibility"] = _export_record(visibility.provenance_visibility)
    data["continuity_metadata"] = _export_record(visibility.continuity_metadata)
    data["drift_visibility"] = _export_record(visibility.drift_visibility)
    data["blocked_state_visibility"] = _export_record(visibility.blocked_state_visibility)
    data["unsupported_state_visibility"] = _export_record(visibility.unsupported_state_visibility)
    data["diagnostics"] = _export_record(visibility.diagnostics)
    data["governance"] = _export_record(visibility.governance)
    return data


def serialize_replay_rollback_identity(identity: ReplayRollbackVisibilityIdentity) -> str:
    return stable_serialize(export_replay_rollback_identity(identity))


def serialize_refresh_replay_rollback_visibility(visibility: RefreshReplayRollbackVisibility) -> str:
    return stable_serialize(export_refresh_replay_rollback_visibility(visibility))
