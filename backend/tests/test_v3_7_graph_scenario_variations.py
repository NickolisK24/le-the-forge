from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_scenario_variations import (
    build_v3_7_graph_planning_scenario,
    build_v3_7_graph_scenario_variations,
)


def test_variations_cover_required_hypothetical_types():
    variations = build_v3_7_graph_scenario_variations()
    variation_types = {variation.variation_type for variation in variations}

    assert len(variations) == 7
    assert "structural_relationship_alternative" in variation_types
    assert "governance_classification_alternative" in variation_types
    assert "compatibility_classification_alternative" in variation_types
    assert "evaluation_chain_alternative" in variation_types
    assert "prohibited_state_alternative" in variation_types
    assert "unsupported_state_alternative" in variation_types
    assert "unknown_state_alternative" in variation_types


def test_variations_are_structural_hypothetical_evidence_only():
    scenario = build_v3_7_graph_planning_scenario()

    assert all(variation.structural_hypothetical_evidence_only for variation in scenario.variations)
    assert all(not variation.executable_orchestration_branch for variation in scenario.variations)
    assert any(variation.governance_classification == "prohibited" for variation in scenario.variations)
    assert any(variation.compatibility_classification == "unsupported" for variation in scenario.variations)
    assert any(variation.evaluation_classification == "unknown" for variation in scenario.variations)
    assert all(variation.planning_session_reference in scenario.planning_session_references for variation in scenario.variations)
    assert all(variation.graph_snapshot_reference in scenario.graph_snapshot_references for variation in scenario.variations)
