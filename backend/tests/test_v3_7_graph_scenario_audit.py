from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_scenario_audit import (
    V37_GRAPH_SCENARIO_AUDIT_FAILED,
    V37_GRAPH_SCENARIO_AUDIT_STABLE,
    V37_SCENARIO_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_SCENARIO_AUDIT_BLOCKED_BY_FINDING_VISIBILITY,
    V37_SCENARIO_AUDIT_BLOCKED_BY_REPLAY,
    V37_SCENARIO_AUDIT_VISIBLE_BLOCKED,
    audit_v3_7_graph_scenario,
    hash_v3_7_graph_scenario_audit_result,
    serialize_v3_7_graph_scenario_audit_result,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def test_scenario_audit_is_stable_and_preserves_continuity_layers():
    result = audit_v3_7_graph_scenario()

    assert result.audit_status == V37_GRAPH_SCENARIO_AUDIT_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 4
    assert result.scenario_identity_stable is True
    assert result.scenario_variation_continuity_preserved is True
    assert result.graph_snapshot_continuity_preserved is True
    assert result.scenario_comparison_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.deterministic_audit_hash == hash_v3_7_graph_scenario_audit_result(result)
    assert serialize_v3_7_graph_scenario_audit_result(result) == serialize_v3_7_graph_scenario_audit_result(result)


def test_scenario_audit_keeps_blocked_state_visible():
    result = audit_v3_7_graph_scenario()

    assert any(finding.status == V37_SCENARIO_AUDIT_VISIBLE_BLOCKED for finding in result.findings)


def test_scenario_audit_detects_hidden_audit_entry():
    scenario = build_v3_7_graph_planning_scenario()
    hidden_entry = replace(scenario.audit_trail[1], hidden=True)
    result = audit_v3_7_graph_scenario(replace(scenario, audit_trail=(scenario.audit_trail[0], hidden_entry) + scenario.audit_trail[2:]))

    assert result.audit_status == V37_GRAPH_SCENARIO_AUDIT_FAILED
    assert any(finding.status == V37_SCENARIO_AUDIT_BLOCKED_BY_FINDING_VISIBILITY for finding in result.findings)


def test_scenario_audit_detects_replay_gap_and_execution_capability():
    scenario = build_v3_7_graph_planning_scenario()
    broken_replay = replace(scenario.replay_evidence[0], variation_references=())
    replay_result = audit_v3_7_graph_scenario(replace(scenario, replay_evidence=(broken_replay,)))
    execution_result = audit_v3_7_graph_scenario(replace(scenario, runtime_branching_behavior_enabled=True))

    assert replay_result.audit_status == V37_GRAPH_SCENARIO_AUDIT_FAILED
    assert any(finding.status == V37_SCENARIO_AUDIT_BLOCKED_BY_REPLAY for finding in replay_result.findings)
    assert execution_result.audit_status == V37_GRAPH_SCENARIO_AUDIT_FAILED
    assert any(finding.status == V37_SCENARIO_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY for finding in execution_result.findings)
