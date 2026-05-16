from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace

import pytest

from app.runtime_orchestration.v3_7_graph_governance_domains import (
    DOMAIN_GRAPH_EXECUTION,
    classify_v3_7_governance_domain,
    default_v3_7_graph_governance_domains,
)
from app.runtime_orchestration.v3_7_graph_governance_models import (
    V37_DOMAIN_PROHIBITED,
    V37_DOMAIN_UNSUPPORTED,
    export_v3_7_governance_counts,
    hash_v3_7_governance_map,
    serialize_v3_7_governance_map,
    validate_v3_7_governance_hash_stability,
    validate_v3_7_governance_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_governance_rules import build_v3_7_graph_governance_map


def test_governance_domains_are_pure_metadata_classifications():
    domains = default_v3_7_graph_governance_domains()

    assert len(domains) == 8
    assert classify_v3_7_governance_domain(DOMAIN_GRAPH_EXECUTION) == V37_DOMAIN_PROHIBITED
    assert classify_v3_7_governance_domain("unknown_domain") == V37_DOMAIN_UNSUPPORTED
    assert {domain.domain_classification for domain in domains} == {
        "supported",
        "unsupported",
        "prohibited",
        "experimental",
        "governance_restricted",
        "compatibility_restricted",
    }


def test_governance_map_is_immutable_and_non_executable():
    governance_map = build_v3_7_graph_governance_map()

    with pytest.raises(FrozenInstanceError):
        governance_map.graph_execution_enabled = True

    assert governance_map.governance_metadata_does_not_enable_orchestration is True
    assert governance_map.structural_governance_artifact_only is True
    assert governance_map.non_executable is True
    assert governance_map.graph_execution_enabled is False
    assert governance_map.node_execution_enabled is False
    assert governance_map.edge_traversal_execution_enabled is False
    assert governance_map.runtime_orchestration_enabled is False
    assert governance_map.routing_enabled is False
    assert governance_map.scheduling_enabled is False
    assert governance_map.dispatch_enabled is False
    assert governance_map.runtime_mutation_enabled is False
    assert governance_map.graph_evaluation_execution_enabled is False


def test_governance_serialization_and_hash_are_deterministic():
    governance_map = build_v3_7_graph_governance_map()
    reordered = replace(
        governance_map,
        domains=tuple(reversed(governance_map.domains)),
        rules=tuple(reversed(governance_map.rules)),
        node_classifications=tuple(reversed(governance_map.node_classifications)),
        edge_classifications=tuple(reversed(governance_map.edge_classifications)),
        findings=tuple(reversed(governance_map.findings)),
    )

    assert serialize_v3_7_governance_map(governance_map) == serialize_v3_7_governance_map(reordered)
    assert hash_v3_7_governance_map(governance_map) == hash_v3_7_governance_map(reordered)
    assert validate_v3_7_governance_serialization_stability(governance_map)["stable"] is True
    assert validate_v3_7_governance_hash_stability(governance_map)["stable"] is True
    assert json.loads(serialize_v3_7_governance_map(governance_map))["non_executable"] is True


def test_governance_counts_are_stable():
    governance_map = build_v3_7_graph_governance_map()

    assert export_v3_7_governance_counts(governance_map) == {
        "domain_count": 8,
        "rule_count": 6,
        "node_classification_count": 3,
        "edge_classification_count": 2,
        "finding_count": 4,
        "continuity_evidence_count": 1,
    }
