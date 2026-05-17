from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest


APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_aggregation_models import (  # noqa: E402
    AGGREGATION_STATE_AGGREGATED,
    AGGREGATION_STATE_BLOCKED,
    AGGREGATION_STATE_EXPERIMENTAL,
    AGGREGATION_STATE_NON_EXECUTABLE,
    AGGREGATION_STATE_PARTIAL,
    AGGREGATION_STATE_PLANNING_ONLY,
    AGGREGATION_STATE_PROHIBITED,
    AGGREGATION_STATE_UNKNOWN,
    AGGREGATION_STATE_UNSUPPORTED,
    AGGREGATION_VISIBILITY_FAIL_VISIBLE,
    SUMMARY_EXECUTION_LANGUAGE_TERMS,
    SUMMARY_OPTIMIZATION_LANGUAGE_TERMS,
    SUMMARY_RANKING_LANGUAGE_TERMS,
    SUMMARY_RECOMMENDATION_LANGUAGE_TERMS,
    SUMMARY_SCORING_LANGUAGE_TERMS,
    SUMMARY_SELECTION_LANGUAGE_TERMS,
    V3_8_AGGREGATION_AUDIT_STABLE,
    aggregation_id,
    export_v3_8_intelligence_summary,
    hash_v3_8_aggregation_audit,
    serialize_v3_8_aggregation_audit,
    validate_v3_8_aggregation_hash_stability,
    validate_v3_8_aggregation_serialization_stability,
)
from runtime_coordination.coordination_intelligence_aggregation import (  # noqa: E402
    aggregate_v3_8_coordination_intelligence,
)
from scripts.report_v3_8_coordination_intelligence_aggregation import (  # noqa: E402
    build_v3_8_coordination_intelligence_aggregation_report,
)


def _summary_text(summary: object) -> str:
    exported = export_v3_8_intelligence_summary(summary)
    values: list[str] = []
    for value in exported.values():
        if isinstance(value, str):
            values.append(value)
    return " ".join(values).lower()


def test_v3_8_aggregation_audit_is_immutable_and_non_executable():
    audit = aggregate_v3_8_coordination_intelligence()

    with pytest.raises(FrozenInstanceError):
        audit.orchestration_execution_enabled = True

    assert audit.audit_status == V3_8_AGGREGATION_AUDIT_STABLE
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
    assert audit.ranking_enabled is False
    assert audit.scoring_choice_system_enabled is False
    assert audit.selection_engine_enabled is False
    assert audit.execution_authorization_enabled is False
    assert audit.runtime_engine_enabled is False
    assert audit.state_machine_enabled is False
    assert audit.aggregation_runtime_state_machine_enabled is False
    assert audit.callable_coordination_flow_enabled is False
    assert audit.persistent_runtime_mutation_enabled is False
    assert audit.hidden_transition_enabled is False
    assert audit.silent_fallback_enabled is False
    assert audit.validation_totals["execution_boundary_violation_count"] == 0


def test_v3_8_aggregation_serialization_hashing_and_output_are_stable():
    first = aggregate_v3_8_coordination_intelligence()
    second = aggregate_v3_8_coordination_intelligence()

    assert first == second
    assert serialize_v3_8_aggregation_audit(first) == serialize_v3_8_aggregation_audit(second)
    assert hash_v3_8_aggregation_audit(first) == hash_v3_8_aggregation_audit(second)
    assert validate_v3_8_aggregation_serialization_stability(first)["stable"] is True
    assert validate_v3_8_aggregation_hash_stability(first)["stable"] is True
    serialized = json.loads(serialize_v3_8_aggregation_audit(first))
    assert serialized["non_executable"] is True
    assert serialized["aggregation_runtime_state_machine_enabled"] is False
    assert serialized["recommendation_enabled"] is False
    assert serialized["optimization_enabled"] is False
    assert serialized["ranking_enabled"] is False
    assert serialized["selection_engine_enabled"] is False


def test_v3_8_aggregation_ids_are_deterministic():
    audit = aggregate_v3_8_coordination_intelligence()

    aggregation_ids = tuple(result.aggregation_id for result in audit.aggregation_results)
    assert len(aggregation_ids) == len(set(aggregation_ids))
    for result in audit.aggregation_results:
        subject_id = result.aggregation_id.removeprefix(f"v3_8_aggregation_{result.aggregation_state}_")
        assert result.aggregation_id == aggregation_id(result.aggregation_state, subject_id)
        assert result.source_coordination_references
        assert result.boundary_context_ids
        assert result.compatibility_context_ids
        assert result.evaluation_context_ids
        assert result.session_context_ids
        assert result.scenario_context_ids
        assert result.provenance_reference
        assert result.replay_safe_evidence
        assert result.rollback_safe_evidence
        assert result.non_execution_confirmation is True


def test_v3_8_aggregation_counts_cover_required_states():
    audit = aggregate_v3_8_coordination_intelligence()

    assert audit.validation_totals["aggregation_result_count"] == 23
    assert audit.state_counts[AGGREGATION_STATE_AGGREGATED] == 8
    assert audit.state_counts[AGGREGATION_STATE_PARTIAL] == 1
    assert audit.state_counts[AGGREGATION_STATE_BLOCKED] == 2
    assert audit.state_counts[AGGREGATION_STATE_UNSUPPORTED] == 3
    assert audit.state_counts[AGGREGATION_STATE_PROHIBITED] == 4
    assert audit.state_counts[AGGREGATION_STATE_UNKNOWN] == 2
    assert audit.state_counts[AGGREGATION_STATE_EXPERIMENTAL] == 1
    assert audit.state_counts[AGGREGATION_STATE_PLANNING_ONLY] == 1
    assert audit.state_counts[AGGREGATION_STATE_NON_EXECUTABLE] == 1
    assert audit.validation_totals["summary_count"] == 1


def test_v3_8_aggregation_summaries_are_stable_visibility_records_without_decision_behavior():
    first = aggregate_v3_8_coordination_intelligence()
    second = aggregate_v3_8_coordination_intelligence()

    assert first.intelligence_summaries == second.intelligence_summaries
    assert first.validation_totals["summary_count"] == 1
    summary = first.intelligence_summaries[0]
    text = _summary_text(summary)

    assert summary.total_coordination_record_count == 23
    assert summary.supported_visibility_count == 8
    assert summary.unsupported_visibility_count == 3
    assert summary.prohibited_visibility_count == 4
    assert summary.unknown_visibility_count == 2
    assert summary.compatibility_visibility_count == 23
    assert summary.evaluation_visibility_count == 23
    assert summary.session_visibility_count == 23
    assert summary.scenario_visibility_count == 23
    assert summary.fail_visible_finding_count == 15
    assert summary.provenance_continuity_count == 23
    assert summary.replay_evidence_count == 23
    assert summary.rollback_evidence_count == 23
    assert summary.non_execution_confirmation_count == 23
    assert summary.non_execution_confirmation is True
    assert summary.immutable_evidence_record is True
    assert summary.runtime_state_machine is False
    assert summary.recommendation_behavior_enabled is False
    assert summary.optimization_behavior_enabled is False
    assert summary.ranking_behavior_enabled is False
    assert summary.scoring_behavior_enabled is False
    assert summary.selection_behavior_enabled is False
    assert summary.execution_behavior_detected is False
    assert all(term not in text for term in SUMMARY_RECOMMENDATION_LANGUAGE_TERMS)
    assert all(term not in text for term in SUMMARY_OPTIMIZATION_LANGUAGE_TERMS)
    assert all(term not in text for term in SUMMARY_RANKING_LANGUAGE_TERMS)
    assert all(term not in text for term in SUMMARY_SCORING_LANGUAGE_TERMS)
    assert all(term not in text for term in SUMMARY_SELECTION_LANGUAGE_TERMS)
    assert all(term not in text for term in SUMMARY_EXECUTION_LANGUAGE_TERMS)

    assert first.validation_totals["recommendation_language_violation_count"] == 0
    assert first.validation_totals["optimization_language_violation_count"] == 0
    assert first.validation_totals["ranking_language_violation_count"] == 0
    assert first.validation_totals["scoring_behavior_violation_count"] == 0
    assert first.validation_totals["selection_behavior_violation_count"] == 0


def test_v3_8_aggregation_preserves_all_required_contexts():
    audit = aggregate_v3_8_coordination_intelligence()

    assert audit.validation_totals["boundary_context_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["compatibility_context_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["evaluation_context_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["session_context_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["scenario_context_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["boundary_context_preserved_count"] == audit.validation_totals["aggregation_result_count"]
    assert (
        audit.validation_totals["compatibility_context_preserved_count"]
        == audit.validation_totals["aggregation_result_count"]
    )
    assert audit.validation_totals["evaluation_context_preserved_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["session_context_preserved_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["scenario_context_preserved_count"] == audit.validation_totals["aggregation_result_count"]
    assert all(result.evidence.boundary_context_preserved for result in audit.aggregation_results)
    assert all(result.evidence.compatibility_context_preserved for result in audit.aggregation_results)
    assert all(result.evidence.evaluation_context_preserved for result in audit.aggregation_results)
    assert all(result.evidence.session_context_preserved for result in audit.aggregation_results)
    assert all(result.evidence.scenario_context_preserved for result in audit.aggregation_results)


def test_v3_8_non_aggregated_states_are_fail_visible_and_distinct():
    audit = aggregate_v3_8_coordination_intelligence()
    required = {
        AGGREGATION_STATE_PARTIAL: 1,
        AGGREGATION_STATE_BLOCKED: 2,
        AGGREGATION_STATE_UNSUPPORTED: 3,
        AGGREGATION_STATE_PROHIBITED: 4,
        AGGREGATION_STATE_UNKNOWN: 2,
    }

    for state, expected_count in required.items():
        results = [result for result in audit.aggregation_results if result.aggregation_state == state]
        assert len(results) == expected_count
        assert all(result.deterministic_visibility_status == AGGREGATION_VISIBILITY_FAIL_VISIBLE for result in results)
        assert all(result.fail_visible and not result.hidden for result in results)
        assert all(result.hidden_risk is False for result in results)

    assert audit.validation_totals["fail_visible_partial_count"] == 1
    assert audit.validation_totals["fail_visible_blocked_count"] == 2
    assert audit.validation_totals["fail_visible_unsupported_count"] == 3
    assert audit.validation_totals["fail_visible_prohibited_count"] == 4
    assert audit.validation_totals["fail_visible_unknown_count"] == 2
    assert audit.validation_totals["fail_visible_finding_count"] == 15


def test_v3_8_experimental_planning_only_and_non_executable_aggregations_are_explicit():
    audit = aggregate_v3_8_coordination_intelligence()

    experimental = [result for result in audit.aggregation_results if result.aggregation_state == AGGREGATION_STATE_EXPERIMENTAL]
    planning_only = [result for result in audit.aggregation_results if result.aggregation_state == AGGREGATION_STATE_PLANNING_ONLY]
    non_executable = [result for result in audit.aggregation_results if result.aggregation_state == AGGREGATION_STATE_NON_EXECUTABLE]

    assert len(experimental) == 1
    assert experimental[0].experimental_label_explicit is True
    assert len(planning_only) == 1
    assert len(non_executable) == 1
    assert all(result.non_execution_confirmation is True for result in experimental + planning_only + non_executable)
    assert all(result.execution_behavior_detected is False for result in experimental + planning_only + non_executable)
    assert all(result.callable_execution_path_enabled is False for result in experimental + planning_only + non_executable)
    assert all(
        result.deterministic_visibility_status == AGGREGATION_VISIBILITY_FAIL_VISIBLE
        for result in experimental + planning_only + non_executable
    )


def test_v3_8_aggregation_replay_rollback_provenance_and_immutability_are_preserved():
    audit = aggregate_v3_8_coordination_intelligence()

    assert audit.validation_totals["replay_safe_evidence_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["rollback_safe_evidence_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["provenance_continuity_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["immutable_evidence_record_count"] == audit.validation_totals["aggregation_result_count"]
    assert audit.validation_totals["runtime_state_machine_count"] == 0
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert all(result.evidence.replay_safe for result in audit.aggregation_results)
    assert all(result.evidence.rollback_safe for result in audit.aggregation_results)
    assert all(result.evidence.provenance_preserved for result in audit.aggregation_results)
    assert all(
        result.immutable_evidence_record and result.evidence.immutable_evidence_record
        for result in audit.aggregation_results
    )
    assert all(result.runtime_state_machine is False for result in audit.aggregation_results)
    assert all(result.evidence.runtime_state_machine is False for result in audit.aggregation_results)
    assert audit.validation_totals["summary_non_execution_confirmation_count"] == audit.validation_totals["summary_count"]


def test_v3_8_aggregation_report_contains_required_totals_and_guarantees():
    report = build_v3_8_coordination_intelligence_aggregation_report()

    assert report["summary"]["audit_status"] == V3_8_AGGREGATION_AUDIT_STABLE
    assert report["summary"]["aggregation_result_count"] == 23
    assert report["summary"]["summary_count"] == 1
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["partial_fail_visible"] is True
    assert report["summary"]["blocked_fail_visible"] is True
    assert report["summary"]["unsupported_fail_visible"] is True
    assert report["summary"]["prohibited_fail_visible"] is True
    assert report["summary"]["unknown_fail_visible"] is True
    assert report["summary"]["boundary_context_verified"] is True
    assert report["summary"]["compatibility_context_verified"] is True
    assert report["summary"]["evaluation_context_verified"] is True
    assert report["summary"]["session_context_verified"] is True
    assert report["summary"]["scenario_context_verified"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["immutable_evidence_records_verified"] is True
    assert report["summary"]["runtime_state_machine_count"] == 0
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["recommendation_language_violation_count"] == 0
    assert report["summary"]["optimization_language_violation_count"] == 0
    assert report["summary"]["ranking_language_violation_count"] == 0
    assert report["summary"]["scoring_behavior_violation_count"] == 0
    assert report["summary"]["selection_behavior_violation_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["aggregation_totals"]["aggregated_count"] == 8
    assert report["aggregation_totals"]["partial_count"] == 1
    assert report["aggregation_totals"]["blocked_count"] == 2
    assert report["aggregation_totals"]["unsupported_count"] == 3
    assert report["aggregation_totals"]["prohibited_count"] == 4
    assert report["aggregation_totals"]["unknown_count"] == 2
    assert report["aggregation_totals"]["experimental_count"] == 1
    assert report["aggregation_totals"]["planning_only_count"] == 1
    assert report["aggregation_totals"]["non_executable_count"] == 1
    assert report["aggregation_totals"]["summary_count"] == 1
    assert report["aggregation_totals"]["boundary_context_count"] == 23
    assert report["aggregation_totals"]["compatibility_context_count"] == 23
    assert report["aggregation_totals"]["evaluation_context_count"] == 23
    assert report["aggregation_totals"]["session_context_count"] == 23
    assert report["aggregation_totals"]["scenario_context_count"] == 23
    assert report["aggregation_totals"]["hidden_risk_count"] == 0
    assert report["aggregation_totals"]["recommendation_language_violation_count"] == 0
    assert report["aggregation_totals"]["optimization_language_violation_count"] == 0
    assert report["aggregation_totals"]["ranking_language_violation_count"] == 0
    assert report["aggregation_totals"]["scoring_behavior_violation_count"] == 0
    assert report["aggregation_totals"]["selection_behavior_violation_count"] == 0
    assert report["aggregation_totals"]["execution_boundary_violation_count"] == 0
