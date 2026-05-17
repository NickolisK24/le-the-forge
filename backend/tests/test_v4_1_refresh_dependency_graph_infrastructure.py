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

from operational_refresh.refresh_dependency_graph_continuity import (  # noqa: E402
    validate_dependency_graph_continuity,
)
from operational_refresh.refresh_dependency_graph_diagnostics import (  # noqa: E402
    build_dependency_graph_diagnostics,
)
from operational_refresh.refresh_dependency_graph_hashing import (  # noqa: E402
    hash_dependency_graph_identity,
    hash_refresh_dependency_graph,
)
from operational_refresh.refresh_dependency_graph_integrity import (  # noqa: E402
    dependency_graph_identities_equal,
    dependency_graph_identity_key,
    refresh_dependency_graphs_equal,
    validate_dependency_graph_integrity,
    validate_dependency_graph_non_execution,
)
from operational_refresh.refresh_dependency_graph_models import (  # noqa: E402
    DEPENDENCY_GRAPH_STATE_BLOCKED,
    DEPENDENCY_GRAPH_STATE_CIRCULAR,
    DEPENDENCY_GRAPH_STATE_LINEAGE_GAP,
    DEPENDENCY_GRAPH_STATE_PROHIBITED,
    DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP,
    DEPENDENCY_GRAPH_STATE_STALE,
    DEPENDENCY_GRAPH_STATE_SUPPORTED,
    DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
    PROHIBITED_DEPENDENCY_DOMAINS,
    V4_1_REFRESH_DEPENDENCY_GRAPH_SCHEMA_VERSION,
    V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE,
    default_refresh_dependency_graph,
)
from operational_refresh.refresh_dependency_graph_serialization import (  # noqa: E402
    export_refresh_dependency_graph,
    serialize_refresh_dependency_graph,
)
from operational_refresh.refresh_dependency_graph_visibility import (  # noqa: E402
    count_dependency_edge_states,
    count_dependency_node_states,
    validate_refresh_dependency_visibility,
)
from scripts.report_v4_1_refresh_dependency_graph_infrastructure import (  # noqa: E402
    build_v4_1_refresh_dependency_graph_diagnostics_report,
    build_v4_1_refresh_dependency_graph_integrity_report,
    build_v4_1_refresh_dependency_graph_report,
)


def test_v4_1_dependency_graph_models_are_immutable_and_non_executable():
    graph = default_refresh_dependency_graph()

    with pytest.raises(FrozenInstanceError):
        graph.dependency_execution_enabled = True

    assert graph.identity.schema_version == V4_1_REFRESH_DEPENDENCY_GRAPH_SCHEMA_VERSION
    assert graph.non_executable is True
    assert graph.descriptive_only is True
    assert graph.refresh_execution_enabled is False
    assert graph.graph_execution_enabled is False
    assert graph.dependency_execution_enabled is False
    assert graph.orchestration_enabled is False
    assert graph.automatic_refresh_sequencing_enabled is False
    assert graph.automatic_dependency_resolution_enabled is False
    assert graph.automatic_migration_enabled is False
    assert graph.automatic_rollback_enabled is False
    assert graph.automatic_recovery_enabled is False
    assert graph.planner_integration_enabled is False
    assert graph.production_consumption_enabled is False
    assert graph.remediation_enabled is False
    assert graph.optimization_enabled is False
    assert graph.recommendation_enabled is False
    assert graph.ranking_enabled is False
    assert graph.scoring_enabled is False
    assert graph.selection_enabled is False
    assert graph.authorization_enabled is False
    assert graph.approval_enabled is False
    assert graph.runtime_mutation_enabled is False
    assert graph.hidden_orchestration_behavior_enabled is False
    assert graph.implicit_execution_pathway_enabled is False
    assert graph.silent_dependency_fallback_enabled is False
    assert all(not node.dependency_execution_enabled for node in graph.nodes)
    assert all(not edge.dependency_execution_enabled for edge in graph.edges)
    assert all(not edge.automatic_dependency_resolution_enabled for edge in graph.edges)
    assert all(not edge.automatic_refresh_sequencing_enabled for edge in graph.edges)
    assert all(not edge.orchestration_enabled for edge in graph.edges)
    assert graph.governance_visibility.production_consumption_enabled is False
    assert graph.governance_visibility.planner_integration_enabled is False


def test_v4_1_dependency_graph_identity_key_is_stable():
    graph = default_refresh_dependency_graph()

    assert dependency_graph_identity_key(graph.identity) == (
        "v4_1.refresh_dependency_graph_infrastructure.1"
        "|v4_1_phase_2_refresh_dependency_graph_infrastructure"
        "|v4_1_refresh_dependency_graph_primary|v4.1.0-phase-2"
        "|v4_1_refresh_manifest_primary"
        "|v4_1_refresh_dependency_graph_provenance_primary"
        "|v4_1_refresh_dependency_graph_lineage_primary"
    )


def test_v4_1_dependency_graph_serialization_hashing_and_equality_are_stable():
    first = default_refresh_dependency_graph()
    second = default_refresh_dependency_graph()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_dependency_graphs_equal(first, second)
    assert dependency_graph_identities_equal(first.identity, second.identity)
    assert serialize_refresh_dependency_graph(first) == serialize_refresh_dependency_graph(second)
    assert hash_refresh_dependency_graph(first) == hash_refresh_dependency_graph(second)
    assert hash_dependency_graph_identity(first.identity) == hash_dependency_graph_identity(second.identity)
    assert json.loads(serialize_refresh_dependency_graph(first))["non_executable"] is True


def test_v4_1_dependency_graph_serialization_preserves_order_and_fail_visible_relationships():
    graph = default_refresh_dependency_graph()
    reordered = replace(
        graph,
        nodes=tuple(reversed(graph.nodes)),
        edges=tuple(reversed(graph.edges)),
        lineage_chains=tuple(reversed(graph.lineage_chains)),
        provenance_chains=tuple(reversed(graph.provenance_chains)),
    )

    assert serialize_refresh_dependency_graph(graph) == serialize_refresh_dependency_graph(reordered)
    assert hash_refresh_dependency_graph(graph) == hash_refresh_dependency_graph(reordered)
    exported = export_refresh_dependency_graph(reordered)
    assert [item["relationship_state"] for item in exported["edges"]] == [
        DEPENDENCY_GRAPH_STATE_SUPPORTED,
        DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
        DEPENDENCY_GRAPH_STATE_PROHIBITED,
        DEPENDENCY_GRAPH_STATE_BLOCKED,
        DEPENDENCY_GRAPH_STATE_CIRCULAR,
        DEPENDENCY_GRAPH_STATE_STALE,
        DEPENDENCY_GRAPH_STATE_LINEAGE_GAP,
        DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP,
    ]
    assert exported["blocked_state_visibility"]["blocked_dependency_edges"] == [
        "v4_1_edge_manifest_to_blocked_dependency_gap"
    ]
    assert exported["blocked_state_visibility"]["circular_dependency_edges"] == [
        "v4_1_edge_future_provider_to_manifest_circular_visibility"
    ]
    assert exported["unsupported_state_visibility"]["unsupported_dependency_edges"] == [
        "v4_1_edge_manifest_to_future_provider"
    ]
    assert exported["unsupported_state_visibility"]["stale_dependency_edges"] == [
        "v4_1_edge_manifest_to_stale_lifecycle_dependency"
    ]
    assert exported["unsupported_state_visibility"]["prohibited_dependency_edges"] == [
        "v4_1_edge_manifest_to_production_runtime_bundle"
    ]


def test_v4_1_dependency_visibility_preserves_blocked_unsupported_circular_and_prohibited_state():
    graph = default_refresh_dependency_graph()
    visibility = validate_refresh_dependency_visibility(graph)
    node_counts = count_dependency_node_states(graph.nodes)
    edge_counts = count_dependency_edge_states(graph.edges)

    assert node_counts[DEPENDENCY_GRAPH_STATE_SUPPORTED] == 2
    assert node_counts[DEPENDENCY_GRAPH_STATE_UNSUPPORTED] == 1
    assert node_counts[DEPENDENCY_GRAPH_STATE_PROHIBITED] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_SUPPORTED] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_UNSUPPORTED] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_PROHIBITED] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_BLOCKED] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_CIRCULAR] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_STALE] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_LINEAGE_GAP] == 1
    assert edge_counts[DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP] == 1
    assert visibility["valid"] is True
    assert visibility["unsupported_nodes_visible"] is True
    assert visibility["unsupported_edges_visible"] is True
    assert visibility["blocked_edges_visible"] is True
    assert visibility["stale_edges_visible"] is True
    assert visibility["prohibited_edges_visible"] is True
    assert visibility["circular_dependencies_visible"] is True
    assert visibility["lineage_discontinuity_visible"] is True
    assert visibility["provenance_discontinuity_visible"] is True
    assert visibility["replay_discontinuity_visible"] is True
    assert visibility["rollback_discontinuity_visible"] is True
    assert visibility["prohibited_dependency_domains_visible"] is True
    assert visibility["prohibited_dependency_domain_visibility_count"] == len(PROHIBITED_DEPENDENCY_DOMAINS)
    assert visibility["node_execution_semantics_count"] == 0
    assert visibility["edge_execution_semantics_count"] == 0


def test_v4_1_dependency_continuity_preserves_lineage_provenance_replay_and_rollback():
    graph = default_refresh_dependency_graph()
    continuity = validate_dependency_graph_continuity(graph)

    with pytest.raises(FrozenInstanceError):
        graph.lineage_chains[0].automatic_lineage_repair_enabled = True

    assert continuity["valid"] is True
    assert continuity["lineage_continuity_valid"] is True
    assert continuity["provenance_continuity_valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True
    assert continuity["lineage_continuity"]["lineage_discontinuity_visibility_count"] == 1
    assert continuity["provenance_continuity"]["provenance_discontinuity_visibility_count"] == 1
    assert continuity["replay_continuity"]["replay_discontinuity_visibility_count"] == 1
    assert continuity["rollback_continuity"]["rollback_discontinuity_visibility_count"] == 1
    assert continuity["replay_continuity"]["replay_safe"] is True
    assert continuity["rollback_continuity"]["rollback_safe"] is True


def test_v4_1_dependency_non_execution_validation_blocks_graph_execution_production_and_planner_flags():
    graph = default_refresh_dependency_graph()
    contaminated = replace(
        graph,
        dependency_execution_enabled=True,
        orchestration_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_dependency_graph_non_execution(contaminated)

    assert validate_dependency_graph_non_execution(graph)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 4
    assert validation["dependency_execution_absent"] is False
    assert validation["orchestration_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_dependency_integrity_blocks_hidden_correction_and_execution_semantics():
    graph = default_refresh_dependency_graph()
    hidden_edge = replace(
        graph.edges[1],
        hidden=True,
        fail_visible=False,
        dependency_execution_enabled=True,
        automatic_dependency_resolution_enabled=True,
    )
    corrective_visibility = replace(
        graph.blocked_state_visibility,
        remediation_enabled=True,
        silent_fallback_enabled=True,
    )
    contaminated = replace(
        graph,
        edges=(graph.edges[0], hidden_edge, *graph.edges[2:]),
        blocked_state_visibility=corrective_visibility,
    )
    validation = validate_dependency_graph_integrity(contaminated)

    assert validate_dependency_graph_integrity(graph)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_edge_count"] == 1
    assert validation["visibility_validation"]["edge_execution_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 4


def test_v4_1_dependency_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_dependency_graph_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_validation"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_DEPENDENCY_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["silent_fallback_absent"] is True
    assert diagnostics["automatic_recovery_absent"] is True
    assert diagnostics["circular_dependency_edges"] == [
        "v4_1_edge_future_provider_to_manifest_circular_visibility"
    ]


def test_v4_1_dependency_graph_reports_contain_required_evidence_and_boundaries():
    report = build_v4_1_refresh_dependency_graph_report()
    diagnostics_report = build_v4_1_refresh_dependency_graph_diagnostics_report()
    integrity_report = build_v4_1_refresh_dependency_graph_integrity_report()

    assert report["foundation_status"] == V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE
    assert report["dependency_graph_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_graph_serialization_verified"] is True
    assert report["summary"]["deterministic_graph_hashing_verified"] is True
    assert report["summary"]["deterministic_dependency_equality_verified"] is True
    assert report["summary"]["deterministic_dependency_visibility_verified"] is True
    assert report["summary"]["lineage_continuity_verified"] is True
    assert report["summary"]["provenance_continuity_verified"] is True
    assert report["summary"]["replay_continuity_verified"] is True
    assert report["summary"]["rollback_continuity_verified"] is True
    assert report["summary"]["blocked_state_visibility_validated"] is True
    assert report["summary"]["unsupported_state_visibility_validated"] is True
    assert report["summary"]["circular_dependency_visibility_validated"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["production_consumption_disabled_validated"] is True
    assert report["summary"]["planner_integration_disabled_validated"] is True
    assert report["summary"]["integrity_validation_verified"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert "No orchestration exists." in report["explicit_prohibitions"]
    assert "No dependency execution exists." in report["explicit_prohibitions"]
    assert "No automatic sequencing exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
