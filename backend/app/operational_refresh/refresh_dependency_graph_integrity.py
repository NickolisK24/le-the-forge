"""Integrity and equality helpers for v4.1 refresh dependency graphs."""

from __future__ import annotations

from typing import Any

from .refresh_dependency_graph_continuity import validate_dependency_graph_continuity
from .refresh_dependency_graph_models import (
    RefreshDependencyGraph,
    RefreshDependencyGraphIdentity,
    default_dependency_graph_identity,
    default_refresh_dependency_graph,
)
from .refresh_dependency_graph_serialization import (
    export_dependency_graph_identity,
    export_refresh_dependency_graph,
    serialize_dependency_graph_identity,
    serialize_refresh_dependency_graph,
    stable_serialize,
)
from .refresh_dependency_graph_visibility import validate_refresh_dependency_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "refresh_execution_enabled",
    "graph_execution_enabled",
    "dependency_execution_enabled",
    "orchestration_enabled",
    "automatic_refresh_sequencing_enabled",
    "automatic_dependency_resolution_enabled",
    "automatic_migration_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "optimization_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "authorization_enabled",
    "approval_enabled",
    "runtime_mutation_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_dependency_fallback_enabled",
    "silent_fallback_enabled",
    "automatic_resolution_enabled",
    "automatic_lineage_repair_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "hidden_drift_resolution_enabled",
    "live_replay_enabled",
    "recovery_execution_enabled",
    "execution_enabled",
)


def dependency_graph_capability_flags(graph: RefreshDependencyGraph) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        graph,
        graph.identity,
        graph.continuity_metadata,
        graph.replay_metadata,
        graph.rollback_metadata,
        graph.blocked_state_visibility,
        graph.unsupported_state_visibility,
        graph.drift_visibility,
        graph.diagnostics_visibility,
        graph.governance_visibility,
        *graph.nodes,
        *graph.edges,
        *graph.lineage_chains,
        *graph.provenance_chains,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_dependency_graph_capability_flags(graph: RefreshDependencyGraph) -> dict[str, bool]:
    return {key: value for key, value in dependency_graph_capability_flags(graph).items() if value}


def dependency_graph_identity_key(identity: RefreshDependencyGraphIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.refresh_cycle_id,
            identity.graph_id,
            identity.graph_version,
            identity.source_manifest_reference,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def dependency_graph_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def dependency_graph_identities_equal(
    left: RefreshDependencyGraphIdentity,
    right: RefreshDependencyGraphIdentity,
) -> bool:
    return serialize_dependency_graph_identity(left) == serialize_dependency_graph_identity(right)


def refresh_dependency_graphs_equal(left: RefreshDependencyGraph, right: RefreshDependencyGraph) -> bool:
    return serialize_refresh_dependency_graph(left) == serialize_refresh_dependency_graph(right)


def normalize_dependency_graph_identity(identity: RefreshDependencyGraphIdentity) -> RefreshDependencyGraphIdentity:
    exported = export_dependency_graph_identity(identity)
    return RefreshDependencyGraphIdentity(**exported)


def dependency_graph_identity_normalization_report(identity: RefreshDependencyGraphIdentity) -> dict[str, object]:
    normalized = normalize_dependency_graph_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": dependency_graph_identity_key(normalized),
        "normalized_identity": export_dependency_graph_identity(normalized),
        "field_count": len(export_dependency_graph_identity(normalized)),
        "omitted_field_count": 0,
        "silent_correction_enabled": False,
        "hidden_fallback_enabled": normalized.hidden_fallback_enabled,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
        "graph_execution_enabled": normalized.graph_execution_enabled,
        "orchestration_enabled": normalized.orchestration_enabled,
    }


def validate_dependency_graph_non_execution(graph: RefreshDependencyGraph) -> dict[str, object]:
    enabled_flags = enabled_dependency_graph_capability_flags(graph)
    return {
        "valid": len(enabled_flags) == 0 and graph.non_executable and graph.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": graph.non_executable,
        "descriptive_only": graph.descriptive_only,
        "refresh_execution_absent": not graph.refresh_execution_enabled,
        "graph_execution_absent": not graph.graph_execution_enabled,
        "dependency_execution_absent": not graph.dependency_execution_enabled,
        "orchestration_absent": not graph.orchestration_enabled,
        "automatic_refresh_sequencing_absent": not graph.automatic_refresh_sequencing_enabled,
        "automatic_dependency_resolution_absent": not graph.automatic_dependency_resolution_enabled,
        "automatic_migration_absent": not graph.automatic_migration_enabled,
        "automatic_rollback_absent": not graph.automatic_rollback_enabled,
        "automatic_recovery_absent": not graph.automatic_recovery_enabled,
        "planner_integration_absent": not graph.planner_integration_enabled,
        "production_consumption_absent": not graph.production_consumption_enabled,
        "remediation_absent": not graph.remediation_enabled,
        "optimization_absent": not graph.optimization_enabled,
        "recommendation_absent": not graph.recommendation_enabled,
        "ranking_absent": not graph.ranking_enabled,
        "scoring_absent": not graph.scoring_enabled,
        "selection_absent": not graph.selection_enabled,
        "authorization_absent": not graph.authorization_enabled,
        "approval_absent": not graph.approval_enabled,
        "runtime_mutation_absent": not graph.runtime_mutation_enabled,
        "hidden_orchestration_behavior_absent": not graph.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not graph.implicit_execution_pathway_enabled,
        "silent_dependency_fallback_absent": not graph.silent_dependency_fallback_enabled,
    }


def validate_dependency_graph_integrity(graph: RefreshDependencyGraph | None = None) -> dict[str, object]:
    source = graph or default_refresh_dependency_graph()
    visibility = validate_refresh_dependency_visibility(source)
    continuity = validate_dependency_graph_continuity(source)
    non_execution = validate_dependency_graph_non_execution(source)
    prohibited_leakage_visible = (
        bool(source.blocked_state_visibility.prohibited_execution_leakage)
        and bool(source.blocked_state_visibility.prohibited_orchestration_leakage)
        and bool(source.blocked_state_visibility.prohibited_remediation_leakage)
        and bool(source.blocked_state_visibility.prohibited_planner_integration_leakage)
    )
    return {
        "valid": (
            visibility["valid"]
            and continuity["valid"]
            and non_execution["valid"]
            and prohibited_leakage_visible
        ),
        "visibility_valid": visibility["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "prohibited_leakage_visible": prohibited_leakage_visible,
        "visibility_validation": visibility,
        "continuity_validation": continuity,
        "non_execution_validation": non_execution,
        "identity_normalization": dependency_graph_identity_normalization_report(source.identity),
        "exported_field_count": len(export_refresh_dependency_graph(source)),
    }


def build_default_dependency_graph_identity() -> RefreshDependencyGraphIdentity:
    return default_dependency_graph_identity()
