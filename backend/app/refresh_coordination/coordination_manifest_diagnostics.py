"""Fail-visible diagnostics for v4.2 coordination manifest foundations.

Diagnostics are descriptive governance evidence only. They aggregate visible
coordination blockers and prohibited states without remediation, authorization,
execution, or runtime mutation.
"""

from __future__ import annotations

from typing import Any

from .coordination_manifest_hashing import (
    hash_coordination_continuity,
    hash_coordination_dependency,
    hash_coordination_lineage,
    hash_coordination_manifest,
)
from .coordination_manifest_models import (
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_UNKNOWN,
    COORDINATION_STATE_UNSUPPORTED,
    COORDINATION_STATES,
    CoordinationDependencyReference,
    CoordinationManifest,
    default_coordination_manifest,
)
from .coordination_manifest_serialization import serialize_coordination_manifest


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "dependency_resolution_enabled",
    "authorization_enabled",
    "approval_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "recovery_execution_enabled",
    "lineage_repair_enabled",
    "inferred_lineage_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_dependency_resolution_enabled",
    "hidden_unsupported_state_resolution_enabled",
    "hidden_operational_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "hidden_fallback_enabled",
    "automatic_refresh_enabled",
)


def count_coordination_dependency_states(
    dependencies: tuple[CoordinationDependencyReference, ...] | list[CoordinationDependencyReference],
) -> dict[str, int]:
    counts = {state: 0 for state in COORDINATION_STATES}
    counts["invalid"] = 0
    for dependency in dependencies:
        if dependency.dependency_state in counts:
            counts[dependency.dependency_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def aggregate_prohibited_states(manifest: CoordinationManifest) -> tuple[str, ...]:
    dependency_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_PROHIBITED
    )
    return tuple(sorted(set(dependency_ids + manifest.prohibited_state_visibility.prohibited_states)))


def aggregate_unsupported_states(manifest: CoordinationManifest) -> tuple[str, ...]:
    dependency_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_UNSUPPORTED
    )
    return tuple(sorted(set(dependency_ids + manifest.unsupported_state_visibility.unsupported_states)))


def aggregate_blocked_coordination(manifest: CoordinationManifest) -> tuple[str, ...]:
    dependency_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_BLOCKED
    )
    return tuple(sorted(set(dependency_ids + manifest.unsupported_state_visibility.blocked_states)))


def coordination_manifest_capability_flags(manifest: CoordinationManifest) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        manifest,
        manifest.identity,
        manifest.metadata,
        manifest.prohibited_state_visibility,
        manifest.unsupported_state_visibility,
        manifest.governance_visibility,
        *manifest.dependency_references,
        *manifest.lineage_references,
        *manifest.continuity_references,
        *manifest.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_manifest_capability_flags(manifest: CoordinationManifest) -> dict[str, bool]:
    return {key: value for key, value in coordination_manifest_capability_flags(manifest).items() if value}


def coordination_manifest_identity_key(manifest: CoordinationManifest) -> str:
    identity = manifest.identity
    return "|".join(
        (
            identity.schema_version,
            identity.coordination_cycle_id,
            identity.manifest_id,
            identity.manifest_version,
            identity.source_readiness_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def coordination_manifests_equal(left: CoordinationManifest, right: CoordinationManifest) -> bool:
    return serialize_coordination_manifest(left) == serialize_coordination_manifest(right)


def validate_coordination_lineage_continuity(manifest: CoordinationManifest) -> dict[str, object]:
    lineage_ids = tuple(reference.lineage_id for reference in manifest.lineage_references)
    lineage_evidence_count = sum(len(reference.lineage_evidence_references) for reference in manifest.lineage_references)
    hidden_lineage_resolution_count = sum(
        1
        for reference in manifest.lineage_references
        if reference.hidden_lineage_resolution_enabled
        or reference.inferred_lineage_enabled
        or reference.lineage_repair_enabled
        or reference.runtime_mutation_enabled
    )
    lineage_preserved = all(reference.lineage_continuity_preserved for reference in manifest.lineage_references)
    provenance_preserved = all(reference.provenance_continuity_preserved for reference in manifest.lineage_references)
    identity_lineage_visible = manifest.identity.lineage_reference in manifest.metadata.evidence_references
    return {
        "valid": (
            len(lineage_ids) > 0
            and lineage_preserved
            and provenance_preserved
            and identity_lineage_visible
            and hidden_lineage_resolution_count == 0
        ),
        "lineage_reference": manifest.identity.lineage_reference,
        "lineage_reference_count": len(lineage_ids),
        "lineage_evidence_reference_count": lineage_evidence_count,
        "lineage_continuity_preserved": lineage_preserved,
        "provenance_continuity_preserved": provenance_preserved,
        "identity_lineage_visible": identity_lineage_visible,
        "hidden_lineage_resolution_count": hidden_lineage_resolution_count,
    }


def validate_coordination_continuity_visibility(manifest: CoordinationManifest) -> dict[str, object]:
    replay_safe = all(reference.replay_safe for reference in manifest.continuity_references)
    rollback_safe = all(reference.rollback_safe for reference in manifest.continuity_references)
    provenance_safe = all(reference.provenance_safe for reference in manifest.continuity_references)
    lineage_safe = all(reference.lineage_safe for reference in manifest.continuity_references)
    continuity_preserved = all(reference.continuity_preserved for reference in manifest.continuity_references)
    continuity_visible = all(reference.continuity_visible for reference in manifest.continuity_references)
    corrective_count = sum(
        1
        for reference in manifest.continuity_references
        if reference.automatic_correction_enabled
        or reference.automatic_rollback_enabled
        or reference.recovery_execution_enabled
        or reference.refresh_execution_enabled
        or reference.orchestration_execution_enabled
        or reference.runtime_mutation_enabled
    )
    return {
        "valid": (
            len(manifest.continuity_references) > 0
            and replay_safe
            and rollback_safe
            and provenance_safe
            and lineage_safe
            and continuity_preserved
            and continuity_visible
            and corrective_count == 0
        ),
        "continuity_reference": manifest.identity.continuity_reference,
        "continuity_reference_count": len(manifest.continuity_references),
        "continuity_preserved": continuity_preserved,
        "continuity_visible": continuity_visible,
        "replay_safe": replay_safe,
        "rollback_safe": rollback_safe,
        "provenance_safe": provenance_safe,
        "lineage_safe": lineage_safe,
        "corrective_continuity_count": corrective_count,
    }


def validate_coordination_manifest_visibility(manifest: CoordinationManifest) -> dict[str, object]:
    unsupported_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_BLOCKED
    )
    prohibited_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_PROHIBITED
    )
    stale_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_STALE
    )
    unknown_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state == COORDINATION_STATE_UNKNOWN
    )
    invalid_dependency_ids = tuple(
        dependency.dependency_id
        for dependency in manifest.dependency_references
        if dependency.dependency_state not in COORDINATION_STATES
    )
    unsupported_visible = set(unsupported_ids).issubset(set(manifest.unsupported_state_visibility.unsupported_states))
    blocked_visible = set(blocked_ids).issubset(set(manifest.unsupported_state_visibility.blocked_states))
    stale_visible = set(stale_ids).issubset(set(manifest.unsupported_state_visibility.stale_states))
    unknown_visible = set(unknown_ids).issubset(set(manifest.unsupported_state_visibility.unknown_states))
    prohibited_visible = set(prohibited_ids).issubset(set(manifest.prohibited_state_visibility.prohibited_states))
    prohibited_capabilities_visible = len(manifest.prohibited_state_visibility.prohibited_capabilities) == len(
        manifest.prohibited_state_visibility.blocked_reason_visibility
    )
    hidden_dependency_count = sum(
        1 for dependency in manifest.dependency_references if dependency.hidden_dependency_resolution_enabled
    )
    corrective_dependency_count = sum(
        1
        for dependency in manifest.dependency_references
        if dependency.dependency_resolution_enabled
        or dependency.automatic_refresh_enabled
        or dependency.refresh_execution_enabled
        or dependency.orchestration_execution_enabled
        or dependency.production_consumption_enabled
    )
    hidden_diagnostic_count = sum(1 for diagnostic in manifest.diagnostics if diagnostic.hidden)
    corrective_diagnostic_count = sum(
        1
        for diagnostic in manifest.diagnostics
        if diagnostic.remediation_enabled
        or diagnostic.automatic_correction_enabled
        or diagnostic.automatic_rollback_enabled
        or diagnostic.dependency_resolution_enabled
        or diagnostic.authorization_enabled
        or diagnostic.approval_enabled
        or diagnostic.execution_enabled
        or diagnostic.refresh_execution_enabled
        or diagnostic.orchestration_execution_enabled
        or diagnostic.runtime_mutation_enabled
    )
    return {
        "valid": (
            unsupported_visible
            and blocked_visible
            and stale_visible
            and unknown_visible
            and prohibited_visible
            and prohibited_capabilities_visible
            and len(invalid_dependency_ids) == 0
            and hidden_dependency_count == 0
            and corrective_dependency_count == 0
            and hidden_diagnostic_count == 0
            and corrective_diagnostic_count == 0
        ),
        "dependency_state_counts": count_coordination_dependency_states(manifest.dependency_references),
        "unsupported_state_visibility_count": len(manifest.unsupported_state_visibility.unsupported_states),
        "unknown_state_visibility_count": len(manifest.unsupported_state_visibility.unknown_states),
        "blocked_state_visibility_count": len(manifest.unsupported_state_visibility.blocked_states),
        "stale_state_visibility_count": len(manifest.unsupported_state_visibility.stale_states),
        "prohibited_state_visibility_count": len(manifest.prohibited_state_visibility.prohibited_states),
        "prohibited_capability_visibility_count": len(manifest.prohibited_state_visibility.prohibited_capabilities),
        "blocked_reason_visibility_count": len(manifest.prohibited_state_visibility.blocked_reason_visibility),
        "unsupported_states_visible": unsupported_visible,
        "blocked_states_visible": blocked_visible,
        "stale_states_visible": stale_visible,
        "unknown_states_visible": unknown_visible,
        "prohibited_states_visible": prohibited_visible,
        "prohibited_capabilities_visible": prohibited_capabilities_visible,
        "invalid_dependency_ids": invalid_dependency_ids,
        "hidden_dependency_count": hidden_dependency_count,
        "corrective_dependency_count": corrective_dependency_count,
        "hidden_diagnostic_count": hidden_diagnostic_count,
        "corrective_diagnostic_count": corrective_diagnostic_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in manifest.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in manifest.diagnostics),
    }


def validate_coordination_manifest_non_execution(manifest: CoordinationManifest) -> dict[str, object]:
    enabled_flags = enabled_coordination_manifest_capability_flags(manifest)
    return {
        "valid": len(enabled_flags) == 0 and manifest.non_executable and manifest.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": manifest.non_executable,
        "descriptive_only": manifest.descriptive_only,
        "orchestration_execution_disabled": not manifest.orchestration_execution_enabled,
        "refresh_execution_disabled": not manifest.refresh_execution_enabled,
        "planner_integration_disabled": not manifest.planner_integration_enabled,
        "production_consumption_disabled": (
            not manifest.production_consumption_enabled and not manifest.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not manifest.runtime_mutation_enabled,
        "remediation_disabled": not manifest.remediation_enabled,
        "automatic_correction_disabled": not manifest.automatic_correction_enabled,
        "automatic_rollback_disabled": not manifest.automatic_rollback_enabled,
        "dependency_resolution_disabled": not manifest.dependency_resolution_enabled,
        "authorization_disabled": not manifest.authorization_enabled,
        "approval_disabled": not manifest.approval_enabled,
        "recommendation_disabled": not manifest.recommendation_enabled,
        "ranking_disabled": not manifest.ranking_enabled,
        "scoring_disabled": not manifest.scoring_enabled,
        "selection_disabled": not manifest.selection_enabled,
        "operational_execution_disabled": not manifest.operational_execution_enabled,
        "hidden_operational_behavior_absent": not manifest.hidden_operational_behavior_enabled,
        "implicit_execution_pathway_absent": not manifest.implicit_execution_pathway_enabled,
    }


def build_coordination_manifest_diagnostics(manifest: CoordinationManifest | None = None) -> dict[str, Any]:
    source = manifest or default_coordination_manifest()
    visibility = validate_coordination_manifest_visibility(source)
    lineage = validate_coordination_lineage_continuity(source)
    continuity = validate_coordination_continuity_visibility(source)
    non_execution = validate_coordination_manifest_non_execution(source)
    enabled_flags = enabled_coordination_manifest_capability_flags(source)
    return {
        "manifest_hash": hash_coordination_manifest(source),
        "dependency_hashes": [
            hash_coordination_dependency(reference) for reference in source.dependency_references
        ],
        "lineage_hashes": [hash_coordination_lineage(reference) for reference in source.lineage_references],
        "continuity_hashes": [
            hash_coordination_continuity(reference) for reference in source.continuity_references
        ],
        "visibility_validation": visibility,
        "lineage_continuity_validation": lineage,
        "continuity_visibility_validation": continuity,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "prohibited_state_ids": aggregate_prohibited_states(source),
        "unsupported_state_ids": aggregate_unsupported_states(source),
        "blocked_coordination_ids": aggregate_blocked_coordination(source),
        "stale_state_ids": tuple(
            sorted(
                dependency.dependency_id
                for dependency in source.dependency_references
                if dependency.dependency_state == COORDINATION_STATE_STALE
            )
        ),
        "unknown_state_ids": tuple(sorted(source.unsupported_state_visibility.unknown_states)),
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "remediation_absent": all(not diagnostic.remediation_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(not diagnostic.authorization_enabled for diagnostic in source.diagnostics),
        "approval_absent": all(not diagnostic.approval_enabled for diagnostic in source.diagnostics),
        "execution_absent": all(
            not diagnostic.execution_enabled
            and not diagnostic.refresh_execution_enabled
            and not diagnostic.orchestration_execution_enabled
            for diagnostic in source.diagnostics
        ),
        "fail_visible_warning_count": (
            visibility["unsupported_state_visibility_count"]
            + visibility["blocked_state_visibility_count"]
            + visibility["stale_state_visibility_count"]
            + visibility["unknown_state_visibility_count"]
            + visibility["prohibited_state_visibility_count"]
        ),
    }
