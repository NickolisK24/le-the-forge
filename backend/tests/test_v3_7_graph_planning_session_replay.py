from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_planning_session_replay import (
    build_v3_7_graph_planning_session_replay_evidence,
    validate_v3_7_graph_planning_session_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


def test_session_replay_evidence_is_non_executable_not_runtime_replay():
    evidence = build_v3_7_graph_planning_session_replay_evidence()[0]

    assert evidence.non_executable_replay_evidence is True
    assert evidence.runtime_replay is False
    assert evidence.orchestration_runtime_packet is False
    assert evidence.execution_authorization is False
    assert evidence.replay_packet_references
    assert evidence.continuity_hashes


def test_session_replay_and_rollback_evidence_preserve_continuity():
    session = build_v3_7_graph_planning_session()
    result = validate_v3_7_graph_planning_session_replay_evidence(session)

    assert result["replay_evidence_count"] == 1
    assert result["rollback_evidence_count"] == 1
    assert result["non_executable_replay_evidence"] is True
    assert result["runtime_replay"] is False
    assert result["execution_authorization"] is False
    assert result["replay_continuity_preserved"] is True
    assert result["rollback_continuity_preserved"] is True


def test_session_rollback_evidence_is_rollback_safe():
    session = build_v3_7_graph_planning_session()
    rollback = session.rollback_evidence[0]

    assert rollback.rollback_safe is True
    assert rollback.runtime_state_mutation_enabled is False
    assert rollback.rollback_reference_ids
    assert rollback.continuity_hashes
