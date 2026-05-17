"""Integrity and equality helpers for v4.1 refresh sequencing visibility."""

from __future__ import annotations

from typing import Any

from .refresh_sequencing_visibility_continuity import certify_refresh_sequencing_continuity
from .refresh_sequencing_visibility_models import (
    RefreshSequencingIdentity,
    RefreshSequencingVisibility,
    default_refresh_sequencing_identity,
    default_refresh_sequencing_visibility,
)
from .refresh_sequencing_visibility_serialization import (
    export_refresh_sequencing_identity,
    export_refresh_sequencing_visibility,
    serialize_refresh_sequencing_identity,
    serialize_refresh_sequencing_visibility,
    stable_serialize,
)
from .refresh_sequencing_visibility_visibility import validate_refresh_sequencing_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "automatic_dependency_resolution_enabled",
    "migration_execution_enabled",
    "automatic_migration_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "runtime_mutation_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_ordering_correction_enabled",
    "hidden_fallback_enabled",
    "hidden_ordering_resolution_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "automatic_lineage_repair_enabled",
    "live_replay_enabled",
    "execution_enabled",
    "inferred_provenance_allowed",
)


def refresh_sequencing_capability_flags(visibility: RefreshSequencingVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        visibility,
        visibility.identity,
        visibility.dependency_aware_visibility,
        visibility.continuity_metadata,
        visibility.lineage_visibility,
        visibility.provenance_visibility,
        visibility.replay_visibility,
        visibility.rollback_visibility,
        visibility.drift_visibility,
        visibility.blocked_state_visibility,
        visibility.unsupported_state_visibility,
        visibility.diagnostics,
        visibility.governance,
        *visibility.ordering_nodes,
        *visibility.ordering_relationships,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_refresh_sequencing_capability_flags(visibility: RefreshSequencingVisibility) -> dict[str, bool]:
    return {key: value for key, value in refresh_sequencing_capability_flags(visibility).items() if value}


def refresh_sequencing_identity_key(identity: RefreshSequencingIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.sequencing_id,
            identity.sequencing_version,
            identity.source_manifest_reference,
            identity.source_dependency_graph_reference,
            identity.source_lineage_certification_reference,
            identity.source_schema_governance_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def refresh_sequencing_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def refresh_sequencing_identities_equal(left: RefreshSequencingIdentity, right: RefreshSequencingIdentity) -> bool:
    return serialize_refresh_sequencing_identity(left) == serialize_refresh_sequencing_identity(right)


def refresh_sequencing_visibilities_equal(
    left: RefreshSequencingVisibility,
    right: RefreshSequencingVisibility,
) -> bool:
    return serialize_refresh_sequencing_visibility(left) == serialize_refresh_sequencing_visibility(right)


def normalize_refresh_sequencing_identity(identity: RefreshSequencingIdentity) -> RefreshSequencingIdentity:
    exported = export_refresh_sequencing_identity(identity)
    return RefreshSequencingIdentity(**exported)


def refresh_sequencing_identity_normalization_report(identity: RefreshSequencingIdentity) -> dict[str, object]:
    normalized = normalize_refresh_sequencing_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": refresh_sequencing_identity_key(normalized),
        "normalized_identity": export_refresh_sequencing_identity(normalized),
        "field_count": len(export_refresh_sequencing_identity(normalized)),
        "omitted_field_count": 0,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "refresh_execution_enabled": normalized.refresh_execution_enabled,
        "orchestration_enabled": normalized.orchestration_enabled,
        "automatic_sequencing_enabled": normalized.automatic_sequencing_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_refresh_sequencing_non_execution(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    enabled_flags = enabled_refresh_sequencing_capability_flags(visibility)
    return {
        "valid": len(enabled_flags) == 0 and visibility.non_executable and visibility.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": visibility.non_executable,
        "descriptive_only": visibility.descriptive_only,
        "refresh_execution_absent": not visibility.refresh_execution_enabled,
        "orchestration_absent": not visibility.orchestration_enabled,
        "automatic_sequencing_absent": not visibility.automatic_sequencing_enabled,
        "automatic_dependency_resolution_absent": not visibility.automatic_dependency_resolution_enabled,
        "migration_execution_absent": not visibility.migration_execution_enabled,
        "automatic_migration_absent": not visibility.automatic_migration_enabled,
        "automatic_rollback_absent": not visibility.automatic_rollback_enabled,
        "automatic_recovery_absent": not visibility.automatic_recovery_enabled,
        "planner_integration_absent": not visibility.planner_integration_enabled,
        "production_consumption_absent": not visibility.production_consumption_enabled,
        "remediation_absent": not visibility.remediation_enabled,
        "recommendation_absent": not visibility.recommendation_enabled,
        "ranking_absent": not visibility.ranking_enabled,
        "scoring_absent": not visibility.scoring_enabled,
        "selection_absent": not visibility.selection_enabled,
        "optimization_absent": not visibility.optimization_enabled,
        "authorization_absent": not visibility.authorization_enabled,
        "approval_absent": not visibility.approval_enabled,
        "runtime_mutation_absent": not visibility.runtime_mutation_enabled,
        "hidden_orchestration_behavior_absent": not visibility.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not visibility.implicit_execution_pathway_enabled,
        "silent_ordering_correction_absent": not visibility.silent_ordering_correction_enabled,
    }


def validate_refresh_sequencing_integrity(visibility: RefreshSequencingVisibility | None = None) -> dict[str, object]:
    source = visibility or default_refresh_sequencing_visibility()
    visibility_validation = validate_refresh_sequencing_visibility(source)
    continuity = certify_refresh_sequencing_continuity(source)
    non_execution = validate_refresh_sequencing_non_execution(source)
    prohibited_leakage_visible = (
        bool(source.blocked_state_visibility.prohibited_orchestration_leakage)
        and bool(source.blocked_state_visibility.prohibited_execution_leakage)
        and bool(source.blocked_state_visibility.prohibited_remediation_leakage)
        and bool(source.blocked_state_visibility.prohibited_planner_integration_leakage)
        and bool(source.blocked_state_visibility.prohibited_production_consumption_leakage)
    )
    return {
        "valid": visibility_validation["valid"] and continuity["valid"] and non_execution["valid"] and prohibited_leakage_visible,
        "visibility_valid": visibility_validation["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "prohibited_leakage_visible": prohibited_leakage_visible,
        "visibility_validation": visibility_validation,
        "continuity_certification": continuity,
        "non_execution_validation": non_execution,
        "identity_normalization": refresh_sequencing_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_sequencing_visibility(source)),
    }


def build_default_refresh_sequencing_identity() -> RefreshSequencingIdentity:
    return default_refresh_sequencing_identity()
