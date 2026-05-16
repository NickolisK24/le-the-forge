"""Fail-visible validation for v3.7 graph planning integrity enforcement."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_integrity_audit import (
    V37_GRAPH_INTEGRITY_AUDIT_STABLE,
    audit_v3_7_graph_integrity,
)
from .v3_7_graph_integrity_enforcement import (
    enforce_v3_7_graph_planning_integrity,
    graph_integrity_enforcement_identities_are_unique,
)
from .v3_7_graph_integrity_explainability import (
    V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_integrity,
)
from .v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION,
    V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
    V37GraphIntegrityEnforcementResult,
    hash_v3_7_graph_integrity_enforcement_result,
    validate_v3_7_graph_integrity_hash_stability,
    validate_v3_7_graph_integrity_serialization_stability,
)
from .v3_7_graph_integrity_policies import graph_integrity_policy_identities_are_unique
from .v3_7_graph_integrity_provenance import (
    V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_integrity_provenance,
)
from .v3_7_graph_integrity_replay import validate_v3_7_graph_integrity_replay_evidence


V37_GRAPH_INTEGRITY_VALIDATION_STABLE = "v3_7_graph_integrity_validation_stable"
V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED = "v3_7_graph_integrity_validation_blocked"
V37_INTEGRITY_VALIDATION_VISIBLE_BLOCKED = "v3_7_graph_integrity_validation_visible_blocked"
V37_INTEGRITY_VALIDATION_VISIBLE_WARNING = "v3_7_graph_integrity_validation_visible_warning"
V37_INTEGRITY_VALIDATION_VISIBLE_EXECUTION_BOUNDARY = "v3_7_graph_integrity_validation_visible_execution_boundary"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_DUPLICATE_POLICY = "v3_7_graph_integrity_blocked_by_duplicate_policy_identity"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_DUPLICATE_ENFORCEMENT = "v3_7_graph_integrity_blocked_by_duplicate_enforcement_identity"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE = "v3_7_graph_integrity_blocked_by_missing_evidence_source"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE_SOURCE = "v3_7_graph_integrity_blocked_by_invalid_evidence_source"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_PROVENANCE = "v3_7_graph_integrity_blocked_by_provenance"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_integrity_blocked_by_explainability"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_REPLAY = "v3_7_graph_integrity_blocked_by_replay"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_ROLLBACK = "v3_7_graph_integrity_blocked_by_rollback"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_HIDDEN_STATE = "v3_7_graph_integrity_blocked_by_hidden_state"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY = "v3_7_graph_integrity_blocked_by_execution_boundary"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_SERIALIZATION = "v3_7_graph_integrity_blocked_by_serialization"
V37_INTEGRITY_VALIDATION_BLOCKED_BY_HASH = "v3_7_graph_integrity_blocked_by_hash"


@dataclass(frozen=True)
class V37GraphIntegrityValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphIntegrityValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    duplicate_policy_identity_count: int
    duplicate_enforcement_identity_count: int
    missing_evidence_source_reference_count: int
    invalid_evidence_source_reference_count: int
    missing_provenance_evidence_count: int
    missing_explainability_evidence_count: int
    missing_replay_evidence_count: int
    missing_rollback_evidence_count: int
    hidden_prohibited_finding_count: int
    hidden_unsupported_finding_count: int
    hidden_unknown_finding_count: int
    execution_boundary_violation_count: int
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    integrity_enforcement_non_executable: bool
    valid_integrity_does_not_authorize_execution: bool
    execution_boundary_violations_blocked: bool
    deterministic_integrity_hash: str
    findings: tuple[V37GraphIntegrityValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_integrity(
    results: tuple[V37GraphIntegrityEnforcementResult, ...] | None = None,
) -> V37GraphIntegrityValidationResult:
    enforcement_results = results or (enforce_v3_7_graph_planning_integrity(),)
    primary = enforcement_results[0]
    findings: list[V37GraphIntegrityValidationFinding] = []
    duplicate_policy_count = 0 if graph_integrity_policy_identities_are_unique(tuple(item.policy.identity for item in enforcement_results)) else 1
    duplicate_enforcement_count = 0 if graph_integrity_enforcement_identities_are_unique(tuple(item.identity for item in enforcement_results)) else 1
    if duplicate_policy_count:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_DUPLICATE_POLICY, "policy", primary.policy.identity.policy_id, "duplicate policy identity detected"))
    if duplicate_enforcement_count:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_DUPLICATE_ENFORCEMENT, "enforcement", primary.identity.enforcement_id, "duplicate enforcement identity detected"))
    for result in enforcement_results:
        _add_visibility_findings(result, findings)
        if not result.evidence_source_references:
            findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE, "enforcement", result.identity.enforcement_id, "missing evidence-source references"))
        required_sources = {
            "graph_foundations",
            "governance",
            "compatibility",
            "evaluation",
            "session",
            "scenario",
            "aggregation",
        }
        if not required_sources.issubset(set(result.evidence_source_types)):
            findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE_SOURCE, "enforcement", result.identity.enforcement_id, "invalid or incomplete evidence-source references"))
        for integrity_finding in result.findings:
            if integrity_finding.finding_classification in (
                V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
                V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
                V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
            ) and (integrity_finding.hidden or not integrity_finding.fail_visible or integrity_finding.active_violation):
                findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_HIDDEN_STATE, "integrity_finding", integrity_finding.finding_id, f"hidden {integrity_finding.finding_classification} finding detected"))
            if integrity_finding.finding_classification == V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION and integrity_finding.active_violation:
                findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY, "integrity_finding", integrity_finding.finding_id, "execution-boundary violation is active"))
        if _execution_boundary_violation(result):
            findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY, "enforcement", result.identity.enforcement_id, "integrity enforcement exposed execution-boundary authorization"))

    audit = audit_v3_7_graph_integrity(primary)
    provenance = audit_v3_7_graph_integrity_provenance(primary)
    explainability = explain_v3_7_graph_integrity(primary)
    replay = validate_v3_7_graph_integrity_replay_evidence(primary)
    serialization = validate_v3_7_graph_integrity_serialization_stability(primary)
    hashing = validate_v3_7_graph_integrity_hash_stability(primary)
    if audit.audit_status != V37_GRAPH_INTEGRITY_AUDIT_STABLE:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE_SOURCE, "enforcement", primary.identity.enforcement_id, "integrity audit is unstable"))
    if provenance.provenance_status != V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_PROVENANCE, "enforcement", primary.identity.enforcement_id, "integrity provenance continuity is incomplete"))
    if explainability.explainability_status != V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXPLAINABILITY, "enforcement", primary.identity.enforcement_id, "integrity explainability continuity is incomplete"))
    if not replay["replay_continuity_preserved"] or replay["runtime_replay"] or replay["execution_authorization"]:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_REPLAY, "enforcement", primary.identity.enforcement_id, "integrity replay evidence is invalid"))
    if not replay["rollback_continuity_preserved"]:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_ROLLBACK, "enforcement", primary.identity.enforcement_id, "integrity rollback evidence is invalid"))
    if not serialization["stable"]:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_SERIALIZATION, "enforcement", primary.identity.enforcement_id, "integrity serialization is unstable"))
    if not hashing["stable"]:
        findings.append(_finding(V37_INTEGRITY_VALIDATION_BLOCKED_BY_HASH, "enforcement", primary.identity.enforcement_id, "integrity hash is unstable"))
    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphIntegrityValidationResult(
        validation_status=V37_GRAPH_INTEGRITY_VALIDATION_STABLE if error_count == 0 else V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        duplicate_policy_identity_count=duplicate_policy_count,
        duplicate_enforcement_identity_count=duplicate_enforcement_count,
        missing_evidence_source_reference_count=sum(1 for finding in findings if finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE),
        invalid_evidence_source_reference_count=sum(1 for finding in findings if finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE_SOURCE),
        missing_provenance_evidence_count=sum(1 for finding in findings if finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_PROVENANCE),
        missing_explainability_evidence_count=sum(1 for finding in findings if finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXPLAINABILITY),
        missing_replay_evidence_count=sum(1 for finding in findings if finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_REPLAY),
        missing_rollback_evidence_count=sum(1 for finding in findings if finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_ROLLBACK),
        hidden_prohibited_finding_count=_hidden_count(enforcement_results, V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE),
        hidden_unsupported_finding_count=_hidden_count(enforcement_results, V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE),
        hidden_unknown_finding_count=_hidden_count(enforcement_results, V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE),
        execution_boundary_violation_count=sum(1 for item in enforcement_results if _execution_boundary_violation(item)),
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=explainability.explainability_status == V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=replay["rollback_continuity_preserved"],
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        integrity_enforcement_non_executable=primary.integrity_enforcement_is_non_executable,
        valid_integrity_does_not_authorize_execution=primary.valid_integrity_does_not_authorize_execution,
        execution_boundary_violations_blocked=all(
            finding.blocks_validation
            for item in enforcement_results
            for finding in item.findings
            if finding.finding_classification == V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION
            and finding.active_violation
        ),
        deterministic_integrity_hash=hash_v3_7_graph_integrity_enforcement_result(primary),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_validation_hash=hash_v3_7_graph_integrity_validation_result(result))


def export_v3_7_graph_integrity_validation_finding(finding: V37GraphIntegrityValidationFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_integrity_validation_result(result: V37GraphIntegrityValidationResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_integrity_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_integrity_validation_result(result: V37GraphIntegrityValidationResult) -> str:
    return stable_serialize(export_v3_7_graph_integrity_validation_result(result))


def hash_v3_7_graph_integrity_validation_result(result: V37GraphIntegrityValidationResult) -> str:
    data = export_v3_7_graph_integrity_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    result: V37GraphIntegrityEnforcementResult,
    findings: list[V37GraphIntegrityValidationFinding],
) -> None:
    for finding in result.findings:
        if finding.finding_classification.endswith("_violation"):
            findings.append(_finding(V37_INTEGRITY_VALIDATION_VISIBLE_EXECUTION_BOUNDARY if finding.finding_classification == V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION else V37_INTEGRITY_VALIDATION_VISIBLE_BLOCKED, "integrity_finding", finding.finding_id, f"{finding.finding_classification} remains fail-visible", "visibility"))
        if finding.severity == "warning":
            findings.append(_finding(V37_INTEGRITY_VALIDATION_VISIBLE_WARNING, "integrity_finding", finding.finding_id, "warning finding remains fail-visible", "visibility"))


def _hidden_count(results: tuple[V37GraphIntegrityEnforcementResult, ...], classification: str) -> int:
    return sum(
        1
        for result in results
        for finding in result.findings
        if finding.finding_classification == classification
        and (finding.hidden or not finding.fail_visible or finding.active_violation)
    )


def _execution_boundary_violation(result: V37GraphIntegrityEnforcementResult) -> bool:
    return any(
        (
            not result.integrity_enforcement_is_non_executable,
            not result.integrity_enforcement_validates_planning_evidence_only,
            not result.valid_integrity_does_not_authorize_execution,
            not result.blocked_integrity_does_not_perform_runtime_blocking,
            not result.enforcement_outcomes_are_planning_validation_only,
            not result.integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
            result.graph_execution_enabled,
            result.integrity_driven_execution_enabled,
            result.orchestration_authorization_enabled,
            result.routing_enabled,
            result.scheduling_enabled,
            result.dispatch_enabled,
            result.traversal_logic_enabled,
            result.path_selection_enabled,
            result.scenario_selection_enabled,
            result.optimization_engine_enabled,
            result.recommendation_enabled,
            result.autonomous_orchestration_enabled,
            result.runtime_mutation_enabled,
            result.persistent_runtime_writes_enabled,
            result.runtime_decision_making_enabled,
            result.execution_gates_enabled,
            result.callable_orchestration_flows_enabled,
            result.runtime_control_system_enabled,
            any(
                (
                    finding.execution_authorization
                    or finding.routing_authorization
                    or finding.scheduling_authorization
                    or finding.dispatch_authorization
                    or finding.traversal_authorization
                    or (
                        finding.finding_classification == V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION
                        and finding.active_violation
                    )
                )
                for finding in result.findings
            ),
            any(
                not replay.non_executable_replay_evidence or replay.runtime_replay or replay.execution_authorization
                for replay in result.replay_evidence
            ),
        )
    )


def _finding(status: str, subject_type: str, subject_id: str, message: str, severity: str = "error") -> V37GraphIntegrityValidationFinding:
    return V37GraphIntegrityValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
