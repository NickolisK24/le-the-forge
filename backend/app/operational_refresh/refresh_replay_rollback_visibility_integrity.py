"""Integrity and equality helpers for v4.1 replay and rollback visibility."""

from __future__ import annotations

from typing import Any

from .refresh_replay_rollback_visibility_continuity import certify_replay_rollback_visibility_continuity
from .refresh_replay_rollback_visibility_models import (
    RefreshReplayRollbackVisibility,
    ReplayRollbackVisibilityIdentity,
    default_refresh_replay_rollback_visibility,
    default_replay_rollback_identity,
)
from .refresh_replay_rollback_visibility_serialization import (
    export_refresh_replay_rollback_visibility,
    export_replay_rollback_identity,
    serialize_refresh_replay_rollback_visibility,
    serialize_replay_rollback_identity,
    stable_serialize,
)
from .refresh_replay_rollback_visibility_visibility import validate_refresh_replay_rollback_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "rollback_execution_enabled",
    "replay_execution_enabled",
    "recovery_execution_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_repair_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "schema_migration_execution_enabled",
    "automatic_migration_enabled",
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
    "hidden_recovery_behavior_enabled",
    "hidden_rollback_behavior_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_replay_rollback_correction_enabled",
    "hidden_fallback_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "inferred_provenance_allowed",
    "execution_enabled",
    "hidden",
)


def replay_rollback_capability_flags(visibility: RefreshReplayRollbackVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        visibility,
        visibility.identity,
        visibility.lineage_visibility,
        visibility.provenance_visibility,
        visibility.continuity_metadata,
        visibility.drift_visibility,
        visibility.blocked_state_visibility,
        visibility.unsupported_state_visibility,
        visibility.diagnostics,
        visibility.governance,
        *visibility.evidence,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_replay_rollback_capability_flags(visibility: RefreshReplayRollbackVisibility) -> dict[str, bool]:
    return {key: value for key, value in replay_rollback_capability_flags(visibility).items() if value}


def replay_rollback_identity_key(identity: ReplayRollbackVisibilityIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.visibility_id,
            identity.visibility_version,
            identity.source_manifest_reference,
            identity.source_dependency_graph_reference,
            identity.source_lineage_certification_reference,
            identity.source_schema_governance_reference,
            identity.source_sequencing_reference,
            identity.source_drift_certification_reference,
            identity.replay_reference,
            identity.rollback_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def replay_rollback_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def replay_rollback_identities_equal(left: ReplayRollbackVisibilityIdentity, right: ReplayRollbackVisibilityIdentity) -> bool:
    return serialize_replay_rollback_identity(left) == serialize_replay_rollback_identity(right)


def refresh_replay_rollback_visibilities_equal(
    left: RefreshReplayRollbackVisibility,
    right: RefreshReplayRollbackVisibility,
) -> bool:
    return serialize_refresh_replay_rollback_visibility(left) == serialize_refresh_replay_rollback_visibility(right)


def normalize_replay_rollback_identity(identity: ReplayRollbackVisibilityIdentity) -> ReplayRollbackVisibilityIdentity:
    exported = export_replay_rollback_identity(identity)
    return ReplayRollbackVisibilityIdentity(**exported)


def replay_rollback_identity_normalization_report(identity: ReplayRollbackVisibilityIdentity) -> dict[str, object]:
    normalized = normalize_replay_rollback_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": replay_rollback_identity_key(normalized),
        "normalized_identity": export_replay_rollback_identity(normalized),
        "field_count": len(export_replay_rollback_identity(normalized)),
        "omitted_field_count": 0,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "replay_execution_enabled": normalized.replay_execution_enabled,
        "rollback_execution_enabled": normalized.rollback_execution_enabled,
        "recovery_execution_enabled": normalized.recovery_execution_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
    }


def validate_replay_rollback_non_execution(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    enabled_flags = enabled_replay_rollback_capability_flags(visibility)
    return {
        "valid": len(enabled_flags) == 0 and visibility.non_executable and visibility.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": visibility.non_executable,
        "descriptive_only": visibility.descriptive_only,
        "rollback_execution_absent": not visibility.rollback_execution_enabled,
        "replay_execution_absent": not visibility.replay_execution_enabled,
        "recovery_execution_absent": not visibility.recovery_execution_enabled,
        "automatic_rollback_absent": not visibility.automatic_rollback_enabled,
        "automatic_recovery_absent": not visibility.automatic_recovery_enabled,
        "remediation_absent": not visibility.remediation_enabled,
        "automatic_correction_absent": not visibility.automatic_correction_enabled,
        "refresh_execution_absent": not visibility.refresh_execution_enabled,
        "orchestration_absent": not visibility.orchestration_enabled,
        "automatic_sequencing_absent": not visibility.automatic_sequencing_enabled,
        "schema_migration_execution_absent": not visibility.schema_migration_execution_enabled,
        "automatic_migration_absent": not visibility.automatic_migration_enabled,
        "planner_integration_absent": not visibility.planner_integration_enabled,
        "production_consumption_absent": not visibility.production_consumption_enabled,
        "runtime_mutation_absent": not visibility.runtime_mutation_enabled,
        "hidden_recovery_behavior_absent": not visibility.hidden_recovery_behavior_enabled,
        "hidden_rollback_behavior_absent": not visibility.hidden_rollback_behavior_enabled,
        "hidden_orchestration_behavior_absent": not visibility.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not visibility.implicit_execution_pathway_enabled,
        "silent_replay_rollback_correction_absent": not visibility.silent_replay_rollback_correction_enabled,
    }


def validate_replay_rollback_integrity(
    visibility: RefreshReplayRollbackVisibility | None = None,
) -> dict[str, object]:
    source = visibility or default_refresh_replay_rollback_visibility()
    visibility_validation = validate_refresh_replay_rollback_visibility(source)
    continuity = certify_replay_rollback_visibility_continuity(source)
    non_execution = validate_replay_rollback_non_execution(source)
    prohibited_leakage_visible = (
        bool(source.blocked_state_visibility.prohibited_remediation_leakage)
        and bool(source.blocked_state_visibility.prohibited_recovery_leakage)
        and bool(source.blocked_state_visibility.prohibited_rollback_execution_leakage)
        and bool(source.blocked_state_visibility.prohibited_orchestration_leakage)
        and bool(source.blocked_state_visibility.prohibited_execution_leakage)
        and bool(source.blocked_state_visibility.prohibited_planner_integration_leakage)
        and bool(source.blocked_state_visibility.prohibited_production_consumption_leakage)
    )
    return {
        "valid": (
            visibility_validation["valid"]
            and continuity["valid"]
            and non_execution["valid"]
            and prohibited_leakage_visible
        ),
        "visibility_valid": visibility_validation["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "prohibited_leakage_visible": prohibited_leakage_visible,
        "visibility_validation": visibility_validation,
        "continuity_certification": continuity,
        "non_execution_validation": non_execution,
        "identity_normalization": replay_rollback_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_replay_rollback_visibility(source)),
    }


def build_default_replay_rollback_identity() -> ReplayRollbackVisibilityIdentity:
    return default_replay_rollback_identity()
