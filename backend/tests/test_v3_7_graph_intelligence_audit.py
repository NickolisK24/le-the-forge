from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from app.runtime_orchestration.v3_7_graph_intelligence_audit import (
    V37_GRAPH_INTELLIGENCE_AUDIT_FAILED,
    V37_GRAPH_INTELLIGENCE_AUDIT_STABLE,
    V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_INTELLIGENCE_AUDIT_BLOCKED_BY_FINDING_VISIBILITY,
    V37_INTELLIGENCE_AUDIT_BLOCKED_BY_REPLAY,
    V37_INTELLIGENCE_AUDIT_VISIBLE_BLOCKED,
    audit_v3_7_graph_intelligence,
    hash_v3_7_graph_intelligence_audit_result,
    serialize_v3_7_graph_intelligence_audit_result,
)


def test_intelligence_audit_is_stable_and_preserves_all_layers():
    result = audit_v3_7_graph_intelligence()

    assert result.audit_status == V37_GRAPH_INTELLIGENCE_AUDIT_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 4
    assert result.aggregation_identity_stable is True
    assert result.evidence_source_continuity_preserved is True
    assert result.governance_aggregation_continuity_preserved is True
    assert result.compatibility_aggregation_continuity_preserved is True
    assert result.evaluation_aggregation_continuity_preserved is True
    assert result.session_aggregation_continuity_preserved is True
    assert result.scenario_aggregation_continuity_preserved is True
    assert result.non_execution_guarantee_preserved is True
    assert result.deterministic_audit_hash == hash_v3_7_graph_intelligence_audit_result(result)
    assert serialize_v3_7_graph_intelligence_audit_result(result) == serialize_v3_7_graph_intelligence_audit_result(result)


def test_intelligence_audit_keeps_blocked_state_visible():
    result = audit_v3_7_graph_intelligence()

    assert any(finding.status == V37_INTELLIGENCE_AUDIT_VISIBLE_BLOCKED for finding in result.findings)


def test_intelligence_audit_detects_hidden_finding():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    hidden_finding = replace(aggregation.findings[0], hidden=True)
    result = audit_v3_7_graph_intelligence(replace(aggregation, findings=(hidden_finding,) + aggregation.findings[1:]))

    assert result.audit_status == V37_GRAPH_INTELLIGENCE_AUDIT_FAILED
    assert any(finding.status == V37_INTELLIGENCE_AUDIT_BLOCKED_BY_FINDING_VISIBILITY for finding in result.findings)


def test_intelligence_audit_detects_replay_gap_and_execution_capability():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    broken_replay = replace(aggregation.replay_evidence[0], evidence_source_references=())
    replay_result = audit_v3_7_graph_intelligence(replace(aggregation, replay_evidence=(broken_replay,)))
    execution_result = audit_v3_7_graph_intelligence(replace(aggregation, runtime_decision_making_enabled=True))

    assert replay_result.audit_status == V37_GRAPH_INTELLIGENCE_AUDIT_FAILED
    assert any(finding.status == V37_INTELLIGENCE_AUDIT_BLOCKED_BY_REPLAY for finding in replay_result.findings)
    assert execution_result.audit_status == V37_GRAPH_INTELLIGENCE_AUDIT_FAILED
    assert any(finding.status == V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY for finding in execution_result.findings)
