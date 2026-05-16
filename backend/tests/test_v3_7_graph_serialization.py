from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from app.runtime_orchestration.v3_7_graph_models import default_v3_7_orchestration_planning_graph
from app.runtime_orchestration.v3_7_graph_serialization import (
    export_v3_7_graph,
    export_v3_7_graph_counts,
    serialize_v3_7_graph,
    validate_v3_7_graph_serialization_stability,
)
from scripts.report_v3_7_graph_foundations import build_v3_7_graph_foundations_report


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_deterministic_serialization_is_stable():
    graph = default_v3_7_orchestration_planning_graph()

    first = serialize_v3_7_graph(graph)
    second = serialize_v3_7_graph(graph)

    assert first == second
    assert validate_v3_7_graph_serialization_stability(graph)["stable"] is True
    assert json.loads(first)["identity"]["graph_id"] == graph.identity.graph_id


def test_serialization_sorts_nodes_edges_and_metadata():
    graph = default_v3_7_orchestration_planning_graph()
    reordered = replace(
        graph,
        metadata=tuple(reversed(graph.metadata)),
        nodes=tuple(reversed(graph.nodes)),
        edges=tuple(reversed(graph.edges)),
        explainability_evidence=tuple(reversed(graph.explainability_evidence)),
    )

    assert serialize_v3_7_graph(graph) == serialize_v3_7_graph(reordered)
    exported = export_v3_7_graph(reordered)
    assert [node["identity"]["node_id"] for node in exported["nodes"]] == sorted(
        node.identity.node_id for node in graph.nodes
    )
    assert [edge["identity"]["edge_id"] for edge in exported["edges"]] == sorted(
        edge.identity.edge_id for edge in graph.edges
    )
    assert [entry["metadata_key"] for entry in exported["metadata"]] == sorted(
        entry.metadata_key for entry in graph.metadata
    )


def test_graph_counts_are_deterministic():
    graph = default_v3_7_orchestration_planning_graph()

    assert export_v3_7_graph_counts(graph) == {
        "metadata_count": 4,
        "node_count": 3,
        "edge_count": 2,
        "governance_boundary_count": 2,
        "compatibility_boundary_count": 1,
        "blocker_count": 2,
        "unsupported_domain_count": 2,
        "prohibited_domain_count": 2,
        "explainability_evidence_count": 5,
        "continuity_evidence_count": 1,
    }


def test_report_generation_is_deterministic_and_non_executable():
    first = build_v3_7_graph_foundations_report(REPO_ROOT)
    second = build_v3_7_graph_foundations_report(REPO_ROOT)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["structural_orchestration_reasoning_only"] is True
    assert first["non_executable"] is True
    assert first["nodes_do_not_imply_executable_behavior"] is True
    assert first["edges_do_not_imply_execution_flow"] is True
    assert first["orchestration_execution_enabled"] is False
    assert first["runtime_dispatch_enabled"] is False
    assert first["routing_enabled"] is False
    assert first["scheduling_enabled"] is False
    assert first["coverage"]["deterministic_serialization_coverage"] is True
    assert first["coverage"]["deterministic_hashing_coverage"] is True
