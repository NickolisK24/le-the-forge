"""Deterministic diagnostics for v4.1 replay and rollback visibility."""

from __future__ import annotations

from typing import Any

from .refresh_replay_rollback_visibility_continuity import certify_replay_rollback_visibility_continuity
from .refresh_replay_rollback_visibility_hashing import (
    hash_refresh_replay_rollback_visibility,
    hash_replay_rollback_diagnostics,
)
from .refresh_replay_rollback_visibility_integrity import enabled_replay_rollback_capability_flags
from .refresh_replay_rollback_visibility_models import (
    VISIBILITY_TYPE_REPLAY,
    VISIBILITY_TYPE_ROLLBACK,
    RefreshReplayRollbackVisibility,
    default_refresh_replay_rollback_visibility,
)
from .refresh_replay_rollback_visibility_visibility import validate_refresh_replay_rollback_visibility


def _evidence_ids_for_type(visibility: RefreshReplayRollbackVisibility, visibility_type: str) -> list[str]:
    return sorted(item.evidence_id for item in visibility.evidence if item.visibility_type == visibility_type)


def build_replay_diagnostics(visibility: RefreshReplayRollbackVisibility | None = None) -> dict[str, Any]:
    source = visibility or default_refresh_replay_rollback_visibility()
    diagnostics = build_replay_rollback_diagnostics(source)
    return {
        "visibility_type": VISIBILITY_TYPE_REPLAY,
        "replay_evidence_ids": _evidence_ids_for_type(source, VISIBILITY_TYPE_REPLAY),
        "blocked_replay_ids": sorted(source.blocked_state_visibility.blocked_replay_ids),
        "unsupported_replay_ids": sorted(source.unsupported_state_visibility.unsupported_replay_ids),
        "stale_replay_ids": sorted(source.unsupported_state_visibility.stale_replay_ids),
        "prohibited_replay_ids": sorted(source.unsupported_state_visibility.prohibited_replay_ids),
        "replay_discontinuity_visibility": sorted(source.blocked_state_visibility.replay_discontinuity_visibility),
        "replay_lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.replay_lineage_discontinuity_visibility
        ),
        "replay_provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.replay_provenance_discontinuity_visibility
        ),
        "replay_drift_conflict_visibility": sorted(source.blocked_state_visibility.replay_drift_conflict_visibility),
        "enabled_capability_count": diagnostics["enabled_capability_count"],
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "replay_execution_absent": not source.diagnostics.replay_execution_enabled,
        "recovery_execution_absent": not source.diagnostics.recovery_execution_enabled,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "automatic_correction_absent": not source.diagnostics.automatic_correction_enabled,
    }


def build_rollback_diagnostics(visibility: RefreshReplayRollbackVisibility | None = None) -> dict[str, Any]:
    source = visibility or default_refresh_replay_rollback_visibility()
    diagnostics = build_replay_rollback_diagnostics(source)
    return {
        "visibility_type": VISIBILITY_TYPE_ROLLBACK,
        "rollback_evidence_ids": _evidence_ids_for_type(source, VISIBILITY_TYPE_ROLLBACK),
        "blocked_rollback_ids": sorted(source.blocked_state_visibility.blocked_rollback_ids),
        "unsupported_rollback_ids": sorted(source.unsupported_state_visibility.unsupported_rollback_ids),
        "stale_rollback_ids": sorted(source.unsupported_state_visibility.stale_rollback_ids),
        "prohibited_rollback_ids": sorted(source.unsupported_state_visibility.prohibited_rollback_ids),
        "rollback_discontinuity_visibility": sorted(source.blocked_state_visibility.rollback_discontinuity_visibility),
        "rollback_lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.rollback_lineage_discontinuity_visibility
        ),
        "rollback_provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.rollback_provenance_discontinuity_visibility
        ),
        "rollback_drift_conflict_visibility": sorted(source.blocked_state_visibility.rollback_drift_conflict_visibility),
        "enabled_capability_count": diagnostics["enabled_capability_count"],
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "rollback_execution_absent": not source.diagnostics.rollback_execution_enabled,
        "recovery_execution_absent": not source.diagnostics.recovery_execution_enabled,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "automatic_correction_absent": not source.diagnostics.automatic_correction_enabled,
    }


def build_replay_rollback_diagnostics(visibility: RefreshReplayRollbackVisibility | None = None) -> dict[str, Any]:
    source = visibility or default_refresh_replay_rollback_visibility()
    visibility_validation = validate_refresh_replay_rollback_visibility(source)
    continuity = certify_replay_rollback_visibility_continuity(source)
    enabled_flags = enabled_replay_rollback_capability_flags(source)
    return {
        "replay_rollback_visibility_hash": hash_refresh_replay_rollback_visibility(source),
        "diagnostics_hash": hash_replay_rollback_diagnostics(source.diagnostics),
        "visibility_validation": visibility_validation,
        "continuity_certification": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "replay_evidence_ids": _evidence_ids_for_type(source, VISIBILITY_TYPE_REPLAY),
        "rollback_evidence_ids": _evidence_ids_for_type(source, VISIBILITY_TYPE_ROLLBACK),
        "blocked_replay_ids": sorted(source.blocked_state_visibility.blocked_replay_ids),
        "blocked_rollback_ids": sorted(source.blocked_state_visibility.blocked_rollback_ids),
        "unsupported_replay_ids": sorted(source.unsupported_state_visibility.unsupported_replay_ids),
        "unsupported_rollback_ids": sorted(source.unsupported_state_visibility.unsupported_rollback_ids),
        "stale_replay_ids": sorted(source.unsupported_state_visibility.stale_replay_ids),
        "stale_rollback_ids": sorted(source.unsupported_state_visibility.stale_rollback_ids),
        "prohibited_replay_ids": sorted(source.unsupported_state_visibility.prohibited_replay_ids),
        "prohibited_rollback_ids": sorted(source.unsupported_state_visibility.prohibited_rollback_ids),
        "prohibited_replay_domains": sorted(source.unsupported_state_visibility.prohibited_replay_domains),
        "prohibited_rollback_domains": sorted(source.unsupported_state_visibility.prohibited_rollback_domains),
        "replay_discontinuity_visibility": sorted(source.blocked_state_visibility.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility": sorted(source.blocked_state_visibility.rollback_discontinuity_visibility),
        "replay_lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.replay_lineage_discontinuity_visibility
        ),
        "rollback_lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.rollback_lineage_discontinuity_visibility
        ),
        "replay_provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.replay_provenance_discontinuity_visibility
        ),
        "rollback_provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.rollback_provenance_discontinuity_visibility
        ),
        "replay_drift_conflict_visibility": sorted(source.blocked_state_visibility.replay_drift_conflict_visibility),
        "rollback_drift_conflict_visibility": sorted(source.blocked_state_visibility.rollback_drift_conflict_visibility),
        "failure_visibility": sorted(source.unsupported_state_visibility.failure_visibility),
        "replay_warning_visibility": sorted(source.diagnostics.replay_warning_visibility),
        "rollback_warning_visibility": sorted(source.diagnostics.rollback_warning_visibility),
        "replay_blocker_visibility": sorted(source.diagnostics.replay_blocker_visibility),
        "rollback_blocker_visibility": sorted(source.diagnostics.rollback_blocker_visibility),
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "replay_execution_absent": not source.diagnostics.replay_execution_enabled,
        "rollback_execution_absent": not source.diagnostics.rollback_execution_enabled,
        "recovery_execution_absent": not source.diagnostics.recovery_execution_enabled,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "automatic_correction_absent": not source.diagnostics.automatic_correction_enabled,
        "automatic_recovery_absent": not source.diagnostics.automatic_recovery_enabled,
        "silent_replay_rollback_correction_absent": not source.diagnostics.silent_replay_rollback_correction_enabled,
        "fail_visible_warning_count": (
            len(source.blocked_state_visibility.blocked_replay_ids)
            + len(source.blocked_state_visibility.blocked_rollback_ids)
            + len(source.blocked_state_visibility.replay_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_drift_conflict_visibility)
            + len(source.blocked_state_visibility.rollback_drift_conflict_visibility)
            + len(source.unsupported_state_visibility.unsupported_replay_ids)
            + len(source.unsupported_state_visibility.unsupported_rollback_ids)
            + len(source.unsupported_state_visibility.stale_replay_ids)
            + len(source.unsupported_state_visibility.stale_rollback_ids)
            + len(source.unsupported_state_visibility.prohibited_replay_ids)
            + len(source.unsupported_state_visibility.prohibited_rollback_ids)
            + len(source.unsupported_state_visibility.prohibited_replay_domains)
            + len(source.unsupported_state_visibility.prohibited_rollback_domains)
            + len(source.unsupported_state_visibility.failure_visibility)
        ),
    }
