from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_planning_session_identity import (
    build_v3_7_graph_planning_session_identity,
    graph_planning_session_identities_are_unique,
    graph_planning_session_identity_key,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session
from app.runtime_orchestration.v3_7_graph_planning_session_validation import (
    V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED,
    V37_SESSION_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY,
    validate_v3_7_graph_planning_sessions,
)


def test_session_identity_is_stable_and_deterministic():
    first = build_v3_7_graph_planning_session_identity()
    second = build_v3_7_graph_planning_session_identity()

    assert first == second
    assert first.stable_identity_key == graph_planning_session_identity_key(first)
    assert first.phase_id == "v3_7_graph_planning_sessions"


def test_session_identity_uniqueness_detects_duplicates():
    identity = build_v3_7_graph_planning_session_identity()

    assert graph_planning_session_identities_are_unique((identity,)) is True
    assert graph_planning_session_identities_are_unique((identity, identity)) is False


def test_validation_detects_duplicate_session_identity():
    session = build_v3_7_graph_planning_session()
    result = validate_v3_7_graph_planning_sessions((session, session))

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
    assert result.duplicate_session_identity_count == 1
    assert any(finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY for finding in result.findings)
