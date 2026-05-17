"""Continuity certification for v4.1 refresh sequencing visibility."""

from __future__ import annotations

from .refresh_sequencing_visibility_models import RefreshSequencingVisibility, default_refresh_sequencing_visibility


def validate_refresh_sequencing_continuity(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    sequencing_reference = visibility.identity.sequencing_reference
    reference_visible = sequencing_reference in visibility.continuity_metadata.sequencing_continuity_references
    discontinuity_visible = bool(visibility.blocked_state_visibility.sequencing_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and visibility.continuity_metadata.sequencing_continuity_preserved
            and not visibility.continuity_metadata.automatic_sequencing_enabled
        ),
        "sequencing_reference": sequencing_reference,
        "sequencing_reference_visible": reference_visible,
        "sequencing_discontinuity_visibility_count": len(visibility.blocked_state_visibility.sequencing_discontinuity_visibility),
        "sequencing_continuity_preserved": visibility.continuity_metadata.sequencing_continuity_preserved,
        "automatic_sequencing_enabled": visibility.continuity_metadata.automatic_sequencing_enabled,
    }


def validate_dependency_ordering_continuity(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    reference_visible = (
        visibility.dependency_aware_visibility.visibility_id
        in visibility.continuity_metadata.dependency_ordering_references
    )
    discontinuity_visible = bool(visibility.blocked_state_visibility.dependency_ordering_discontinuity_visibility)
    circular_visible = bool(visibility.blocked_state_visibility.circular_sequencing_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and circular_visible
            and visibility.dependency_aware_visibility.dependency_aware_visibility_preserved
            and visibility.continuity_metadata.dependency_ordering_continuity_preserved
            and not visibility.dependency_aware_visibility.automatic_sequencing_enabled
            and not visibility.dependency_aware_visibility.automatic_dependency_resolution_enabled
            and not visibility.dependency_aware_visibility.orchestration_enabled
        ),
        "dependency_ordering_reference": visibility.dependency_aware_visibility.visibility_id,
        "dependency_ordering_reference_visible": reference_visible,
        "dependency_ordering_discontinuity_visibility_count": len(
            visibility.blocked_state_visibility.dependency_ordering_discontinuity_visibility
        ),
        "circular_sequencing_visibility_count": len(visibility.blocked_state_visibility.circular_sequencing_visibility),
        "dependency_ordering_continuity_preserved": (
            visibility.dependency_aware_visibility.dependency_aware_visibility_preserved
            and visibility.continuity_metadata.dependency_ordering_continuity_preserved
        ),
    }


def validate_refresh_sequencing_lineage_continuity(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    lineage_reference = visibility.identity.lineage_reference
    reference_visible = lineage_reference in visibility.continuity_metadata.lineage_continuity_references
    lineage_visible = lineage_reference in visibility.lineage_visibility.lineage_references
    discontinuity_visible = bool(visibility.lineage_visibility.lineage_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and lineage_visible
            and discontinuity_visible
            and visibility.lineage_visibility.lineage_continuity_preserved
            and visibility.continuity_metadata.lineage_continuity_preserved
            and not visibility.lineage_visibility.automatic_lineage_repair_enabled
        ),
        "lineage_reference": lineage_reference,
        "lineage_reference_visible": reference_visible,
        "lineage_visibility_visible": lineage_visible,
        "lineage_discontinuity_visibility_count": len(visibility.lineage_visibility.lineage_discontinuity_visibility),
        "lineage_continuity_preserved": (
            visibility.lineage_visibility.lineage_continuity_preserved
            and visibility.continuity_metadata.lineage_continuity_preserved
        ),
    }


def validate_refresh_sequencing_provenance_continuity(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    provenance_reference = visibility.identity.provenance_reference
    reference_visible = provenance_reference in visibility.continuity_metadata.provenance_continuity_references
    provenance_visible = provenance_reference in visibility.provenance_visibility.provenance_references
    discontinuity_visible = bool(visibility.provenance_visibility.provenance_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and provenance_visible
            and discontinuity_visible
            and visibility.provenance_visibility.provenance_continuity_preserved
            and visibility.continuity_metadata.provenance_continuity_preserved
            and not visibility.provenance_visibility.inferred_provenance_allowed
            and not visibility.provenance_visibility.hidden_provenance_resolution_enabled
        ),
        "provenance_reference": provenance_reference,
        "provenance_reference_visible": reference_visible,
        "provenance_visibility_visible": provenance_visible,
        "provenance_discontinuity_visibility_count": len(
            visibility.provenance_visibility.provenance_discontinuity_visibility
        ),
        "inferred_provenance_allowed": visibility.provenance_visibility.inferred_provenance_allowed,
        "provenance_continuity_preserved": (
            visibility.provenance_visibility.provenance_continuity_preserved
            and visibility.continuity_metadata.provenance_continuity_preserved
        ),
    }


def validate_refresh_sequencing_replay_continuity(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    replay_id = visibility.replay_visibility.replay_id
    reference_visible = replay_id in visibility.continuity_metadata.replay_sequencing_references
    discontinuity_visible = bool(visibility.replay_visibility.replay_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and visibility.replay_visibility.replay_safe
            and visibility.continuity_metadata.replay_safe
            and visibility.continuity_metadata.replay_sequencing_preserved
            and not visibility.replay_visibility.live_replay_enabled
            and not visibility.replay_visibility.refresh_execution_enabled
            and not visibility.replay_visibility.orchestration_enabled
        ),
        "replay_reference": replay_id,
        "replay_reference_visible": reference_visible,
        "replay_discontinuity_visibility_count": len(visibility.replay_visibility.replay_discontinuity_visibility),
        "replay_safe": visibility.replay_visibility.replay_safe and visibility.continuity_metadata.replay_safe,
        "replay_sequencing_preserved": visibility.continuity_metadata.replay_sequencing_preserved,
    }


def validate_refresh_sequencing_rollback_continuity(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    rollback_id = visibility.rollback_visibility.rollback_id
    reference_visible = rollback_id in visibility.continuity_metadata.rollback_sequencing_references
    discontinuity_visible = bool(visibility.rollback_visibility.rollback_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and visibility.rollback_visibility.rollback_safe
            and visibility.continuity_metadata.rollback_safe
            and visibility.continuity_metadata.rollback_sequencing_preserved
            and not visibility.rollback_visibility.automatic_rollback_enabled
            and not visibility.rollback_visibility.automatic_recovery_enabled
            and not visibility.rollback_visibility.orchestration_enabled
            and not visibility.rollback_visibility.runtime_mutation_enabled
        ),
        "rollback_reference": rollback_id,
        "rollback_reference_visible": reference_visible,
        "rollback_discontinuity_visibility_count": len(visibility.rollback_visibility.rollback_discontinuity_visibility),
        "rollback_safe": visibility.rollback_visibility.rollback_safe and visibility.continuity_metadata.rollback_safe,
        "rollback_sequencing_preserved": visibility.continuity_metadata.rollback_sequencing_preserved,
    }


def certify_refresh_sequencing_continuity(visibility: RefreshSequencingVisibility | None = None) -> dict[str, object]:
    source = visibility or default_refresh_sequencing_visibility()
    sequencing = validate_refresh_sequencing_continuity(source)
    dependency_ordering = validate_dependency_ordering_continuity(source)
    lineage = validate_refresh_sequencing_lineage_continuity(source)
    provenance = validate_refresh_sequencing_provenance_continuity(source)
    replay = validate_refresh_sequencing_replay_continuity(source)
    rollback = validate_refresh_sequencing_rollback_continuity(source)
    return {
        "valid": (
            sequencing["valid"]
            and dependency_ordering["valid"]
            and lineage["valid"]
            and provenance["valid"]
            and replay["valid"]
            and rollback["valid"]
        ),
        "sequencing_continuity_valid": sequencing["valid"],
        "dependency_ordering_continuity_valid": dependency_ordering["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "sequencing_continuity": sequencing,
        "dependency_ordering_continuity": dependency_ordering,
        "lineage_continuity": lineage,
        "provenance_continuity": provenance,
        "replay_continuity": replay,
        "rollback_continuity": rollback,
    }
