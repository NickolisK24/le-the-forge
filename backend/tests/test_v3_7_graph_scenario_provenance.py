from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_scenario_provenance import (
    V37_GRAPH_SCENARIO_PROVENANCE_BLOCKED,
    V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED,
    audit_v3_7_graph_scenario_provenance,
    collect_v3_7_graph_scenario_provenance,
    hash_v3_7_graph_scenario_provenance_result,
    serialize_v3_7_graph_scenario_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def test_scenario_provenance_is_preserved_for_all_required_layers():
    scenario = build_v3_7_graph_planning_scenario()
    result = audit_v3_7_graph_scenario_provenance(scenario)

    assert result.provenance_status == V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED
    assert result.provenance_record_count == 8
    assert result.scenario_creation_provenance_preserved is True
    assert result.planning_session_provenance_preserved is True
    assert result.graph_snapshot_provenance_preserved is True
    assert result.evaluation_provenance_preserved is True
    assert result.replay_provenance_preserved is True
    assert result.rollback_provenance_preserved is True
    assert result.explainability_provenance_preserved is True
    assert result.continuity_provenance_preserved is True
    assert result.comparison_provenance_preserved is True
    assert result.deterministic_provenance_hash == hash_v3_7_graph_scenario_provenance_result(result)
    assert serialize_v3_7_graph_scenario_provenance_result(result) == serialize_v3_7_graph_scenario_provenance_result(result)
    assert len(collect_v3_7_graph_scenario_provenance(scenario)) == 8


def test_scenario_provenance_detects_discontinuity():
    scenario = build_v3_7_graph_planning_scenario()
    broken_provenance = replace(scenario.variations[0].provenance, replay_lineage_references=())
    broken_variation = replace(scenario.variations[0], provenance=broken_provenance)
    result = audit_v3_7_graph_scenario_provenance(
        replace(scenario, variations=(broken_variation,) + scenario.variations[1:])
    )

    assert result.provenance_status == V37_GRAPH_SCENARIO_PROVENANCE_BLOCKED
    assert scenario.variations[0].variation_id in result.missing_provenance_subjects
