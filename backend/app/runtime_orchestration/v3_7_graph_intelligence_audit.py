"""Deterministic audit infrastructure for v3.7 planning intelligence aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_intelligence_aggregation import (
    build_v3_7_graph_planning_intelligence_aggregation,
    graph_intelligence_identity_key,
)
from .v3_7_graph_intelligence_models import (
    V37_INTELLIGENCE_FINDING_BLOCKED_VISIBLE,
    V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
    V37GraphPlanningIntelligenceAggregation,
    validate_v3_7_graph_intelligence_hash_stability,
    validate_v3_7_graph_intelligence_serialization_stability,
)


V37_GRAPH_INTELLIGENCE_AUDIT_STABLE = "v3_7_graph_intelligence_audit_stable"
V37_GRAPH_INTELLIGENCE_AUDIT_FAILED = "v3_7_graph_intelligence_audit_failed"
V37_INTELLIGENCE_AUDIT_VISIBLE_BLOCKED = "v3_7_graph_intelligence_visible_blocked"
V37_INTELLIGENCE_AUDIT_VISIBLE_UNSUPPORTED = "v3_7_graph_intelligence_visible_unsupported"
V37_INTELLIGENCE_AUDIT_VISIBLE_PROHIBITED = "v3_7_graph_intelligence_visible_prohibited"
V37_INTELLIGENCE_AUDIT_VISIBLE_UNKNOWN = "v3_7_graph_intelligence_visible_unknown"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_IDENTITY = "v3_7_graph_intelligence_audit_blocked_by_identity"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EVIDENCE_SOURCE = "v3_7_graph_intelligence_audit_blocked_by_evidence_source"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_GOVERNANCE = "v3_7_graph_intelligence_audit_blocked_by_governance"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_COMPATIBILITY = "v3_7_graph_intelligence_audit_blocked_by_compatibility"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EVALUATION = "v3_7_graph_intelligence_audit_blocked_by_evaluation"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_SESSION = "v3_7_graph_intelligence_audit_blocked_by_session"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_SCENARIO = "v3_7_graph_intelligence_audit_blocked_by_scenario"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_REPLAY = "v3_7_graph_intelligence_audit_blocked_by_replay"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_ROLLBACK = "v3_7_graph_intelligence_audit_blocked_by_rollback"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_PROVENANCE = "v3_7_graph_intelligence_audit_blocked_by_provenance"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_intelligence_audit_blocked_by_explainability"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_FINDING_VISIBILITY = "v3_7_graph_intelligence_audit_blocked_by_finding_visibility"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_SERIALIZATION = "v3_7_graph_intelligence_audit_blocked_by_serialization"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_HASH = "v3_7_graph_intelligence_audit_blocked_by_hash"
V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_intelligence_audit_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphIntelligenceAuditFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphIntelligenceAuditResult:
    audit_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    aggregation_identity_stable: bool
    evidence_source_continuity_preserved: bool
    governance_aggregation_continuity_preserved: bool
    compatibility_aggregation_continuity_preserved: bool
    evaluation_aggregation_continuity_preserved: bool
    session_aggregation_continuity_preserved: bool
    scenario_aggregation_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    fail_visible_finding_preservation: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    non_execution_guarantee_preserved: bool
    deterministic_audit_hash: str
    findings: tuple[V37GraphIntelligenceAuditFinding, ...]


def audit_v3_7_graph_intelligence(
    aggregation: V37GraphPlanningIntelligenceAggregation | None = None,
) -> V37GraphIntelligenceAuditResult:
    planning_intelligence = aggregation or build_v3_7_graph_planning_intelligence_aggregation()
    findings: list[V37GraphIntelligenceAuditFinding] = []
    _add_visibility_findings(planning_intelligence, findings)
    source_types = {source.source_type for source in planning_intelligence.evidence_sources}
    identity_ok = planning_intelligence.identity.stable_identity_key == graph_intelligence_identity_key(planning_intelligence.identity)
    _append_error_if_false(findings, identity_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_IDENTITY, "aggregation", planning_intelligence.identity.aggregation_id, "aggregation identity is unstable")
    evidence_source_ok = {"graph_foundations", "governance", "compatibility", "evaluation", "session", "scenario"}.issubset(source_types) and all(
        source.source_hash and source.provenance_references and source.explainability_references and source.continuity_references
        for source in planning_intelligence.evidence_sources
    )
    _append_error_if_false(findings, evidence_source_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EVIDENCE_SOURCE, "aggregation", planning_intelligence.identity.aggregation_id, "evidence-source continuity is incomplete")
    governance_ok = planning_intelligence.totals.governance_finding_total > 0 and "governance" in source_types
    compatibility_ok = planning_intelligence.totals.compatibility_finding_total > 0 and "compatibility" in source_types
    evaluation_ok = planning_intelligence.totals.evaluation_finding_total > 0 and "evaluation" in source_types
    session_ok = planning_intelligence.totals.session_finding_total > 0 and "session" in source_types
    scenario_ok = planning_intelligence.totals.scenario_finding_total > 0 and "scenario" in source_types
    _append_error_if_false(findings, governance_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_GOVERNANCE, "aggregation", planning_intelligence.identity.aggregation_id, "governance aggregation continuity is incomplete")
    _append_error_if_false(findings, compatibility_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_COMPATIBILITY, "aggregation", planning_intelligence.identity.aggregation_id, "compatibility aggregation continuity is incomplete")
    _append_error_if_false(findings, evaluation_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EVALUATION, "aggregation", planning_intelligence.identity.aggregation_id, "evaluation aggregation continuity is incomplete")
    _append_error_if_false(findings, session_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_SESSION, "aggregation", planning_intelligence.identity.aggregation_id, "session aggregation continuity is incomplete")
    _append_error_if_false(findings, scenario_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_SCENARIO, "aggregation", planning_intelligence.identity.aggregation_id, "scenario aggregation continuity is incomplete")
    replay_ok = all(
        item.non_executable_replay_evidence
        and not item.runtime_replay
        and not item.execution_authorization
        and item.evidence_source_references
        and item.graph_evidence_references
        and item.governance_evidence_references
        and item.compatibility_evidence_references
        and item.evaluation_evidence_references
        and item.session_evidence_references
        and item.scenario_evidence_references
        and item.continuity_hashes
        for item in planning_intelligence.replay_evidence
    )
    rollback_ok = bool(planning_intelligence.rollback_continuity_references)
    provenance_ok = bool(planning_intelligence.provenance.provenance_id) and all(source.provenance_references for source in planning_intelligence.evidence_sources)
    explainability_ok = bool(planning_intelligence.explainability_reference_ids) and all(source.explainability_references for source in planning_intelligence.evidence_sources)
    fail_visible_ok = all(finding.fail_visible and not finding.hidden for finding in planning_intelligence.findings)
    serialization = validate_v3_7_graph_intelligence_serialization_stability(planning_intelligence)
    hashing = validate_v3_7_graph_intelligence_hash_stability(planning_intelligence)
    non_execution_ok = _non_execution_guarantee_preserved(planning_intelligence)
    _append_error_if_false(findings, replay_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_REPLAY, "aggregation", planning_intelligence.identity.aggregation_id, "replay continuity is incomplete")
    _append_error_if_false(findings, rollback_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_ROLLBACK, "aggregation", planning_intelligence.identity.aggregation_id, "rollback continuity is incomplete")
    _append_error_if_false(findings, provenance_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_PROVENANCE, "aggregation", planning_intelligence.identity.aggregation_id, "provenance continuity is incomplete")
    _append_error_if_false(findings, explainability_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EXPLAINABILITY, "aggregation", planning_intelligence.identity.aggregation_id, "explainability continuity is incomplete")
    _append_error_if_false(findings, fail_visible_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_FINDING_VISIBILITY, "aggregation", planning_intelligence.identity.aggregation_id, "aggregated finding visibility is incomplete")
    _append_error_if_false(findings, serialization["stable"], V37_INTELLIGENCE_AUDIT_BLOCKED_BY_SERIALIZATION, "aggregation", planning_intelligence.identity.aggregation_id, "aggregation serialization is unstable")
    _append_error_if_false(findings, hashing["stable"], V37_INTELLIGENCE_AUDIT_BLOCKED_BY_HASH, "aggregation", planning_intelligence.identity.aggregation_id, "aggregation hash is unstable")
    _append_error_if_false(findings, non_execution_ok, V37_INTELLIGENCE_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY, "aggregation", planning_intelligence.identity.aggregation_id, "aggregation exposed execution capability")
    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphIntelligenceAuditResult(
        audit_status=V37_GRAPH_INTELLIGENCE_AUDIT_STABLE if error_count == 0 else V37_GRAPH_INTELLIGENCE_AUDIT_FAILED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        aggregation_identity_stable=identity_ok,
        evidence_source_continuity_preserved=evidence_source_ok,
        governance_aggregation_continuity_preserved=governance_ok,
        compatibility_aggregation_continuity_preserved=compatibility_ok,
        evaluation_aggregation_continuity_preserved=evaluation_ok,
        session_aggregation_continuity_preserved=session_ok,
        scenario_aggregation_continuity_preserved=scenario_ok,
        replay_continuity_preserved=replay_ok,
        rollback_continuity_preserved=rollback_ok,
        provenance_continuity_preserved=provenance_ok,
        explainability_continuity_preserved=explainability_ok,
        fail_visible_finding_preservation=fail_visible_ok,
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=non_execution_ok,
        deterministic_audit_hash="",
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_audit_hash=hash_v3_7_graph_intelligence_audit_result(result))


def export_v3_7_graph_intelligence_audit_finding(finding: V37GraphIntelligenceAuditFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_intelligence_audit_result(result: V37GraphIntelligenceAuditResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_intelligence_audit_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_intelligence_audit_result(result: V37GraphIntelligenceAuditResult) -> str:
    return stable_serialize(export_v3_7_graph_intelligence_audit_result(result))


def hash_v3_7_graph_intelligence_audit_result(result: V37GraphIntelligenceAuditResult) -> str:
    data = export_v3_7_graph_intelligence_audit_result(result)
    data.pop("deterministic_audit_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(aggregation, findings: list[V37GraphIntelligenceAuditFinding]) -> None:
    status_map = {
        V37_INTELLIGENCE_FINDING_BLOCKED_VISIBLE: V37_INTELLIGENCE_AUDIT_VISIBLE_BLOCKED,
        V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE: V37_INTELLIGENCE_AUDIT_VISIBLE_UNSUPPORTED,
        V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE: V37_INTELLIGENCE_AUDIT_VISIBLE_PROHIBITED,
        V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE: V37_INTELLIGENCE_AUDIT_VISIBLE_UNKNOWN,
    }
    for finding in aggregation.findings:
        status = status_map.get(finding.finding_classification)
        if status:
            findings.append(_finding(status, "intelligence_finding", finding.finding_id, f"{finding.finding_classification} remains fail-visible", "visibility"))


def _append_error_if_false(findings, condition: bool, status: str, subject_type: str, subject_id: str, message: str) -> None:
    if not condition:
        findings.append(_finding(status, subject_type, subject_id, message))


def _non_execution_guarantee_preserved(aggregation) -> bool:
    return all(
        (
            aggregation.aggregation_is_non_executable,
            aggregation.planning_evidence_summarization_only,
            aggregation.aggregated_insights_are_not_recommendations,
            aggregation.aggregated_insights_do_not_authorize_execution,
            aggregation.aggregation_does_not_select_graph_paths,
            aggregation.aggregation_does_not_select_scenarios_for_execution,
            aggregation.aggregation_does_not_enable_routing_scheduling_dispatch_traversal_runtime_orchestration,
            not aggregation.graph_execution_enabled,
            not aggregation.aggregation_driven_execution_enabled,
            not aggregation.orchestration_selection_enabled,
            not aggregation.routing_enabled,
            not aggregation.scheduling_enabled,
            not aggregation.dispatch_enabled,
            not aggregation.graph_traversal_execution_enabled,
            not aggregation.optimization_engine_enabled,
            not aggregation.recommendation_enabled,
            not aggregation.autonomous_orchestration_enabled,
            not aggregation.runtime_mutation_enabled,
            not aggregation.persistent_runtime_writes_enabled,
            not aggregation.runtime_decision_making_enabled,
            not aggregation.path_ranking_for_execution_enabled,
            not aggregation.scenario_selection_for_execution_enabled,
            not aggregation.executable_planning_insights_enabled,
            not aggregation.orchestration_state_machine_enabled,
            all(not insight.recommends_execution and not insight.selects_runtime_path and not insight.authorizes_orchestration for insight in aggregation.insights),
            all(not finding.execution_recommendation and not finding.runtime_path_selection for finding in aggregation.findings),
            all(evidence.non_executable_replay_evidence and not evidence.runtime_replay and not evidence.execution_authorization for evidence in aggregation.replay_evidence),
        )
    )


def _finding(status: str, subject_type: str, subject_id: str, message: str, severity: str = "error") -> V37GraphIntelligenceAuditFinding:
    return V37GraphIntelligenceAuditFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
