from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_compatibility_domains import (
    COMPAT_DOMAIN_GRAPH_EXECUTION,
    classify_v3_7_compatibility_domain,
    default_v3_7_graph_compatibility_domains,
)
from app.runtime_orchestration.v3_7_graph_compatibility_models import (
    V37_COMPATIBILITY_CLASSIFICATIONS,
    V37_PROHIBITED_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
    export_v3_7_compatibility_counts,
    hash_v3_7_compatibility_map,
    serialize_v3_7_compatibility_map,
    validate_v3_7_compatibility_hash_stability,
    validate_v3_7_compatibility_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map
from scripts.report_v3_7_graph_compatibility_reasoning import (
    build_v3_7_graph_compatibility_reasoning_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_compatibility_domains_cover_explicit_classifications():
    domains = default_v3_7_graph_compatibility_domains()

    assert len(domains) == 8
    assert classify_v3_7_compatibility_domain(COMPAT_DOMAIN_GRAPH_EXECUTION) == V37_PROHIBITED_COMPATIBILITY
    assert classify_v3_7_compatibility_domain("missing-domain") == V37_UNKNOWN_COMPATIBILITY
    assert {domain.compatibility_classification for domain in domains} == {
        "compatible",
        "incompatible",
        "unsupported",
        "prohibited",
        "governance_restricted",
        "compatibility_restricted",
        "experimental",
        "unknown",
    }


def test_compatibility_map_is_immutable_and_non_executable():
    compatibility_map = build_v3_7_graph_compatibility_map()

    with pytest.raises(FrozenInstanceError):
        compatibility_map.routing_enabled = True

    assert compatibility_map.compatibility_reasoning_is_non_executable is True
    assert compatibility_map.compatibility_does_not_authorize_execution is True
    assert compatibility_map.edge_compatibility_does_not_imply_traversal is True
    assert compatibility_map.node_compatibility_does_not_imply_runtime_ordering is True
    assert compatibility_map.structural_planning_evidence_only is True
    assert compatibility_map.graph_execution_enabled is False
    assert compatibility_map.node_execution_enabled is False
    assert compatibility_map.edge_traversal_execution_enabled is False
    assert compatibility_map.routing_enabled is False
    assert compatibility_map.scheduling_enabled is False
    assert compatibility_map.dispatch_enabled is False
    assert compatibility_map.graph_path_selection_enabled is False


def test_compatibility_serialization_and_hash_are_deterministic():
    compatibility_map = build_v3_7_graph_compatibility_map()
    reordered = replace(
        compatibility_map,
        domains=tuple(reversed(compatibility_map.domains)),
        rules=tuple(reversed(compatibility_map.rules)),
        node_results=tuple(reversed(compatibility_map.node_results)),
        edge_results=tuple(reversed(compatibility_map.edge_results)),
        findings=tuple(reversed(compatibility_map.findings)),
    )

    assert serialize_v3_7_compatibility_map(compatibility_map) == serialize_v3_7_compatibility_map(reordered)
    assert hash_v3_7_compatibility_map(compatibility_map) == hash_v3_7_compatibility_map(reordered)
    assert validate_v3_7_compatibility_serialization_stability(compatibility_map)["stable"] is True
    assert validate_v3_7_compatibility_hash_stability(compatibility_map)["stable"] is True
    assert json.loads(serialize_v3_7_compatibility_map(compatibility_map))["routing_enabled"] is False


def test_compatibility_counts_and_graph_level_aggregation_are_stable():
    compatibility_map = build_v3_7_graph_compatibility_map()

    assert export_v3_7_compatibility_counts(compatibility_map) == {
        "domain_count": 8,
        "rule_count": 7,
        "node_result_count": 2,
        "edge_result_count": 2,
        "finding_count": 7,
        "continuity_evidence_count": 1,
    }
    assert compatibility_map.aggregation.compatible_relationship_count == 1
    assert compatibility_map.aggregation.incompatible_relationship_count == 1
    assert compatibility_map.aggregation.unsupported_relationship_count == 1
    assert compatibility_map.aggregation.prohibited_relationship_count == 1
    assert compatibility_map.aggregation.unknown_relationship_count == 1
    assert compatibility_map.aggregation.fail_visible_finding_count == 7


def test_compatibility_report_generation_is_deterministic_and_non_executable():
    first = build_v3_7_graph_compatibility_reasoning_report(REPO_ROOT)
    second = build_v3_7_graph_compatibility_reasoning_report(REPO_ROOT)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["compatibility_reasoning_is_non_executable"] is True
    assert first["compatibility_does_not_authorize_execution"] is True
    assert first["edge_compatibility_does_not_imply_traversal"] is True
    assert first["node_compatibility_does_not_imply_runtime_ordering"] is True
    assert first["routing_enabled"] is False
    assert first["scheduling_enabled"] is False
    assert first["dispatch_enabled"] is False
    assert first["coverage"]["prohibited_visibility_coverage"] is True
    assert first["coverage"]["unsupported_visibility_coverage"] is True
    assert first["coverage"]["unknown_visibility_coverage"] is True
    assert set(first["compatibility_classification_counts"]) == set(V37_COMPATIBILITY_CLASSIFICATIONS)
    assert first["compatibility_classification_counts"]["compatibility_restricted"] > 0
