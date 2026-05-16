from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_evaluation_explainability import (
    V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_evaluation,
    hash_v3_7_graph_evaluation_explainability_result,
    serialize_v3_7_graph_evaluation_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


def test_evaluation_explainability_is_stable_and_replay_safe():
    chain = build_v3_7_graph_evaluation_chain()
    result = explain_v3_7_graph_evaluation(chain)

    assert result.explainability_status == V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE
    assert result.replay_safe is True
    assert result.missing_explanation_subjects == ()
    assert result.explanation_count == len(chain.steps) + len(chain.findings)
    assert result.deterministic_explainability_hash == hash_v3_7_graph_evaluation_explainability_result(result)
    assert serialize_v3_7_graph_evaluation_explainability_result(result) == serialize_v3_7_graph_evaluation_explainability_result(result)


def test_evaluation_explainability_covers_required_failure_states():
    result = explain_v3_7_graph_evaluation()
    classifications = {explanation.finding_classification for explanation in result.explanations}

    assert {"prohibited", "unsupported", "unknown", "incompatible", "compatible"}.issubset(classifications)
    assert result.prohibited_explanation_count >= 2
    assert result.unsupported_explanation_count >= 2
    assert result.unknown_explanation_count >= 2


def test_evaluation_explainability_preserves_governance_compatibility_and_continuity_context():
    result = explain_v3_7_graph_evaluation()

    assert result.governance_influenced_explanation_count > 0
    assert result.compatibility_influenced_explanation_count > 0
    assert result.continuity_influenced_explanation_count == result.explanation_count
    assert all(explanation.execution_authorization is False for explanation in result.explanations)
    assert all(explanation.reasoning_chain for explanation in result.explanations)
