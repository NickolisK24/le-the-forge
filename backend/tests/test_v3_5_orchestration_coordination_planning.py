from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    COORDINATION_BLOCKED_BY_DEPENDENCY,
    COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    COORDINATION_BLOCKED_BY_LINEAGE_GAP,
    COORDINATION_INCOMPATIBLE,
    COORDINATION_PROHIBITED,
    COORDINATION_READY_FOR_PLANNING,
    COORDINATION_REQUIRES_MANUAL_REVIEW,
    COORDINATION_UNSUPPORTED,
    default_orchestration_coordination_graph,
    default_orchestration_coordination_planning_input,
    export_orchestration_coordination_planning_result,
    hash_coordination_graph,
    hash_coordination_planning_result,
    plan_orchestration_coordination,
    serialize_orchestration_coordination_planning_result,
)
from scripts.report_v3_5_orchestration_coordination_planning import (
    build_v3_5_orchestration_coordination_planning_report,
)


def _base_input():
    return default_orchestration_coordination_planning_input()


def _base_graph():
    return default_orchestration_coordination_graph()


def _result(source=None):
    return plan_orchestration_coordination(source or _base_input())


def _export(source=None):
    return export_orchestration_coordination_planning_result(_result(source))


def test_deterministic_coordination_classification():
    first = _export()
    second = _export()

    assert first["coordination_status"] == COORDINATION_READY_FOR_PLANNING
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    assert serialize_orchestration_coordination_planning_result(_result()) == serialize_orchestration_coordination_planning_result(_result())


def test_stable_deterministic_hash_output():
    assert hash_coordination_planning_result(_result()) == hash_coordination_planning_result(_result())


def test_coordination_graph_stability():
    assert hash_coordination_graph(_base_graph()) == hash_coordination_graph(_base_graph())
    assert _export()["coordination_graph_id"] == "coordination-graph-v3-5-phase-4"


def test_dependency_chain_stability():
    chains = _export()["dependency_chains"]

    assert chains == sorted(chains)
    assert "coordination-node-governance-consumption->coordination-node-readiness-evaluation:v3_5_governance_consumption_contract:source_before_target" in chains


def test_blocker_propagation_stability():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(graph, nodes=(replace(graph.nodes[0], blocker_reasons=("dependency_chain_blocker",)), graph.nodes[1], graph.nodes[2])),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_BLOCKED_BY_DEPENDENCY
    assert result["propagated_blockers"] == ["dependency_chain_blocker"]


def test_unsupported_state_propagation_visibility():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(graph, nodes=(replace(graph.nodes[0], unsupported_reasons=("unsupported_coordination_scope",)), graph.nodes[1], graph.nodes[2])),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_UNSUPPORTED
    assert result["propagated_unsupported_states"] == ["unsupported_coordination_scope"]


def test_prohibited_state_propagation_visibility():
    source = replace(
        _base_input(),
        graph=replace(_base_graph(), coordination_scope_ids=("runtime_execution", "coordination-scope-readiness-evaluation")),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_PROHIBITED
    assert result["propagated_prohibited_states"] == ["runtime_execution"]


def test_manual_review_propagation_visibility():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(graph, nodes=(replace(graph.nodes[0], manual_review_reasons=("coordination_owner_review_required",)), graph.nodes[1], graph.nodes[2])),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_REQUIRES_MANUAL_REVIEW
    assert result["propagated_manual_review_states"] == ["coordination_owner_review_required"]


def test_compatibility_propagation_visibility():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(graph, nodes=(replace(graph.nodes[0], compatibility_references=()), graph.nodes[1], graph.nodes[2])),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_INCOMPATIBLE
    assert result["propagated_compatibility_failures"] == ["compatibility_lineage_missing"]


def test_environment_propagation_visibility():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(graph, nodes=(replace(graph.nodes[0], environment_references=()), graph.nodes[1], graph.nodes[2])),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH
    assert result["propagated_environment_mismatches"] == ["environment_reference_missing"]


def test_lineage_aggregation_visibility():
    source = replace(_base_input(), graph=replace(_base_graph(), replay_lineage_aggregation=(), rollback_lineage_aggregation=()))
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_BLOCKED_BY_LINEAGE_GAP
    assert result["propagated_lineage_gaps"] == ["replay_lineage_aggregation", "rollback_lineage_aggregation"]


def test_multi_scope_coordination_aggregation():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(
            graph,
            nodes=(
                replace(graph.nodes[0], dependency_references=("v3_5_governance_consumption_contract", "v3_4_closeout_and_v3_5_readiness")),
                graph.nodes[1],
                graph.nodes[2],
            ),
        ),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_READY_FOR_PLANNING
    assert len(result["coordination_scopes"]) == 3
    assert len(result["coordination_nodes"]) == 3
    assert len(result["coordination_edges"]) == 2


def test_cross_scope_lineage_aggregation_visibility():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(
            graph,
            upstream_coordination_scopes=("coordination-scope-governance-consumption", "coordination-scope-readiness-evaluation"),
            downstream_coordination_scopes=("coordination-scope-dependency-resolution", "coordination-scope-phase-4-coordination"),
            governance_lineage_aggregation=(
                "v3_5_governance_consumption_contract",
                "v3_5_orchestration_readiness_evaluation",
                "v3_5_governance_dependency_resolution",
                "v3_5_orchestration_coordination_planning",
            ),
        ),
    )
    lineage = _export(source)["lineage_aggregation"]

    assert lineage["upstream_coordination_scopes"] == [
        "coordination-scope-governance-consumption",
        "coordination-scope-readiness-evaluation",
    ]
    assert lineage["downstream_coordination_scopes"] == [
        "coordination-scope-dependency-resolution",
        "coordination-scope-phase-4-coordination",
    ]
    assert lineage["non_executable"] is True
    assert lineage["graph_traversal_execution_enabled"] is False


def test_multiple_simultaneous_propagated_blockers():
    graph = _base_graph()
    source = replace(
        _base_input(),
        graph=replace(
            graph,
            replay_lineage_aggregation=(),
            rollback_lineage_aggregation=(),
            coordination_scope_ids=("runtime_execution", "coordination-scope-readiness-evaluation"),
            nodes=(
                replace(
                    graph.nodes[0],
                    blocker_reasons=("dependency_chain_blocker",),
                    unsupported_reasons=("unsupported_coordination_scope",),
                    manual_review_reasons=("coordination_owner_review_required",),
                    compatibility_references=(),
                    environment_references=(),
                ),
                graph.nodes[1],
                graph.nodes[2],
            ),
        ),
    )
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_PROHIBITED
    assert result["propagated_blockers"]
    assert result["propagated_unsupported_states"]
    assert result["propagated_prohibited_states"]
    assert result["propagated_manual_review_states"]
    assert result["propagated_lineage_gaps"]
    assert result["propagated_compatibility_failures"]
    assert result["propagated_environment_mismatches"]


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["audit_log_writing_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["scheduling_behavior_enabled"] is False
    assert result["orchestration_dispatch_enabled"] is False


def test_prohibited_behavior_is_not_exposed():
    source = replace(_base_input(), graph=replace(_base_graph(), graph_execution_enabled=True, orchestration_dispatch_enabled=True))
    result = _export(source)

    assert result["coordination_status"] == COORDINATION_PROHIBITED
    assert result["graph_execution_enabled"] is False
    assert result["orchestration_dispatch_enabled"] is False
    assert any(
        row["blocker_id"] == "prohibited:execution_routing_mutation_graph_scheduling_or_dispatch_behavior_detected"
        for row in result["blockers"]
    )


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_orchestration_coordination_planning_report()
    second = build_v3_5_orchestration_coordination_planning_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_coordination_planning_status"] == COORDINATION_READY_FOR_PLANNING
    assert distribution[COORDINATION_READY_FOR_PLANNING] == 3
    assert distribution[COORDINATION_BLOCKED_BY_DEPENDENCY] == 1
    assert distribution[COORDINATION_UNSUPPORTED] == 1
    assert distribution[COORDINATION_PROHIBITED] == 2
    assert distribution[COORDINATION_BLOCKED_BY_LINEAGE_GAP] == 1
    assert distribution[COORDINATION_INCOMPATIBLE] == 1
    assert distribution[COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH] == 1
    assert distribution[COORDINATION_REQUIRES_MANUAL_REVIEW] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_orchestration_coordination_planning_report()["explicit_non_execution_guarantees"]

    assert guarantees["runtime_execution_enabled"] is False
    assert guarantees["orchestration_execution_enabled"] is False
    assert guarantees["routing_behavior_enabled"] is False
    assert guarantees["mutation_behavior_enabled"] is False
    assert guarantees["audit_log_writing_enabled"] is False
    assert guarantees["production_consumption_enabled"] is False
    assert guarantees["graph_execution_enabled"] is False
    assert guarantees["scheduling_behavior_enabled"] is False
    assert guarantees["orchestration_dispatch_enabled"] is False
