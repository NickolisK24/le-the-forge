"""Planning-only orchestration snapshot generation for v3.5 Phase 6."""

from __future__ import annotations

from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .governance_dependency_status import DEPENDENCY_SATISFIED
from .orchestration_coordination_status import COORDINATION_READY_FOR_PLANNING
from .orchestration_planning_snapshot_models import (
    OrchestrationPlanningSnapshotInput,
    OrchestrationPlanningStateReference,
)
from .orchestration_planning_snapshot_report_models import (
    OrchestrationPlanningSnapshotResult,
    export_snapshot_result,
    serialize_snapshot_result,
)
from .orchestration_planning_snapshot_status import (
    SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY,
    SNAPSHOT_BLOCKED_BY_LINEAGE_GAP,
    SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE,
    SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_UNSUPPORTED,
    classify_snapshot_status,
)
from .orchestration_readiness_status import READY_FOR_FUTURE_ORCHESTRATION_PLANNING
from .governance_dependency_resolution import resolve_governance_dependency
from .governance_dependency_report_models import hash_dependency_resolution_result
from .orchestration_coordination_planning import plan_orchestration_coordination
from .orchestration_coordination_report_models import hash_coordination_planning_result
from .orchestration_readiness_evaluation import evaluate_orchestration_readiness
from .orchestration_readiness_report_models import hash_readiness_result
from .orchestration_visibility_aggregation import aggregate_orchestration_visibility
from .orchestration_visibility_aggregation_models import OrchestrationVisibilityAggregationInput
from .orchestration_visibility_aggregation_report_models import hash_visibility_aggregation_result
from .orchestration_visibility_aggregation_status import (
    VISIBILITY_PROHIBITED,
    VISIBILITY_READY_FOR_PLANNING,
    VISIBILITY_REQUIRES_MANUAL_REVIEW,
    VISIBILITY_UNSUPPORTED,
)


DEFAULT_SNAPSHOT_LIMITATIONS: tuple[str, ...] = (
    "snapshot generation is declarative and planning-only",
    "snapshot generation does not authorize orchestration execution",
    "snapshot generation does not capture runtime traces",
    "snapshot generation does not read production state",
)


def default_orchestration_planning_snapshot_input() -> OrchestrationPlanningSnapshotInput:
    readiness = evaluate_orchestration_readiness()
    dependency = resolve_governance_dependency()
    coordination = plan_orchestration_coordination()
    visibility = aggregate_orchestration_visibility(
        OrchestrationVisibilityAggregationInput(
            visibility_aggregation_id="visibility-aggregation-v3-5-phase-5",
            orchestration_planning_graph_id=coordination.coordination_graph_id,
            readiness_result=readiness,
            dependency_result=dependency,
            coordination_result=coordination,
            limitation_summary=(
                "visibility aggregation is declarative and planning-only",
                "visibility aggregation does not authorize orchestration execution",
                "visibility aggregation does not auto-approve planning states",
            ),
        )
    )
    return OrchestrationPlanningSnapshotInput(
        snapshot_id="snapshot-v3-5-phase-6",
        orchestration_planning_graph_id=visibility.orchestration_planning_graph_id,
        readiness_result=readiness,
        dependency_result=dependency,
        coordination_result=coordination,
        visibility_result=visibility,
        replay_lineage_references=("replay-lineage-v3-5-phase-6",),
        rollback_lineage_references=("rollback-lineage-v3-5-phase-6",),
        compatibility_references=("compatibility-v3-5-phase-6",),
        environment_references=("non-production-environment-v3-5-phase-6",),
        limitation_summary=DEFAULT_SNAPSHOT_LIMITATIONS,
        manual_review_reasons=(),
        hash_stability_verified=True,
    )


def generate_orchestration_planning_snapshot(
    snapshot_input: OrchestrationPlanningSnapshotInput | None = None,
) -> OrchestrationPlanningSnapshotResult:
    source = snapshot_input or default_orchestration_planning_snapshot_input()
    readiness_reference = _readiness_reference(source)
    dependency_reference = _dependency_reference(source)
    coordination_reference = _coordination_reference(source)
    visibility_reference = _visibility_reference(source)
    blocker_summary = _blockers(source)
    unsupported_summary = _unsupported(source)
    prohibited_summary = _prohibited(source)
    lineage_summary = _lineage_gaps(source)
    manual_review_summary = _manual_review(source)
    limitation_summary = _limitations(source)
    candidates = _candidate_statuses(
        source,
        blocker_summary,
        unsupported_summary,
        prohibited_summary,
        lineage_summary,
        manual_review_summary,
    )
    status = classify_snapshot_status(candidates)
    snapshot_hash = _snapshot_hash(
        source,
        readiness_reference,
        dependency_reference,
        coordination_reference,
        visibility_reference,
        blocker_summary,
        unsupported_summary,
        prohibited_summary,
        lineage_summary,
        manual_review_summary,
        limitation_summary,
    )
    return OrchestrationPlanningSnapshotResult(
        snapshot_id=source.snapshot_id,
        orchestration_planning_graph_id=source.orchestration_planning_graph_id,
        snapshot_status=status,
        planning_only=True,
        readiness_state_reference=readiness_reference,
        dependency_state_reference=dependency_reference,
        coordination_state_reference=coordination_reference,
        visibility_aggregation_reference=visibility_reference,
        blocker_summary=blocker_summary,
        unsupported_state_summary=unsupported_summary,
        prohibited_state_summary=prohibited_summary,
        lineage_summary=lineage_summary,
        replay_lineage_references=tuple(sorted(source.replay_lineage_references)),
        rollback_lineage_references=tuple(sorted(source.rollback_lineage_references)),
        compatibility_references=tuple(sorted(source.compatibility_references)),
        environment_references=tuple(sorted(source.environment_references)),
        limitation_summary=limitation_summary,
        manual_review_summary=manual_review_summary,
        deterministic_snapshot_hash=snapshot_hash,
        deterministic_explanation_summary=_explanation_summary(
            status,
            blocker_summary,
            lineage_summary,
            unsupported_summary,
            prohibited_summary,
            manual_review_summary,
        ),
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
        runtime_trace_capture_enabled=False,
        production_state_reads_enabled=False,
    )


def export_orchestration_planning_snapshot_result(
    result: OrchestrationPlanningSnapshotResult,
) -> dict[str, Any]:
    return export_snapshot_result(result)


def serialize_orchestration_planning_snapshot_result(result: OrchestrationPlanningSnapshotResult) -> str:
    return serialize_snapshot_result(result)


def hash_orchestration_planning_snapshot_input(source: OrchestrationPlanningSnapshotInput) -> str:
    return deterministic_hash(
        {
            "snapshot_id": source.snapshot_id,
            "orchestration_planning_graph_id": source.orchestration_planning_graph_id,
            "readiness_present": source.readiness_result is not None,
            "dependency_present": source.dependency_result is not None,
            "coordination_present": source.coordination_result is not None,
            "visibility_present": source.visibility_result is not None,
            "replay_lineage_references": sorted(source.replay_lineage_references),
            "rollback_lineage_references": sorted(source.rollback_lineage_references),
            "compatibility_references": sorted(source.compatibility_references),
            "environment_references": sorted(source.environment_references),
            "limitation_summary": sorted(source.limitation_summary),
            "manual_review_reasons": sorted(source.manual_review_reasons),
            "hash_stability_verified": source.hash_stability_verified,
        }
    )


def _readiness_reference(source: OrchestrationPlanningSnapshotInput) -> OrchestrationPlanningStateReference | None:
    if source.readiness_result is None:
        return None
    return OrchestrationPlanningStateReference(
        reference_type="readiness",
        reference_id="readiness",
        reference_status=source.readiness_result.readiness_status,
        deterministic_hash=hash_readiness_result(source.readiness_result),
    )


def _dependency_reference(source: OrchestrationPlanningSnapshotInput) -> OrchestrationPlanningStateReference | None:
    if source.dependency_result is None:
        return None
    return OrchestrationPlanningStateReference(
        reference_type="dependency",
        reference_id=source.dependency_result.dependency_id,
        reference_status=source.dependency_result.dependency_status,
        deterministic_hash=hash_dependency_resolution_result(source.dependency_result),
    )


def _coordination_reference(source: OrchestrationPlanningSnapshotInput) -> OrchestrationPlanningStateReference | None:
    if source.coordination_result is None:
        return None
    return OrchestrationPlanningStateReference(
        reference_type="coordination",
        reference_id=source.coordination_result.coordination_graph_id,
        reference_status=source.coordination_result.coordination_status,
        deterministic_hash=hash_coordination_planning_result(source.coordination_result),
    )


def _visibility_reference(source: OrchestrationPlanningSnapshotInput) -> OrchestrationPlanningStateReference | None:
    if source.visibility_result is None:
        return None
    return OrchestrationPlanningStateReference(
        reference_type="visibility",
        reference_id=source.visibility_result.visibility_aggregation_id,
        reference_status=source.visibility_result.aggregate_visibility_status,
        deterministic_hash=hash_visibility_aggregation_result(source.visibility_result),
    )


def _blockers(source: OrchestrationPlanningSnapshotInput) -> tuple[str, ...]:
    blockers: set[str] = set()
    if source.visibility_result is not None:
        blockers.update(source.visibility_result.blocker_summary)
    if source.readiness_result is not None:
        blockers.update(row.blocker_id for row in source.readiness_result.blockers)
    if source.dependency_result is not None:
        blockers.update(row.blocker_id for row in source.dependency_result.blockers)
    if source.coordination_result is not None:
        blockers.update(row.blocker_id for row in source.coordination_result.blockers)
    if not source.hash_stability_verified:
        blockers.add("snapshot_hash_stability_not_verified")
    return tuple(sorted(blockers))


def _unsupported(source: OrchestrationPlanningSnapshotInput) -> tuple[str, ...]:
    values: set[str] = set()
    if source.visibility_result is not None:
        values.update(source.visibility_result.unsupported_state_summary)
    return tuple(sorted(values))


def _prohibited(source: OrchestrationPlanningSnapshotInput) -> tuple[str, ...]:
    values: set[str] = set()
    if source.visibility_result is not None:
        values.update(source.visibility_result.prohibited_state_summary)
    return tuple(sorted(values))


def _lineage_gaps(source: OrchestrationPlanningSnapshotInput) -> tuple[str, ...]:
    gaps: set[str] = set()
    if source.visibility_result is not None:
        gaps.update(source.visibility_result.lineage_gap_summary)
    if not source.replay_lineage_references:
        gaps.add("replay_lineage_references")
    if not source.rollback_lineage_references:
        gaps.add("rollback_lineage_references")
    return tuple(sorted(gaps))


def _manual_review(source: OrchestrationPlanningSnapshotInput) -> tuple[str, ...]:
    values: set[str] = set(source.manual_review_reasons)
    if source.visibility_result is not None:
        values.update(source.visibility_result.manual_review_summary)
    return tuple(sorted(values))


def _limitations(source: OrchestrationPlanningSnapshotInput) -> tuple[str, ...]:
    values: set[str] = set(source.limitation_summary)
    if source.visibility_result is not None:
        values.update(source.visibility_result.limitation_summary)
    return tuple(sorted(values))


def _candidate_statuses(
    source: OrchestrationPlanningSnapshotInput,
    blockers: tuple[str, ...],
    unsupported: tuple[str, ...],
    prohibited: tuple[str, ...],
    lineage_gaps: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> list[str]:
    candidates: list[str] = []
    if (
        prohibited
        or _prohibited_behavior_detected(source)
        or (
            source.visibility_result is not None
            and source.visibility_result.aggregate_visibility_status == VISIBILITY_PROHIBITED
        )
    ):
        candidates.append(SNAPSHOT_PROHIBITED)
    if (
        unsupported
        or (
            source.visibility_result is not None
            and source.visibility_result.aggregate_visibility_status == VISIBILITY_UNSUPPORTED
        )
    ):
        candidates.append(SNAPSHOT_UNSUPPORTED)
    if source.visibility_result is None:
        candidates.append(SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE)
    elif source.visibility_result.aggregate_visibility_status not in (
        VISIBILITY_READY_FOR_PLANNING,
        VISIBILITY_REQUIRES_MANUAL_REVIEW,
    ):
        candidates.append(SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE)
    if source.readiness_result is None:
        candidates.append(SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE)
    elif source.readiness_result.readiness_status != READY_FOR_FUTURE_ORCHESTRATION_PLANNING:
        candidates.append(SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE)
    if source.dependency_result is None:
        candidates.append(SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE)
    elif source.dependency_result.dependency_status != DEPENDENCY_SATISFIED:
        candidates.append(SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE)
    if source.coordination_result is None:
        candidates.append(SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE)
    elif source.coordination_result.coordination_status != COORDINATION_READY_FOR_PLANNING:
        candidates.append(SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE)
    if lineage_gaps:
        candidates.append(SNAPSHOT_BLOCKED_BY_LINEAGE_GAP)
    if not source.hash_stability_verified:
        candidates.append(SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY)
    if manual_review:
        candidates.append(SNAPSHOT_REQUIRES_MANUAL_REVIEW)
    return candidates


def _prohibited_behavior_detected(source: OrchestrationPlanningSnapshotInput) -> bool:
    results = (
        source.readiness_result,
        source.dependency_result,
        source.coordination_result,
        source.visibility_result,
    )
    for result in results:
        if result is None:
            continue
        for field in (
            "runtime_execution_enabled",
            "orchestration_execution_enabled",
            "routing_behavior_enabled",
            "mutation_behavior_enabled",
            "audit_log_writing_enabled",
            "production_consumption_enabled",
            "graph_execution_enabled",
            "graph_traversal_behavior_enabled",
            "scheduling_behavior_enabled",
            "orchestration_dispatch_enabled",
            "auto_approval_behavior_enabled",
            "runtime_trace_capture_enabled",
            "production_state_reads_enabled",
        ):
            if getattr(result, field, False):
                return True
    return False


def _snapshot_hash(
    source: OrchestrationPlanningSnapshotInput,
    readiness: OrchestrationPlanningStateReference | None,
    dependency: OrchestrationPlanningStateReference | None,
    coordination: OrchestrationPlanningStateReference | None,
    visibility: OrchestrationPlanningStateReference | None,
    blockers: tuple[str, ...],
    unsupported: tuple[str, ...],
    prohibited: tuple[str, ...],
    lineage_gaps: tuple[str, ...],
    manual_review: tuple[str, ...],
    limitations: tuple[str, ...],
) -> str:
    def export_ref(reference: OrchestrationPlanningStateReference | None) -> dict[str, str] | None:
        if reference is None:
            return None
        return {
            "reference_type": reference.reference_type,
            "reference_id": reference.reference_id,
            "reference_status": reference.reference_status,
            "deterministic_hash": reference.deterministic_hash,
        }

    return deterministic_hash(
        {
            "snapshot_id": source.snapshot_id,
            "orchestration_planning_graph_id": source.orchestration_planning_graph_id,
            "readiness_reference": export_ref(readiness),
            "dependency_reference": export_ref(dependency),
            "coordination_reference": export_ref(coordination),
            "visibility_reference": export_ref(visibility),
            "blockers": sorted(blockers),
            "unsupported": sorted(unsupported),
            "prohibited": sorted(prohibited),
            "lineage_gaps": sorted(lineage_gaps),
            "replay_lineage_references": sorted(source.replay_lineage_references),
            "rollback_lineage_references": sorted(source.rollback_lineage_references),
            "compatibility_references": sorted(source.compatibility_references),
            "environment_references": sorted(source.environment_references),
            "manual_review": sorted(manual_review),
            "limitations": sorted(limitations),
            "hash_stability_verified": source.hash_stability_verified,
        }
    )


def _explanation_summary(
    status: str,
    blockers: tuple[str, ...],
    lineage_gaps: tuple[str, ...],
    unsupported: tuple[str, ...],
    prohibited: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> str:
    entries = tuple(sorted(blockers + lineage_gaps + unsupported + prohibited + manual_review))
    if not entries:
        if status == "snapshot_ready_for_replay_planning":
            return (
                "Snapshot is ready for replay planning; no execution, dispatch, routing, mutation, audit writing, "
                "graph execution, scheduling, production consumption, runtime trace capture, or production state read is authorized."
            )
        return f"Snapshot classified as {status}; no execution behavior is authorized."
    return f"Snapshot classified as {status}; fail-visible entries: {', '.join(entries)}."
