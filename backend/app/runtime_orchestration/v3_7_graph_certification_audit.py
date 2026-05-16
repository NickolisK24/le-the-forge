"""Deterministic audit infrastructure for v3.7 planning continuity certification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_certification_evidence import build_v3_7_graph_planning_continuity_certification
from .v3_7_graph_certification_explainability import (
    V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_certification,
)
from .v3_7_graph_certification_models import (
    V37_CERTIFICATION_FINDING_BLOCKED,
    V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED,
    V37_CERTIFICATION_FINDING_SCOPE_INCOMPLETE,
    V37_CERTIFICATION_FINDING_WARNING,
    V37GraphPlanningContinuityCertification,
    validate_v3_7_graph_certification_hash_stability,
    validate_v3_7_graph_certification_serialization_stability,
)
from .v3_7_graph_certification_provenance import (
    V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_certification_provenance,
)
from .v3_7_graph_certification_replay import validate_v3_7_graph_certification_replay_evidence
from .v3_7_graph_certification_scope import (
    certification_scope_is_complete,
    graph_certification_identity_key,
    graph_certification_scope_identity_key,
)


V37_GRAPH_CERTIFICATION_AUDIT_STABLE = "v3_7_graph_certification_audit_stable"
V37_GRAPH_CERTIFICATION_AUDIT_FAILED = "v3_7_graph_certification_audit_failed"
V37_CERTIFICATION_AUDIT_VISIBLE_BLOCKED = "v3_7_graph_certification_visible_blocked"
V37_CERTIFICATION_AUDIT_VISIBLE_WARNING = "v3_7_graph_certification_visible_warning"
V37_CERTIFICATION_AUDIT_VISIBLE_SCOPE_INCOMPLETE = "v3_7_graph_certification_visible_scope_incomplete"
V37_CERTIFICATION_AUDIT_VISIBLE_EXECUTION_BOUNDARY = "v3_7_graph_certification_visible_execution_boundary"
V37_CERTIFICATION_AUDIT_VISIBLE_HIDDEN_RISK = "v3_7_graph_certification_visible_hidden_risk"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_CERTIFICATION_IDENTITY = "v3_7_graph_certification_audit_blocked_by_certification_identity"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_SCOPE_IDENTITY = "v3_7_graph_certification_audit_blocked_by_scope_identity"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_SCOPE = "v3_7_graph_certification_audit_blocked_by_scope"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_EVIDENCE_SOURCE = "v3_7_graph_certification_audit_blocked_by_evidence_source"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_REPLAY = "v3_7_graph_certification_audit_blocked_by_replay"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_ROLLBACK = "v3_7_graph_certification_audit_blocked_by_rollback"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_PROVENANCE = "v3_7_graph_certification_audit_blocked_by_provenance"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_certification_audit_blocked_by_explainability"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY = "v3_7_graph_certification_audit_blocked_by_finding_visibility"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY = "v3_7_graph_certification_audit_blocked_by_execution_boundary"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_SERIALIZATION = "v3_7_graph_certification_audit_blocked_by_serialization"
V37_CERTIFICATION_AUDIT_BLOCKED_BY_HASH = "v3_7_graph_certification_audit_blocked_by_hash"


@dataclass(frozen=True)
class V37GraphCertificationAuditFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphCertificationAuditResult:
    audit_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    certification_identity_continuity_preserved: bool
    certification_scope_continuity_preserved: bool
    evidence_source_continuity_preserved: bool
    graph_continuity_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    evaluation_continuity_preserved: bool
    session_continuity_preserved: bool
    scenario_continuity_preserved: bool
    aggregation_continuity_preserved: bool
    integrity_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    execution_boundary_continuity_preserved: bool
    fail_visible_finding_preservation: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    deterministic_audit_hash: str
    findings: tuple[V37GraphCertificationAuditFinding, ...]


def audit_v3_7_graph_certification(
    certification: V37GraphPlanningContinuityCertification | None = None,
) -> V37GraphCertificationAuditResult:
    result = certification or build_v3_7_graph_planning_continuity_certification()
    findings: list[V37GraphCertificationAuditFinding] = []
    _add_visibility_findings(result, findings)
    reference_types = {reference.reference_type for reference in result.scope.references}
    identity_ok = result.identity.stable_identity_key == graph_certification_identity_key(result.identity)
    scope_identity_ok = result.scope.identity.stable_identity_key == graph_certification_scope_identity_key(result.scope.identity)
    scope_ok = certification_scope_is_complete(result.scope)
    required = {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
        "aggregation",
        "integrity",
    }
    evidence_source_ok = required.issubset(reference_types)
    replay = validate_v3_7_graph_certification_replay_evidence(result)
    provenance = audit_v3_7_graph_certification_provenance(result)
    explainability = explain_v3_7_graph_certification(result)
    serialization = validate_v3_7_graph_certification_serialization_stability(result)
    hashing = validate_v3_7_graph_certification_hash_stability(result)
    finding_visibility_ok = all(finding.fail_visible and not finding.hidden for finding in result.findings)
    execution_boundary_ok = _execution_boundary_preserved(result)
    _append_error_if_false(findings, identity_ok, V37_CERTIFICATION_AUDIT_BLOCKED_BY_CERTIFICATION_IDENTITY, "certification", result.identity.certification_id, "certification identity continuity is unstable")
    _append_error_if_false(findings, scope_identity_ok, V37_CERTIFICATION_AUDIT_BLOCKED_BY_SCOPE_IDENTITY, "scope", result.scope.identity.scope_id, "scope identity continuity is unstable")
    _append_error_if_false(findings, scope_ok, V37_CERTIFICATION_AUDIT_BLOCKED_BY_SCOPE, "scope", result.scope.identity.scope_id, "certification scope is incomplete")
    _append_error_if_false(findings, evidence_source_ok, V37_CERTIFICATION_AUDIT_BLOCKED_BY_EVIDENCE_SOURCE, "certification", result.identity.certification_id, "evidence-source continuity is incomplete")
    _append_error_if_false(findings, replay["replay_continuity_preserved"], V37_CERTIFICATION_AUDIT_BLOCKED_BY_REPLAY, "certification", result.identity.certification_id, "replay continuity is incomplete")
    _append_error_if_false(findings, replay["rollback_continuity_preserved"], V37_CERTIFICATION_AUDIT_BLOCKED_BY_ROLLBACK, "certification", result.identity.certification_id, "rollback continuity is incomplete")
    _append_error_if_false(findings, provenance.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED, V37_CERTIFICATION_AUDIT_BLOCKED_BY_PROVENANCE, "certification", result.identity.certification_id, "provenance continuity is incomplete")
    _append_error_if_false(findings, explainability.explainability_status == V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE, V37_CERTIFICATION_AUDIT_BLOCKED_BY_EXPLAINABILITY, "certification", result.identity.certification_id, "explainability continuity is incomplete")
    _append_error_if_false(findings, finding_visibility_ok, V37_CERTIFICATION_AUDIT_BLOCKED_BY_FINDING_VISIBILITY, "certification", result.identity.certification_id, "certification finding visibility is incomplete")
    _append_error_if_false(findings, execution_boundary_ok, V37_CERTIFICATION_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY, "certification", result.identity.certification_id, "execution-boundary continuity is violated")
    _append_error_if_false(findings, serialization["stable"], V37_CERTIFICATION_AUDIT_BLOCKED_BY_SERIALIZATION, "certification", result.identity.certification_id, "certification serialization is unstable")
    _append_error_if_false(findings, hashing["stable"], V37_CERTIFICATION_AUDIT_BLOCKED_BY_HASH, "certification", result.identity.certification_id, "certification hash is unstable")
    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    audit = V37GraphCertificationAuditResult(
        audit_status=V37_GRAPH_CERTIFICATION_AUDIT_STABLE if error_count == 0 else V37_GRAPH_CERTIFICATION_AUDIT_FAILED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        certification_identity_continuity_preserved=identity_ok,
        certification_scope_continuity_preserved=scope_identity_ok and scope_ok,
        evidence_source_continuity_preserved=evidence_source_ok,
        graph_continuity_preserved="graph_foundations" in reference_types,
        governance_continuity_preserved="governance" in reference_types,
        compatibility_continuity_preserved="compatibility" in reference_types,
        evaluation_continuity_preserved="evaluation" in reference_types,
        session_continuity_preserved="session" in reference_types,
        scenario_continuity_preserved="scenario" in reference_types,
        aggregation_continuity_preserved="aggregation" in reference_types,
        integrity_continuity_preserved="integrity" in reference_types,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=replay["rollback_continuity_preserved"],
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=explainability.explainability_status == V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
        execution_boundary_continuity_preserved=execution_boundary_ok,
        fail_visible_finding_preservation=finding_visibility_ok,
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        deterministic_audit_hash="",
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(audit, deterministic_audit_hash=hash_v3_7_graph_certification_audit_result(audit))


def export_v3_7_graph_certification_audit_finding(finding: V37GraphCertificationAuditFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_certification_audit_result(result: V37GraphCertificationAuditResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_certification_audit_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_certification_audit_result(result: V37GraphCertificationAuditResult) -> str:
    return stable_serialize(export_v3_7_graph_certification_audit_result(result))


def hash_v3_7_graph_certification_audit_result(result: V37GraphCertificationAuditResult) -> str:
    data = export_v3_7_graph_certification_audit_result(result)
    data.pop("deterministic_audit_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    result: V37GraphPlanningContinuityCertification,
    findings: list[V37GraphCertificationAuditFinding],
) -> None:
    status_map = {
        V37_CERTIFICATION_FINDING_BLOCKED: V37_CERTIFICATION_AUDIT_VISIBLE_BLOCKED,
        V37_CERTIFICATION_FINDING_WARNING: V37_CERTIFICATION_AUDIT_VISIBLE_WARNING,
        V37_CERTIFICATION_FINDING_SCOPE_INCOMPLETE: V37_CERTIFICATION_AUDIT_VISIBLE_SCOPE_INCOMPLETE,
        V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_UNCERTIFIED: V37_CERTIFICATION_AUDIT_VISIBLE_EXECUTION_BOUNDARY,
        V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED: V37_CERTIFICATION_AUDIT_VISIBLE_HIDDEN_RISK,
    }
    for finding in result.findings:
        status = status_map.get(finding.finding_classification)
        if status:
            findings.append(_finding(status, "certification_finding", finding.finding_id, f"{finding.finding_classification} remains fail-visible", "visibility"))


def _append_error_if_false(findings, condition: bool, status: str, subject_type: str, subject_id: str, message: str) -> None:
    if not condition:
        findings.append(_finding(status, subject_type, subject_id, message))


def _execution_boundary_preserved(result: V37GraphPlanningContinuityCertification) -> bool:
    return all(
        (
            result.certification_is_non_executable,
            result.certification_validates_planning_continuity_only,
            result.certified_continuity_does_not_authorize_execution,
            result.certification_does_not_mark_runtime_execution_readiness,
            result.certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
            not result.graph_execution_enabled,
            not result.certification_driven_execution_enabled,
            not result.orchestration_authorization_enabled,
            not result.execution_readiness_approval_enabled,
            not result.routing_enabled,
            not result.scheduling_enabled,
            not result.dispatch_enabled,
            not result.traversal_logic_enabled,
            not result.path_selection_enabled,
            not result.scenario_selection_enabled,
            not result.optimization_engine_enabled,
            not result.recommendation_enabled,
            not result.runtime_decision_making_enabled,
            not result.executable_certification_gates_enabled,
            not result.runtime_control_system_enabled,
            not result.evidence.runtime_readiness_certification,
            not result.evidence.execution_authorization,
            all(
                not any(
                    (
                        finding.execution_authorization,
                        finding.runtime_readiness_certification,
                        finding.routing_authorization,
                        finding.scheduling_authorization,
                        finding.dispatch_authorization,
                        finding.traversal_authorization,
                    )
                )
                for finding in result.findings
            ),
            all(
                item.non_executable_replay_evidence
                and not item.runtime_replay
                and not item.execution_authorization
                and not item.runtime_readiness_certification
                for item in result.replay_evidence
            ),
        )
    )


def _finding(status: str, subject_type: str, subject_id: str, message: str, severity: str = "error") -> V37GraphCertificationAuditFinding:
    return V37GraphCertificationAuditFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
