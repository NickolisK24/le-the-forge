from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_planning_session_explainability import (
    V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_planning_session,
    hash_v3_7_graph_planning_session_explainability_result,
    serialize_v3_7_graph_planning_session_explainability_result,
)


def test_session_explainability_is_stable_and_replay_safe():
    result = explain_v3_7_graph_planning_session()

    assert result.explainability_status == V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE
    assert result.replay_safe is True
    assert result.missing_explanation_subjects == ()
    assert result.explanation_count == 9
    assert result.deterministic_explainability_hash == hash_v3_7_graph_planning_session_explainability_result(result)
    assert serialize_v3_7_graph_planning_session_explainability_result(result) == serialize_v3_7_graph_planning_session_explainability_result(result)


def test_session_explainability_covers_session_snapshot_evaluation_and_visible_findings():
    result = explain_v3_7_graph_planning_session()

    assert result.session_existence_explanation_count == 1
    assert result.snapshot_explanation_count == 1
    assert result.evaluation_evidence_explanation_count == 1
    assert result.visible_finding_explanation_count == 6
    assert result.blocked_explanation_count == 1
    assert result.unsupported_explanation_count == 1
    assert result.prohibited_explanation_count == 1
    assert result.unknown_explanation_count == 1


def test_session_explainability_preserves_provenance_and_continuity_support():
    result = explain_v3_7_graph_planning_session()

    assert result.provenance_supported_explanation_count == result.explanation_count
    assert result.continuity_supported_explanation_count == result.explanation_count
    assert all(explanation.execution_authorization is False for explanation in result.explanations)
    assert all(explanation.reasoning_chain for explanation in result.explanations)
