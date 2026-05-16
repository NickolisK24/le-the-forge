"""Planning-only orchestration visibility aggregation for v3.5 Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .governance_dependency_resolution import resolve_governance_dependency
from .governance_dependency_status import DEPENDENCY_SATISFIED
from .orchestration_coordination_planning import plan_orchestration_coordination
from .orchestration_coordination_status import COORDINATION_READY_FOR_PLANNING
from .orchestration_readiness_evaluation import evaluate_orchestration_readiness
from .orchestration_readiness_status import READY_FOR_FUTURE_ORCHESTRATION_PLANNING
from .orchestration_visibility_aggregation_models import (
    OrchestrationVisibilityAggregationInput,
    OrchestrationVisibilitySummary,
)
from .orchestration_visibility_aggregation_report_models import (
    OrchestrationVisibilityAggregationResult,
    export_visibility_aggregation_result,
    serialize_visibility_aggregation_result,
)
from .orchestration_visibility_aggregation_status import (
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
    classify_visibility_status,
)


DEFAULT_LIMITATIONS: tuple[str, ...] = (
    "visibility aggregation is declarative and planning-only",
    "visibility aggregation does not authorize orchestration execution",
    "visibility aggregation does not auto-approve planning states",
)


def default_orchestration_visibility_aggregation_input() -> OrchestrationVisibilityAggregationInput:
    coordination = plan_orchestration_coordination()
    return OrchestrationVisibilityAggregationInput(
        visibility_aggregation_id="visibility-aggregation-v3-5-phase-5",
        orchestration_planning_graph_id=coordination.coordination_graph_id,
        readiness_result=evaluate_orchestration_readiness(),
        dependency_result=resolve_governance_dependency(),
        coordination_result=coordination,
        limitation_summary=DEFAULT_LIMITATIONS,
    )


def aggregate_orchestration_visibility(
    aggregation_input: OrchestrationVisibilityAggregationInput | None = None,
) -> OrchestrationVisibilityAggregationResult:
    source = aggregation_input or default_orchestration_visibility_aggregation_input()
    readiness_summary = _readiness_summary(source)
    dependency_summary = _dependency_summary(source)
    coordination_summary = _coordination_summary(source)
    blocker_summary = _combine(
        readiness_summary.blocker_ids,
        dependency_summary.blocker_ids,
        coordination_summary.blocker_ids,
    )
    unsupported_summary = _combine(
        readiness_summary.unsupported_entries,
        dependency_summary.unsupported_entries,
        coordination_summary.unsupported_entries,
    )
    prohibited_summary = _combine(
        readiness_summary.prohibited_entries,
        dependency_summary.prohibited_entries,
        coordination_summary.prohibited_entries,
    )
    lineage_gap_summary = _combine(
        readiness_summary.lineage_gap_entries,
        dependency_summary.lineage_gap_entries,
        coordination_summary.lineage_gap_entries,
    )
    compatibility_summary = _combine(
        readiness_summary.compatibility_failure_entries,
        dependency_summary.compatibility_failure_entries,
        coordination_summary.compatibility_failure_entries,
    )
    environment_summary = _combine(
        readiness_summary.environment_mismatch_entries,
        dependency_summary.environment_mismatch_entries,
        coordination_summary.environment_mismatch_entries,
    )
    manual_review_summary = _combine(
        readiness_summary.manual_review_entries,
        dependency_summary.manual_review_entries,
        coordination_summary.manual_review_entries,
    )
    limitation_summary = _combine(
        source.limitation_summary,
        readiness_summary.limitation_entries,
        dependency_summary.limitation_entries,
        coordination_summary.limitation_entries,
    )
    candidate_statuses = _candidate_statuses(
        source,
        readiness_summary,
        dependency_summary,
        coordination_summary,
        blocker_summary,
        unsupported_summary,
        prohibited_summary,
        lineage_gap_summary,
        compatibility_summary,
        environment_summary,
        manual_review_summary,
    )
    status = classify_visibility_status(candidate_statuses)
    return OrchestrationVisibilityAggregationResult(
        visibility_aggregation_id=source.visibility_aggregation_id,
        orchestration_planning_graph_id=source.orchestration_planning_graph_id,
        aggregate_visibility_status=status,
        planning_only=True,
        readiness_summary=readiness_summary,
        dependency_summary=dependency_summary,
        coordination_summary=coordination_summary,
        blocker_summary=blocker_summary,
        unsupported_state_summary=unsupported_summary,
        prohibited_state_summary=prohibited_summary,
        lineage_gap_summary=lineage_gap_summary,
        compatibility_failure_summary=compatibility_summary,
        environment_mismatch_summary=environment_summary,
        manual_review_summary=manual_review_summary,
        limitation_summary=limitation_summary,
        deterministic_explanation_summary=_explanation_summary(status, blocker_summary),
        runtime_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_behavior_enabled=False,
        mutation_behavior_enabled=False,
        audit_log_writing_enabled=False,
        production_consumption_enabled=False,
        graph_execution_enabled=False,
        graph_traversal_behavior_enabled=False,
        scheduling_behavior_enabled=False,
        orchestration_dispatch_enabled=False,
        auto_approval_behavior_enabled=False,
    )


def export_orchestration_visibility_aggregation_result(
    result: OrchestrationVisibilityAggregationResult,
) -> dict[str, Any]:
    return export_visibility_aggregation_result(result)


def serialize_orchestration_visibility_aggregation_result(
    result: OrchestrationVisibilityAggregationResult,
) -> str:
    return serialize_visibility_aggregation_result(result)


def hash_orchestration_visibility_aggregation_input(source: OrchestrationVisibilityAggregationInput) -> str:
    return deterministic_hash(
        {
            "visibility_aggregation_id": source.visibility_aggregation_id,
            "orchestration_planning_graph_id": source.orchestration_planning_graph_id,
            "readiness_status": source.readiness_result.readiness_status,
            "dependency_status": source.dependency_result.dependency_status,
            "coordination_status": source.coordination_result.coordination_status,
            "limitation_summary": source.limitation_summary,
        }
    )


def _readiness_summary(source: OrchestrationVisibilityAggregationInput) -> OrchestrationVisibilitySummary:
    result = source.readiness_result
    return OrchestrationVisibilitySummary(
        source_id="readiness",
        source_status=result.readiness_status,
        blocker_ids=tuple(row.blocker_id for row in result.blockers),
        unsupported_entries=result.unsupported_states,
        prohibited_entries=result.prohibited_domains,
        lineage_gap_entries=tuple(sorted(result.missing_replay_requirements + result.missing_rollback_requirements)),
        compatibility_failure_entries=result.compatibility_failures,
        environment_mismatch_entries=result.environment_failures,
        manual_review_entries=result.manual_review_reasons,
        limitation_entries=("readiness classification is planning-only",),
    )


def _dependency_summary(source: OrchestrationVisibilityAggregationInput) -> OrchestrationVisibilitySummary:
    result = source.dependency_result
    return OrchestrationVisibilitySummary(
        source_id=result.dependency_id,
        source_status=result.dependency_status,
        blocker_ids=tuple(row.blocker_id for row in result.blockers),
        unsupported_entries=result.unsupported_reasons,
        prohibited_entries=result.prohibited_reasons,
        lineage_gap_entries=result.lineage_gaps,
        compatibility_failure_entries=result.compatibility_failures,
        environment_mismatch_entries=result.environment_mismatches,
        manual_review_entries=result.manual_review_reasons,
        limitation_entries=("dependency resolution is declarative and non-fetching",),
    )


def _coordination_summary(source: OrchestrationVisibilityAggregationInput) -> OrchestrationVisibilitySummary:
    result = source.coordination_result
    return OrchestrationVisibilitySummary(
        source_id=result.coordination_graph_id,
        source_status=result.coordination_status,
        blocker_ids=tuple(row.blocker_id for row in result.blockers),
        unsupported_entries=result.propagated_unsupported_states,
        prohibited_entries=result.propagated_prohibited_states,
        lineage_gap_entries=result.propagated_lineage_gaps,
        compatibility_failure_entries=result.propagated_compatibility_failures,
        environment_mismatch_entries=result.propagated_environment_mismatches,
        manual_review_entries=result.propagated_manual_review_states,
        limitation_entries=("coordination planning graphs are non-executable",),
    )


def _candidate_statuses(
    source: OrchestrationVisibilityAggregationInput,
    readiness: OrchestrationVisibilitySummary,
    dependency: OrchestrationVisibilitySummary,
    coordination: OrchestrationVisibilitySummary,
    blockers: tuple[str, ...],
    unsupported: tuple[str, ...],
    prohibited: tuple[str, ...],
    lineage_gaps: tuple[str, ...],
    compatibility_failures: tuple[str, ...],
    environment_mismatches: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> list[str]:
    candidates: list[str] = []
    if prohibited:
        candidates.append(VISIBILITY_PROHIBITED)
    if unsupported:
        candidates.append(VISIBILITY_UNSUPPORTED)
    if readiness.source_status != READY_FOR_FUTURE_ORCHESTRATION_PLANNING or readiness.blocker_ids:
        candidates.append(VISIBILITY_BLOCKED_BY_READINESS)
    if dependency.source_status != DEPENDENCY_SATISFIED or dependency.blocker_ids:
        candidates.append(VISIBILITY_BLOCKED_BY_DEPENDENCY)
    if coordination.source_status != COORDINATION_READY_FOR_PLANNING or coordination.blocker_ids:
        candidates.append(VISIBILITY_BLOCKED_BY_COORDINATION)
    if lineage_gaps:
        candidates.append(VISIBILITY_BLOCKED_BY_LINEAGE_GAP)
    if compatibility_failures:
        candidates.append(VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE)
    if environment_mismatches:
        candidates.append(VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH)
    if manual_review:
        candidates.append(VISIBILITY_REQUIRES_MANUAL_REVIEW)
    if _prohibited_behavior_detected(source):
        candidates.append(VISIBILITY_PROHIBITED)
    return candidates


def _combine(*groups: tuple[str, ...]) -> tuple[str, ...]:
    values: set[str] = set()
    for group in groups:
        values.update(group)
    return tuple(sorted(values))


def _prohibited_behavior_detected(source: OrchestrationVisibilityAggregationInput) -> bool:
    return any(
        (
            source.readiness_result.runtime_execution_enabled,
            source.readiness_result.orchestration_execution_enabled,
            source.readiness_result.routing_behavior_enabled,
            source.readiness_result.mutation_behavior_enabled,
            source.readiness_result.audit_log_writing_enabled,
            source.readiness_result.production_consumption_enabled,
            source.dependency_result.runtime_execution_enabled,
            source.dependency_result.orchestration_execution_enabled,
            source.dependency_result.routing_behavior_enabled,
            source.dependency_result.mutation_behavior_enabled,
            source.dependency_result.audit_log_writing_enabled,
            source.dependency_result.production_consumption_enabled,
            source.coordination_result.runtime_execution_enabled,
            source.coordination_result.orchestration_execution_enabled,
            source.coordination_result.routing_behavior_enabled,
            source.coordination_result.mutation_behavior_enabled,
            source.coordination_result.audit_log_writing_enabled,
            source.coordination_result.production_consumption_enabled,
            source.coordination_result.graph_execution_enabled,
            source.coordination_result.scheduling_behavior_enabled,
            source.coordination_result.orchestration_dispatch_enabled,
        )
    )


def _explanation_summary(status: str, blockers: tuple[str, ...]) -> str:
    if not blockers:
        return (
            "Visibility aggregation is ready for planning-only explanation; no execution, dispatch, routing, "
            "mutation, audit writing, graph execution, scheduling, production consumption, or auto-approval is authorized."
        )
    return f"Visibility aggregation classified as {status}; fail-visible entries: {', '.join(sorted(blockers))}."
