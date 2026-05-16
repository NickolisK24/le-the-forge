"""Planning-only orchestration integrity auditing for v3.5 Phase 9."""

from __future__ import annotations

from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .governance_dependency_resolution import resolve_governance_dependency
from .governance_dependency_status import DEPENDENCY_PROHIBITED, DEPENDENCY_SATISFIED, DEPENDENCY_UNSUPPORTED
from .orchestration_audit_chain import build_orchestration_audit_chain
from .orchestration_audit_chain_status import AUDIT_CHAIN_PROHIBITED, AUDIT_CHAIN_STABLE, AUDIT_CHAIN_UNSUPPORTED
from .orchestration_coordination_planning import plan_orchestration_coordination
from .orchestration_coordination_status import COORDINATION_PROHIBITED, COORDINATION_READY_FOR_PLANNING, COORDINATION_UNSUPPORTED
from .orchestration_integrity_audit_models import OrchestrationIntegrityAuditInput, OrchestrationIntegritySummary
from .orchestration_integrity_audit_report_models import (
    OrchestrationIntegrityAuditResult,
    export_integrity_audit_result,
    serialize_integrity_audit_result,
)
from .orchestration_integrity_audit_status import (
    INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY,
    INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE,
    INTEGRITY_AUDIT_INTEGRITY_COMPROMISED,
    INTEGRITY_AUDIT_PROHIBITED,
    INTEGRITY_AUDIT_REQUIRES_MANUAL_REVIEW,
    INTEGRITY_AUDIT_UNSUPPORTED,
    classify_integrity_audit_status,
)
from .orchestration_planning_snapshot import generate_orchestration_planning_snapshot
from .orchestration_planning_snapshot_status import SNAPSHOT_PROHIBITED, SNAPSHOT_READY_FOR_REPLAY_PLANNING, SNAPSHOT_UNSUPPORTED
from .orchestration_readiness_evaluation import evaluate_orchestration_readiness
from .orchestration_readiness_status import (
    PROHIBITED_ORCHESTRATION_REQUEST,
    READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
    UNSUPPORTED_ORCHESTRATION_REQUEST,
)
from .orchestration_snapshot_diff_analysis import analyze_orchestration_snapshot_diff
from .orchestration_snapshot_diff_status import SNAPSHOT_DIFF_PROHIBITED, SNAPSHOT_DIFF_STABLE, SNAPSHOT_DIFF_UNSUPPORTED
from .orchestration_visibility_aggregation import aggregate_orchestration_visibility
from .orchestration_visibility_aggregation_status import VISIBILITY_PROHIBITED, VISIBILITY_READY_FOR_PLANNING, VISIBILITY_UNSUPPORTED


DEFAULT_INTEGRITY_AUDIT_LIMITATIONS: tuple[str, ...] = (
    "integrity auditing is declarative and planning-only",
    "integrity auditing does not execute, dispatch, route, mutate, write, schedule, or traverse orchestration",
    "integrity auditing does not persist audit state",
    "integrity auditing does not capture runtime traces, perform live replay, or read production state",
)


def default_orchestration_integrity_audit_input() -> OrchestrationIntegrityAuditInput:
    return OrchestrationIntegrityAuditInput(
        integrity_audit_id="integrity-audit-v3-5-phase-9",
        governance_integrity_references=("governance-consumption-v3-5-phase-1",),
        readiness_result=evaluate_orchestration_readiness(),
        dependency_result=resolve_governance_dependency(),
        coordination_result=plan_orchestration_coordination(),
        visibility_result=aggregate_orchestration_visibility(),
        snapshot_result=generate_orchestration_planning_snapshot(),
        diff_result=analyze_orchestration_snapshot_diff(),
        audit_chain_result=build_orchestration_audit_chain(),
        replay_integrity_references=("replay-integrity-v3-5-phase-9",),
        rollback_integrity_references=("rollback-integrity-v3-5-phase-9",),
        lineage_integrity_references=("lineage-integrity-v3-5-phase-9",),
        deterministic_serialization_verified=True,
        expected_integrity_hash=None,
        manual_review_reasons=(),
        unsupported_reasons=(),
        prohibited_reasons=(),
        limitation_summary=DEFAULT_INTEGRITY_AUDIT_LIMITATIONS,
    )


def audit_orchestration_planning_integrity(
    audit_input: OrchestrationIntegrityAuditInput | None = None,
) -> OrchestrationIntegrityAuditResult:
    source = audit_input or default_orchestration_integrity_audit_input()
    governance = _reference_summary("governance", source.governance_integrity_references, "governance_integrity_references")
    readiness = _status_summary(
        "readiness",
        source.readiness_result,
        "readiness_status",
        READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
        "readiness_integrity_failure",
    )
    dependency = _status_summary("dependency", source.dependency_result, "dependency_status", DEPENDENCY_SATISFIED, "dependency_integrity_failure")
    coordination = _status_summary(
        "coordination",
        source.coordination_result,
        "coordination_status",
        COORDINATION_READY_FOR_PLANNING,
        "coordination_integrity_failure",
    )
    visibility = _status_summary(
        "visibility",
        source.visibility_result,
        "aggregate_visibility_status",
        VISIBILITY_READY_FOR_PLANNING,
        "visibility_integrity_failure",
    )
    snapshot = _status_summary("snapshot", source.snapshot_result, "snapshot_status", SNAPSHOT_READY_FOR_REPLAY_PLANNING, "snapshot_integrity_failure")
    diff = _status_summary("diff_drift", source.diff_result, "diff_status", SNAPSHOT_DIFF_STABLE, "diff_drift_integrity_failure")
    audit_chain = _status_summary("audit_chain", source.audit_chain_result, "audit_chain_status", AUDIT_CHAIN_STABLE, "audit_chain_integrity_failure")
    replay = _reference_summary("replay", source.replay_integrity_references, "replay_integrity_references")
    rollback = _reference_summary("rollback", source.rollback_integrity_references, "rollback_integrity_references")
    lineage = _reference_summary("lineage", source.lineage_integrity_references, "lineage_integrity_references")
    serialization = _boolean_summary("deterministic_serialization", source.deterministic_serialization_verified, "deterministic_serialization_not_verified")
    integrity_hash = _integrity_hash(
        source,
        (governance, readiness, dependency, coordination, visibility, snapshot, diff, audit_chain, replay, rollback, lineage, serialization),
    )
    hash_stability = _hash_summary(source.expected_integrity_hash, integrity_hash)
    failures = _failure_summary(
        governance,
        readiness,
        dependency,
        coordination,
        visibility,
        snapshot,
        diff,
        audit_chain,
        replay,
        rollback,
        lineage,
        serialization,
        hash_stability,
    )
    unsupported_prohibited = tuple(sorted(set(source.unsupported_reasons + source.prohibited_reasons)))
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    limitations = _limitations(source)
    candidates = _candidate_statuses(
        source,
        governance,
        readiness,
        dependency,
        coordination,
        visibility,
        snapshot,
        diff,
        audit_chain,
        replay,
        rollback,
        lineage,
        serialization,
        hash_stability,
        manual_review,
    )
    status = classify_integrity_audit_status(candidates)
    return OrchestrationIntegrityAuditResult(
        integrity_audit_id=source.integrity_audit_id,
        integrity_audit_status=status,
        planning_only=True,
        governance_integrity=governance,
        readiness_integrity=readiness,
        dependency_integrity=dependency,
        coordination_integrity=coordination,
        visibility_integrity=visibility,
        snapshot_integrity=snapshot,
        diff_drift_integrity=diff,
        audit_chain_integrity=audit_chain,
        replay_integrity=replay,
        rollback_integrity=rollback,
        lineage_integrity=lineage,
        deterministic_serialization_integrity=serialization,
        deterministic_hash_stability=hash_stability,
        failure_classification_summary=failures,
        blocker_summary=failures,
        unsupported_prohibited_summary=unsupported_prohibited,
        limitation_summary=limitations,
        manual_review_summary=manual_review,
        deterministic_integrity_hash=integrity_hash,
        deterministic_explanation_summary=_explanation(status, failures + unsupported_prohibited + manual_review),
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
        persistent_audit_storage_enabled=False,
    )


def export_orchestration_integrity_audit_result(result: OrchestrationIntegrityAuditResult) -> dict[str, Any]:
    return export_integrity_audit_result(result)


def serialize_orchestration_integrity_audit_result(result: OrchestrationIntegrityAuditResult) -> str:
    return serialize_integrity_audit_result(result)


def hash_orchestration_integrity_audit_input(source: OrchestrationIntegrityAuditInput) -> str:
    return deterministic_hash(
        {
            "integrity_audit_id": source.integrity_audit_id,
            "governance_integrity_references": sorted(source.governance_integrity_references),
            "readiness_status": getattr(source.readiness_result, "readiness_status", None),
            "dependency_status": getattr(source.dependency_result, "dependency_status", None),
            "coordination_status": getattr(source.coordination_result, "coordination_status", None),
            "visibility_status": getattr(source.visibility_result, "aggregate_visibility_status", None),
            "snapshot_status": getattr(source.snapshot_result, "snapshot_status", None),
            "diff_status": getattr(source.diff_result, "diff_status", None),
            "audit_chain_status": getattr(source.audit_chain_result, "audit_chain_status", None),
            "replay_integrity_references": sorted(source.replay_integrity_references),
            "rollback_integrity_references": sorted(source.rollback_integrity_references),
            "lineage_integrity_references": sorted(source.lineage_integrity_references),
            "deterministic_serialization_verified": source.deterministic_serialization_verified,
            "manual_review_reasons": sorted(source.manual_review_reasons),
            "unsupported_reasons": sorted(source.unsupported_reasons),
            "prohibited_reasons": sorted(source.prohibited_reasons),
            "limitation_summary": sorted(source.limitation_summary),
        }
    )


def _reference_summary(integrity_type: str, references: tuple[str, ...], failure_label: str) -> OrchestrationIntegritySummary:
    return OrchestrationIntegritySummary(
        integrity_type=integrity_type,
        references=tuple(sorted(references)),
        failures=() if references else (failure_label,),
    )


def _status_summary(result_type: str, result: Any | None, status_field: str, stable_status: str, failure_label: str) -> OrchestrationIntegritySummary:
    if result is None:
        return OrchestrationIntegritySummary(result_type, (), (f"{result_type}_result_missing",))
    status = getattr(result, status_field)
    failures = () if status == stable_status else (f"{failure_label}:{status}",)
    return OrchestrationIntegritySummary(result_type, (status,), failures)


def _boolean_summary(integrity_type: str, value: bool, failure_label: str) -> OrchestrationIntegritySummary:
    return OrchestrationIntegritySummary(
        integrity_type=integrity_type,
        references=("verified",) if value else (),
        failures=() if value else (failure_label,),
    )


def _hash_summary(expected_hash: str | None, integrity_hash: str) -> OrchestrationIntegritySummary:
    if expected_hash is None or expected_hash == integrity_hash:
        return OrchestrationIntegritySummary("deterministic_hash", (integrity_hash,), ())
    return OrchestrationIntegritySummary("deterministic_hash", (integrity_hash,), ("integrity_hash_mismatch",))


def _failure_summary(*summaries: OrchestrationIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _candidate_statuses(
    source: OrchestrationIntegrityAuditInput,
    governance: OrchestrationIntegritySummary,
    readiness: OrchestrationIntegritySummary,
    dependency: OrchestrationIntegritySummary,
    coordination: OrchestrationIntegritySummary,
    visibility: OrchestrationIntegritySummary,
    snapshot: OrchestrationIntegritySummary,
    diff: OrchestrationIntegritySummary,
    audit_chain: OrchestrationIntegritySummary,
    replay: OrchestrationIntegritySummary,
    rollback: OrchestrationIntegritySummary,
    lineage: OrchestrationIntegritySummary,
    serialization: OrchestrationIntegritySummary,
    hash_stability: OrchestrationIntegritySummary,
    manual_review: tuple[str, ...],
) -> list[str]:
    candidates: list[str] = []
    if source.prohibited_reasons or _has_prohibited_state(source):
        candidates.append(INTEGRITY_AUDIT_PROHIBITED)
    if source.unsupported_reasons or _has_unsupported_state(source):
        candidates.append(INTEGRITY_AUDIT_UNSUPPORTED)
    if replay.failures or rollback.failures or lineage.failures or serialization.failures:
        candidates.append(INTEGRITY_AUDIT_INTEGRITY_COMPROMISED)
    if governance.failures or readiness.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE)
    if dependency.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE)
    if coordination.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE)
    if visibility.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE)
    if snapshot.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE)
    if diff.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE)
    if audit_chain.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE)
    if hash_stability.failures:
        candidates.append(INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY)
    if manual_review:
        candidates.append(INTEGRITY_AUDIT_REQUIRES_MANUAL_REVIEW)
    return candidates


def _has_prohibited_state(source: OrchestrationIntegrityAuditInput) -> bool:
    return any(
        (
            getattr(source.readiness_result, "readiness_status", None) == PROHIBITED_ORCHESTRATION_REQUEST,
            getattr(source.dependency_result, "dependency_status", None) == DEPENDENCY_PROHIBITED,
            getattr(source.coordination_result, "coordination_status", None) == COORDINATION_PROHIBITED,
            getattr(source.visibility_result, "aggregate_visibility_status", None) == VISIBILITY_PROHIBITED,
            getattr(source.snapshot_result, "snapshot_status", None) == SNAPSHOT_PROHIBITED,
            getattr(source.diff_result, "diff_status", None) == SNAPSHOT_DIFF_PROHIBITED,
            getattr(source.audit_chain_result, "audit_chain_status", None) == AUDIT_CHAIN_PROHIBITED,
        )
    )


def _has_unsupported_state(source: OrchestrationIntegrityAuditInput) -> bool:
    return any(
        (
            getattr(source.readiness_result, "readiness_status", None) == UNSUPPORTED_ORCHESTRATION_REQUEST,
            getattr(source.dependency_result, "dependency_status", None) == DEPENDENCY_UNSUPPORTED,
            getattr(source.coordination_result, "coordination_status", None) == COORDINATION_UNSUPPORTED,
            getattr(source.visibility_result, "aggregate_visibility_status", None) == VISIBILITY_UNSUPPORTED,
            getattr(source.snapshot_result, "snapshot_status", None) == SNAPSHOT_UNSUPPORTED,
            getattr(source.diff_result, "diff_status", None) == SNAPSHOT_DIFF_UNSUPPORTED,
            getattr(source.audit_chain_result, "audit_chain_status", None) == AUDIT_CHAIN_UNSUPPORTED,
        )
    )


def _limitations(source: OrchestrationIntegrityAuditInput) -> tuple[str, ...]:
    values: set[str] = set(source.limitation_summary)
    for result in (
        source.readiness_result,
        source.dependency_result,
        source.coordination_result,
        source.visibility_result,
        source.snapshot_result,
        source.diff_result,
        source.audit_chain_result,
    ):
        if result is not None and hasattr(result, "limitation_summary"):
            values.update(getattr(result, "limitation_summary"))
        if result is not None and hasattr(result, "deterministic_drift_summary"):
            values.update(getattr(result, "deterministic_drift_summary"))
    return tuple(sorted(values))


def _integrity_hash(source: OrchestrationIntegrityAuditInput, summaries: tuple[OrchestrationIntegritySummary, ...]) -> str:
    return deterministic_hash(
        {
            "integrity_audit_id": source.integrity_audit_id,
            "summaries": [
                {
                    "integrity_type": summary.integrity_type,
                    "references": sorted(summary.references),
                    "failures": sorted(summary.failures),
                }
                for summary in summaries
            ],
            "manual_review": sorted(source.manual_review_reasons),
            "unsupported": sorted(source.unsupported_reasons),
            "prohibited": sorted(source.prohibited_reasons),
            "limitations": sorted(source.limitation_summary),
        }
    )


def _explanation(status: str, entries: tuple[str, ...]) -> str:
    visible = tuple(sorted(set(entries)))
    if not visible:
        if status == "integrity_audit_stable":
            return (
                "Integrity audit is stable; no execution, dispatch, routing, mutation, audit writing, graph execution, "
                "scheduling, live replay, persistent audit storage, runtime trace capture, or production state read is authorized."
            )
        return f"Integrity audit classified as {status}; no execution behavior is authorized."
    return f"Integrity audit classified as {status}; integrity entries: {', '.join(visible)}."
