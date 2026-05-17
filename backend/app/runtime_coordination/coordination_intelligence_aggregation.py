"""Deterministic v3.8 coordination intelligence aggregation."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_aggregation_models import (
    AGGREGATION_SEVERITY_BLOCKED,
    AGGREGATION_SEVERITY_INFO,
    AGGREGATION_SEVERITY_WARNING,
    AGGREGATION_STATE_AGGREGATED,
    AGGREGATION_STATE_BLOCKED,
    AGGREGATION_STATE_EXPERIMENTAL,
    AGGREGATION_STATE_NON_EXECUTABLE,
    AGGREGATION_STATE_PARTIAL,
    AGGREGATION_STATE_PLANNING_ONLY,
    AGGREGATION_STATE_PROHIBITED,
    AGGREGATION_STATE_UNKNOWN,
    AGGREGATION_STATE_UNSUPPORTED,
    AGGREGATION_STATES,
    AGGREGATION_VISIBILITY_FAIL_VISIBLE,
    AGGREGATION_VISIBILITY_VISIBLE,
    NON_AGGREGATED_STATES,
    SUMMARY_EXECUTION_LANGUAGE_TERMS,
    SUMMARY_OPTIMIZATION_LANGUAGE_TERMS,
    SUMMARY_RANKING_LANGUAGE_TERMS,
    SUMMARY_RECOMMENDATION_LANGUAGE_TERMS,
    SUMMARY_SCORING_LANGUAGE_TERMS,
    SUMMARY_SELECTION_LANGUAGE_TERMS,
    V3_8_AGGREGATION_AUDIT_BLOCKED,
    V3_8_AGGREGATION_AUDIT_STABLE,
    V38CoordinationAggregationAudit,
    V38CoordinationAggregationEvidence,
    V38CoordinationAggregationResult,
    V38CoordinationIntelligenceSummary,
    aggregation_id,
    aggregation_summary_id,
    export_v3_8_aggregation_audit,
    hash_v3_8_aggregation_audit,
)
from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_compatibility_reasoning import reason_v3_8_coordination_compatibility
from .coordination_evaluation_reasoning import reason_v3_8_coordination_evaluation
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation
from .coordination_scenario_models import (
    SCENARIO_STATE_BLOCKED,
    SCENARIO_STATE_EXPERIMENTAL,
    SCENARIO_STATE_MODELED,
    SCENARIO_STATE_NON_EXECUTABLE,
    SCENARIO_STATE_PLANNING_ONLY,
    SCENARIO_STATE_PROHIBITED,
    SCENARIO_STATE_UNKNOWN,
    SCENARIO_STATE_UNMODELED,
    SCENARIO_STATE_UNSUPPORTED,
    V38CoordinationScenarioAudit,
    V38CoordinationScenarioResult,
)
from .coordination_scenario_reasoning import reason_v3_8_coordination_scenario
from .coordination_session_reasoning import reason_v3_8_coordination_session


SCENARIO_TO_AGGREGATION_STATE = {
    SCENARIO_STATE_MODELED: AGGREGATION_STATE_AGGREGATED,
    SCENARIO_STATE_UNMODELED: AGGREGATION_STATE_PARTIAL,
    SCENARIO_STATE_BLOCKED: AGGREGATION_STATE_BLOCKED,
    SCENARIO_STATE_UNSUPPORTED: AGGREGATION_STATE_UNSUPPORTED,
    SCENARIO_STATE_PROHIBITED: AGGREGATION_STATE_PROHIBITED,
    SCENARIO_STATE_UNKNOWN: AGGREGATION_STATE_UNKNOWN,
    SCENARIO_STATE_EXPERIMENTAL: AGGREGATION_STATE_EXPERIMENTAL,
    SCENARIO_STATE_PLANNING_ONLY: AGGREGATION_STATE_PLANNING_ONLY,
    SCENARIO_STATE_NON_EXECUTABLE: AGGREGATION_STATE_NON_EXECUTABLE,
}


def aggregate_v3_8_coordination_intelligence(
    foundation: V38CoordinationFoundation | None = None,
) -> V38CoordinationAggregationAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    compatibility_audit = reason_v3_8_coordination_compatibility(source)
    evaluation_audit = reason_v3_8_coordination_evaluation(source)
    session_audit = reason_v3_8_coordination_session(source)
    scenario_audit = reason_v3_8_coordination_scenario(source)
    results = _build_aggregation_results(scenario_audit)
    state_counts = _count_states(results)
    summaries = _build_intelligence_summaries(results, state_counts)
    recommendation_language_violation_count = _summary_language_violation_count(
        summaries,
        SUMMARY_RECOMMENDATION_LANGUAGE_TERMS,
    )
    optimization_language_violation_count = _summary_language_violation_count(
        summaries,
        SUMMARY_OPTIMIZATION_LANGUAGE_TERMS,
    )
    ranking_language_violation_count = _summary_language_violation_count(
        summaries,
        SUMMARY_RANKING_LANGUAGE_TERMS,
    )
    scoring_language_violation_count = _summary_language_violation_count(
        summaries,
        SUMMARY_SCORING_LANGUAGE_TERMS,
    )
    selection_language_violation_count = _summary_language_violation_count(
        summaries,
        SUMMARY_SELECTION_LANGUAGE_TERMS,
    )
    summary_execution_language_violation_count = _summary_language_violation_count(
        summaries,
        SUMMARY_EXECUTION_LANGUAGE_TERMS,
    )
    recommendation_behavior_violation_count = _behavior_count(
        results,
        summaries,
        "recommendation_behavior_enabled",
    )
    optimization_behavior_violation_count = _behavior_count(
        results,
        summaries,
        "optimization_behavior_enabled",
    )
    ranking_behavior_violation_count = _behavior_count(
        results,
        summaries,
        "ranking_behavior_enabled",
    )
    scoring_behavior_violation_count = _behavior_count(
        results,
        summaries,
        "scoring_behavior_enabled",
    )
    selection_behavior_violation_count = _behavior_count(
        results,
        summaries,
        "selection_behavior_enabled",
    )
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden) + sum(
        1 for summary in summaries if summary.hidden_risk or summary.hidden
    )
    runtime_state_machine_count = sum(
        1
        for result in results
        if result.runtime_state_machine or result.evidence.runtime_state_machine
    ) + sum(1 for summary in summaries if summary.runtime_state_machine)
    execution_boundary_violation_count = _execution_boundary_violation_count(
        source,
        boundary_audit,
        compatibility_audit,
        evaluation_audit,
        session_audit,
        scenario_audit,
        results,
        summaries,
    )
    validation_totals = {
        "aggregation_result_count": len(results),
        "aggregated_count": state_counts[AGGREGATION_STATE_AGGREGATED],
        "partial_count": state_counts[AGGREGATION_STATE_PARTIAL],
        "blocked_count": state_counts[AGGREGATION_STATE_BLOCKED],
        "unsupported_count": state_counts[AGGREGATION_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[AGGREGATION_STATE_PROHIBITED],
        "unknown_count": state_counts[AGGREGATION_STATE_UNKNOWN],
        "experimental_count": state_counts[AGGREGATION_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[AGGREGATION_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[AGGREGATION_STATE_NON_EXECUTABLE],
        "summary_count": len(summaries),
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
        "scenario_context_count": sum(1 for result in results if result.scenario_context_ids),
        "scenario_context_preserved_count": sum(
            1 for result in results if result.evidence.scenario_context_preserved
        ),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_preserved),
        "non_execution_confirmation_count": sum(1 for result in results if result.non_execution_confirmation),
        "fail_visible_finding_count": sum(
            1
            for result in results
            if result.aggregation_state in NON_AGGREGATED_STATES
            and result.fail_visible
            and not result.hidden
            and result.deterministic_visibility_status == AGGREGATION_VISIBILITY_FAIL_VISIBLE
        ),
        "fail_visible_partial_count": _visible_count(results, AGGREGATION_STATE_PARTIAL),
        "fail_visible_blocked_count": _visible_count(results, AGGREGATION_STATE_BLOCKED),
        "fail_visible_unsupported_count": _visible_count(results, AGGREGATION_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, AGGREGATION_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, AGGREGATION_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1
            for result in results
            if result.aggregation_state == AGGREGATION_STATE_EXPERIMENTAL
            and result.experimental_label_explicit
        ),
        "immutable_evidence_record_count": sum(
            1
            for result in results
            if result.immutable_evidence_record and result.evidence.immutable_evidence_record
        ),
        "summary_non_execution_confirmation_count": sum(
            1 for summary in summaries if summary.non_execution_confirmation
        ),
        "hidden_risk_count": hidden_risk_count,
        "runtime_state_machine_count": runtime_state_machine_count,
        "recommendation_language_violation_count": recommendation_language_violation_count,
        "optimization_language_violation_count": optimization_language_violation_count,
        "ranking_language_violation_count": ranking_language_violation_count,
        "scoring_language_violation_count": scoring_language_violation_count,
        "selection_language_violation_count": selection_language_violation_count,
        "summary_execution_language_violation_count": summary_execution_language_violation_count,
        "recommendation_behavior_violation_count": recommendation_behavior_violation_count,
        "optimization_behavior_violation_count": optimization_behavior_violation_count,
        "ranking_behavior_violation_count": ranking_behavior_violation_count,
        "scoring_behavior_violation_count": scoring_behavior_violation_count,
        "selection_behavior_violation_count": selection_behavior_violation_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "valid": execution_boundary_violation_count == 0
        and hidden_risk_count == 0
        and runtime_state_machine_count == 0
        and recommendation_language_violation_count == 0
        and optimization_language_violation_count == 0
        and ranking_language_violation_count == 0
        and scoring_language_violation_count == 0
        and selection_language_violation_count == 0
        and summary_execution_language_violation_count == 0
        and recommendation_behavior_violation_count == 0
        and optimization_behavior_violation_count == 0
        and ranking_behavior_violation_count == 0
        and scoring_behavior_violation_count == 0
        and selection_behavior_violation_count == 0
        and all(
            result.fail_visible
            and not result.hidden
            and result.deterministic_visibility_status == AGGREGATION_VISIBILITY_FAIL_VISIBLE
            for result in results
            if result.aggregation_state in NON_AGGREGATED_STATES
        ),
    }
    audit = V38CoordinationAggregationAudit(
        audit_id="v3_8_coordination_intelligence_aggregation_audit",
        audit_status=V3_8_AGGREGATION_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_AGGREGATION_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        source_compatibility_audit_id=compatibility_audit.audit_id,
        source_evaluation_audit_id=evaluation_audit.audit_id,
        source_session_audit_id=session_audit.audit_id,
        source_scenario_audit_id=scenario_audit.audit_id,
        aggregation_results=results,
        intelligence_summaries=summaries,
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
        ranking_enabled=False,
        scoring_choice_system_enabled=False,
        selection_engine_enabled=False,
        execution_authorization_enabled=False,
        runtime_engine_enabled=False,
        state_machine_enabled=False,
        aggregation_runtime_state_machine_enabled=False,
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_aggregation_hash=hash_v3_8_aggregation_audit(audit))


def export_v3_8_coordination_intelligence_aggregation_audit(
    audit: V38CoordinationAggregationAudit,
) -> dict[str, object]:
    return export_v3_8_aggregation_audit(audit)


def count_v3_8_aggregation_states(
    results: tuple[V38CoordinationAggregationResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_aggregation_results(
    scenario_audit: V38CoordinationScenarioAudit,
) -> tuple[V38CoordinationAggregationResult, ...]:
    results = [
        _result_from_scenario(scenario_result)
        for scenario_result in scenario_audit.scenario_results
    ]
    return tuple(sorted(results, key=lambda item: (item.aggregation_state, item.aggregation_id)))


def _result_from_scenario(
    scenario_result: V38CoordinationScenarioResult,
) -> V38CoordinationAggregationResult:
    state = SCENARIO_TO_AGGREGATION_STATE[scenario_result.scenario_state]
    return _result(
        subject_id=scenario_result.scenario_id,
        state=state,
        severity=_severity_for_state(state),
        explanation=_aggregation_explanation(state, scenario_result.explanation),
        source_references=scenario_result.source_coordination_references,
        boundary_context_ids=scenario_result.boundary_context_ids,
        compatibility_context_ids=scenario_result.compatibility_context_ids,
        evaluation_context_ids=scenario_result.evaluation_context_ids,
        session_context_ids=scenario_result.session_context_ids,
        scenario_context_ids=(scenario_result.scenario_id,),
        provenance_reference=scenario_result.provenance_reference,
        replay_evidence=scenario_result.replay_safe_evidence,
        rollback_evidence=scenario_result.rollback_safe_evidence,
        deterministic_hash_references=("v3_8_coordination_scenario_hash",),
        experimental_label_explicit=state == AGGREGATION_STATE_EXPERIMENTAL,
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
    session_context_ids: tuple[str, ...],
    scenario_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    experimental_label_explicit: bool = False,
) -> V38CoordinationAggregationResult:
    deterministic_visibility_status = (
        AGGREGATION_VISIBILITY_VISIBLE
        if state == AGGREGATION_STATE_AGGREGATED
        else AGGREGATION_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationAggregationEvidence(
        evidence_id=f"evidence_{aggregation_id(state, subject_id)}",
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_context_ids=scenario_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
    )
    return V38CoordinationAggregationResult(
        aggregation_id=aggregation_id(state, subject_id),
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_context_ids=scenario_context_ids,
        aggregation_state=state,
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
        ranking_behavior_enabled=False,
        scoring_behavior_enabled=False,
        selection_behavior_enabled=False,
        execution_behavior_detected=False,
        callable_execution_path_enabled=False,
    )


def _build_intelligence_summaries(
    results: tuple[V38CoordinationAggregationResult, ...],
    state_counts: dict[str, int],
) -> tuple[V38CoordinationIntelligenceSummary, ...]:
    fail_visible_finding_count = sum(
        1
        for result in results
        if result.aggregation_state in NON_AGGREGATED_STATES
        and result.fail_visible
        and not result.hidden
    )
    summary = V38CoordinationIntelligenceSummary(
        summary_id=aggregation_summary_id("visibility_coverage"),
        summary_scope="planning_only_aggregation_visibility_coverage",
        summary_statement=(
            "summary preserves aggregation visibility evidence coverage context delta comparison planning-only non-executable"
        ),
        total_coordination_record_count=len(results),
        supported_visibility_count=state_counts[AGGREGATION_STATE_AGGREGATED],
        unsupported_visibility_count=state_counts[AGGREGATION_STATE_UNSUPPORTED],
        prohibited_visibility_count=state_counts[AGGREGATION_STATE_PROHIBITED],
        unknown_visibility_count=state_counts[AGGREGATION_STATE_UNKNOWN],
        compatibility_visibility_count=sum(1 for result in results if result.compatibility_context_ids),
        evaluation_visibility_count=sum(1 for result in results if result.evaluation_context_ids),
        session_visibility_count=sum(1 for result in results if result.session_context_ids),
        scenario_visibility_count=sum(1 for result in results if result.scenario_context_ids),
        fail_visible_finding_count=fail_visible_finding_count,
        provenance_continuity_count=sum(1 for result in results if result.evidence.provenance_preserved),
        replay_evidence_count=sum(1 for result in results if result.evidence.replay_safe),
        rollback_evidence_count=sum(1 for result in results if result.evidence.rollback_safe),
        non_execution_confirmation_count=sum(1 for result in results if result.non_execution_confirmation),
        visibility_status=AGGREGATION_VISIBILITY_FAIL_VISIBLE
        if fail_visible_finding_count
        else AGGREGATION_VISIBILITY_VISIBLE,
        non_execution_confirmation=True,
        immutable_evidence_record=True,
        runtime_state_machine=False,
        recommendation_behavior_enabled=False,
        optimization_behavior_enabled=False,
        ranking_behavior_enabled=False,
        scoring_behavior_enabled=False,
        selection_behavior_enabled=False,
        execution_behavior_detected=False,
        hidden=False,
        hidden_risk=False,
    )
    return (summary,)


def _aggregation_explanation(state: str, scenario_explanation: str) -> str:
    if state == AGGREGATION_STATE_AGGREGATED:
        return f"aggregated coordination evidence is complete enough for deterministic summary coverage: {scenario_explanation}"
    if state == AGGREGATION_STATE_PARTIAL:
        return f"partial aggregation evidence remains fail-visible: {scenario_explanation}"
    if state == AGGREGATION_STATE_BLOCKED:
        return f"blocked aggregation evidence remains fail-visible: {scenario_explanation}"
    if state == AGGREGATION_STATE_UNSUPPORTED:
        return f"unsupported aggregation evidence remains fail-visible: {scenario_explanation}"
    if state == AGGREGATION_STATE_PROHIBITED:
        return f"prohibited aggregation evidence remains intentionally blocked: {scenario_explanation}"
    if state == AGGREGATION_STATE_UNKNOWN:
        return f"unknown aggregation evidence lacks sufficient deterministic support: {scenario_explanation}"
    if state == AGGREGATION_STATE_EXPERIMENTAL:
        return f"experimental aggregation is explicitly labeled: {scenario_explanation}"
    if state == AGGREGATION_STATE_PLANNING_ONLY:
        return f"planning-only aggregation evidence remains non-executable: {scenario_explanation}"
    if state == AGGREGATION_STATE_NON_EXECUTABLE:
        return f"non-executable aggregation evidence confirms execution is absent: {scenario_explanation}"
    return scenario_explanation


def _severity_for_state(state: str) -> str:
    if state in (AGGREGATION_STATE_BLOCKED, AGGREGATION_STATE_PROHIBITED):
        return AGGREGATION_SEVERITY_BLOCKED
    if state in (AGGREGATION_STATE_PARTIAL, AGGREGATION_STATE_UNSUPPORTED, AGGREGATION_STATE_UNKNOWN):
        return AGGREGATION_SEVERITY_WARNING
    return AGGREGATION_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationAggregationResult, ...]) -> dict[str, int]:
    counts = Counter(result.aggregation_state for result in results)
    return {state: counts.get(state, 0) for state in AGGREGATION_STATES}


def _visible_count(results: tuple[V38CoordinationAggregationResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.aggregation_state == state
        and result.deterministic_visibility_status == AGGREGATION_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _summary_language_violation_count(
    summaries: tuple[V38CoordinationIntelligenceSummary, ...],
    terms: tuple[str, ...],
) -> int:
    return sum(
        _text_violation_count(
            (
                summary.summary_id,
                summary.summary_scope,
                summary.summary_statement,
                summary.visibility_status,
            ),
            terms,
        )
        for summary in summaries
    )


def _text_violation_count(values: tuple[str, ...], terms: tuple[str, ...]) -> int:
    text = " ".join(values).lower()
    return sum(1 for term in terms if term.lower() in text)


def _behavior_count(
    results: tuple[V38CoordinationAggregationResult, ...],
    summaries: tuple[V38CoordinationIntelligenceSummary, ...],
    field_name: str,
) -> int:
    return sum(1 for result in results if getattr(result, field_name)) + sum(
        1 for summary in summaries if getattr(summary, field_name)
    )


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    compatibility_audit: object,
    evaluation_audit: object,
    session_audit: object,
    scenario_audit: V38CoordinationScenarioAudit,
    results: tuple[V38CoordinationAggregationResult, ...],
    summaries: tuple[V38CoordinationIntelligenceSummary, ...],
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
        scenario_audit.coordination_execution_enabled,
        scenario_audit.orchestration_execution_enabled,
        scenario_audit.routing_enabled,
        scenario_audit.scheduling_enabled,
        scenario_audit.dispatch_enabled,
        scenario_audit.traversal_execution_enabled,
        scenario_audit.optimization_enabled,
        scenario_audit.recommendation_enabled,
        scenario_audit.scoring_decision_system_enabled,
        scenario_audit.execution_authorization_enabled,
        scenario_audit.runtime_engine_enabled,
        scenario_audit.state_machine_enabled,
        scenario_audit.scenario_runtime_state_machine_enabled,
        scenario_audit.callable_coordination_flow_enabled,
        scenario_audit.persistent_runtime_mutation_enabled,
        scenario_audit.hidden_transition_enabled,
        scenario_audit.silent_fallback_enabled,
    )
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for value in audit_flags if value)
        + sum(
            1
            for result in scenario_audit.scenario_results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_state_machine
            or result.evidence.runtime_state_machine
        )
        + sum(
            1
            for comparison in scenario_audit.scenario_comparisons
            if comparison.execution_behavior_detected
            or not comparison.non_execution_confirmation
            or comparison.runtime_state_machine
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
            for summary in summaries
            if summary.execution_behavior_detected
            or not summary.non_execution_confirmation
            or summary.runtime_state_machine
        )
    )
