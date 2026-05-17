"""Integrity and equality helpers for v4.1 refresh lineage certification."""

from __future__ import annotations

from typing import Any

from .refresh_lineage_certification_continuity import certify_refresh_lineage_continuity
from .refresh_lineage_certification_models import (
    RefreshLineageCertification,
    RefreshLineageIdentity,
    default_lineage_identity,
    default_refresh_lineage_certification,
)
from .refresh_lineage_certification_serialization import (
    export_lineage_identity,
    export_refresh_lineage_certification,
    serialize_lineage_identity,
    serialize_refresh_lineage_certification,
    stable_serialize,
)
from .refresh_lineage_certification_visibility import validate_refresh_lineage_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "migration_execution_enabled",
    "automatic_lineage_repair_enabled",
    "automatic_repair_enabled",
    "automatic_continuity_correction_enabled",
    "automatic_schema_migration_enabled",
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
    "silent_continuity_correction_enabled",
    "silent_correction_enabled",
    "live_replay_enabled",
    "recovery_execution_enabled",
    "execution_enabled",
    "inferred_provenance_allowed",
    "hidden_provenance_resolution_enabled",
    "hidden_evolution_resolution_enabled",
    "hidden_schema_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "hidden_drift_resolution_enabled",
)


def lineage_certification_capability_flags(certification: RefreshLineageCertification) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.evolution_visibility,
        certification.continuity_metadata,
        certification.replay_lineage_visibility,
        certification.rollback_lineage_visibility,
        certification.schema_transition_continuity,
        certification.blocked_state_visibility,
        certification.unsupported_state_visibility,
        certification.drift_visibility,
        certification.diagnostics,
        certification.governance,
        *certification.ancestry_nodes,
        *certification.ancestry_links,
        *certification.provenance_inheritance,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_lineage_certification_capability_flags(certification: RefreshLineageCertification) -> dict[str, bool]:
    return {key: value for key, value in lineage_certification_capability_flags(certification).items() if value}


def lineage_identity_key(identity: RefreshLineageIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.certification_id,
            identity.certification_version,
            identity.source_manifest_reference,
            identity.source_dependency_graph_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def lineage_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def lineage_identities_equal(left: RefreshLineageIdentity, right: RefreshLineageIdentity) -> bool:
    return serialize_lineage_identity(left) == serialize_lineage_identity(right)


def refresh_lineage_certifications_equal(
    left: RefreshLineageCertification,
    right: RefreshLineageCertification,
) -> bool:
    return serialize_refresh_lineage_certification(left) == serialize_refresh_lineage_certification(right)


def normalize_lineage_identity(identity: RefreshLineageIdentity) -> RefreshLineageIdentity:
    exported = export_lineage_identity(identity)
    return RefreshLineageIdentity(**exported)


def lineage_identity_normalization_report(identity: RefreshLineageIdentity) -> dict[str, object]:
    normalized = normalize_lineage_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": lineage_identity_key(normalized),
        "normalized_identity": export_lineage_identity(normalized),
        "field_count": len(export_lineage_identity(normalized)),
        "omitted_field_count": 0,
        "silent_correction_enabled": False,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "refresh_execution_enabled": normalized.refresh_execution_enabled,
        "orchestration_enabled": normalized.orchestration_enabled,
        "migration_execution_enabled": normalized.migration_execution_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_lineage_non_execution(certification: RefreshLineageCertification) -> dict[str, object]:
    enabled_flags = enabled_lineage_certification_capability_flags(certification)
    return {
        "valid": len(enabled_flags) == 0 and certification.non_executable and certification.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": certification.non_executable,
        "descriptive_only": certification.descriptive_only,
        "refresh_execution_absent": not certification.refresh_execution_enabled,
        "orchestration_absent": not certification.orchestration_enabled,
        "migration_execution_absent": not certification.migration_execution_enabled,
        "automatic_lineage_repair_absent": not certification.automatic_lineage_repair_enabled,
        "automatic_continuity_correction_absent": not certification.automatic_continuity_correction_enabled,
        "automatic_schema_migration_absent": not certification.automatic_schema_migration_enabled,
        "automatic_rollback_absent": not certification.automatic_rollback_enabled,
        "automatic_recovery_absent": not certification.automatic_recovery_enabled,
        "planner_integration_absent": not certification.planner_integration_enabled,
        "production_consumption_absent": not certification.production_consumption_enabled,
        "remediation_absent": not certification.remediation_enabled,
        "recommendation_absent": not certification.recommendation_enabled,
        "ranking_absent": not certification.ranking_enabled,
        "scoring_absent": not certification.scoring_enabled,
        "selection_absent": not certification.selection_enabled,
        "optimization_absent": not certification.optimization_enabled,
        "authorization_absent": not certification.authorization_enabled,
        "approval_absent": not certification.approval_enabled,
        "runtime_mutation_absent": not certification.runtime_mutation_enabled,
        "hidden_orchestration_behavior_absent": not certification.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not certification.implicit_execution_pathway_enabled,
        "silent_continuity_correction_absent": not certification.silent_continuity_correction_enabled,
    }


def validate_lineage_integrity(certification: RefreshLineageCertification | None = None) -> dict[str, object]:
    source = certification or default_refresh_lineage_certification()
    visibility = validate_refresh_lineage_visibility(source)
    continuity = certify_refresh_lineage_continuity(source)
    non_execution = validate_lineage_non_execution(source)
    prohibited_leakage_visible = (
        bool(source.blocked_state_visibility.prohibited_execution_leakage)
        and bool(source.blocked_state_visibility.prohibited_orchestration_leakage)
        and bool(source.blocked_state_visibility.prohibited_remediation_leakage)
        and bool(source.blocked_state_visibility.prohibited_migration_leakage)
        and bool(source.blocked_state_visibility.prohibited_planner_integration_leakage)
    )
    return {
        "valid": visibility["valid"] and continuity["valid"] and non_execution["valid"] and prohibited_leakage_visible,
        "visibility_valid": visibility["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "prohibited_leakage_visible": prohibited_leakage_visible,
        "visibility_validation": visibility,
        "continuity_validation": continuity,
        "non_execution_validation": non_execution,
        "identity_normalization": lineage_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_lineage_certification(source)),
    }


def build_default_lineage_identity() -> RefreshLineageIdentity:
    return default_lineage_identity()
