"""Integrity, equality, and continuity helpers for v4.1 refresh manifests.

Integrity checks are descriptive validation only. They do not remediate,
authorize, execute, recover, roll back, or mutate refresh manifest evidence.
"""

from __future__ import annotations

from typing import Any

from .refresh_manifest_diagnostics import enabled_refresh_manifest_capability_flags
from .refresh_manifest_models import (
    RefreshManifest,
    RefreshManifestIdentity,
    default_refresh_manifest,
    default_refresh_manifest_identity,
)
from .refresh_manifest_serialization import (
    export_refresh_manifest,
    export_refresh_manifest_identity,
    serialize_refresh_manifest,
    serialize_refresh_manifest_identity,
    stable_serialize,
)
from .refresh_manifest_visibility import validate_refresh_manifest_visibility


def refresh_manifest_identity_key(identity: RefreshManifestIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.manifest_id,
            identity.manifest_version,
            identity.source_bundle_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def refresh_manifest_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def refresh_manifest_identities_equal(left: RefreshManifestIdentity, right: RefreshManifestIdentity) -> bool:
    return serialize_refresh_manifest_identity(left) == serialize_refresh_manifest_identity(right)


def refresh_manifests_equal(left: RefreshManifest, right: RefreshManifest) -> bool:
    return serialize_refresh_manifest(left) == serialize_refresh_manifest(right)


def normalize_refresh_manifest_identity(identity: RefreshManifestIdentity) -> RefreshManifestIdentity:
    exported = export_refresh_manifest_identity(identity)
    return RefreshManifestIdentity(**exported)


def refresh_manifest_identity_normalization_report(identity: RefreshManifestIdentity) -> dict[str, object]:
    normalized = normalize_refresh_manifest_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": refresh_manifest_identity_key(normalized),
        "normalized_identity": export_refresh_manifest_identity(normalized),
        "field_count": len(export_refresh_manifest_identity(normalized)),
        "omitted_field_count": 0,
        "silent_correction_enabled": False,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
        "refresh_execution_enabled": normalized.refresh_execution_enabled,
    }


def validate_refresh_manifest_provenance_continuity(manifest: RefreshManifest) -> dict[str, object]:
    provenance_reference = manifest.identity.provenance_reference
    source_refs = tuple(record.provenance_reference for record in manifest.source_lineage)
    extraction_refs = tuple(record.provenance_reference for record in manifest.extraction_lineage)
    patch_refs = tuple(record.provenance_reference for record in manifest.patch_lineage)
    continuity_refs = manifest.continuity_metadata.provenance_continuity_references
    provenance_visible = provenance_reference in source_refs + extraction_refs + patch_refs + continuity_refs
    no_inferred_provenance = all(not record.inferred_source_allowed for record in manifest.source_lineage)
    no_hidden_source_resolution = all(
        not record.hidden_source_resolution_enabled for record in manifest.source_lineage
    )
    return {
        "valid": (
            provenance_visible
            and no_inferred_provenance
            and no_hidden_source_resolution
            and manifest.continuity_metadata.provenance_continuity_preserved
        ),
        "provenance_reference": provenance_reference,
        "source_provenance_reference_count": len(source_refs),
        "extraction_provenance_reference_count": len(extraction_refs),
        "patch_provenance_reference_count": len(patch_refs),
        "provenance_continuity_reference_count": len(continuity_refs),
        "provenance_visible": provenance_visible,
        "provenance_continuity_preserved": manifest.continuity_metadata.provenance_continuity_preserved,
        "no_inferred_provenance": no_inferred_provenance,
        "hidden_source_resolution_absent": no_hidden_source_resolution,
    }


def validate_refresh_manifest_lineage_continuity(manifest: RefreshManifest) -> dict[str, object]:
    lineage_reference = manifest.identity.lineage_reference
    source_lineage_count = len(manifest.source_lineage)
    extraction_lineage_count = len(manifest.extraction_lineage)
    patch_lineage_count = len(manifest.patch_lineage)
    lineage_continuity_refs = manifest.continuity_metadata.lineage_continuity_references
    rollback_refs = manifest.continuity_metadata.rollback_references + manifest.rollback_metadata.rollback_evidence_references
    replay_refs = manifest.continuity_metadata.replay_references + manifest.replay_metadata.replay_evidence_references
    hidden_lineage_resolution_count = sum(
        1
        for record in (*manifest.source_lineage, *manifest.extraction_lineage, *manifest.patch_lineage)
        if getattr(record, "hidden_source_resolution_enabled", False)
        or getattr(record, "hidden_extraction_fallback_enabled", False)
        or getattr(record, "hidden_patch_resolution_enabled", False)
    )
    return {
        "valid": (
            lineage_reference in lineage_continuity_refs
            and source_lineage_count > 0
            and extraction_lineage_count > 0
            and patch_lineage_count > 0
            and manifest.continuity_metadata.lineage_continuity_preserved
            and manifest.continuity_metadata.replay_safe
            and manifest.continuity_metadata.rollback_safe
            and hidden_lineage_resolution_count == 0
        ),
        "lineage_reference": lineage_reference,
        "source_lineage_count": source_lineage_count,
        "extraction_lineage_count": extraction_lineage_count,
        "patch_lineage_count": patch_lineage_count,
        "lineage_continuity_reference_count": len(lineage_continuity_refs),
        "rollback_reference_count": len(rollback_refs),
        "replay_reference_count": len(replay_refs),
        "lineage_continuity_preserved": manifest.continuity_metadata.lineage_continuity_preserved,
        "replay_safe": manifest.continuity_metadata.replay_safe and manifest.replay_metadata.replay_safe,
        "rollback_safe": manifest.continuity_metadata.rollback_safe and manifest.rollback_metadata.rollback_safe,
        "hidden_lineage_resolution_count": hidden_lineage_resolution_count,
    }


def validate_refresh_manifest_non_execution(manifest: RefreshManifest) -> dict[str, object]:
    enabled_flags = enabled_refresh_manifest_capability_flags(manifest)
    return {
        "valid": len(enabled_flags) == 0 and manifest.non_executable and manifest.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": manifest.non_executable,
        "descriptive_only": manifest.descriptive_only,
        "refresh_execution_absent": not manifest.refresh_execution_enabled,
        "orchestration_absent": not manifest.orchestration_enabled,
        "deployment_execution_absent": not manifest.deployment_execution_enabled,
        "automatic_refresh_absent": not manifest.automatic_refresh_enabled,
        "automatic_migration_absent": not manifest.automatic_migration_enabled,
        "planner_integration_absent": not manifest.planner_integration_enabled,
        "production_consumption_absent": not manifest.production_consumption_enabled,
        "remediation_absent": not manifest.remediation_enabled,
        "runtime_mutation_absent": not manifest.runtime_mutation_enabled and not manifest.mutation_enabled,
        "recommendation_absent": not manifest.recommendation_enabled,
        "ranking_absent": not manifest.ranking_enabled,
        "scoring_absent": not manifest.scoring_enabled,
        "selection_absent": not manifest.selection_enabled,
        "authorization_absent": not manifest.authorization_enabled,
        "approval_absent": not manifest.approval_enabled,
        "automatic_rollback_absent": not manifest.automatic_rollback_enabled,
        "automatic_recovery_absent": not manifest.automatic_recovery_enabled,
        "hidden_operational_behavior_absent": not manifest.hidden_operational_behavior_enabled,
        "implicit_execution_pathway_absent": not manifest.implicit_execution_pathway_enabled,
        "silent_fallback_absent": not manifest.silent_fallback_enabled,
    }


def validate_refresh_manifest_integrity(manifest: RefreshManifest | None = None) -> dict[str, object]:
    source = manifest or default_refresh_manifest()
    visibility = validate_refresh_manifest_visibility(source)
    provenance = validate_refresh_manifest_provenance_continuity(source)
    lineage = validate_refresh_manifest_lineage_continuity(source)
    non_execution = validate_refresh_manifest_non_execution(source)
    return {
        "valid": visibility["valid"] and provenance["valid"] and lineage["valid"] and non_execution["valid"],
        "visibility_valid": visibility["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "non_execution_valid": non_execution["valid"],
        "visibility_validation": visibility,
        "provenance_continuity_validation": provenance,
        "lineage_continuity_validation": lineage,
        "non_execution_validation": non_execution,
        "identity_normalization": refresh_manifest_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_manifest(source)),
    }


def build_default_refresh_manifest_identity() -> RefreshManifestIdentity:
    return default_refresh_manifest_identity()
