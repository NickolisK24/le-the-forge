"""Deterministic serialization for v4.1 refresh sequencing visibility."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_sequencing_visibility_models import RefreshSequencingIdentity, RefreshSequencingVisibility


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


CAPABILITY_FIELDS: tuple[str, ...] = (
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "automatic_dependency_resolution_enabled",
    "migration_execution_enabled",
    "automatic_migration_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "runtime_mutation_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_ordering_correction_enabled",
    "hidden_fallback_enabled",
    "hidden_ordering_resolution_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "automatic_lineage_repair_enabled",
    "live_replay_enabled",
    "execution_enabled",
    "inferred_provenance_allowed",
)


STRING_TUPLE_FIELDS: tuple[str, ...] = (
    "dependency_ordering_references",
    "ready_relationship_ids",
    "warning_relationship_ids",
    "blocked_relationship_ids",
    "unsupported_relationship_ids",
    "stale_relationship_ids",
    "prohibited_relationship_ids",
    "circular_relationship_ids",
    "sequencing_discontinuity_ids",
    "dependency_ordering_discontinuity_ids",
    "sequencing_continuity_references",
    "lineage_continuity_references",
    "provenance_continuity_references",
    "replay_sequencing_references",
    "rollback_sequencing_references",
    "lineage_references",
    "lineage_discontinuity_visibility",
    "provenance_references",
    "inherited_from_references",
    "provenance_discontinuity_visibility",
    "replay_discontinuity_visibility",
    "rollback_discontinuity_visibility",
    "sequencing_drift_references",
    "dependency_ordering_drift_references",
    "blocked_ordering_states",
    "sequencing_discontinuity_visibility",
    "dependency_ordering_discontinuity_visibility",
    "replay_discontinuity_visibility",
    "rollback_discontinuity_visibility",
    "circular_sequencing_visibility",
    "prohibited_orchestration_leakage",
    "prohibited_execution_leakage",
    "prohibited_remediation_leakage",
    "prohibited_planner_integration_leakage",
    "prohibited_production_consumption_leakage",
    "unsupported_node_ids",
    "unsupported_sequencing_providers",
    "prohibited_sequencing_domains",
    "failure_visibility",
    "diagnostic_references",
    "warning_visibility",
    "blocker_visibility",
    "unsupported_sequencing_visibility",
    "prohibited_sequencing_visibility",
    "drift_visibility",
    "integrity_visibility",
    "governance_references",
    "explicit_limitations",
    "explicit_prohibitions",
)


def _disable_capability_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELDS:
        if field_name in data:
            data[field_name] = False
    return data


def _export_record(record: object) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(record))
    for field_name in STRING_TUPLE_FIELDS:
        if field_name in data and isinstance(data[field_name], (list, tuple)):
            data[field_name] = sorted_entries(data[field_name])
    return data


def export_refresh_sequencing_identity(identity: RefreshSequencingIdentity) -> dict[str, Any]:
    return _export_record(identity)


def export_refresh_sequencing_visibility(visibility: RefreshSequencingVisibility) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(visibility))
    data["identity"] = export_refresh_sequencing_identity(visibility.identity)
    data["ordering_nodes"] = [
        _export_record(node)
        for node in sorted(visibility.ordering_nodes, key=lambda item: (item.deterministic_order, item.node_id))
    ]
    data["ordering_relationships"] = [
        _export_record(relationship)
        for relationship in sorted(
            visibility.ordering_relationships,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["dependency_aware_visibility"] = _export_record(visibility.dependency_aware_visibility)
    data["continuity_metadata"] = _export_record(visibility.continuity_metadata)
    data["lineage_visibility"] = _export_record(visibility.lineage_visibility)
    data["provenance_visibility"] = _export_record(visibility.provenance_visibility)
    data["replay_visibility"] = _export_record(visibility.replay_visibility)
    data["rollback_visibility"] = _export_record(visibility.rollback_visibility)
    data["drift_visibility"] = _export_record(visibility.drift_visibility)
    data["blocked_state_visibility"] = _export_record(visibility.blocked_state_visibility)
    data["unsupported_state_visibility"] = _export_record(visibility.unsupported_state_visibility)
    data["diagnostics"] = _export_record(visibility.diagnostics)
    data["governance"] = _export_record(visibility.governance)
    return data


def serialize_refresh_sequencing_identity(identity: RefreshSequencingIdentity) -> str:
    return stable_serialize(export_refresh_sequencing_identity(identity))


def serialize_refresh_sequencing_visibility(visibility: RefreshSequencingVisibility) -> str:
    return stable_serialize(export_refresh_sequencing_visibility(visibility))
