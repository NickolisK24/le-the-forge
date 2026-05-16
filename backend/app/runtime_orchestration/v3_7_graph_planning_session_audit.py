"""Deterministic audit infrastructure for v3.7 graph planning sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_planning_session_identity import graph_planning_session_identity_key
from .v3_7_graph_planning_session_models import (
    V37_SESSION_STATUS_BLOCKED,
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_UNSUPPORTED,
    V37GraphPlanningSession,
)
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE = "v3_7_graph_planning_session_audit_stable"
V37_GRAPH_PLANNING_SESSION_AUDIT_FAILED = "v3_7_graph_planning_session_audit_failed"
V37_SESSION_AUDIT_VISIBLE_BLOCKED = "v3_7_graph_planning_session_visible_blocked"
V37_SESSION_AUDIT_VISIBLE_UNSUPPORTED = "v3_7_graph_planning_session_visible_unsupported"
V37_SESSION_AUDIT_VISIBLE_PROHIBITED = "v3_7_graph_planning_session_visible_prohibited"
V37_SESSION_AUDIT_VISIBLE_UNKNOWN = "v3_7_graph_planning_session_visible_unknown"
V37_SESSION_AUDIT_BLOCKED_BY_IDENTITY = "v3_7_graph_planning_session_audit_blocked_by_identity"
V37_SESSION_AUDIT_BLOCKED_BY_SNAPSHOT = "v3_7_graph_planning_session_audit_blocked_by_snapshot"
V37_SESSION_AUDIT_BLOCKED_BY_GRAPH_HASH = "v3_7_graph_planning_session_audit_blocked_by_graph_hash"
V37_SESSION_AUDIT_BLOCKED_BY_EVALUATION = "v3_7_graph_planning_session_audit_blocked_by_evaluation"
V37_SESSION_AUDIT_BLOCKED_BY_REPLAY = "v3_7_graph_planning_session_audit_blocked_by_replay"
V37_SESSION_AUDIT_BLOCKED_BY_ROLLBACK = "v3_7_graph_planning_session_audit_blocked_by_rollback"
V37_SESSION_AUDIT_BLOCKED_BY_PROVENANCE = "v3_7_graph_planning_session_audit_blocked_by_provenance"
V37_SESSION_AUDIT_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_planning_session_audit_blocked_by_explainability"
V37_SESSION_AUDIT_BLOCKED_BY_GOVERNANCE = "v3_7_graph_planning_session_audit_blocked_by_governance"
V37_SESSION_AUDIT_BLOCKED_BY_COMPATIBILITY = "v3_7_graph_planning_session_audit_blocked_by_compatibility"
V37_SESSION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY = "v3_7_graph_planning_session_audit_blocked_by_finding_visibility"
V37_SESSION_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_planning_session_audit_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphPlanningSessionAuditFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphPlanningSessionAuditResult:
    audit_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    session_identity_stable: bool
    snapshot_continuity_preserved: bool
    graph_hash_continuity_preserved: bool
    evaluation_evidence_continuity_preserved: bool
    replay_evidence_continuity_preserved: bool
    rollback_evidence_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    fail_visible_finding_preservation: bool
    non_execution_guarantee_preserved: bool
    deterministic_audit_hash: str
    findings: tuple[V37GraphPlanningSessionAuditFinding, ...]


def audit_v3_7_graph_planning_session(
    session: V37GraphPlanningSession | None = None,
) -> V37GraphPlanningSessionAuditResult:
    planning_session = session or build_v3_7_graph_planning_session()
    findings: list[V37GraphPlanningSessionAuditFinding] = []
    _add_visibility_findings(planning_session, findings)

    identity_ok = planning_session.identity.stable_identity_key == graph_planning_session_identity_key(planning_session.identity)
    _append_error_if_false(findings, identity_ok, V37_SESSION_AUDIT_BLOCKED_BY_IDENTITY, "session", planning_session.identity.session_id, "planning session identity is unstable")
    snapshot_ok = bool(planning_session.snapshots) and all(snapshot.session_id == planning_session.identity.session_id for snapshot in planning_session.snapshots)
    _append_error_if_false(findings, snapshot_ok, V37_SESSION_AUDIT_BLOCKED_BY_SNAPSHOT, "session", planning_session.identity.session_id, "snapshot continuity is incomplete")
    graph_hash_ok = all(snapshot.graph_hash and snapshot.graph_serialization_hash for snapshot in planning_session.snapshots)
    _append_error_if_false(findings, graph_hash_ok, V37_SESSION_AUDIT_BLOCKED_BY_GRAPH_HASH, "session", planning_session.identity.session_id, "graph hash continuity is incomplete")
    evaluation_ok = bool(planning_session.evaluation_evidence) and all(
        evidence.evaluation_trace_references and evidence.evaluation_hash and evidence.evaluation_validation_hash
        for evidence in planning_session.evaluation_evidence
    )
    _append_error_if_false(findings, evaluation_ok, V37_SESSION_AUDIT_BLOCKED_BY_EVALUATION, "session", planning_session.identity.session_id, "evaluation evidence continuity is incomplete")
    replay_ok = bool(planning_session.replay_evidence) and all(
        evidence.non_executable_replay_evidence
        and not evidence.runtime_replay
        and evidence.replay_packet_references
        and evidence.continuity_hashes
        for evidence in planning_session.replay_evidence
    )
    _append_error_if_false(findings, replay_ok, V37_SESSION_AUDIT_BLOCKED_BY_REPLAY, "session", planning_session.identity.session_id, "replay evidence continuity is incomplete")
    rollback_ok = bool(planning_session.rollback_evidence) and all(
        evidence.rollback_safe and evidence.rollback_reference_ids and evidence.continuity_hashes
        for evidence in planning_session.rollback_evidence
    )
    _append_error_if_false(findings, rollback_ok, V37_SESSION_AUDIT_BLOCKED_BY_ROLLBACK, "session", planning_session.identity.session_id, "rollback evidence continuity is incomplete")
    provenance_ok = _provenance_continuity_preserved(planning_session)
    _append_error_if_false(findings, provenance_ok, V37_SESSION_AUDIT_BLOCKED_BY_PROVENANCE, "session", planning_session.identity.session_id, "provenance continuity is incomplete")
    explainability_ok = planning_session.explainability_reference_ids and all(
        snapshot.explainability_references for snapshot in planning_session.snapshots
    )
    _append_error_if_false(findings, bool(explainability_ok), V37_SESSION_AUDIT_BLOCKED_BY_EXPLAINABILITY, "session", planning_session.identity.session_id, "explainability continuity is incomplete")
    governance_ok = all(snapshot.governance_evidence_references for snapshot in planning_session.snapshots)
    _append_error_if_false(findings, governance_ok, V37_SESSION_AUDIT_BLOCKED_BY_GOVERNANCE, "session", planning_session.identity.session_id, "governance continuity is incomplete")
    compatibility_ok = all(snapshot.compatibility_evidence_references for snapshot in planning_session.snapshots)
    _append_error_if_false(findings, compatibility_ok, V37_SESSION_AUDIT_BLOCKED_BY_COMPATIBILITY, "session", planning_session.identity.session_id, "compatibility continuity is incomplete")
    fail_visible_ok = all(entry.fail_visible and not entry.hidden for entry in planning_session.audit_trail)
    _append_error_if_false(findings, fail_visible_ok, V37_SESSION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY, "session", planning_session.identity.session_id, "audit trail contains hidden or non-visible finding")
    non_execution_ok = _non_execution_guarantee_preserved(planning_session)
    _append_error_if_false(findings, non_execution_ok, V37_SESSION_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY, "session", planning_session.identity.session_id, "planning session exposed execution capability")

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphPlanningSessionAuditResult(
        audit_status=V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE if error_count == 0 else V37_GRAPH_PLANNING_SESSION_AUDIT_FAILED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        session_identity_stable=identity_ok,
        snapshot_continuity_preserved=snapshot_ok,
        graph_hash_continuity_preserved=graph_hash_ok,
        evaluation_evidence_continuity_preserved=evaluation_ok,
        replay_evidence_continuity_preserved=replay_ok,
        rollback_evidence_continuity_preserved=rollback_ok,
        provenance_continuity_preserved=provenance_ok,
        explainability_continuity_preserved=bool(explainability_ok),
        governance_continuity_preserved=governance_ok,
        compatibility_continuity_preserved=compatibility_ok,
        fail_visible_finding_preservation=fail_visible_ok,
        non_execution_guarantee_preserved=non_execution_ok,
        deterministic_audit_hash="",
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_audit_hash=hash_v3_7_graph_planning_session_audit_result(result))


def export_v3_7_graph_planning_session_audit_finding(
    finding: V37GraphPlanningSessionAuditFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_planning_session_audit_result(
    result: V37GraphPlanningSessionAuditResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_planning_session_audit_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_planning_session_audit_result(
    result: V37GraphPlanningSessionAuditResult,
) -> str:
    return stable_serialize(export_v3_7_graph_planning_session_audit_result(result))


def hash_v3_7_graph_planning_session_audit_result(
    result: V37GraphPlanningSessionAuditResult,
) -> str:
    data = export_v3_7_graph_planning_session_audit_result(result)
    data.pop("deterministic_audit_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    session: V37GraphPlanningSession,
    findings: list[V37GraphPlanningSessionAuditFinding],
) -> None:
    status_map = {
        V37_SESSION_STATUS_BLOCKED: V37_SESSION_AUDIT_VISIBLE_BLOCKED,
        V37_SESSION_STATUS_UNSUPPORTED: V37_SESSION_AUDIT_VISIBLE_UNSUPPORTED,
        V37_SESSION_STATUS_PROHIBITED: V37_SESSION_AUDIT_VISIBLE_PROHIBITED,
        V37_SESSION_STATUS_UNKNOWN: V37_SESSION_AUDIT_VISIBLE_UNKNOWN,
    }
    for entry in session.audit_trail:
        status = status_map.get(entry.session_status)
        if status:
            findings.append(
                _finding(
                    status,
                    entry.subject_type,
                    entry.subject_id,
                    f"{entry.session_status} session state remains fail-visible",
                    severity="visibility",
                )
            )


def _append_error_if_false(
    findings: list[V37GraphPlanningSessionAuditFinding],
    condition: bool,
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
) -> None:
    if not condition:
        findings.append(_finding(status, subject_type, subject_id, message))


def _provenance_continuity_preserved(session: V37GraphPlanningSession) -> bool:
    return (
        bool(session.provenance.replay_lineage_references)
        and bool(session.provenance.rollback_lineage_references)
        and all(snapshot.provenance_references and snapshot.provenance.replay_lineage_references for snapshot in session.snapshots)
        and all(evidence.provenance_references for evidence in session.evaluation_evidence)
        and all(evidence.provenance_references for evidence in session.replay_evidence)
        and all(evidence.provenance_references for evidence in session.rollback_evidence)
    )


def _non_execution_guarantee_preserved(session: V37GraphPlanningSession) -> bool:
    return all(
        (
            session.planning_sessions_are_non_executable,
            session.evidence_container_only,
            session.session_replay_evidence_is_not_runtime_replay,
            session.snapshots_do_not_imply_execution_state,
            session.audit_trails_do_not_imply_runtime_history,
            session.session_statuses_do_not_authorize_orchestration,
            session.graph_planning_sessions_do_not_enable_routing_scheduling_dispatch,
            not session.graph_execution_enabled,
            not session.session_execution_enabled,
            not session.runtime_orchestration_enabled,
            not session.routing_enabled,
            not session.scheduling_enabled,
            not session.dispatch_enabled,
            not session.graph_traversal_execution_enabled,
            not session.path_selection_enabled,
            not session.graph_optimization_enabled,
            not session.recommendation_enabled,
            not session.autonomous_orchestration_enabled,
            not session.runtime_mutation_enabled,
            not session.persistent_runtime_writes_enabled,
            not session.background_orchestration_processing_enabled,
            not session.execution_capable_session_state_enabled,
            not session.session_driven_orchestration_behavior_enabled,
            all(not snapshot.snapshot_is_executable and not snapshot.execution_state for snapshot in session.snapshots),
            all(evidence.non_executable_replay_evidence and not evidence.runtime_replay for evidence in session.replay_evidence),
        )
    )


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphPlanningSessionAuditFinding:
    return V37GraphPlanningSessionAuditFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
