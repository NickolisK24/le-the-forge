"""Deterministic v3.8 coordination session reasoning."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_compatibility_reasoning import reason_v3_8_coordination_compatibility
from .coordination_evaluation_models import (
    EVALUATION_STATE_BLOCKED,
    EVALUATION_STATE_EXPERIMENTAL,
    EVALUATION_STATE_INVALID,
    EVALUATION_STATE_NON_EXECUTABLE,
    EVALUATION_STATE_PLANNING_ONLY,
    EVALUATION_STATE_PROHIBITED,
    EVALUATION_STATE_UNKNOWN,
    EVALUATION_STATE_UNSUPPORTED,
    EVALUATION_STATE_VALID,
    V38CoordinationEvaluationAudit,
    V38CoordinationEvaluationResult,
)
from .coordination_evaluation_reasoning import reason_v3_8_coordination_evaluation
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation
from .coordination_session_models import (
    NON_COMPLETE_SESSION_STATES,
    SESSION_SEVERITY_BLOCKED,
    SESSION_SEVERITY_INFO,
    SESSION_SEVERITY_WARNING,
    SESSION_STATE_BLOCKED,
    SESSION_STATE_COMPLETE,
    SESSION_STATE_EXPERIMENTAL,
    SESSION_STATE_INCOMPLETE,
    SESSION_STATE_NON_EXECUTABLE,
    SESSION_STATE_PLANNING_ONLY,
    SESSION_STATE_PROHIBITED,
    SESSION_STATE_UNKNOWN,
    SESSION_STATE_UNSUPPORTED,
    SESSION_STATES,
    SESSION_VISIBILITY_FAIL_VISIBLE,
    SESSION_VISIBILITY_VISIBLE,
    V3_8_SESSION_AUDIT_BLOCKED,
    V3_8_SESSION_AUDIT_STABLE,
    V38CoordinationSessionAudit,
    V38CoordinationSessionEvidence,
    V38CoordinationSessionResult,
    export_v3_8_session_audit,
    hash_v3_8_session_audit,
    session_id,
)


EVALUATION_TO_SESSION_STATE = {
    EVALUATION_STATE_VALID: SESSION_STATE_COMPLETE,
    EVALUATION_STATE_INVALID: SESSION_STATE_BLOCKED,
    EVALUATION_STATE_BLOCKED: SESSION_STATE_BLOCKED,
    EVALUATION_STATE_UNSUPPORTED: SESSION_STATE_UNSUPPORTED,
    EVALUATION_STATE_PROHIBITED: SESSION_STATE_PROHIBITED,
    EVALUATION_STATE_UNKNOWN: SESSION_STATE_UNKNOWN,
    EVALUATION_STATE_EXPERIMENTAL: SESSION_STATE_EXPERIMENTAL,
    EVALUATION_STATE_PLANNING_ONLY: SESSION_STATE_PLANNING_ONLY,
    EVALUATION_STATE_NON_EXECUTABLE: SESSION_STATE_NON_EXECUTABLE,
}


def reason_v3_8_coordination_session(
    foundation: V38CoordinationFoundation | None = None,
) -> V38CoordinationSessionAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    compatibility_audit = reason_v3_8_coordination_compatibility(source)
    evaluation_audit = reason_v3_8_coordination_evaluation(source)
    results = _build_session_results(source, evaluation_audit)
    state_counts = _count_states(results)
    execution_boundary_violation_count = _execution_boundary_violation_count(
        source,
        boundary_audit,
        compatibility_audit,
        evaluation_audit,
        results,
    )
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden)
    runtime_state_machine_count = sum(
        1 for result in results if result.runtime_state_machine or result.evidence.runtime_state_machine
    )
    validation_totals = {
        "session_result_count": len(results),
        "complete_count": state_counts[SESSION_STATE_COMPLETE],
        "incomplete_count": state_counts[SESSION_STATE_INCOMPLETE],
        "blocked_count": state_counts[SESSION_STATE_BLOCKED],
        "unsupported_count": state_counts[SESSION_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[SESSION_STATE_PROHIBITED],
        "unknown_count": state_counts[SESSION_STATE_UNKNOWN],
        "experimental_count": state_counts[SESSION_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[SESSION_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[SESSION_STATE_NON_EXECUTABLE],
        "boundary_context_count": sum(1 for result in results if result.boundary_context_ids),
        "boundary_context_preserved_count": sum(
            1 for result in results if result.evidence.boundary_context_preserved
        ),
        "compatibility_context_count": sum(1 for result in results if result.compatibility_context_ids),
        "compatibility_context_preserved_count": sum(
            1 for result in results if result.evidence.compatibility_context_preserved
        ),
        "evaluation_context_count": sum(1 for result in results if result.evaluation_context_ids),
        "evaluation_context_preserved_count": sum(
            1 for result in results if result.evidence.evaluation_context_preserved
        ),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_preserved),
        "fail_visible_incomplete_count": _visible_count(results, SESSION_STATE_INCOMPLETE),
        "fail_visible_blocked_count": _visible_count(results, SESSION_STATE_BLOCKED),
        "fail_visible_unsupported_count": _visible_count(results, SESSION_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, SESSION_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, SESSION_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1
            for result in results
            if result.session_state == SESSION_STATE_EXPERIMENTAL
            and result.experimental_label_explicit
        ),
        "immutable_evidence_record_count": sum(
            1 for result in results if result.immutable_evidence_record and result.evidence.immutable_evidence_record
        ),
        "runtime_state_machine_count": runtime_state_machine_count,
        "hidden_risk_count": hidden_risk_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "non_executable_result_count": sum(1 for result in results if result.non_execution_confirmation),
        "valid": execution_boundary_violation_count == 0
        and hidden_risk_count == 0
        and runtime_state_machine_count == 0
        and all(
            result.fail_visible
            and not result.hidden
            and result.deterministic_visibility_status == SESSION_VISIBILITY_FAIL_VISIBLE
            for result in results
            if result.session_state in NON_COMPLETE_SESSION_STATES
        ),
    }
    audit = V38CoordinationSessionAudit(
        audit_id="v3_8_coordination_session_reasoning_audit",
        audit_status=V3_8_SESSION_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_SESSION_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        source_compatibility_audit_id=compatibility_audit.audit_id,
        source_evaluation_audit_id=evaluation_audit.audit_id,
        session_results=results,
        state_counts=state_counts,
        validation_totals=validation_totals,
        immutable_evidence_records=True,
        non_executable=True,
        coordination_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_enabled=False,
        scheduling_enabled=False,
        dispatch_enabled=False,
        traversal_execution_enabled=False,
        optimization_enabled=False,
        recommendation_enabled=False,
        execution_authorization_enabled=False,
        runtime_engine_enabled=False,
        state_machine_enabled=False,
        session_runtime_state_machine_enabled=False,
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_session_hash=hash_v3_8_session_audit(audit))


def export_v3_8_coordination_session_reasoning_audit(
    audit: V38CoordinationSessionAudit,
) -> dict[str, object]:
    return export_v3_8_session_audit(audit)


def count_v3_8_session_states(
    results: tuple[V38CoordinationSessionResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_session_results(
    foundation: V38CoordinationFoundation,
    evaluation_audit: V38CoordinationEvaluationAudit,
) -> tuple[V38CoordinationSessionResult, ...]:
    results = [
        _result_from_evaluation(evaluation_result)
        for evaluation_result in evaluation_audit.evaluation_results
    ]
    results.append(_incomplete_runtime_state_machine_session(foundation, evaluation_audit))
    return tuple(sorted(results, key=lambda item: (item.session_state, item.session_id)))


def _result_from_evaluation(
    evaluation_result: V38CoordinationEvaluationResult,
) -> V38CoordinationSessionResult:
    state = EVALUATION_TO_SESSION_STATE[evaluation_result.evaluation_state]
    return _result(
        subject_id=evaluation_result.evaluation_id,
        state=state,
        severity=_severity_for_state(state),
        explanation=_session_explanation(state, evaluation_result.explanation),
        source_references=evaluation_result.source_coordination_references,
        boundary_context_ids=evaluation_result.boundary_context_ids,
        compatibility_context_ids=evaluation_result.compatibility_context_ids,
        evaluation_context_ids=(evaluation_result.evaluation_id,),
        provenance_reference=evaluation_result.provenance_reference,
        replay_evidence=evaluation_result.replay_safe_evidence,
        rollback_evidence=evaluation_result.rollback_safe_evidence,
        deterministic_hash_references=("v3_8_coordination_evaluation_hash",),
        experimental_label_explicit=state == SESSION_STATE_EXPERIMENTAL,
    )


def _incomplete_runtime_state_machine_session(
    foundation: V38CoordinationFoundation,
    evaluation_audit: V38CoordinationEvaluationAudit,
) -> V38CoordinationSessionResult:
    return _result(
        subject_id="runtime_state_machine_evidence_absent",
        state=SESSION_STATE_INCOMPLETE,
        severity=SESSION_SEVERITY_WARNING,
        explanation=(
            "runtime state-machine evidence is absent by design; coordination sessions are immutable planning "
            "evidence records and cannot be inferred as executable runtime state machines"
        ),
        source_references=(foundation.identity.coordination_id,),
        boundary_context_ids=("v3_8_non_execution_coordination_boundary",),
        compatibility_context_ids=(evaluation_audit.source_compatibility_audit_id,),
        evaluation_context_ids=(evaluation_audit.audit_id,),
        provenance_reference=foundation.provenance_state.provenance_id,
        replay_evidence=(foundation.replay_evidence[0].replay_evidence_id,),
        rollback_evidence=(foundation.rollback_evidence[0].rollback_evidence_id,),
        deterministic_hash_references=(
            "v3_8_coordination_foundation_hash",
            "v3_8_coordination_evaluation_hash",
        ),
    )


def _result(
    *,
    subject_id: str,
    state: str,
    severity: str,
    explanation: str,
    source_references: tuple[str, ...],
    boundary_context_ids: tuple[str, ...],
    compatibility_context_ids: tuple[str, ...],
    evaluation_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    experimental_label_explicit: bool = False,
) -> V38CoordinationSessionResult:
    deterministic_visibility_status = (
        SESSION_VISIBILITY_VISIBLE if state == SESSION_STATE_COMPLETE else SESSION_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationSessionEvidence(
        evidence_id=f"evidence_{session_id(state, subject_id)}",
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
    )
    return V38CoordinationSessionResult(
        session_id=session_id(state, subject_id),
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_state=state,
        severity=severity,
        explanation=explanation,
        provenance_reference=provenance_reference,
        replay_safe_evidence=replay_evidence,
        rollback_safe_evidence=rollback_evidence,
        deterministic_visibility_status=deterministic_visibility_status,
        non_execution_confirmation=True,
        evidence=evidence,
        fail_visible=True,
        hidden=False,
        hidden_risk=False,
        experimental_label_explicit=experimental_label_explicit,
        immutable_evidence_record=True,
        runtime_state_machine=False,
        execution_behavior_detected=False,
        callable_execution_path_enabled=False,
    )


def _session_explanation(state: str, evaluation_explanation: str) -> str:
    if state == SESSION_STATE_COMPLETE:
        return f"complete session evidence is deterministic and internally consistent: {evaluation_explanation}"
    if state == SESSION_STATE_BLOCKED:
        return f"blocked session evidence remains fail-visible: {evaluation_explanation}"
    if state == SESSION_STATE_UNSUPPORTED:
        return f"unsupported session evidence remains fail-visible: {evaluation_explanation}"
    if state == SESSION_STATE_PROHIBITED:
        return f"prohibited session evidence remains intentionally blocked: {evaluation_explanation}"
    if state == SESSION_STATE_UNKNOWN:
        return f"unknown session evidence lacks sufficient deterministic support: {evaluation_explanation}"
    if state == SESSION_STATE_EXPERIMENTAL:
        return f"experimental session reasoning is explicitly labeled: {evaluation_explanation}"
    if state == SESSION_STATE_PLANNING_ONLY:
        return f"planning-only session evidence remains non-executable: {evaluation_explanation}"
    if state == SESSION_STATE_NON_EXECUTABLE:
        return f"non-executable session evidence confirms execution is absent: {evaluation_explanation}"
    return evaluation_explanation


def _severity_for_state(state: str) -> str:
    if state in (SESSION_STATE_BLOCKED, SESSION_STATE_PROHIBITED):
        return SESSION_SEVERITY_BLOCKED
    if state in (SESSION_STATE_INCOMPLETE, SESSION_STATE_UNSUPPORTED, SESSION_STATE_UNKNOWN):
        return SESSION_SEVERITY_WARNING
    return SESSION_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationSessionResult, ...]) -> dict[str, int]:
    counts = Counter(result.session_state for result in results)
    return {state: counts.get(state, 0) for state in SESSION_STATES}


def _visible_count(results: tuple[V38CoordinationSessionResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.session_state == state
        and result.deterministic_visibility_status == SESSION_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    compatibility_audit: object,
    evaluation_audit: V38CoordinationEvaluationAudit,
    results: tuple[V38CoordinationSessionResult, ...],
) -> int:
    foundation_flags = (
        foundation.coordination_execution_enabled,
        foundation.orchestration_execution_enabled,
        foundation.execution_authorization_enabled,
        foundation.routing_enabled,
        foundation.scheduling_enabled,
        foundation.dispatch_enabled,
        foundation.traversal_execution_enabled,
        foundation.graph_traversal_execution_enabled,
        foundation.runtime_path_selection_enabled,
        foundation.recommendation_enabled,
        foundation.optimization_enabled,
        foundation.autonomous_orchestration_enabled,
        foundation.callable_execution_flow_enabled,
        foundation.persistent_runtime_mutation_enabled,
        foundation.persistent_runtime_writes_enabled,
        foundation.hidden_state_transition_enabled,
        foundation.silent_fallback_enabled,
    )
    boundary_flags = (
        boundary_audit.coordination_execution_enabled,
        boundary_audit.orchestration_execution_enabled,
        boundary_audit.routing_enabled,
        boundary_audit.scheduling_enabled,
        boundary_audit.dispatch_enabled,
        boundary_audit.traversal_execution_enabled,
        boundary_audit.optimization_enabled,
        boundary_audit.recommendation_enabled,
        boundary_audit.execution_authorization_enabled,
        boundary_audit.callable_coordination_flow_enabled,
        boundary_audit.persistent_runtime_mutation_enabled,
        boundary_audit.hidden_transition_enabled,
        boundary_audit.silent_fallback_enabled,
    )
    compatibility_flags = (
        compatibility_audit.coordination_execution_enabled,
        compatibility_audit.orchestration_execution_enabled,
        compatibility_audit.routing_enabled,
        compatibility_audit.scheduling_enabled,
        compatibility_audit.dispatch_enabled,
        compatibility_audit.traversal_execution_enabled,
        compatibility_audit.optimization_enabled,
        compatibility_audit.recommendation_enabled,
        compatibility_audit.execution_authorization_enabled,
        compatibility_audit.runtime_engine_enabled,
        compatibility_audit.state_machine_enabled,
        compatibility_audit.callable_coordination_flow_enabled,
        compatibility_audit.persistent_runtime_mutation_enabled,
        compatibility_audit.hidden_transition_enabled,
        compatibility_audit.silent_fallback_enabled,
    )
    evaluation_flags = (
        evaluation_audit.coordination_execution_enabled,
        evaluation_audit.orchestration_execution_enabled,
        evaluation_audit.routing_enabled,
        evaluation_audit.scheduling_enabled,
        evaluation_audit.dispatch_enabled,
        evaluation_audit.traversal_execution_enabled,
        evaluation_audit.optimization_enabled,
        evaluation_audit.recommendation_enabled,
        evaluation_audit.execution_authorization_enabled,
        evaluation_audit.runtime_engine_enabled,
        evaluation_audit.state_machine_enabled,
        evaluation_audit.callable_coordination_flow_enabled,
        evaluation_audit.persistent_runtime_mutation_enabled,
        evaluation_audit.hidden_transition_enabled,
        evaluation_audit.silent_fallback_enabled,
    )
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for value in boundary_flags if value)
        + sum(1 for value in compatibility_flags if value)
        + sum(1 for value in evaluation_flags if value)
        + sum(
            1
            for result in compatibility_audit.compatibility_results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
        )
        + sum(
            1
            for result in evaluation_audit.evaluation_results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
        )
        + sum(
            1
            for result in results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_state_machine
            or result.evidence.runtime_state_machine
        )
    )
