"""Deterministic serialization for v4.1 schema evolution governance."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .schema_evolution_governance_models import (
    SchemaBlockedStateVisibility,
    SchemaCompatibilityVisibility,
    SchemaContinuityMetadata,
    SchemaDriftVisibility,
    SchemaEvolutionDiagnostics,
    SchemaEvolutionGovernance,
    SchemaEvolutionIdentity,
    SchemaGovernanceVisibility,
    SchemaLineageVisibility,
    SchemaProvenanceVisibility,
    SchemaReplayVisibility,
    SchemaRollbackVisibility,
    SchemaUnsupportedStateVisibility,
    SchemaVersionNode,
    SchemaVersionTransition,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _disable_capability_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in (
        "schema_migration_execution_enabled",
        "automatic_schema_migration_enabled",
        "automatic_schema_repair_enabled",
        "automatic_compatibility_correction_enabled",
        "compatibility_correction_enabled",
        "refresh_execution_enabled",
        "orchestration_enabled",
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
        "automatic_rollback_enabled",
        "automatic_recovery_enabled",
        "hidden_migration_behavior_enabled",
        "implicit_execution_pathway_enabled",
        "silent_compatibility_fallback_enabled",
        "hidden_fallback_enabled",
        "hidden_compatibility_resolution_enabled",
        "hidden_lineage_resolution_enabled",
        "hidden_provenance_resolution_enabled",
        "hidden_drift_resolution_enabled",
        "hidden_unsupported_resolution_enabled",
        "live_replay_enabled",
        "execution_enabled",
        "inferred_provenance_allowed",
    ):
        if field_name in data:
            data[field_name] = False
    return data


def export_schema_evolution_identity(identity: SchemaEvolutionIdentity) -> dict[str, Any]:
    return _disable_capability_fields(asdict(identity))


def export_schema_version_node(node: SchemaVersionNode) -> dict[str, Any]:
    return _disable_capability_fields(asdict(node))


def export_schema_version_transition(transition: SchemaVersionTransition) -> dict[str, Any]:
    return _disable_capability_fields(asdict(transition))


def _export_tuple_fields(source: object, field_names: tuple[str, ...]) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(source))
    for field_name in field_names:
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_schema_compatibility_visibility(visibility: SchemaCompatibilityVisibility) -> dict[str, Any]:
    return _export_tuple_fields(
        visibility,
        (
            "transition_classifications",
            "compatible_transition_ids",
            "warning_transition_ids",
            "blocked_transition_ids",
            "unsupported_transition_ids",
            "stale_transition_ids",
            "prohibited_transition_ids",
            "circular_schema_ancestry_ids",
            "schema_version_discontinuity_ids",
        ),
    )


def export_schema_continuity_metadata(metadata: SchemaContinuityMetadata) -> dict[str, Any]:
    return _export_tuple_fields(
        metadata,
        (
            "schema_continuity_references",
            "lineage_continuity_references",
            "provenance_continuity_references",
            "replay_continuity_references",
            "rollback_continuity_references",
            "compatibility_references",
        ),
    )


def export_schema_lineage_visibility(visibility: SchemaLineageVisibility) -> dict[str, Any]:
    return _export_tuple_fields(
        visibility,
        (
            "lineage_references",
            "lineage_discontinuity_visibility",
            "circular_schema_ancestry_visibility",
        ),
    )


def export_schema_provenance_visibility(visibility: SchemaProvenanceVisibility) -> dict[str, Any]:
    return _export_tuple_fields(
        visibility,
        (
            "provenance_references",
            "inherited_from_references",
            "provenance_discontinuity_visibility",
        ),
    )


def export_schema_replay_visibility(visibility: SchemaReplayVisibility) -> dict[str, Any]:
    return _export_tuple_fields(visibility, ("replay_references", "replay_discontinuity_visibility"))


def export_schema_rollback_visibility(visibility: SchemaRollbackVisibility) -> dict[str, Any]:
    return _export_tuple_fields(visibility, ("rollback_references", "rollback_discontinuity_visibility"))


def export_schema_drift_visibility(visibility: SchemaDriftVisibility) -> dict[str, Any]:
    return _export_tuple_fields(
        visibility,
        ("stale_transition_ids", "schema_drift_references", "compatibility_drift_references"),
    )


def export_schema_blocked_state_visibility(visibility: SchemaBlockedStateVisibility) -> dict[str, Any]:
    return _export_tuple_fields(
        visibility,
        (
            "blocked_transition_ids",
            "blocked_compatibility_states",
            "schema_version_discontinuity_visibility",
            "schema_lineage_discontinuity_visibility",
            "schema_provenance_discontinuity_visibility",
            "schema_replay_discontinuity_visibility",
            "schema_rollback_discontinuity_visibility",
            "circular_schema_ancestry_visibility",
            "prohibited_migration_leakage",
            "prohibited_execution_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_remediation_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ),
    )


def export_schema_unsupported_state_visibility(visibility: SchemaUnsupportedStateVisibility) -> dict[str, Any]:
    return _export_tuple_fields(
        visibility,
        (
            "unsupported_node_ids",
            "unsupported_transition_ids",
            "unsupported_schema_providers",
            "stale_transition_ids",
            "prohibited_transition_ids",
            "prohibited_schema_domains",
            "failure_visibility",
        ),
    )


def export_schema_evolution_diagnostics(diagnostics: SchemaEvolutionDiagnostics) -> dict[str, Any]:
    return _export_tuple_fields(
        diagnostics,
        (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "unsupported_schema_visibility",
            "prohibited_schema_visibility",
            "compatibility_visibility",
            "drift_visibility",
            "integrity_visibility",
        ),
    )


def export_schema_governance_visibility(governance: SchemaGovernanceVisibility) -> dict[str, Any]:
    return _export_tuple_fields(governance, ("governance_references", "explicit_limitations", "explicit_prohibitions"))


def export_schema_evolution_governance(governance: SchemaEvolutionGovernance) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(governance))
    data["identity"] = export_schema_evolution_identity(governance.identity)
    data["version_nodes"] = [
        export_schema_version_node(node)
        for node in sorted(governance.version_nodes, key=lambda item: (item.deterministic_order, item.node_id))
    ]
    data["version_transitions"] = [
        export_schema_version_transition(transition)
        for transition in sorted(
            governance.version_transitions,
            key=lambda item: (item.deterministic_order, item.transition_id),
        )
    ]
    data["compatibility_visibility"] = export_schema_compatibility_visibility(governance.compatibility_visibility)
    data["continuity_metadata"] = export_schema_continuity_metadata(governance.continuity_metadata)
    data["lineage_visibility"] = export_schema_lineage_visibility(governance.lineage_visibility)
    data["provenance_visibility"] = export_schema_provenance_visibility(governance.provenance_visibility)
    data["replay_visibility"] = export_schema_replay_visibility(governance.replay_visibility)
    data["rollback_visibility"] = export_schema_rollback_visibility(governance.rollback_visibility)
    data["drift_visibility"] = export_schema_drift_visibility(governance.drift_visibility)
    data["blocked_state_visibility"] = export_schema_blocked_state_visibility(governance.blocked_state_visibility)
    data["unsupported_state_visibility"] = export_schema_unsupported_state_visibility(governance.unsupported_state_visibility)
    data["diagnostics"] = export_schema_evolution_diagnostics(governance.diagnostics)
    data["governance"] = export_schema_governance_visibility(governance.governance)
    return data


def serialize_schema_evolution_identity(identity: SchemaEvolutionIdentity) -> str:
    return stable_serialize(export_schema_evolution_identity(identity))


def serialize_schema_evolution_governance(governance: SchemaEvolutionGovernance) -> str:
    return stable_serialize(export_schema_evolution_governance(governance))
