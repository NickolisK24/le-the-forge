"""Deterministic diagnostics for v4.1 refresh sequencing visibility."""

from __future__ import annotations

from typing import Any

from .refresh_sequencing_visibility_continuity import certify_refresh_sequencing_continuity
from .refresh_sequencing_visibility_hashing import (
    hash_refresh_sequencing_diagnostics,
    hash_refresh_sequencing_visibility,
)
from .refresh_sequencing_visibility_integrity import enabled_refresh_sequencing_capability_flags
from .refresh_sequencing_visibility_models import RefreshSequencingVisibility, default_refresh_sequencing_visibility
from .refresh_sequencing_visibility_visibility import validate_refresh_sequencing_visibility


def build_refresh_sequencing_diagnostics(visibility: RefreshSequencingVisibility | None = None) -> dict[str, Any]:
    source = visibility or default_refresh_sequencing_visibility()
    visibility_validation = validate_refresh_sequencing_visibility(source)
    continuity = certify_refresh_sequencing_continuity(source)
    enabled_flags = enabled_refresh_sequencing_capability_flags(source)
    return {
        "sequencing_visibility_hash": hash_refresh_sequencing_visibility(source),
        "diagnostics_hash": hash_refresh_sequencing_diagnostics(source.diagnostics),
        "visibility_validation": visibility_validation,
        "continuity_certification": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "blocked_relationship_ids": sorted(source.blocked_state_visibility.blocked_relationship_ids),
        "blocked_ordering_states": sorted(source.blocked_state_visibility.blocked_ordering_states),
        "sequencing_discontinuity_visibility": sorted(source.blocked_state_visibility.sequencing_discontinuity_visibility),
        "dependency_ordering_discontinuity_visibility": sorted(
            source.blocked_state_visibility.dependency_ordering_discontinuity_visibility
        ),
        "lineage_discontinuity_visibility": sorted(source.blocked_state_visibility.lineage_discontinuity_visibility),
        "provenance_discontinuity_visibility": sorted(source.blocked_state_visibility.provenance_discontinuity_visibility),
        "replay_discontinuity_visibility": sorted(source.blocked_state_visibility.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility": sorted(source.blocked_state_visibility.rollback_discontinuity_visibility),
        "circular_sequencing_visibility": sorted(source.blocked_state_visibility.circular_sequencing_visibility),
        "unsupported_node_ids": sorted(source.unsupported_state_visibility.unsupported_node_ids),
        "unsupported_relationship_ids": sorted(source.unsupported_state_visibility.unsupported_relationship_ids),
        "unsupported_sequencing_providers": sorted(source.unsupported_state_visibility.unsupported_sequencing_providers),
        "stale_relationship_ids": sorted(source.unsupported_state_visibility.stale_relationship_ids),
        "prohibited_relationship_ids": sorted(source.unsupported_state_visibility.prohibited_relationship_ids),
        "prohibited_sequencing_domains": sorted(source.unsupported_state_visibility.prohibited_sequencing_domains),
        "failure_visibility": sorted(source.unsupported_state_visibility.failure_visibility),
        "dependency_ordering_references": sorted(source.dependency_aware_visibility.dependency_ordering_references),
        "drift_visibility": sorted(
            source.drift_visibility.stale_relationship_ids + source.drift_visibility.sequencing_drift_references
        ),
        "integrity_visibility": sorted(source.diagnostics.integrity_visibility),
        "warning_visibility": sorted(source.diagnostics.warning_visibility),
        "blocker_visibility": sorted(source.diagnostics.blocker_visibility),
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "automatic_sequencing_absent": not source.diagnostics.automatic_sequencing_enabled,
        "automatic_dependency_resolution_absent": not source.diagnostics.automatic_dependency_resolution_enabled,
        "silent_ordering_correction_absent": not source.diagnostics.silent_ordering_correction_enabled,
        "automatic_recovery_absent": not source.diagnostics.automatic_recovery_enabled,
        "fail_visible_warning_count": (
            len(source.blocked_state_visibility.blocked_relationship_ids)
            + len(source.blocked_state_visibility.sequencing_discontinuity_visibility)
            + len(source.blocked_state_visibility.dependency_ordering_discontinuity_visibility)
            + len(source.blocked_state_visibility.lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_discontinuity_visibility)
            + len(source.blocked_state_visibility.circular_sequencing_visibility)
            + len(source.unsupported_state_visibility.unsupported_node_ids)
            + len(source.unsupported_state_visibility.unsupported_relationship_ids)
            + len(source.unsupported_state_visibility.stale_relationship_ids)
            + len(source.unsupported_state_visibility.prohibited_relationship_ids)
            + len(source.unsupported_state_visibility.prohibited_sequencing_domains)
            + len(source.unsupported_state_visibility.failure_visibility)
        ),
    }
