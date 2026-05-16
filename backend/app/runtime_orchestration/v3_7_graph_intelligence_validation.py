"""Fail-visible validation for v3.7 planning intelligence aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_intelligence_aggregation import (
    build_v3_7_graph_planning_intelligence_aggregation,
    graph_intelligence_identities_are_unique,
)
from .v3_7_graph_intelligence_audit import (
    V37_GRAPH_INTELLIGENCE_AUDIT_STABLE,
    audit_v3_7_graph_intelligence,
)
from .v3_7_graph_intelligence_explainability import (
    V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_intelligence,
)
from .v3_7_graph_intelligence_models import (
    V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
    V37GraphPlanningIntelligenceAggregation,
    hash_v3_7_graph_planning_intelligence_aggregation,
    validate_v3_7_graph_intelligence_hash_stability,
    validate_v3_7_graph_intelligence_serialization_stability,
)
from .v3_7_graph_intelligence_provenance import (
    V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_intelligence_provenance,
)
from .v3_7_graph_intelligence_replay import validate_v3_7_graph_intelligence_replay_evidence


V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE = "v3_7_graph_intelligence_validation_stable"
V37_GRAPH_INTELLIGENCE_VALIDATION_BLOCKED = "v3_7_graph_intelligence_validation_blocked"
V37_INTELLIGENCE_VALIDATION_VISIBLE_PROHIBITED = "v3_7_graph_intelligence_validation_visible_prohibited"
V37_INTELLIGENCE_VALIDATION_VISIBLE_UNSUPPORTED = "v3_7_graph_intelligence_validation_visible_unsupported"
V37_INTELLIGENCE_VALIDATION_VISIBLE_UNKNOWN = "v3_7_graph_intelligence_validation_visible_unknown"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY = "v3_7_graph_intelligence_blocked_by_duplicate_identity"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE = "v3_7_graph_intelligence_blocked_by_missing_evidence_source"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_GRAPH_EVIDENCE = "v3_7_graph_intelligence_blocked_by_invalid_graph_evidence"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_GOVERNANCE_EVIDENCE = "v3_7_graph_intelligence_blocked_by_invalid_governance_evidence"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_COMPATIBILITY_EVIDENCE = "v3_7_graph_intelligence_blocked_by_invalid_compatibility_evidence"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE = "v3_7_graph_intelligence_blocked_by_invalid_evaluation_evidence"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SESSION_EVIDENCE = "v3_7_graph_intelligence_blocked_by_invalid_session_evidence"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SCENARIO_EVIDENCE = "v3_7_graph_intelligence_blocked_by_invalid_scenario_evidence"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_PROVENANCE = "v3_7_graph_intelligence_blocked_by_provenance"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_intelligence_blocked_by_explainability"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_HIDDEN_STATE = "v3_7_graph_intelligence_blocked_by_hidden_state"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_SERIALIZATION = "v3_7_graph_intelligence_blocked_by_serialization"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_HASH = "v3_7_graph_intelligence_blocked_by_hash"
V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_EXECUTION_AUTHORIZATION = "v3_7_graph_intelligence_blocked_by_execution_authorization"


@dataclass(frozen=True)
class V37GraphIntelligenceValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphIntelligenceValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    duplicate_aggregation_identity_count: int
    missing_evidence_source_reference_count: int
    invalid_graph_evidence_reference_count: int
    invalid_governance_evidence_reference_count: int
    invalid_compatibility_evidence_reference_count: int
    invalid_evaluation_evidence_reference_count: int
    invalid_session_evidence_reference_count: int
    invalid_scenario_evidence_reference_count: int
    hidden_prohibited_finding_count: int
    hidden_unsupported_finding_count: int
    hidden_unknown_finding_count: int
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    non_execution_guarantee_preserved: bool
    no_execution_recommendation_preserved: bool
    no_runtime_path_selection_preserved: bool
    deterministic_aggregation_hash: str
    findings: tuple[V37GraphIntelligenceValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_intelligence(
    aggregations: tuple[V37GraphPlanningIntelligenceAggregation, ...] | None = None,
) -> V37GraphIntelligenceValidationResult:
    planning_intelligence = aggregations or (build_v3_7_graph_planning_intelligence_aggregation(),)
    primary = planning_intelligence[0]
    findings: list[V37GraphIntelligenceValidationFinding] = []
    duplicate_count = 0 if graph_intelligence_identities_are_unique(tuple(item.identity for item in planning_intelligence)) else 1
    if duplicate_count:
        findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY, "aggregation", primary.identity.aggregation_id, "duplicate aggregation identity detected"))
    for aggregation in planning_intelligence:
        _add_visibility_findings(aggregation, findings)
        source_types = {source.source_type for source in aggregation.evidence_sources}
        if not aggregation.evidence_sources:
            findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE, "aggregation", aggregation.identity.aggregation_id, "missing evidence-source references"))
        _require_source(findings, source_types, "graph_foundations", V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_GRAPH_EVIDENCE, aggregation.identity.aggregation_id)
        _require_source(findings, source_types, "governance", V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_GOVERNANCE_EVIDENCE, aggregation.identity.aggregation_id)
        _require_source(findings, source_types, "compatibility", V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_COMPATIBILITY_EVIDENCE, aggregation.identity.aggregation_id)
        _require_source(findings, source_types, "evaluation", V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE, aggregation.identity.aggregation_id)
        _require_source(findings, source_types, "session", V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SESSION_EVIDENCE, aggregation.identity.aggregation_id)
        _require_source(findings, source_types, "scenario", V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SCENARIO_EVIDENCE, aggregation.identity.aggregation_id)
        for finding in aggregation.findings:
            if finding.finding_classification in (
                V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
                V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
                V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
            ) and (finding.hidden or not finding.fail_visible):
                findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_HIDDEN_STATE, "intelligence_finding", finding.finding_id, f"hidden {finding.finding_classification} finding detected"))
        if _accidental_execution_authorization(aggregation):
            findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_EXECUTION_AUTHORIZATION, "aggregation", aggregation.identity.aggregation_id, "aggregation exposed execution recommendation, authorization, or runtime path selection"))

    audit = audit_v3_7_graph_intelligence(primary)
    provenance = audit_v3_7_graph_intelligence_provenance(primary)
    explainability = explain_v3_7_graph_intelligence(primary)
    replay = validate_v3_7_graph_intelligence_replay_evidence(primary)
    serialization = validate_v3_7_graph_intelligence_serialization_stability(primary)
    hashing = validate_v3_7_graph_intelligence_hash_stability(primary)
    if audit.audit_status != V37_GRAPH_INTELLIGENCE_AUDIT_STABLE:
        findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE, "aggregation", primary.identity.aggregation_id, "aggregation audit is unstable"))
    if provenance.provenance_status != V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED:
        findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_PROVENANCE, "aggregation", primary.identity.aggregation_id, "aggregation provenance continuity is incomplete"))
    if explainability.explainability_status != V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE:
        findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_EXPLAINABILITY, "aggregation", primary.identity.aggregation_id, "aggregation explainability continuity is incomplete"))
    if not serialization["stable"]:
        findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_SERIALIZATION, "aggregation", primary.identity.aggregation_id, "aggregation serialization is unstable"))
    if not hashing["stable"]:
        findings.append(_finding(V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_HASH, "aggregation", primary.identity.aggregation_id, "aggregation hash is unstable"))
    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphIntelligenceValidationResult(
        validation_status=V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE if error_count == 0 else V37_GRAPH_INTELLIGENCE_VALIDATION_BLOCKED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        duplicate_aggregation_identity_count=duplicate_count,
        missing_evidence_source_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_MISSING_EVIDENCE_SOURCE),
        invalid_graph_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_GRAPH_EVIDENCE),
        invalid_governance_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_GOVERNANCE_EVIDENCE),
        invalid_compatibility_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_COMPATIBILITY_EVIDENCE),
        invalid_evaluation_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_EVALUATION_EVIDENCE),
        invalid_session_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SESSION_EVIDENCE),
        invalid_scenario_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SCENARIO_EVIDENCE),
        hidden_prohibited_finding_count=_hidden_count(planning_intelligence, V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE),
        hidden_unsupported_finding_count=_hidden_count(planning_intelligence, V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE),
        hidden_unknown_finding_count=_hidden_count(planning_intelligence, V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE),
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=explainability.explainability_status == V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=replay["rollback_continuity_preserved"],
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=audit.non_execution_guarantee_preserved,
        no_execution_recommendation_preserved=not any(insight.recommends_execution for insight in primary.insights),
        no_runtime_path_selection_preserved=not any(insight.selects_runtime_path for insight in primary.insights),
        deterministic_aggregation_hash=hash_v3_7_graph_planning_intelligence_aggregation(primary),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_validation_hash=hash_v3_7_graph_intelligence_validation_result(result))


def export_v3_7_graph_intelligence_validation_finding(finding: V37GraphIntelligenceValidationFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_intelligence_validation_result(result: V37GraphIntelligenceValidationResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_intelligence_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_intelligence_validation_result(result: V37GraphIntelligenceValidationResult) -> str:
    return stable_serialize(export_v3_7_graph_intelligence_validation_result(result))


def hash_v3_7_graph_intelligence_validation_result(result: V37GraphIntelligenceValidationResult) -> str:
    data = export_v3_7_graph_intelligence_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(aggregation, findings: list[V37GraphIntelligenceValidationFinding]) -> None:
    status_map = {
        V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE: V37_INTELLIGENCE_VALIDATION_VISIBLE_PROHIBITED,
        V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE: V37_INTELLIGENCE_VALIDATION_VISIBLE_UNSUPPORTED,
        V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE: V37_INTELLIGENCE_VALIDATION_VISIBLE_UNKNOWN,
    }
    for finding in aggregation.findings:
        status = status_map.get(finding.finding_classification)
        if status:
            findings.append(_finding(status, "intelligence_finding", finding.finding_id, f"{finding.finding_classification} remains fail-visible", "visibility"))


def _require_source(findings, source_types: set[str], source_type: str, status: str, aggregation_id: str) -> None:
    if source_type not in source_types:
        findings.append(_finding(status, "aggregation", aggregation_id, f"missing {source_type} evidence source"))


def _hidden_count(aggregations: tuple[V37GraphPlanningIntelligenceAggregation, ...], classification: str) -> int:
    return sum(
        1
        for aggregation in aggregations
        for finding in aggregation.findings
        if finding.finding_classification == classification and (finding.hidden or not finding.fail_visible)
    )


def _accidental_execution_authorization(aggregation: V37GraphPlanningIntelligenceAggregation) -> bool:
    blocked_phrases = (
        "should execute",
        "recommend execution",
        "select runtime path",
        "authorize orchestration",
        "rank for execution",
        "runtime guidance",
    )
    return any(
        (
            aggregation.graph_execution_enabled,
            aggregation.aggregation_driven_execution_enabled,
            aggregation.orchestration_selection_enabled,
            aggregation.routing_enabled,
            aggregation.scheduling_enabled,
            aggregation.dispatch_enabled,
            aggregation.graph_traversal_execution_enabled,
            aggregation.recommendation_enabled,
            aggregation.runtime_decision_making_enabled,
            aggregation.path_ranking_for_execution_enabled,
            aggregation.scenario_selection_for_execution_enabled,
            aggregation.executable_planning_insights_enabled,
            any(
                insight.recommends_execution
                or insight.selects_runtime_path
                or insight.authorizes_orchestration
                or any(phrase in insight.summary.lower() for phrase in blocked_phrases)
                for insight in aggregation.insights
            ),
        )
    )


def _finding(status: str, subject_type: str, subject_id: str, message: str, severity: str = "error") -> V37GraphIntelligenceValidationFinding:
    return V37GraphIntelligenceValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
