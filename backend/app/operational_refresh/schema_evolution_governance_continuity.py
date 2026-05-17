"""Continuity certification for v4.1 schema evolution governance."""

from __future__ import annotations

from .schema_evolution_governance_models import SchemaEvolutionGovernance, default_schema_evolution_governance


def validate_schema_version_continuity(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    schema_reference = governance.identity.schema_reference
    reference_visible = schema_reference in governance.continuity_metadata.schema_continuity_references
    version_gap_visible = bool(governance.blocked_state_visibility.schema_version_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and version_gap_visible
            and governance.continuity_metadata.schema_continuity_preserved
            and not governance.continuity_metadata.automatic_schema_migration_enabled
        ),
        "schema_reference": schema_reference,
        "schema_reference_visible": reference_visible,
        "schema_version_discontinuity_visibility_count": len(
            governance.blocked_state_visibility.schema_version_discontinuity_visibility
        ),
        "schema_continuity_preserved": governance.continuity_metadata.schema_continuity_preserved,
        "automatic_schema_migration_enabled": governance.continuity_metadata.automatic_schema_migration_enabled,
    }


def validate_schema_lineage_continuity(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    lineage_reference = governance.identity.lineage_reference
    reference_visible = lineage_reference in governance.continuity_metadata.lineage_continuity_references
    lineage_visible = lineage_reference in governance.lineage_visibility.lineage_references
    discontinuity_visible = bool(governance.lineage_visibility.lineage_discontinuity_visibility)
    circular_visible = bool(governance.lineage_visibility.circular_schema_ancestry_visibility)
    return {
        "valid": (
            reference_visible
            and lineage_visible
            and discontinuity_visible
            and circular_visible
            and governance.lineage_visibility.lineage_continuity_preserved
            and governance.continuity_metadata.lineage_continuity_preserved
            and not governance.lineage_visibility.automatic_lineage_repair_enabled
        ),
        "lineage_reference": lineage_reference,
        "lineage_reference_visible": reference_visible,
        "lineage_visibility_visible": lineage_visible,
        "lineage_discontinuity_visibility_count": len(governance.lineage_visibility.lineage_discontinuity_visibility),
        "circular_schema_ancestry_visibility_count": len(governance.lineage_visibility.circular_schema_ancestry_visibility),
        "lineage_continuity_preserved": (
            governance.lineage_visibility.lineage_continuity_preserved
            and governance.continuity_metadata.lineage_continuity_preserved
        ),
    }


def validate_schema_provenance_continuity(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    provenance_reference = governance.identity.provenance_reference
    reference_visible = provenance_reference in governance.continuity_metadata.provenance_continuity_references
    provenance_visible = provenance_reference in governance.provenance_visibility.provenance_references
    discontinuity_visible = bool(governance.provenance_visibility.provenance_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and provenance_visible
            and discontinuity_visible
            and governance.provenance_visibility.provenance_continuity_preserved
            and governance.continuity_metadata.provenance_continuity_preserved
            and not governance.provenance_visibility.inferred_provenance_allowed
            and not governance.provenance_visibility.hidden_provenance_resolution_enabled
        ),
        "provenance_reference": provenance_reference,
        "provenance_reference_visible": reference_visible,
        "provenance_visibility_visible": provenance_visible,
        "provenance_discontinuity_visibility_count": len(
            governance.provenance_visibility.provenance_discontinuity_visibility
        ),
        "inferred_provenance_allowed": governance.provenance_visibility.inferred_provenance_allowed,
        "hidden_provenance_resolution_enabled": governance.provenance_visibility.hidden_provenance_resolution_enabled,
        "provenance_continuity_preserved": (
            governance.provenance_visibility.provenance_continuity_preserved
            and governance.continuity_metadata.provenance_continuity_preserved
        ),
    }


def validate_schema_replay_continuity(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    replay_id = governance.replay_visibility.replay_id
    reference_visible = replay_id in governance.continuity_metadata.replay_continuity_references
    discontinuity_visible = bool(governance.replay_visibility.replay_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and governance.replay_visibility.replay_safe
            and governance.continuity_metadata.replay_safe
            and governance.continuity_metadata.replay_continuity_preserved
            and not governance.replay_visibility.live_replay_enabled
            and not governance.replay_visibility.schema_migration_execution_enabled
            and not governance.replay_visibility.refresh_execution_enabled
        ),
        "replay_reference": replay_id,
        "replay_reference_visible": reference_visible,
        "replay_discontinuity_visibility_count": len(governance.replay_visibility.replay_discontinuity_visibility),
        "replay_safe": governance.replay_visibility.replay_safe and governance.continuity_metadata.replay_safe,
        "replay_continuity_preserved": governance.continuity_metadata.replay_continuity_preserved,
        "live_replay_enabled": governance.replay_visibility.live_replay_enabled,
    }


def validate_schema_rollback_continuity(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    rollback_id = governance.rollback_visibility.rollback_id
    reference_visible = rollback_id in governance.continuity_metadata.rollback_continuity_references
    discontinuity_visible = bool(governance.rollback_visibility.rollback_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and governance.rollback_visibility.rollback_safe
            and governance.continuity_metadata.rollback_safe
            and governance.continuity_metadata.rollback_continuity_preserved
            and not governance.rollback_visibility.automatic_rollback_enabled
            and not governance.rollback_visibility.automatic_recovery_enabled
            and not governance.rollback_visibility.schema_migration_execution_enabled
            and not governance.rollback_visibility.runtime_mutation_enabled
        ),
        "rollback_reference": rollback_id,
        "rollback_reference_visible": reference_visible,
        "rollback_discontinuity_visibility_count": len(governance.rollback_visibility.rollback_discontinuity_visibility),
        "rollback_safe": governance.rollback_visibility.rollback_safe and governance.continuity_metadata.rollback_safe,
        "rollback_continuity_preserved": governance.continuity_metadata.rollback_continuity_preserved,
        "automatic_rollback_enabled": governance.rollback_visibility.automatic_rollback_enabled,
        "automatic_recovery_enabled": governance.rollback_visibility.automatic_recovery_enabled,
    }


def validate_schema_compatibility_continuity(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    compatibility_id = governance.compatibility_visibility.compatibility_id
    reference_visible = compatibility_id in governance.continuity_metadata.compatibility_references
    blocked_visible = bool(governance.compatibility_visibility.blocked_transition_ids)
    unsupported_visible = bool(governance.compatibility_visibility.unsupported_transition_ids)
    stale_visible = bool(governance.compatibility_visibility.stale_transition_ids)
    prohibited_visible = bool(governance.compatibility_visibility.prohibited_transition_ids)
    circular_visible = bool(governance.compatibility_visibility.circular_schema_ancestry_ids)
    return {
        "valid": (
            reference_visible
            and blocked_visible
            and unsupported_visible
            and stale_visible
            and prohibited_visible
            and circular_visible
            and governance.continuity_metadata.compatibility_visibility_preserved
            and governance.compatibility_visibility.compatibility_visible
            and not governance.compatibility_visibility.automatic_compatibility_correction_enabled
            and not governance.compatibility_visibility.schema_migration_execution_enabled
            and not governance.compatibility_visibility.hidden_compatibility_resolution_enabled
        ),
        "compatibility_reference": compatibility_id,
        "compatibility_reference_visible": reference_visible,
        "blocked_transition_visibility_count": len(governance.compatibility_visibility.blocked_transition_ids),
        "unsupported_transition_visibility_count": len(governance.compatibility_visibility.unsupported_transition_ids),
        "stale_transition_visibility_count": len(governance.compatibility_visibility.stale_transition_ids),
        "prohibited_transition_visibility_count": len(governance.compatibility_visibility.prohibited_transition_ids),
        "circular_schema_ancestry_visibility_count": len(governance.compatibility_visibility.circular_schema_ancestry_ids),
        "compatibility_visibility_preserved": governance.continuity_metadata.compatibility_visibility_preserved,
        "automatic_compatibility_correction_enabled": (
            governance.compatibility_visibility.automatic_compatibility_correction_enabled
        ),
        "schema_migration_execution_enabled": governance.compatibility_visibility.schema_migration_execution_enabled,
    }


def certify_schema_evolution_continuity(governance: SchemaEvolutionGovernance | None = None) -> dict[str, object]:
    source = governance or default_schema_evolution_governance()
    schema = validate_schema_version_continuity(source)
    lineage = validate_schema_lineage_continuity(source)
    provenance = validate_schema_provenance_continuity(source)
    replay = validate_schema_replay_continuity(source)
    rollback = validate_schema_rollback_continuity(source)
    compatibility = validate_schema_compatibility_continuity(source)
    return {
        "valid": (
            schema["valid"]
            and lineage["valid"]
            and provenance["valid"]
            and replay["valid"]
            and rollback["valid"]
            and compatibility["valid"]
        ),
        "schema_continuity_valid": schema["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "compatibility_continuity_valid": compatibility["valid"],
        "schema_continuity": schema,
        "lineage_continuity": lineage,
        "provenance_continuity": provenance,
        "replay_continuity": replay,
        "rollback_continuity": rollback,
        "compatibility_continuity": compatibility,
    }
