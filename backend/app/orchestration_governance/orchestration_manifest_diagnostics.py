"""Fail-visible diagnostics for v4.3 orchestration manifest foundations.

Diagnostics are descriptive governance evidence only. They aggregate visible
orchestration blockers, unsupported states, prohibited states, and metadata
warnings without remediation, authorization, execution, routing, scheduling,
sequencing, dependency resolution, inference, repair, rollback, or mutation.
"""

from __future__ import annotations

from typing import Any

from .orchestration_manifest_hashing import (
    hash_orchestration_boundary_visibility,
    hash_orchestration_capability_visibility,
    hash_orchestration_continuity_metadata,
    hash_orchestration_explainability_summary,
    hash_orchestration_manifest,
)
from .orchestration_manifest_models import (
    ORCHESTRATION_STATE_BLOCKED,
    ORCHESTRATION_STATE_CONFLICTING_METADATA,
    ORCHESTRATION_STATE_MISSING_METADATA,
    ORCHESTRATION_STATE_PROHIBITED,
    ORCHESTRATION_STATE_STALE_METADATA,
    ORCHESTRATION_STATE_UNSUPPORTED,
    ORCHESTRATION_STATES,
    OrchestrationCapabilityVisibility,
    OrchestrationManifest,
    default_orchestration_manifest,
)
from .orchestration_manifest_serialization import serialize_orchestration_manifest


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "runtime_execution_enabled",
    "routing_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "orchestration_remediation_enabled",
    "orchestration_repair_enabled",
    "orchestration_inference_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "runtime_mutation_enabled",
    "operational_state_mutation_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "orchestration_engine_enabled",
    "state_machine_execution_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
)


def count_orchestration_capability_states(
    capabilities: tuple[OrchestrationCapabilityVisibility, ...] | list[OrchestrationCapabilityVisibility],
) -> dict[str, int]:
    counts = {state: 0 for state in ORCHESTRATION_STATES}
    counts["invalid"] = 0
    for capability in capabilities:
        if capability.visibility_state in counts:
            counts[capability.visibility_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def aggregate_prohibited_states(manifest: OrchestrationManifest) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_PROHIBITED
    )
    return tuple(sorted(set(capability_ids + manifest.prohibited_state_visibility.prohibited_states)))


def aggregate_unsupported_states(manifest: OrchestrationManifest) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_UNSUPPORTED
    )
    return tuple(sorted(set(capability_ids + manifest.unsupported_state_visibility.unsupported_states)))


def aggregate_blocked_states(manifest: OrchestrationManifest) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_BLOCKED
    )
    return tuple(sorted(set(capability_ids + manifest.unsupported_state_visibility.blocked_states)))


def aggregate_missing_metadata_states(manifest: OrchestrationManifest) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_MISSING_METADATA
    )
    return tuple(sorted(set(capability_ids + manifest.unsupported_state_visibility.missing_metadata_states)))


def aggregate_conflicting_metadata_states(manifest: OrchestrationManifest) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_CONFLICTING_METADATA
    )
    return tuple(sorted(set(capability_ids + manifest.unsupported_state_visibility.conflicting_metadata_states)))


def aggregate_stale_metadata_states(manifest: OrchestrationManifest) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_STALE_METADATA
    )
    return tuple(sorted(set(capability_ids + manifest.unsupported_state_visibility.stale_metadata_states)))


def orchestration_manifest_capability_flags(manifest: OrchestrationManifest) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        manifest,
        manifest.identity,
        manifest.metadata,
        manifest.prohibited_state_visibility,
        manifest.unsupported_state_visibility,
        *manifest.capability_visibility,
        *manifest.boundary_visibility,
        *manifest.continuity_metadata,
        *manifest.diagnostics,
        *manifest.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_orchestration_manifest_capability_flags(manifest: OrchestrationManifest) -> dict[str, bool]:
    return {key: value for key, value in orchestration_manifest_capability_flags(manifest).items() if value}


def orchestration_manifest_identity_key(manifest: OrchestrationManifest) -> str:
    identity = manifest.identity
    return "|".join(
        (
            identity.schema_version,
            identity.orchestration_domain_id,
            identity.manifest_id,
            identity.manifest_version,
            identity.source_readiness_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def orchestration_manifests_equal(left: OrchestrationManifest, right: OrchestrationManifest) -> bool:
    return serialize_orchestration_manifest(left) == serialize_orchestration_manifest(right)


def validate_orchestration_manifest_visibility(manifest: OrchestrationManifest) -> dict[str, object]:
    unsupported_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_BLOCKED
    )
    prohibited_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_PROHIBITED
    )
    missing_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_MISSING_METADATA
    )
    conflicting_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_CONFLICTING_METADATA
    )
    stale_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state == ORCHESTRATION_STATE_STALE_METADATA
    )
    invalid_capability_ids = tuple(
        capability.capability_id
        for capability in manifest.capability_visibility
        if capability.visibility_state not in ORCHESTRATION_STATES
    )
    unsupported_visible = set(unsupported_ids).issubset(set(manifest.unsupported_state_visibility.unsupported_states))
    blocked_visible = set(blocked_ids).issubset(set(manifest.unsupported_state_visibility.blocked_states))
    missing_visible = set(missing_ids).issubset(set(manifest.unsupported_state_visibility.missing_metadata_states))
    conflicting_visible = set(conflicting_ids).issubset(
        set(manifest.unsupported_state_visibility.conflicting_metadata_states)
    )
    stale_visible = set(stale_ids).issubset(set(manifest.unsupported_state_visibility.stale_metadata_states))
    prohibited_visible = set(prohibited_ids).issubset(set(manifest.prohibited_state_visibility.prohibited_states))
    prohibited_capabilities_visible = len(manifest.prohibited_state_visibility.prohibited_capabilities) == len(
        manifest.prohibited_state_visibility.blocked_reason_visibility
    )
    hidden_capability_count = sum(1 for capability in manifest.capability_visibility if capability.hidden)
    corrective_capability_count = sum(
        1
        for capability in manifest.capability_visibility
        if capability.orchestration_execution_enabled
        or capability.runtime_execution_enabled
        or capability.routing_execution_enabled
        or capability.scheduling_execution_enabled
        or capability.sequencing_execution_enabled
        or capability.dependency_resolution_enabled
        or capability.orchestration_remediation_enabled
        or capability.orchestration_repair_enabled
        or capability.orchestration_inference_enabled
        or capability.orchestration_authorization_enabled
        or capability.readiness_approval_enabled
        or capability.planner_integration_enabled
        or capability.production_consumption_enabled
        or capability.automatic_correction_enabled
        or capability.automatic_rollback_enabled
        or capability.runtime_mutation_enabled
        or capability.operational_state_mutation_enabled
    )
    hidden_diagnostic_count = sum(1 for diagnostic in manifest.diagnostics if diagnostic.hidden)
    corrective_diagnostic_count = sum(
        1
        for diagnostic in manifest.diagnostics
        if diagnostic.remediation_enabled
        or diagnostic.automatic_correction_enabled
        or diagnostic.automatic_rollback_enabled
        or diagnostic.dependency_resolution_enabled
        or diagnostic.orchestration_remediation_enabled
        or diagnostic.orchestration_repair_enabled
        or diagnostic.orchestration_inference_enabled
        or diagnostic.orchestration_authorization_enabled
        or diagnostic.readiness_approval_enabled
        or diagnostic.authorization_enabled
        or diagnostic.approval_enabled
        or diagnostic.execution_enabled
        or diagnostic.orchestration_execution_enabled
        or diagnostic.runtime_execution_enabled
        or diagnostic.routing_execution_enabled
        or diagnostic.scheduling_execution_enabled
        or diagnostic.sequencing_execution_enabled
        or diagnostic.planner_integration_enabled
        or diagnostic.production_consumption_enabled
        or diagnostic.runtime_mutation_enabled
        or diagnostic.operational_state_mutation_enabled
        or diagnostic.recommendation_enabled
        or diagnostic.ranking_enabled
        or diagnostic.scoring_enabled
        or diagnostic.selection_enabled
    )
    return {
        "valid": (
            unsupported_visible
            and blocked_visible
            and missing_visible
            and conflicting_visible
            and stale_visible
            and prohibited_visible
            and prohibited_capabilities_visible
            and len(invalid_capability_ids) == 0
            and hidden_capability_count == 0
            and corrective_capability_count == 0
            and hidden_diagnostic_count == 0
            and corrective_diagnostic_count == 0
        ),
        "capability_state_counts": count_orchestration_capability_states(manifest.capability_visibility),
        "unsupported_state_visibility_count": len(manifest.unsupported_state_visibility.unsupported_states),
        "blocked_state_visibility_count": len(manifest.unsupported_state_visibility.blocked_states),
        "missing_metadata_visibility_count": len(manifest.unsupported_state_visibility.missing_metadata_states),
        "conflicting_metadata_visibility_count": len(manifest.unsupported_state_visibility.conflicting_metadata_states),
        "stale_metadata_visibility_count": len(manifest.unsupported_state_visibility.stale_metadata_states),
        "unknown_state_visibility_count": len(manifest.unsupported_state_visibility.unknown_states),
        "prohibited_state_visibility_count": len(manifest.prohibited_state_visibility.prohibited_states),
        "prohibited_capability_visibility_count": len(manifest.prohibited_state_visibility.prohibited_capabilities),
        "blocked_reason_visibility_count": len(manifest.prohibited_state_visibility.blocked_reason_visibility),
        "unsupported_states_visible": unsupported_visible,
        "blocked_states_visible": blocked_visible,
        "missing_metadata_visible": missing_visible,
        "conflicting_metadata_visible": conflicting_visible,
        "stale_metadata_visible": stale_visible,
        "unknown_states_visible": len(manifest.unsupported_state_visibility.unknown_states) > 0,
        "prohibited_states_visible": prohibited_visible,
        "prohibited_capabilities_visible": prohibited_capabilities_visible,
        "invalid_capability_ids": invalid_capability_ids,
        "hidden_capability_count": hidden_capability_count,
        "corrective_capability_count": corrective_capability_count,
        "hidden_diagnostic_count": hidden_diagnostic_count,
        "corrective_diagnostic_count": corrective_diagnostic_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in manifest.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in manifest.diagnostics),
    }


def validate_orchestration_continuity_metadata(manifest: OrchestrationManifest) -> dict[str, object]:
    replay_safe = all(metadata.replay_safe for metadata in manifest.continuity_metadata)
    rollback_safe = all(metadata.rollback_safe for metadata in manifest.continuity_metadata)
    provenance_safe = all(metadata.provenance_continuity_preserved for metadata in manifest.continuity_metadata)
    lineage_safe = all(metadata.lineage_continuity_preserved for metadata in manifest.continuity_metadata)
    explainability_safe = all(
        metadata.explainability_continuity_preserved for metadata in manifest.continuity_metadata
    )
    continuity_visible = all(metadata.continuity_visible for metadata in manifest.continuity_metadata)
    corrective_count = sum(
        1
        for metadata in manifest.continuity_metadata
        if metadata.automatic_correction_enabled
        or metadata.automatic_rollback_enabled
        or metadata.orchestration_execution_enabled
        or metadata.runtime_execution_enabled
        or metadata.runtime_mutation_enabled
        or metadata.operational_state_mutation_enabled
    )
    return {
        "valid": (
            len(manifest.continuity_metadata) > 0
            and replay_safe
            and rollback_safe
            and provenance_safe
            and lineage_safe
            and explainability_safe
            and continuity_visible
            and corrective_count == 0
        ),
        "continuity_metadata_count": len(manifest.continuity_metadata),
        "replay_safe": replay_safe,
        "rollback_safe": rollback_safe,
        "provenance_continuity_preserved": provenance_safe,
        "lineage_continuity_preserved": lineage_safe,
        "explainability_continuity_preserved": explainability_safe,
        "continuity_visible": continuity_visible,
        "corrective_continuity_count": corrective_count,
    }


def validate_orchestration_explainability(manifest: OrchestrationManifest) -> dict[str, object]:
    categories = tuple(sorted(set(summary.category for summary in manifest.explainability_summaries)))
    required_categories = (
        "blocked_state",
        "unsupported_state",
        "prohibited_state",
        "capability_unavailable",
        "governance_boundary",
    )
    corrective_count = sum(
        1
        for summary in manifest.explainability_summaries
        if summary.recommendation_enabled
        or summary.ranking_enabled
        or summary.scoring_enabled
        or summary.selection_enabled
        or summary.remediation_enabled
        or summary.orchestration_execution_enabled
        or summary.runtime_execution_enabled
        or summary.runtime_mutation_enabled
    )
    return {
        "valid": (
            len(manifest.explainability_summaries) > 0
            and set(required_categories).issubset(set(categories))
            and all(summary.deterministic for summary in manifest.explainability_summaries)
            and all(summary.fail_visible for summary in manifest.explainability_summaries)
            and all(summary.descriptive_only for summary in manifest.explainability_summaries)
            and all(len(summary.affected_reference_ids) > 0 for summary in manifest.explainability_summaries)
            and corrective_count == 0
        ),
        "explainability_summary_count": len(manifest.explainability_summaries),
        "explainability_categories": categories,
        "required_categories": required_categories,
        "deterministic": all(summary.deterministic for summary in manifest.explainability_summaries),
        "fail_visible": all(summary.fail_visible for summary in manifest.explainability_summaries),
        "descriptive_only": all(summary.descriptive_only for summary in manifest.explainability_summaries),
        "corrective_explainability_count": corrective_count,
    }


def validate_orchestration_manifest_non_execution(manifest: OrchestrationManifest) -> dict[str, object]:
    enabled_flags = enabled_orchestration_manifest_capability_flags(manifest)
    return {
        "valid": len(enabled_flags) == 0 and manifest.non_executable and manifest.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": manifest.non_executable,
        "descriptive_only": manifest.descriptive_only,
        "orchestration_execution_disabled": not manifest.orchestration_execution_enabled,
        "runtime_execution_disabled": not manifest.runtime_execution_enabled,
        "routing_execution_disabled": not manifest.routing_execution_enabled,
        "scheduling_execution_disabled": not manifest.scheduling_execution_enabled,
        "sequencing_execution_disabled": not manifest.sequencing_execution_enabled,
        "dependency_resolution_disabled": not manifest.dependency_resolution_enabled,
        "orchestration_remediation_disabled": not manifest.orchestration_remediation_enabled,
        "orchestration_repair_disabled": not manifest.orchestration_repair_enabled,
        "orchestration_inference_disabled": not manifest.orchestration_inference_enabled,
        "orchestration_authorization_disabled": not manifest.orchestration_authorization_enabled,
        "readiness_approval_disabled": not manifest.readiness_approval_enabled,
        "planner_integration_disabled": not manifest.planner_integration_enabled,
        "production_consumption_disabled": not manifest.production_consumption_enabled,
        "automatic_correction_disabled": not manifest.automatic_correction_enabled,
        "automatic_rollback_disabled": not manifest.automatic_rollback_enabled,
        "runtime_mutation_disabled": not manifest.runtime_mutation_enabled,
        "operational_state_mutation_disabled": not manifest.operational_state_mutation_enabled,
        "recommendation_disabled": not manifest.recommendation_enabled,
        "ranking_disabled": not manifest.ranking_enabled,
        "scoring_disabled": not manifest.scoring_enabled,
        "selection_disabled": not manifest.selection_enabled,
        "hidden_orchestration_behavior_absent": not manifest.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not manifest.implicit_execution_pathway_enabled,
        "orchestration_engine_absent": not manifest.orchestration_engine_enabled,
        "state_machine_execution_absent": not manifest.state_machine_execution_enabled,
    }


def build_orchestration_manifest_diagnostics(manifest: OrchestrationManifest | None = None) -> dict[str, Any]:
    source = manifest or default_orchestration_manifest()
    visibility = validate_orchestration_manifest_visibility(source)
    continuity = validate_orchestration_continuity_metadata(source)
    explainability = validate_orchestration_explainability(source)
    non_execution = validate_orchestration_manifest_non_execution(source)
    enabled_flags = enabled_orchestration_manifest_capability_flags(source)
    return {
        "manifest_hash": hash_orchestration_manifest(source),
        "capability_hashes": [
            hash_orchestration_capability_visibility(visibility_record)
            for visibility_record in source.capability_visibility
        ],
        "boundary_hashes": [
            hash_orchestration_boundary_visibility(visibility_record)
            for visibility_record in source.boundary_visibility
        ],
        "continuity_hashes": [
            hash_orchestration_continuity_metadata(metadata) for metadata in source.continuity_metadata
        ],
        "explainability_hashes": [
            hash_orchestration_explainability_summary(summary) for summary in source.explainability_summaries
        ],
        "visibility_validation": visibility,
        "continuity_validation": continuity,
        "explainability_validation": explainability,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "prohibited_state_ids": aggregate_prohibited_states(source),
        "unsupported_state_ids": aggregate_unsupported_states(source),
        "blocked_state_ids": aggregate_blocked_states(source),
        "missing_metadata_ids": aggregate_missing_metadata_states(source),
        "conflicting_metadata_ids": aggregate_conflicting_metadata_states(source),
        "stale_metadata_ids": aggregate_stale_metadata_states(source),
        "unknown_state_ids": tuple(sorted(source.unsupported_state_visibility.unknown_states)),
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "remediation_absent": all(not diagnostic.remediation_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(
            not diagnostic.authorization_enabled
            and not diagnostic.orchestration_authorization_enabled
            and not diagnostic.readiness_approval_enabled
            for diagnostic in source.diagnostics
        ),
        "approval_absent": all(not diagnostic.approval_enabled for diagnostic in source.diagnostics),
        "execution_absent": all(
            not diagnostic.execution_enabled
            and not diagnostic.orchestration_execution_enabled
            and not diagnostic.runtime_execution_enabled
            and not diagnostic.routing_execution_enabled
            and not diagnostic.scheduling_execution_enabled
            and not diagnostic.sequencing_execution_enabled
            for diagnostic in source.diagnostics
        ),
        "selection_systems_absent": all(
            not diagnostic.recommendation_enabled
            and not diagnostic.ranking_enabled
            and not diagnostic.scoring_enabled
            and not diagnostic.selection_enabled
            for diagnostic in source.diagnostics
        ),
        "fail_visible_warning_count": (
            visibility["unsupported_state_visibility_count"]
            + visibility["blocked_state_visibility_count"]
            + visibility["missing_metadata_visibility_count"]
            + visibility["conflicting_metadata_visibility_count"]
            + visibility["stale_metadata_visibility_count"]
            + visibility["unknown_state_visibility_count"]
            + visibility["prohibited_state_visibility_count"]
        ),
    }
