from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_scenario_replay import (
    build_v3_7_graph_scenario_replay_evidence,
    validate_v3_7_graph_scenario_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def test_scenario_replay_evidence_is_non_executable_not_runtime_replay():
    evidence = build_v3_7_graph_scenario_replay_evidence()[0]

    assert evidence.non_executable_replay_evidence is True
    assert evidence.runtime_replay_state is False
    assert evidence.execution_authorization is False
    assert evidence.variation_references
    assert evidence.graph_snapshot_references
    assert evidence.evaluation_references
    assert evidence.continuity_hashes


def test_scenario_replay_and_rollback_evidence_preserve_continuity():
    scenario = build_v3_7_graph_planning_scenario()
    result = validate_v3_7_graph_scenario_replay_evidence(scenario)

    assert result["replay_evidence_count"] == 1
    assert result["rollback_reference_count"] > 0
    assert result["non_executable_replay_evidence"] is True
    assert result["runtime_replay_state"] is False
    assert result["execution_authorization"] is False
    assert result["replay_continuity_preserved"] is True
    assert result["rollback_continuity_preserved"] is True
