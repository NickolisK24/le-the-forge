from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.runtime_orchestration.v3_7_graph_identity import (
    build_v3_7_edge_identity,
    build_v3_7_graph_identity,
    build_v3_7_node_identity,
    edge_identity_key,
    graph_identity_key,
    identity_values_are_unique,
    node_identity_key,
)
from app.runtime_orchestration.v3_7_graph_models import (
    V3_7_GRAPH_FOUNDATIONS_PHASE_ID,
    V3_7_GRAPH_SCHEMA_VERSION,
    V3_7_STRUCTURAL_REASONING_ONLY,
    default_v3_7_orchestration_planning_graph,
)


def test_default_graph_models_are_immutable_and_non_executable():
    graph = default_v3_7_orchestration_planning_graph()

    with pytest.raises(FrozenInstanceError):
        graph.graph_execution_enabled = True

    assert graph.identity.schema_version == V3_7_GRAPH_SCHEMA_VERSION
    assert graph.identity.phase_id == V3_7_GRAPH_FOUNDATIONS_PHASE_ID
    assert graph.planning_only is True
    assert graph.structural_reasoning_only is True
    assert graph.non_executable is True
    assert graph.graph_execution_enabled is False
    assert graph.graph_traversal_execution_enabled is False
    assert graph.runtime_dispatch_enabled is False
    assert graph.scheduling_enabled is False
    assert graph.routing_enabled is False
    assert graph.mutation_enabled is False
    assert graph.persistent_runtime_writes_enabled is False
    assert graph.background_processing_enabled is False
    assert graph.optimization_enabled is False
    assert graph.recommendation_enabled is False
    assert graph.autonomous_orchestration_enabled is False
    assert all(node.node_executable is False and node.action_enabled is False for node in graph.nodes)
    assert all(
        edge.edge_executable is False
        and edge.traversal_enabled is False
        and edge.execution_flow_enabled is False
        for edge in graph.edges
    )


def test_default_graph_contains_required_structural_domains():
    graph = default_v3_7_orchestration_planning_graph()

    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2
    assert len(graph.governance_boundaries) == 2
    assert len(graph.compatibility_boundaries) == 1
    assert len(graph.unsupported_domains) == 2
    assert len(graph.prohibited_domains) == 2
    assert len(graph.explainability_evidence) == 5
    assert len(graph.continuity_evidence) == 1
    assert all("execution" in finding.reason or "routing" in finding.reason for finding in graph.prohibited_domains)


def test_identity_helpers_are_deterministic():
    graph_identity = build_v3_7_graph_identity("graph-a")
    node_identity = build_v3_7_node_identity("node-a", "structural_boundary", "Node A")
    edge_identity = build_v3_7_edge_identity("edge-a", "node-a", "node-b", "structural_reference")

    assert graph_identity.structural_purpose == V3_7_STRUCTURAL_REASONING_ONLY
    assert graph_identity_key(graph_identity) == "v3_7.orchestration_planning_graph.1|v3_7_graph_foundations|v3.7|graph-a"
    assert node_identity_key(node_identity) == "structural_boundary|node-a"
    assert edge_identity_key(edge_identity) == "structural_reference|node-a|node-b|edge-a"
    assert identity_values_are_unique(("node-a", "node-b")) is True
    assert identity_values_are_unique(("node-a", "node-a")) is False
