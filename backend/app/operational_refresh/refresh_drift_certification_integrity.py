"""Integrity and equality helpers for v4.1 refresh drift certification."""

from __future__ import annotations

from typing import Any

from .refresh_drift_certification_continuity import certify_refresh_drift_continuity
from .refresh_drift_certification_models import (
    RefreshDriftCertification,
    RefreshDriftCertificationIdentity,
    default_refresh_drift_certification,
    default_refresh_drift_certification_identity,
)
from .refresh_drift_certification_serialization import (
    export_refresh_drift_certification,
    export_refresh_drift_certification_identity,
    serialize_refresh_drift_certification,
    serialize_refresh_drift_certification_identity,
    stable_serialize,
)
from .refresh_drift_certification_visibility import validate_refresh_drift_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "drift_remediation_enabled",
    "automatic_drift_correction_enabled",
    "automatic_correction_enabled",
    "automatic_repair_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "automatic_dependency_resolution_enabled",
    "schema_migration_execution_enabled",
    "automatic_migration_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "runtime_mutation_enabled",
    "hidden_remediation_behavior_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_drift_suppression_enabled",
    "hidden_fallback_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_classification_resolution_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "inferred_provenance_allowed",
    "execution_enabled",
    "live_replay_enabled",
    "correction_execution_enabled",
    "remediation_enabled",
)


def refresh_drift_capability_flags(certification: RefreshDriftCertification) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.layer_visibility,
        certification.classification_visibility,
        certification.continuity_metadata,
        certification.lineage_visibility,
        certification.provenance_visibility,
        certification.replay_visibility,
        certification.rollback_visibility,
        certification.blocked_state_visibility,
        certification.unsupported_state_visibility,
        certification.diagnostics,
        certification.governance,
        *certification.drift_observations,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_refresh_drift_capability_flags(certification: RefreshDriftCertification) -> dict[str, bool]:
    return {key: value for key, value in refresh_drift_capability_flags(certification).items() if value}


def refresh_drift_identity_key(identity: RefreshDriftCertificationIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.certification_id,
            identity.certification_version,
            identity.source_manifest_reference,
            identity.source_dependency_graph_reference,
            identity.source_lineage_certification_reference,
            identity.source_schema_governance_reference,
            identity.source_sequencing_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def refresh_drift_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def refresh_drift_identities_equal(left: RefreshDriftCertificationIdentity, right: RefreshDriftCertificationIdentity) -> bool:
    return serialize_refresh_drift_certification_identity(left) == serialize_refresh_drift_certification_identity(right)


def refresh_drift_certifications_equal(left: RefreshDriftCertification, right: RefreshDriftCertification) -> bool:
    return serialize_refresh_drift_certification(left) == serialize_refresh_drift_certification(right)


def normalize_refresh_drift_identity(identity: RefreshDriftCertificationIdentity) -> RefreshDriftCertificationIdentity:
    exported = export_refresh_drift_certification_identity(identity)
    return RefreshDriftCertificationIdentity(**exported)


def refresh_drift_identity_normalization_report(identity: RefreshDriftCertificationIdentity) -> dict[str, object]:
    normalized = normalize_refresh_drift_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": refresh_drift_identity_key(normalized),
        "normalized_identity": export_refresh_drift_certification_identity(normalized),
        "field_count": len(export_refresh_drift_certification_identity(normalized)),
        "omitted_field_count": 0,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "drift_remediation_enabled": normalized.drift_remediation_enabled,
        "automatic_drift_correction_enabled": normalized.automatic_drift_correction_enabled,
        "refresh_execution_enabled": normalized.refresh_execution_enabled,
        "orchestration_enabled": normalized.orchestration_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_refresh_drift_non_execution(certification: RefreshDriftCertification) -> dict[str, object]:
    enabled_flags = enabled_refresh_drift_capability_flags(certification)
    return {
        "valid": len(enabled_flags) == 0 and certification.non_executable and certification.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": certification.non_executable,
        "descriptive_only": certification.descriptive_only,
        "drift_remediation_absent": not certification.drift_remediation_enabled,
        "automatic_drift_correction_absent": not certification.automatic_drift_correction_enabled,
        "automatic_repair_absent": not certification.automatic_repair_enabled,
        "refresh_execution_absent": not certification.refresh_execution_enabled,
        "orchestration_absent": not certification.orchestration_enabled,
        "automatic_sequencing_absent": not certification.automatic_sequencing_enabled,
        "automatic_dependency_resolution_absent": not certification.automatic_dependency_resolution_enabled,
        "schema_migration_execution_absent": not certification.schema_migration_execution_enabled,
        "automatic_migration_absent": not certification.automatic_migration_enabled,
        "automatic_rollback_absent": not certification.automatic_rollback_enabled,
        "automatic_recovery_absent": not certification.automatic_recovery_enabled,
        "planner_integration_absent": not certification.planner_integration_enabled,
        "production_consumption_absent": not certification.production_consumption_enabled,
        "runtime_mutation_absent": not certification.runtime_mutation_enabled,
        "hidden_remediation_behavior_absent": not certification.hidden_remediation_behavior_enabled,
        "hidden_orchestration_behavior_absent": not certification.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not certification.implicit_execution_pathway_enabled,
        "silent_drift_suppression_absent": not certification.silent_drift_suppression_enabled,
    }


def validate_refresh_drift_integrity(certification: RefreshDriftCertification | None = None) -> dict[str, object]:
    source = certification or default_refresh_drift_certification()
    visibility = validate_refresh_drift_visibility(source)
    continuity = certify_refresh_drift_continuity(source)
    non_execution = validate_refresh_drift_non_execution(source)
    prohibited_leakage_visible = (
        bool(source.blocked_state_visibility.prohibited_remediation_leakage)
        and bool(source.blocked_state_visibility.prohibited_correction_leakage)
        and bool(source.blocked_state_visibility.prohibited_orchestration_leakage)
        and bool(source.blocked_state_visibility.prohibited_execution_leakage)
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
        "identity_normalization": refresh_drift_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_drift_certification(source)),
    }


def build_default_refresh_drift_certification_identity() -> RefreshDriftCertificationIdentity:
    return default_refresh_drift_certification_identity()
