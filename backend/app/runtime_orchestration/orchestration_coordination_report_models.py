"""Stable report models for v3.5 orchestration coordination planning."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .orchestration_coordination_models import OrchestrationCoordinationGraph, export_coordination_graph


@dataclass(frozen=True)
class OrchestrationCoordinationBlocker:
    blocker_id: str
    coordination_status: str
    blocker_category: str
    deterministic_rank: int
    fail_visible: bool
    audit_safe: bool
    explanation: str


@dataclass(frozen=True)
class OrchestrationCoordinationPlanningResult:
    coordination_graph_id: str
    coordination_status: str
    planning_only: bool
    coordination_scopes: tuple[str, ...]
    coordination_nodes: tuple[str, ...]
    coordination_edges: tuple[str, ...]
    propagated_blockers: tuple[str, ...]
    propagated_unsupported_states: tuple[str, ...]
    propagated_prohibited_states: tuple[str, ...]
    propagated_manual_review_states: tuple[str, ...]
    propagated_lineage_gaps: tuple[str, ...]
    propagated_compatibility_failures: tuple[str, ...]
    propagated_environment_mismatches: tuple[str, ...]
    dependency_chains: tuple[str, ...]
    lineage_aggregation: dict[str, Any]
    visibility_aggregation: dict[str, Any]
    blockers: tuple[OrchestrationCoordinationBlocker, ...]
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool
    orchestration_execution_enabled: bool
    routing_behavior_enabled: bool
    mutation_behavior_enabled: bool
    audit_log_writing_enabled: bool
    production_consumption_enabled: bool
    graph_execution_enabled: bool
    scheduling_behavior_enabled: bool
    orchestration_dispatch_enabled: bool
    graph: OrchestrationCoordinationGraph


def order_coordination_blockers(
    blockers: tuple[OrchestrationCoordinationBlocker, ...],
) -> tuple[OrchestrationCoordinationBlocker, ...]:
    return tuple(sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))


def export_coordination_planning_result(result: OrchestrationCoordinationPlanningResult) -> dict[str, Any]:
    data = asdict(result)
    data["graph"] = export_coordination_graph(result.graph)
    data["blockers"] = [asdict(row) for row in order_coordination_blockers(result.blockers)]
    for field in (
        "coordination_scopes",
        "coordination_nodes",
        "coordination_edges",
        "propagated_blockers",
        "propagated_unsupported_states",
        "propagated_prohibited_states",
        "propagated_manual_review_states",
        "propagated_lineage_gaps",
        "propagated_compatibility_failures",
        "propagated_environment_mismatches",
        "dependency_chains",
    ):
        data[field] = list(data[field])
    data["deterministic_hash"] = hash_coordination_planning_result(result)
    return data


def serialize_coordination_planning_result(result: OrchestrationCoordinationPlanningResult) -> str:
    return stable_serialize(export_coordination_planning_result(result))


def hash_coordination_planning_result(result: OrchestrationCoordinationPlanningResult) -> str:
    payload = asdict(result)
    payload["graph"] = export_coordination_graph(result.graph)
    payload["blockers"] = [asdict(row) for row in order_coordination_blockers(result.blockers)]
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
