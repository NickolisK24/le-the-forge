"""Diagnostics for v4.2 coordination dependency graph governance."""

from __future__ import annotations

from typing import Any

from .coordination_dependency_graph_hashing import (
    hash_continuity_aware_dependency_reference,
    hash_coordination_dependency_graph,
    hash_coordination_direction_visibility,
    hash_coordination_graph_edge,
    hash_coordination_graph_node,
    hash_lineage_aware_dependency_reference,
)
from .coordination_dependency_graph_models import (
    FAIL_VISIBLE_GRAPH_DEPENDENCY_STATES,
    GRAPH_DEPENDENCY_STATE_BLOCKED,
    GRAPH_DEPENDENCY_STATE_PROHIBITED,
    GRAPH_DEPENDENCY_STATE_STALE,
    GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
    GRAPH_DEPENDENCY_STATES,
    CoordinationDependencyGraph,
    CoordinationGraphEdge,
    CoordinationGraphNode,
    default_coordination_dependency_graph,
)
from .coordination_dependency_graph_serialization import serialize_coordination_dependency_graph
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "graph_execution_enabled",
    "dependency_resolution_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "recovery_execution_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "lineage_repair_enabled",
    "inferred_lineage_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_dependency_resolution_enabled",
    "hidden_direction_inference_enabled",
    "hidden_fallback_enabled",
    "implicit_execution_pathway_enabled",
)


def count_coordination_graph_node_states(nodes: tuple[CoordinationGraphNode, ...]) -> dict[str, int]:
    counts = {state: 0 for state in GRAPH_DEPENDENCY_STATES}
    counts["invalid"] = 0
    for node in nodes:
        if node.node_state in counts:
            counts[node.node_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_coordination_graph_edge_states(edges: tuple[CoordinationGraphEdge, ...]) -> dict[str, int]:
    counts = {state: 0 for state in GRAPH_DEPENDENCY_STATES}
    counts["invalid"] = 0
    for edge in edges:
        if edge.dependency_state in counts:
            counts[edge.dependency_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_coordination_graph_node_ids(nodes: tuple[CoordinationGraphNode, ...]) -> tuple[str, ...]:
    return tuple(
        node.node_id for node in nodes if node.node_state in FAIL_VISIBLE_GRAPH_DEPENDENCY_STATES and node.fail_visible
    )


def fail_visible_coordination_graph_edge_ids(edges: tuple[CoordinationGraphEdge, ...]) -> tuple[str, ...]:
    return tuple(
        edge.edge_id for edge in edges if edge.dependency_state in FAIL_VISIBLE_GRAPH_DEPENDENCY_STATES and edge.fail_visible
    )


def coordination_dependency_graph_capability_flags(graph: CoordinationDependencyGraph) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        graph,
        graph.identity,
        graph.direction_visibility,
        graph.blocked_dependency_visibility,
        graph.prohibited_dependency_visibility,
        graph.unsupported_dependency_visibility,
        graph.governance_visibility,
        *graph.nodes,
        *graph.edges,
        *graph.lineage_references,
        *graph.continuity_references,
        *graph.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_dependency_graph_capability_flags(graph: CoordinationDependencyGraph) -> dict[str, bool]:
    return {key: value for key, value in coordination_dependency_graph_capability_flags(graph).items() if value}


def coordination_dependency_graphs_equal(left: CoordinationDependencyGraph, right: CoordinationDependencyGraph) -> bool:
    return serialize_coordination_dependency_graph(left) == serialize_coordination_dependency_graph(right)


def validate_dependency_direction_visibility(graph: CoordinationDependencyGraph) -> dict[str, object]:
    edge_ids = tuple(edge.edge_id for edge in graph.edges)
    visible_edge_ids = graph.direction_visibility.directional_edge_ids
    missing_direction_ids = tuple(sorted(set(edge_ids) - set(visible_edge_ids)))
    corrective_count = sum(
        1
        for item in (graph.direction_visibility, *graph.edges)
        if getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "automatic_correction_enabled", False)
        or getattr(item, "hidden_direction_inference_enabled", False)
    )
    return {
        "valid": (
            len(missing_direction_ids) == 0
            and graph.direction_visibility.direction_visible
            and corrective_count == 0
        ),
        "directional_edge_count": len(visible_edge_ids),
        "missing_direction_ids": missing_direction_ids,
        "reverse_dependency_visibility_count": len(graph.direction_visibility.reverse_dependency_visibility),
        "ambiguous_direction_visibility_count": len(graph.direction_visibility.ambiguous_direction_visibility),
        "circular_direction_visibility_count": len(graph.direction_visibility.circular_direction_visibility),
        "direction_visible": graph.direction_visibility.direction_visible,
        "corrective_direction_count": corrective_count,
    }


def validate_dependency_graph_visibility(graph: CoordinationDependencyGraph) -> dict[str, object]:
    blocked_node_ids = tuple(node.node_id for node in graph.nodes if node.node_state == GRAPH_DEPENDENCY_STATE_BLOCKED)
    blocked_edge_ids = tuple(edge.edge_id for edge in graph.edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_BLOCKED)
    prohibited_node_ids = tuple(
        node.node_id for node in graph.nodes if node.node_state == GRAPH_DEPENDENCY_STATE_PROHIBITED
    )
    prohibited_edge_ids = tuple(
        edge.edge_id for edge in graph.edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_PROHIBITED
    )
    unsupported_node_ids = tuple(
        node.node_id for node in graph.nodes if node.node_state == GRAPH_DEPENDENCY_STATE_UNSUPPORTED
    )
    unsupported_edge_ids = tuple(
        edge.edge_id for edge in graph.edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_UNSUPPORTED
    )
    stale_node_ids = tuple(node.node_id for node in graph.nodes if node.node_state == GRAPH_DEPENDENCY_STATE_STALE)
    stale_edge_ids = tuple(edge.edge_id for edge in graph.edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_STALE)
    blocked_visible = set(blocked_node_ids).issubset(set(graph.blocked_dependency_visibility.blocked_node_ids)) and set(
        blocked_edge_ids
    ).issubset(set(graph.blocked_dependency_visibility.blocked_edge_ids))
    prohibited_visible = set(prohibited_node_ids).issubset(
        set(graph.prohibited_dependency_visibility.prohibited_node_ids)
    ) and set(prohibited_edge_ids).issubset(set(graph.prohibited_dependency_visibility.prohibited_edge_ids))
    unsupported_visible = set(unsupported_node_ids).issubset(
        set(graph.unsupported_dependency_visibility.unsupported_node_ids)
    ) and set(unsupported_edge_ids).issubset(set(graph.unsupported_dependency_visibility.unsupported_edge_ids))
    stale_visible = set(stale_node_ids + stale_edge_ids).issubset(
        set(graph.unsupported_dependency_visibility.stale_dependency_visibility)
        | set(graph.unsupported_dependency_visibility.unsupported_edge_ids)
    )
    invalid_node_ids = tuple(node.node_id for node in graph.nodes if node.node_state not in GRAPH_DEPENDENCY_STATES)
    invalid_edge_ids = tuple(edge.edge_id for edge in graph.edges if edge.dependency_state not in GRAPH_DEPENDENCY_STATES)
    hidden_count = sum(1 for item in (*graph.nodes, *graph.edges, *graph.diagnostics) if getattr(item, "hidden", False))
    corrective_count = sum(
        1
        for item in (
            graph.blocked_dependency_visibility,
            graph.prohibited_dependency_visibility,
            graph.unsupported_dependency_visibility,
            *graph.nodes,
            *graph.edges,
            *graph.diagnostics,
        )
        if getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "planner_integration_enabled", False)
        or getattr(item, "production_consumption_enabled", False)
        or getattr(item, "runtime_mutation_enabled", False)
        or getattr(item, "remediation_enabled", False)
        or getattr(item, "automatic_correction_enabled", False)
        or getattr(item, "automatic_rollback_enabled", False)
        or getattr(item, "authorization_enabled", False)
        or getattr(item, "approval_enabled", False)
        or getattr(item, "execution_enabled", False)
    )
    return {
        "valid": (
            blocked_visible
            and prohibited_visible
            and unsupported_visible
            and stale_visible
            and len(invalid_node_ids) == 0
            and len(invalid_edge_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "node_state_counts": count_coordination_graph_node_states(graph.nodes),
        "edge_state_counts": count_coordination_graph_edge_states(graph.edges),
        "fail_visible_node_ids": fail_visible_coordination_graph_node_ids(graph.nodes),
        "fail_visible_edge_ids": fail_visible_coordination_graph_edge_ids(graph.edges),
        "blocked_node_ids": blocked_node_ids,
        "blocked_edge_ids": blocked_edge_ids,
        "prohibited_node_ids": prohibited_node_ids,
        "prohibited_edge_ids": prohibited_edge_ids,
        "unsupported_node_ids": unsupported_node_ids,
        "unsupported_edge_ids": unsupported_edge_ids,
        "stale_node_ids": stale_node_ids,
        "stale_edge_ids": stale_edge_ids,
        "blocked_dependencies_visible": blocked_visible,
        "prohibited_dependencies_visible": prohibited_visible,
        "unsupported_dependencies_visible": unsupported_visible,
        "stale_dependencies_visible": stale_visible,
        "invalid_node_ids": invalid_node_ids,
        "invalid_edge_ids": invalid_edge_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in graph.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in graph.diagnostics),
    }


def validate_dependency_graph_lineage_continuity(graph: CoordinationDependencyGraph) -> dict[str, object]:
    node_ids = {node.node_id for node in graph.nodes}
    edge_ids = {edge.edge_id for edge in graph.edges}
    missing_node_refs = tuple(
        sorted(
            ref
            for lineage in graph.lineage_references
            for ref in lineage.node_references
            if ref not in node_ids
        )
    )
    missing_edge_refs = tuple(
        sorted(
            ref
            for lineage in graph.lineage_references
            for ref in lineage.edge_references
            if ref not in edge_ids
        )
    )
    corrective_count = sum(
        1
        for lineage in graph.lineage_references
        if lineage.inferred_lineage_enabled
        or lineage.lineage_repair_enabled
        or lineage.hidden_lineage_resolution_enabled
        or lineage.dependency_resolution_enabled
        or lineage.refresh_execution_enabled
        or lineage.orchestration_execution_enabled
        or lineage.runtime_mutation_enabled
    )
    return {
        "valid": (
            len(graph.lineage_references) > 0
            and len(missing_node_refs) == 0
            and len(missing_edge_refs) == 0
            and all(lineage.lineage_continuity_preserved for lineage in graph.lineage_references)
            and all(lineage.provenance_continuity_preserved for lineage in graph.lineage_references)
            and corrective_count == 0
        ),
        "lineage_reference": graph.identity.lineage_reference,
        "lineage_reference_count": len(graph.lineage_references),
        "missing_node_references": missing_node_refs,
        "missing_edge_references": missing_edge_refs,
        "lineage_continuity_preserved": all(
            lineage.lineage_continuity_preserved for lineage in graph.lineage_references
        ),
        "provenance_continuity_preserved": all(
            lineage.provenance_continuity_preserved for lineage in graph.lineage_references
        ),
        "corrective_lineage_count": corrective_count,
    }


def validate_dependency_graph_continuity(graph: CoordinationDependencyGraph) -> dict[str, object]:
    edge_ids = {edge.edge_id for edge in graph.edges}
    missing_dependency_refs = tuple(
        sorted(
            ref
            for continuity in graph.continuity_references
            for ref in continuity.dependency_references
            if ref not in edge_ids
        )
    )
    corrective_count = sum(
        1
        for continuity in graph.continuity_references
        if continuity.automatic_correction_enabled
        or continuity.automatic_rollback_enabled
        or continuity.recovery_execution_enabled
        or continuity.dependency_resolution_enabled
        or continuity.refresh_execution_enabled
        or continuity.orchestration_execution_enabled
        or continuity.runtime_mutation_enabled
    )
    return {
        "valid": (
            len(graph.continuity_references) > 0
            and len(missing_dependency_refs) == 0
            and all(continuity.continuity_preserved for continuity in graph.continuity_references)
            and all(continuity.replay_safe for continuity in graph.continuity_references)
            and all(continuity.rollback_safe for continuity in graph.continuity_references)
            and all(continuity.provenance_safe for continuity in graph.continuity_references)
            and all(continuity.lineage_safe for continuity in graph.continuity_references)
            and corrective_count == 0
        ),
        "continuity_reference": graph.identity.continuity_reference,
        "continuity_reference_count": len(graph.continuity_references),
        "missing_dependency_references": missing_dependency_refs,
        "continuity_preserved": all(continuity.continuity_preserved for continuity in graph.continuity_references),
        "replay_safe": all(continuity.replay_safe for continuity in graph.continuity_references),
        "rollback_safe": all(continuity.rollback_safe for continuity in graph.continuity_references),
        "provenance_safe": all(continuity.provenance_safe for continuity in graph.continuity_references),
        "lineage_safe": all(continuity.lineage_safe for continuity in graph.continuity_references),
        "corrective_continuity_count": corrective_count,
    }


def validate_coordination_manifest_compatibility(
    graph: CoordinationDependencyGraph,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    manifest_hash = hash_coordination_manifest(source)
    return {
        "valid": (
            graph.identity.source_manifest_reference == source.identity.manifest_id
            and graph.compatibility_manifest_reference == source.identity.manifest_id
            and graph.identity.source_manifest_hash_reference == manifest_hash
        ),
        "graph_source_manifest_reference": graph.identity.source_manifest_reference,
        "graph_compatibility_manifest_reference": graph.compatibility_manifest_reference,
        "manifest_reference": source.identity.manifest_id,
        "source_manifest_hash_reference": graph.identity.source_manifest_hash_reference,
        "expected_manifest_hash": manifest_hash,
        "manifest_hash_matches": graph.identity.source_manifest_hash_reference == manifest_hash,
    }


def validate_coordination_dependency_graph_non_execution(graph: CoordinationDependencyGraph) -> dict[str, object]:
    enabled_flags = enabled_coordination_dependency_graph_capability_flags(graph)
    return {
        "valid": len(enabled_flags) == 0 and graph.non_executable and graph.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": graph.non_executable,
        "descriptive_only": graph.descriptive_only,
        "dependency_resolution_disabled": not graph.dependency_resolution_enabled,
        "orchestration_execution_disabled": not graph.orchestration_execution_enabled,
        "refresh_execution_disabled": not graph.refresh_execution_enabled,
        "planner_integration_disabled": not graph.planner_integration_enabled,
        "production_consumption_disabled": (
            not graph.production_consumption_enabled and not graph.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not graph.runtime_mutation_enabled,
        "remediation_disabled": not graph.remediation_enabled,
        "automatic_correction_disabled": not graph.automatic_correction_enabled,
        "automatic_rollback_disabled": not graph.automatic_rollback_enabled,
        "authorization_disabled": not graph.authorization_enabled,
        "approval_disabled": not graph.approval_enabled,
        "ranking_disabled": not graph.ranking_enabled,
        "scoring_disabled": not graph.scoring_enabled,
        "selection_disabled": not graph.selection_enabled,
        "operational_execution_disabled": not graph.operational_execution_enabled,
        "hidden_dependency_resolution_absent": not graph.hidden_dependency_resolution_enabled,
        "implicit_execution_pathway_absent": not graph.implicit_execution_pathway_enabled,
    }


def build_coordination_dependency_graph_diagnostics(
    graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, Any]:
    source_manifest = manifest or default_coordination_manifest()
    source = graph or default_coordination_dependency_graph(source_manifest)
    direction = validate_dependency_direction_visibility(source)
    visibility = validate_dependency_graph_visibility(source)
    lineage = validate_dependency_graph_lineage_continuity(source)
    continuity = validate_dependency_graph_continuity(source)
    compatibility = validate_coordination_manifest_compatibility(source, source_manifest)
    non_execution = validate_coordination_dependency_graph_non_execution(source)
    enabled_flags = enabled_coordination_dependency_graph_capability_flags(source)
    return {
        "graph_hash": hash_coordination_dependency_graph(source),
        "node_hashes": [hash_coordination_graph_node(node) for node in source.nodes],
        "edge_hashes": [hash_coordination_graph_edge(edge) for edge in source.edges],
        "direction_visibility_hash": hash_coordination_direction_visibility(source.direction_visibility),
        "lineage_hashes": [
            hash_lineage_aware_dependency_reference(reference) for reference in source.lineage_references
        ],
        "continuity_hashes": [
            hash_continuity_aware_dependency_reference(reference) for reference in source.continuity_references
        ],
        "direction_visibility_validation": direction,
        "dependency_visibility_validation": visibility,
        "lineage_continuity_validation": lineage,
        "continuity_validation": continuity,
        "manifest_compatibility_validation": compatibility,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "blocked_node_ids": visibility["blocked_node_ids"],
        "blocked_edge_ids": visibility["blocked_edge_ids"],
        "prohibited_node_ids": visibility["prohibited_node_ids"],
        "prohibited_edge_ids": visibility["prohibited_edge_ids"],
        "unsupported_node_ids": visibility["unsupported_node_ids"],
        "unsupported_edge_ids": visibility["unsupported_edge_ids"],
        "stale_node_ids": visibility["stale_node_ids"],
        "stale_edge_ids": visibility["stale_edge_ids"],
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "fail_visible_dependency_count": (
            len(visibility["fail_visible_node_ids"]) + len(visibility["fail_visible_edge_ids"])
        ),
    }
