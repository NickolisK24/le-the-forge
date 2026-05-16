from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_integrity_audit import (
    V37_GRAPH_INTEGRITY_AUDIT_FAILED,
    V37_GRAPH_INTEGRITY_AUDIT_STABLE,
    V37_INTEGRITY_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY,
    V37_INTEGRITY_AUDIT_BLOCKED_BY_FINDING_VISIBILITY,
    V37_INTEGRITY_AUDIT_BLOCKED_BY_REPLAY,
    V37_INTEGRITY_AUDIT_VISIBLE_BLOCKED,
    V37_INTEGRITY_AUDIT_VISIBLE_WARNING,
    audit_v3_7_graph_integrity,
    hash_v3_7_graph_integrity_audit_result,
    serialize_v3_7_graph_integrity_audit_result,
)
from app.runtime_orchestration.v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity


def test_integrity_audit_is_stable_and_preserves_all_layers():
    result = audit_v3_7_graph_integrity()

    assert result.audit_status == V37_GRAPH_INTEGRITY_AUDIT_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 6
    assert result.policy_identity_continuity_preserved is True
    assert result.enforcement_identity_continuity_preserved is True
    assert result.graph_continuity_preserved is True
    assert result.governance_continuity_preserved is True
    assert result.compatibility_continuity_preserved is True
    assert result.evaluation_continuity_preserved is True
    assert result.session_continuity_preserved is True
    assert result.scenario_continuity_preserved is True
    assert result.aggregation_continuity_preserved is True
    assert result.execution_boundary_continuity_preserved is True
    assert result.deterministic_audit_hash == hash_v3_7_graph_integrity_audit_result(result)
    assert serialize_v3_7_graph_integrity_audit_result(result) == serialize_v3_7_graph_integrity_audit_result(result)


def test_integrity_audit_keeps_blocked_and_warning_findings_visible():
    result = audit_v3_7_graph_integrity()

    assert any(finding.status == V37_INTEGRITY_AUDIT_VISIBLE_BLOCKED for finding in result.findings)
    assert any(finding.status == V37_INTEGRITY_AUDIT_VISIBLE_WARNING for finding in result.findings)


def test_integrity_audit_detects_hidden_finding():
    enforcement = enforce_v3_7_graph_planning_integrity()
    hidden_finding = replace(enforcement.findings[0], hidden=True)
    result = audit_v3_7_graph_integrity(replace(enforcement, findings=(hidden_finding,) + enforcement.findings[1:]))

    assert result.audit_status == V37_GRAPH_INTEGRITY_AUDIT_FAILED
    assert any(finding.status == V37_INTEGRITY_AUDIT_BLOCKED_BY_FINDING_VISIBILITY for finding in result.findings)


def test_integrity_audit_detects_replay_gap_and_execution_boundary():
    enforcement = enforce_v3_7_graph_planning_integrity()
    broken_replay = replace(enforcement.replay_evidence[0], evidence_source_references=())
    replay_result = audit_v3_7_graph_integrity(replace(enforcement, replay_evidence=(broken_replay,)))
    execution_result = audit_v3_7_graph_integrity(replace(enforcement, routing_enabled=True))

    assert replay_result.audit_status == V37_GRAPH_INTEGRITY_AUDIT_FAILED
    assert any(finding.status == V37_INTEGRITY_AUDIT_BLOCKED_BY_REPLAY for finding in replay_result.findings)
    assert execution_result.audit_status == V37_GRAPH_INTEGRITY_AUDIT_FAILED
    assert any(finding.status == V37_INTEGRITY_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY for finding in execution_result.findings)
