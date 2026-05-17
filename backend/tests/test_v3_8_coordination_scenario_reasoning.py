from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest


APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_scenario_models import (  # noqa: E402
    COMPARISON_EXECUTION_LANGUAGE_TERMS,
    COMPARISON_OPTIMIZATION_LANGUAGE_TERMS,
    COMPARISON_RECOMMENDATION_LANGUAGE_TERMS,
    SCENARIO_STATE_BLOCKED,
    SCENARIO_STATE_EXPERIMENTAL,
    SCENARIO_STATE_MODELED,
    SCENARIO_STATE_NON_EXECUTABLE,
    SCENARIO_STATE_PLANNING_ONLY,
    SCENARIO_STATE_PROHIBITED,
    SCENARIO_STATE_UNKNOWN,
    SCENARIO_STATE_UNMODELED,
    SCENARIO_STATE_UNSUPPORTED,
    SCENARIO_VISIBILITY_FAIL_VISIBLE,
    V3_8_SCENARIO_AUDIT_STABLE,
    export_v3_8_scenario_comparison,
    hash_v3_8_scenario_audit,
    scenario_id,
    serialize_v3_8_scenario_audit,
    validate_v3_8_scenario_hash_stability,
    validate_v3_8_scenario_serialization_stability,
)
from runtime_coordination.coordination_scenario_reasoning import (  # noqa: E402
    reason_v3_8_coordination_scenario,
)
from scripts.report_v3_8_coordination_scenario_reasoning import (  # noqa: E402
    build_v3_8_coordination_scenario_reasoning_report,
)


def _comparison_text(comparison: object) -> str:
    exported = export_v3_8_scenario_comparison(comparison)
    values: list[str] = []
    for value in exported.values():
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            values.extend(str(item) for item in value)
    return " ".join(values).lower()


def test_v3_8_scenario_audit_is_immutable_and_non_executable():
    audit = reason_v3_8_coordination_scenario()

    with pytest.raises(FrozenInstanceError):
        audit.orchestration_execution_enabled = True

    assert audit.audit_status == V3_8_SCENARIO_AUDIT_STABLE
    assert audit.immutable_evidence_records is True
    assert audit.non_executable is True
    assert audit.coordination_execution_enabled is False
    assert audit.orchestration_execution_enabled is False
    assert audit.routing_enabled is False
    assert audit.scheduling_enabled is False
    assert audit.dispatch_enabled is False
    assert audit.traversal_execution_enabled is False
    assert audit.optimization_enabled is False
    assert audit.recommendation_enabled is False
    assert audit.scoring_decision_system_enabled is False
    assert audit.execution_authorization_enabled is False
    assert audit.runtime_engine_enabled is False
    assert audit.state_machine_enabled is False
    assert audit.scenario_runtime_state_machine_enabled is False
    assert audit.callable_coordination_flow_enabled is False
    assert audit.persistent_runtime_mutation_enabled is False
    assert audit.hidden_transition_enabled is False
    assert audit.silent_fallback_enabled is False
    assert audit.validation_totals["execution_boundary_violation_count"] == 0


def test_v3_8_scenario_serialization_hashing_and_output_are_stable():
    first = reason_v3_8_coordination_scenario()
    second = reason_v3_8_coordination_scenario()

    assert first == second
    assert serialize_v3_8_scenario_audit(first) == serialize_v3_8_scenario_audit(second)
    assert hash_v3_8_scenario_audit(first) == hash_v3_8_scenario_audit(second)
    assert validate_v3_8_scenario_serialization_stability(first)["stable"] is True
    assert validate_v3_8_scenario_hash_stability(first)["stable"] is True
    serialized = json.loads(serialize_v3_8_scenario_audit(first))
    assert serialized["non_executable"] is True
    assert serialized["scenario_runtime_state_machine_enabled"] is False
    assert serialized["recommendation_enabled"] is False
    assert serialized["optimization_enabled"] is False


def test_v3_8_scenario_ids_are_deterministic():
    audit = reason_v3_8_coordination_scenario()

    scenario_ids = tuple(result.scenario_id for result in audit.scenario_results)
    assert len(scenario_ids) == len(set(scenario_ids))
    for result in audit.scenario_results:
        subject_id = result.scenario_id.removeprefix(f"v3_8_scenario_{result.scenario_state}_")
        assert result.scenario_id == scenario_id(result.scenario_state, subject_id)
        assert result.source_coordination_references
        assert result.boundary_context_ids
        assert result.compatibility_context_ids
        assert result.evaluation_context_ids
        assert result.session_context_ids
        assert result.provenance_reference
        assert result.replay_safe_evidence
        assert result.rollback_safe_evidence
        assert result.non_execution_confirmation is True


def test_v3_8_scenario_counts_cover_required_states():
    audit = reason_v3_8_coordination_scenario()

    assert audit.validation_totals["scenario_result_count"] == 23
    assert audit.state_counts[SCENARIO_STATE_MODELED] == 8
    assert audit.state_counts[SCENARIO_STATE_UNMODELED] == 1
    assert audit.state_counts[SCENARIO_STATE_BLOCKED] == 2
    assert audit.state_counts[SCENARIO_STATE_UNSUPPORTED] == 3
    assert audit.state_counts[SCENARIO_STATE_PROHIBITED] == 4
    assert audit.state_counts[SCENARIO_STATE_UNKNOWN] == 2
    assert audit.state_counts[SCENARIO_STATE_EXPERIMENTAL] == 1
    assert audit.state_counts[SCENARIO_STATE_PLANNING_ONLY] == 1
    assert audit.state_counts[SCENARIO_STATE_NON_EXECUTABLE] == 1


def test_v3_8_scenario_comparisons_are_stable_evidence_records_without_decision_behavior():
    first = reason_v3_8_coordination_scenario()
    second = reason_v3_8_coordination_scenario()

    assert first.scenario_comparisons == second.scenario_comparisons
    assert first.validation_totals["comparison_count"] == 3
    assert len({comparison.comparison_id for comparison in first.scenario_comparisons}) == 3
    for comparison in first.scenario_comparisons:
        text = _comparison_text(comparison)
        assert comparison.compared_scenario_ids
        assert comparison.boundary_context_ids
        assert comparison.compatibility_context_ids
        assert comparison.evaluation_context_ids
        assert comparison.session_context_ids
        assert comparison.provenance_references
        assert comparison.replay_safe_evidence
        assert comparison.rollback_safe_evidence
        assert comparison.non_execution_confirmation is True
        assert comparison.immutable_evidence_record is True
        assert comparison.runtime_state_machine is False
        assert comparison.recommendation_behavior_enabled is False
        assert comparison.optimization_behavior_enabled is False
        assert comparison.scoring_behavior_enabled is False
        assert comparison.execution_behavior_detected is False
        assert all(term not in text for term in COMPARISON_RECOMMENDATION_LANGUAGE_TERMS)
        assert all(term not in text for term in COMPARISON_OPTIMIZATION_LANGUAGE_TERMS)
        assert all(term not in text for term in COMPARISON_EXECUTION_LANGUAGE_TERMS)

    assert first.validation_totals["recommendation_language_violation_count"] == 0
    assert first.validation_totals["optimization_language_violation_count"] == 0
    assert first.validation_totals["comparison_execution_language_violation_count"] == 0
    assert first.validation_totals["recommendation_behavior_violation_count"] == 0
    assert first.validation_totals["optimization_behavior_violation_count"] == 0


def test_v3_8_scenario_preserves_boundary_compatibility_evaluation_and_session_context():
    audit = reason_v3_8_coordination_scenario()

    assert audit.validation_totals["boundary_context_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["compatibility_context_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["evaluation_context_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["session_context_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["boundary_context_preserved_count"] == audit.validation_totals["scenario_result_count"]
    assert (
        audit.validation_totals["compatibility_context_preserved_count"]
        == audit.validation_totals["scenario_result_count"]
    )
    assert audit.validation_totals["evaluation_context_preserved_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["session_context_preserved_count"] == audit.validation_totals["scenario_result_count"]
    assert all(result.evidence.boundary_context_preserved for result in audit.scenario_results)
    assert all(result.evidence.compatibility_context_preserved for result in audit.scenario_results)
    assert all(result.evidence.evaluation_context_preserved for result in audit.scenario_results)
    assert all(result.evidence.session_context_preserved for result in audit.scenario_results)


def test_v3_8_non_modeled_scenario_states_are_fail_visible_and_distinct():
    audit = reason_v3_8_coordination_scenario()
    required = {
        SCENARIO_STATE_UNMODELED: 1,
        SCENARIO_STATE_BLOCKED: 2,
        SCENARIO_STATE_UNSUPPORTED: 3,
        SCENARIO_STATE_PROHIBITED: 4,
        SCENARIO_STATE_UNKNOWN: 2,
    }

    for state, expected_count in required.items():
        results = [result for result in audit.scenario_results if result.scenario_state == state]
        assert len(results) == expected_count
        assert all(result.deterministic_visibility_status == SCENARIO_VISIBILITY_FAIL_VISIBLE for result in results)
        assert all(result.fail_visible and not result.hidden for result in results)
        assert all(result.hidden_risk is False for result in results)

    assert audit.validation_totals["fail_visible_unmodeled_count"] == 1
    assert audit.validation_totals["fail_visible_blocked_count"] == 2
    assert audit.validation_totals["fail_visible_unsupported_count"] == 3
    assert audit.validation_totals["fail_visible_prohibited_count"] == 4
    assert audit.validation_totals["fail_visible_unknown_count"] == 2


def test_v3_8_experimental_planning_only_and_non_executable_scenarios_are_explicit():
    audit = reason_v3_8_coordination_scenario()

    experimental = [result for result in audit.scenario_results if result.scenario_state == SCENARIO_STATE_EXPERIMENTAL]
    planning_only = [result for result in audit.scenario_results if result.scenario_state == SCENARIO_STATE_PLANNING_ONLY]
    non_executable = [result for result in audit.scenario_results if result.scenario_state == SCENARIO_STATE_NON_EXECUTABLE]

    assert len(experimental) == 1
    assert experimental[0].experimental_label_explicit is True
    assert len(planning_only) == 1
    assert len(non_executable) == 1
    assert all(result.non_execution_confirmation is True for result in experimental + planning_only + non_executable)
    assert all(result.execution_behavior_detected is False for result in experimental + planning_only + non_executable)
    assert all(result.callable_execution_path_enabled is False for result in experimental + planning_only + non_executable)
    assert all(
        result.deterministic_visibility_status == SCENARIO_VISIBILITY_FAIL_VISIBLE
        for result in experimental + planning_only + non_executable
    )


def test_v3_8_scenario_replay_rollback_provenance_and_immutability_are_preserved():
    audit = reason_v3_8_coordination_scenario()

    assert audit.validation_totals["replay_safe_evidence_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["rollback_safe_evidence_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["provenance_continuity_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["immutable_evidence_record_count"] == audit.validation_totals["scenario_result_count"]
    assert audit.validation_totals["runtime_state_machine_count"] == 0
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert all(result.evidence.replay_safe for result in audit.scenario_results)
    assert all(result.evidence.rollback_safe for result in audit.scenario_results)
    assert all(result.evidence.provenance_preserved for result in audit.scenario_results)
    assert all(
        result.immutable_evidence_record and result.evidence.immutable_evidence_record
        for result in audit.scenario_results
    )
    assert all(result.runtime_state_machine is False for result in audit.scenario_results)
    assert all(result.evidence.runtime_state_machine is False for result in audit.scenario_results)
    assert audit.validation_totals["comparison_replay_safe_evidence_count"] == audit.validation_totals["comparison_count"]
    assert (
        audit.validation_totals["comparison_rollback_safe_evidence_count"]
        == audit.validation_totals["comparison_count"]
    )
    assert (
        audit.validation_totals["comparison_provenance_continuity_count"]
        == audit.validation_totals["comparison_count"]
    )


def test_v3_8_scenario_report_contains_required_totals_and_guarantees():
    report = build_v3_8_coordination_scenario_reasoning_report()

    assert report["summary"]["audit_status"] == V3_8_SCENARIO_AUDIT_STABLE
    assert report["summary"]["scenario_result_count"] == 23
    assert report["summary"]["comparison_count"] == 3
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["unmodeled_fail_visible"] is True
    assert report["summary"]["blocked_fail_visible"] is True
    assert report["summary"]["unsupported_fail_visible"] is True
    assert report["summary"]["prohibited_fail_visible"] is True
    assert report["summary"]["unknown_fail_visible"] is True
    assert report["summary"]["boundary_context_verified"] is True
    assert report["summary"]["compatibility_context_verified"] is True
    assert report["summary"]["evaluation_context_verified"] is True
    assert report["summary"]["session_context_verified"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["comparison_replay_verified"] is True
    assert report["summary"]["comparison_rollback_verified"] is True
    assert report["summary"]["comparison_provenance_verified"] is True
    assert report["summary"]["immutable_evidence_records_verified"] is True
    assert report["summary"]["runtime_state_machine_count"] == 0
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["recommendation_language_violation_count"] == 0
    assert report["summary"]["optimization_language_violation_count"] == 0
    assert report["summary"]["recommendation_behavior_violation_count"] == 0
    assert report["summary"]["optimization_behavior_violation_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["scenario_totals"]["modeled_count"] == 8
    assert report["scenario_totals"]["unmodeled_count"] == 1
    assert report["scenario_totals"]["blocked_count"] == 2
    assert report["scenario_totals"]["unsupported_count"] == 3
    assert report["scenario_totals"]["prohibited_count"] == 4
    assert report["scenario_totals"]["unknown_count"] == 2
    assert report["scenario_totals"]["experimental_count"] == 1
    assert report["scenario_totals"]["planning_only_count"] == 1
    assert report["scenario_totals"]["non_executable_count"] == 1
    assert report["scenario_totals"]["comparison_count"] == 3
    assert report["scenario_totals"]["boundary_context_count"] == 23
    assert report["scenario_totals"]["compatibility_context_count"] == 23
    assert report["scenario_totals"]["evaluation_context_count"] == 23
    assert report["scenario_totals"]["session_context_count"] == 23
    assert report["scenario_totals"]["hidden_risk_count"] == 0
    assert report["scenario_totals"]["recommendation_language_violation_count"] == 0
    assert report["scenario_totals"]["optimization_language_violation_count"] == 0
    assert report["scenario_totals"]["execution_boundary_violation_count"] == 0
