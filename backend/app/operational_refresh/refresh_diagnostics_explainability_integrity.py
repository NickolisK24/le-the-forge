"""Integrity and equality helpers for v4.1 diagnostics explainability."""

from __future__ import annotations

from typing import Any

from .refresh_diagnostics_explainability_continuity import certify_diagnostics_explainability_continuity
from .refresh_diagnostics_explainability_models import (
    RefreshDiagnosticsExplainability,
    RefreshDiagnosticsExplainabilityIdentity,
    default_refresh_diagnostics_explainability,
    default_refresh_diagnostics_explainability_identity,
)
from .refresh_diagnostics_explainability_serialization import (
    export_diagnostics_explainability_identity,
    export_refresh_diagnostics_explainability,
    serialize_diagnostics_explainability_identity,
    serialize_refresh_diagnostics_explainability,
    stable_serialize,
)
from .refresh_diagnostics_explainability_visibility import validate_refresh_diagnostics_explainability_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_repair_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "dependency_resolution_enabled",
    "schema_migration_execution_enabled",
    "automatic_migration_enabled",
    "rollback_execution_enabled",
    "recovery_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
    "runtime_mutation_enabled",
    "hidden_remediation_behavior_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "hidden_fallback_enabled",
    "hidden",
)


def diagnostics_explainability_capability_flags(payload: RefreshDiagnosticsExplainability) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        payload,
        payload.identity,
        payload.diagnostic_aggregation,
        payload.explanation_aggregation,
        payload.continuity_metadata,
        payload.integrity_boundary,
        payload.governance,
        *payload.diagnostic_summaries,
        *payload.explanation_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_diagnostics_explainability_capability_flags(payload: RefreshDiagnosticsExplainability) -> dict[str, bool]:
    return {key: value for key, value in diagnostics_explainability_capability_flags(payload).items() if value}


def diagnostics_explainability_identity_key(identity: RefreshDiagnosticsExplainabilityIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.diagnostics_id,
            identity.explanation_id,
            identity.diagnostics_version,
            identity.source_manifest_reference,
            identity.source_dependency_graph_reference,
            identity.source_lineage_certification_reference,
            identity.source_schema_governance_reference,
            identity.source_sequencing_reference,
            identity.source_drift_certification_reference,
            identity.source_replay_rollback_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def diagnostics_explainability_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def diagnostics_explainability_identities_equal(
    left: RefreshDiagnosticsExplainabilityIdentity,
    right: RefreshDiagnosticsExplainabilityIdentity,
) -> bool:
    return serialize_diagnostics_explainability_identity(left) == serialize_diagnostics_explainability_identity(right)


def refresh_diagnostics_explainabilities_equal(
    left: RefreshDiagnosticsExplainability,
    right: RefreshDiagnosticsExplainability,
) -> bool:
    return serialize_refresh_diagnostics_explainability(left) == serialize_refresh_diagnostics_explainability(right)


def normalize_diagnostics_explainability_identity(
    identity: RefreshDiagnosticsExplainabilityIdentity,
) -> RefreshDiagnosticsExplainabilityIdentity:
    exported = export_diagnostics_explainability_identity(identity)
    return RefreshDiagnosticsExplainabilityIdentity(**exported)


def diagnostics_explainability_identity_normalization_report(
    identity: RefreshDiagnosticsExplainabilityIdentity,
) -> dict[str, object]:
    normalized = normalize_diagnostics_explainability_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": diagnostics_explainability_identity_key(normalized),
        "normalized_identity": export_diagnostics_explainability_identity(normalized),
        "field_count": len(export_diagnostics_explainability_identity(normalized)),
        "omitted_field_count": 0,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "remediation_enabled": normalized.remediation_enabled,
        "recommendation_enabled": normalized.recommendation_enabled,
        "approval_enabled": normalized.approval_enabled,
        "execution_enabled": normalized.execution_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_diagnostics_explainability_non_execution(payload: RefreshDiagnosticsExplainability) -> dict[str, object]:
    enabled_flags = enabled_diagnostics_explainability_capability_flags(payload)
    return {
        "valid": len(enabled_flags) == 0 and payload.non_executable and payload.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": payload.non_executable,
        "descriptive_only": payload.descriptive_only,
        "remediation_absent": not payload.remediation_enabled,
        "automatic_correction_absent": not payload.automatic_correction_enabled,
        "automatic_repair_absent": not payload.automatic_repair_enabled,
        "refresh_execution_absent": not payload.refresh_execution_enabled,
        "orchestration_absent": not payload.orchestration_enabled,
        "automatic_sequencing_absent": not payload.automatic_sequencing_enabled,
        "dependency_resolution_absent": not payload.dependency_resolution_enabled,
        "schema_migration_execution_absent": not payload.schema_migration_execution_enabled,
        "automatic_migration_absent": not payload.automatic_migration_enabled,
        "rollback_execution_absent": not payload.rollback_execution_enabled,
        "recovery_execution_absent": not payload.recovery_execution_enabled,
        "planner_integration_absent": not payload.planner_integration_enabled,
        "production_consumption_absent": not payload.production_consumption_enabled,
        "recommendation_absent": not payload.recommendation_enabled,
        "ranking_absent": not payload.ranking_enabled,
        "scoring_absent": not payload.scoring_enabled,
        "selection_absent": not payload.selection_enabled,
        "approval_absent": not payload.approval_enabled,
        "authorization_absent": not payload.authorization_enabled,
        "runtime_mutation_absent": not payload.runtime_mutation_enabled,
        "hidden_remediation_behavior_absent": not payload.hidden_remediation_behavior_enabled,
        "hidden_orchestration_behavior_absent": not payload.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not payload.implicit_execution_pathway_enabled,
    }


def validate_diagnostics_explainability_integrity(
    payload: RefreshDiagnosticsExplainability | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_diagnostics_explainability()
    visibility = validate_refresh_diagnostics_explainability_visibility(source)
    continuity = certify_diagnostics_explainability_continuity(source)
    non_execution = validate_diagnostics_explainability_non_execution(source)
    boundary = source.integrity_boundary
    prohibited_leakage_visible = (
        bool(boundary.prohibited_remediation_leakage)
        and bool(boundary.prohibited_correction_leakage)
        and bool(boundary.prohibited_recommendation_leakage)
        and bool(boundary.prohibited_ranking_leakage)
        and bool(boundary.prohibited_scoring_leakage)
        and bool(boundary.prohibited_selection_leakage)
        and bool(boundary.prohibited_approval_leakage)
        and bool(boundary.prohibited_authorization_leakage)
        and bool(boundary.prohibited_orchestration_leakage)
        and bool(boundary.prohibited_execution_leakage)
        and bool(boundary.prohibited_planner_integration_leakage)
        and bool(boundary.prohibited_production_consumption_leakage)
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
        "identity_normalization": diagnostics_explainability_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_diagnostics_explainability(source)),
    }


def build_default_diagnostics_explainability_identity() -> RefreshDiagnosticsExplainabilityIdentity:
    return default_refresh_diagnostics_explainability_identity()
