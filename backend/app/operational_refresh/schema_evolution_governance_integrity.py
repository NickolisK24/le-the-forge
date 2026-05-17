"""Integrity and equality helpers for v4.1 schema evolution governance."""

from __future__ import annotations

from typing import Any

from .schema_evolution_governance_continuity import certify_schema_evolution_continuity
from .schema_evolution_governance_models import (
    SchemaEvolutionGovernance,
    SchemaEvolutionIdentity,
    default_schema_evolution_governance,
    default_schema_evolution_identity,
)
from .schema_evolution_governance_serialization import (
    export_schema_evolution_governance,
    export_schema_evolution_identity,
    serialize_schema_evolution_governance,
    serialize_schema_evolution_identity,
    stable_serialize,
)
from .schema_evolution_governance_visibility import validate_schema_evolution_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "schema_migration_execution_enabled",
    "automatic_schema_migration_enabled",
    "automatic_schema_repair_enabled",
    "automatic_compatibility_correction_enabled",
    "compatibility_correction_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
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
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "hidden_migration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_compatibility_fallback_enabled",
    "hidden_fallback_enabled",
    "hidden_compatibility_resolution_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "live_replay_enabled",
    "execution_enabled",
    "inferred_provenance_allowed",
)


def schema_evolution_capability_flags(governance: SchemaEvolutionGovernance) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        governance,
        governance.identity,
        governance.compatibility_visibility,
        governance.continuity_metadata,
        governance.lineage_visibility,
        governance.provenance_visibility,
        governance.replay_visibility,
        governance.rollback_visibility,
        governance.drift_visibility,
        governance.blocked_state_visibility,
        governance.unsupported_state_visibility,
        governance.diagnostics,
        governance.governance,
        *governance.version_nodes,
        *governance.version_transitions,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_schema_evolution_capability_flags(governance: SchemaEvolutionGovernance) -> dict[str, bool]:
    return {key: value for key, value in schema_evolution_capability_flags(governance).items() if value}


def schema_evolution_identity_key(identity: SchemaEvolutionIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.governance_id,
            identity.governance_version,
            identity.source_manifest_reference,
            identity.source_dependency_graph_reference,
            identity.source_lineage_certification_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def schema_evolution_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def schema_evolution_identities_equal(left: SchemaEvolutionIdentity, right: SchemaEvolutionIdentity) -> bool:
    return serialize_schema_evolution_identity(left) == serialize_schema_evolution_identity(right)


def schema_evolution_governances_equal(
    left: SchemaEvolutionGovernance,
    right: SchemaEvolutionGovernance,
) -> bool:
    return serialize_schema_evolution_governance(left) == serialize_schema_evolution_governance(right)


def normalize_schema_evolution_identity(identity: SchemaEvolutionIdentity) -> SchemaEvolutionIdentity:
    exported = export_schema_evolution_identity(identity)
    return SchemaEvolutionIdentity(**exported)


def schema_evolution_identity_normalization_report(identity: SchemaEvolutionIdentity) -> dict[str, object]:
    normalized = normalize_schema_evolution_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": schema_evolution_identity_key(normalized),
        "normalized_identity": export_schema_evolution_identity(normalized),
        "field_count": len(export_schema_evolution_identity(normalized)),
        "omitted_field_count": 0,
        "silent_compatibility_fallback_enabled": normalized.silent_compatibility_fallback_enabled
        if hasattr(normalized, "silent_compatibility_fallback_enabled")
        else False,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "schema_migration_execution_enabled": normalized.schema_migration_execution_enabled,
        "automatic_schema_migration_enabled": normalized.automatic_schema_migration_enabled,
        "automatic_compatibility_correction_enabled": normalized.automatic_compatibility_correction_enabled,
        "refresh_execution_enabled": normalized.refresh_execution_enabled,
        "orchestration_enabled": normalized.orchestration_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_schema_evolution_non_execution(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    enabled_flags = enabled_schema_evolution_capability_flags(governance)
    return {
        "valid": len(enabled_flags) == 0 and governance.non_executable and governance.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": governance.non_executable,
        "descriptive_only": governance.descriptive_only,
        "schema_migration_execution_absent": not governance.schema_migration_execution_enabled,
        "automatic_schema_migration_absent": not governance.automatic_schema_migration_enabled,
        "automatic_schema_repair_absent": not governance.automatic_schema_repair_enabled,
        "automatic_compatibility_correction_absent": not governance.automatic_compatibility_correction_enabled,
        "refresh_execution_absent": not governance.refresh_execution_enabled,
        "orchestration_absent": not governance.orchestration_enabled,
        "planner_integration_absent": not governance.planner_integration_enabled,
        "production_consumption_absent": not governance.production_consumption_enabled,
        "remediation_absent": not governance.remediation_enabled,
        "recommendation_absent": not governance.recommendation_enabled,
        "ranking_absent": not governance.ranking_enabled,
        "scoring_absent": not governance.scoring_enabled,
        "selection_absent": not governance.selection_enabled,
        "optimization_absent": not governance.optimization_enabled,
        "authorization_absent": not governance.authorization_enabled,
        "approval_absent": not governance.approval_enabled,
        "runtime_mutation_absent": not governance.runtime_mutation_enabled,
        "automatic_rollback_absent": not governance.automatic_rollback_enabled,
        "automatic_recovery_absent": not governance.automatic_recovery_enabled,
        "hidden_migration_behavior_absent": not governance.hidden_migration_behavior_enabled,
        "implicit_execution_pathway_absent": not governance.implicit_execution_pathway_enabled,
        "silent_compatibility_fallback_absent": not governance.silent_compatibility_fallback_enabled,
    }


def validate_schema_evolution_integrity(governance: SchemaEvolutionGovernance | None = None) -> dict[str, object]:
    source = governance or default_schema_evolution_governance()
    visibility = validate_schema_evolution_visibility(source)
    continuity = certify_schema_evolution_continuity(source)
    non_execution = validate_schema_evolution_non_execution(source)
    prohibited_leakage_visible = (
        bool(source.blocked_state_visibility.prohibited_migration_leakage)
        and bool(source.blocked_state_visibility.prohibited_execution_leakage)
        and bool(source.blocked_state_visibility.prohibited_orchestration_leakage)
        and bool(source.blocked_state_visibility.prohibited_remediation_leakage)
        and bool(source.blocked_state_visibility.prohibited_planner_integration_leakage)
        and bool(source.blocked_state_visibility.prohibited_production_consumption_leakage)
    )
    return {
        "valid": visibility["valid"] and continuity["valid"] and non_execution["valid"] and prohibited_leakage_visible,
        "visibility_valid": visibility["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "prohibited_leakage_visible": prohibited_leakage_visible,
        "visibility_validation": visibility,
        "continuity_certification": continuity,
        "non_execution_validation": non_execution,
        "identity_normalization": schema_evolution_identity_normalization_report(source.identity),
        "exported_field_count": len(export_schema_evolution_governance(source)),
    }


def build_default_schema_evolution_identity() -> SchemaEvolutionIdentity:
    return default_schema_evolution_identity()
