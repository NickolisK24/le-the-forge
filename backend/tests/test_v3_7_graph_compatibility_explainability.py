from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_compatibility_explainability import (
    V37_COMPATIBILITY_EXPLAINABILITY_BLOCKED,
    V37_COMPATIBILITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_compatibility,
    hash_v3_7_graph_compatibility_explainability_result,
    serialize_v3_7_graph_compatibility_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map


def test_compatibility_explainability_is_deterministic_and_replay_safe():
    compatibility_map = build_v3_7_graph_compatibility_map()
    first = explain_v3_7_graph_compatibility(compatibility_map)
    second = explain_v3_7_graph_compatibility(compatibility_map)

    assert first.explainability_status == V37_COMPATIBILITY_EXPLAINABILITY_STABLE
    assert first.replay_safe is True
    assert first.explanation_count == 11
    assert first.node_explanation_count == 2
    assert first.edge_explanation_count == 2
    assert first.compatible_explanation_count == 1
    assert first.incompatible_explanation_count == 1
    assert first.unsupported_explanation_count == 1
    assert first.prohibited_explanation_count == 1
    assert first.unknown_explanation_count == 1
    assert first.deterministic_explainability_hash == second.deterministic_explainability_hash
    assert serialize_v3_7_graph_compatibility_explainability_result(first) == (
        serialize_v3_7_graph_compatibility_explainability_result(second)
    )
    assert hash_v3_7_graph_compatibility_explainability_result(first) == (
        hash_v3_7_graph_compatibility_explainability_result(second)
    )


def test_compatibility_explainability_covers_required_reasons():
    result = explain_v3_7_graph_compatibility(build_v3_7_graph_compatibility_map())
    classes = {explanation.compatibility_classification for explanation in result.explanations}

    assert {"compatible", "incompatible", "unsupported", "prohibited", "unknown"}.issubset(classes)
    assert all(explanation.reasoning_chain for explanation in result.explanations)
    assert all(explanation.provenance_lineage for explanation in result.explanations)
    assert result.governance_influenced_explanation_count > 0


def test_missing_compatibility_explainability_is_fail_visible():
    compatibility_map = build_v3_7_graph_compatibility_map()
    broken_node = replace(
        compatibility_map.node_results[0],
        provenance=replace(compatibility_map.node_results[0].provenance, lineage_references=()),
    )
    result = explain_v3_7_graph_compatibility(
        replace(compatibility_map, node_results=(broken_node,) + compatibility_map.node_results[1:])
    )

    assert result.explainability_status == V37_COMPATIBILITY_EXPLAINABILITY_BLOCKED
    assert result.replay_safe is False
