"""Deterministic audit infrastructure for v3.7 graph planning integrity."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_integrity_enforcement import (
    enforce_v3_7_graph_planning_integrity,
    graph_integrity_enforcement_identity_key,
)
from .v3_7_graph_integrity_explainability import (
    V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_integrity,
)
from .v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_BLOCKED,
    V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION,
    V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
    V37_INTEGRITY_FINDING_WARNING,
    V37GraphIntegrityEnforcementResult,
    validate_v3_7_graph_integrity_hash_stability,
    validate_v3_7_graph_integrity_serialization_stability,
)
from .v3_7_graph_integrity_policies import graph_integrity_policy_identity_key
from .v3_7_graph_integrity_provenance import (
    V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_integrity_provenance,
)
from .v3_7_graph_integrity_replay import validate_v3_7_graph_integrity_replay_evidence


V37_GRAPH_INTEGRITY_AUDIT_STABLE = "v3_7_graph_integrity_audit_stable"
V37_GRAPH_INTEGRITY_AUDIT_FAILED = "v3_7_graph_integrity_audit_failed"
V37_INTEGRITY_AUDIT_VISIBLE_BLOCKED = "v3_7_graph_integrity_visible_blocked"
V37_INTEGRITY_AUDIT_VISIBLE_WARNING = "v3_7_graph_integrity_visible_warning"
V37_INTEGRITY_AUDIT_VISIBLE_EXECUTION_BOUNDARY = "v3_7_graph_integrity_visible_execution_boundary"
V37_INTEGRITY_AUDIT_VISIBLE_HIDDEN_PROHIBITED = "v3_7_graph_integrity_visible_hidden_prohibited"
V37_INTEGRITY_AUDIT_VISIBLE_HIDDEN_UNSUPPORTED = "v3_7_graph_integrity_visible_hidden_unsupported"
V37_INTEGRITY_AUDIT_VISIBLE_HIDDEN_UNKNOWN = "v3_7_graph_integrity_visible_hidden_unknown"
V37_INTEGRITY_AUDIT_BLOCKED_BY_POLICY_IDENTITY = "v3_7_graph_integrity_audit_blocked_by_policy_identity"
V37_INTEGRITY_AUDIT_BLOCKED_BY_ENFORCEMENT_IDENTITY = "v3_7_graph_integrity_audit_blocked_by_enforcement_identity"
V37_INTEGRITY_AUDIT_BLOCKED_BY_EVIDENCE_SOURCE = "v3_7_graph_integrity_audit_blocked_by_evidence_source"
V37_INTEGRITY_AUDIT_BLOCKED_BY_REPLAY = "v3_7_graph_integrity_audit_blocked_by_replay"
V37_INTEGRITY_AUDIT_BLOCKED_BY_ROLLBACK = "v3_7_graph_integrity_audit_blocked_by_rollback"
V37_INTEGRITY_AUDIT_BLOCKED_BY_PROVENANCE = "v3_7_graph_integrity_audit_blocked_by_provenance"
V37_INTEGRITY_AUDIT_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_integrity_audit_blocked_by_explainability"
V37_INTEGRITY_AUDIT_BLOCKED_BY_FINDING_VISIBILITY = "v3_7_graph_integrity_audit_blocked_by_finding_visibility"
V37_INTEGRITY_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY = "v3_7_graph_integrity_audit_blocked_by_execution_boundary"
V37_INTEGRITY_AUDIT_BLOCKED_BY_SERIALIZATION = "v3_7_graph_integrity_audit_blocked_by_serialization"
V37_INTEGRITY_AUDIT_BLOCKED_BY_HASH = "v3_7_graph_integrity_audit_blocked_by_hash"


@dataclass(frozen=True)
class V37GraphIntegrityAuditFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphIntegrityAuditResult:
    audit_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    policy_identity_continuity_preserved: bool
    enforcement_identity_continuity_preserved: bool
    evidence_source_continuity_preserved: bool
    graph_continuity_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    evaluation_continuity_preserved: bool
    session_continuity_preserved: bool
    scenario_continuity_preserved: bool
    aggregation_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    execution_boundary_continuity_preserved: bool
    fail_visible_finding_preservation: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    deterministic_audit_hash: str
    findings: tuple[V37GraphIntegrityAuditFinding, ...]


def audit_v3_7_graph_integrity(
    result: V37GraphIntegrityEnforcementResult | None = None,
) -> V37GraphIntegrityAuditResult:
    enforcement = result or enforce_v3_7_graph_planning_integrity()
    findings: list[V37GraphIntegrityAuditFinding] = []
    _add_visibility_findings(enforcement, findings)
    source_types = set(enforcement.evidence_source_types)
    policy_identity_ok = enforcement.policy.identity.stable_identity_key == graph_integrity_policy_identity_key(enforcement.policy.identity)
    enforcement_identity_ok = enforcement.identity.stable_identity_key == graph_integrity_enforcement_identity_key(enforcement.identity)
    required_sources = {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
        "aggregation",
    }
    evidence_source_ok = required_sources.issubset(source_types) and bool(enforcement.evidence_source_references)
    replay = validate_v3_7_graph_integrity_replay_evidence(enforcement)
    provenance = audit_v3_7_graph_integrity_provenance(enforcement)
    explainability = explain_v3_7_graph_integrity(enforcement)
    serialization = validate_v3_7_graph_integrity_serialization_stability(enforcement)
    hashing = validate_v3_7_graph_integrity_hash_stability(enforcement)
    rollback_ok = bool(enforcement.rollback_continuity_references) and replay["rollback_continuity_preserved"]
    finding_visibility_ok = all(finding.fail_visible and not finding.hidden for finding in enforcement.findings)
    execution_boundary_ok = _execution_boundary_preserved(enforcement)
    _append_error_if_false(findings, policy_identity_ok, V37_INTEGRITY_AUDIT_BLOCKED_BY_POLICY_IDENTITY, "policy", enforcement.policy.identity.policy_id, "policy identity continuity is unstable")
    _append_error_if_false(findings, enforcement_identity_ok, V37_INTEGRITY_AUDIT_BLOCKED_BY_ENFORCEMENT_IDENTITY, "enforcement", enforcement.identity.enforcement_id, "enforcement identity continuity is unstable")
    _append_error_if_false(findings, evidence_source_ok, V37_INTEGRITY_AUDIT_BLOCKED_BY_EVIDENCE_SOURCE, "enforcement", enforcement.identity.enforcement_id, "evidence-source continuity is incomplete")
    _append_error_if_false(findings, replay["replay_continuity_preserved"], V37_INTEGRITY_AUDIT_BLOCKED_BY_REPLAY, "enforcement", enforcement.identity.enforcement_id, "replay continuity is incomplete")
    _append_error_if_false(findings, rollback_ok, V37_INTEGRITY_AUDIT_BLOCKED_BY_ROLLBACK, "enforcement", enforcement.identity.enforcement_id, "rollback continuity is incomplete")
    _append_error_if_false(findings, provenance.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED, V37_INTEGRITY_AUDIT_BLOCKED_BY_PROVENANCE, "enforcement", enforcement.identity.enforcement_id, "provenance continuity is incomplete")
    _append_error_if_false(findings, explainability.explainability_status == V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE, V37_INTEGRITY_AUDIT_BLOCKED_BY_EXPLAINABILITY, "enforcement", enforcement.identity.enforcement_id, "explainability continuity is incomplete")
    _append_error_if_false(findings, finding_visibility_ok, V37_INTEGRITY_AUDIT_BLOCKED_BY_FINDING_VISIBILITY, "enforcement", enforcement.identity.enforcement_id, "integrity finding visibility is incomplete")
    _append_error_if_false(findings, execution_boundary_ok, V37_INTEGRITY_AUDIT_BLOCKED_BY_EXECUTION_BOUNDARY, "enforcement", enforcement.identity.enforcement_id, "execution-boundary continuity is violated")
    _append_error_if_false(findings, serialization["stable"], V37_INTEGRITY_AUDIT_BLOCKED_BY_SERIALIZATION, "enforcement", enforcement.identity.enforcement_id, "integrity serialization is unstable")
    _append_error_if_false(findings, hashing["stable"], V37_INTEGRITY_AUDIT_BLOCKED_BY_HASH, "enforcement", enforcement.identity.enforcement_id, "integrity hash is unstable")
    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    audit = V37GraphIntegrityAuditResult(
        audit_status=V37_GRAPH_INTEGRITY_AUDIT_STABLE if error_count == 0 else V37_GRAPH_INTEGRITY_AUDIT_FAILED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        policy_identity_continuity_preserved=policy_identity_ok,
        enforcement_identity_continuity_preserved=enforcement_identity_ok,
        evidence_source_continuity_preserved=evidence_source_ok,
        graph_continuity_preserved="graph_foundations" in source_types,
        governance_continuity_preserved="governance" in source_types,
        compatibility_continuity_preserved="compatibility" in source_types,
        evaluation_continuity_preserved="evaluation" in source_types,
        session_continuity_preserved="session" in source_types,
        scenario_continuity_preserved="scenario" in source_types,
        aggregation_continuity_preserved="aggregation" in source_types,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=rollback_ok,
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=explainability.explainability_status == V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
        execution_boundary_continuity_preserved=execution_boundary_ok,
        fail_visible_finding_preservation=finding_visibility_ok,
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        deterministic_audit_hash="",
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(audit, deterministic_audit_hash=hash_v3_7_graph_integrity_audit_result(audit))


def export_v3_7_graph_integrity_audit_finding(finding: V37GraphIntegrityAuditFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_integrity_audit_result(result: V37GraphIntegrityAuditResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_integrity_audit_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_integrity_audit_result(result: V37GraphIntegrityAuditResult) -> str:
    return stable_serialize(export_v3_7_graph_integrity_audit_result(result))


def hash_v3_7_graph_integrity_audit_result(result: V37GraphIntegrityAuditResult) -> str:
    data = export_v3_7_graph_integrity_audit_result(result)
    data.pop("deterministic_audit_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    enforcement: V37GraphIntegrityEnforcementResult,
    findings: list[V37GraphIntegrityAuditFinding],
) -> None:
    status_map = {
        V37_INTEGRITY_FINDING_BLOCKED: V37_INTEGRITY_AUDIT_VISIBLE_BLOCKED,
        V37_INTEGRITY_FINDING_WARNING: V37_INTEGRITY_AUDIT_VISIBLE_WARNING,
        V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION: V37_INTEGRITY_AUDIT_VISIBLE_EXECUTION_BOUNDARY,
        V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE: V37_INTEGRITY_AUDIT_VISIBLE_HIDDEN_PROHIBITED,
        V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE: V37_INTEGRITY_AUDIT_VISIBLE_HIDDEN_UNSUPPORTED,
        V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE: V37_INTEGRITY_AUDIT_VISIBLE_HIDDEN_UNKNOWN,
    }
    for finding in enforcement.findings:
        status = status_map.get(finding.finding_classification)
        if status:
            findings.append(_finding(status, "integrity_finding", finding.finding_id, f"{finding.finding_classification} remains fail-visible", "visibility"))


def _append_error_if_false(findings, condition: bool, status: str, subject_type: str, subject_id: str, message: str) -> None:
    if not condition:
        findings.append(_finding(status, subject_type, subject_id, message))


def _execution_boundary_preserved(enforcement: V37GraphIntegrityEnforcementResult) -> bool:
    return all(
        (
            enforcement.integrity_enforcement_is_non_executable,
            enforcement.integrity_enforcement_validates_planning_evidence_only,
            enforcement.valid_integrity_does_not_authorize_execution,
            enforcement.blocked_integrity_does_not_perform_runtime_blocking,
            enforcement.enforcement_outcomes_are_planning_validation_only,
            enforcement.integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
            not enforcement.graph_execution_enabled,
            not enforcement.integrity_driven_execution_enabled,
            not enforcement.orchestration_authorization_enabled,
            not enforcement.routing_enabled,
            not enforcement.scheduling_enabled,
            not enforcement.dispatch_enabled,
            not enforcement.traversal_logic_enabled,
            not enforcement.path_selection_enabled,
            not enforcement.scenario_selection_enabled,
            not enforcement.optimization_engine_enabled,
            not enforcement.recommendation_enabled,
            not enforcement.autonomous_orchestration_enabled,
            not enforcement.runtime_mutation_enabled,
            not enforcement.persistent_runtime_writes_enabled,
            not enforcement.runtime_decision_making_enabled,
            not enforcement.execution_gates_enabled,
            not enforcement.callable_orchestration_flows_enabled,
            not enforcement.runtime_control_system_enabled,
            all(
                not any(
                    (
                        finding.execution_authorization,
                        finding.routing_authorization,
                        finding.scheduling_authorization,
                        finding.dispatch_authorization,
                        finding.traversal_authorization,
                    )
                )
                for finding in enforcement.findings
            ),
            all(
                item.non_executable_replay_evidence and not item.runtime_replay and not item.execution_authorization
                for item in enforcement.replay_evidence
            ),
        )
    )


def _finding(status: str, subject_type: str, subject_id: str, message: str, severity: str = "error") -> V37GraphIntegrityAuditFinding:
    return V37GraphIntegrityAuditFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
