from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from refresh_coordination.coordination_dependency_graph_diagnostics import (  # noqa: E402
    build_coordination_dependency_graph_diagnostics,
    coordination_dependency_graphs_equal,
    count_coordination_graph_edge_states,
    count_coordination_graph_node_states,
    validate_coordination_dependency_graph_non_execution,
    validate_coordination_manifest_compatibility,
    validate_dependency_direction_visibility,
    validate_dependency_graph_continuity,
    validate_dependency_graph_lineage_continuity,
    validate_dependency_graph_visibility,
)
from refresh_coordination.coordination_dependency_graph_hashing import (  # noqa: E402
    hash_coordination_dependency_graph,
    hash_coordination_dependency_graph_identity,
    hash_coordination_graph_edge,
    hash_coordination_graph_node,
)
from refresh_coordination.coordination_dependency_graph_models import (  # noqa: E402
    GRAPH_DEPENDENCY_STATE_BLOCKED,
    GRAPH_DEPENDENCY_STATE_PROHIBITED,
    GRAPH_DEPENDENCY_STATE_STALE,
    GRAPH_DEPENDENCY_STATE_SUPPORTED,
    GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
    V4_2_COORDINATION_DEPENDENCY_GRAPH_SCHEMA_VERSION,
    V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_STABLE,
    default_coordination_dependency_graph,
)
from refresh_coordination.coordination_dependency_graph_serialization import (  # noqa: E402
    export_coordination_dependency_graph,
    serialize_coordination_dependency_graph,
)
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from scripts.report_v4_2_coordination_dependency_graph_governance import (  # noqa: E402
    build_v4_2_coordination_dependency_graph_governance_report,
)


def test_v4_2_coordination_dependency_graph_models_are_immutable_and_non_executable():
    graph = default_coordination_dependency_graph()

    with pytest.raises(FrozenInstanceError):
        graph.dependency_resolution_enabled = True

    assert graph.identity.schema_version == V4_2_COORDINATION_DEPENDENCY_GRAPH_SCHEMA_VERSION
    assert graph.non_executable is True
    assert graph.descriptive_only is True
    assert graph.dependency_resolution_enabled is False
    assert graph.orchestration_execution_enabled is False
    assert graph.refresh_execution_enabled is False
    assert graph.planner_integration_enabled is False
    assert graph.production_consumption_enabled is False
    assert graph.production_bundle_consumption_enabled is False
    assert graph.runtime_mutation_enabled is False
    assert graph.remediation_enabled is False
    assert graph.automatic_correction_enabled is False
    assert graph.automatic_rollback_enabled is False
    assert graph.authorization_enabled is False
    assert graph.approval_enabled is False
    assert graph.ranking_enabled is False
    assert graph.scoring_enabled is False
    assert graph.selection_enabled is False
    assert all(not node.dependency_resolution_enabled for node in graph.nodes)
    assert all(not edge.dependency_resolution_enabled for edge in graph.edges)
    assert all(not diagnostic.execution_enabled for diagnostic in graph.diagnostics)


def test_v4_2_coordination_dependency_graph_serialization_and_hashing_are_stable():
    first = default_coordination_dependency_graph()
    second = default_coordination_dependency_graph()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_dependency_graphs_equal(first, second)
    assert serialize_coordination_dependency_graph(first) == serialize_coordination_dependency_graph(second)
    assert hash_coordination_dependency_graph(first) == hash_coordination_dependency_graph(second)
    assert hash_coordination_dependency_graph_identity(first.identity) == hash_coordination_dependency_graph_identity(
        second.identity
    )
    assert json.loads(serialize_coordination_dependency_graph(first))["non_executable"] is True


def test_v4_2_coordination_dependency_graph_node_and_edge_ordering_are_stable():
    graph = default_coordination_dependency_graph()
    reordered = replace(
        graph,
        nodes=tuple(reversed(graph.nodes)),
        edges=tuple(reversed(graph.edges)),
        lineage_references=tuple(reversed(graph.lineage_references)),
        continuity_references=tuple(reversed(graph.continuity_references)),
        diagnostics=tuple(reversed(graph.diagnostics)),
    )

    assert serialize_coordination_dependency_graph(graph) == serialize_coordination_dependency_graph(reordered)
    assert hash_coordination_dependency_graph(graph) == hash_coordination_dependency_graph(reordered)
    exported = export_coordination_dependency_graph(reordered)
    assert [node["node_state"] for node in exported["nodes"]] == [
        GRAPH_DEPENDENCY_STATE_SUPPORTED,
        GRAPH_DEPENDENCY_STATE_SUPPORTED,
        GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
        GRAPH_DEPENDENCY_STATE_BLOCKED,
        GRAPH_DEPENDENCY_STATE_PROHIBITED,
        GRAPH_DEPENDENCY_STATE_STALE,
    ]
    assert [edge["dependency_state"] for edge in exported["edges"]] == [
        GRAPH_DEPENDENCY_STATE_SUPPORTED,
        GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
        GRAPH_DEPENDENCY_STATE_BLOCKED,
        GRAPH_DEPENDENCY_STATE_PROHIBITED,
        GRAPH_DEPENDENCY_STATE_STALE,
    ]


def test_v4_2_coordination_dependency_graph_hashes_nodes_and_edges_deterministically():
    graph = default_coordination_dependency_graph()

    assert [hash_coordination_graph_node(node) for node in graph.nodes] == [
        hash_coordination_graph_node(node) for node in graph.nodes
    ]
    assert [hash_coordination_graph_edge(edge) for edge in graph.edges] == [
        hash_coordination_graph_edge(edge) for edge in graph.edges
    ]


def test_v4_2_coordination_dependency_graph_visibility_preserves_blocked_prohibited_and_unsupported_dependencies():
    graph = default_coordination_dependency_graph()
    visibility = validate_dependency_graph_visibility(graph)
    node_counts = count_coordination_graph_node_states(graph.nodes)
    edge_counts = count_coordination_graph_edge_states(graph.edges)

    assert node_counts[GRAPH_DEPENDENCY_STATE_BLOCKED] == 1
    assert node_counts[GRAPH_DEPENDENCY_STATE_PROHIBITED] == 1
    assert node_counts[GRAPH_DEPENDENCY_STATE_UNSUPPORTED] == 1
    assert edge_counts[GRAPH_DEPENDENCY_STATE_BLOCKED] == 1
    assert edge_counts[GRAPH_DEPENDENCY_STATE_PROHIBITED] == 1
    assert edge_counts[GRAPH_DEPENDENCY_STATE_UNSUPPORTED] == 1
    assert visibility["valid"] is True
    assert visibility["blocked_dependencies_visible"] is True
    assert visibility["prohibited_dependencies_visible"] is True
    assert visibility["unsupported_dependencies_visible"] is True
    assert visibility["stale_dependencies_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_coordination_dependency_direction_visibility_is_stable_and_non_executing():
    graph = default_coordination_dependency_graph()
    direction = validate_dependency_direction_visibility(graph)

    assert direction["valid"] is True
    assert direction["directional_edge_count"] == len(graph.edges)
    assert direction["missing_direction_ids"] == ()
    assert direction["reverse_dependency_visibility_count"] == 1
    assert direction["ambiguous_direction_visibility_count"] == 1
    assert direction["corrective_direction_count"] == 0


def test_v4_2_coordination_dependency_graph_lineage_and_continuity_visibility_are_preserved():
    graph = default_coordination_dependency_graph()
    lineage = validate_dependency_graph_lineage_continuity(graph)
    continuity = validate_dependency_graph_continuity(graph)

    with pytest.raises(FrozenInstanceError):
        graph.lineage_references[0].inferred_lineage_enabled = True

    assert lineage["valid"] is True
    assert lineage["lineage_reference_count"] == 1
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["corrective_lineage_count"] == 0
    assert continuity["valid"] is True
    assert continuity["continuity_reference_count"] == 1
    assert continuity["continuity_preserved"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_safe"] is True
    assert continuity["lineage_safe"] is True


def test_v4_2_coordination_dependency_graph_is_manifest_compatible():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    compatibility = validate_coordination_manifest_compatibility(graph, manifest)

    assert compatibility["valid"] is True
    assert compatibility["graph_source_manifest_reference"] == manifest.identity.manifest_id
    assert compatibility["graph_compatibility_manifest_reference"] == manifest.identity.manifest_id
    assert compatibility["manifest_hash_matches"] is True


def test_v4_2_coordination_dependency_graph_non_execution_validation_blocks_resolution_and_execution_flags():
    graph = default_coordination_dependency_graph()
    contaminated = replace(
        graph,
        dependency_resolution_enabled=True,
        orchestration_execution_enabled=True,
        refresh_execution_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        remediation_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_coordination_dependency_graph_non_execution(contaminated)

    assert validate_coordination_dependency_graph_non_execution(graph)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 7
    assert validation["dependency_resolution_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["remediation_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_coordination_dependency_graph_report_contains_required_evidence_and_boundaries():
    diagnostics = build_coordination_dependency_graph_diagnostics()
    report = build_v4_2_coordination_dependency_graph_governance_report()

    assert report["foundation_status"] == V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_STABLE
    assert report["graph_mode"] == "descriptive_only_non_executable"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_node_ordering_verified"] is True
    assert report["summary"]["stable_edge_ordering_verified"] is True
    assert report["summary"]["dependency_direction_visibility_verified"] is True
    assert report["summary"]["blocked_dependency_visibility_verified"] is True
    assert report["summary"]["prohibited_dependency_visibility_verified"] is True
    assert report["summary"]["unsupported_dependency_visibility_verified"] is True
    assert report["summary"]["lineage_continuity_verified"] is True
    assert report["summary"]["coordination_manifest_compatibility_verified"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
