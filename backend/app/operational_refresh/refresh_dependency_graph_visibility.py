"""Fail-visible visibility helpers for v4.1 refresh dependency graphs."""

from __future__ import annotations

from .refresh_dependency_graph_models import (
    DEPENDENCY_GRAPH_STATE_BLOCKED,
    DEPENDENCY_GRAPH_STATE_CIRCULAR,
    DEPENDENCY_GRAPH_STATE_LINEAGE_GAP,
    DEPENDENCY_GRAPH_STATE_PROHIBITED,
    DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP,
    DEPENDENCY_GRAPH_STATE_STALE,
    DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
    DEPENDENCY_GRAPH_STATES,
    FAIL_VISIBLE_DEPENDENCY_GRAPH_STATES,
    PROHIBITED_DEPENDENCY_DOMAINS,
    RefreshDependencyEdge,
    RefreshDependencyGraph,
    RefreshDependencyNode,
    default_dependency_edges,
    default_dependency_nodes,
    default_refresh_dependency_graph,
)


def count_dependency_node_states(nodes: tuple[RefreshDependencyNode, ...] | list[RefreshDependencyNode]) -> dict[str, int]:
    counts = {state: 0 for state in DEPENDENCY_GRAPH_STATES}
    counts["invalid"] = 0
    for node in nodes:
        if node.state in counts:
            counts[node.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_dependency_edge_states(edges: tuple[RefreshDependencyEdge, ...] | list[RefreshDependencyEdge]) -> dict[str, int]:
    counts = {state: 0 for state in DEPENDENCY_GRAPH_STATES}
    counts["invalid"] = 0
    for edge in edges:
        if edge.relationship_state in counts:
            counts[edge.relationship_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_dependency_edge_ids(edges: tuple[RefreshDependencyEdge, ...] | list[RefreshDependencyEdge]) -> tuple[str, ...]:
    return tuple(edge.edge_id for edge in edges if edge.relationship_state in FAIL_VISIBLE_DEPENDENCY_GRAPH_STATES and edge.fail_visible)


def validate_refresh_dependency_visibility(graph: RefreshDependencyGraph) -> dict[str, object]:
    node_counts = count_dependency_node_states(graph.nodes)
    edge_counts = count_dependency_edge_states(graph.edges)
    unsupported_nodes = tuple(node.node_id for node in graph.nodes if node.state == DEPENDENCY_GRAPH_STATE_UNSUPPORTED)
    unsupported_edges = tuple(
        edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_UNSUPPORTED
    )
    blocked_edges = tuple(edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_BLOCKED)
    stale_edges = tuple(edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_STALE)
    prohibited_edges = tuple(
        edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_PROHIBITED
    )
    circular_edges = tuple(edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_CIRCULAR)
    lineage_gap_edges = tuple(
        edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_LINEAGE_GAP
    )
    provenance_gap_edges = tuple(
        edge.edge_id for edge in graph.edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP
    )
    hidden_node_count = sum(1 for node in graph.nodes if node.hidden)
    hidden_edge_count = sum(1 for edge in graph.edges if edge.hidden)
    invalid_node_count = node_counts["invalid"]
    invalid_edge_count = edge_counts["invalid"]
    node_execution_count = sum(
        1
        for node in graph.nodes
        if node.dependency_execution_enabled
        or node.automatic_dependency_resolution_enabled
        or node.remediation_enabled
        or node.runtime_mutation_enabled
        or node.silent_fallback_enabled
    )
    edge_execution_count = sum(
        1
        for edge in graph.edges
        if edge.dependency_execution_enabled
        or edge.automatic_dependency_resolution_enabled
        or edge.automatic_refresh_sequencing_enabled
        or edge.orchestration_enabled
        or edge.remediation_enabled
        or edge.planner_integration_enabled
        or edge.production_consumption_enabled
        or edge.runtime_mutation_enabled
        or edge.silent_fallback_enabled
    )
    visibility_unsupported_nodes = graph.unsupported_state_visibility.unsupported_dependency_nodes
    visibility_unsupported_edges = graph.unsupported_state_visibility.unsupported_dependency_edges
    visibility_stale_edges = graph.unsupported_state_visibility.stale_dependency_edges
    visibility_prohibited_edges = graph.unsupported_state_visibility.prohibited_dependency_edges
    visibility_circular_edges = graph.blocked_state_visibility.circular_dependency_edges
    visibility_lineage_discontinuity = graph.blocked_state_visibility.lineage_discontinuity_visibility
    visibility_provenance_discontinuity = graph.blocked_state_visibility.provenance_discontinuity_visibility
    visibility_replay_discontinuity = graph.blocked_state_visibility.replay_discontinuity_visibility
    visibility_rollback_discontinuity = graph.blocked_state_visibility.rollback_discontinuity_visibility
    prohibited_domains_visible = set(PROHIBITED_DEPENDENCY_DOMAINS).issubset(
        set(graph.unsupported_state_visibility.prohibited_dependency_domains)
    )
    visibility_failures = [
        bool(set(unsupported_nodes) - set(visibility_unsupported_nodes)),
        bool(set(unsupported_edges) - set(visibility_unsupported_edges)),
        bool(set(stale_edges) - set(visibility_stale_edges)),
        bool(set(prohibited_edges) - set(visibility_prohibited_edges)),
        bool(set(circular_edges) - set(visibility_circular_edges)),
        bool(set(lineage_gap_edges) and not visibility_lineage_discontinuity),
        bool(set(provenance_gap_edges) and not visibility_provenance_discontinuity),
        not prohibited_domains_visible,
    ]
    return {
        "node_state_counts": node_counts,
        "edge_state_counts": edge_counts,
        "fail_visible_dependency_edge_count": len(fail_visible_dependency_edge_ids(graph.edges)),
        "unsupported_dependency_node_visibility_count": len(visibility_unsupported_nodes),
        "unsupported_dependency_edge_visibility_count": len(visibility_unsupported_edges),
        "blocked_dependency_edge_visibility_count": len(graph.blocked_state_visibility.blocked_dependency_edges),
        "stale_dependency_edge_visibility_count": len(visibility_stale_edges),
        "prohibited_dependency_edge_visibility_count": len(visibility_prohibited_edges),
        "circular_dependency_visibility_count": len(visibility_circular_edges),
        "lineage_discontinuity_visibility_count": len(visibility_lineage_discontinuity),
        "provenance_discontinuity_visibility_count": len(visibility_provenance_discontinuity),
        "replay_discontinuity_visibility_count": len(visibility_replay_discontinuity),
        "rollback_discontinuity_visibility_count": len(visibility_rollback_discontinuity),
        "prohibited_dependency_domain_visibility_count": len(graph.unsupported_state_visibility.prohibited_dependency_domains),
        "diagnostics_warning_visibility_count": (
            len(graph.diagnostics_visibility.warning_visibility)
            + len(graph.diagnostics_visibility.blocker_visibility)
            + len(graph.diagnostics_visibility.circular_dependency_visibility)
            + len(graph.diagnostics_visibility.unsupported_dependency_visibility)
            + len(graph.diagnostics_visibility.prohibited_dependency_visibility)
            + len(graph.diagnostics_visibility.drift_visibility)
            + len(graph.diagnostics_visibility.integrity_visibility)
        ),
        "governance_limitation_count": len(graph.governance_visibility.explicit_limitations),
        "governance_prohibition_count": len(graph.governance_visibility.explicit_prohibitions),
        "hidden_node_count": hidden_node_count,
        "hidden_edge_count": hidden_edge_count,
        "invalid_dependency_node_state_count": invalid_node_count,
        "invalid_dependency_edge_state_count": invalid_edge_count,
        "node_execution_semantics_count": node_execution_count,
        "edge_execution_semantics_count": edge_execution_count,
        "unsupported_nodes_visible": not bool(set(unsupported_nodes) - set(visibility_unsupported_nodes)),
        "unsupported_edges_visible": not bool(set(unsupported_edges) - set(visibility_unsupported_edges)),
        "blocked_edges_visible": not bool(set(blocked_edges) - set(graph.blocked_state_visibility.blocked_dependency_edges)),
        "stale_edges_visible": not bool(set(stale_edges) - set(visibility_stale_edges)),
        "prohibited_edges_visible": not bool(set(prohibited_edges) - set(visibility_prohibited_edges)),
        "circular_dependencies_visible": not bool(set(circular_edges) - set(visibility_circular_edges)),
        "lineage_discontinuity_visible": bool(visibility_lineage_discontinuity),
        "provenance_discontinuity_visible": bool(visibility_provenance_discontinuity),
        "replay_discontinuity_visible": bool(visibility_replay_discontinuity),
        "rollback_discontinuity_visible": bool(visibility_rollback_discontinuity),
        "prohibited_dependency_domains_visible": prohibited_domains_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *graph.nodes,
                *graph.edges,
                *graph.lineage_chains,
                *graph.provenance_chains,
                graph.continuity_metadata,
                graph.replay_metadata,
                graph.rollback_metadata,
                graph.blocked_state_visibility,
                graph.unsupported_state_visibility,
                graph.drift_visibility,
                graph.diagnostics_visibility,
                graph.governance_visibility,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_node_count == 0
            and hidden_edge_count == 0
            and invalid_node_count == 0
            and invalid_edge_count == 0
            and node_execution_count == 0
            and edge_execution_count == 0
            and all(
                getattr(record, "descriptive_only", False)
                for record in (
                    *graph.nodes,
                    *graph.edges,
                    *graph.lineage_chains,
                    *graph.provenance_chains,
                    graph.continuity_metadata,
                    graph.replay_metadata,
                    graph.rollback_metadata,
                    graph.blocked_state_visibility,
                    graph.unsupported_state_visibility,
                    graph.drift_visibility,
                    graph.diagnostics_visibility,
                    graph.governance_visibility,
                )
            )
        ),
    }


def build_default_dependency_nodes() -> tuple[RefreshDependencyNode, ...]:
    return default_dependency_nodes()


def build_default_dependency_edges() -> tuple[RefreshDependencyEdge, ...]:
    return default_dependency_edges()


def build_default_refresh_dependency_graph() -> RefreshDependencyGraph:
    return default_refresh_dependency_graph()
