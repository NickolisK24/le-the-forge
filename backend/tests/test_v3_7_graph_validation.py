from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_models import (
    V3_7_VISIBILITY_GAP,
    V37GraphEdgeIdentity,
    default_v3_7_orchestration_planning_graph,
)
from app.runtime_orchestration.v3_7_graph_validation import (
    V37_GRAPH_BLOCKED_BY_DUPLICATE_EDGE_IDENTITY,
    V37_GRAPH_BLOCKED_BY_DUPLICATE_NODE_IDENTITY,
    V37_GRAPH_BLOCKED_BY_INVALID_EDGE_REFERENCE,
    V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE,
    V37_GRAPH_BLOCKED_BY_UNSUPPORTED_STATE_VISIBILITY_GAP,
    V37_GRAPH_PROHIBITED_STATE_VISIBLE,
    V37_GRAPH_UNSUPPORTED_STATE_VISIBLE,
    V37_GRAPH_VALIDATION_BLOCKED,
    V37_GRAPH_VALIDATION_STABLE,
    validate_v3_7_graph,
)


def _statuses(result):
    return {finding.status for finding in result.findings}


def test_default_graph_validation_is_stable_with_visible_boundaries():
    result = validate_v3_7_graph(default_v3_7_orchestration_planning_graph())

    assert result.validation_status == V37_GRAPH_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 4
    assert result.unsupported_state_visible_count == 2
    assert result.prohibited_state_visible_count == 2
    assert result.serialization_stable is True
    assert result.hash_stable is True
    assert result.governance_continuity_preserved is True
    assert result.provenance_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.non_execution_guarantee_preserved is True
    assert V37_GRAPH_UNSUPPORTED_STATE_VISIBLE in _statuses(result)
    assert V37_GRAPH_PROHIBITED_STATE_VISIBLE in _statuses(result)


def test_duplicate_identity_rejection_is_fail_visible():
    graph = default_v3_7_orchestration_planning_graph()
    duplicate_nodes = replace(graph, nodes=graph.nodes + (graph.nodes[0],))
    duplicate_edges = replace(graph, edges=graph.edges + (graph.edges[0],))

    node_result = validate_v3_7_graph(duplicate_nodes)
    edge_result = validate_v3_7_graph(duplicate_edges)

    assert node_result.validation_status == V37_GRAPH_VALIDATION_BLOCKED
    assert node_result.duplicate_node_identity_count == 1
    assert V37_GRAPH_BLOCKED_BY_DUPLICATE_NODE_IDENTITY in _statuses(node_result)
    assert edge_result.validation_status == V37_GRAPH_VALIDATION_BLOCKED
    assert edge_result.duplicate_edge_identity_count == 1
    assert V37_GRAPH_BLOCKED_BY_DUPLICATE_EDGE_IDENTITY in _statuses(edge_result)


def test_invalid_edge_reference_rejection_is_fail_visible():
    graph = default_v3_7_orchestration_planning_graph()
    invalid_edge = replace(
        graph.edges[0],
        identity=V37GraphEdgeIdentity(
            edge_id=graph.edges[0].identity.edge_id,
            source_node_id=graph.edges[0].identity.source_node_id,
            target_node_id="missing-target-node",
            relationship_type=graph.edges[0].identity.relationship_type,
            structural_purpose=graph.edges[0].identity.structural_purpose,
        ),
    )
    result = validate_v3_7_graph(replace(graph, edges=(invalid_edge,) + graph.edges[1:]))

    assert result.validation_status == V37_GRAPH_VALIDATION_BLOCKED
    assert result.invalid_edge_reference_count == 1
    assert V37_GRAPH_BLOCKED_BY_INVALID_EDGE_REFERENCE in _statuses(result)


def test_prohibited_execution_states_are_rejected():
    graph = default_v3_7_orchestration_planning_graph()
    executable_node = replace(graph.nodes[0], node_executable=True)
    executable_edge = replace(graph.edges[0], traversal_enabled=True)
    result = validate_v3_7_graph(
        replace(
            graph,
            nodes=(executable_node,) + graph.nodes[1:],
            edges=(executable_edge,) + graph.edges[1:],
            graph_execution_enabled=True,
            routing_enabled=True,
            scheduling_enabled=True,
        )
    )

    assert result.validation_status == V37_GRAPH_VALIDATION_BLOCKED
    assert result.non_execution_guarantee_preserved is False
    assert V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE in _statuses(result)


def test_unsupported_visibility_gap_is_rejected():
    graph = default_v3_7_orchestration_planning_graph()
    hidden_unsupported = replace(graph.unsupported_domains[0], visibility_status=V3_7_VISIBILITY_GAP)
    result = validate_v3_7_graph(replace(graph, unsupported_domains=(hidden_unsupported,) + graph.unsupported_domains[1:]))

    assert result.validation_status == V37_GRAPH_VALIDATION_BLOCKED
    assert V37_GRAPH_BLOCKED_BY_UNSUPPORTED_STATE_VISIBILITY_GAP in _statuses(result)
