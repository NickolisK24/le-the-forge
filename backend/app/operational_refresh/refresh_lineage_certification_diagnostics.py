"""Deterministic diagnostics for v4.1 refresh lineage certification."""

from __future__ import annotations

from typing import Any

from .refresh_lineage_certification_continuity import certify_refresh_lineage_continuity
from .refresh_lineage_certification_hashing import (
    hash_lineage_diagnostics,
    hash_refresh_lineage_certification,
)
from .refresh_lineage_certification_integrity import enabled_lineage_certification_capability_flags
from .refresh_lineage_certification_models import RefreshLineageCertification, default_refresh_lineage_certification
from .refresh_lineage_certification_visibility import validate_refresh_lineage_visibility


def build_lineage_certification_diagnostics(
    certification: RefreshLineageCertification | None = None,
) -> dict[str, Any]:
    source = certification or default_refresh_lineage_certification()
    visibility = validate_refresh_lineage_visibility(source)
    continuity = certify_refresh_lineage_continuity(source)
    enabled_flags = enabled_lineage_certification_capability_flags(source)
    return {
        "certification_hash": hash_refresh_lineage_certification(source),
        "diagnostics_hash": hash_lineage_diagnostics(source.diagnostics),
        "visibility_validation": visibility,
        "continuity_certification": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "blocked_lineage_links": sorted(source.blocked_state_visibility.blocked_lineage_links),
        "circular_ancestry_links": sorted(source.blocked_state_visibility.circular_ancestry_links),
        "ancestry_discontinuity_visibility": sorted(
            source.blocked_state_visibility.ancestry_discontinuity_visibility
        ),
        "lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.lineage_discontinuity_visibility
        ),
        "provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.provenance_discontinuity_visibility
        ),
        "replay_discontinuity_visibility": sorted(source.blocked_state_visibility.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility": sorted(source.blocked_state_visibility.rollback_discontinuity_visibility),
        "schema_discontinuity_visibility": sorted(source.blocked_state_visibility.schema_discontinuity_visibility),
        "unsupported_lineage_nodes": sorted(source.unsupported_state_visibility.unsupported_lineage_nodes),
        "unsupported_lineage_links": sorted(source.unsupported_state_visibility.unsupported_lineage_links),
        "unsupported_lineage_providers": sorted(source.unsupported_state_visibility.unsupported_lineage_providers),
        "stale_lineage_links": sorted(source.unsupported_state_visibility.stale_lineage_links),
        "prohibited_lineage_links": sorted(source.unsupported_state_visibility.prohibited_lineage_links),
        "prohibited_lineage_domains": sorted(source.unsupported_state_visibility.prohibited_lineage_domains),
        "failure_visibility": sorted(source.unsupported_state_visibility.failure_visibility),
        "drift_visibility": sorted(source.drift_visibility.stale_lineage_references + source.drift_visibility.lineage_drift_references),
        "integrity_visibility": sorted(source.diagnostics.integrity_visibility),
        "warning_visibility": sorted(source.diagnostics.warning_visibility),
        "blocker_visibility": sorted(source.diagnostics.blocker_visibility),
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "silent_correction_absent": not source.diagnostics.silent_correction_enabled,
        "automatic_recovery_absent": not source.diagnostics.automatic_recovery_enabled,
        "fail_visible_warning_count": (
            len(source.blocked_state_visibility.blocked_lineage_links)
            + len(source.blocked_state_visibility.circular_ancestry_links)
            + len(source.blocked_state_visibility.ancestry_discontinuity_visibility)
            + len(source.blocked_state_visibility.lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.replay_discontinuity_visibility)
            + len(source.blocked_state_visibility.rollback_discontinuity_visibility)
            + len(source.blocked_state_visibility.schema_discontinuity_visibility)
            + len(source.unsupported_state_visibility.unsupported_lineage_nodes)
            + len(source.unsupported_state_visibility.unsupported_lineage_links)
            + len(source.unsupported_state_visibility.stale_lineage_links)
            + len(source.unsupported_state_visibility.prohibited_lineage_links)
            + len(source.unsupported_state_visibility.prohibited_lineage_domains)
            + len(source.unsupported_state_visibility.failure_visibility)
        ),
    }
