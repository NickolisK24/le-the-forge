from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from app.runtime_orchestration.v3_7_graph_intelligence_explainability import (
    V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_BLOCKED,
    V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_intelligence,
    hash_v3_7_graph_intelligence_explainability_result,
    serialize_v3_7_graph_intelligence_explainability_result,
)


def test_intelligence_explainability_is_stable_and_replay_safe():
    result = explain_v3_7_graph_intelligence()

    assert result.explainability_status == V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE
    assert result.replay_safe is True
    assert result.explanation_count == 31
    assert result.aggregation_explanation_count == 1
    assert result.evidence_source_explanation_count == 6
    assert result.finding_explanation_count == 15
    assert result.insight_explanation_count == 8
    assert result.replay_explanation_count == 1
    assert result.does_not_authorize_explanation_count == 30
    assert result.deterministic_explainability_hash == hash_v3_7_graph_intelligence_explainability_result(result)
    assert serialize_v3_7_graph_intelligence_explainability_result(result) == serialize_v3_7_graph_intelligence_explainability_result(result)


def test_intelligence_explainability_detects_missing_continuity():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    broken_source = replace(aggregation.evidence_sources[0], continuity_references=())
    result = explain_v3_7_graph_intelligence(replace(aggregation, evidence_sources=(broken_source,) + aggregation.evidence_sources[1:]))

    assert result.explainability_status == V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_BLOCKED
    assert result.replay_safe is False
