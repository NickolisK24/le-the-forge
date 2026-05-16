from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_explainability import (
    V37_EXPLAINABILITY_BLOCKED,
    V37_EXPLAINABILITY_STABLE,
    explain_v3_7_graph,
    hash_v3_7_graph_explainability_result,
    serialize_v3_7_graph_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_models import default_v3_7_orchestration_planning_graph


def test_default_graph_explainability_is_deterministic_and_complete():
    graph = default_v3_7_orchestration_planning_graph()
    first = explain_v3_7_graph(graph)
    second = explain_v3_7_graph(graph)

    assert first.explainability_status == V37_EXPLAINABILITY_STABLE
    assert first.structural_reasoning_only is True
    assert first.replay_safe is True
    assert first.node_explanation_count == len(graph.nodes)
    assert first.edge_explanation_count == len(graph.edges)
    assert first.governance_restriction_count == len(graph.governance_boundaries)
    assert first.unsupported_boundary_count == len(graph.unsupported_domains)
    assert first.prohibited_boundary_count == len(graph.prohibited_domains)
    assert first.compatibility_visibility_count == len(graph.compatibility_boundaries)
    assert first.continuity_reference_count == len(graph.continuity_evidence)
    assert first.deterministic_explainability_hash == second.deterministic_explainability_hash
    assert serialize_v3_7_graph_explainability_result(first) == serialize_v3_7_graph_explainability_result(second)
    assert hash_v3_7_graph_explainability_result(first) == hash_v3_7_graph_explainability_result(second)


def test_missing_node_explainability_is_fail_visible():
    graph = default_v3_7_orchestration_planning_graph()
    missing_node_subject = graph.nodes[0].identity.node_id
    result = explain_v3_7_graph(
        replace(
            graph,
            explainability_evidence=tuple(
                evidence
                for evidence in graph.explainability_evidence
                if evidence.subject_id != missing_node_subject
            ),
        )
    )

    assert result.explainability_status == V37_EXPLAINABILITY_BLOCKED
    assert result.replay_safe is False
    assert result.missing_explanation_subjects == (missing_node_subject,)


def test_explainability_preserves_governance_unsupported_prohibited_and_provenance_context():
    graph = default_v3_7_orchestration_planning_graph()
    result = explain_v3_7_graph(graph)

    for evidence in result.evidence:
        assert evidence.why_exists
        assert evidence.governance_restrictions
        assert evidence.unsupported_boundaries
        assert evidence.prohibited_boundaries
        assert evidence.compatibility_visibility
        assert evidence.provenance_lineage
        assert evidence.continuity_references
