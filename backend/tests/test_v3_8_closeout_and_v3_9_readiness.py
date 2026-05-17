from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.v3_8_closeout_readiness_audit import (  # noqa: E402
    EXPECTED_PHASE_COUNT,
    audit_v3_8_closeout_and_v3_9_readiness,
)
from runtime_coordination.v3_8_closeout_readiness_models import (  # noqa: E402
    V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING,
    V3_8_CLOSEOUT_ID,
    V3_8_CLOSEOUT_INCOMPLETE,
    V3_8_CLOSEOUT_PROHIBITED,
    V3_8_CLOSEOUT_UNKNOWN,
    V3_8_CLOSEOUT_UNSUPPORTED,
    V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE,
    V3_9_PLANNING_BLOCKED,
    V3_9_PLANNING_READY,
    V38CloseoutReadinessInput,
    hash_v3_8_closeout_readiness_result,
    serialize_v3_8_closeout_readiness_result,
    validate_v3_8_closeout_hash_stability,
    validate_v3_8_closeout_serialization_stability,
)
from scripts.report_v3_8_closeout_and_v3_9_readiness import (  # noqa: E402
    build_v3_8_closeout_and_v3_9_readiness_report,
)


def test_v3_8_closeout_is_immutable_ready_and_non_executable():
    result = audit_v3_8_closeout_and_v3_9_readiness()

    with pytest.raises(FrozenInstanceError):
        result.orchestration_execution_enabled = True

    assert result.closeout_id == V3_8_CLOSEOUT_ID
    assert result.closeout_state == V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING
    assert result.v3_9_readiness_state == V3_9_PLANNING_READY
    assert result.non_execution_confirmation is True
    assert result.prohibited_behavior_confirmation is True
    assert result.coordination_execution_enabled is False
    assert result.orchestration_execution_enabled is False
    assert result.routing_enabled is False
    assert result.scheduling_enabled is False
    assert result.dispatch_enabled is False
    assert result.traversal_enabled is False
    assert result.optimization_enabled is False
    assert result.recommendation_enabled is False
    assert result.ranking_enabled is False
    assert result.scoring_enabled is False
    assert result.selection_enabled is False
    assert result.execution_authorization_enabled is False
    assert result.runtime_mutation_enabled is False
    assert result.runtime_engine_enabled is False
    assert result.state_machine_enabled is False
    assert result.callable_coordination_flow_enabled is False
    assert result.hidden_transition_enabled is False
    assert result.silent_fallback_enabled is False
    assert result.production_behavior_enabled is False


def test_v3_8_closeout_serialization_hashing_and_output_are_stable():
    first = audit_v3_8_closeout_and_v3_9_readiness()
    second = audit_v3_8_closeout_and_v3_9_readiness()

    assert first == second
    assert serialize_v3_8_closeout_readiness_result(first) == serialize_v3_8_closeout_readiness_result(second)
    assert hash_v3_8_closeout_readiness_result(first) == hash_v3_8_closeout_readiness_result(second)
    assert validate_v3_8_closeout_serialization_stability(first)["stable"] is True
    assert validate_v3_8_closeout_hash_stability(first)["stable"] is True
    serialized = json.loads(serialize_v3_8_closeout_readiness_result(first))
    assert serialized["closeout_id"] == V3_8_CLOSEOUT_ID
    assert serialized["closeout_state"] == V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING
    assert serialized["non_execution_confirmation"] is True


def test_v3_8_closeout_covers_all_phases_reports_and_docs():
    result = audit_v3_8_closeout_and_v3_9_readiness()

    assert result.validation_totals["expected_phase_count"] == EXPECTED_PHASE_COUNT
    assert result.validation_totals["audited_phase_count"] == EXPECTED_PHASE_COUNT
    assert result.validation_totals["generated_report_count"] == EXPECTED_PHASE_COUNT
    assert result.validation_totals["migration_documentation_count"] == EXPECTED_PHASE_COUNT
    assert len(result.audited_phase_list) == EXPECTED_PHASE_COUNT
    assert len(result.generated_report_list) == EXPECTED_PHASE_COUNT
    assert len(result.migration_doc_list) == EXPECTED_PHASE_COUNT
    assert all(evidence.report_exists for evidence in result.audited_phase_list)
    assert all(evidence.migration_doc_exists for evidence in result.audited_phase_list)
    assert all(evidence.module_paths_exist for evidence in result.audited_phase_list)
    assert all(evidence.script_exists for evidence in result.audited_phase_list)
    assert all(evidence.test_exists for evidence in result.audited_phase_list)
    assert "docs/generated/v3_8_coordination_foundations_report.json" in result.generated_report_list
    assert "docs/generated/v3_8_coordination_continuity_certification_report.json" in result.generated_report_list
    assert "docs/migration/V3_8_COORDINATION_FOUNDATIONS.md" in result.migration_doc_list
    assert "docs/migration/V3_8_COORDINATION_CONTINUITY_CERTIFICATION.md" in result.migration_doc_list


def test_v3_8_closeout_evidence_coverage_is_visible():
    result = audit_v3_8_closeout_and_v3_9_readiness()

    assert result.validation_totals["deterministic_evidence_count"] == EXPECTED_PHASE_COUNT
    assert result.validation_totals["replay_evidence_count"] == EXPECTED_PHASE_COUNT
    assert result.validation_totals["rollback_evidence_count"] == EXPECTED_PHASE_COUNT
    assert result.validation_totals["provenance_continuity_count"] == EXPECTED_PHASE_COUNT
    assert result.provenance_continuity_summary["provenance_continuity_complete"] is True
    assert result.replay_evidence_summary["replay_evidence_complete"] is True
    assert result.rollback_evidence_summary["rollback_evidence_complete"] is True
    assert all(evidence.deterministic_evidence_present for evidence in result.audited_phase_list)
    assert all(evidence.replay_evidence_visible for evidence in result.audited_phase_list)
    assert all(evidence.rollback_evidence_visible for evidence in result.audited_phase_list)
    assert all(evidence.provenance_continuity_visible for evidence in result.audited_phase_list)


def test_v3_8_closeout_visibility_and_hidden_risk_counts_are_stable():
    result = audit_v3_8_closeout_and_v3_9_readiness()

    assert result.validation_totals["fail_visible_state_count"] == 37
    assert result.validation_totals["unsupported_visibility_count"] == 8
    assert result.validation_totals["prohibited_visibility_count"] == 8
    assert result.validation_totals["unknown_visibility_count"] == 8
    assert result.validation_totals["hidden_risk_count"] == 0
    assert result.deterministic_visibility_summary["non_ready_states_fail_visible"] is True
    assert any(evidence.unsupported_visibility for evidence in result.audited_phase_list)
    assert any(evidence.prohibited_visibility for evidence in result.audited_phase_list)
    assert any(evidence.unknown_visibility for evidence in result.audited_phase_list)


def test_v3_8_closeout_violation_counts_remain_zero():
    result = audit_v3_8_closeout_and_v3_9_readiness()

    assert result.validation_totals["recommendation_language_violation_count"] == 0
    assert result.validation_totals["optimization_language_violation_count"] == 0
    assert result.validation_totals["ranking_language_violation_count"] == 0
    assert result.validation_totals["scoring_behavior_violation_count"] == 0
    assert result.validation_totals["selection_behavior_violation_count"] == 0
    assert result.validation_totals["execution_boundary_violation_count"] == 0
    assert result.validation_totals["prohibited_behavior_violation_count"] == 0
    assert result.validation_totals["blocker_count"] == 0
    assert result.validation_totals["warning_count"] == 24


def test_v3_8_closeout_ready_only_when_required_evidence_exists():
    missing_phase = audit_v3_8_closeout_and_v3_9_readiness(
        V38CloseoutReadinessInput(omitted_phase_ids=("coordination_scenario_reasoning",))
    )
    missing_report = audit_v3_8_closeout_and_v3_9_readiness(
        V38CloseoutReadinessInput(
            omitted_report_paths=("docs/generated/v3_8_coordination_scenario_reasoning_report.json",)
        )
    )

    assert missing_phase.closeout_state == V3_8_CLOSEOUT_INCOMPLETE
    assert missing_phase.v3_9_readiness_state == V3_9_PLANNING_BLOCKED
    assert missing_phase.closeout_visibility_status == V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE
    assert missing_phase.validation_totals["non_ready_state_fail_visible"] is True
    assert any(blocker.startswith("missing_phase:") for blocker in missing_phase.blocker_list)

    assert missing_report.closeout_state == V3_8_CLOSEOUT_INCOMPLETE
    assert missing_report.v3_9_readiness_state == V3_9_PLANNING_BLOCKED
    assert missing_report.validation_totals["generated_report_count"] == EXPECTED_PHASE_COUNT - 1
    assert any(blocker.startswith("missing_generated_report:") for blocker in missing_report.blocker_list)


def test_v3_8_closeout_non_ready_states_remain_fail_visible():
    unsupported = audit_v3_8_closeout_and_v3_9_readiness(
        V38CloseoutReadinessInput(force_unsupported_state=True)
    )
    prohibited = audit_v3_8_closeout_and_v3_9_readiness(
        V38CloseoutReadinessInput(force_prohibited_state=True)
    )
    unknown = audit_v3_8_closeout_and_v3_9_readiness(
        V38CloseoutReadinessInput(force_unknown_state=True)
    )

    assert unsupported.closeout_state == V3_8_CLOSEOUT_UNSUPPORTED
    assert prohibited.closeout_state == V3_8_CLOSEOUT_PROHIBITED
    assert unknown.closeout_state == V3_8_CLOSEOUT_UNKNOWN
    for result in (unsupported, prohibited, unknown):
        assert result.v3_9_readiness_state == V3_9_PLANNING_BLOCKED
        assert result.closeout_visibility_status == V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE
        assert result.fail_visible is True
        assert result.hidden is False
        assert result.validation_totals["blocker_count"] >= 1


def test_v3_8_closeout_forced_prohibited_behavior_blocks_readiness():
    result = audit_v3_8_closeout_and_v3_9_readiness(
        V38CloseoutReadinessInput(
            force_recommendation_language_violation_count=1,
            force_execution_boundary_violation_count=1,
        )
    )

    assert result.closeout_state == V3_8_CLOSEOUT_PROHIBITED
    assert result.v3_9_readiness_state == V3_9_PLANNING_BLOCKED
    assert result.non_execution_confirmation is False
    assert result.prohibited_behavior_confirmation is False
    assert result.validation_totals["recommendation_language_violation_count"] == 1
    assert result.validation_totals["execution_boundary_violation_count"] == 1
    assert result.validation_totals["prohibited_behavior_violation_count"] == 2
    assert result.closeout_visibility_status == V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE


def test_v3_8_closeout_report_contains_required_totals_and_guidance():
    report = build_v3_8_closeout_and_v3_9_readiness_report()

    assert report["summary"]["closeout_state"] == V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING
    assert report["summary"]["v3_9_readiness_state"] == V3_9_PLANNING_READY
    assert report["summary"]["audited_phase_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["expected_phase_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["generated_report_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["migration_documentation_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["deterministic_evidence_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["replay_evidence_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["rollback_evidence_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["provenance_continuity_count"] == EXPECTED_PHASE_COUNT
    assert report["summary"]["fail_visible_state_count"] == 37
    assert report["summary"]["unsupported_visibility_count"] == 8
    assert report["summary"]["prohibited_visibility_count"] == 8
    assert report["summary"]["unknown_visibility_count"] == 8
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["recommendation_language_violation_count"] == 0
    assert report["summary"]["optimization_language_violation_count"] == 0
    assert report["summary"]["ranking_language_violation_count"] == 0
    assert report["summary"]["scoring_behavior_violation_count"] == 0
    assert report["summary"]["selection_behavior_violation_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["blocker_count"] == 0
    assert report["summary"]["warning_count"] == 24
    assert report["summary"]["non_execution_confirmation"] is True
    assert report["summary"]["prohibited_behavior_confirmation"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["v3_9_planning_guidance"]["non_executable_until_later_decision"] is True
