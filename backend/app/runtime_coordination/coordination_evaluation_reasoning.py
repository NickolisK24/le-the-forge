"""Deterministic v3.8 coordination evaluation reasoning."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_compatibility_models import (
    COMPATIBILITY_STATE_COMPATIBLE,
    COMPATIBILITY_STATE_EXPERIMENTAL,
    COMPATIBILITY_STATE_INCOMPATIBLE,
    COMPATIBILITY_STATE_NON_EXECUTABLE,
    COMPATIBILITY_STATE_PLANNING_ONLY,
    COMPATIBILITY_STATE_PROHIBITED,
    COMPATIBILITY_STATE_UNKNOWN,
    COMPATIBILITY_STATE_UNSUPPORTED,
    V38CoordinationCompatibilityAudit,
    V38CoordinationCompatibilityResult,
)
from .coordination_compatibility_reasoning import reason_v3_8_coordination_compatibility
from .coordination_evaluation_models import (
    EVALUATION_SEVERITY_BLOCKED,
    EVALUATION_SEVERITY_INFO,
    EVALUATION_SEVERITY_WARNING,
    EVALUATION_STATE_BLOCKED,
    EVALUATION_STATE_EXPERIMENTAL,
    EVALUATION_STATE_INVALID,
    EVALUATION_STATE_NON_EXECUTABLE,
    EVALUATION_STATE_PLANNING_ONLY,
    EVALUATION_STATE_PROHIBITED,
    EVALUATION_STATE_UNKNOWN,
    EVALUATION_STATE_UNSUPPORTED,
    EVALUATION_STATE_VALID,
    EVALUATION_STATES,
    EVALUATION_VISIBILITY_FAIL_VISIBLE,
    EVALUATION_VISIBILITY_VISIBLE,
    NON_VALID_EVALUATION_STATES,
    V3_8_EVALUATION_AUDIT_BLOCKED,
    V3_8_EVALUATION_AUDIT_STABLE,
    V38CoordinationEvaluationAudit,
    V38CoordinationEvaluationEvidence,
    V38CoordinationEvaluationResult,
    evaluation_id,
    export_v3_8_evaluation_audit,
    hash_v3_8_evaluation_audit,
)
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation


COMPATIBILITY_TO_EVALUATION_STATE = {
    COMPATIBILITY_STATE_COMPATIBLE: EVALUATION_STATE_VALID,
    COMPATIBILITY_STATE_INCOMPATIBLE: EVALUATION_STATE_INVALID,
    COMPATIBILITY_STATE_UNSUPPORTED: EVALUATION_STATE_UNSUPPORTED,
    COMPATIBILITY_STATE_PROHIBITED: EVALUATION_STATE_PROHIBITED,
    COMPATIBILITY_STATE_UNKNOWN: EVALUATION_STATE_UNKNOWN,
    COMPATIBILITY_STATE_EXPERIMENTAL: EVALUATION_STATE_EXPERIMENTAL,
    COMPATIBILITY_STATE_PLANNING_ONLY: EVALUATION_STATE_PLANNING_ONLY,
    COMPATIBILITY_STATE_NON_EXECUTABLE: EVALUATION_STATE_NON_EXECUTABLE,
}


def reason_v3_8_coordination_evaluation(
    foundation: V38CoordinationFoundation | None = None,
) -> V38CoordinationEvaluationAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    compatibility_audit = reason_v3_8_coordination_compatibility(source)
    results = _build_evaluation_results(source, compatibility_audit)
    state_counts = _count_states(results)
    execution_boundary_violation_count = _execution_boundary_violation_count(
        source,
        boundary_audit,
        compatibility_audit,
        results,
    )
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden)
    validation_totals = {
        "evaluation_result_count": len(results),
        "valid_count": state_counts[EVALUATION_STATE_VALID],
        "invalid_count": state_counts[EVALUATION_STATE_INVALID],
        "blocked_count": state_counts[EVALUATION_STATE_BLOCKED],
        "unsupported_count": state_counts[EVALUATION_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[EVALUATION_STATE_PROHIBITED],
        "unknown_count": state_counts[EVALUATION_STATE_UNKNOWN],
        "experimental_count": state_counts[EVALUATION_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[EVALUATION_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[EVALUATION_STATE_NON_EXECUTABLE],
        "boundary_context_count": sum(1 for result in results if result.boundary_context_ids),
        "boundary_context_preserved_count": sum(
            1 for result in results if result.evidence.boundary_context_preserved
        ),
        "compatibility_context_count": sum(1 for result in results if result.compatibility_context_ids),
        "compatibility_context_preserved_count": sum(
            1 for result in results if result.evidence.compatibility_context_preserved
        ),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_preserved),
        "fail_visible_invalid_count": _visible_count(results, EVALUATION_STATE_INVALID),
        "fail_visible_blocked_count": _visible_count(results, EVALUATION_STATE_BLOCKED),
        "fail_visible_unsupported_count": _visible_count(results, EVALUATION_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, EVALUATION_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, EVALUATION_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1
            for result in results
            if result.evaluation_state == EVALUATION_STATE_EXPERIMENTAL
            and result.experimental_label_explicit
        ),
        "hidden_risk_count": hidden_risk_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "non_executable_result_count": sum(1 for result in results if result.non_execution_confirmation),
        "valid": execution_boundary_violation_count == 0
        and hidden_risk_count == 0
        and all(
            result.fail_visible
            and not result.hidden
            and result.deterministic_visibility_status == EVALUATION_VISIBILITY_FAIL_VISIBLE
            for result in results
            if result.evaluation_state in NON_VALID_EVALUATION_STATES
        ),
    }
    audit = V38CoordinationEvaluationAudit(
        audit_id="v3_8_coordination_evaluation_reasoning_audit",
        audit_status=V3_8_EVALUATION_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_EVALUATION_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        source_compatibility_audit_id=compatibility_audit.audit_id,
        evaluation_results=results,
        state_counts=state_counts,
        validation_totals=validation_totals,
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
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_evaluation_hash=hash_v3_8_evaluation_audit(audit))


def export_v3_8_coordination_evaluation_reasoning_audit(
    audit: V38CoordinationEvaluationAudit,
) -> dict[str, object]:
    return export_v3_8_evaluation_audit(audit)


def count_v3_8_evaluation_states(
    results: tuple[V38CoordinationEvaluationResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_evaluation_results(
    foundation: V38CoordinationFoundation,
    compatibility_audit: V38CoordinationCompatibilityAudit,
) -> tuple[V38CoordinationEvaluationResult, ...]:
    results = [
        _result_from_compatibility(compatibility_result)
        for compatibility_result in compatibility_audit.compatibility_results
    ]
    results.append(_blocked_evaluation_result(foundation, compatibility_audit))
    return tuple(sorted(results, key=lambda item: (item.evaluation_state, item.evaluation_id)))


def _result_from_compatibility(
    compatibility_result: V38CoordinationCompatibilityResult,
) -> V38CoordinationEvaluationResult:
    state = COMPATIBILITY_TO_EVALUATION_STATE[compatibility_result.compatibility_state]
    return _result(
        subject_id=compatibility_result.compatibility_id,
        state=state,
        severity=_severity_for_state(state),
        explanation=_evaluation_explanation(state, compatibility_result.explanation),
        source_references=compatibility_result.source_coordination_references,
        boundary_context_ids=compatibility_result.boundary_context_ids,
        compatibility_context_ids=(compatibility_result.compatibility_id,),
        provenance_reference=compatibility_result.provenance_reference,
        replay_evidence=compatibility_result.replay_safe_evidence,
        rollback_evidence=compatibility_result.rollback_safe_evidence,
        deterministic_hash_references=("v3_8_coordination_compatibility_hash",),
        experimental_label_explicit=state == EVALUATION_STATE_EXPERIMENTAL,
    )


def _blocked_evaluation_result(
    foundation: V38CoordinationFoundation,
    compatibility_audit: V38CoordinationCompatibilityAudit,
) -> V38CoordinationEvaluationResult:
    blocked_compatibility = tuple(
        result
        for result in compatibility_audit.compatibility_results
        if result.compatibility_state in (COMPATIBILITY_STATE_INCOMPATIBLE, COMPATIBILITY_STATE_PROHIBITED)
    )
    boundary_context_ids = tuple(
        sorted({boundary_id for result in blocked_compatibility for boundary_id in result.boundary_context_ids})
    )
    compatibility_context_ids = tuple(sorted(result.compatibility_id for result in blocked_compatibility))
    replay_evidence = tuple(
        sorted({evidence_id for result in blocked_compatibility for evidence_id in result.replay_safe_evidence})
    )
    rollback_evidence = tuple(
        sorted({evidence_id for result in blocked_compatibility for evidence_id in result.rollback_safe_evidence})
    )
    return _result(
        subject_id="boundary_and_compatibility_findings_block_execution_interpretation",
        state=EVALUATION_STATE_BLOCKED,
        severity=EVALUATION_SEVERITY_BLOCKED,
        explanation=(
            "evaluation is blocked from executable interpretation because boundary and compatibility findings "
            "include prohibited or incompatible coordination evidence"
        ),
        source_references=(foundation.identity.coordination_id,),
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        provenance_reference=foundation.provenance_state.provenance_id,
        replay_evidence=replay_evidence or (foundation.replay_evidence[0].replay_evidence_id,),
        rollback_evidence=rollback_evidence or (foundation.rollback_evidence[0].rollback_evidence_id,),
        deterministic_hash_references=(
            "v3_8_coordination_foundation_hash",
            "v3_8_coordination_boundary_intelligence_hash",
            "v3_8_coordination_compatibility_hash",
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
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    experimental_label_explicit: bool = False,
) -> V38CoordinationEvaluationResult:
    deterministic_visibility_status = (
        EVALUATION_VISIBILITY_VISIBLE if state == EVALUATION_STATE_VALID else EVALUATION_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationEvaluationEvidence(
        evidence_id=f"evidence_{evaluation_id(state, subject_id)}",
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
    )
    return V38CoordinationEvaluationResult(
        evaluation_id=evaluation_id(state, subject_id),
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_state=state,
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
        execution_behavior_detected=False,
        callable_execution_path_enabled=False,
    )


def _evaluation_explanation(state: str, compatibility_explanation: str) -> str:
    if state == EVALUATION_STATE_VALID:
        return f"valid evaluation preserves deterministic coordination evidence: {compatibility_explanation}"
    if state == EVALUATION_STATE_INVALID:
        return f"invalid evaluation remains fail-visible: {compatibility_explanation}"
    if state == EVALUATION_STATE_UNSUPPORTED:
        return f"unsupported evaluation remains fail-visible: {compatibility_explanation}"
    if state == EVALUATION_STATE_PROHIBITED:
        return f"prohibited evaluation remains intentionally blocked: {compatibility_explanation}"
    if state == EVALUATION_STATE_UNKNOWN:
        return f"unknown evaluation lacks sufficient deterministic evidence: {compatibility_explanation}"
    if state == EVALUATION_STATE_EXPERIMENTAL:
        return f"experimental evaluation is explicitly labeled reasoning-only: {compatibility_explanation}"
    if state == EVALUATION_STATE_PLANNING_ONLY:
        return f"planning-only evaluation remains non-executable: {compatibility_explanation}"
    if state == EVALUATION_STATE_NON_EXECUTABLE:
        return f"non-executable evaluation confirms execution is absent: {compatibility_explanation}"
    return compatibility_explanation


def _severity_for_state(state: str) -> str:
    if state in (EVALUATION_STATE_INVALID, EVALUATION_STATE_BLOCKED, EVALUATION_STATE_PROHIBITED):
        return EVALUATION_SEVERITY_BLOCKED
    if state in (EVALUATION_STATE_UNSUPPORTED, EVALUATION_STATE_UNKNOWN):
        return EVALUATION_SEVERITY_WARNING
    return EVALUATION_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationEvaluationResult, ...]) -> dict[str, int]:
    counts = Counter(result.evaluation_state for result in results)
    return {state: counts.get(state, 0) for state in EVALUATION_STATES}


def _visible_count(results: tuple[V38CoordinationEvaluationResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.evaluation_state == state
        and result.deterministic_visibility_status == EVALUATION_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    compatibility_audit: V38CoordinationCompatibilityAudit,
    results: tuple[V38CoordinationEvaluationResult, ...],
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
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for value in boundary_flags if value)
        + sum(1 for value in compatibility_flags if value)
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
            for result in results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
        )
    )
