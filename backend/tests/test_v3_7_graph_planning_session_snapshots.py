from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import (
    build_v3_7_graph_planning_session,
    build_v3_7_graph_planning_session_snapshots,
)
from app.runtime_orchestration.v3_7_graph_planning_session_validation import (
    V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED,
    V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_GRAPH_HASH,
    V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_SNAPSHOT,
    validate_v3_7_graph_planning_sessions,
)


def test_session_snapshots_preserve_graph_hash_and_continuity_references():
    snapshots = build_v3_7_graph_planning_session_snapshots()
    snapshot = snapshots[0]

    assert len(snapshots) == 1
    assert snapshot.graph_id
    assert snapshot.graph_hash
    assert snapshot.graph_serialization_hash
    assert snapshot.governance_evidence_references
    assert snapshot.compatibility_evidence_references
    assert snapshot.evaluation_evidence_references
    assert snapshot.replay_continuity_references
    assert snapshot.rollback_continuity_references
    assert snapshot.snapshot_is_executable is False
    assert snapshot.execution_state is False


def test_session_snapshot_validation_detects_missing_snapshot():
    session = build_v3_7_graph_planning_session()
    result = validate_v3_7_graph_planning_sessions((replace(session, snapshots=()),))

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
    assert any(finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_SNAPSHOT for finding in result.findings)


def test_session_snapshot_validation_detects_invalid_graph_hash():
    session = build_v3_7_graph_planning_session()
    broken_snapshot = replace(session.snapshots[0], graph_hash="")
    result = validate_v3_7_graph_planning_sessions((replace(session, snapshots=(broken_snapshot,)),))

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
    assert any(finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_GRAPH_HASH for finding in result.findings)
