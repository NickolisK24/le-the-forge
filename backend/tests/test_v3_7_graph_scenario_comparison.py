from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_scenario_comparison import (
    export_v3_7_graph_scenario_comparison_records,
    validate_v3_7_graph_scenario_comparison_stability,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def test_scenario_comparison_is_deterministic_and_non_selecting():
    scenario = build_v3_7_graph_planning_scenario()
    comparison = scenario.comparison_evidence[0]
    result = validate_v3_7_graph_scenario_comparison_stability(scenario.comparison_evidence)

    assert comparison.comparison_implies_orchestration_selection is False
    assert comparison.compared_variation_ids == tuple(sorted(variation.variation_id for variation in scenario.variations))
    assert result["comparison_count"] == 1
    assert result["deterministic_comparison_stable"] is True
    assert result["comparison_selection_enabled"] is False


def test_scenario_comparison_keeps_risk_deltas_visible():
    scenario = build_v3_7_graph_planning_scenario()
    comparison = scenario.comparison_evidence[0]

    assert len(comparison.prohibited_state_delta_references) == 1
    assert len(comparison.unsupported_state_delta_references) == 1
    assert len(comparison.unknown_state_delta_references) == 1
    assert export_v3_7_graph_scenario_comparison_records(scenario.comparison_evidence)[0]["comparison_id"] == comparison.comparison_id
