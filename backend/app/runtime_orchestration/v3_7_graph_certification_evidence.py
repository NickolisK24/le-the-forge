"""Deterministic continuity certification evidence for v3.7 graph planning."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .v3_7_graph_certification_models import (
    V37_CERTIFICATION_FINDING_BLOCKED,
    V37_CERTIFICATION_FINDING_CLASSIFICATIONS,
    V37_CERTIFICATION_FINDING_CONTINUITY_CERTIFIED,
    V37_CERTIFICATION_FINDING_CONTINUITY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_CERTIFIED,
    V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_EXPLAINABILITY_CERTIFIED,
    V37_CERTIFICATION_FINDING_EXPLAINABILITY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_FAILED,
    V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED,
    V37_CERTIFICATION_FINDING_INTEGRITY_CERTIFIED,
    V37_CERTIFICATION_FINDING_INTEGRITY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_PASSED,
    V37_CERTIFICATION_FINDING_PROVENANCE_CERTIFIED,
    V37_CERTIFICATION_FINDING_PROVENANCE_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_REPLAY_CERTIFIED,
    V37_CERTIFICATION_FINDING_REPLAY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_ROLLBACK_CERTIFIED,
    V37_CERTIFICATION_FINDING_ROLLBACK_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_SCOPE_COMPLETE,
    V37_CERTIFICATION_FINDING_SCOPE_INCOMPLETE,
    V37_CERTIFICATION_FINDING_WARNING,
    V37_CERTIFICATION_OUTCOME_BLOCKED,
    V37_CERTIFICATION_OUTCOME_CERTIFIED,
    V37_CERTIFICATION_OUTCOME_UNCERTIFIED,
    V37GraphCertificationEvidence,
    V37GraphCertificationFinding,
    V37GraphCertificationMetadata,
    V37GraphCertificationReplayEvidence,
    V37GraphPlanningContinuityCertification,
    export_v3_7_graph_certification_finding,
)
from .v3_7_graph_certification_scope import (
    build_v3_7_graph_certification_identity,
    build_v3_7_graph_certification_scope,
    certification_scope_is_complete,
)
from .v3_7_graph_integrity_audit import (
    V37_GRAPH_INTEGRITY_AUDIT_STABLE,
    audit_v3_7_graph_integrity,
)
from .v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from .v3_7_graph_integrity_explainability import (
    V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_integrity,
)
from .v3_7_graph_integrity_models import hash_v3_7_graph_integrity_enforcement_result
from .v3_7_graph_integrity_provenance import (
    V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_integrity_provenance,
)
from .v3_7_graph_integrity_replay import validate_v3_7_graph_integrity_replay_evidence
from .v3_7_graph_integrity_validation import (
    V37_GRAPH_INTEGRITY_VALIDATION_STABLE,
    validate_v3_7_graph_integrity,
)
from .v3_7_graph_models import default_v3_7_graph_provenance


def build_v3_7_graph_planning_continuity_certification() -> V37GraphPlanningContinuityCertification:
    identity = build_v3_7_graph_certification_identity()
    scope = build_v3_7_graph_certification_scope(identity)
    integrity = enforce_v3_7_graph_planning_integrity()
    integrity_validation = validate_v3_7_graph_integrity((integrity,))
    integrity_audit = audit_v3_7_graph_integrity(integrity)
    integrity_provenance = audit_v3_7_graph_integrity_provenance(integrity)
    integrity_explainability = explain_v3_7_graph_integrity(integrity)
    integrity_replay = validate_v3_7_graph_integrity_replay_evidence(integrity)
    references_by_type = _references_by_type(scope)
    all_scope_references = tuple(reference.reference_id for reference in scope.references)
    continuity_hashes = tuple(
        sorted(
            set(reference.artifact_hash for reference in scope.references)
            | set(hash_value for reference in scope.references for hash_value in reference.continuity_hashes)
            | {
                hash_v3_7_graph_integrity_enforcement_result(integrity),
                integrity_validation.deterministic_validation_hash,
                integrity_audit.deterministic_audit_hash,
                integrity_provenance.deterministic_provenance_hash,
                integrity_explainability.deterministic_explainability_hash,
            }
        )
    )
    evidence = V37GraphCertificationEvidence(
        evidence_id="v3_7_graph_certification_evidence_default",
        certification_id=identity.certification_id,
        scope_id=scope.identity.scope_id,
        graph_evidence_references=references_by_type["graph_foundations"],
        governance_evidence_references=references_by_type["governance"],
        compatibility_evidence_references=references_by_type["compatibility"],
        evaluation_evidence_references=references_by_type["evaluation"],
        session_evidence_references=references_by_type["session"],
        scenario_evidence_references=references_by_type["scenario"],
        aggregation_evidence_references=references_by_type["aggregation"],
        integrity_evidence_references=references_by_type["integrity"],
        continuity_hashes=continuity_hashes,
        provenance_references=tuple(
            sorted(
                set(scope.provenance.provenance_id for _ in (scope,))
                | set(reference for item in scope.references for reference in item.provenance_references)
                | {integrity.provenance.provenance_id, integrity.policy.provenance.provenance_id}
            )
        ),
        explainability_references=tuple(
            sorted(
                set(reference for item in scope.references for reference in item.explainability_references)
                | set(integrity.explainability_reference_ids)
                | {"v3_7_graph_certification_explainability"}
            )
        ),
        replay_references=tuple(item.replay_evidence_id for item in integrity.replay_evidence),
        rollback_references=integrity.rollback_continuity_references,
        execution_boundary_references=("v3_7_graph_certification_execution_boundary",),
    )
    totals = {
        "scope_complete": certification_scope_is_complete(scope),
        "continuity_certified": bool(continuity_hashes)
        and integrity_validation.deterministic_hash_stable
        and integrity_audit.deterministic_hash_stable,
        "provenance_certified": integrity_provenance.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
        "explainability_certified": integrity_explainability.explainability_status == V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
        "replay_certified": integrity_replay["replay_continuity_preserved"]
        and integrity_replay["non_executable_replay_evidence"]
        and not integrity_replay["runtime_replay"],
        "rollback_certified": integrity_replay["rollback_continuity_preserved"],
        "integrity_certified": integrity_validation.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_STABLE
        and integrity_audit.audit_status == V37_GRAPH_INTEGRITY_AUDIT_STABLE,
        "execution_boundary_certified": _execution_boundary_certified(integrity),
        "hidden_risk_state_detected": any(
            (
                integrity_validation.hidden_prohibited_finding_count,
                integrity_validation.hidden_unsupported_finding_count,
                integrity_validation.hidden_unknown_finding_count,
            )
        ),
    }
    findings = build_v3_7_graph_certification_findings(totals, all_scope_references)
    outcome = _certification_outcome(findings, totals)
    replay_evidence = (
        V37GraphCertificationReplayEvidence(
            replay_evidence_id="v3_7_graph_certification_replay_evidence_default",
            certification_id=identity.certification_id,
            scope_id=scope.identity.scope_id,
            certification_outcome=outcome,
            finding_references=tuple(finding.finding_id for finding in findings),
            evidence_source_references=all_scope_references,
            provenance_references=evidence.provenance_references,
            explainability_references=evidence.explainability_references,
            continuity_hashes=continuity_hashes,
        ),
    )
    return V37GraphPlanningContinuityCertification(
        identity=identity,
        metadata=(
            V37GraphCertificationMetadata("certification_semantics", "planning_continuity_certification"),
            V37GraphCertificationMetadata("runtime_capability", "none"),
            V37GraphCertificationMetadata("readiness_boundary", "certified_continuity_not_runtime_readiness"),
        ),
        scope=scope,
        evidence=evidence,
        certification_outcome=outcome,
        findings=findings,
        replay_evidence=replay_evidence,
        rollback_continuity_references=integrity.rollback_continuity_references,
        provenance=default_v3_7_graph_provenance(identity.certification_id, "graph_planning_continuity_certification"),
        explainability_reference_ids=("v3_7_graph_certification_explainability",),
        continuity_hash_references=continuity_hashes,
    )


def build_v3_7_graph_certification_findings(
    totals: dict[str, bool],
    evidence_references: tuple[str, ...],
) -> tuple[V37GraphCertificationFinding, ...]:
    specs = (
        (V37_CERTIFICATION_FINDING_PASSED, "certification", "passed", True, False, "certification passed when all continuity evidence is certified"),
        (V37_CERTIFICATION_FINDING_FAILED, "certification", "failed", False, not totals["integrity_certified"], "certification failures remain visible"),
        (V37_CERTIFICATION_FINDING_BLOCKED, "certification", "blocked", False, False, "blocked certification states remain visible"),
        (V37_CERTIFICATION_FINDING_WARNING, "certification", "warning", True, False, "warning certification states remain visible"),
        (V37_CERTIFICATION_FINDING_SCOPE_COMPLETE, "scope", "complete", totals["scope_complete"], False, "certification scope is complete"),
        (V37_CERTIFICATION_FINDING_SCOPE_INCOMPLETE, "scope", "incomplete", False, not totals["scope_complete"], "incomplete scope blocks certification"),
        (V37_CERTIFICATION_FINDING_CONTINUITY_CERTIFIED, "continuity", "certified", totals["continuity_certified"], False, "continuity evidence is certified"),
        (V37_CERTIFICATION_FINDING_CONTINUITY_UNCERTIFIED, "continuity", "uncertified", False, not totals["continuity_certified"], "uncertified continuity blocks certification"),
        (V37_CERTIFICATION_FINDING_PROVENANCE_CERTIFIED, "provenance", "certified", totals["provenance_certified"], False, "provenance continuity is certified"),
        (V37_CERTIFICATION_FINDING_PROVENANCE_UNCERTIFIED, "provenance", "uncertified", False, not totals["provenance_certified"], "uncertified provenance blocks certification"),
        (V37_CERTIFICATION_FINDING_EXPLAINABILITY_CERTIFIED, "explainability", "certified", totals["explainability_certified"], False, "explainability continuity is certified"),
        (V37_CERTIFICATION_FINDING_EXPLAINABILITY_UNCERTIFIED, "explainability", "uncertified", False, not totals["explainability_certified"], "uncertified explainability blocks certification"),
        (V37_CERTIFICATION_FINDING_REPLAY_CERTIFIED, "replay", "certified", totals["replay_certified"], False, "replay continuity is certified"),
        (V37_CERTIFICATION_FINDING_REPLAY_UNCERTIFIED, "replay", "uncertified", False, not totals["replay_certified"], "uncertified replay blocks certification"),
        (V37_CERTIFICATION_FINDING_ROLLBACK_CERTIFIED, "rollback", "certified", totals["rollback_certified"], False, "rollback continuity is certified"),
        (V37_CERTIFICATION_FINDING_ROLLBACK_UNCERTIFIED, "rollback", "uncertified", False, not totals["rollback_certified"], "uncertified rollback blocks certification"),
        (V37_CERTIFICATION_FINDING_INTEGRITY_CERTIFIED, "integrity", "certified", totals["integrity_certified"], False, "integrity enforcement is certified"),
        (V37_CERTIFICATION_FINDING_INTEGRITY_UNCERTIFIED, "integrity", "uncertified", False, not totals["integrity_certified"], "uncertified integrity blocks certification"),
        (V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_CERTIFIED, "execution_boundary", "certified", totals["execution_boundary_certified"], False, "execution boundary is certified"),
        (V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_UNCERTIFIED, "execution_boundary", "uncertified", False, not totals["execution_boundary_certified"], "execution-boundary failures block certification"),
        (V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED, "risk_visibility", "hidden", False, totals["hidden_risk_state_detected"], "hidden risk states block certification"),
    )
    findings = []
    for classification, subject_type, subject_id, certified, active, summary in specs:
        severity = "blocked" if active else ("info" if certified else "visibility")
        findings.append(
            V37GraphCertificationFinding(
                finding_id=f"v3_7_graph_certification_{classification}",
                finding_classification=classification,
                subject_type=subject_type,
                subject_id=f"{subject_id}:{int(active)}",
                severity=severity,
                summary=summary,
                evidence_references=evidence_references,
                fail_visible=True,
                hidden=False,
                active_violation=active,
                blocks_certification=active,
            )
        )
    return tuple(sorted(findings, key=lambda item: item.finding_id))


def count_v3_7_graph_certification_findings_by_classification(
    findings: tuple[V37GraphCertificationFinding, ...],
) -> dict[str, int]:
    counts = Counter(finding.finding_classification for finding in findings)
    return {
        classification: counts.get(classification, 0)
        for classification in V37_CERTIFICATION_FINDING_CLASSIFICATIONS
    }


def export_v3_7_graph_certification_finding_records(
    findings: tuple[V37GraphCertificationFinding, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_certification_finding(finding)
        for finding in sorted(findings, key=lambda item: item.finding_id)
    ]


def _references_by_type(scope) -> dict[str, tuple[str, ...]]:
    by_type: dict[str, list[str]] = {
        "graph_foundations": [],
        "governance": [],
        "compatibility": [],
        "evaluation": [],
        "session": [],
        "scenario": [],
        "aggregation": [],
        "integrity": [],
    }
    for reference in scope.references:
        by_type.setdefault(reference.reference_type, []).append(reference.reference_id)
    return {key: tuple(sorted(value)) for key, value in by_type.items()}


def _certification_outcome(findings, totals: dict[str, bool]) -> str:
    if any(finding.blocks_certification for finding in findings):
        return V37_CERTIFICATION_OUTCOME_BLOCKED
    if not all(
        totals[key]
        for key in (
            "scope_complete",
            "continuity_certified",
            "provenance_certified",
            "explainability_certified",
            "replay_certified",
            "rollback_certified",
            "integrity_certified",
            "execution_boundary_certified",
        )
    ):
        return V37_CERTIFICATION_OUTCOME_UNCERTIFIED
    return V37_CERTIFICATION_OUTCOME_CERTIFIED


def _execution_boundary_certified(integrity) -> bool:
    return all(
        (
            integrity.integrity_enforcement_is_non_executable,
            integrity.valid_integrity_does_not_authorize_execution,
            integrity.integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
            not integrity.graph_execution_enabled,
            not integrity.integrity_driven_execution_enabled,
            not integrity.orchestration_authorization_enabled,
            not integrity.routing_enabled,
            not integrity.scheduling_enabled,
            not integrity.dispatch_enabled,
            not integrity.traversal_logic_enabled,
            not integrity.path_selection_enabled,
            not integrity.scenario_selection_enabled,
            not integrity.optimization_engine_enabled,
            not integrity.recommendation_enabled,
            not integrity.runtime_decision_making_enabled,
            not integrity.execution_gates_enabled,
            not integrity.callable_orchestration_flows_enabled,
            not integrity.runtime_control_system_enabled,
        )
    )
