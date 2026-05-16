from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_integrity_explainability import (
    V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_integrity,
    hash_v3_7_graph_integrity_explainability_result,
    serialize_v3_7_graph_integrity_explainability_result,
)


def test_integrity_explainability_is_stable_and_replay_safe():
    result = explain_v3_7_graph_integrity()

    assert result.explainability_status == V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE
    assert result.enforcement_explanation_count == 1
    assert result.policy_explanation_count == 1
    assert result.evidence_source_explanation_count == 7
    assert result.finding_explanation_count == 13
    assert result.execution_boundary_explanation_count == 1
    assert result.does_not_authorize_explanation_count == 1
    assert all(explanation.replay_safe for explanation in result.explanations)
    assert result.deterministic_explainability_hash == hash_v3_7_graph_integrity_explainability_result(result)
    assert serialize_v3_7_graph_integrity_explainability_result(result) == serialize_v3_7_graph_integrity_explainability_result(result)


def test_integrity_explainability_states_non_execution_boundary():
    result = explain_v3_7_graph_integrity()
    summaries = " ".join(explanation.summary for explanation in result.explanations)

    assert "does not authorize runtime orchestration" in summaries
    assert "execution-boundary integrity is preserved" in summaries
