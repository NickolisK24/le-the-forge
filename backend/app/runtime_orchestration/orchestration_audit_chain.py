"""Planning-only orchestration audit-chain construction for v3.5 Phase 8."""

from __future__ import annotations

from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .orchestration_audit_chain_models import (
    OrchestrationAuditChainInput,
    OrchestrationAuditContinuitySummary,
)
from .orchestration_audit_chain_report_models import (
    OrchestrationAuditChainResult,
    export_audit_chain_result,
    serialize_audit_chain_result,
)
from .orchestration_audit_chain_status import (
    AUDIT_CHAIN_BLOCKED_BY_HASH_INSTABILITY,
    AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT,
    AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP,
    AUDIT_CHAIN_INTEGRITY_COMPROMISED,
    AUDIT_CHAIN_PROHIBITED,
    AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW,
    AUDIT_CHAIN_UNSUPPORTED,
    classify_audit_chain_status,
)
from .orchestration_planning_snapshot import generate_orchestration_planning_snapshot
from .orchestration_planning_snapshot_status import SNAPSHOT_PROHIBITED, SNAPSHOT_UNSUPPORTED
from .orchestration_snapshot_diff_analysis import analyze_orchestration_snapshot_diff
from .orchestration_snapshot_diff_models import OrchestrationSnapshotDiffInput
from .orchestration_snapshot_diff_status import SNAPSHOT_DIFF_PROHIBITED, SNAPSHOT_DIFF_UNSUPPORTED


DEFAULT_AUDIT_CHAIN_LIMITATIONS: tuple[str, ...] = (
    "audit-chain construction is declarative and planning-only",
    "audit-chain construction does not persist audit state",
    "audit-chain construction does not capture runtime lineage or traces",
    "audit-chain construction does not read production state",
)


def default_orchestration_audit_chain_input() -> OrchestrationAuditChainInput:
    source = generate_orchestration_planning_snapshot()
    target = generate_orchestration_planning_snapshot()
    diff = analyze_orchestration_snapshot_diff(
        OrchestrationSnapshotDiffInput(
            diff_analysis_id="snapshot-diff-v3-5-phase-7",
            source_snapshot=source,
            target_snapshot=target,
            replay_stability_verified=True,
            deterministic_serialization_verified=True,
            expected_source_snapshot_hash=source.deterministic_snapshot_hash,
            expected_target_snapshot_hash=target.deterministic_snapshot_hash,
            manual_review_reasons=(),
            limitation_summary=(
                "snapshot diff analysis is declarative and planning-only",
                "snapshot diff analysis does not authorize orchestration execution",
                "snapshot diff analysis does not perform live replay execution",
                "snapshot diff analysis does not capture runtime traces or read production state",
            ),
        )
    )
    return OrchestrationAuditChainInput(
        audit_chain_id="audit-chain-v3-5-phase-8",
        chain_root_snapshot_id=source.snapshot_id,
        snapshot_sequence=(source, target),
        diff_analysis_sequence=(diff,),
        chain_lineage_references=("lineage-v3-5-phase-8",),
        replay_continuity_references=("replay-continuity-v3-5-phase-8",),
        rollback_continuity_references=("rollback-continuity-v3-5-phase-8",),
        governance_continuity_references=("governance-continuity-v3-5-phase-8",),
        blocker_continuity_references=("blocker-continuity-v3-5-phase-8",),
        compatibility_continuity_references=("compatibility-continuity-v3-5-phase-8",),
        environment_continuity_references=("environment-continuity-v3-5-phase-8",),
        deterministic_serialization_verified=True,
        expected_audit_chain_hash=None,
        manual_review_reasons=(),
        unsupported_reasons=(),
        prohibited_reasons=(),
        limitation_summary=DEFAULT_AUDIT_CHAIN_LIMITATIONS,
    )


def build_orchestration_audit_chain(
    chain_input: OrchestrationAuditChainInput | None = None,
) -> OrchestrationAuditChainResult:
    source = chain_input or default_orchestration_audit_chain_input()
    snapshot_sequence = tuple(snapshot.snapshot_id for snapshot in source.snapshot_sequence if snapshot is not None)
    diff_sequence = tuple(diff.diff_analysis_id for diff in source.diff_analysis_sequence if diff is not None)
    snapshot_gaps = _snapshot_gaps(source)
    diff_gaps = _diff_gaps(source)
    lineage = _continuity("lineage", source.chain_lineage_references, ("lineage_continuity_references",))
    replay = _continuity("replay", source.replay_continuity_references, ("replay_continuity_references",))
    rollback = _continuity("rollback", source.rollback_continuity_references, ("rollback_continuity_references",))
    governance = _continuity("governance", source.governance_continuity_references, ("governance_continuity_references",))
    blocker = _continuity("blocker", source.blocker_continuity_references, ("blocker_continuity_references",))
    compatibility = _continuity("compatibility", source.compatibility_continuity_references, ("compatibility_continuity_references",))
    environment = _continuity("environment", source.environment_continuity_references, ("environment_continuity_references",))
    integrity = _integrity_summary(source, snapshot_gaps, diff_gaps)
    lineage_gaps = _combine(lineage.gaps, governance.gaps)
    replay_gaps = replay.gaps
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    limitations = _limitations(source)
    audit_hash = _audit_chain_hash(source, snapshot_sequence, diff_sequence, lineage, replay, rollback, governance, blocker, compatibility, environment, integrity)
    hash_instability = _hash_instability(source, audit_hash)
    candidates = _candidate_statuses(
        source,
        snapshot_gaps,
        diff_gaps,
        lineage_gaps,
        replay_gaps,
        hash_instability,
        integrity,
        manual_review,
    )
    status = classify_audit_chain_status(candidates)
    return OrchestrationAuditChainResult(
        audit_chain_id=source.audit_chain_id,
        chain_root_snapshot_id=source.chain_root_snapshot_id,
        audit_chain_status=status,
        planning_only=True,
        chain_snapshot_sequence=snapshot_sequence,
        chain_diff_analysis_sequence=diff_sequence,
        lineage_continuity=lineage,
        replay_continuity=replay,
        rollback_continuity=rollback,
        governance_continuity=governance,
        blocker_continuity=blocker,
        compatibility_continuity=compatibility,
        environment_continuity=environment,
        lineage_gap_summary=lineage_gaps,
        replay_gap_summary=replay_gaps,
        snapshot_gap_summary=snapshot_gaps,
        diff_analysis_gap_summary=diff_gaps,
        integrity_summary=tuple(sorted(set(integrity + hash_instability))),
        manual_review_summary=manual_review,
        limitation_summary=limitations,
        deterministic_audit_chain_hash=audit_hash,
        deterministic_explanation_summary=_explanation(status, snapshot_gaps + diff_gaps + lineage_gaps + replay_gaps + integrity + hash_instability + manual_review),
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


def export_orchestration_audit_chain_result(result: OrchestrationAuditChainResult) -> dict[str, Any]:
    return export_audit_chain_result(result)


def serialize_orchestration_audit_chain_result(result: OrchestrationAuditChainResult) -> str:
    return serialize_audit_chain_result(result)


def hash_orchestration_audit_chain_input(source: OrchestrationAuditChainInput) -> str:
    return deterministic_hash(
        {
            "audit_chain_id": source.audit_chain_id,
            "chain_root_snapshot_id": source.chain_root_snapshot_id,
            "snapshot_hashes": sorted(snapshot.deterministic_snapshot_hash for snapshot in source.snapshot_sequence if snapshot is not None),
            "diff_hashes": sorted(diff.source_snapshot_hash + diff.target_snapshot_hash for diff in source.diff_analysis_sequence if diff is not None),
            "chain_lineage_references": sorted(source.chain_lineage_references),
            "replay_continuity_references": sorted(source.replay_continuity_references),
            "rollback_continuity_references": sorted(source.rollback_continuity_references),
            "governance_continuity_references": sorted(source.governance_continuity_references),
            "blocker_continuity_references": sorted(source.blocker_continuity_references),
            "compatibility_continuity_references": sorted(source.compatibility_continuity_references),
            "environment_continuity_references": sorted(source.environment_continuity_references),
            "deterministic_serialization_verified": source.deterministic_serialization_verified,
            "manual_review_reasons": sorted(source.manual_review_reasons),
            "unsupported_reasons": sorted(source.unsupported_reasons),
            "prohibited_reasons": sorted(source.prohibited_reasons),
            "limitation_summary": sorted(source.limitation_summary),
        }
    )


def _snapshot_gaps(source: OrchestrationAuditChainInput) -> tuple[str, ...]:
    gaps: set[str] = set()
    if not source.snapshot_sequence:
        gaps.add("snapshot_sequence")
    for index, snapshot in enumerate(source.snapshot_sequence):
        if snapshot is None:
            gaps.add(f"snapshot_sequence[{index}]")
    if source.chain_root_snapshot_id not in {snapshot.snapshot_id for snapshot in source.snapshot_sequence if snapshot is not None}:
        gaps.add("chain_root_snapshot_id")
    return tuple(sorted(gaps))


def _diff_gaps(source: OrchestrationAuditChainInput) -> tuple[str, ...]:
    gaps: set[str] = set()
    expected = max(len(source.snapshot_sequence) - 1, 0)
    if len(source.diff_analysis_sequence) < expected:
        gaps.add("diff_analysis_sequence")
    for index, diff in enumerate(source.diff_analysis_sequence):
        if diff is None:
            gaps.add(f"diff_analysis_sequence[{index}]")
    return tuple(sorted(gaps))


def _continuity(continuity_type: str, references: tuple[str, ...], required: tuple[str, ...]) -> OrchestrationAuditContinuitySummary:
    gaps = tuple(item for item in required if not references)
    return OrchestrationAuditContinuitySummary(
        continuity_type=continuity_type,
        references=tuple(sorted(references)),
        gaps=tuple(sorted(gaps)),
    )


def _integrity_summary(source: OrchestrationAuditChainInput, snapshot_gaps: tuple[str, ...], diff_gaps: tuple[str, ...]) -> tuple[str, ...]:
    issues: set[str] = set()
    if not source.deterministic_serialization_verified:
        issues.add("deterministic_serialization_not_verified")
    if not source.blocker_continuity_references:
        issues.add("blocker_continuity_gap")
    if not source.compatibility_continuity_references:
        issues.add("compatibility_continuity_gap")
    if not source.environment_continuity_references:
        issues.add("environment_continuity_gap")
    if not source.rollback_continuity_references:
        issues.add("rollback_continuity_gap")
    snapshots = [snapshot for snapshot in source.snapshot_sequence if snapshot is not None]
    diffs = [diff for diff in source.diff_analysis_sequence if diff is not None]
    for left, right, diff in zip(snapshots, snapshots[1:], diffs):
        if diff.source_snapshot_hash != left.deterministic_snapshot_hash:
            issues.add("diff_source_snapshot_hash_mismatch")
        if diff.target_snapshot_hash != right.deterministic_snapshot_hash:
            issues.add("diff_target_snapshot_hash_mismatch")
    return tuple(sorted(issues))


def _hash_instability(source: OrchestrationAuditChainInput, audit_hash: str) -> tuple[str, ...]:
    if source.expected_audit_chain_hash is not None and source.expected_audit_chain_hash != audit_hash:
        return ("audit_chain_hash_mismatch",)
    return ()


def _candidate_statuses(
    source: OrchestrationAuditChainInput,
    snapshot_gaps: tuple[str, ...],
    diff_gaps: tuple[str, ...],
    lineage_gaps: tuple[str, ...],
    replay_gaps: tuple[str, ...],
    hash_instability: tuple[str, ...],
    integrity: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> list[str]:
    candidates: list[str] = []
    if source.prohibited_reasons or _has_prohibited_state(source):
        candidates.append(AUDIT_CHAIN_PROHIBITED)
    if source.unsupported_reasons or _has_unsupported_state(source):
        candidates.append(AUDIT_CHAIN_UNSUPPORTED)
    if integrity:
        candidates.append(AUDIT_CHAIN_INTEGRITY_COMPROMISED)
    if snapshot_gaps:
        candidates.append(AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT)
    if diff_gaps:
        candidates.append(AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS)
    if lineage_gaps:
        candidates.append(AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP)
    if replay_gaps:
        candidates.append(AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP)
    if hash_instability:
        candidates.append(AUDIT_CHAIN_BLOCKED_BY_HASH_INSTABILITY)
    if manual_review:
        candidates.append(AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW)
    return candidates


def _has_prohibited_state(source: OrchestrationAuditChainInput) -> bool:
    return any(
        (snapshot is not None and snapshot.snapshot_status == SNAPSHOT_PROHIBITED)
        for snapshot in source.snapshot_sequence
    ) or any((diff is not None and diff.diff_status == SNAPSHOT_DIFF_PROHIBITED) for diff in source.diff_analysis_sequence)


def _has_unsupported_state(source: OrchestrationAuditChainInput) -> bool:
    return any(
        (snapshot is not None and snapshot.snapshot_status == SNAPSHOT_UNSUPPORTED)
        for snapshot in source.snapshot_sequence
    ) or any((diff is not None and diff.diff_status == SNAPSHOT_DIFF_UNSUPPORTED) for diff in source.diff_analysis_sequence)


def _combine(*groups: tuple[str, ...]) -> tuple[str, ...]:
    values: set[str] = set()
    for group in groups:
        values.update(group)
    return tuple(sorted(values))


def _limitations(source: OrchestrationAuditChainInput) -> tuple[str, ...]:
    values: set[str] = set(source.limitation_summary)
    for snapshot in source.snapshot_sequence:
        if snapshot is not None:
            values.update(snapshot.limitation_summary)
    for diff in source.diff_analysis_sequence:
        if diff is not None:
            values.update(diff.deterministic_drift_summary)
    return tuple(sorted(values))


def _audit_chain_hash(
    source: OrchestrationAuditChainInput,
    snapshot_sequence: tuple[str, ...],
    diff_sequence: tuple[str, ...],
    lineage: OrchestrationAuditContinuitySummary,
    replay: OrchestrationAuditContinuitySummary,
    rollback: OrchestrationAuditContinuitySummary,
    governance: OrchestrationAuditContinuitySummary,
    blocker: OrchestrationAuditContinuitySummary,
    compatibility: OrchestrationAuditContinuitySummary,
    environment: OrchestrationAuditContinuitySummary,
    integrity: tuple[str, ...],
) -> str:
    return deterministic_hash(
        {
            "audit_chain_id": source.audit_chain_id,
            "chain_root_snapshot_id": source.chain_root_snapshot_id,
            "snapshot_sequence": sorted(snapshot_sequence),
            "snapshot_hashes": sorted(snapshot.deterministic_snapshot_hash for snapshot in source.snapshot_sequence if snapshot is not None),
            "diff_sequence": sorted(diff_sequence),
            "diff_statuses": sorted(diff.diff_status for diff in source.diff_analysis_sequence if diff is not None),
            "lineage": sorted(lineage.references + lineage.gaps),
            "replay": sorted(replay.references + replay.gaps),
            "rollback": sorted(rollback.references + rollback.gaps),
            "governance": sorted(governance.references + governance.gaps),
            "blocker": sorted(blocker.references + blocker.gaps),
            "compatibility": sorted(compatibility.references + compatibility.gaps),
            "environment": sorted(environment.references + environment.gaps),
            "integrity": sorted(integrity),
            "manual_review": sorted(source.manual_review_reasons),
            "unsupported": sorted(source.unsupported_reasons),
            "prohibited": sorted(source.prohibited_reasons),
        }
    )


def _explanation(status: str, entries: tuple[str, ...]) -> str:
    visible = tuple(sorted(set(entries)))
    if not visible:
        if status == "audit_chain_stable":
            return (
                "Audit chain is stable; no execution, dispatch, routing, mutation, audit writing, graph execution, "
                "scheduling, live replay, persistent audit storage, runtime trace capture, or production state read is authorized."
            )
        return f"Audit chain classified as {status}; no execution behavior is authorized."
    return f"Audit chain classified as {status}; continuity entries: {', '.join(visible)}."
