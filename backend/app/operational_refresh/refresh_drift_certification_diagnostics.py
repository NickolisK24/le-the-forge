"""Deterministic diagnostics for v4.1 refresh drift certification."""

from __future__ import annotations

from typing import Any

from .refresh_drift_certification_continuity import certify_refresh_drift_continuity
from .refresh_drift_certification_hashing import hash_refresh_drift_certification, hash_refresh_drift_diagnostics
from .refresh_drift_certification_integrity import enabled_refresh_drift_capability_flags
from .refresh_drift_certification_models import RefreshDriftCertification, default_refresh_drift_certification
from .refresh_drift_certification_visibility import validate_refresh_drift_visibility


def build_refresh_drift_diagnostics(certification: RefreshDriftCertification | None = None) -> dict[str, Any]:
    source = certification or default_refresh_drift_certification()
    visibility = validate_refresh_drift_visibility(source)
    continuity = certify_refresh_drift_continuity(source)
    enabled_flags = enabled_refresh_drift_capability_flags(source)
    return {
        "drift_certification_hash": hash_refresh_drift_certification(source),
        "diagnostics_hash": hash_refresh_drift_diagnostics(source.diagnostics),
        "visibility_validation": visibility,
        "continuity_certification": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "manifest_drift_ids": sorted(source.layer_visibility.manifest_drift_ids),
        "dependency_drift_ids": sorted(source.layer_visibility.dependency_drift_ids),
        "lineage_drift_ids": sorted(source.layer_visibility.lineage_drift_ids),
        "schema_drift_ids": sorted(source.layer_visibility.schema_drift_ids),
        "sequencing_drift_ids": sorted(source.layer_visibility.sequencing_drift_ids),
        "cross_layer_conflict_ids": sorted(source.layer_visibility.cross_layer_conflict_ids),
        "blocked_drift_ids": sorted(source.blocked_state_visibility.blocked_drift_ids),
        "unresolved_drift_ids": sorted(source.blocked_state_visibility.unresolved_drift_ids),
        "unsupported_drift_ids": sorted(source.unsupported_state_visibility.unsupported_drift_ids),
        "unsupported_drift_providers": sorted(source.unsupported_state_visibility.unsupported_drift_providers),
        "stale_drift_ids": sorted(source.unsupported_state_visibility.stale_drift_ids),
        "prohibited_drift_ids": sorted(source.unsupported_state_visibility.prohibited_drift_ids),
        "prohibited_drift_domains": sorted(source.unsupported_state_visibility.prohibited_drift_domains),
        "lineage_discontinuity_visibility": sorted(source.blocked_state_visibility.lineage_discontinuity_visibility),
        "provenance_discontinuity_visibility": sorted(source.blocked_state_visibility.provenance_discontinuity_visibility),
        "replay_discontinuity_visibility": sorted(source.blocked_state_visibility.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility": sorted(source.blocked_state_visibility.rollback_discontinuity_visibility),
        "failure_visibility": sorted(source.unsupported_state_visibility.failure_visibility),
        "warning_visibility": sorted(source.diagnostics.warning_visibility),
        "blocker_visibility": sorted(source.diagnostics.blocker_visibility),
        "integrity_visibility": sorted(source.diagnostics.integrity_visibility),
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "drift_remediation_absent": not source.diagnostics.drift_remediation_enabled,
        "automatic_drift_correction_absent": not source.diagnostics.automatic_drift_correction_enabled,
        "automatic_repair_absent": not source.diagnostics.automatic_repair_enabled,
        "silent_drift_suppression_absent": not source.diagnostics.silent_drift_suppression_enabled,
        "automatic_recovery_absent": not source.diagnostics.automatic_recovery_enabled,
        "fail_visible_warning_count": (
            len(source.layer_visibility.cross_layer_conflict_ids)
            + len(source.blocked_state_visibility.blocked_drift_ids)
            + len(source.blocked_state_visibility.unresolved_drift_ids)
            + len(source.blocked_state_visibility.lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_discontinuity_visibility)
            + len(source.unsupported_state_visibility.unsupported_drift_ids)
            + len(source.unsupported_state_visibility.stale_drift_ids)
            + len(source.unsupported_state_visibility.prohibited_drift_ids)
            + len(source.unsupported_state_visibility.prohibited_drift_domains)
            + len(source.unsupported_state_visibility.failure_visibility)
        ),
    }
