from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_governance_models import (
    V37_EDGE_COMPATIBILITY_RESTRICTED,
    V37_EDGE_GOVERNANCE_RESTRICTED,
    V37_EDGE_PROHIBITED_STRUCTURAL,
    V37_EDGE_UNSUPPORTED_STRUCTURAL,
    V37_NODE_EXPERIMENTAL,
    V37_NODE_GOVERNANCE_RESTRICTED,
    V37_NODE_SUPPORTED,
)
from app.runtime_orchestration.v3_7_graph_governance_rules import (
    RULE_GRAPH_EXECUTION_PROHIBITED,
    RULE_OPTIMIZATION_UNSUPPORTED,
    RULE_ROUTING_SCHEDULING_DISPATCH_PROHIBITED,
    RULE_RUNTIME_DISPATCH_UNSUPPORTED,
    build_v3_7_graph_governance_map,
)


def test_node_and_edge_governance_classification_is_stable():
    governance_map = build_v3_7_graph_governance_map()
    node_classifications = {
        classification.node_id: classification.governance_classification
        for classification in governance_map.node_classifications
    }
    edge_classifications = {
        classification.edge_id: classification.governance_classification
        for classification in governance_map.edge_classifications
    }

    assert set(node_classifications.values()) == {
        V37_NODE_SUPPORTED,
        V37_NODE_EXPERIMENTAL,
        V37_NODE_GOVERNANCE_RESTRICTED,
    }
    assert set(edge_classifications.values()) == {
        V37_EDGE_GOVERNANCE_RESTRICTED,
        V37_EDGE_COMPATIBILITY_RESTRICTED,
    }
    assert len(node_classifications) == 3


def test_prohibited_and_unsupported_relationship_rules_are_visible():
    governance_map = build_v3_7_graph_governance_map()
    rules = {rule.rule_id: rule for rule in governance_map.rules}
    findings = {finding.rule_id: finding for finding in governance_map.findings}

    assert rules[RULE_GRAPH_EXECUTION_PROHIBITED].edge_classification == V37_EDGE_PROHIBITED_STRUCTURAL
    assert rules[RULE_ROUTING_SCHEDULING_DISPATCH_PROHIBITED].edge_classification == (
        V37_EDGE_PROHIBITED_STRUCTURAL
    )
    assert rules[RULE_RUNTIME_DISPATCH_UNSUPPORTED].edge_classification == V37_EDGE_UNSUPPORTED_STRUCTURAL
    assert rules[RULE_OPTIMIZATION_UNSUPPORTED].edge_classification == V37_EDGE_UNSUPPORTED_STRUCTURAL
    assert RULE_GRAPH_EXECUTION_PROHIBITED in findings
    assert RULE_RUNTIME_DISPATCH_UNSUPPORTED in findings
    assert all(finding.fail_visible for finding in governance_map.findings)


def test_edges_never_imply_runtime_traversal():
    governance_map = build_v3_7_graph_governance_map()

    assert all(not classification.edge_implies_execution_flow for classification in governance_map.edge_classifications)
    assert all(not classification.traversal_execution_enabled for classification in governance_map.edge_classifications)
    assert all(
        classification.governance_classification
        in {V37_EDGE_GOVERNANCE_RESTRICTED, V37_EDGE_COMPATIBILITY_RESTRICTED}
        for classification in governance_map.edge_classifications
    )
