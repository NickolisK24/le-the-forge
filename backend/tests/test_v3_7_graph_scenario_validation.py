from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_scenario_models import (
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_UNSUPPORTED,
)
from app.runtime_orchestration.v3_7_graph_scenario_validation import (
    V37_GRAPH_SCENARIO_VALIDATION_BLOCKED,
    V37_GRAPH_SCENARIO_VALIDATION_STABLE,
    V37_SCENARIO_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_SCENARIO_VALIDATION_BLOCKED_BY_HIDDEN_STATE,
    V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_COMPARISON,
    V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE,
    V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_VARIATION,
    validate_v3_7_graph_scenarios,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def test_default_scenario_validation_is_stable_and_fail_visible():
    result = validate_v3_7_graph_scenarios()

    assert result.validation_status == V37_GRAPH_SCENARIO_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 3
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.governance_continuity_preserved is True
    assert result.compatibility_continuity_preserved is True
    assert result.evaluation_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.non_execution_guarantee_preserved is True


def test_validation_detects_invalid_variation_replay_and_comparison():
    scenario = build_v3_7_graph_planning_scenario()
    broken_variation = replace(scenario.variations[0], executable_orchestration_branch=True)
    variation_result = validate_v3_7_graph_scenarios((replace(scenario, variations=(broken_variation,) + scenario.variations[1:]),))
    broken_replay = replace(scenario.replay_evidence[0], variation_references=())
    replay_result = validate_v3_7_graph_scenarios((replace(scenario, replay_evidence=(broken_replay,)),))
    broken_comparison = replace(scenario.comparison_evidence[0], compared_variation_ids=("missing",))
    comparison_result = validate_v3_7_graph_scenarios((replace(scenario, comparison_evidence=(broken_comparison,)),))

    assert variation_result.validation_status == V37_GRAPH_SCENARIO_VALIDATION_BLOCKED
    assert any(finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_VARIATION for finding in variation_result.findings)
    assert replay_result.validation_status == V37_GRAPH_SCENARIO_VALIDATION_BLOCKED
    assert any(finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE for finding in replay_result.findings)
    assert comparison_result.validation_status == V37_GRAPH_SCENARIO_VALIDATION_BLOCKED
    assert any(finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_COMPARISON for finding in comparison_result.findings)


def test_validation_detects_hidden_unsupported_prohibited_and_unknown_states():
    scenario = build_v3_7_graph_planning_scenario()
    hidden_entries = tuple(
        replace(entry, hidden=True)
        if entry.scenario_status in (V37_SCENARIO_STATUS_PROHIBITED, V37_SCENARIO_STATUS_UNSUPPORTED, V37_SCENARIO_STATUS_UNKNOWN)
        else entry
        for entry in scenario.audit_trail
    )
    result = validate_v3_7_graph_scenarios((replace(scenario, audit_trail=hidden_entries),))

    assert result.validation_status == V37_GRAPH_SCENARIO_VALIDATION_BLOCKED
    assert any(finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_HIDDEN_STATE for finding in result.findings)
    assert result.hidden_prohibited_state_count == 1
    assert result.hidden_unsupported_state_count == 1
    assert result.hidden_unknown_state_count == 1


def test_validation_detects_execution_capability():
    scenario = build_v3_7_graph_planning_scenario()
    result = validate_v3_7_graph_scenarios((replace(scenario, scenario_execution_enabled=True),))

    assert result.validation_status == V37_GRAPH_SCENARIO_VALIDATION_BLOCKED
    assert any(finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY for finding in result.findings)
