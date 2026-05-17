"""Deterministic diagnostics for v4.1 schema evolution governance."""

from __future__ import annotations

from typing import Any

from .schema_evolution_governance_continuity import certify_schema_evolution_continuity
from .schema_evolution_governance_hashing import hash_schema_diagnostics, hash_schema_evolution_governance
from .schema_evolution_governance_integrity import enabled_schema_evolution_capability_flags
from .schema_evolution_governance_models import SchemaEvolutionGovernance, default_schema_evolution_governance
from .schema_evolution_governance_visibility import validate_schema_evolution_visibility


def build_schema_evolution_diagnostics(governance: SchemaEvolutionGovernance | None = None) -> dict[str, Any]:
    source = governance or default_schema_evolution_governance()
    visibility = validate_schema_evolution_visibility(source)
    continuity = certify_schema_evolution_continuity(source)
    enabled_flags = enabled_schema_evolution_capability_flags(source)
    return {
        "schema_governance_hash": hash_schema_evolution_governance(source),
        "diagnostics_hash": hash_schema_diagnostics(source.diagnostics),
        "visibility_validation": visibility,
        "continuity_certification": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "blocked_transition_ids": sorted(source.blocked_state_visibility.blocked_transition_ids),
        "blocked_compatibility_states": sorted(source.blocked_state_visibility.blocked_compatibility_states),
        "schema_version_discontinuity_visibility": sorted(
            source.blocked_state_visibility.schema_version_discontinuity_visibility
        ),
        "schema_lineage_discontinuity_visibility": sorted(
            source.blocked_state_visibility.schema_lineage_discontinuity_visibility
        ),
        "schema_provenance_discontinuity_visibility": sorted(
            source.blocked_state_visibility.schema_provenance_discontinuity_visibility
        ),
        "schema_replay_discontinuity_visibility": sorted(
            source.blocked_state_visibility.schema_replay_discontinuity_visibility
        ),
        "schema_rollback_discontinuity_visibility": sorted(
            source.blocked_state_visibility.schema_rollback_discontinuity_visibility
        ),
        "circular_schema_ancestry_visibility": sorted(
            source.blocked_state_visibility.circular_schema_ancestry_visibility
        ),
        "unsupported_node_ids": sorted(source.unsupported_state_visibility.unsupported_node_ids),
        "unsupported_transition_ids": sorted(source.unsupported_state_visibility.unsupported_transition_ids),
        "unsupported_schema_providers": sorted(source.unsupported_state_visibility.unsupported_schema_providers),
        "stale_transition_ids": sorted(source.unsupported_state_visibility.stale_transition_ids),
        "prohibited_transition_ids": sorted(source.unsupported_state_visibility.prohibited_transition_ids),
        "prohibited_schema_domains": sorted(source.unsupported_state_visibility.prohibited_schema_domains),
        "failure_visibility": sorted(source.unsupported_state_visibility.failure_visibility),
        "compatibility_classifications": sorted(source.compatibility_visibility.transition_classifications),
        "drift_visibility": sorted(
            source.drift_visibility.stale_transition_ids + source.drift_visibility.schema_drift_references
        ),
        "integrity_visibility": sorted(source.diagnostics.integrity_visibility),
        "warning_visibility": sorted(source.diagnostics.warning_visibility),
        "blocker_visibility": sorted(source.diagnostics.blocker_visibility),
        "diagnostics_visible": source.diagnostics.diagnostics_visible,
        "diagnostics_are_descriptive_only": source.diagnostics.descriptive_only,
        "remediation_absent": not source.diagnostics.remediation_enabled,
        "automatic_schema_migration_absent": not source.diagnostics.automatic_schema_migration_enabled,
        "automatic_schema_repair_absent": not source.diagnostics.automatic_schema_repair_enabled,
        "automatic_compatibility_correction_absent": not source.diagnostics.automatic_compatibility_correction_enabled,
        "silent_compatibility_fallback_absent": not source.diagnostics.silent_compatibility_fallback_enabled,
        "automatic_recovery_absent": not source.diagnostics.automatic_recovery_enabled,
        "fail_visible_warning_count": (
            len(source.blocked_state_visibility.blocked_transition_ids)
            + len(source.blocked_state_visibility.schema_version_discontinuity_visibility)
            + len(source.blocked_state_visibility.schema_lineage_discontinuity_visibility)
            + len(source.blocked_state_visibility.schema_provenance_discontinuity_visibility)
            + len(source.blocked_state_visibility.schema_replay_discontinuity_visibility)
            + len(source.blocked_state_visibility.schema_rollback_discontinuity_visibility)
            + len(source.blocked_state_visibility.circular_schema_ancestry_visibility)
            + len(source.unsupported_state_visibility.unsupported_node_ids)
            + len(source.unsupported_state_visibility.unsupported_transition_ids)
            + len(source.unsupported_state_visibility.stale_transition_ids)
            + len(source.unsupported_state_visibility.prohibited_transition_ids)
            + len(source.unsupported_state_visibility.prohibited_schema_domains)
            + len(source.unsupported_state_visibility.failure_visibility)
        ),
    }
