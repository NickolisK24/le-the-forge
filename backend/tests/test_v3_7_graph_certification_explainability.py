from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_certification_explainability import (
    V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_certification,
    hash_v3_7_graph_certification_explainability_result,
    serialize_v3_7_graph_certification_explainability_result,
)


def test_certification_explainability_is_stable_and_replay_safe():
    result = explain_v3_7_graph_certification()

    assert result.explainability_status == V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE
    assert result.certification_explanation_count == 1
    assert result.scope_explanation_count == 1
    assert result.evidence_source_explanation_count == 8
    assert result.execution_boundary_explanation_count == 1
    assert result.does_not_authorize_explanation_count == 1
    assert all(explanation.replay_safe for explanation in result.explanations)
    assert result.deterministic_explainability_hash == hash_v3_7_graph_certification_explainability_result(result)
    assert serialize_v3_7_graph_certification_explainability_result(result) == serialize_v3_7_graph_certification_explainability_result(result)


def test_certification_explainability_states_non_execution_boundary():
    result = explain_v3_7_graph_certification()
    summaries = " ".join(explanation.summary for explanation in result.explanations)

    assert "does not authorize execution" in summaries
    assert "does not mark runtime execution readiness" in summaries
    assert "execution-boundary certification passed" in summaries
