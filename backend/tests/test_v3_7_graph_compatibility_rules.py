from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_compatibility_models import (
    V37_COMPATIBILITY_RESTRICTED,
    V37_EXPERIMENTAL_COMPATIBILITY,
    V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
    V37_PROHIBITED_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
    V37_UNSUPPORTED_COMPATIBILITY,
)
from app.runtime_orchestration.v3_7_graph_compatibility_rules import (
    RULE_COMPAT_GRAPH_EXECUTION_PROHIBITED,
    RULE_COMPAT_RUNTIME_DISPATCH_UNSUPPORTED,
    RULE_COMPAT_UNKNOWN_EXTERNAL,
    build_v3_7_graph_compatibility_map,
    classify_v3_7_edge_compatibility,
    classify_v3_7_node_compatibility,
)


def test_node_and_edge_compatibility_classification_is_stable():
    compatibility_map = build_v3_7_graph_compatibility_map()
    node_classes = {result.relationship_id: result.compatibility_classification for result in compatibility_map.node_results}
    edge_classes = {result.edge_id: result.compatibility_classification for result in compatibility_map.edge_results}

    assert set(node_classes.values()) == {
        V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
        V37_EXPERIMENTAL_COMPATIBILITY,
    }
    assert set(edge_classes.values()) == {
        V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
        V37_COMPATIBILITY_RESTRICTED,
    }
    assert classify_v3_7_node_compatibility("governance_restricted", "supported") == (
        V37_GOVERNANCE_RESTRICTED_COMPATIBILITY
    )
    assert classify_v3_7_edge_compatibility("compatibility_restricted_relationship") == V37_COMPATIBILITY_RESTRICTED


def test_unsupported_prohibited_and_unknown_compatibility_remain_visible():
    compatibility_map = build_v3_7_graph_compatibility_map()
    rules = {rule.rule_id: rule for rule in compatibility_map.rules}
    findings = {finding.rule_id: finding for finding in compatibility_map.findings}

    assert rules[RULE_COMPAT_GRAPH_EXECUTION_PROHIBITED].compatibility_classification == V37_PROHIBITED_COMPATIBILITY
    assert rules[RULE_COMPAT_RUNTIME_DISPATCH_UNSUPPORTED].compatibility_classification == (
        V37_UNSUPPORTED_COMPATIBILITY
    )
    assert rules[RULE_COMPAT_UNKNOWN_EXTERNAL].compatibility_classification == V37_UNKNOWN_COMPATIBILITY
    assert RULE_COMPAT_GRAPH_EXECUTION_PROHIBITED in findings
    assert RULE_COMPAT_RUNTIME_DISPATCH_UNSUPPORTED in findings
    assert RULE_COMPAT_UNKNOWN_EXTERNAL in findings
    assert all(finding.fail_visible for finding in compatibility_map.findings)


def test_compatibility_results_do_not_authorize_ordering_or_traversal():
    compatibility_map = build_v3_7_graph_compatibility_map()

    assert all(not result.node_relationship_implies_runtime_ordering for result in compatibility_map.node_results)
    assert all(not result.edge_compatibility_implies_traversal for result in compatibility_map.edge_results)
    assert all(not result.traversal_enabled for result in compatibility_map.edge_results)
    assert compatibility_map.compatibility_does_not_authorize_execution is True
