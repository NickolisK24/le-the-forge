from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE,
    VISIBILITY_BLOCKED_BY_COORDINATION,
    VISIBILITY_BLOCKED_BY_DEPENDENCY,
    VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    VISIBILITY_BLOCKED_BY_LINEAGE_GAP,
    VISIBILITY_BLOCKED_BY_READINESS,
    VISIBILITY_PROHIBITED,
    VISIBILITY_READY_FOR_PLANNING,
    VISIBILITY_REQUIRES_MANUAL_REVIEW,
    VISIBILITY_UNSUPPORTED,
    aggregate_orchestration_visibility,
    default_governance_dependency_contract,
    default_governance_dependency_resolution_input,
    default_governance_consumption_contract,
    default_orchestration_coordination_graph,
    default_orchestration_coordination_planning_input,
    default_orchestration_readiness_evaluation_input,
    default_orchestration_visibility_aggregation_input,
    evaluate_orchestration_readiness,
    export_orchestration_visibility_aggregation_result,
    hash_visibility_aggregation_result,
    plan_orchestration_coordination,
    resolve_governance_dependency,
    serialize_orchestration_visibility_aggregation_result,
)
from scripts.report_v3_5_orchestration_visibility_aggregation import (
    build_v3_5_orchestration_visibility_aggregation_report,
)


def _base_input():
    return default_orchestration_visibility_aggregation_input()


def _result(source=None):
    return aggregate_orchestration_visibility(source or _base_input())


def _export(source=None):
    return export_orchestration_visibility_aggregation_result(_result(source))


def _readiness_with(**changes):
    contract = replace(default_governance_consumption_contract(), **changes)
    return evaluate_orchestration_readiness(
        replace(default_orchestration_readiness_evaluation_input(), contract=contract)
    )


def _dependency_with(**changes):
    contract = replace(default_governance_dependency_contract(), **changes)
    return resolve_governance_dependency(
        replace(default_governance_dependency_resolution_input(), contract=contract)
    )


def _coordination_with_node(**node_changes):
    graph = default_orchestration_coordination_graph()
    return plan_orchestration_coordination(
        replace(
            default_orchestration_coordination_planning_input(),
            graph=replace(graph, nodes=(replace(graph.nodes[0], **node_changes), graph.nodes[1], graph.nodes[2])),
        )
    )


def test_deterministic_visibility_classification():
    first = _export()
    second = _export()

    assert first["aggregate_visibility_status"] == VISIBILITY_READY_FOR_PLANNING
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    assert serialize_orchestration_visibility_aggregation_result(_result()) == serialize_orchestration_visibility_aggregation_result(_result())


def test_stable_deterministic_hash_output():
    assert hash_visibility_aggregation_result(_result()) == hash_visibility_aggregation_result(_result())


def test_priority_order_status_selection():
    source = replace(
        _base_input(),
        readiness_result=_readiness_with(unsupported_orchestration_states=("unsupported_visibility_state",)),
        dependency_result=_dependency_with(blocker_reasons=("dependency_visibility_blocker",)),
        coordination_result=plan_orchestration_coordination(
            replace(
                default_orchestration_coordination_planning_input(),
                graph=replace(
                    default_orchestration_coordination_graph(),
                    coordination_scope_ids=("runtime_execution", "coordination-scope-readiness-evaluation"),
                ),
            )
        ),
    )
    result = _export(source)

    assert result["aggregate_visibility_status"] == VISIBILITY_PROHIBITED
    assert result["unsupported_state_summary"]
    assert result["blocker_summary"]
    assert result["prohibited_state_summary"] == ["runtime_execution"]


def test_readiness_blocker_aggregation():
    result = _export(replace(_base_input(), readiness_result=_readiness_with(authorization_state="missing")))

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_READINESS
    assert "authorization_not_satisfied" in result["blocker_summary"]


def test_dependency_blocker_aggregation():
    result = _export(replace(_base_input(), dependency_result=_dependency_with(blocker_reasons=("dependency_visibility_blocker",))))

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_DEPENDENCY
    assert "blocked:dependency_visibility_blocker" in result["blocker_summary"]


def test_coordination_blocker_aggregation():
    result = _export(
        replace(
            _base_input(),
            coordination_result=_coordination_with_node(blocker_reasons=("coordination_visibility_blocker",)),
        )
    )

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_COORDINATION
    assert "dependency_blocker:coordination_visibility_blocker" in result["blocker_summary"]


def test_unsupported_state_aggregation():
    result = _export(
        replace(
            _base_input(),
            readiness_result=_readiness_with(unsupported_orchestration_states=("unsupported_visibility_state",)),
            dependency_result=_dependency_with(blocker_reasons=("dependency_visibility_blocker",)),
        )
    )

    assert result["aggregate_visibility_status"] == VISIBILITY_UNSUPPORTED
    assert result["unsupported_state_summary"] == ["unsupported_visibility_state"]


def test_prohibited_state_aggregation():
    result = _export(replace(_base_input(), readiness_result=_readiness_with(requested_orchestration_domain="runtime_execution")))

    assert result["aggregate_visibility_status"] == VISIBILITY_PROHIBITED
    assert result["prohibited_state_summary"] == ["runtime_execution"]


def test_lineage_gap_aggregation():
    contract = default_governance_dependency_contract()
    result = _export(
        replace(
            _base_input(),
            dependency_result=resolve_governance_dependency(
                replace(
                    default_governance_dependency_resolution_input(),
                    contract=replace(
                        contract,
                        lineage=replace(contract.lineage, replay_lineage_references=(), rollback_lineage_references=()),
                    ),
                )
            ),
        )
    )

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_DEPENDENCY
    assert result["lineage_gap_summary"] == ["replay_lineage_references", "rollback_lineage_references"]


def test_compatibility_failure_aggregation():
    result = _export(replace(_base_input(), readiness_result=_readiness_with(compatibility_verified=False)))

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_READINESS
    assert result["compatibility_failure_summary"] == ["compatibility_not_verified"]


def test_environment_mismatch_aggregation():
    result = _export(replace(_base_input(), readiness_result=_readiness_with(environment="production", environment_isolated=False)))

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_READINESS
    assert "environment_mismatch" in result["environment_mismatch_summary"]
    assert "non_production_environment_required" in result["environment_mismatch_summary"]


def test_manual_review_aggregation():
    result = _export(replace(_base_input(), coordination_result=_coordination_with_node(manual_review_reasons=("visibility_manual_review_required",))))

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_COORDINATION
    assert result["manual_review_summary"] == ["visibility_manual_review_required"]


def test_direct_lineage_status_when_no_source_status_blocker():
    source = replace(
        _base_input(),
        readiness_result=replace(_base_input().readiness_result, missing_replay_requirements=("manual_lineage_gap",)),
    )
    result = _export(source)

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_LINEAGE_GAP
    assert result["lineage_gap_summary"] == ["manual_lineage_gap"]


def test_direct_compatibility_status_when_no_source_status_blocker():
    source = replace(
        _base_input(),
        dependency_result=replace(_base_input().dependency_result, compatibility_failures=("manual_compatibility_failure",)),
    )
    result = _export(source)

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE
    assert result["compatibility_failure_summary"] == ["manual_compatibility_failure"]


def test_direct_environment_status_when_no_source_status_blocker():
    source = replace(
        _base_input(),
        coordination_result=replace(_base_input().coordination_result, propagated_environment_mismatches=("manual_environment_mismatch",)),
    )
    result = _export(source)

    assert result["aggregate_visibility_status"] == VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH
    assert result["environment_mismatch_summary"] == ["manual_environment_mismatch"]


def test_direct_manual_review_status_when_no_source_status_blocker():
    source = replace(
        _base_input(),
        readiness_result=replace(_base_input().readiness_result, manual_review_reasons=("manual_visibility_review",)),
    )
    result = _export(source)

    assert result["aggregate_visibility_status"] == VISIBILITY_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_summary"] == ["manual_visibility_review"]


def test_limitation_visibility_preservation():
    result = _export()

    assert "visibility aggregation is declarative and planning-only" in result["limitation_summary"]
    assert "readiness classification is planning-only" in result["limitation_summary"]
    assert "dependency resolution is declarative and non-fetching" in result["limitation_summary"]
    assert "coordination planning graphs are non-executable" in result["limitation_summary"]


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["audit_log_writing_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["graph_traversal_behavior_enabled"] is False
    assert result["scheduling_behavior_enabled"] is False
    assert result["orchestration_dispatch_enabled"] is False
    assert result["auto_approval_behavior_enabled"] is False


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_orchestration_visibility_aggregation_report()
    second = build_v3_5_orchestration_visibility_aggregation_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_visibility_aggregation_status"] == VISIBILITY_READY_FOR_PLANNING
    assert distribution[VISIBILITY_READY_FOR_PLANNING] == 1
    assert distribution[VISIBILITY_BLOCKED_BY_READINESS] == 1
    assert distribution[VISIBILITY_BLOCKED_BY_DEPENDENCY] == 1
    assert distribution[VISIBILITY_BLOCKED_BY_COORDINATION] == 1
    assert distribution[VISIBILITY_BLOCKED_BY_LINEAGE_GAP] == 1
    assert distribution[VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE] == 1
    assert distribution[VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH] == 1
    assert distribution[VISIBILITY_REQUIRES_MANUAL_REVIEW] == 1
    assert distribution[VISIBILITY_UNSUPPORTED] == 1
    assert distribution[VISIBILITY_PROHIBITED] == 2


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_orchestration_visibility_aggregation_report()["explicit_non_execution_guarantees"]

    assert guarantees["runtime_execution_enabled"] is False
    assert guarantees["orchestration_execution_enabled"] is False
    assert guarantees["routing_behavior_enabled"] is False
    assert guarantees["mutation_behavior_enabled"] is False
    assert guarantees["audit_log_writing_enabled"] is False
    assert guarantees["production_consumption_enabled"] is False
    assert guarantees["graph_execution_enabled"] is False
    assert guarantees["graph_traversal_behavior_enabled"] is False
    assert guarantees["scheduling_behavior_enabled"] is False
    assert guarantees["orchestration_dispatch_enabled"] is False
    assert guarantees["auto_approval_behavior_enabled"] is False
