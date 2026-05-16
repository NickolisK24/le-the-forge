from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_scenario_explainability import (
    V37_GRAPH_SCENARIO_EXPLAINABILITY_BLOCKED,
    V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_scenario,
    hash_v3_7_graph_scenario_explainability_result,
    serialize_v3_7_graph_scenario_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def test_scenario_explainability_is_stable_and_replay_safe():
    result = explain_v3_7_graph_scenario()

    assert result.explainability_status == V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE
    assert result.replay_safe is True
    assert result.explanation_count == 17
    assert result.scenario_existence_explanation_count == 1
    assert result.variation_explanation_count == 7
    assert result.comparison_explanation_count == 1
    assert result.replay_explanation_count == 1
    assert result.visible_finding_explanation_count == 7
    assert result.changed_between_scenarios_explanation_count == 1
    assert result.unsupported_explanation_count == 2
    assert result.prohibited_explanation_count == 2
    assert result.unknown_explanation_count == 2
    assert result.deterministic_explainability_hash == hash_v3_7_graph_scenario_explainability_result(result)
    assert serialize_v3_7_graph_scenario_explainability_result(result) == serialize_v3_7_graph_scenario_explainability_result(result)


def test_scenario_explainability_detects_missing_subjects():
    scenario = build_v3_7_graph_planning_scenario()
    broken_replay = replace(scenario.replay_evidence[0], provenance_references=())
    result = explain_v3_7_graph_scenario(replace(scenario, replay_evidence=(broken_replay,)))

    assert result.explainability_status == V37_GRAPH_SCENARIO_EXPLAINABILITY_BLOCKED
    assert result.replay_safe is False
    assert result.missing_explanation_subjects == ()
