from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_governance_explainability import (
    V37_GOVERNANCE_EXPLAINABILITY_BLOCKED,
    V37_GOVERNANCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_governance,
    hash_v3_7_graph_governance_explainability_result,
    serialize_v3_7_graph_governance_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_governance_rules import build_v3_7_graph_governance_map


def test_governance_explainability_is_deterministic_and_replay_safe():
    governance_map = build_v3_7_graph_governance_map()
    first = explain_v3_7_graph_governance(governance_map)
    second = explain_v3_7_graph_governance(governance_map)

    assert first.explainability_status == V37_GOVERNANCE_EXPLAINABILITY_STABLE
    assert first.replay_safe is True
    assert first.explanation_count == 9
    assert first.node_explanation_count == 3
    assert first.edge_explanation_count == 2
    assert first.prohibited_relationship_explanation_count >= 2
    assert first.unsupported_relationship_explanation_count >= 2
    assert first.deterministic_explainability_hash == second.deterministic_explainability_hash
    assert serialize_v3_7_graph_governance_explainability_result(first) == (
        serialize_v3_7_graph_governance_explainability_result(second)
    )
    assert hash_v3_7_graph_governance_explainability_result(first) == (
        hash_v3_7_graph_governance_explainability_result(second)
    )


def test_governance_explainability_describes_prohibited_and_unsupported_relationships():
    result = explain_v3_7_graph_governance(build_v3_7_graph_governance_map())

    prohibited = [
        explanation
        for explanation in result.explanations
        if explanation.prohibited_relationship_reasons
    ]
    unsupported = [
        explanation
        for explanation in result.explanations
        if explanation.unsupported_relationship_reasons
    ]
    assert prohibited
    assert unsupported
    assert all(explanation.reasoning_chain for explanation in result.explanations)
    assert all(explanation.provenance_lineage for explanation in result.explanations)


def test_missing_governance_explanation_subject_is_fail_visible():
    governance_map = build_v3_7_graph_governance_map()
    broken_node = replace(governance_map.node_classifications[0], provenance=replace(
        governance_map.node_classifications[0].provenance,
        lineage_references=(),
    ))
    result = explain_v3_7_graph_governance(
        replace(governance_map, node_classifications=(broken_node,) + governance_map.node_classifications[1:])
    )

    assert result.explainability_status == V37_GOVERNANCE_EXPLAINABILITY_BLOCKED
    assert result.replay_safe is False
