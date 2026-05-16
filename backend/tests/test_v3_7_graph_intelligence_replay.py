from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from app.runtime_orchestration.v3_7_graph_intelligence_replay import (
    build_v3_7_graph_intelligence_replay_evidence,
    validate_v3_7_graph_intelligence_replay_evidence,
)


def test_intelligence_replay_evidence_is_non_executable_not_runtime_replay():
    evidence = build_v3_7_graph_intelligence_replay_evidence()[0]

    assert evidence.non_executable_replay_evidence is True
    assert evidence.runtime_replay is False
    assert evidence.execution_authorization is False
    assert evidence.evidence_source_references
    assert evidence.graph_evidence_references
    assert evidence.scenario_evidence_references
    assert evidence.continuity_hashes


def test_intelligence_replay_and_rollback_continuity_are_preserved():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    result = validate_v3_7_graph_intelligence_replay_evidence(aggregation)

    assert result["replay_evidence_count"] == 1
    assert result["rollback_reference_count"] == 1
    assert result["non_executable_replay_evidence"] is True
    assert result["runtime_replay"] is False
    assert result["execution_authorization"] is False
    assert result["replay_continuity_preserved"] is True
    assert result["rollback_continuity_preserved"] is True
