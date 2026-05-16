from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_certification_audit import (
    V37_CERTIFICATION_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY,
    V37_CERTIFICATION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY,
    V37_CERTIFICATION_AUDIT_BLOCKED_BY_REPLAY,
    V37_CERTIFICATION_AUDIT_VISIBLE_BLOCKED,
    V37_CERTIFICATION_AUDIT_VISIBLE_WARNING,
    V37_GRAPH_CERTIFICATION_AUDIT_FAILED,
    V37_GRAPH_CERTIFICATION_AUDIT_STABLE,
    audit_v3_7_graph_certification,
    hash_v3_7_graph_certification_audit_result,
    serialize_v3_7_graph_certification_audit_result,
)
from app.runtime_orchestration.v3_7_graph_certification_evidence import (
    build_v3_7_graph_planning_continuity_certification,
)


def test_certification_audit_is_stable_and_preserves_all_layers():
    result = audit_v3_7_graph_certification()

    assert result.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 5
    assert result.certification_identity_continuity_preserved is True
    assert result.certification_scope_continuity_preserved is True
    assert result.graph_continuity_preserved is True
    assert result.governance_continuity_preserved is True
    assert result.compatibility_continuity_preserved is True
    assert result.evaluation_continuity_preserved is True
    assert result.session_continuity_preserved is True
    assert result.scenario_continuity_preserved is True
    assert result.aggregation_continuity_preserved is True
    assert result.integrity_continuity_preserved is True
    assert result.execution_boundary_continuity_preserved is True
    assert result.deterministic_audit_hash == hash_v3_7_graph_certification_audit_result(result)
    assert serialize_v3_7_graph_certification_audit_result(result) == serialize_v3_7_graph_certification_audit_result(result)


def test_certification_audit_keeps_blocked_and_warning_findings_visible():
    result = audit_v3_7_graph_certification()

    assert any(finding.status == V37_CERTIFICATION_AUDIT_VISIBLE_BLOCKED for finding in result.findings)
    assert any(finding.status == V37_CERTIFICATION_AUDIT_VISIBLE_WARNING for finding in result.findings)


def test_certification_audit_detects_hidden_finding():
    certification = build_v3_7_graph_planning_continuity_certification()
    hidden_finding = replace(certification.findings[0], hidden=True)
    result = audit_v3_7_graph_certification(replace(certification, findings=(hidden_finding,) + certification.findings[1:]))

    assert result.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_FAILED
    assert any(finding.status == V37_CERTIFICATION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY for finding in result.findings)


def test_certification_audit_detects_replay_gap_and_execution_boundary():
    certification = build_v3_7_graph_planning_continuity_certification()
    broken_replay = replace(certification.replay_evidence[0], evidence_source_references=())
    replay_result = audit_v3_7_graph_certification(replace(certification, replay_evidence=(broken_replay,)))
    execution_result = audit_v3_7_graph_certification(replace(certification, routing_enabled=True))

    assert replay_result.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_FAILED
    assert any(finding.status == V37_CERTIFICATION_AUDIT_BLOCKED_BY_REPLAY for finding in replay_result.findings)
    assert execution_result.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_FAILED
    assert any(finding.status == V37_CERTIFICATION_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY for finding in execution_result.findings)
