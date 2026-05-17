"""Deterministic serialization for v4.1 refresh dependency graphs."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_dependency_graph_models import (
    RefreshDependencyBlockedStateVisibility,
    RefreshDependencyContinuityMetadata,
    RefreshDependencyDiagnosticsVisibility,
    RefreshDependencyDriftVisibility,
    RefreshDependencyEdge,
    RefreshDependencyGovernanceVisibility,
    RefreshDependencyGraph,
    RefreshDependencyGraphIdentity,
    RefreshDependencyLineageChain,
    RefreshDependencyNode,
    RefreshDependencyProvenanceChain,
    RefreshDependencyReplayMetadata,
    RefreshDependencyRollbackMetadata,
    RefreshDependencyUnsupportedStateVisibility,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in (
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
        "dependency_execution_enabled",
    ):
        if field_name in data:
            data[field_name] = False
    return data


def export_dependency_graph_identity(identity: RefreshDependencyGraphIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_dependency_node(node: RefreshDependencyNode) -> dict[str, Any]:
    return _disable_execution_fields(asdict(node))


def export_dependency_edge(edge: RefreshDependencyEdge) -> dict[str, Any]:
    return _disable_execution_fields(asdict(edge))


def export_lineage_chain(chain: RefreshDependencyLineageChain) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(chain))
    for field_name in (
        "node_references",
        "edge_references",
        "prior_graph_references",
        "successor_graph_references",
        "lineage_discontinuity_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_provenance_chain(chain: RefreshDependencyProvenanceChain) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(chain))
    for field_name in (
        "source_evidence_references",
        "node_provenance_references",
        "edge_provenance_references",
        "provenance_discontinuity_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_continuity_metadata(metadata: RefreshDependencyContinuityMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in (
        "graph_continuity_references",
        "lineage_continuity_references",
        "provenance_continuity_references",
        "replay_continuity_references",
        "rollback_continuity_references",
        "drift_visibility_references",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_replay_metadata(metadata: RefreshDependencyReplayMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("replay_evidence_references", "replay_discontinuity_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_rollback_metadata(metadata: RefreshDependencyRollbackMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("rollback_evidence_references", "rollback_discontinuity_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_blocked_state_visibility(visibility: RefreshDependencyBlockedStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "blocked_dependency_edges",
        "circular_dependency_edges",
        "lineage_discontinuity_visibility",
        "provenance_discontinuity_visibility",
        "replay_discontinuity_visibility",
        "rollback_discontinuity_visibility",
        "prohibited_execution_leakage",
        "prohibited_orchestration_leakage",
        "prohibited_remediation_leakage",
        "prohibited_planner_integration_leakage",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_unsupported_state_visibility(visibility: RefreshDependencyUnsupportedStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "unsupported_dependency_nodes",
        "unsupported_dependency_edges",
        "unsupported_dependency_providers",
        "stale_dependency_edges",
        "prohibited_dependency_edges",
        "prohibited_dependency_domains",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_drift_visibility(visibility: RefreshDependencyDriftVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("stale_relationships", "changed_manifest_references", "dependency_drift_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_diagnostics_visibility(visibility: RefreshDependencyDiagnosticsVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "diagnostic_references",
        "warning_visibility",
        "blocker_visibility",
        "circular_dependency_visibility",
        "unsupported_dependency_visibility",
        "prohibited_dependency_visibility",
        "drift_visibility",
        "integrity_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_visibility(visibility: RefreshDependencyGovernanceVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_refresh_dependency_graph(graph: RefreshDependencyGraph) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(graph))
    data["identity"] = export_dependency_graph_identity(graph.identity)
    data["nodes"] = [
        export_dependency_node(node)
        for node in sorted(graph.nodes, key=lambda item: (item.deterministic_order, item.node_id))
    ]
    data["edges"] = [
        export_dependency_edge(edge)
        for edge in sorted(graph.edges, key=lambda item: (item.deterministic_order, item.edge_id))
    ]
    data["lineage_chains"] = [
        export_lineage_chain(chain)
        for chain in sorted(graph.lineage_chains, key=lambda item: (item.deterministic_order, item.lineage_chain_id))
    ]
    data["provenance_chains"] = [
        export_provenance_chain(chain)
        for chain in sorted(
            graph.provenance_chains,
            key=lambda item: (item.deterministic_order, item.provenance_chain_id),
        )
    ]
    data["continuity_metadata"] = export_continuity_metadata(graph.continuity_metadata)
    data["replay_metadata"] = export_replay_metadata(graph.replay_metadata)
    data["rollback_metadata"] = export_rollback_metadata(graph.rollback_metadata)
    data["blocked_state_visibility"] = export_blocked_state_visibility(graph.blocked_state_visibility)
    data["unsupported_state_visibility"] = export_unsupported_state_visibility(graph.unsupported_state_visibility)
    data["drift_visibility"] = export_drift_visibility(graph.drift_visibility)
    data["diagnostics_visibility"] = export_diagnostics_visibility(graph.diagnostics_visibility)
    data["governance_visibility"] = export_governance_visibility(graph.governance_visibility)
    return data


def serialize_dependency_graph_identity(identity: RefreshDependencyGraphIdentity) -> str:
    return stable_serialize(export_dependency_graph_identity(identity))


def serialize_refresh_dependency_graph(graph: RefreshDependencyGraph) -> str:
    return stable_serialize(export_refresh_dependency_graph(graph))
