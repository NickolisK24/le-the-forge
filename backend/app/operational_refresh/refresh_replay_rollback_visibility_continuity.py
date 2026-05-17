"""Continuity certification for v4.1 replay and rollback visibility."""

from __future__ import annotations

from .refresh_replay_rollback_visibility_models import (
    RefreshReplayRollbackVisibility,
    default_refresh_replay_rollback_visibility,
)


def validate_replay_visibility_continuity(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    replay_reference = visibility.identity.replay_reference
    reference_visible = replay_reference in visibility.continuity_metadata.replay_continuity_references
    lineage_visible = bool(visibility.lineage_visibility.replay_lineage_references)
    provenance_visible = bool(visibility.provenance_visibility.replay_provenance_references)
    discontinuity_visible = bool(visibility.blocked_state_visibility.replay_discontinuity_visibility)
    drift_visible = bool(visibility.drift_visibility.replay_drift_conflict_ids)
    return {
        "valid": (
            reference_visible
            and lineage_visible
            and provenance_visible
            and discontinuity_visible
            and drift_visible
            and visibility.continuity_metadata.replay_continuity_preserved
            and visibility.continuity_metadata.replay_safe
            and not visibility.continuity_metadata.replay_execution_enabled
            and not visibility.continuity_metadata.recovery_execution_enabled
            and not visibility.continuity_metadata.automatic_recovery_enabled
        ),
        "replay_reference": replay_reference,
        "replay_reference_visible": reference_visible,
        "replay_lineage_visible": lineage_visible,
        "replay_provenance_visible": provenance_visible,
        "replay_discontinuity_visibility_count": len(visibility.blocked_state_visibility.replay_discontinuity_visibility),
        "replay_drift_conflict_visibility_count": len(visibility.drift_visibility.replay_drift_conflict_ids),
        "replay_continuity_preserved": visibility.continuity_metadata.replay_continuity_preserved,
        "replay_safe": visibility.continuity_metadata.replay_safe,
    }


def validate_rollback_visibility_continuity(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    rollback_reference = visibility.identity.rollback_reference
    reference_visible = rollback_reference in visibility.continuity_metadata.rollback_continuity_references
    lineage_visible = bool(visibility.lineage_visibility.rollback_lineage_references)
    provenance_visible = bool(visibility.provenance_visibility.rollback_provenance_references)
    discontinuity_visible = bool(visibility.blocked_state_visibility.rollback_discontinuity_visibility)
    drift_visible = bool(visibility.drift_visibility.rollback_drift_conflict_ids)
    return {
        "valid": (
            reference_visible
            and lineage_visible
            and provenance_visible
            and discontinuity_visible
            and drift_visible
            and visibility.continuity_metadata.rollback_continuity_preserved
            and visibility.continuity_metadata.rollback_safe
            and not visibility.continuity_metadata.rollback_execution_enabled
            and not visibility.continuity_metadata.automatic_rollback_enabled
            and not visibility.continuity_metadata.automatic_recovery_enabled
            and not visibility.continuity_metadata.runtime_mutation_enabled
        ),
        "rollback_reference": rollback_reference,
        "rollback_reference_visible": reference_visible,
        "rollback_lineage_visible": lineage_visible,
        "rollback_provenance_visible": provenance_visible,
        "rollback_discontinuity_visibility_count": len(visibility.blocked_state_visibility.rollback_discontinuity_visibility),
        "rollback_drift_conflict_visibility_count": len(visibility.drift_visibility.rollback_drift_conflict_ids),
        "rollback_continuity_preserved": visibility.continuity_metadata.rollback_continuity_preserved,
        "rollback_safe": visibility.continuity_metadata.rollback_safe,
    }


def validate_replay_rollback_lineage_continuity(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    lineage_reference = visibility.identity.lineage_reference
    return {
        "valid": (
            visibility.lineage_visibility.lineage_id == lineage_reference
            and bool(visibility.lineage_visibility.replay_lineage_references)
            and bool(visibility.lineage_visibility.rollback_lineage_references)
            and bool(visibility.lineage_visibility.replay_lineage_discontinuity_visibility)
            and bool(visibility.lineage_visibility.rollback_lineage_discontinuity_visibility)
            and visibility.lineage_visibility.replay_lineage_continuity_preserved
            and visibility.lineage_visibility.rollback_lineage_continuity_preserved
            and not visibility.lineage_visibility.automatic_repair_enabled
            and not visibility.lineage_visibility.hidden_lineage_resolution_enabled
        ),
        "lineage_reference": lineage_reference,
        "lineage_reference_visible": visibility.lineage_visibility.lineage_id == lineage_reference,
        "replay_lineage_visibility_count": len(visibility.lineage_visibility.replay_lineage_references),
        "rollback_lineage_visibility_count": len(visibility.lineage_visibility.rollback_lineage_references),
        "replay_lineage_discontinuity_visibility_count": len(
            visibility.lineage_visibility.replay_lineage_discontinuity_visibility
        ),
        "rollback_lineage_discontinuity_visibility_count": len(
            visibility.lineage_visibility.rollback_lineage_discontinuity_visibility
        ),
    }


def validate_replay_rollback_provenance_continuity(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    provenance_reference = visibility.identity.provenance_reference
    return {
        "valid": (
            visibility.provenance_visibility.provenance_id == provenance_reference
            and bool(visibility.provenance_visibility.replay_provenance_references)
            and bool(visibility.provenance_visibility.rollback_provenance_references)
            and bool(visibility.provenance_visibility.inherited_from_references)
            and bool(visibility.provenance_visibility.replay_provenance_discontinuity_visibility)
            and bool(visibility.provenance_visibility.rollback_provenance_discontinuity_visibility)
            and visibility.provenance_visibility.replay_provenance_continuity_preserved
            and visibility.provenance_visibility.rollback_provenance_continuity_preserved
            and not visibility.provenance_visibility.inferred_provenance_allowed
            and not visibility.provenance_visibility.hidden_provenance_resolution_enabled
            and not visibility.provenance_visibility.execution_enabled
        ),
        "provenance_reference": provenance_reference,
        "provenance_reference_visible": visibility.provenance_visibility.provenance_id == provenance_reference,
        "replay_provenance_visibility_count": len(visibility.provenance_visibility.replay_provenance_references),
        "rollback_provenance_visibility_count": len(visibility.provenance_visibility.rollback_provenance_references),
        "inherited_from_count": len(visibility.provenance_visibility.inherited_from_references),
        "replay_provenance_discontinuity_visibility_count": len(
            visibility.provenance_visibility.replay_provenance_discontinuity_visibility
        ),
        "rollback_provenance_discontinuity_visibility_count": len(
            visibility.provenance_visibility.rollback_provenance_discontinuity_visibility
        ),
    }


def validate_replay_rollback_drift_continuity(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    return {
        "valid": (
            visibility.drift_visibility.replay_drift_visible
            and visibility.drift_visibility.rollback_drift_visible
            and bool(visibility.drift_visibility.replay_drift_conflict_ids)
            and bool(visibility.drift_visibility.rollback_drift_conflict_ids)
            and not visibility.drift_visibility.automatic_correction_enabled
            and not visibility.drift_visibility.remediation_enabled
            and not visibility.drift_visibility.hidden_drift_resolution_enabled
        ),
        "replay_drift_visible": visibility.drift_visibility.replay_drift_visible,
        "rollback_drift_visible": visibility.drift_visibility.rollback_drift_visible,
        "replay_drift_conflict_visibility_count": len(visibility.drift_visibility.replay_drift_conflict_ids),
        "rollback_drift_conflict_visibility_count": len(visibility.drift_visibility.rollback_drift_conflict_ids),
        "stale_replay_visibility_count": len(visibility.drift_visibility.stale_replay_ids),
        "stale_rollback_visibility_count": len(visibility.drift_visibility.stale_rollback_ids),
    }


def certify_replay_rollback_visibility_continuity(
    visibility: RefreshReplayRollbackVisibility | None = None,
) -> dict[str, object]:
    source = visibility or default_refresh_replay_rollback_visibility()
    replay = validate_replay_visibility_continuity(source)
    rollback = validate_rollback_visibility_continuity(source)
    lineage = validate_replay_rollback_lineage_continuity(source)
    provenance = validate_replay_rollback_provenance_continuity(source)
    drift = validate_replay_rollback_drift_continuity(source)
    return {
        "valid": replay["valid"] and rollback["valid"] and lineage["valid"] and provenance["valid"] and drift["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "replay_lineage_continuity_valid": lineage["valid"],
        "rollback_lineage_continuity_valid": lineage["valid"],
        "replay_provenance_continuity_valid": provenance["valid"],
        "rollback_provenance_continuity_valid": provenance["valid"],
        "replay_drift_valid": drift["valid"],
        "rollback_drift_valid": drift["valid"],
        "replay_continuity": replay,
        "rollback_continuity": rollback,
        "lineage_continuity": lineage,
        "provenance_continuity": provenance,
        "drift_continuity": drift,
    }
