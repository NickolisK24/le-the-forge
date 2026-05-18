from __future__ import annotations

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

from orchestration_governance.orchestration_manifest_hashing import hash_orchestration_manifest  # noqa: E402
from orchestration_governance.orchestration_manifest_models import default_orchestration_manifest  # noqa: E402
from orchestration_governance.orchestration_topology_diagnostics import (  # noqa: E402
    aggregate_blocked_relationships,
    aggregate_conflicting_relationships,
    aggregate_missing_metadata_relationships,
    aggregate_prohibited_relationships,
    aggregate_stale_relationships,
    aggregate_unsupported_relationships,
    build_orchestration_topology_diagnostics,
    count_topology_edge_states,
    count_topology_node_states,
    count_topology_relationship_states,
    topologies_equal,
    topology_identity_key,
    validate_topology_continuity,
    validate_topology_explainability,
    validate_topology_metadata,
    validate_topology_non_execution,
    validate_topology_relationship_visibility,
    validate_topology_structure,
)
from orchestration_governance.orchestration_topology_hashing import (  # noqa: E402
    hash_orchestration_topology,
    hash_orchestration_topology_edge,
    hash_orchestration_topology_node,
    hash_orchestration_topology_relationship,
)
from orchestration_governance.orchestration_topology_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_TOPOLOGY_PROHIBITIONS,
    TOPOLOGY_STATE_BLOCKED,
    TOPOLOGY_STATE_CONFLICTING,
    TOPOLOGY_STATE_MISSING_METADATA,
    TOPOLOGY_STATE_PROHIBITED,
    TOPOLOGY_STATE_STALE,
    TOPOLOGY_STATE_SUPPORTED,
    TOPOLOGY_STATE_UNSUPPORTED,
    V4_3_ORCHESTRATION_TOPOLOGY_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_TOPOLOGY_STATUS_STABLE,
    default_orchestration_topology,
)
from orchestration_governance.orchestration_topology_serialization import (  # noqa: E402
    export_orchestration_topology,
    serialize_orchestration_topology,
)
from scripts.report_v4_3_orchestration_topology_visibility import (  # noqa: E402
    build_v4_3_orchestration_topology_visibility_report,
)


def test_v4_3_topology_models_are_immutable_and_non_executable():
    topology = default_orchestration_topology()

    with pytest.raises(FrozenInstanceError):
        topology.traversal_enabled = True

    assert topology.identity.schema_version == V4_3_ORCHESTRATION_TOPOLOGY_SCHEMA_VERSION
    assert topology.identity.source_manifest_reference == default_orchestration_manifest().identity.manifest_id
    assert topology.identity.source_manifest_hash_reference == hash_orchestration_manifest(
        default_orchestration_manifest()
    )
    assert topology.non_executable is True
    assert topology.descriptive_only is True
    assert topology.traversal_enabled is False
    assert topology.graph_execution_enabled is False
    assert topology.orchestration_execution_enabled is False
    assert topology.runtime_execution_enabled is False
    assert topology.routing_execution_enabled is False
    assert topology.scheduling_execution_enabled is False
    assert topology.sequencing_execution_enabled is False
    assert topology.dependency_resolution_enabled is False
    assert topology.route_selection_enabled is False
    assert topology.planner_integration_enabled is False
    assert topology.production_consumption_enabled is False
    assert topology.runtime_mutation_enabled is False
    assert topology.operational_state_mutation_enabled is False
    assert topology.graph_engine_enabled is False
    assert topology.traversal_engine_enabled is False
    assert topology.routing_engine_enabled is False
    assert topology.dependency_resolver_enabled is False
    assert all(not relationship.traversal_enabled for relationship in topology.relationships)
    assert all(not relationship.routable for relationship in topology.relationships)
    assert all(not relationship.resolvable for relationship in topology.relationships)
    assert all(not diagnostic.repair_enabled for diagnostic in topology.diagnostics)


def test_v4_3_topology_identity_key_is_stable():
    topology = default_orchestration_topology()

    assert topology_identity_key(topology) == (
        "v4_3.orchestration_topology_visibility.1"
        "|v4_3_orchestration_topology_primary"
        "|v4.3.0-phase-2"
        "|v4_3_orchestration_manifest_primary"
        f"|{hash_orchestration_manifest(default_orchestration_manifest())}"
        "|v4_3_orchestration_topology_governance_primary"
        "|v4_3_orchestration_topology_lineage_primary"
        "|v4_3_orchestration_topology_provenance_primary"
    )


def test_v4_3_topology_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_topology()
    second = default_orchestration_topology()

    assert first == second
    assert hash(first) == hash(second)
    assert topologies_equal(first, second)
    assert serialize_orchestration_topology(first) == serialize_orchestration_topology(second)
    assert hash_orchestration_topology(first) == hash_orchestration_topology(second)


def test_v4_3_topology_ordering_stability_survives_reordered_collections():
    topology = default_orchestration_topology()
    reordered = replace(
        topology,
        nodes=tuple(reversed(topology.nodes)),
        edges=tuple(reversed(topology.edges)),
        relationships=tuple(reversed(topology.relationships)),
        continuity_metadata=tuple(reversed(topology.continuity_metadata)),
        diagnostics=tuple(reversed(topology.diagnostics)),
        explainability_summaries=tuple(reversed(topology.explainability_summaries)),
    )

    assert serialize_orchestration_topology(topology) == serialize_orchestration_topology(reordered)
    assert hash_orchestration_topology(topology) == hash_orchestration_topology(reordered)
    exported = export_orchestration_topology(reordered)
    assert [item["node_state"] for item in exported["nodes"]] == [
        TOPOLOGY_STATE_SUPPORTED,
        TOPOLOGY_STATE_SUPPORTED,
        TOPOLOGY_STATE_UNSUPPORTED,
        TOPOLOGY_STATE_BLOCKED,
        TOPOLOGY_STATE_STALE,
        TOPOLOGY_STATE_CONFLICTING,
        TOPOLOGY_STATE_MISSING_METADATA,
        TOPOLOGY_STATE_PROHIBITED,
    ]
    assert [item["edge_state"] for item in exported["edges"]] == [
        TOPOLOGY_STATE_SUPPORTED,
        TOPOLOGY_STATE_UNSUPPORTED,
        TOPOLOGY_STATE_BLOCKED,
        TOPOLOGY_STATE_STALE,
        TOPOLOGY_STATE_CONFLICTING,
        TOPOLOGY_STATE_MISSING_METADATA,
        TOPOLOGY_STATE_PROHIBITED,
    ]
    assert [item["relationship_state"] for item in exported["relationships"]] == [
        TOPOLOGY_STATE_SUPPORTED,
        TOPOLOGY_STATE_UNSUPPORTED,
        TOPOLOGY_STATE_BLOCKED,
        TOPOLOGY_STATE_STALE,
        TOPOLOGY_STATE_CONFLICTING,
        TOPOLOGY_STATE_MISSING_METADATA,
        TOPOLOGY_STATE_PROHIBITED,
    ]


def test_v4_3_topology_visibility_counts_are_fail_visible():
    topology = default_orchestration_topology()
    visibility = validate_topology_relationship_visibility(topology)

    assert count_topology_node_states(topology.nodes)[TOPOLOGY_STATE_UNSUPPORTED] == 1
    assert count_topology_edge_states(topology.edges)[TOPOLOGY_STATE_PROHIBITED] == 1
    assert count_topology_relationship_states(topology.relationships)[TOPOLOGY_STATE_BLOCKED] == 1
    assert visibility["valid"] is True
    assert visibility["unsupported_relationships_visible"] is True
    assert visibility["prohibited_relationships_visible"] is True
    assert visibility["blocked_relationships_visible"] is True
    assert visibility["stale_relationships_visible"] is True
    assert visibility["conflicting_relationships_visible"] is True
    assert visibility["missing_metadata_relationships_visible"] is True
    assert visibility["boundary_relationships_visible"] is True
    assert visibility["executable_relationship_ids"] == ()


def test_v4_3_topology_diagnostics_detect_duplicate_nodes_and_edges():
    topology = default_orchestration_topology()
    duplicate_node = replace(topology.nodes[0], deterministic_order=999)
    duplicate_edge = replace(topology.edges[0], deterministic_order=999)
    contaminated = replace(
        topology,
        nodes=topology.nodes + (duplicate_node,),
        edges=topology.edges + (duplicate_edge,),
    )
    validation = validate_topology_structure(contaminated)

    assert validation["valid"] is False
    assert validation["duplicate_node_ids"] == (topology.nodes[0].node_id,)
    assert validation["duplicate_edge_ids"] == (topology.edges[0].edge_id,)


def test_v4_3_topology_diagnostics_detect_unknown_and_missing_endpoints():
    topology = default_orchestration_topology()
    unknown_source = replace(
        topology.edges[0],
        edge_id="v4_3_topology_edge_unknown_source",
        source_node_id="missing_source_node",
        deterministic_order=900,
    )
    unknown_target = replace(
        topology.edges[1],
        edge_id="v4_3_topology_edge_unknown_target",
        target_node_id="missing_target_node",
        deterministic_order=901,
    )
    missing_source = replace(
        topology.edges[2],
        edge_id="v4_3_topology_edge_missing_source",
        source_node_id="",
        deterministic_order=902,
    )
    missing_target = replace(
        topology.edges[3],
        edge_id="v4_3_topology_edge_missing_target",
        target_node_id="",
        deterministic_order=903,
    )
    contaminated = replace(
        topology,
        edges=topology.edges + (unknown_source, unknown_target, missing_source, missing_target),
    )
    validation = validate_topology_structure(contaminated)

    assert validation["valid"] is False
    assert validation["unknown_source_edge_ids"] == ("v4_3_topology_edge_unknown_source",)
    assert validation["unknown_target_edge_ids"] == ("v4_3_topology_edge_unknown_target",)
    assert validation["missing_source_edge_ids"] == ("v4_3_topology_edge_missing_source",)
    assert validation["missing_target_edge_ids"] == ("v4_3_topology_edge_missing_target",)


def test_v4_3_topology_diagnostics_detect_self_reference_when_prohibited():
    topology = default_orchestration_topology()
    self_edge = replace(
        topology.edges[0],
        edge_id="v4_3_topology_edge_self_reference",
        source_node_id=topology.nodes[0].node_id,
        target_node_id=topology.nodes[0].node_id,
        deterministic_order=900,
    )
    contaminated = replace(topology, edges=topology.edges + (self_edge,))
    validation = validate_topology_structure(contaminated)

    assert validation["valid"] is False
    assert validation["self_referential_edge_ids"] == ("v4_3_topology_edge_self_reference",)


def test_v4_3_topology_relationship_aggregation_is_deterministic():
    topology = default_orchestration_topology()
    diagnostics = build_orchestration_topology_diagnostics(topology)

    assert aggregate_unsupported_relationships(topology) == diagnostics["unsupported_relationship_ids"]
    assert aggregate_prohibited_relationships(topology) == diagnostics["prohibited_relationship_ids"]
    assert aggregate_blocked_relationships(topology) == diagnostics["blocked_relationship_ids"]
    assert aggregate_stale_relationships(topology) == diagnostics["stale_relationship_ids"]
    assert aggregate_conflicting_relationships(topology) == diagnostics["conflicting_relationship_ids"]
    assert aggregate_missing_metadata_relationships(topology) == diagnostics["missing_metadata_relationship_ids"]
    assert diagnostics["repair_absent"] is True
    assert diagnostics["inference_absent"] is True
    assert diagnostics["auto_correction_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["execution_absent"] is True
    assert diagnostics["selection_systems_absent"] is True


def test_v4_3_topology_metadata_continuity_and_explainability_are_valid():
    topology = default_orchestration_topology()
    metadata = validate_topology_metadata(topology)
    continuity = validate_topology_continuity(topology)
    explainability = validate_topology_explainability(topology)

    assert metadata["valid"] is True
    assert metadata["governance_metadata_present"] is True
    assert metadata["lineage_metadata_present"] is True
    assert metadata["provenance_metadata_present"] is True
    assert metadata["continuity_metadata_present"] is True
    assert continuity["valid"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert explainability["valid"] is True
    assert "traversal_unavailable" in explainability["explainability_categories"]
    assert "routing_unavailable" in explainability["explainability_categories"]
    assert "dependency_resolution_unavailable" in explainability["explainability_categories"]
    assert "execution_disabled" in explainability["explainability_categories"]


def test_v4_3_topology_non_execution_validation_blocks_operational_flags():
    topology = default_orchestration_topology()
    contaminated = replace(
        topology,
        traversal_enabled=True,
        graph_execution_enabled=True,
        routing_execution_enabled=True,
        scheduling_execution_enabled=True,
        sequencing_execution_enabled=True,
        dependency_resolution_enabled=True,
        route_selection_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_topology_non_execution(contaminated)

    assert validate_topology_non_execution(topology)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 9
    assert validation["traversal_disabled"] is False
    assert validation["graph_execution_disabled"] is False
    assert validation["routing_execution_disabled"] is False
    assert validation["scheduling_execution_disabled"] is False
    assert validation["sequencing_execution_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["route_selection_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_3_topology_report_generation_and_report_hash_are_stable():
    first = build_v4_3_orchestration_topology_visibility_report()
    second = build_v4_3_orchestration_topology_visibility_report()

    assert first == second
    assert first["topology_visibility_status"] == V4_3_ORCHESTRATION_TOPOLOGY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["node_ordering_verified"] is True
    assert first["summary"]["edge_ordering_verified"] is True
    assert first["summary"]["relationship_ordering_verified"] is True
    assert first["summary"]["replay_safe_status"] is True
    assert first["summary"]["rollback_safe_status"] is True
    assert first["summary"]["non_execution_enforcement_validated"] is True
    assert first["summary"]["traversal_disabled"] is True
    assert first["summary"]["routing_execution_disabled"] is True
    assert first["summary"]["dependency_resolution_disabled"] is True
    assert first["summary"]["graph_engine_absent"] is True
    assert first["summary"]["traversal_engine_absent"] is True
    assert first["summary"]["routing_engine_absent"] is True
    assert first["summary"]["dependency_resolver_absent"] is True
    assert "No graph engine exists." in EXPLICIT_ORCHESTRATION_TOPOLOGY_PROHIBITIONS
    assert "No traversal engine exists." in first["explicit_prohibitions"]


def test_v4_3_topology_hashes_for_nodes_edges_and_relationships_are_stable():
    topology = default_orchestration_topology()

    assert [hash_orchestration_topology_node(node) for node in topology.nodes] == [
        hash_orchestration_topology_node(node) for node in topology.nodes
    ]
    assert [hash_orchestration_topology_edge(edge) for edge in topology.edges] == [
        hash_orchestration_topology_edge(edge) for edge in topology.edges
    ]
    assert [hash_orchestration_topology_relationship(relationship) for relationship in topology.relationships] == [
        hash_orchestration_topology_relationship(relationship) for relationship in topology.relationships
    ]
