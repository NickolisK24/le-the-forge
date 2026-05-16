"""Planning-only orchestration coordination planning contracts for v3.5 Phase 4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .orchestration_coordination_models import (
    OrchestrationCoordinationGraph,
    default_orchestration_coordination_graph,
)
from .orchestration_coordination_report_models import (
    OrchestrationCoordinationBlocker,
    OrchestrationCoordinationPlanningResult,
    export_coordination_planning_result,
    serialize_coordination_planning_result,
)
from .orchestration_coordination_status import (
    COORDINATION_BLOCKED_BY_DEPENDENCY,
    COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    COORDINATION_BLOCKED_BY_GOVERNANCE,
    COORDINATION_BLOCKED_BY_LINEAGE_GAP,
    COORDINATION_INCOMPATIBLE,
    COORDINATION_PROHIBITED,
    COORDINATION_READY_FOR_PLANNING,
    COORDINATION_REQUIRES_MANUAL_REVIEW,
    COORDINATION_UNSUPPORTED,
    classify_coordination_status,
)


@dataclass(frozen=True)
class OrchestrationCoordinationPlanningInput:
    graph: OrchestrationCoordinationGraph
    prohibited_coordination_scopes: tuple[str, ...]
    required_lineage_categories: tuple[str, ...]


def default_orchestration_coordination_planning_input() -> OrchestrationCoordinationPlanningInput:
    return OrchestrationCoordinationPlanningInput(
        graph=default_orchestration_coordination_graph(),
        prohibited_coordination_scopes=(
            "runtime_execution",
            "orchestration_execution",
            "production_routing",
            "state_write",
            "audit_log_write",
            "graph_execution",
            "orchestration_scheduling",
            "orchestration_dispatch",
        ),
        required_lineage_categories=("replay", "rollback", "governance", "compatibility", "environment"),
    )


def plan_orchestration_coordination(
    planning_input: OrchestrationCoordinationPlanningInput | None = None,
) -> OrchestrationCoordinationPlanningResult:
    source = planning_input or default_orchestration_coordination_planning_input()
    graph = source.graph
    blockers: list[OrchestrationCoordinationBlocker] = []
    candidate_statuses: list[str] = []

    dependency_chains = _dependency_chains(graph)
    propagated_blockers = _propagated_reasons(graph, "blocker_reasons")
    propagated_unsupported = _propagated_reasons(graph, "unsupported_reasons")
    propagated_prohibited = _propagated_prohibited_states(source)
    propagated_manual_review = _propagated_reasons(graph, "manual_review_reasons")
    propagated_lineage_gaps = _lineage_gaps(source)
    propagated_compatibility_failures = _compatibility_failures(graph)
    propagated_environment_mismatches = _environment_mismatches(graph)

    if not graph.coordination_scope_id or not graph.coordination_planning_graph_id:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_BLOCKED_BY_GOVERNANCE,
            "coordination_graph_identity_missing",
            "governance",
            10,
            "coordination scope and planning graph identity must be explicit",
        )
    for reason in propagated_prohibited:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_PROHIBITED,
            f"prohibited:{reason}",
            "prohibited",
            5,
            "prohibited coordination state must not be downgraded",
        )
    for reason in propagated_blockers:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_BLOCKED_BY_DEPENDENCY,
            f"dependency_blocker:{reason}",
            "dependency",
            20,
            "coordination dependency blocker must remain fail-visible",
        )
    if _governance_gap_detected(graph):
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_BLOCKED_BY_GOVERNANCE,
            "governance_lineage_missing",
            "governance",
            30,
            "governance lineage aggregation must be explicit",
        )
    for gap in propagated_lineage_gaps:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_BLOCKED_BY_LINEAGE_GAP,
            f"lineage_gap:{gap}",
            "lineage",
            40,
            "coordination lineage gap must remain explicit",
        )
    for mismatch in propagated_environment_mismatches:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH,
            f"environment_mismatch:{mismatch}",
            "environment",
            50,
            "environment propagation must preserve non-production isolation",
        )
    for failure in propagated_compatibility_failures:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_INCOMPATIBLE,
            f"compatibility_failure:{failure}",
            "compatibility",
            60,
            "compatibility propagation failure must remain visible",
        )
    for reason in propagated_unsupported:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_UNSUPPORTED,
            f"unsupported:{reason}",
            "unsupported",
            70,
            "unsupported coordination state must remain explicit",
        )
    for reason in propagated_manual_review:
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_REQUIRES_MANUAL_REVIEW,
            f"manual_review:{reason}",
            "manual_review",
            80,
            "manual review propagation must remain explicit",
        )
    if _prohibited_behavior_detected(graph):
        _add_blocker(
            blockers,
            candidate_statuses,
            COORDINATION_PROHIBITED,
            "prohibited:execution_routing_mutation_graph_scheduling_or_dispatch_behavior_detected",
            "prohibited_behavior",
            6,
            "execution, graph execution, scheduling, dispatch, routing, mutation, writing, and production consumption are prohibited",
        )

    status = classify_coordination_status(candidate_statuses)
    return OrchestrationCoordinationPlanningResult(
        coordination_graph_id=graph.coordination_planning_graph_id,
        coordination_status=status,
        planning_only=True,
        coordination_scopes=tuple(sorted(graph.coordination_scope_ids)),
        coordination_nodes=tuple(sorted(node.node_id for node in graph.nodes)),
        coordination_edges=tuple(sorted(edge.edge_id for edge in graph.edges)),
        propagated_blockers=propagated_blockers,
        propagated_unsupported_states=propagated_unsupported,
        propagated_prohibited_states=propagated_prohibited,
        propagated_manual_review_states=propagated_manual_review,
        propagated_lineage_gaps=propagated_lineage_gaps,
        propagated_compatibility_failures=propagated_compatibility_failures,
        propagated_environment_mismatches=propagated_environment_mismatches,
        dependency_chains=dependency_chains,
        lineage_aggregation=_lineage_aggregation(graph),
        visibility_aggregation=_visibility_aggregation(
            propagated_blockers,
            propagated_unsupported,
            propagated_prohibited,
            propagated_manual_review,
        ),
        blockers=tuple(blockers),
        deterministic_explanation_summary=_explanation_summary(status, blockers),
        runtime_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_behavior_enabled=False,
        mutation_behavior_enabled=False,
        audit_log_writing_enabled=False,
        production_consumption_enabled=False,
        graph_execution_enabled=False,
        scheduling_behavior_enabled=False,
        orchestration_dispatch_enabled=False,
        graph=graph,
    )


def export_orchestration_coordination_planning_result(
    result: OrchestrationCoordinationPlanningResult,
) -> dict[str, Any]:
    return export_coordination_planning_result(result)


def serialize_orchestration_coordination_planning_result(
    result: OrchestrationCoordinationPlanningResult,
) -> str:
    return serialize_coordination_planning_result(result)


def hash_orchestration_coordination_planning_input(source: OrchestrationCoordinationPlanningInput) -> str:
    return deterministic_hash(
        {
            "graph": source.graph,
            "prohibited_coordination_scopes": source.prohibited_coordination_scopes,
            "required_lineage_categories": source.required_lineage_categories,
        }
    )


def _dependency_chains(graph: OrchestrationCoordinationGraph) -> tuple[str, ...]:
    return tuple(
        sorted(
            f"{edge.source_node_id}->{edge.target_node_id}:{edge.dependency_reference}:{edge.sequencing_rule}"
            for edge in graph.edges
        )
    )


def _propagated_reasons(graph: OrchestrationCoordinationGraph, field: str) -> tuple[str, ...]:
    values: set[str] = set()
    for node in graph.nodes:
        values.update(getattr(node, field))
    return tuple(sorted(values))


def _propagated_prohibited_states(source: OrchestrationCoordinationPlanningInput) -> tuple[str, ...]:
    values = set(_propagated_reasons(source.graph, "prohibited_reasons"))
    values.update(scope for scope in source.graph.coordination_scope_ids if scope in source.prohibited_coordination_scopes)
    return tuple(sorted(values))


def _lineage_gaps(source: OrchestrationCoordinationPlanningInput) -> tuple[str, ...]:
    graph = source.graph
    gaps: list[str] = []
    if "replay" in source.required_lineage_categories and not graph.replay_lineage_aggregation:
        gaps.append("replay_lineage_aggregation")
    if "rollback" in source.required_lineage_categories and not graph.rollback_lineage_aggregation:
        gaps.append("rollback_lineage_aggregation")
    if "governance" in source.required_lineage_categories and not graph.governance_lineage_aggregation:
        gaps.append("governance_lineage_aggregation")
    if "compatibility" in source.required_lineage_categories and not graph.compatibility_lineage_aggregation:
        gaps.append("compatibility_lineage_aggregation")
    if "environment" in source.required_lineage_categories and not graph.environment_lineage_aggregation:
        gaps.append("environment_lineage_aggregation")
    return tuple(sorted(gaps))


def _compatibility_failures(graph: OrchestrationCoordinationGraph) -> tuple[str, ...]:
    failures = {
        "compatibility_lineage_missing"
        for node in graph.nodes
        if not node.compatibility_references
    }
    if not graph.compatibility_lineage_aggregation:
        failures.add("compatibility_aggregation_missing")
    return tuple(sorted(failures))


def _environment_mismatches(graph: OrchestrationCoordinationGraph) -> tuple[str, ...]:
    mismatches = {
        "environment_reference_missing"
        for node in graph.nodes
        if not node.environment_references
    }
    if not graph.environment_lineage_aggregation:
        mismatches.add("environment_aggregation_missing")
    return tuple(sorted(mismatches))


def _governance_gap_detected(graph: OrchestrationCoordinationGraph) -> bool:
    return not graph.nodes or not graph.edges or not graph.governance_lineage_aggregation


def _lineage_aggregation(graph: OrchestrationCoordinationGraph) -> dict[str, Any]:
    return {
        "upstream_coordination_scopes": sorted(graph.upstream_coordination_scopes),
        "downstream_coordination_scopes": sorted(graph.downstream_coordination_scopes),
        "replay_lineage_aggregation": sorted(graph.replay_lineage_aggregation),
        "rollback_lineage_aggregation": sorted(graph.rollback_lineage_aggregation),
        "governance_lineage_aggregation": sorted(graph.governance_lineage_aggregation),
        "compatibility_lineage_aggregation": sorted(graph.compatibility_lineage_aggregation),
        "environment_lineage_aggregation": sorted(graph.environment_lineage_aggregation),
        "non_executable": True,
        "graph_traversal_execution_enabled": False,
        "automatic_resolution_enabled": False,
    }


def _visibility_aggregation(
    blockers: tuple[str, ...],
    unsupported: tuple[str, ...],
    prohibited: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "blocker_visibility_count": len(blockers),
        "unsupported_visibility_count": len(unsupported),
        "prohibited_visibility_count": len(prohibited),
        "manual_review_visibility_count": len(manual_review),
        "fail_visible": True,
        "audit_safe": True,
    }


def _prohibited_behavior_detected(graph: OrchestrationCoordinationGraph) -> bool:
    return any(
        (
            graph.graph_execution_enabled,
            graph.graph_traversal_execution_enabled,
            graph.orchestration_scheduling_enabled,
            graph.orchestration_dispatch_enabled,
            graph.runtime_execution_enabled,
            graph.orchestration_execution_enabled,
            graph.routing_behavior_enabled,
            graph.mutation_behavior_enabled,
            graph.audit_log_writing_enabled,
            graph.production_consumption_enabled,
        )
    )


def _add_blocker(
    blockers: list[OrchestrationCoordinationBlocker],
    candidate_statuses: list[str],
    status: str,
    blocker_id: str,
    category: str,
    rank: int,
    explanation: str,
) -> None:
    candidate_statuses.append(status)
    blockers.append(
        OrchestrationCoordinationBlocker(
            blocker_id=blocker_id,
            coordination_status=status,
            blocker_category=category,
            deterministic_rank=rank,
            fail_visible=True,
            audit_safe=True,
            explanation=explanation,
        )
    )


def _explanation_summary(status: str, blockers: list[OrchestrationCoordinationBlocker]) -> str:
    if not blockers:
        return (
            "Coordination graph is ready for planning-only relationship modeling; no execution, dispatch, "
            "routing, mutation, audit writing, graph execution, scheduling, or production consumption is authorized."
        )
    blocker_ids = ", ".join(row.blocker_id for row in sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))
    return f"Coordination planning classified as {status}; fail-visible blockers: {blocker_ids}."
