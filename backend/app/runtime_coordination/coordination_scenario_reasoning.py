"""Deterministic v3.8 coordination scenario reasoning."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_compatibility_reasoning import reason_v3_8_coordination_compatibility
from .coordination_evaluation_reasoning import reason_v3_8_coordination_evaluation
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation
from .coordination_scenario_models import (
    COMPARISON_EXECUTION_LANGUAGE_TERMS,
    COMPARISON_OPTIMIZATION_LANGUAGE_TERMS,
    COMPARISON_RECOMMENDATION_LANGUAGE_TERMS,
    NON_MODELED_SCENARIO_STATES,
    SCENARIO_SEVERITY_BLOCKED,
    SCENARIO_SEVERITY_INFO,
    SCENARIO_SEVERITY_WARNING,
    SCENARIO_STATE_BLOCKED,
    SCENARIO_STATE_EXPERIMENTAL,
    SCENARIO_STATE_MODELED,
    SCENARIO_STATE_NON_EXECUTABLE,
    SCENARIO_STATE_PLANNING_ONLY,
    SCENARIO_STATE_PROHIBITED,
    SCENARIO_STATE_UNKNOWN,
    SCENARIO_STATE_UNMODELED,
    SCENARIO_STATE_UNSUPPORTED,
    SCENARIO_STATES,
    SCENARIO_VISIBILITY_FAIL_VISIBLE,
    SCENARIO_VISIBILITY_VISIBLE,
    V3_8_SCENARIO_AUDIT_BLOCKED,
    V3_8_SCENARIO_AUDIT_STABLE,
    V38CoordinationScenarioAudit,
    V38CoordinationScenarioComparison,
    V38CoordinationScenarioEvidence,
    V38CoordinationScenarioResult,
    export_v3_8_scenario_audit,
    hash_v3_8_scenario_audit,
    scenario_comparison_id,
    scenario_id,
)
from .coordination_session_models import (
    SESSION_STATE_BLOCKED,
    SESSION_STATE_COMPLETE,
    SESSION_STATE_EXPERIMENTAL,
    SESSION_STATE_INCOMPLETE,
    SESSION_STATE_NON_EXECUTABLE,
    SESSION_STATE_PLANNING_ONLY,
    SESSION_STATE_PROHIBITED,
    SESSION_STATE_UNKNOWN,
    SESSION_STATE_UNSUPPORTED,
    V38CoordinationSessionAudit,
    V38CoordinationSessionResult,
)
from .coordination_session_reasoning import reason_v3_8_coordination_session


SESSION_TO_SCENARIO_STATE = {
    SESSION_STATE_COMPLETE: SCENARIO_STATE_MODELED,
    SESSION_STATE_INCOMPLETE: SCENARIO_STATE_UNMODELED,
    SESSION_STATE_BLOCKED: SCENARIO_STATE_BLOCKED,
    SESSION_STATE_UNSUPPORTED: SCENARIO_STATE_UNSUPPORTED,
    SESSION_STATE_PROHIBITED: SCENARIO_STATE_PROHIBITED,
    SESSION_STATE_UNKNOWN: SCENARIO_STATE_UNKNOWN,
    SESSION_STATE_EXPERIMENTAL: SCENARIO_STATE_EXPERIMENTAL,
    SESSION_STATE_PLANNING_ONLY: SCENARIO_STATE_PLANNING_ONLY,
    SESSION_STATE_NON_EXECUTABLE: SCENARIO_STATE_NON_EXECUTABLE,
}


def reason_v3_8_coordination_scenario(
    foundation: V38CoordinationFoundation | None = None,
) -> V38CoordinationScenarioAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    compatibility_audit = reason_v3_8_coordination_compatibility(source)
    evaluation_audit = reason_v3_8_coordination_evaluation(source)
    session_audit = reason_v3_8_coordination_session(source)
    results = _build_scenario_results(session_audit)
    comparisons = _build_scenario_comparisons(results)
    state_counts = _count_states(results)
    recommendation_language_violation_count = _comparison_language_violation_count(
        comparisons,
        COMPARISON_RECOMMENDATION_LANGUAGE_TERMS,
    )
    optimization_language_violation_count = _comparison_language_violation_count(
        comparisons,
        COMPARISON_OPTIMIZATION_LANGUAGE_TERMS,
    )
    comparison_execution_language_violation_count = _comparison_language_violation_count(
        comparisons,
        COMPARISON_EXECUTION_LANGUAGE_TERMS,
    )
    recommendation_behavior_violation_count = sum(
        1
        for result in results
        if result.recommendation_behavior_enabled or result.scoring_behavior_enabled
    ) + sum(
        1
        for comparison in comparisons
        if comparison.recommendation_behavior_enabled or comparison.scoring_behavior_enabled
    )
    optimization_behavior_violation_count = sum(
        1 for result in results if result.optimization_behavior_enabled
    ) + sum(1 for comparison in comparisons if comparison.optimization_behavior_enabled)
    execution_boundary_violation_count = _execution_boundary_violation_count(
        source,
        boundary_audit,
        compatibility_audit,
        evaluation_audit,
        session_audit,
        results,
        comparisons,
    )
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden)
    runtime_state_machine_count = sum(
        1 for result in results if result.runtime_state_machine or result.evidence.runtime_state_machine
    )
    validation_totals = {
        "scenario_result_count": len(results),
        "modeled_count": state_counts[SCENARIO_STATE_MODELED],
        "unmodeled_count": state_counts[SCENARIO_STATE_UNMODELED],
        "blocked_count": state_counts[SCENARIO_STATE_BLOCKED],
        "unsupported_count": state_counts[SCENARIO_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[SCENARIO_STATE_PROHIBITED],
        "unknown_count": state_counts[SCENARIO_STATE_UNKNOWN],
        "experimental_count": state_counts[SCENARIO_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[SCENARIO_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[SCENARIO_STATE_NON_EXECUTABLE],
        "comparison_count": len(comparisons),
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
        "session_context_count": sum(1 for result in results if result.session_context_ids),
        "session_context_preserved_count": sum(
            1 for result in results if result.evidence.session_context_preserved
        ),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_preserved),
        "comparison_replay_safe_evidence_count": sum(1 for comparison in comparisons if comparison.replay_safe_evidence),
        "comparison_rollback_safe_evidence_count": sum(
            1 for comparison in comparisons if comparison.rollback_safe_evidence
        ),
        "comparison_provenance_continuity_count": sum(
            1 for comparison in comparisons if comparison.provenance_references
        ),
        "fail_visible_unmodeled_count": _visible_count(results, SCENARIO_STATE_UNMODELED),
        "fail_visible_blocked_count": _visible_count(results, SCENARIO_STATE_BLOCKED),
        "fail_visible_unsupported_count": _visible_count(results, SCENARIO_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, SCENARIO_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, SCENARIO_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1
            for result in results
            if result.scenario_state == SCENARIO_STATE_EXPERIMENTAL
            and result.experimental_label_explicit
        ),
        "immutable_evidence_record_count": sum(
            1 for result in results if result.immutable_evidence_record and result.evidence.immutable_evidence_record
        ),
        "runtime_state_machine_count": runtime_state_machine_count,
        "hidden_risk_count": hidden_risk_count,
        "recommendation_language_violation_count": recommendation_language_violation_count,
        "optimization_language_violation_count": optimization_language_violation_count,
        "comparison_execution_language_violation_count": comparison_execution_language_violation_count,
        "recommendation_behavior_violation_count": recommendation_behavior_violation_count,
        "optimization_behavior_violation_count": optimization_behavior_violation_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "non_executable_result_count": sum(1 for result in results if result.non_execution_confirmation),
        "valid": execution_boundary_violation_count == 0
        and hidden_risk_count == 0
        and runtime_state_machine_count == 0
        and recommendation_language_violation_count == 0
        and optimization_language_violation_count == 0
        and comparison_execution_language_violation_count == 0
        and recommendation_behavior_violation_count == 0
        and optimization_behavior_violation_count == 0
        and all(
            result.fail_visible
            and not result.hidden
            and result.deterministic_visibility_status == SCENARIO_VISIBILITY_FAIL_VISIBLE
            for result in results
            if result.scenario_state in NON_MODELED_SCENARIO_STATES
        ),
    }
    audit = V38CoordinationScenarioAudit(
        audit_id="v3_8_coordination_scenario_reasoning_audit",
        audit_status=V3_8_SCENARIO_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_SCENARIO_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        source_compatibility_audit_id=compatibility_audit.audit_id,
        source_evaluation_audit_id=evaluation_audit.audit_id,
        source_session_audit_id=session_audit.audit_id,
        scenario_results=results,
        scenario_comparisons=comparisons,
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
        scoring_decision_system_enabled=False,
        execution_authorization_enabled=False,
        runtime_engine_enabled=False,
        state_machine_enabled=False,
        scenario_runtime_state_machine_enabled=False,
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_scenario_hash=hash_v3_8_scenario_audit(audit))


def export_v3_8_coordination_scenario_reasoning_audit(
    audit: V38CoordinationScenarioAudit,
) -> dict[str, object]:
    return export_v3_8_scenario_audit(audit)


def count_v3_8_scenario_states(
    results: tuple[V38CoordinationScenarioResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_scenario_results(
    session_audit: V38CoordinationSessionAudit,
) -> tuple[V38CoordinationScenarioResult, ...]:
    results = [
        _result_from_session(session_result)
        for session_result in session_audit.session_results
    ]
    return tuple(sorted(results, key=lambda item: (item.scenario_state, item.scenario_id)))


def _result_from_session(
    session_result: V38CoordinationSessionResult,
) -> V38CoordinationScenarioResult:
    state = SESSION_TO_SCENARIO_STATE[session_result.session_state]
    return _result(
        subject_id=session_result.session_id,
        state=state,
        severity=_severity_for_state(state),
        explanation=_scenario_explanation(state, session_result.explanation),
        source_references=session_result.source_coordination_references,
        boundary_context_ids=session_result.boundary_context_ids,
        compatibility_context_ids=session_result.compatibility_context_ids,
        evaluation_context_ids=session_result.evaluation_context_ids,
        session_context_ids=(session_result.session_id,),
        provenance_reference=session_result.provenance_reference,
        replay_evidence=session_result.replay_safe_evidence,
        rollback_evidence=session_result.rollback_safe_evidence,
        deterministic_hash_references=("v3_8_coordination_session_hash",),
        experimental_label_explicit=state == SCENARIO_STATE_EXPERIMENTAL,
    )


def _build_scenario_comparisons(
    results: tuple[V38CoordinationScenarioResult, ...],
) -> tuple[V38CoordinationScenarioComparison, ...]:
    modeled = _comparison_safe_results(results, SCENARIO_STATE_MODELED)
    planning_only = _comparison_safe_results(results, SCENARIO_STATE_PLANNING_ONLY)
    non_executable = _comparison_safe_results(results, SCENARIO_STATE_NON_EXECUTABLE)
    comparison_specs: list[tuple[str, V38CoordinationScenarioResult, V38CoordinationScenarioResult]] = [
        ("modeled_evidence_delta", modeled[0], modeled[1]),
        ("modeled_visibility_delta", modeled[2], modeled[3]),
        ("planning_only_non_executable_delta", planning_only[0], non_executable[0]),
    ]
    comparisons = [
        _comparison(subject_id=subject_id, left=left, right=right)
        for subject_id, left, right in comparison_specs
    ]
    return tuple(sorted(comparisons, key=lambda item: item.comparison_id))


def _comparison(
    *,
    subject_id: str,
    left: V38CoordinationScenarioResult,
    right: V38CoordinationScenarioResult,
) -> V38CoordinationScenarioComparison:
    return V38CoordinationScenarioComparison(
        comparison_id=scenario_comparison_id(subject_id),
        compared_scenario_ids=(left.scenario_id, right.scenario_id),
        comparison_scope="hypothetical_planning_only_evidence_comparison",
        comparison_summary="hypothetical planning-only comparison preserves evidence visibility and provenance",
        difference_summary="delta records evidence difference and visibility difference only",
        visibility_status=SCENARIO_VISIBILITY_FAIL_VISIBLE
        if SCENARIO_VISIBILITY_FAIL_VISIBLE in (
            left.deterministic_visibility_status,
            right.deterministic_visibility_status,
        )
        else SCENARIO_VISIBILITY_VISIBLE,
        boundary_context_ids=_merged(left.boundary_context_ids, right.boundary_context_ids),
        compatibility_context_ids=_merged(left.compatibility_context_ids, right.compatibility_context_ids),
        evaluation_context_ids=_merged(left.evaluation_context_ids, right.evaluation_context_ids),
        session_context_ids=_merged(left.session_context_ids, right.session_context_ids),
        provenance_references=tuple(sorted({left.provenance_reference, right.provenance_reference})),
        replay_safe_evidence=_merged(left.replay_safe_evidence, right.replay_safe_evidence),
        rollback_safe_evidence=_merged(left.rollback_safe_evidence, right.rollback_safe_evidence),
        non_execution_confirmation=True,
        immutable_evidence_record=True,
        runtime_state_machine=False,
        recommendation_behavior_enabled=False,
        optimization_behavior_enabled=False,
        scoring_behavior_enabled=False,
        execution_behavior_detected=False,
    )


def _comparison_safe_results(
    results: tuple[V38CoordinationScenarioResult, ...],
    state: str,
) -> tuple[V38CoordinationScenarioResult, ...]:
    candidates = tuple(
        result
        for result in results
        if result.scenario_state == state
        and _comparison_text_violation_count(
            (
                result.scenario_id,
                *result.boundary_context_ids,
                *result.compatibility_context_ids,
                *result.evaluation_context_ids,
                *result.session_context_ids,
            ),
            COMPARISON_EXECUTION_LANGUAGE_TERMS,
        )
        == 0
    )
    return tuple(sorted(candidates, key=lambda item: item.scenario_id))


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
    session_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    experimental_label_explicit: bool = False,
) -> V38CoordinationScenarioResult:
    deterministic_visibility_status = (
        SCENARIO_VISIBILITY_VISIBLE if state == SCENARIO_STATE_MODELED else SCENARIO_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationScenarioEvidence(
        evidence_id=f"evidence_{scenario_id(state, subject_id)}",
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
    )
    return V38CoordinationScenarioResult(
        scenario_id=scenario_id(state, subject_id),
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_state=state,
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
        recommendation_behavior_enabled=False,
        optimization_behavior_enabled=False,
        scoring_behavior_enabled=False,
        execution_behavior_detected=False,
        callable_execution_path_enabled=False,
    )


def _scenario_explanation(state: str, session_explanation: str) -> str:
    if state == SCENARIO_STATE_MODELED:
        return f"modeled hypothetical scenario evidence is complete enough for planning-only comparison: {session_explanation}"
    if state == SCENARIO_STATE_UNMODELED:
        return f"unmodeled scenario evidence remains fail-visible: {session_explanation}"
    if state == SCENARIO_STATE_BLOCKED:
        return f"blocked scenario evidence remains fail-visible: {session_explanation}"
    if state == SCENARIO_STATE_UNSUPPORTED:
        return f"unsupported scenario evidence remains fail-visible: {session_explanation}"
    if state == SCENARIO_STATE_PROHIBITED:
        return f"prohibited scenario evidence remains intentionally blocked: {session_explanation}"
    if state == SCENARIO_STATE_UNKNOWN:
        return f"unknown scenario evidence lacks sufficient deterministic support: {session_explanation}"
    if state == SCENARIO_STATE_EXPERIMENTAL:
        return f"experimental scenario reasoning is explicitly labeled: {session_explanation}"
    if state == SCENARIO_STATE_PLANNING_ONLY:
        return f"planning-only scenario evidence remains non-executable: {session_explanation}"
    if state == SCENARIO_STATE_NON_EXECUTABLE:
        return f"non-executable scenario evidence confirms execution is absent: {session_explanation}"
    return session_explanation


def _severity_for_state(state: str) -> str:
    if state in (SCENARIO_STATE_BLOCKED, SCENARIO_STATE_PROHIBITED):
        return SCENARIO_SEVERITY_BLOCKED
    if state in (SCENARIO_STATE_UNMODELED, SCENARIO_STATE_UNSUPPORTED, SCENARIO_STATE_UNKNOWN):
        return SCENARIO_SEVERITY_WARNING
    return SCENARIO_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationScenarioResult, ...]) -> dict[str, int]:
    counts = Counter(result.scenario_state for result in results)
    return {state: counts.get(state, 0) for state in SCENARIO_STATES}


def _visible_count(results: tuple[V38CoordinationScenarioResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.scenario_state == state
        and result.deterministic_visibility_status == SCENARIO_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _merged(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({*left, *right}))


def _comparison_language_violation_count(
    comparisons: tuple[V38CoordinationScenarioComparison, ...],
    terms: tuple[str, ...],
) -> int:
    return sum(
        _comparison_text_violation_count(
            (
                comparison.comparison_id,
                comparison.comparison_scope,
                comparison.comparison_summary,
                comparison.difference_summary,
                *comparison.compared_scenario_ids,
                *comparison.boundary_context_ids,
                *comparison.compatibility_context_ids,
                *comparison.evaluation_context_ids,
                *comparison.session_context_ids,
            ),
            terms,
        )
        for comparison in comparisons
    )


def _comparison_text_violation_count(values: tuple[str, ...], terms: tuple[str, ...]) -> int:
    text = " ".join(values).lower()
    return sum(1 for term in terms if term.lower() in text)


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    compatibility_audit: object,
    evaluation_audit: object,
    session_audit: V38CoordinationSessionAudit,
    results: tuple[V38CoordinationScenarioResult, ...],
    comparisons: tuple[V38CoordinationScenarioComparison, ...],
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
    audit_flags = (
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
        session_audit.coordination_execution_enabled,
        session_audit.orchestration_execution_enabled,
        session_audit.routing_enabled,
        session_audit.scheduling_enabled,
        session_audit.dispatch_enabled,
        session_audit.traversal_execution_enabled,
        session_audit.optimization_enabled,
        session_audit.recommendation_enabled,
        session_audit.execution_authorization_enabled,
        session_audit.runtime_engine_enabled,
        session_audit.state_machine_enabled,
        session_audit.session_runtime_state_machine_enabled,
        session_audit.callable_coordination_flow_enabled,
        session_audit.persistent_runtime_mutation_enabled,
        session_audit.hidden_transition_enabled,
        session_audit.silent_fallback_enabled,
    )
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for value in audit_flags if value)
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
            for result in session_audit.session_results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_state_machine
            or result.evidence.runtime_state_machine
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
        + sum(
            1
            for comparison in comparisons
            if comparison.execution_behavior_detected
            or not comparison.non_execution_confirmation
            or comparison.runtime_state_machine
        )
    )
