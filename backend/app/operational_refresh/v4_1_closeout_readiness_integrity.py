"""Integrity helpers for v4.1 closeout readiness."""

from __future__ import annotations

from typing import Any

from .v4_1_closeout_readiness_continuity import certify_v4_1_closeout_continuity
from .v4_1_closeout_readiness_models import (
    V41CloseoutIdentity,
    V41CloseoutReadiness,
    default_v4_1_closeout_identity,
    default_v4_1_closeout_readiness,
)
from .v4_1_closeout_readiness_serialization import (
    export_v4_1_closeout_identity,
    export_v4_1_closeout_readiness,
    serialize_v4_1_closeout_identity,
    serialize_v4_1_closeout_readiness,
    stable_serialize,
)
from .v4_1_closeout_readiness_visibility import validate_v4_1_closeout_visibility


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


def v4_1_closeout_capability_flags(payload: V41CloseoutReadiness) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        payload,
        payload.identity,
        payload.warning_aggregation,
        payload.readiness,
        payload.integrity_boundary,
        payload.governance,
        *payload.phase_coverage,
        *payload.report_coverage,
        *payload.warnings,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_v4_1_closeout_capability_flags(payload: V41CloseoutReadiness) -> dict[str, bool]:
    return {key: value for key, value in v4_1_closeout_capability_flags(payload).items() if value}


def v4_1_closeout_identity_key(identity: V41CloseoutIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.closeout_id,
            identity.refresh_generation_id,
            identity.closeout_version,
            str(identity.phase_count),
            str(identity.report_count),
            identity.provenance_reference,
            identity.lineage_reference,
            identity.continuity_reference,
            identity.readiness_reference,
        )
    )


def v4_1_closeout_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def v4_1_closeout_identities_equal(left: V41CloseoutIdentity, right: V41CloseoutIdentity) -> bool:
    return serialize_v4_1_closeout_identity(left) == serialize_v4_1_closeout_identity(right)


def v4_1_closeout_readiness_equal(left: V41CloseoutReadiness, right: V41CloseoutReadiness) -> bool:
    return serialize_v4_1_closeout_readiness(left) == serialize_v4_1_closeout_readiness(right)


def v4_1_closeout_identity_normalization_report(identity: V41CloseoutIdentity) -> dict[str, object]:
    exported = export_v4_1_closeout_identity(identity)
    normalized = V41CloseoutIdentity(**exported)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": v4_1_closeout_identity_key(normalized),
        "normalized_identity": export_v4_1_closeout_identity(normalized),
        "field_count": len(exported),
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "remediation_enabled": normalized.remediation_enabled,
        "automatic_correction_enabled": normalized.automatic_correction_enabled,
        "approval_enabled": normalized.approval_enabled,
        "authorization_enabled": normalized.authorization_enabled,
        "execution_enabled": normalized.execution_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_v4_1_closeout_non_execution(payload: V41CloseoutReadiness) -> dict[str, object]:
    enabled_flags = enabled_v4_1_closeout_capability_flags(payload)
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


def validate_v4_1_closeout_integrity(payload: V41CloseoutReadiness | None = None) -> dict[str, object]:
    source = payload or default_v4_1_closeout_readiness()
    visibility = validate_v4_1_closeout_visibility(source)
    continuity = certify_v4_1_closeout_continuity(source)
    non_execution = validate_v4_1_closeout_non_execution(source)
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
        "identity_normalization": v4_1_closeout_identity_normalization_report(source.identity),
        "exported_field_count": len(export_v4_1_closeout_readiness(source)),
    }


def build_default_v4_1_closeout_identity() -> V41CloseoutIdentity:
    return default_v4_1_closeout_identity()
