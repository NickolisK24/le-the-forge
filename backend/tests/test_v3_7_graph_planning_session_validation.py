from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_planning_session_models import (
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_UNSUPPORTED,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session
from app.runtime_orchestration.v3_7_graph_planning_session_validation import (
    V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED,
    V37_GRAPH_PLANNING_SESSION_VALIDATION_STABLE,
    V37_SESSION_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_SESSION_VALIDATION_BLOCKED_BY_HIDDEN_STATE,
    V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE,
    validate_v3_7_graph_planning_sessions,
)


def test_default_session_validation_is_stable_and_fail_visible():
    result = validate_v3_7_graph_planning_sessions()

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 3
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.non_execution_guarantee_preserved is True


def test_validation_detects_invalid_evaluation_evidence():
    session = build_v3_7_graph_planning_session()
    broken = replace(session.evaluation_evidence[0], evaluation_trace_references=())
    result = validate_v3_7_graph_planning_sessions((replace(session, evaluation_evidence=(broken,)),))

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
    assert any(finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE for finding in result.findings)


def test_validation_detects_hidden_unsupported_prohibited_and_unknown_states():
    session = build_v3_7_graph_planning_session()
    hidden_entries = tuple(
        replace(entry, hidden=True)
        if entry.session_status in (V37_SESSION_STATUS_PROHIBITED, V37_SESSION_STATUS_UNSUPPORTED, V37_SESSION_STATUS_UNKNOWN)
        else entry
        for entry in session.audit_trail
    )
    result = validate_v3_7_graph_planning_sessions((replace(session, audit_trail=hidden_entries),))

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
    assert any(finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_HIDDEN_STATE for finding in result.findings)
    assert result.hidden_prohibited_state_count == 1
    assert result.hidden_unsupported_state_count == 1
    assert result.hidden_unknown_state_count == 1


def test_validation_detects_execution_capability():
    session = build_v3_7_graph_planning_session()
    result = validate_v3_7_graph_planning_sessions((replace(session, session_execution_enabled=True),))

    assert result.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
    assert any(finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY for finding in result.findings)
