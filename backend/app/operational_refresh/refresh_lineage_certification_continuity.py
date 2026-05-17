"""Continuity certification for v4.1 refresh lineage evidence."""

from __future__ import annotations

from .refresh_lineage_certification_models import RefreshLineageCertification, default_refresh_lineage_certification


def validate_lineage_ancestry_continuity(certification: RefreshLineageCertification) -> dict[str, object]:
    ancestry_reference = certification.identity.ancestry_reference
    reference_visible = ancestry_reference in certification.continuity_metadata.ancestry_continuity_references
    parent_child_links_visible = bool(certification.evolution_visibility.parent_child_lineage_visibility)
    circular_visible = bool(certification.blocked_state_visibility.circular_ancestry_links)
    discontinuity_visible = bool(certification.blocked_state_visibility.ancestry_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and parent_child_links_visible
            and circular_visible
            and discontinuity_visible
            and certification.continuity_metadata.ancestry_continuity_preserved
        ),
        "ancestry_reference": ancestry_reference,
        "ancestry_reference_visible": reference_visible,
        "parent_child_lineage_visibility_count": len(certification.evolution_visibility.parent_child_lineage_visibility),
        "circular_ancestry_visibility_count": len(certification.blocked_state_visibility.circular_ancestry_links),
        "ancestry_discontinuity_visibility_count": len(certification.blocked_state_visibility.ancestry_discontinuity_visibility),
        "ancestry_continuity_preserved": certification.continuity_metadata.ancestry_continuity_preserved,
    }


def validate_lineage_lineage_continuity(certification: RefreshLineageCertification) -> dict[str, object]:
    lineage_reference = certification.identity.lineage_reference
    reference_visible = lineage_reference in certification.continuity_metadata.lineage_continuity_references
    link_reference_visible = any(link.lineage_reference == lineage_reference for link in certification.ancestry_links)
    discontinuity_visible = bool(certification.blocked_state_visibility.lineage_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and link_reference_visible
            and discontinuity_visible
            and certification.continuity_metadata.lineage_continuity_preserved
        ),
        "lineage_reference": lineage_reference,
        "lineage_reference_visible": reference_visible,
        "lineage_link_reference_visible": link_reference_visible,
        "lineage_discontinuity_visibility_count": len(certification.blocked_state_visibility.lineage_discontinuity_visibility),
        "lineage_continuity_preserved": certification.continuity_metadata.lineage_continuity_preserved,
    }


def validate_lineage_provenance_continuity(certification: RefreshLineageCertification) -> dict[str, object]:
    provenance_reference = certification.identity.provenance_reference
    reference_visible = provenance_reference in certification.continuity_metadata.provenance_continuity_references
    inheritance_visible = any(
        inheritance.inherited_to_reference == provenance_reference
        for inheritance in certification.provenance_inheritance
    )
    discontinuity_visible = any(
        inheritance.provenance_discontinuity_visibility
        for inheritance in certification.provenance_inheritance
    )
    no_inferred_provenance = all(
        not inheritance.inferred_provenance_allowed for inheritance in certification.provenance_inheritance
    )
    hidden_resolution_count = sum(
        1 for inheritance in certification.provenance_inheritance if inheritance.hidden_provenance_resolution_enabled
    )
    return {
        "valid": (
            reference_visible
            and inheritance_visible
            and discontinuity_visible
            and no_inferred_provenance
            and hidden_resolution_count == 0
            and certification.continuity_metadata.provenance_continuity_preserved
        ),
        "provenance_reference": provenance_reference,
        "provenance_reference_visible": reference_visible,
        "provenance_inheritance_visible": inheritance_visible,
        "provenance_discontinuity_visibility_count": sum(
            len(inheritance.provenance_discontinuity_visibility)
            for inheritance in certification.provenance_inheritance
        ),
        "no_inferred_provenance": no_inferred_provenance,
        "hidden_provenance_resolution_count": hidden_resolution_count,
        "provenance_continuity_preserved": certification.continuity_metadata.provenance_continuity_preserved,
    }


def validate_lineage_replay_continuity(certification: RefreshLineageCertification) -> dict[str, object]:
    replay_id = certification.replay_lineage_visibility.replay_id
    reference_visible = replay_id in certification.continuity_metadata.replay_lineage_references
    discontinuity_visible = bool(certification.replay_lineage_visibility.replay_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and certification.continuity_metadata.replay_lineage_preserved
            and certification.continuity_metadata.replay_safe
            and certification.replay_lineage_visibility.replay_safe
            and not certification.replay_lineage_visibility.live_replay_enabled
            and not certification.replay_lineage_visibility.refresh_execution_enabled
        ),
        "replay_reference": replay_id,
        "replay_reference_visible": reference_visible,
        "replay_discontinuity_visibility_count": len(certification.replay_lineage_visibility.replay_discontinuity_visibility),
        "replay_lineage_preserved": certification.continuity_metadata.replay_lineage_preserved,
        "replay_safe": certification.continuity_metadata.replay_safe and certification.replay_lineage_visibility.replay_safe,
        "live_replay_enabled": certification.replay_lineage_visibility.live_replay_enabled,
        "refresh_execution_enabled": certification.replay_lineage_visibility.refresh_execution_enabled,
    }


def validate_lineage_rollback_continuity(certification: RefreshLineageCertification) -> dict[str, object]:
    rollback_id = certification.rollback_lineage_visibility.rollback_id
    reference_visible = rollback_id in certification.continuity_metadata.rollback_lineage_references
    discontinuity_visible = bool(certification.rollback_lineage_visibility.rollback_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and certification.continuity_metadata.rollback_lineage_preserved
            and certification.continuity_metadata.rollback_safe
            and certification.rollback_lineage_visibility.rollback_safe
            and not certification.rollback_lineage_visibility.automatic_rollback_enabled
            and not certification.rollback_lineage_visibility.recovery_execution_enabled
        ),
        "rollback_reference": rollback_id,
        "rollback_reference_visible": reference_visible,
        "rollback_discontinuity_visibility_count": len(certification.rollback_lineage_visibility.rollback_discontinuity_visibility),
        "rollback_lineage_preserved": certification.continuity_metadata.rollback_lineage_preserved,
        "rollback_safe": certification.continuity_metadata.rollback_safe and certification.rollback_lineage_visibility.rollback_safe,
        "automatic_rollback_enabled": certification.rollback_lineage_visibility.automatic_rollback_enabled,
        "recovery_execution_enabled": certification.rollback_lineage_visibility.recovery_execution_enabled,
    }


def validate_lineage_schema_continuity(certification: RefreshLineageCertification) -> dict[str, object]:
    schema_transition_id = certification.schema_transition_continuity.schema_transition_id
    reference_visible = schema_transition_id in certification.continuity_metadata.schema_transition_references
    discontinuity_visible = bool(certification.schema_transition_continuity.schema_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and certification.continuity_metadata.schema_transition_continuity_preserved
            and certification.schema_transition_continuity.schema_transition_continuity_preserved
            and not certification.schema_transition_continuity.automatic_schema_migration_enabled
            and not certification.schema_transition_continuity.migration_execution_enabled
            and not certification.schema_transition_continuity.hidden_schema_resolution_enabled
        ),
        "schema_transition_reference": schema_transition_id,
        "schema_transition_reference_visible": reference_visible,
        "schema_transition_visibility_count": len(certification.schema_transition_continuity.schema_transition_visibility),
        "schema_discontinuity_visibility_count": len(certification.schema_transition_continuity.schema_discontinuity_visibility),
        "schema_transition_continuity_preserved": (
            certification.continuity_metadata.schema_transition_continuity_preserved
            and certification.schema_transition_continuity.schema_transition_continuity_preserved
        ),
        "automatic_schema_migration_enabled": certification.schema_transition_continuity.automatic_schema_migration_enabled,
        "migration_execution_enabled": certification.schema_transition_continuity.migration_execution_enabled,
    }


def certify_refresh_lineage_continuity(
    certification: RefreshLineageCertification | None = None,
) -> dict[str, object]:
    source = certification or default_refresh_lineage_certification()
    ancestry = validate_lineage_ancestry_continuity(source)
    lineage = validate_lineage_lineage_continuity(source)
    provenance = validate_lineage_provenance_continuity(source)
    replay = validate_lineage_replay_continuity(source)
    rollback = validate_lineage_rollback_continuity(source)
    schema = validate_lineage_schema_continuity(source)
    return {
        "valid": (
            ancestry["valid"]
            and lineage["valid"]
            and provenance["valid"]
            and replay["valid"]
            and rollback["valid"]
            and schema["valid"]
        ),
        "ancestry_continuity_valid": ancestry["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "schema_continuity_valid": schema["valid"],
        "ancestry_continuity": ancestry,
        "lineage_continuity": lineage,
        "provenance_continuity": provenance,
        "replay_continuity": replay,
        "rollback_continuity": rollback,
        "schema_continuity": schema,
    }
