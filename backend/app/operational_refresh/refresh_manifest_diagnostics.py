"""Deterministic diagnostics visibility for v4.1 refresh manifest foundations."""

from __future__ import annotations

from typing import Any

from .refresh_manifest_hashing import hash_refresh_manifest, hash_refresh_manifest_diagnostics
from .refresh_manifest_models import RefreshManifest, default_refresh_manifest
from .refresh_manifest_visibility import validate_refresh_manifest_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "deployment_execution_enabled",
    "automatic_refresh_enabled",
    "automatic_migration_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "mutation_enabled",
    "runtime_mutation_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "authorization_enabled",
    "approval_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "hidden_operational_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_fallback_enabled",
    "execution_enabled",
    "extraction_execution_enabled",
    "patch_execution_enabled",
    "automatic_source_refresh_enabled",
    "automatic_extraction_enabled",
    "automatic_dependency_refresh_enabled",
    "automatic_validation_execution_enabled",
    "schema_migration_enabled",
    "trust_inference_enabled",
    "live_replay_enabled",
    "runtime_execution_enabled",
    "recovery_execution_enabled",
)


def refresh_manifest_capability_flags(manifest: RefreshManifest) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        manifest,
        manifest.identity,
        manifest.continuity_metadata,
        manifest.replay_metadata,
        manifest.rollback_metadata,
        manifest.governance_visibility,
        *manifest.states,
        *manifest.source_lineage,
        *manifest.extraction_lineage,
        *manifest.patch_lineage,
        *manifest.schema_version_visibility,
        *manifest.dependency_visibility,
        *manifest.trust_visibility,
        *manifest.validation_visibility,
        *manifest.prohibited_domain_visibility,
        *manifest.unsupported_state_visibility,
        *manifest.diagnostics_visibility,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_refresh_manifest_capability_flags(manifest: RefreshManifest) -> dict[str, bool]:
    return {key: value for key, value in refresh_manifest_capability_flags(manifest).items() if value}


def build_refresh_manifest_diagnostics(manifest: RefreshManifest | None = None) -> dict[str, Any]:
    source = manifest or default_refresh_manifest()
    visibility = validate_refresh_manifest_visibility(source)
    enabled_flags = enabled_refresh_manifest_capability_flags(source)
    diagnostic_hashes = [
        hash_refresh_manifest_diagnostics(record) for record in source.diagnostics_visibility
    ]
    unsupported_state_ids = tuple(
        item for record in source.unsupported_state_visibility for item in record.unsupported_states
    )
    unknown_state_ids = tuple(item for record in source.unsupported_state_visibility for item in record.unknown_states)
    blocked_state_ids = tuple(item for record in source.unsupported_state_visibility for item in record.blocked_states)
    prohibited_state_ids = tuple(
        item for record in source.unsupported_state_visibility for item in record.prohibited_states
    )
    stale_state_ids = tuple(item for record in source.unsupported_state_visibility for item in record.stale_states)
    prohibited_domains = tuple(
        item for record in source.prohibited_domain_visibility for item in record.prohibited_domains
    )
    return {
        "manifest_hash": hash_refresh_manifest(source),
        "diagnostics_hashes": diagnostic_hashes,
        "visibility_validation": visibility,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "unsupported_state_ids": sorted(unsupported_state_ids),
        "unknown_state_ids": sorted(unknown_state_ids),
        "blocked_state_ids": sorted(blocked_state_ids),
        "prohibited_state_ids": sorted(prohibited_state_ids),
        "stale_state_ids": sorted(stale_state_ids),
        "prohibited_domains": sorted(prohibited_domains),
        "warning_visibility": sorted(
            item for record in source.diagnostics_visibility for item in record.warning_visibility
        ),
        "blocker_visibility": sorted(
            item for record in source.diagnostics_visibility for item in record.blocker_visibility
        ),
        "fail_visible_warning_count": (
            len(unsupported_state_ids)
            + len(unknown_state_ids)
            + len(blocked_state_ids)
            + len(prohibited_state_ids)
            + len(stale_state_ids)
            + len(prohibited_domains)
        ),
        "diagnostics_visible": all(record.diagnostics_visible for record in source.diagnostics_visibility),
        "diagnostics_are_descriptive_only": all(record.descriptive_only for record in source.diagnostics_visibility),
        "remediation_absent": all(not record.remediation_enabled for record in source.diagnostics_visibility),
        "silent_fallback_absent": all(not record.silent_fallback_enabled for record in source.diagnostics_visibility),
        "automatic_recovery_absent": all(not record.automatic_recovery_enabled for record in source.diagnostics_visibility),
    }
