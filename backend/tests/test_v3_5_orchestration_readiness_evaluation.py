from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    BLOCKED_BY_AUTHORIZATION_FAILURE,
    BLOCKED_BY_COMPATIBILITY_FAILURE,
    BLOCKED_BY_ENVIRONMENT_FAILURE,
    BLOCKED_BY_GOVERNANCE_DEPENDENCY,
    BLOCKED_BY_REPLAY_LINEAGE_GAP,
    BLOCKED_BY_ROLLBACK_LINEAGE_GAP,
    MANUAL_REVIEW_REQUIRED,
    PROHIBITED_ORCHESTRATION_REQUEST,
    READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
    UNSUPPORTED_ORCHESTRATION_REQUEST,
    default_governance_consumption_contract,
    default_orchestration_readiness_evaluation_input,
    evaluate_orchestration_readiness,
    export_orchestration_readiness_result,
    hash_readiness_result,
    serialize_orchestration_readiness_result,
)
from scripts.report_v3_5_orchestration_readiness_evaluation import (
    build_v3_5_orchestration_readiness_evaluation_report,
)


def _base_input():
    return default_orchestration_readiness_evaluation_input()


def _base_contract():
    return default_governance_consumption_contract()


def _result(source=None):
    return evaluate_orchestration_readiness(source or _base_input())


def _export(source=None):
    return export_orchestration_readiness_result(_result(source))


def test_deterministic_readiness_classification():
    first = _export()
    second = _export()

    assert first["readiness_status"] == READY_FOR_FUTURE_ORCHESTRATION_PLANNING
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["planning_ready"] is True


def test_stable_serialization():
    first = _result()
    second = _result()

    assert serialize_orchestration_readiness_result(first) == serialize_orchestration_readiness_result(second)


def test_stable_deterministic_hash_output():
    first = _result()
    second = _result()

    assert hash_readiness_result(first) == hash_readiness_result(second)


def test_blocker_ordering_stability():
    source = replace(
        _base_input(),
        contract=replace(
            _base_contract(),
            authorization_state="missing",
            governance_dependency_ids=(),
            replay_lineage_id="",
            rollback_lineage_id="",
        ),
    )
    first = _export(source)["blockers"]
    second = _export(source)["blockers"]

    assert [row["blocker_id"] for row in first] == [row["blocker_id"] for row in second]
    assert [row["deterministic_rank"] for row in first] == sorted(row["deterministic_rank"] for row in first)


def test_unsupported_state_preservation():
    source = replace(
        _base_input(),
        contract=replace(_base_contract(), unsupported_orchestration_states=("unsupported_orchestration_scope",)),
    )
    result = _export(source)

    assert result["readiness_status"] == UNSUPPORTED_ORCHESTRATION_REQUEST
    assert result["unsupported_states"] == ["unsupported_orchestration_scope"]


def test_prohibited_domain_preservation():
    source = replace(_base_input(), contract=replace(_base_contract(), requested_orchestration_domain="runtime_execution"))
    result = _export(source)

    assert result["readiness_status"] == PROHIBITED_ORCHESTRATION_REQUEST
    assert result["prohibited_domains"] == ["runtime_execution"]


def test_manual_review_preservation():
    source = replace(
        _base_input(),
        manual_review_required=True,
        manual_review_reasons=("governance_review_required",),
    )
    result = _export(source)

    assert result["readiness_status"] == MANUAL_REVIEW_REQUIRED
    assert result["manual_review_reasons"] == ["governance_review_required"]


def test_missing_dependency_preservation():
    contract = _base_contract()
    source = replace(_base_input(), contract=replace(contract, governance_dependency_ids=contract.governance_dependency_ids[:-1]))
    result = _export(source)

    assert result["readiness_status"] == BLOCKED_BY_GOVERNANCE_DEPENDENCY
    assert result["missing_governance_dependencies"] == ["v3_4_closeout_and_v3_5_readiness"]


def test_replay_lineage_gap_preservation():
    source = replace(_base_input(), contract=replace(_base_contract(), replay_lineage_id=""))
    result = _export(source)

    assert result["readiness_status"] == BLOCKED_BY_REPLAY_LINEAGE_GAP
    assert result["missing_replay_requirements"] == ["replay_lineage_id"]


def test_rollback_lineage_gap_preservation():
    source = replace(_base_input(), contract=replace(_base_contract(), rollback_lineage_id=""))
    result = _export(source)

    assert result["readiness_status"] == BLOCKED_BY_ROLLBACK_LINEAGE_GAP
    assert result["missing_rollback_requirements"] == ["rollback_lineage_id"]


def test_authorization_failure_visibility():
    source = replace(_base_input(), contract=replace(_base_contract(), authorization_state="missing"))
    result = _export(source)

    assert result["readiness_status"] == BLOCKED_BY_AUTHORIZATION_FAILURE
    assert result["blockers"][0]["blocker_id"] == "authorization_not_satisfied"


def test_compatibility_failure_visibility():
    source = replace(_base_input(), contract=replace(_base_contract(), compatibility_verified=False))
    result = _export(source)

    assert result["readiness_status"] == BLOCKED_BY_COMPATIBILITY_FAILURE
    assert result["compatibility_failures"] == ["compatibility_not_verified"]


def test_environment_failure_visibility():
    source = replace(_base_input(), contract=replace(_base_contract(), environment="production", environment_isolated=False))
    result = _export(source)

    assert result["readiness_status"] == BLOCKED_BY_ENVIRONMENT_FAILURE
    assert "environment_mismatch" in result["environment_failures"]
    assert "non_production_environment_required" in result["environment_failures"]


def test_multiple_blocker_aggregation():
    source = replace(
        _base_input(),
        contract=replace(
            _base_contract(),
            governance_dependency_ids=(),
            authorization_state="missing",
            replay_lineage_id="",
            rollback_lineage_id="",
            compatibility_verified=False,
            environment="production",
            requested_orchestration_domain="runtime_execution",
        ),
    )
    result = _export(source)

    assert result["readiness_status"] == PROHIBITED_ORCHESTRATION_REQUEST
    assert len(result["blockers"]) >= 7
    assert result["missing_governance_dependencies"]
    assert result["missing_replay_requirements"]
    assert result["missing_rollback_requirements"]
    assert result["compatibility_failures"]
    assert result["environment_failures"]
    assert result["prohibited_domains"] == ["runtime_execution"]


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["audit_log_writing_enabled"] is False
    assert result["production_consumption_enabled"] is False


def test_prohibited_behavior_is_not_exposed():
    source = replace(_base_input(), contract=replace(_base_contract(), orchestration_execution_enabled=True))
    result = _export(source)

    assert result["readiness_status"] == PROHIBITED_ORCHESTRATION_REQUEST
    assert result["orchestration_execution_enabled"] is False
    assert any(row["blocker_id"] == "prohibited_execution_or_consumption_behavior_detected" for row in result["blockers"])


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_orchestration_readiness_evaluation_report()
    second = build_v3_5_orchestration_readiness_evaluation_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_readiness_status"] == READY_FOR_FUTURE_ORCHESTRATION_PLANNING
    assert distribution[READY_FOR_FUTURE_ORCHESTRATION_PLANNING] == 1
    assert distribution[BLOCKED_BY_GOVERNANCE_DEPENDENCY] == 1
    assert distribution[BLOCKED_BY_AUTHORIZATION_FAILURE] == 1
    assert distribution[BLOCKED_BY_REPLAY_LINEAGE_GAP] == 1
    assert distribution[BLOCKED_BY_ROLLBACK_LINEAGE_GAP] == 1
    assert distribution[UNSUPPORTED_ORCHESTRATION_REQUEST] == 1
    assert distribution[PROHIBITED_ORCHESTRATION_REQUEST] == 2
    assert distribution[BLOCKED_BY_COMPATIBILITY_FAILURE] == 1
    assert distribution[BLOCKED_BY_ENVIRONMENT_FAILURE] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_orchestration_readiness_evaluation_report()["explicit_non_execution_guarantees"]

    assert guarantees["runtime_execution_enabled"] is False
    assert guarantees["orchestration_execution_enabled"] is False
    assert guarantees["routing_behavior_enabled"] is False
    assert guarantees["mutation_behavior_enabled"] is False
    assert guarantees["audit_log_writing_enabled"] is False
    assert guarantees["production_consumption_enabled"] is False
    assert guarantees["default_runtime_manifest_consumption_enabled"] is False
    assert guarantees["production_authoritative_manifest_treatment_enabled"] is False
