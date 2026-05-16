"""Fail-visible validation for v3.7 planning continuity certification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_certification_audit import (
    V37_GRAPH_CERTIFICATION_AUDIT_STABLE,
    audit_v3_7_graph_certification,
)
from .v3_7_graph_certification_evidence import build_v3_7_graph_planning_continuity_certification
from .v3_7_graph_certification_explainability import (
    V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_certification,
)
from .v3_7_graph_certification_models import (
    V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED,
    V37GraphPlanningContinuityCertification,
    hash_v3_7_graph_planning_continuity_certification,
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
    graph_certification_identities_are_unique,
    graph_certification_scope_identities_are_unique,
)


V37_GRAPH_CERTIFICATION_VALIDATION_STABLE = "v3_7_graph_certification_validation_stable"
V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED = "v3_7_graph_certification_validation_blocked"
V37_CERTIFICATION_VALIDATION_VISIBLE_BLOCKED = "v3_7_graph_certification_validation_visible_blocked"
V37_CERTIFICATION_VALIDATION_VISIBLE_WARNING = "v3_7_graph_certification_validation_visible_warning"
V37_CERTIFICATION_VALIDATION_VISIBLE_HIDDEN_RISK = "v3_7_graph_certification_validation_visible_hidden_risk"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_DUPLICATE_CERTIFICATION = "v3_7_graph_certification_blocked_by_duplicate_certification_identity"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_DUPLICATE_SCOPE = "v3_7_graph_certification_blocked_by_duplicate_scope_identity"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_MISSING_SCOPE = "v3_7_graph_certification_blocked_by_missing_scope_reference"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INCOMPLETE_SCOPE = "v3_7_graph_certification_blocked_by_incomplete_scope"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE = "v3_7_graph_certification_blocked_by_invalid_evidence_reference"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_PROVENANCE = "v3_7_graph_certification_blocked_by_provenance"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_certification_blocked_by_explainability"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_REPLAY = "v3_7_graph_certification_blocked_by_replay"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_ROLLBACK = "v3_7_graph_certification_blocked_by_rollback"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_HIDDEN_STATE = "v3_7_graph_certification_blocked_by_hidden_state"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY = "v3_7_graph_certification_blocked_by_execution_boundary"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_SERIALIZATION = "v3_7_graph_certification_blocked_by_serialization"
V37_CERTIFICATION_VALIDATION_BLOCKED_BY_HASH = "v3_7_graph_certification_blocked_by_hash"


@dataclass(frozen=True)
class V37GraphCertificationValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphCertificationValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    duplicate_certification_identity_count: int
    duplicate_scope_identity_count: int
    missing_scope_reference_count: int
    incomplete_scope_count: int
    invalid_evidence_reference_count: int
    missing_provenance_evidence_count: int
    missing_explainability_evidence_count: int
    missing_replay_evidence_count: int
    missing_rollback_evidence_count: int
    hidden_prohibited_finding_count: int
    hidden_unsupported_finding_count: int
    hidden_unknown_finding_count: int
    execution_boundary_certification_failure_count: int
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    certification_non_executable: bool
    certified_continuity_does_not_authorize_execution: bool
    certification_does_not_mark_runtime_execution_readiness: bool
    routing_scheduling_dispatch_traversal_prohibited: bool
    deterministic_certification_hash: str
    findings: tuple[V37GraphCertificationValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_certification(
    certifications: tuple[V37GraphPlanningContinuityCertification, ...] | None = None,
) -> V37GraphCertificationValidationResult:
    results = certifications or (build_v3_7_graph_planning_continuity_certification(),)
    primary = results[0]
    findings: list[V37GraphCertificationValidationFinding] = []
    duplicate_certification_count = 0 if graph_certification_identities_are_unique(tuple(item.identity for item in results)) else 1
    duplicate_scope_count = 0 if graph_certification_scope_identities_are_unique(tuple(item.scope.identity for item in results)) else 1
    if duplicate_certification_count:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_DUPLICATE_CERTIFICATION, "certification", primary.identity.certification_id, "duplicate certification identity detected"))
    if duplicate_scope_count:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_DUPLICATE_SCOPE, "scope", primary.scope.identity.scope_id, "duplicate scope identity detected"))
    for certification in results:
        _add_visibility_findings(certification, findings)
        if not certification.scope.references:
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_MISSING_SCOPE, "scope", certification.scope.identity.scope_id, "missing scope references"))
        if not certification_scope_is_complete(certification.scope):
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INCOMPLETE_SCOPE, "scope", certification.scope.identity.scope_id, "certification scope is incomplete"))
        if not _evidence_references_complete(certification):
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE, "certification", certification.identity.certification_id, "certification evidence references are incomplete"))
        hidden_risk_count = sum(
            1
            for finding in certification.findings
            if finding.finding_classification == V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED
            and (finding.hidden or not finding.fail_visible or finding.active_violation)
        )
        if hidden_risk_count:
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_HIDDEN_STATE, "certification", certification.identity.certification_id, "hidden risk-state finding detected"))
        if _execution_boundary_failure(certification):
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY, "certification", certification.identity.certification_id, "execution-boundary certification failed"))

    audit = audit_v3_7_graph_certification(primary)
    provenance = audit_v3_7_graph_certification_provenance(primary)
    explainability = explain_v3_7_graph_certification(primary)
    replay = validate_v3_7_graph_certification_replay_evidence(primary)
    serialization = validate_v3_7_graph_certification_serialization_stability(primary)
    hashing = validate_v3_7_graph_certification_hash_stability(primary)
    if audit.audit_status != V37_GRAPH_CERTIFICATION_AUDIT_STABLE:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE, "certification", primary.identity.certification_id, "certification audit is unstable"))
    if provenance.provenance_status != V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_PROVENANCE, "certification", primary.identity.certification_id, "certification provenance continuity is incomplete"))
    if explainability.explainability_status != V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXPLAINABILITY, "certification", primary.identity.certification_id, "certification explainability continuity is incomplete"))
    if not replay["replay_continuity_preserved"] or replay["runtime_replay"] or replay["execution_authorization"]:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_REPLAY, "certification", primary.identity.certification_id, "certification replay evidence is invalid"))
    if not replay["rollback_continuity_preserved"]:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_ROLLBACK, "certification", primary.identity.certification_id, "certification rollback evidence is invalid"))
    if not serialization["stable"]:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_SERIALIZATION, "certification", primary.identity.certification_id, "certification serialization is unstable"))
    if not hashing["stable"]:
        findings.append(_finding(V37_CERTIFICATION_VALIDATION_BLOCKED_BY_HASH, "certification", primary.identity.certification_id, "certification hash is unstable"))
    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    validation = V37GraphCertificationValidationResult(
        validation_status=V37_GRAPH_CERTIFICATION_VALIDATION_STABLE if error_count == 0 else V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        duplicate_certification_identity_count=duplicate_certification_count,
        duplicate_scope_identity_count=duplicate_scope_count,
        missing_scope_reference_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_MISSING_SCOPE),
        incomplete_scope_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INCOMPLETE_SCOPE),
        invalid_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE),
        missing_provenance_evidence_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_PROVENANCE),
        missing_explainability_evidence_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXPLAINABILITY),
        missing_replay_evidence_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_REPLAY),
        missing_rollback_evidence_count=sum(1 for finding in findings if finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_ROLLBACK),
        hidden_prohibited_finding_count=_hidden_risk_count(results),
        hidden_unsupported_finding_count=_hidden_risk_count(results),
        hidden_unknown_finding_count=_hidden_risk_count(results),
        execution_boundary_certification_failure_count=sum(1 for item in results if _execution_boundary_failure(item)),
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=explainability.explainability_status == V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=replay["rollback_continuity_preserved"],
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        certification_non_executable=primary.certification_is_non_executable,
        certified_continuity_does_not_authorize_execution=primary.certified_continuity_does_not_authorize_execution,
        certification_does_not_mark_runtime_execution_readiness=primary.certification_does_not_mark_runtime_execution_readiness,
        routing_scheduling_dispatch_traversal_prohibited=not any(
            (primary.routing_enabled, primary.scheduling_enabled, primary.dispatch_enabled, primary.traversal_logic_enabled)
        ),
        deterministic_certification_hash=hash_v3_7_graph_planning_continuity_certification(primary),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(validation, deterministic_validation_hash=hash_v3_7_graph_certification_validation_result(validation))


def export_v3_7_graph_certification_validation_finding(
    finding: V37GraphCertificationValidationFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_certification_validation_result(result: V37GraphCertificationValidationResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_certification_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_certification_validation_result(result: V37GraphCertificationValidationResult) -> str:
    return stable_serialize(export_v3_7_graph_certification_validation_result(result))


def hash_v3_7_graph_certification_validation_result(result: V37GraphCertificationValidationResult) -> str:
    data = export_v3_7_graph_certification_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(certification, findings: list[V37GraphCertificationValidationFinding]) -> None:
    for finding in certification.findings:
        if finding.finding_classification.endswith("_uncertified") or finding.finding_classification in (
            "certification_blocked",
            "scope_incomplete",
        ):
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_VISIBLE_BLOCKED, "certification_finding", finding.finding_id, f"{finding.finding_classification} remains fail-visible", "visibility"))
        if finding.finding_classification == "certification_warning":
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_VISIBLE_WARNING, "certification_finding", finding.finding_id, "certification warning remains fail-visible", "visibility"))
        if finding.finding_classification == V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED:
            findings.append(_finding(V37_CERTIFICATION_VALIDATION_VISIBLE_HIDDEN_RISK, "certification_finding", finding.finding_id, "hidden risk state detection remains fail-visible", "visibility"))


def _evidence_references_complete(certification: V37GraphPlanningContinuityCertification) -> bool:
    evidence = certification.evidence
    return all(
        (
            evidence.graph_evidence_references,
            evidence.governance_evidence_references,
            evidence.compatibility_evidence_references,
            evidence.evaluation_evidence_references,
            evidence.session_evidence_references,
            evidence.scenario_evidence_references,
            evidence.aggregation_evidence_references,
            evidence.integrity_evidence_references,
            evidence.continuity_hashes,
            evidence.provenance_references,
            evidence.explainability_references,
            evidence.replay_references,
            evidence.rollback_references,
            evidence.execution_boundary_references,
        )
    )


def _hidden_risk_count(certifications: tuple[V37GraphPlanningContinuityCertification, ...]) -> int:
    return sum(
        1
        for certification in certifications
        for finding in certification.findings
        if finding.finding_classification == V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED
        and (finding.hidden or not finding.fail_visible or finding.active_violation)
    )


def _execution_boundary_failure(certification: V37GraphPlanningContinuityCertification) -> bool:
    return any(
        (
            not certification.certification_is_non_executable,
            not certification.certification_validates_planning_continuity_only,
            not certification.certified_continuity_does_not_authorize_execution,
            not certification.certification_does_not_mark_runtime_execution_readiness,
            not certification.certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
            certification.graph_execution_enabled,
            certification.certification_driven_execution_enabled,
            certification.orchestration_authorization_enabled,
            certification.execution_readiness_approval_enabled,
            certification.routing_enabled,
            certification.scheduling_enabled,
            certification.dispatch_enabled,
            certification.traversal_logic_enabled,
            certification.path_selection_enabled,
            certification.scenario_selection_enabled,
            certification.optimization_engine_enabled,
            certification.recommendation_enabled,
            certification.runtime_decision_making_enabled,
            certification.executable_certification_gates_enabled,
            certification.runtime_control_system_enabled,
            certification.evidence.execution_authorization,
            certification.evidence.runtime_readiness_certification,
            any(
                finding.execution_authorization
                or finding.runtime_readiness_certification
                or finding.routing_authorization
                or finding.scheduling_authorization
                or finding.dispatch_authorization
                or finding.traversal_authorization
                for finding in certification.findings
            ),
        )
    )


def _finding(status: str, subject_type: str, subject_id: str, message: str, severity: str = "error") -> V37GraphCertificationValidationFinding:
    return V37GraphCertificationValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
