from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_scenario_models import (
    V37_GRAPH_SCENARIO_STATUSES,
    V37_SCENARIO_STATUS_COMPARISON_READY,
    export_v3_7_graph_scenario_counts,
    hash_v3_7_graph_planning_scenario,
    serialize_v3_7_graph_planning_scenario,
    validate_v3_7_graph_scenario_hash_stability,
    validate_v3_7_graph_scenario_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario
from scripts.report_v3_7_graph_planning_scenarios import build_v3_7_graph_planning_scenarios_report


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_scenario_statuses_are_explicit():
    assert V37_GRAPH_SCENARIO_STATUSES == (
        "initialized",
        "evaluated",
        "blocked",
        "unsupported",
        "prohibited",
        "unknown",
        "comparison_ready",
        "audit_failed",
        "closed",
    )


def test_scenario_is_immutable_and_non_executable():
    scenario = build_v3_7_graph_planning_scenario()

    with pytest.raises(FrozenInstanceError):
        scenario.routing_enabled = True

    assert scenario.status == V37_SCENARIO_STATUS_COMPARISON_READY
    assert scenario.scenarios_are_non_executable is True
    assert scenario.hypothetical_planning_evidence_only is True
    assert scenario.hypothetical_variations_are_not_runtime_branches is True
    assert scenario.scenario_replay_evidence_is_not_runtime_replay is True
    assert scenario.comparisons_do_not_imply_orchestration_selection is True
    assert scenario.routing_enabled is False
    assert scenario.scheduling_enabled is False
    assert scenario.dispatch_enabled is False
    assert scenario.graph_traversal_execution_enabled is False
    assert scenario.scenario_execution_enabled is False


def test_scenario_serialization_and_hash_are_deterministic():
    scenario = build_v3_7_graph_planning_scenario()
    reordered = replace(
        scenario,
        metadata=tuple(reversed(scenario.metadata)),
        planning_session_references=tuple(reversed(scenario.planning_session_references)),
        graph_snapshot_references=tuple(reversed(scenario.graph_snapshot_references)),
        variations=tuple(reversed(scenario.variations)),
        evaluation_evidence_references=tuple(reversed(scenario.evaluation_evidence_references)),
        comparison_evidence=tuple(reversed(scenario.comparison_evidence)),
        replay_evidence=tuple(reversed(scenario.replay_evidence)),
        rollback_continuity_references=tuple(reversed(scenario.rollback_continuity_references)),
        audit_trail=tuple(reversed(scenario.audit_trail)),
    )

    assert serialize_v3_7_graph_planning_scenario(scenario) == serialize_v3_7_graph_planning_scenario(reordered)
    assert hash_v3_7_graph_planning_scenario(scenario) == hash_v3_7_graph_planning_scenario(reordered)
    assert validate_v3_7_graph_scenario_serialization_stability(scenario)["stable"] is True
    assert validate_v3_7_graph_scenario_hash_stability(scenario)["stable"] is True
    assert json.loads(serialize_v3_7_graph_planning_scenario(scenario))["dispatch_enabled"] is False


def test_scenario_counts_and_report_are_deterministic():
    scenario = build_v3_7_graph_planning_scenario()
    first = build_v3_7_graph_planning_scenarios_report(REPO_ROOT)
    second = build_v3_7_graph_planning_scenarios_report(REPO_ROOT)

    assert export_v3_7_graph_scenario_counts(scenario) == {
        "scenario_count": 1,
        "variation_count": 7,
        "comparison_count": 1,
        "replay_evidence_count": 1,
        "audit_trail_count": 7,
    }
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["scenarios_are_non_executable"] is True
    assert first["hypothetical_variations_are_not_runtime_branches"] is True
    assert first["routing_enabled"] is False
    assert first["scheduling_enabled"] is False
    assert first["dispatch_enabled"] is False
    assert first["graph_traversal_execution_enabled"] is False
