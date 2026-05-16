"""Fail-visible validation for v3.7 graph planning sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_planning_session_audit import (
    V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE,
    audit_v3_7_graph_planning_session,
)
from .v3_7_graph_planning_session_explainability import (
    V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_planning_session,
)
from .v3_7_graph_planning_session_identity import graph_planning_session_identities_are_unique
from .v3_7_graph_planning_session_models import (
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_UNSUPPORTED,
    V37GraphPlanningSession,
    hash_v3_7_graph_planning_session,
    validate_v3_7_graph_planning_session_hash_stability,
    validate_v3_7_graph_planning_session_serialization_stability,
)
from .v3_7_graph_planning_session_provenance import (
    V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_planning_session_provenance,
)
from .v3_7_graph_planning_session_replay import validate_v3_7_graph_planning_session_replay_evidence
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


V37_GRAPH_PLANNING_SESSION_VALIDATION_STABLE = "v3_7_graph_planning_session_validation_stable"
V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED = "v3_7_graph_planning_session_validation_blocked"
V37_SESSION_VALIDATION_VISIBLE_PROHIBITED = "v3_7_graph_planning_session_validation_visible_prohibited"
V37_SESSION_VALIDATION_VISIBLE_UNSUPPORTED = "v3_7_graph_planning_session_validation_visible_unsupported"
V37_SESSION_VALIDATION_VISIBLE_UNKNOWN = "v3_7_graph_planning_session_validation_visible_unknown"
V37_SESSION_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY = "v3_7_graph_planning_session_blocked_by_duplicate_identity"
V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_SNAPSHOT = "v3_7_graph_planning_session_blocked_by_missing_snapshot"
V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_GRAPH_HASH = "v3_7_graph_planning_session_blocked_by_invalid_graph_hash"
V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE = "v3_7_graph_planning_session_blocked_by_invalid_evaluation_evidence"
V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_REPLAY_EVIDENCE = "v3_7_graph_planning_session_blocked_by_missing_replay_evidence"
V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_ROLLBACK_EVIDENCE = "v3_7_graph_planning_session_blocked_by_missing_rollback_evidence"
V37_SESSION_VALIDATION_BLOCKED_BY_PROVENANCE = "v3_7_graph_planning_session_blocked_by_provenance"
V37_SESSION_VALIDATION_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_planning_session_blocked_by_explainability"
V37_SESSION_VALIDATION_BLOCKED_BY_AUDIT_TRAIL = "v3_7_graph_planning_session_blocked_by_audit_trail"
V37_SESSION_VALIDATION_BLOCKED_BY_HIDDEN_STATE = "v3_7_graph_planning_session_blocked_by_hidden_state"
V37_SESSION_VALIDATION_BLOCKED_BY_SERIALIZATION = "v3_7_graph_planning_session_blocked_by_serialization"
V37_SESSION_VALIDATION_BLOCKED_BY_HASH = "v3_7_graph_planning_session_blocked_by_hash"
V37_SESSION_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_planning_session_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphPlanningSessionValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphPlanningSessionValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    duplicate_session_identity_count: int
    missing_snapshot_reference_count: int
    invalid_graph_hash_reference_count: int
    invalid_evaluation_evidence_count: int
    missing_replay_evidence_count: int
    missing_rollback_evidence_count: int
    hidden_prohibited_state_count: int
    hidden_unsupported_state_count: int
    hidden_unknown_state_count: int
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    audit_trail_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    non_execution_guarantee_preserved: bool
    deterministic_session_hash: str
    findings: tuple[V37GraphPlanningSessionValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_planning_sessions(
    sessions: tuple[V37GraphPlanningSession, ...] | None = None,
) -> V37GraphPlanningSessionValidationResult:
    planning_sessions = sessions or (build_v3_7_graph_planning_session(),)
    primary = planning_sessions[0]
    findings: list[V37GraphPlanningSessionValidationFinding] = []
    duplicate_count = 0 if graph_planning_session_identities_are_unique(tuple(session.identity for session in planning_sessions)) else 1
    if duplicate_count:
        findings.append(
            _finding(
                V37_SESSION_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY,
                "planning_sessions",
                primary.identity.session_id,
                "duplicate planning session identity detected",
            )
        )
    for session in planning_sessions:
        _add_visibility_findings(session, findings)
        if not session.snapshots:
            findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_SNAPSHOT, "session", session.identity.session_id, "missing graph snapshot reference"))
        if any(not snapshot.graph_hash or not snapshot.graph_serialization_hash for snapshot in session.snapshots):
            findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_GRAPH_HASH, "session", session.identity.session_id, "invalid graph hash reference"))
        if any(not evidence.evaluation_trace_references or not evidence.evaluation_hash for evidence in session.evaluation_evidence):
            findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE, "session", session.identity.session_id, "invalid evaluation evidence reference"))
        if not session.replay_evidence:
            findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_REPLAY_EVIDENCE, "session", session.identity.session_id, "missing replay evidence"))
        if not session.rollback_evidence:
            findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_ROLLBACK_EVIDENCE, "session", session.identity.session_id, "missing rollback evidence"))
        for entry in session.audit_trail:
            if entry.session_status in (V37_SESSION_STATUS_PROHIBITED, V37_SESSION_STATUS_UNSUPPORTED, V37_SESSION_STATUS_UNKNOWN) and (entry.hidden or not entry.fail_visible):
                findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_HIDDEN_STATE, entry.subject_type, entry.subject_id, f"hidden {entry.session_status} state detected"))

    audit = audit_v3_7_graph_planning_session(primary)
    provenance = audit_v3_7_graph_planning_session_provenance(primary)
    explainability = explain_v3_7_graph_planning_session(primary)
    replay = validate_v3_7_graph_planning_session_replay_evidence(primary)
    serialization = validate_v3_7_graph_planning_session_serialization_stability(primary)
    hashing = validate_v3_7_graph_planning_session_hash_stability(primary)

    if audit.audit_status != V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_AUDIT_TRAIL, "session", primary.identity.session_id, "session audit trail is unstable"))
    if provenance.provenance_status != V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_PROVENANCE, "session", primary.identity.session_id, "session provenance continuity is incomplete"))
    if explainability.explainability_status != V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_EXPLAINABILITY, "session", primary.identity.session_id, "session explainability continuity is incomplete"))
    if not replay["replay_continuity_preserved"]:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_REPLAY_EVIDENCE, "session", primary.identity.session_id, "replay continuity is incomplete"))
    if not replay["rollback_continuity_preserved"]:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_ROLLBACK_EVIDENCE, "session", primary.identity.session_id, "rollback continuity is incomplete"))
    if not serialization["stable"]:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_SERIALIZATION, "session", primary.identity.session_id, "session serialization is unstable"))
    if not hashing["stable"]:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_HASH, "session", primary.identity.session_id, "session hash is unstable"))
    if not audit.non_execution_guarantee_preserved:
        findings.append(_finding(V37_SESSION_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY, "session", primary.identity.session_id, "planning session exposed execution capability"))

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphPlanningSessionValidationResult(
        validation_status=(
            V37_GRAPH_PLANNING_SESSION_VALIDATION_STABLE
            if error_count == 0
            else V37_GRAPH_PLANNING_SESSION_VALIDATION_BLOCKED
        ),
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        duplicate_session_identity_count=duplicate_count,
        missing_snapshot_reference_count=sum(1 for finding in findings if finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_SNAPSHOT),
        invalid_graph_hash_reference_count=sum(1 for finding in findings if finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_GRAPH_HASH),
        invalid_evaluation_evidence_count=sum(1 for finding in findings if finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE),
        missing_replay_evidence_count=sum(1 for finding in findings if finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_REPLAY_EVIDENCE),
        missing_rollback_evidence_count=sum(1 for finding in findings if finding.status == V37_SESSION_VALIDATION_BLOCKED_BY_MISSING_ROLLBACK_EVIDENCE),
        hidden_prohibited_state_count=_hidden_state_count(planning_sessions, V37_SESSION_STATUS_PROHIBITED),
        hidden_unsupported_state_count=_hidden_state_count(planning_sessions, V37_SESSION_STATUS_UNSUPPORTED),
        hidden_unknown_state_count=_hidden_state_count(planning_sessions, V37_SESSION_STATUS_UNKNOWN),
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=(
            explainability.explainability_status == V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE
        ),
        audit_trail_continuity_preserved=audit.audit_status == V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=replay["rollback_continuity_preserved"],
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=audit.non_execution_guarantee_preserved,
        deterministic_session_hash=hash_v3_7_graph_planning_session(primary),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(
        result,
        deterministic_validation_hash=hash_v3_7_graph_planning_session_validation_result(result),
    )


def export_v3_7_graph_planning_session_validation_finding(
    finding: V37GraphPlanningSessionValidationFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_planning_session_validation_result(
    result: V37GraphPlanningSessionValidationResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_planning_session_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_planning_session_validation_result(
    result: V37GraphPlanningSessionValidationResult,
) -> str:
    return stable_serialize(export_v3_7_graph_planning_session_validation_result(result))


def hash_v3_7_graph_planning_session_validation_result(
    result: V37GraphPlanningSessionValidationResult,
) -> str:
    data = export_v3_7_graph_planning_session_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    session: V37GraphPlanningSession,
    findings: list[V37GraphPlanningSessionValidationFinding],
) -> None:
    status_map = {
        V37_SESSION_STATUS_PROHIBITED: V37_SESSION_VALIDATION_VISIBLE_PROHIBITED,
        V37_SESSION_STATUS_UNSUPPORTED: V37_SESSION_VALIDATION_VISIBLE_UNSUPPORTED,
        V37_SESSION_STATUS_UNKNOWN: V37_SESSION_VALIDATION_VISIBLE_UNKNOWN,
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


def _hidden_state_count(sessions: tuple[V37GraphPlanningSession, ...], status: str) -> int:
    return sum(
        1
        for session in sessions
        for entry in session.audit_trail
        if entry.session_status == status and (entry.hidden or not entry.fail_visible)
    )


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphPlanningSessionValidationFinding:
    return V37GraphPlanningSessionValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
