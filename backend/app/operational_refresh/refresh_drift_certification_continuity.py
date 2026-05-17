"""Continuity certification for v4.1 refresh drift evidence."""

from __future__ import annotations

from .refresh_drift_certification_models import RefreshDriftCertification, default_refresh_drift_certification


def validate_drift_stack_continuity(certification: RefreshDriftCertification) -> dict[str, object]:
    drift_reference = certification.identity.drift_reference
    reference_visible = drift_reference in certification.continuity_metadata.drift_continuity_references
    cross_layer_visible = bool(certification.layer_visibility.cross_layer_conflict_ids)
    return {
        "valid": (
            reference_visible
            and cross_layer_visible
            and certification.continuity_metadata.drift_continuity_preserved
            and certification.continuity_metadata.dependency_continuity_preserved
            and certification.continuity_metadata.sequencing_continuity_preserved
            and certification.continuity_metadata.schema_continuity_preserved
            and not certification.continuity_metadata.drift_remediation_enabled
            and not certification.continuity_metadata.automatic_drift_correction_enabled
        ),
        "drift_reference": drift_reference,
        "drift_reference_visible": reference_visible,
        "cross_layer_conflict_visibility_count": len(certification.layer_visibility.cross_layer_conflict_ids),
        "drift_continuity_preserved": certification.continuity_metadata.drift_continuity_preserved,
        "dependency_continuity_preserved": certification.continuity_metadata.dependency_continuity_preserved,
        "sequencing_continuity_preserved": certification.continuity_metadata.sequencing_continuity_preserved,
        "schema_continuity_preserved": certification.continuity_metadata.schema_continuity_preserved,
    }


def validate_drift_lineage_continuity(certification: RefreshDriftCertification) -> dict[str, object]:
    lineage_reference = certification.identity.lineage_reference
    reference_visible = lineage_reference in certification.continuity_metadata.lineage_continuity_references
    lineage_visible = lineage_reference in certification.lineage_visibility.lineage_references
    discontinuity_visible = bool(certification.lineage_visibility.lineage_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and lineage_visible
            and discontinuity_visible
            and certification.lineage_visibility.lineage_continuity_preserved
            and certification.continuity_metadata.lineage_continuity_preserved
            and not certification.lineage_visibility.automatic_repair_enabled
        ),
        "lineage_reference": lineage_reference,
        "lineage_reference_visible": reference_visible,
        "lineage_visibility_visible": lineage_visible,
        "lineage_discontinuity_visibility_count": len(certification.lineage_visibility.lineage_discontinuity_visibility),
        "lineage_continuity_preserved": (
            certification.lineage_visibility.lineage_continuity_preserved
            and certification.continuity_metadata.lineage_continuity_preserved
        ),
    }


def validate_drift_provenance_continuity(certification: RefreshDriftCertification) -> dict[str, object]:
    provenance_reference = certification.identity.provenance_reference
    reference_visible = provenance_reference in certification.continuity_metadata.provenance_continuity_references
    provenance_visible = provenance_reference in certification.provenance_visibility.provenance_references
    discontinuity_visible = bool(certification.provenance_visibility.provenance_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and provenance_visible
            and discontinuity_visible
            and certification.provenance_visibility.provenance_continuity_preserved
            and certification.continuity_metadata.provenance_continuity_preserved
            and not certification.provenance_visibility.inferred_provenance_allowed
            and not certification.provenance_visibility.hidden_provenance_resolution_enabled
        ),
        "provenance_reference": provenance_reference,
        "provenance_reference_visible": reference_visible,
        "provenance_visibility_visible": provenance_visible,
        "provenance_discontinuity_visibility_count": len(
            certification.provenance_visibility.provenance_discontinuity_visibility
        ),
        "provenance_continuity_preserved": (
            certification.provenance_visibility.provenance_continuity_preserved
            and certification.continuity_metadata.provenance_continuity_preserved
        ),
    }


def validate_drift_replay_continuity(certification: RefreshDriftCertification) -> dict[str, object]:
    replay_id = certification.replay_visibility.replay_id
    reference_visible = replay_id in certification.continuity_metadata.replay_drift_references
    discontinuity_visible = bool(certification.replay_visibility.replay_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and certification.replay_visibility.replay_safe
            and certification.continuity_metadata.replay_safe
            and certification.continuity_metadata.replay_drift_preserved
            and not certification.replay_visibility.live_replay_enabled
            and not certification.replay_visibility.refresh_execution_enabled
            and not certification.replay_visibility.correction_execution_enabled
        ),
        "replay_reference": replay_id,
        "replay_reference_visible": reference_visible,
        "replay_discontinuity_visibility_count": len(certification.replay_visibility.replay_discontinuity_visibility),
        "replay_safe": certification.replay_visibility.replay_safe and certification.continuity_metadata.replay_safe,
        "replay_drift_preserved": certification.continuity_metadata.replay_drift_preserved,
    }


def validate_drift_rollback_continuity(certification: RefreshDriftCertification) -> dict[str, object]:
    rollback_id = certification.rollback_visibility.rollback_id
    reference_visible = rollback_id in certification.continuity_metadata.rollback_drift_references
    discontinuity_visible = bool(certification.rollback_visibility.rollback_discontinuity_visibility)
    return {
        "valid": (
            reference_visible
            and discontinuity_visible
            and certification.rollback_visibility.rollback_safe
            and certification.continuity_metadata.rollback_safe
            and certification.continuity_metadata.rollback_drift_preserved
            and not certification.rollback_visibility.automatic_rollback_enabled
            and not certification.rollback_visibility.automatic_recovery_enabled
            and not certification.rollback_visibility.runtime_mutation_enabled
        ),
        "rollback_reference": rollback_id,
        "rollback_reference_visible": reference_visible,
        "rollback_discontinuity_visibility_count": len(certification.rollback_visibility.rollback_discontinuity_visibility),
        "rollback_safe": certification.rollback_visibility.rollback_safe and certification.continuity_metadata.rollback_safe,
        "rollback_drift_preserved": certification.continuity_metadata.rollback_drift_preserved,
    }


def certify_refresh_drift_continuity(certification: RefreshDriftCertification | None = None) -> dict[str, object]:
    source = certification or default_refresh_drift_certification()
    drift = validate_drift_stack_continuity(source)
    lineage = validate_drift_lineage_continuity(source)
    provenance = validate_drift_provenance_continuity(source)
    replay = validate_drift_replay_continuity(source)
    rollback = validate_drift_rollback_continuity(source)
    return {
        "valid": drift["valid"] and lineage["valid"] and provenance["valid"] and replay["valid"] and rollback["valid"],
        "drift_continuity_valid": drift["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "drift_continuity": drift,
        "lineage_continuity": lineage,
        "provenance_continuity": provenance,
        "replay_continuity": replay,
        "rollback_continuity": rollback,
    }
