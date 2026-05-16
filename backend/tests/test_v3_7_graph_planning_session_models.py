from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_planning_session_models import (
    V37_GRAPH_PLANNING_SESSION_STATUSES,
    V37_SESSION_STATUS_EVALUATED,
    export_v3_7_graph_planning_session_counts,
    hash_v3_7_graph_planning_session,
    serialize_v3_7_graph_planning_session,
    validate_v3_7_graph_planning_session_hash_stability,
    validate_v3_7_graph_planning_session_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session
from scripts.report_v3_7_graph_planning_sessions import build_v3_7_graph_planning_sessions_report


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_planning_session_statuses_are_explicit():
    assert V37_GRAPH_PLANNING_SESSION_STATUSES == (
        "initialized",
        "evaluated",
        "blocked",
        "unsupported",
        "prohibited",
        "unknown",
        "audit_failed",
        "closed",
    )


def test_planning_session_is_immutable_and_non_executable():
    session = build_v3_7_graph_planning_session()

    with pytest.raises(FrozenInstanceError):
        session.routing_enabled = True

    assert session.status == V37_SESSION_STATUS_EVALUATED
    assert session.planning_sessions_are_non_executable is True
    assert session.evidence_container_only is True
    assert session.session_replay_evidence_is_not_runtime_replay is True
    assert session.snapshots_do_not_imply_execution_state is True
    assert session.audit_trails_do_not_imply_runtime_history is True
    assert session.session_statuses_do_not_authorize_orchestration is True
    assert session.routing_enabled is False
    assert session.scheduling_enabled is False
    assert session.dispatch_enabled is False
    assert session.session_execution_enabled is False


def test_planning_session_serialization_and_hash_are_deterministic():
    session = build_v3_7_graph_planning_session()
    reordered = replace(
        session,
        metadata=tuple(reversed(session.metadata)),
        snapshots=tuple(reversed(session.snapshots)),
        evaluation_evidence=tuple(reversed(session.evaluation_evidence)),
        replay_evidence=tuple(reversed(session.replay_evidence)),
        rollback_evidence=tuple(reversed(session.rollback_evidence)),
        audit_trail=tuple(reversed(session.audit_trail)),
    )

    assert serialize_v3_7_graph_planning_session(session) == serialize_v3_7_graph_planning_session(reordered)
    assert hash_v3_7_graph_planning_session(session) == hash_v3_7_graph_planning_session(reordered)
    assert validate_v3_7_graph_planning_session_serialization_stability(session)["stable"] is True
    assert validate_v3_7_graph_planning_session_hash_stability(session)["stable"] is True
    assert json.loads(serialize_v3_7_graph_planning_session(session))["dispatch_enabled"] is False


def test_planning_session_counts_and_report_are_deterministic():
    session = build_v3_7_graph_planning_session()
    first = build_v3_7_graph_planning_sessions_report(REPO_ROOT)
    second = build_v3_7_graph_planning_sessions_report(REPO_ROOT)

    assert export_v3_7_graph_planning_session_counts(session) == {
        "planning_session_count": 1,
        "snapshot_count": 1,
        "evaluation_evidence_count": 1,
        "replay_evidence_count": 1,
        "rollback_evidence_count": 1,
        "audit_trail_count": 6,
    }
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["planning_sessions_are_non_executable"] is True
    assert first["session_replay_evidence_is_not_runtime_replay"] is True
    assert first["routing_enabled"] is False
    assert first["scheduling_enabled"] is False
    assert first["dispatch_enabled"] is False
