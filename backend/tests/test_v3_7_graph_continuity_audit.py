from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_continuity_audit import (
    V37_GRAPH_CONTINUITY_AUDIT_BLOCKED,
    V37_GRAPH_CONTINUITY_AUDIT_STABLE,
    V37_GRAPH_CONTINUITY_BLOCKED_BY_EVALUATION_GAP,
    V37_GRAPH_CONTINUITY_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_GRAPH_CONTINUITY_BLOCKED_BY_REPLAY_GAP,
    audit_v3_7_graph_continuity,
    hash_v3_7_graph_continuity_audit_result,
    serialize_v3_7_graph_continuity_audit_result,
)
from app.runtime_orchestration.v3_7_graph_evaluation_replay import build_v3_7_graph_evaluation_replay_packets
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


def test_graph_continuity_audit_is_stable_and_preserves_all_continuity_layers():
    result = audit_v3_7_graph_continuity()

    assert result.audit_status == V37_GRAPH_CONTINUITY_AUDIT_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 3
    assert result.evaluation_continuity_preserved is True
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.governance_continuity_preserved is True
    assert result.compatibility_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.deterministic_audit_hash == hash_v3_7_graph_continuity_audit_result(result)
    assert serialize_v3_7_graph_continuity_audit_result(result) == serialize_v3_7_graph_continuity_audit_result(result)


def test_graph_continuity_audit_detects_evaluation_ordering_gap():
    chain = build_v3_7_graph_evaluation_chain()
    broken_step = replace(chain.steps[0], step_order=3)
    result = audit_v3_7_graph_continuity(replace(chain, steps=(broken_step,) + chain.steps[1:]))

    assert result.audit_status == V37_GRAPH_CONTINUITY_AUDIT_BLOCKED
    assert any(finding.status == V37_GRAPH_CONTINUITY_BLOCKED_BY_EVALUATION_GAP for finding in result.findings)


def test_graph_continuity_audit_detects_replay_gap():
    chain = build_v3_7_graph_evaluation_chain()
    packet = build_v3_7_graph_evaluation_replay_packets(chain)[0]
    result = audit_v3_7_graph_continuity(chain, (replace(packet, replay_lineage_references=()),))

    assert result.audit_status == V37_GRAPH_CONTINUITY_AUDIT_BLOCKED
    assert any(finding.status == V37_GRAPH_CONTINUITY_BLOCKED_BY_REPLAY_GAP for finding in result.findings)


def test_graph_continuity_audit_detects_execution_capability():
    chain = build_v3_7_graph_evaluation_chain()
    result = audit_v3_7_graph_continuity(replace(chain, graph_execution_enabled=True))

    assert result.audit_status == V37_GRAPH_CONTINUITY_AUDIT_BLOCKED
    assert any(finding.status == V37_GRAPH_CONTINUITY_BLOCKED_BY_EXECUTION_CAPABILITY for finding in result.findings)
