"""Deterministic v3.7 closeout and v3.8 planning-readiness audit."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .v3_7_closeout_readiness_models import (
    V37_CLOSEOUT_FINDING_CLASSIFICATIONS,
    V37_CLOSEOUT_FINDING_CLOSEOUT_BLOCKED,
    V37_CLOSEOUT_FINDING_CLOSEOUT_READY,
    V37_CLOSEOUT_FINDING_CONTINUITY_BROKEN,
    V37_CLOSEOUT_FINDING_CONTINUITY_PRESERVED,
    V37_CLOSEOUT_FINDING_DETERMINISTIC,
    V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_BROKEN,
    V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_PRESERVED,
    V37_CLOSEOUT_FINDING_EXPLAINABILITY_SAFE,
    V37_CLOSEOUT_FINDING_HIDDEN_RISK_DETECTED,
    V37_CLOSEOUT_FINDING_NON_EXECUTABLE,
    V37_CLOSEOUT_FINDING_PROVENANCE_SAFE,
    V37_CLOSEOUT_FINDING_READINESS_BLOCKED,
    V37_CLOSEOUT_FINDING_READINESS_CERTIFIED,
    V37_CLOSEOUT_FINDING_REPLAY_SAFE,
    V37_CLOSEOUT_FINDING_ROLLBACK_SAFE,
    V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING,
    V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING,
    V3_7_CLOSEOUT_PHASE_ID,
    V37CloseoutPhaseEvidence,
    V37CloseoutReadinessFinding,
    V37CloseoutReadinessInput,
    V37CloseoutReadinessResult,
    export_v3_7_closeout_readiness_result,
    hash_v3_7_closeout_readiness_result,
)
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
from .v3_7_graph_certification_validation import (
    V37_GRAPH_CERTIFICATION_VALIDATION_STABLE,
    validate_v3_7_graph_certification,
)


V37_CLOSEOUT_VALIDATION_STABLE = "v3_7_closeout_validation_stable"
V37_CLOSEOUT_VALIDATION_BLOCKED = "v3_7_closeout_validation_blocked"

PHASE_CHAIN: tuple[tuple[int, str, str, str], ...] = (
    (1, "graph_foundations", "Graph Foundations", "graph_foundations"),
    (2, "governance_boundaries", "Governance Boundary Intelligence", "governance"),
    (3, "compatibility_reasoning", "Compatibility Reasoning", "compatibility"),
    (4, "evaluation_reasoning", "Evaluation Reasoning", "evaluation"),
    (5, "planning_sessions", "Planning Sessions", "session"),
    (6, "planning_scenarios", "Planning Scenarios", "scenario"),
    (7, "intelligence_aggregation", "Intelligence Aggregation", "aggregation"),
    (8, "integrity_enforcement", "Integrity Enforcement", "integrity"),
    (9, "continuity_certification", "Continuity Certification", "certification"),
)


def default_v3_7_closeout_readiness_input() -> V37CloseoutReadinessInput:
    return V37CloseoutReadinessInput()


def audit_v3_7_closeout_and_v3_8_readiness(
    source: V37CloseoutReadinessInput | None = None,
) -> V37CloseoutReadinessResult:
    request = source or default_v3_7_closeout_readiness_input()
    certification = request.certification or build_v3_7_graph_planning_continuity_certification()
    assert isinstance(certification, V37GraphPlanningContinuityCertification)
    certification_validation = validate_v3_7_graph_certification((certification,))
    certification_audit = audit_v3_7_graph_certification(certification)
    certification_provenance = audit_v3_7_graph_certification_provenance(certification)
    certification_explainability = explain_v3_7_graph_certification(certification)
    certification_replay = validate_v3_7_graph_certification_replay_evidence(certification)
    certification_serialization = validate_v3_7_graph_certification_serialization_stability(certification)
    certification_hashing = validate_v3_7_graph_certification_hash_stability(certification)
    phase_evidence = _phase_evidence(certification, request.omitted_phase_ids)
    missing_phase_ids = _missing_phase_ids(phase_evidence)
    hidden_risk_detected = request.force_hidden_risk_detected or any(
        (
            certification_validation.hidden_prohibited_finding_count,
            certification_validation.hidden_unsupported_finding_count,
            certification_validation.hidden_unknown_finding_count,
        )
    )
    replay_safe = certification_replay["replay_continuity_preserved"] and not request.force_missing_replay_evidence
    rollback_safe = certification_replay["rollback_continuity_preserved"] and not request.force_missing_rollback_evidence
    execution_boundary_preserved = _execution_boundary_preserved(certification) and not request.force_execution_boundary_violation
    provenance_safe = certification_provenance.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED
    explainability_safe = certification_explainability.explainability_status == V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE
    deterministic = certification_serialization["stable"] and certification_hashing["stable"]
    continuity_preserved = (
        len(missing_phase_ids) == 0
        and certification_validation.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_STABLE
        and certification_audit.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_STABLE
        and all(evidence.continuity_preserved for evidence in phase_evidence)
    )
    closeout_ready = all(
        (
            continuity_preserved,
            execution_boundary_preserved,
            replay_safe,
            rollback_safe,
            provenance_safe,
            explainability_safe,
            deterministic,
            not hidden_risk_detected,
            not request.manual_blocker_reasons,
        )
    )
    evidence_reference_ids = tuple(sorted(evidence.evidence_reference_id for evidence in phase_evidence))
    findings = _build_findings(
        closeout_ready=closeout_ready,
        readiness_certified=closeout_ready,
        continuity_preserved=continuity_preserved,
        execution_boundary_preserved=execution_boundary_preserved,
        replay_safe=replay_safe,
        rollback_safe=rollback_safe,
        provenance_safe=provenance_safe,
        explainability_safe=explainability_safe,
        deterministic=deterministic,
        non_executable=certification.certification_is_non_executable,
        hidden_risk_detected=hidden_risk_detected,
        evidence_references=evidence_reference_ids,
    )
    execution_boundary_violations = _execution_boundary_violation_count(
        certification,
        request.force_execution_boundary_violation,
    )
    validation_totals = {
        "validation_status": V37_CLOSEOUT_VALIDATION_STABLE if closeout_ready else V37_CLOSEOUT_VALIDATION_BLOCKED,
        "valid": closeout_ready,
        "finding_count": len(findings),
        "error_count": sum(1 for finding in findings if finding.blocks_closeout),
        "visibility_finding_count": sum(1 for finding in findings if finding.fail_visible and not finding.hidden),
        "total_phases_audited": len(phase_evidence),
        "missing_phase_continuity_count": len(missing_phase_ids),
        "hidden_prohibited_state_count": 1 if hidden_risk_detected else 0,
        "hidden_unsupported_state_count": 1 if hidden_risk_detected else 0,
        "hidden_unknown_state_count": 1 if hidden_risk_detected else 0,
        "missing_replay_evidence_count": 0 if replay_safe else 1,
        "missing_rollback_evidence_count": 0 if rollback_safe else 1,
        "execution_boundary_violation_count": execution_boundary_violations,
        "manual_blocker_count": len(request.manual_blocker_reasons),
    }
    continuity_validation_totals = {
        "deterministic_serialization_continuity": certification_serialization["stable"],
        "deterministic_hashing_continuity": certification_hashing["stable"],
        "governance_continuity": certification_audit.governance_continuity_preserved,
        "compatibility_continuity": certification_audit.compatibility_continuity_preserved,
        "evaluation_continuity": certification_audit.evaluation_continuity_preserved,
        "planning_session_continuity": certification_audit.session_continuity_preserved,
        "planning_scenario_continuity": certification_audit.scenario_continuity_preserved,
        "aggregation_continuity": certification_audit.aggregation_continuity_preserved,
        "integrity_continuity": certification_audit.integrity_continuity_preserved,
        "certification_continuity": certification_audit.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_STABLE,
        "provenance_continuity": provenance_safe,
        "explainability_continuity": explainability_safe,
        "replay_continuity": replay_safe,
        "rollback_continuity": rollback_safe,
        "fail_visible_continuity": all(finding.fail_visible and not finding.hidden for finding in findings),
        "execution_boundary_continuity": execution_boundary_preserved,
    }
    execution_boundary_audit_totals = {
        "execution_authorization_absent": not certification.orchestration_authorization_enabled,
        "orchestration_routing_absent": not certification.routing_enabled,
        "orchestration_scheduling_absent": not certification.scheduling_enabled,
        "orchestration_dispatch_absent": not certification.dispatch_enabled,
        "traversal_authorization_absent": not certification.traversal_logic_enabled,
        "runtime_path_selection_absent": not certification.path_selection_enabled,
        "scenario_execution_selection_absent": not certification.scenario_selection_enabled,
        "execution_recommendation_absent": not certification.recommendation_enabled,
        "optimization_for_execution_absent": not certification.optimization_engine_enabled,
        "callable_execution_flow_absent": not certification.executable_certification_gates_enabled,
        "runtime_orchestration_engine_absent": not certification.runtime_control_system_enabled,
        "execution_boundary_preserved": execution_boundary_preserved,
        "execution_boundary_violation_count": execution_boundary_violations,
    }
    replay_rollback_totals = {
        "replay_evidence_count": certification_replay["replay_evidence_count"],
        "rollback_reference_count": certification_replay["rollback_reference_count"],
        "replay_safe": replay_safe,
        "rollback_safe": rollback_safe,
        "runtime_replay_detected": certification_replay["runtime_replay"],
        "runtime_readiness_certification_detected": certification_replay["runtime_readiness_certification"],
    }
    provenance_explainability_totals = {
        "provenance_record_count": certification_provenance.provenance_record_count,
        "explanation_count": certification_explainability.explanation_count,
        "provenance_safe": provenance_safe,
        "explainability_safe": explainability_safe,
        "graph_provenance_preserved": certification_provenance.graph_provenance_preserved,
        "governance_provenance_preserved": certification_provenance.governance_provenance_preserved,
        "compatibility_provenance_preserved": certification_provenance.compatibility_provenance_preserved,
        "evaluation_provenance_preserved": certification_provenance.evaluation_provenance_preserved,
        "session_provenance_preserved": certification_provenance.session_provenance_preserved,
        "scenario_provenance_preserved": certification_provenance.scenario_provenance_preserved,
        "aggregation_provenance_preserved": certification_provenance.aggregation_provenance_preserved,
        "integrity_provenance_preserved": certification_provenance.integrity_provenance_preserved,
        "certification_provenance_preserved": certification_provenance.certification_provenance_preserved,
    }
    deterministic_guarantees = {
        "certification_serialization_stable": certification_serialization["stable"],
        "certification_hash_stable": certification_hashing["stable"],
        "closeout_serialization_stable": True,
        "closeout_hash_stable": True,
        "certification_hash": hash_v3_7_graph_planning_continuity_certification(certification),
        "certification_validation_hash": certification_validation.deterministic_validation_hash,
        "certification_audit_hash": certification_audit.deterministic_audit_hash,
        "certification_provenance_hash": certification_provenance.deterministic_provenance_hash,
        "certification_explainability_hash": certification_explainability.deterministic_explainability_hash,
    }
    result = V37CloseoutReadinessResult(
        closeout_status=V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING
        if closeout_ready
        else V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING,
        v3_8_readiness_classification=V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING
        if closeout_ready
        else V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING,
        phase_id=V3_7_CLOSEOUT_PHASE_ID,
        total_phases_audited=len(phase_evidence),
        phase_evidence=phase_evidence,
        findings=findings,
        validation_totals=validation_totals,
        continuity_validation_totals=continuity_validation_totals,
        execution_boundary_audit_totals=execution_boundary_audit_totals,
        replay_rollback_totals=replay_rollback_totals,
        provenance_explainability_totals=provenance_explainability_totals,
        deterministic_guarantees=deterministic_guarantees,
        hidden_risk_totals={
            "hidden_risk_detected": hidden_risk_detected,
            "hidden_prohibited_state_count": validation_totals["hidden_prohibited_state_count"],
            "hidden_unsupported_state_count": validation_totals["hidden_unsupported_state_count"],
            "hidden_unknown_state_count": validation_totals["hidden_unknown_state_count"],
        },
        explanation_summary=_explanation_summary(closeout_ready),
        v3_8_allowed_expansion_summary=(
            "v3.8 may expand deterministic planning intelligence evidence",
            "v3.8 may expand structural governance, compatibility, evaluation, and continuity reasoning",
            "v3.8 may add additional non-executable planning audit evidence",
        ),
        v3_8_prohibited_expansion_summary=(
            "v3.8 may not enable runtime orchestration execution",
            "v3.8 may not enable routing, scheduling, dispatch, or traversal",
            "v3.8 may not authorize execution readiness",
            "v3.8 may not add optimization-for-execution or recommendation-to-execute behavior",
        ),
        provenance_references=tuple(sorted({ref for evidence in phase_evidence for ref in evidence.provenance_references})),
        explainability_references=tuple(sorted({ref for evidence in phase_evidence for ref in evidence.explainability_references})),
        replay_references=tuple(sorted({ref for evidence in phase_evidence for ref in evidence.replay_references})),
        rollback_references=tuple(sorted({ref for evidence in phase_evidence for ref in evidence.rollback_references})),
        readiness_for_v3_8_planning=closeout_ready,
        runtime_execution_readiness_certified=False,
        execution_authorization_enabled=request.force_execution_boundary_violation,
        orchestration_execution_enabled=False,
        routing_enabled=False,
        scheduling_enabled=False,
        dispatch_enabled=False,
        traversal_enabled=False,
        runtime_path_selection_enabled=False,
        scenario_execution_selection_enabled=False,
        execution_recommendation_enabled=False,
        optimization_for_execution_enabled=False,
        callable_execution_flow_enabled=False,
        runtime_orchestration_engine_enabled=False,
        runtime_mutation_enabled=False,
        persistent_runtime_writes_enabled=False,
        autonomous_orchestration_enabled=False,
    )
    result = replace(result, deterministic_closeout_hash=hash_v3_7_closeout_readiness_result(result))
    deterministic_guarantees = dict(result.deterministic_guarantees)
    deterministic_guarantees["closeout_hash"] = result.deterministic_closeout_hash
    return replace(result, deterministic_guarantees=deterministic_guarantees)


def export_v3_7_closeout_and_v3_8_readiness_result(result: V37CloseoutReadinessResult) -> dict[str, object]:
    return export_v3_7_closeout_readiness_result(result)


def count_v3_7_closeout_findings_by_classification(
    findings: tuple[V37CloseoutReadinessFinding, ...],
) -> dict[str, int]:
    counts = Counter(finding.finding_classification for finding in findings)
    return {classification: counts.get(classification, 0) for classification in V37_CLOSEOUT_FINDING_CLASSIFICATIONS}


def _phase_evidence(
    certification: V37GraphPlanningContinuityCertification,
    omitted_phase_ids: tuple[str, ...],
) -> tuple[V37CloseoutPhaseEvidence, ...]:
    refs_by_type = {reference.reference_type: reference for reference in certification.scope.references}
    phase_records: list[V37CloseoutPhaseEvidence] = []
    for phase_order, phase_id, phase_name, reference_type in PHASE_CHAIN:
        if phase_id in omitted_phase_ids:
            continue
        if reference_type == "certification":
            phase_records.append(
                V37CloseoutPhaseEvidence(
                    phase_order=phase_order,
                    phase_id=phase_id,
                    phase_name=phase_name,
                    reference_type=reference_type,
                    evidence_reference_id=certification.identity.certification_id,
                    artifact_id=certification.identity.certification_id,
                    artifact_hash=hash_v3_7_graph_planning_continuity_certification(certification),
                    provenance_references=(certification.provenance.provenance_id,),
                    explainability_references=certification.explainability_reference_ids,
                    continuity_hashes=certification.continuity_hash_references,
                    replay_references=tuple(item.replay_evidence_id for item in certification.replay_evidence),
                    rollback_references=certification.rollback_continuity_references,
                )
            )
            continue
        reference = refs_by_type[reference_type]
        phase_records.append(
            V37CloseoutPhaseEvidence(
                phase_order=phase_order,
                phase_id=phase_id,
                phase_name=phase_name,
                reference_type=reference.reference_type,
                evidence_reference_id=reference.reference_id,
                artifact_id=reference.artifact_id,
                artifact_hash=reference.artifact_hash,
                provenance_references=reference.provenance_references,
                explainability_references=reference.explainability_references,
                continuity_hashes=reference.continuity_hashes,
                replay_references=certification.evidence.replay_references,
                rollback_references=certification.evidence.rollback_references,
            )
        )
    return tuple(sorted(phase_records, key=lambda item: item.phase_order))


def _missing_phase_ids(phase_evidence: tuple[V37CloseoutPhaseEvidence, ...]) -> tuple[str, ...]:
    present = {evidence.phase_id for evidence in phase_evidence}
    required = {phase_id for _, phase_id, _, _ in PHASE_CHAIN}
    return tuple(sorted(required - present))


def _build_findings(
    *,
    closeout_ready: bool,
    readiness_certified: bool,
    continuity_preserved: bool,
    execution_boundary_preserved: bool,
    replay_safe: bool,
    rollback_safe: bool,
    provenance_safe: bool,
    explainability_safe: bool,
    deterministic: bool,
    non_executable: bool,
    hidden_risk_detected: bool,
    evidence_references: tuple[str, ...],
) -> tuple[V37CloseoutReadinessFinding, ...]:
    specs = (
        (V37_CLOSEOUT_FINDING_CLOSEOUT_READY, closeout_ready, False, "v3.7 closeout is ready for v3.8 deterministic planning expansion"),
        (V37_CLOSEOUT_FINDING_CLOSEOUT_BLOCKED, not closeout_ready, not closeout_ready, "closeout blockers remain fail-visible"),
        (V37_CLOSEOUT_FINDING_READINESS_CERTIFIED, readiness_certified, False, "v3.8 planning readiness is certified for planning expansion only"),
        (V37_CLOSEOUT_FINDING_READINESS_BLOCKED, not readiness_certified, not readiness_certified, "v3.8 planning readiness blockers remain fail-visible"),
        (V37_CLOSEOUT_FINDING_CONTINUITY_PRESERVED, continuity_preserved, False, "v3.7 phase continuity is preserved"),
        (V37_CLOSEOUT_FINDING_CONTINUITY_BROKEN, not continuity_preserved, not continuity_preserved, "broken continuity blocks closeout"),
        (V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_PRESERVED, execution_boundary_preserved, False, "execution boundaries remain preserved"),
        (V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_BROKEN, not execution_boundary_preserved, not execution_boundary_preserved, "execution-boundary failures block closeout"),
        (V37_CLOSEOUT_FINDING_REPLAY_SAFE, replay_safe, not replay_safe, "replay continuity is planning evidence only"),
        (V37_CLOSEOUT_FINDING_ROLLBACK_SAFE, rollback_safe, not rollback_safe, "rollback continuity is planning evidence only"),
        (V37_CLOSEOUT_FINDING_PROVENANCE_SAFE, provenance_safe, not provenance_safe, "provenance continuity is preserved"),
        (V37_CLOSEOUT_FINDING_EXPLAINABILITY_SAFE, explainability_safe, not explainability_safe, "explainability continuity is preserved"),
        (V37_CLOSEOUT_FINDING_DETERMINISTIC, deterministic, not deterministic, "serialization and hashing remain deterministic"),
        (V37_CLOSEOUT_FINDING_NON_EXECUTABLE, non_executable, not non_executable, "closeout evidence remains non-executable"),
        (V37_CLOSEOUT_FINDING_HIDDEN_RISK_DETECTED, hidden_risk_detected, hidden_risk_detected, "hidden risk states block closeout"),
    )
    findings = []
    for classification, active, blocks, summary in specs:
        severity = "error" if blocks else ("info" if active else "visibility")
        findings.append(
            V37CloseoutReadinessFinding(
                finding_id=f"v3_7_closeout_{classification}",
                finding_classification=classification,
                subject_type="v3_7_closeout",
                subject_id=classification,
                severity=severity,
                summary=summary,
                evidence_references=evidence_references,
                active=active,
                active_violation=blocks,
                blocks_closeout=blocks,
            )
        )
    return tuple(sorted(findings, key=lambda item: item.finding_id))


def _execution_boundary_preserved(certification: V37GraphPlanningContinuityCertification) -> bool:
    return all(
        (
            certification.certification_is_non_executable,
            certification.certified_continuity_does_not_authorize_execution,
            certification.certification_does_not_mark_runtime_execution_readiness,
            certification.certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
            not certification.graph_execution_enabled,
            not certification.certification_driven_execution_enabled,
            not certification.orchestration_authorization_enabled,
            not certification.execution_readiness_approval_enabled,
            not certification.routing_enabled,
            not certification.scheduling_enabled,
            not certification.dispatch_enabled,
            not certification.traversal_logic_enabled,
            not certification.path_selection_enabled,
            not certification.scenario_selection_enabled,
            not certification.optimization_engine_enabled,
            not certification.recommendation_enabled,
            not certification.autonomous_orchestration_enabled,
            not certification.runtime_mutation_enabled,
            not certification.persistent_runtime_writes_enabled,
            not certification.runtime_decision_making_enabled,
            not certification.executable_certification_gates_enabled,
            not certification.runtime_control_system_enabled,
        )
    )


def _execution_boundary_violation_count(
    certification: V37GraphPlanningContinuityCertification,
    forced: bool,
) -> int:
    checks = (
        certification.orchestration_authorization_enabled,
        certification.routing_enabled,
        certification.scheduling_enabled,
        certification.dispatch_enabled,
        certification.traversal_logic_enabled,
        certification.path_selection_enabled,
        certification.scenario_selection_enabled,
        certification.recommendation_enabled,
        certification.optimization_engine_enabled,
        certification.executable_certification_gates_enabled,
        certification.runtime_control_system_enabled,
        forced,
    )
    return sum(1 for value in checks if value)


def _explanation_summary(closeout_ready: bool) -> tuple[str, ...]:
    status = "certified" if closeout_ready else "blocked"
    return (
        "v3.7 implemented deterministic orchestration planning intelligence across graph foundations, governance, compatibility, evaluation, sessions, scenarios, aggregation, integrity, and certification.",
        "v3.7 preserved deterministic serialization, deterministic hashing, governance continuity, compatibility continuity, evaluation continuity, provenance continuity, explainability continuity, replay continuity, and rollback continuity.",
        "v3.7 explicitly prohibited graph execution, orchestration execution, routing, scheduling, dispatch, traversal, runtime path selection, scenario execution selection, optimization for execution, recommendation to execute, callable flows, and runtime control systems.",
        f"v3.7 closeout status is {status} for future deterministic planning expansion only.",
        "v3.8 may expand planning intelligence evidence but may not enable runtime orchestration execution.",
    )
