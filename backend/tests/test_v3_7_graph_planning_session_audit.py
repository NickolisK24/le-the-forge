from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_planning_session_audit import (
    V37_GRAPH_PLANNING_SESSION_AUDIT_FAILED,
    V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE,
    V37_SESSION_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_SESSION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY,
    V37_SESSION_AUDIT_BLOCKED_BY_REPLAY,
    V37_SESSION_AUDIT_VISIBLE_BLOCKED,
    audit_v3_7_graph_planning_session,
    hash_v3_7_graph_planning_session_audit_result,
    serialize_v3_7_graph_planning_session_audit_result,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


def test_session_audit_is_stable_and_preserves_continuity_layers():
    result = audit_v3_7_graph_planning_session()

    assert result.audit_status == V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 4
    assert result.session_identity_stable is True
    assert result.snapshot_continuity_preserved is True
    assert result.graph_hash_continuity_preserved is True
    assert result.evaluation_evidence_continuity_preserved is True
    assert result.replay_evidence_continuity_preserved is True
    assert result.rollback_evidence_continuity_preserved is True
    assert result.deterministic_audit_hash == hash_v3_7_graph_planning_session_audit_result(result)
    assert serialize_v3_7_graph_planning_session_audit_result(result) == serialize_v3_7_graph_planning_session_audit_result(result)


def test_session_audit_keeps_blocked_state_visible():
    result = audit_v3_7_graph_planning_session()

    assert any(finding.status == V37_SESSION_AUDIT_VISIBLE_BLOCKED for finding in result.findings)


def test_session_audit_detects_hidden_audit_entry():
    session = build_v3_7_graph_planning_session()
    hidden_entry = replace(session.audit_trail[1], hidden=True)
    result = audit_v3_7_graph_planning_session(replace(session, audit_trail=(session.audit_trail[0], hidden_entry) + session.audit_trail[2:]))

    assert result.audit_status == V37_GRAPH_PLANNING_SESSION_AUDIT_FAILED
    assert any(finding.status == V37_SESSION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY for finding in result.findings)


def test_session_audit_detects_replay_gap_and_execution_capability():
    session = build_v3_7_graph_planning_session()
    broken_replay = replace(session.replay_evidence[0], replay_packet_references=())
    replay_result = audit_v3_7_graph_planning_session(replace(session, replay_evidence=(broken_replay,)))
    execution_result = audit_v3_7_graph_planning_session(replace(session, routing_enabled=True))

    assert replay_result.audit_status == V37_GRAPH_PLANNING_SESSION_AUDIT_FAILED
    assert any(finding.status == V37_SESSION_AUDIT_BLOCKED_BY_REPLAY for finding in replay_result.findings)
    assert execution_result.audit_status == V37_GRAPH_PLANNING_SESSION_AUDIT_FAILED
    assert any(finding.status == V37_SESSION_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY for finding in execution_result.findings)
