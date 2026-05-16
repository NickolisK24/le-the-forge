from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_hashing import (
    hash_v3_7_graph,
    hash_v3_7_graph_edge,
    hash_v3_7_graph_node,
    validate_v3_7_graph_hash_stability,
)
from app.runtime_orchestration.v3_7_graph_models import (
    V37GraphMetadataEntry,
    V37GraphNodeIdentity,
    default_v3_7_orchestration_planning_graph,
)


def test_deterministic_graph_hash_is_stable():
    graph = default_v3_7_orchestration_planning_graph()

    assert hash_v3_7_graph(graph) == hash_v3_7_graph(graph)
    assert validate_v3_7_graph_hash_stability(graph)["stable"] is True


def test_hash_excludes_timestamp_and_transient_metadata():
    graph = default_v3_7_orchestration_planning_graph()
    first = replace(
        graph,
        metadata=graph.metadata
        + (
            V37GraphMetadataEntry("generated_at", "2026-05-16T01:00:00+00:00", included_in_hash=False),
            V37GraphMetadataEntry("transient_memory_reference", "object-a", included_in_hash=False),
        ),
    )
    second = replace(
        graph,
        metadata=graph.metadata
        + (
            V37GraphMetadataEntry("generated_at", "2026-05-16T02:00:00+00:00", included_in_hash=False),
            V37GraphMetadataEntry("transient_memory_reference", "object-b", included_in_hash=False),
        ),
    )

    assert hash_v3_7_graph(first) == hash_v3_7_graph(second)


def test_hash_includes_node_and_edge_identity():
    graph = default_v3_7_orchestration_planning_graph()
    altered_node = replace(
        graph.nodes[0],
        identity=V37GraphNodeIdentity(
            node_id="v3_7_node_changed_identity",
            node_type=graph.nodes[0].identity.node_type,
            node_label=graph.nodes[0].identity.node_label,
            structural_purpose=graph.nodes[0].identity.structural_purpose,
        ),
    )
    altered = replace(graph, nodes=(altered_node,) + graph.nodes[1:])

    assert hash_v3_7_graph(graph) != hash_v3_7_graph(altered)
    assert hash_v3_7_graph_node(graph.nodes[0]) == hash_v3_7_graph_node(graph.nodes[0])
    assert hash_v3_7_graph_edge(graph.edges[0]) == hash_v3_7_graph_edge(graph.edges[0])
