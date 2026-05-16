"""Planning-only snapshot diff and drift analysis for v3.5 Phase 7."""

from __future__ import annotations

from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .orchestration_planning_snapshot import generate_orchestration_planning_snapshot
from .orchestration_planning_snapshot_report_models import OrchestrationPlanningSnapshotResult
from .orchestration_planning_snapshot_status import (
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_READY_FOR_REPLAY_PLANNING,
    SNAPSHOT_UNSUPPORTED,
)
from .orchestration_snapshot_diff_models import (
    OrchestrationSnapshotDiffInput,
    OrchestrationSnapshotFieldDiff,
)
from .orchestration_snapshot_diff_report_models import (
    OrchestrationSnapshotDiffResult,
    export_snapshot_diff_result,
    serialize_snapshot_diff_result,
)
from .orchestration_snapshot_diff_status import (
    SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH,
    SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE,
    SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY,
    SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    SNAPSHOT_DIFF_PROHIBITED,
    SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED,
    SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_DIFF_UNSUPPORTED,
    classify_snapshot_diff_status,
)


DEFAULT_DIFF_LIMITATIONS: tuple[str, ...] = (
    "snapshot diff analysis is declarative and planning-only",
    "snapshot diff analysis does not authorize orchestration execution",
    "snapshot diff analysis does not perform live replay execution",
    "snapshot diff analysis does not capture runtime traces or read production state",
)


def default_orchestration_snapshot_diff_input() -> OrchestrationSnapshotDiffInput:
    source = generate_orchestration_planning_snapshot()
    target = generate_orchestration_planning_snapshot()
    return OrchestrationSnapshotDiffInput(
        diff_analysis_id="snapshot-diff-v3-5-phase-7",
        source_snapshot=source,
        target_snapshot=target,
        replay_stability_verified=True,
        deterministic_serialization_verified=True,
        expected_source_snapshot_hash=source.deterministic_snapshot_hash,
        expected_target_snapshot_hash=target.deterministic_snapshot_hash,
        manual_review_reasons=(),
        limitation_summary=DEFAULT_DIFF_LIMITATIONS,
    )


def analyze_orchestration_snapshot_diff(
    diff_input: OrchestrationSnapshotDiffInput | None = None,
) -> OrchestrationSnapshotDiffResult:
    source = diff_input or default_orchestration_snapshot_diff_input()
    readiness_diffs = (_scalar_diff("readiness_state", _reference_status(source.source_snapshot.readiness_state_reference), _reference_status(source.target_snapshot.readiness_state_reference)),)
    dependency_diffs = (_scalar_diff("dependency_state", _reference_status(source.source_snapshot.dependency_state_reference), _reference_status(source.target_snapshot.dependency_state_reference)),)
    coordination_diffs = (_scalar_diff("coordination_state", _reference_status(source.source_snapshot.coordination_state_reference), _reference_status(source.target_snapshot.coordination_state_reference)),)
    visibility_diffs = (_scalar_diff("visibility_state", _reference_status(source.source_snapshot.visibility_aggregation_reference), _reference_status(source.target_snapshot.visibility_aggregation_reference)),)
    blocker_diffs = (_tuple_diff("blockers", source.source_snapshot.blocker_summary, source.target_snapshot.blocker_summary),)
    unsupported_prohibited_diffs = (
        _tuple_diff("unsupported_states", source.source_snapshot.unsupported_state_summary, source.target_snapshot.unsupported_state_summary),
        _tuple_diff("prohibited_states", source.source_snapshot.prohibited_state_summary, source.target_snapshot.prohibited_state_summary),
    )
    lineage_diffs = (
        _tuple_diff("lineage_gaps", source.source_snapshot.lineage_summary, source.target_snapshot.lineage_summary),
        _tuple_diff("replay_lineage", source.source_snapshot.replay_lineage_references, source.target_snapshot.replay_lineage_references),
        _tuple_diff("rollback_lineage", source.source_snapshot.rollback_lineage_references, source.target_snapshot.rollback_lineage_references),
    )
    compatibility_diffs = (_tuple_diff("compatibility_references", source.source_snapshot.compatibility_references, source.target_snapshot.compatibility_references),)
    environment_diffs = (_tuple_diff("environment_references", source.source_snapshot.environment_references, source.target_snapshot.environment_references),)
    limitation_diffs = (_tuple_diff("limitations", source.source_snapshot.limitation_summary + source.limitation_summary, source.target_snapshot.limitation_summary + source.limitation_summary),)
    replay_safety = _replay_safety_diffs(source)
    manual_review = tuple(sorted(set(source.manual_review_reasons + source.source_snapshot.manual_review_summary + source.target_snapshot.manual_review_summary)))
    drift = _drift_classifications(
        readiness_diffs,
        dependency_diffs,
        coordination_diffs,
        visibility_diffs,
        blocker_diffs,
        unsupported_prohibited_diffs,
        lineage_diffs,
        compatibility_diffs,
        environment_diffs,
        limitation_diffs,
        replay_safety,
    )
    candidates = _candidate_statuses(source, drift, replay_safety, manual_review, unsupported_prohibited_diffs, lineage_diffs)
    status = classify_snapshot_diff_status(candidates)
    drift_summary = _drift_summary(drift, replay_safety)
    return OrchestrationSnapshotDiffResult(
        diff_analysis_id=source.diff_analysis_id,
        source_snapshot_id=source.source_snapshot.snapshot_id,
        target_snapshot_id=source.target_snapshot.snapshot_id,
        source_snapshot_hash=source.source_snapshot.deterministic_snapshot_hash,
        target_snapshot_hash=source.target_snapshot.deterministic_snapshot_hash,
        diff_status=status,
        planning_only=True,
        readiness_diffs=_changed_only(readiness_diffs),
        dependency_diffs=_changed_only(dependency_diffs),
        coordination_diffs=_changed_only(coordination_diffs),
        visibility_diffs=_changed_only(visibility_diffs),
        blocker_diffs=_changed_only(blocker_diffs),
        unsupported_prohibited_diffs=_changed_only(unsupported_prohibited_diffs),
        lineage_diffs=_changed_only(lineage_diffs),
        compatibility_diffs=_changed_only(compatibility_diffs),
        environment_diffs=_changed_only(environment_diffs),
        replay_safety_diffs=replay_safety,
        manual_review_diffs=manual_review,
        limitation_diffs=_changed_only(limitation_diffs),
        drift_classifications=drift,
        deterministic_drift_summary=drift_summary,
        deterministic_explanation_summary=_explanation(status, drift_summary),
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
        runtime_trace_capture_enabled=False,
        production_state_reads_enabled=False,
        live_replay_enabled=False,
    )


def export_orchestration_snapshot_diff_result(result: OrchestrationSnapshotDiffResult) -> dict[str, Any]:
    return export_snapshot_diff_result(result)


def serialize_orchestration_snapshot_diff_result(result: OrchestrationSnapshotDiffResult) -> str:
    return serialize_snapshot_diff_result(result)


def hash_orchestration_snapshot_diff_input(source: OrchestrationSnapshotDiffInput) -> str:
    return deterministic_hash(
        {
            "diff_analysis_id": source.diff_analysis_id,
            "source_snapshot_hash": source.source_snapshot.deterministic_snapshot_hash,
            "target_snapshot_hash": source.target_snapshot.deterministic_snapshot_hash,
            "replay_stability_verified": source.replay_stability_verified,
            "deterministic_serialization_verified": source.deterministic_serialization_verified,
            "expected_source_snapshot_hash": source.expected_source_snapshot_hash,
            "expected_target_snapshot_hash": source.expected_target_snapshot_hash,
            "manual_review_reasons": sorted(source.manual_review_reasons),
            "limitation_summary": sorted(source.limitation_summary),
        }
    )


def _reference_status(reference: Any | None) -> tuple[str, ...]:
    if reference is None:
        return ()
    return (reference.reference_status,)


def _scalar_diff(diff_type: str, source: tuple[str, ...], target: tuple[str, ...]) -> OrchestrationSnapshotFieldDiff:
    return _tuple_diff(diff_type, source, target)


def _tuple_diff(diff_type: str, source: tuple[str, ...], target: tuple[str, ...]) -> OrchestrationSnapshotFieldDiff:
    source_values = tuple(sorted(source))
    target_values = tuple(sorted(target))
    return OrchestrationSnapshotFieldDiff(
        diff_type=diff_type,
        source_values=source_values,
        target_values=target_values,
        added_values=tuple(sorted(set(target_values) - set(source_values))),
        removed_values=tuple(sorted(set(source_values) - set(target_values))),
    )


def _changed_only(diffs: tuple[OrchestrationSnapshotFieldDiff, ...]) -> tuple[OrchestrationSnapshotFieldDiff, ...]:
    return tuple(diff for diff in diffs if diff.added_values or diff.removed_values)


def _replay_safety_diffs(source: OrchestrationSnapshotDiffInput) -> tuple[str, ...]:
    entries: set[str] = set()
    if not source.replay_stability_verified:
        entries.add("replay_stability_not_verified")
    if not source.deterministic_serialization_verified:
        entries.add("deterministic_serialization_not_verified")
    if source.expected_source_snapshot_hash != source.source_snapshot.deterministic_snapshot_hash:
        entries.add("source_snapshot_hash_mismatch")
    if source.expected_target_snapshot_hash != source.target_snapshot.deterministic_snapshot_hash:
        entries.add("target_snapshot_hash_mismatch")
    if source.source_snapshot.deterministic_snapshot_hash != source.target_snapshot.deterministic_snapshot_hash:
        entries.add("snapshot_hash_changed")
    return tuple(sorted(entries))


def _drift_classifications(*groups: tuple[Any, ...]) -> tuple[str, ...]:
    drift: set[str] = set()
    for group in groups:
        for item in group:
            if isinstance(item, str):
                if item in ("replay_stability_not_verified", "deterministic_serialization_not_verified"):
                    drift.add("replay_drift")
                if item.endswith("_hash_mismatch"):
                    drift.add("hash_drift")
                continue
            if not (item.added_values or item.removed_values):
                continue
            mapping = {
                "readiness_state": "governance_drift",
                "dependency_state": "governance_drift",
                "coordination_state": "governance_drift",
                "visibility_state": "governance_drift",
                "blockers": "blocker_drift",
                "unsupported_states": "unsupported_state_drift",
                "prohibited_states": "prohibited_state_drift",
                "lineage_gaps": "lineage_drift",
                "replay_lineage": "lineage_drift",
                "rollback_lineage": "lineage_drift",
                "compatibility_references": "compatibility_drift",
                "environment_references": "environment_drift",
                "limitations": "limitation_drift",
            }
            drift.add(mapping.get(item.diff_type, "governance_drift"))
    return tuple(sorted(drift))


def _candidate_statuses(
    source: OrchestrationSnapshotDiffInput,
    drift: tuple[str, ...],
    replay_safety: tuple[str, ...],
    manual_review: tuple[str, ...],
    unsupported_prohibited: tuple[OrchestrationSnapshotFieldDiff, ...],
    lineage: tuple[OrchestrationSnapshotFieldDiff, ...],
) -> list[str]:
    candidates: list[str] = []
    if (
        source.source_snapshot.snapshot_status == SNAPSHOT_PROHIBITED
        or source.target_snapshot.snapshot_status == SNAPSHOT_PROHIBITED
        or any(diff.diff_type == "prohibited_states" and (diff.added_values or diff.removed_values) for diff in unsupported_prohibited)
        or _prohibited_behavior_detected(source)
    ):
        candidates.append(SNAPSHOT_DIFF_PROHIBITED)
    if (
        source.source_snapshot.snapshot_status == SNAPSHOT_UNSUPPORTED
        or source.target_snapshot.snapshot_status == SNAPSHOT_UNSUPPORTED
        or any(diff.diff_type == "unsupported_states" and (diff.added_values or diff.removed_values) for diff in unsupported_prohibited)
    ):
        candidates.append(SNAPSHOT_DIFF_UNSUPPORTED)
    if "deterministic_serialization_not_verified" in replay_safety:
        candidates.append(SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED)
    if any(diff.added_values or diff.removed_values for diff in lineage):
        candidates.append(SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE)
    if "replay_stability_not_verified" in replay_safety:
        candidates.append(SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY)
    if any(item.endswith("_hash_mismatch") for item in replay_safety):
        candidates.append(SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH)
    if drift:
        candidates.append(SNAPSHOT_DIFF_DRIFT_DETECTED)
    if manual_review:
        candidates.append(SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW)
    if source.source_snapshot.deterministic_snapshot_hash != source.target_snapshot.deterministic_snapshot_hash:
        candidates.append(SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT)
    return candidates


def _prohibited_behavior_detected(source: OrchestrationSnapshotDiffInput) -> bool:
    for snapshot in (source.source_snapshot, source.target_snapshot):
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
            "runtime_trace_capture_enabled",
            "production_state_reads_enabled",
        ):
            if getattr(snapshot, field, False):
                return True
    return False


def _drift_summary(drift: tuple[str, ...], replay_safety: tuple[str, ...]) -> tuple[str, ...]:
    entries = set(drift)
    entries.update(replay_safety)
    if not entries:
        entries.add("no_snapshot_drift_detected")
    return tuple(sorted(entries))


def _explanation(status: str, drift_summary: tuple[str, ...]) -> str:
    if drift_summary == ("no_snapshot_drift_detected",):
        return (
            "Snapshot diff is stable; no execution, dispatch, routing, mutation, audit writing, graph execution, "
            "scheduling, live replay, runtime trace capture, or production state read is authorized."
        )
    return f"Snapshot diff classified as {status}; drift entries: {', '.join(drift_summary)}."
