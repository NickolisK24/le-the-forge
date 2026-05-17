"""Deterministic v3.8 coordination integrity enforcement by audit."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_aggregation_models import (
    AGGREGATION_STATE_AGGREGATED,
    AGGREGATION_STATE_BLOCKED,
    AGGREGATION_STATE_EXPERIMENTAL,
    AGGREGATION_STATE_NON_EXECUTABLE,
    AGGREGATION_STATE_PARTIAL,
    AGGREGATION_STATE_PLANNING_ONLY,
    AGGREGATION_STATE_PROHIBITED,
    AGGREGATION_STATE_UNKNOWN,
    AGGREGATION_STATE_UNSUPPORTED,
    V38CoordinationAggregationAudit,
    V38CoordinationAggregationResult,
)
from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_compatibility_reasoning import reason_v3_8_coordination_compatibility
from .coordination_evaluation_reasoning import reason_v3_8_coordination_evaluation
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation
from .coordination_integrity_models import (
    INTEGRITY_OPTIMIZATION_LANGUAGE_TERMS,
    INTEGRITY_RANKING_LANGUAGE_TERMS,
    INTEGRITY_RECOMMENDATION_LANGUAGE_TERMS,
    INTEGRITY_SCORING_LANGUAGE_TERMS,
    INTEGRITY_SELECTION_LANGUAGE_TERMS,
    INTEGRITY_SEVERITY_BLOCKED,
    INTEGRITY_SEVERITY_INFO,
    INTEGRITY_SEVERITY_WARNING,
    INTEGRITY_STATE_BLOCKED,
    INTEGRITY_STATE_EXPERIMENTAL,
    INTEGRITY_STATE_NON_EXECUTABLE,
    INTEGRITY_STATE_PLANNING_ONLY,
    INTEGRITY_STATE_PROHIBITED,
    INTEGRITY_STATE_SATISFIED,
    INTEGRITY_STATE_UNKNOWN,
    INTEGRITY_STATE_UNSUPPORTED,
    INTEGRITY_STATE_VIOLATED,
    INTEGRITY_STATES,
    INTEGRITY_VISIBILITY_FAIL_VISIBLE,
    INTEGRITY_VISIBILITY_VISIBLE,
    NON_SATISFIED_INTEGRITY_STATES,
    V3_8_INTEGRITY_AUDIT_BLOCKED,
    V3_8_INTEGRITY_AUDIT_STABLE,
    V38CoordinationIntegrityAudit,
    V38CoordinationIntegrityEvidence,
    V38CoordinationIntegrityResult,
    export_v3_8_integrity_audit,
    hash_v3_8_integrity_audit,
    integrity_id,
)
from .coordination_intelligence_aggregation import aggregate_v3_8_coordination_intelligence
from .coordination_scenario_reasoning import reason_v3_8_coordination_scenario
from .coordination_session_reasoning import reason_v3_8_coordination_session


AGGREGATION_TO_INTEGRITY_STATE = {
    AGGREGATION_STATE_AGGREGATED: INTEGRITY_STATE_SATISFIED,
    AGGREGATION_STATE_PARTIAL: INTEGRITY_STATE_UNKNOWN,
    AGGREGATION_STATE_BLOCKED: INTEGRITY_STATE_BLOCKED,
    AGGREGATION_STATE_UNSUPPORTED: INTEGRITY_STATE_UNSUPPORTED,
    AGGREGATION_STATE_PROHIBITED: INTEGRITY_STATE_PROHIBITED,
    AGGREGATION_STATE_UNKNOWN: INTEGRITY_STATE_UNKNOWN,
    AGGREGATION_STATE_EXPERIMENTAL: INTEGRITY_STATE_EXPERIMENTAL,
    AGGREGATION_STATE_PLANNING_ONLY: INTEGRITY_STATE_PLANNING_ONLY,
    AGGREGATION_STATE_NON_EXECUTABLE: INTEGRITY_STATE_NON_EXECUTABLE,
}


def enforce_v3_8_coordination_integrity(
    foundation: V38CoordinationFoundation | None = None,
    *,
    include_violation_fixture: bool = False,
) -> V38CoordinationIntegrityAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    compatibility_audit = reason_v3_8_coordination_compatibility(source)
    evaluation_audit = reason_v3_8_coordination_evaluation(source)
    session_audit = reason_v3_8_coordination_session(source)
    scenario_audit = reason_v3_8_coordination_scenario(source)
    aggregation_audit = aggregate_v3_8_coordination_intelligence(source)
    results = _build_integrity_results(source, aggregation_audit)
    if include_violation_fixture:
        results = tuple(sorted((*results, _violation_fixture(source)), key=lambda item: (item.integrity_state, item.integrity_id)))
    state_counts = _count_states(results)
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden)
    runtime_state_machine_count = sum(
        1
        for result in results
        if result.runtime_enforcement_state_machine
        or result.evidence.runtime_enforcement_state_machine
    )
    recommendation_language_violation_count = _language_violation_count(
        results,
        INTEGRITY_RECOMMENDATION_LANGUAGE_TERMS,
    )
    optimization_language_violation_count = _language_violation_count(
        results,
        INTEGRITY_OPTIMIZATION_LANGUAGE_TERMS,
    )
    ranking_language_violation_count = _language_violation_count(
        results,
        INTEGRITY_RANKING_LANGUAGE_TERMS,
    )
    scoring_language_violation_count = _language_violation_count(
        results,
        INTEGRITY_SCORING_LANGUAGE_TERMS,
    )
    selection_language_violation_count = _language_violation_count(
        results,
        INTEGRITY_SELECTION_LANGUAGE_TERMS,
    )
    scoring_behavior_violation_count = _behavior_count(results, "scoring_behavior_enabled")
    selection_behavior_violation_count = _behavior_count(results, "selection_behavior_enabled")
    recommendation_behavior_violation_count = _behavior_count(results, "recommendation_behavior_enabled")
    optimization_behavior_violation_count = _behavior_count(results, "optimization_behavior_enabled")
    ranking_behavior_violation_count = _behavior_count(results, "ranking_behavior_enabled")
    execution_boundary_violation_count = _execution_boundary_violation_count(
        source,
        boundary_audit,
        compatibility_audit,
        evaluation_audit,
        session_audit,
        scenario_audit,
        aggregation_audit,
        results,
    )
    validation_totals = {
        "integrity_result_count": len(results),
        "satisfied_count": state_counts[INTEGRITY_STATE_SATISFIED],
        "violated_count": state_counts[INTEGRITY_STATE_VIOLATED],
        "blocked_count": state_counts[INTEGRITY_STATE_BLOCKED],
        "unsupported_count": state_counts[INTEGRITY_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[INTEGRITY_STATE_PROHIBITED],
        "unknown_count": state_counts[INTEGRITY_STATE_UNKNOWN],
        "experimental_count": state_counts[INTEGRITY_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[INTEGRITY_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[INTEGRITY_STATE_NON_EXECUTABLE],
        "foundation_context_count": sum(1 for result in results if result.foundation_context_ids),
        "foundation_context_preserved_count": sum(
            1 for result in results if result.evidence.foundation_context_preserved
        ),
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
        "aggregation_context_count": sum(1 for result in results if result.aggregation_context_ids),
        "aggregation_context_preserved_count": sum(
            1 for result in results if result.evidence.aggregation_context_preserved
        ),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_preserved),
        "integrity_violation_count": sum(1 for result in results if result.violation_codes),
        "violation_code_count": sum(len(result.violation_codes) for result in results),
        "fail_visible_violated_count": _visible_count(results, INTEGRITY_STATE_VIOLATED),
        "fail_visible_blocked_count": _visible_count(results, INTEGRITY_STATE_BLOCKED),
        "fail_visible_unsupported_count": _visible_count(results, INTEGRITY_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, INTEGRITY_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, INTEGRITY_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1
            for result in results
            if result.integrity_state == INTEGRITY_STATE_EXPERIMENTAL
            and result.experimental_label_explicit
        ),
        "immutable_audit_evidence_record_count": sum(
            1
            for result in results
            if result.immutable_audit_evidence_record
            and result.evidence.immutable_audit_evidence_record
        ),
        "hidden_risk_count": hidden_risk_count,
        "runtime_enforcement_state_machine_count": runtime_state_machine_count,
        "recommendation_language_violation_count": recommendation_language_violation_count,
        "optimization_language_violation_count": optimization_language_violation_count,
        "ranking_language_violation_count": ranking_language_violation_count,
        "scoring_language_violation_count": scoring_language_violation_count,
        "selection_language_violation_count": selection_language_violation_count,
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
        and recommendation_behavior_violation_count == 0
        and optimization_behavior_violation_count == 0
        and ranking_behavior_violation_count == 0
        and scoring_behavior_violation_count == 0
        and selection_behavior_violation_count == 0
        and all(
            result.fail_visible
            and not result.hidden
            and result.deterministic_visibility_status == INTEGRITY_VISIBILITY_FAIL_VISIBLE
            for result in results
            if result.integrity_state in NON_SATISFIED_INTEGRITY_STATES
        ),
    }
    audit = V38CoordinationIntegrityAudit(
        audit_id="v3_8_coordination_integrity_enforcement_audit",
        audit_status=V3_8_INTEGRITY_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_INTEGRITY_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        source_compatibility_audit_id=compatibility_audit.audit_id,
        source_evaluation_audit_id=evaluation_audit.audit_id,
        source_session_audit_id=session_audit.audit_id,
        source_scenario_audit_id=scenario_audit.audit_id,
        source_aggregation_audit_id=aggregation_audit.audit_id,
        integrity_results=results,
        state_counts=state_counts,
        validation_totals=validation_totals,
        immutable_audit_evidence_records=True,
        non_executable=True,
        coordination_execution_enabled=False,
        orchestration_execution_enabled=False,
        runtime_enforcement_engine_enabled=False,
        routing_enabled=False,
        scheduling_enabled=False,
        dispatch_enabled=False,
        traversal_execution_enabled=False,
        optimization_enabled=False,
        recommendation_enabled=False,
        ranking_enabled=False,
        scoring_enabled=False,
        selection_enabled=False,
        execution_authorization_enabled=False,
        runtime_engine_enabled=False,
        state_machine_enabled=False,
        integrity_runtime_state_machine_enabled=False,
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_integrity_hash=hash_v3_8_integrity_audit(audit))


def export_v3_8_coordination_integrity_enforcement_audit(
    audit: V38CoordinationIntegrityAudit,
) -> dict[str, object]:
    return export_v3_8_integrity_audit(audit)


def count_v3_8_integrity_states(
    results: tuple[V38CoordinationIntegrityResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_integrity_results(
    source: V38CoordinationFoundation,
    aggregation_audit: V38CoordinationAggregationAudit,
) -> tuple[V38CoordinationIntegrityResult, ...]:
    results = [
        _result_from_aggregation(source, aggregation_result)
        for aggregation_result in aggregation_audit.aggregation_results
    ]
    return tuple(sorted(results, key=lambda item: (item.integrity_state, item.integrity_id)))


def _result_from_aggregation(
    source: V38CoordinationFoundation,
    aggregation_result: V38CoordinationAggregationResult,
) -> V38CoordinationIntegrityResult:
    state = AGGREGATION_TO_INTEGRITY_STATE[aggregation_result.aggregation_state]
    violation_codes = _detect_violation_codes(
        source_coordination_references=aggregation_result.source_coordination_references,
        foundation_context_ids=(source.identity.coordination_id,),
        boundary_context_ids=aggregation_result.boundary_context_ids,
        compatibility_context_ids=aggregation_result.compatibility_context_ids,
        evaluation_context_ids=aggregation_result.evaluation_context_ids,
        session_context_ids=aggregation_result.session_context_ids,
        scenario_context_ids=aggregation_result.scenario_context_ids,
        aggregation_context_ids=(aggregation_result.aggregation_id,),
        provenance_reference=aggregation_result.provenance_reference,
        replay_safe_evidence=aggregation_result.replay_safe_evidence,
        rollback_safe_evidence=aggregation_result.rollback_safe_evidence,
        hidden=aggregation_result.hidden,
        aggregation_state=aggregation_result.aggregation_state,
        execution_behavior_detected=aggregation_result.execution_behavior_detected,
        callable_execution_path_enabled=aggregation_result.callable_execution_path_enabled,
        non_execution_confirmation=aggregation_result.non_execution_confirmation,
        recommendation_behavior_enabled=aggregation_result.recommendation_behavior_enabled,
        optimization_behavior_enabled=aggregation_result.optimization_behavior_enabled,
        ranking_behavior_enabled=aggregation_result.ranking_behavior_enabled,
        scoring_behavior_enabled=aggregation_result.scoring_behavior_enabled,
        selection_behavior_enabled=aggregation_result.selection_behavior_enabled,
    )
    if violation_codes:
        state = INTEGRITY_STATE_VIOLATED
    return _result(
        subject_id=aggregation_result.aggregation_id,
        state=state,
        severity=_severity_for_state(state),
        explanation=_integrity_explanation(state),
        source_references=aggregation_result.source_coordination_references,
        foundation_context_ids=(source.identity.coordination_id,),
        boundary_context_ids=aggregation_result.boundary_context_ids,
        compatibility_context_ids=aggregation_result.compatibility_context_ids,
        evaluation_context_ids=aggregation_result.evaluation_context_ids,
        session_context_ids=aggregation_result.session_context_ids,
        scenario_context_ids=aggregation_result.scenario_context_ids,
        aggregation_context_ids=(aggregation_result.aggregation_id,),
        provenance_reference=aggregation_result.provenance_reference,
        replay_evidence=aggregation_result.replay_safe_evidence,
        rollback_evidence=aggregation_result.rollback_safe_evidence,
        deterministic_hash_references=("v3_8_coordination_aggregation_hash",),
        violation_codes=violation_codes,
        experimental_label_explicit=state == INTEGRITY_STATE_EXPERIMENTAL,
    )


def _result(
    *,
    subject_id: str,
    state: str,
    severity: str,
    explanation: str,
    source_references: tuple[str, ...],
    foundation_context_ids: tuple[str, ...],
    boundary_context_ids: tuple[str, ...],
    compatibility_context_ids: tuple[str, ...],
    evaluation_context_ids: tuple[str, ...],
    session_context_ids: tuple[str, ...],
    scenario_context_ids: tuple[str, ...],
    aggregation_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    violation_codes: tuple[str, ...],
    experimental_label_explicit: bool = False,
) -> V38CoordinationIntegrityResult:
    deterministic_visibility_status = (
        INTEGRITY_VISIBILITY_VISIBLE if state == INTEGRITY_STATE_SATISFIED else INTEGRITY_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationIntegrityEvidence(
        evidence_id=f"evidence_{integrity_id(state, subject_id)}",
        source_coordination_references=source_references,
        foundation_context_ids=foundation_context_ids,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_context_ids=scenario_context_ids,
        aggregation_context_ids=aggregation_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
        violation_codes=violation_codes,
        replay_safe=bool(replay_evidence),
        rollback_safe=bool(rollback_evidence),
        provenance_preserved=bool(provenance_reference),
        foundation_context_preserved=bool(foundation_context_ids),
        boundary_context_preserved=bool(boundary_context_ids),
        compatibility_context_preserved=bool(compatibility_context_ids),
        evaluation_context_preserved=bool(evaluation_context_ids),
        session_context_preserved=bool(session_context_ids),
        scenario_context_preserved=bool(scenario_context_ids),
        aggregation_context_preserved=bool(aggregation_context_ids),
    )
    return V38CoordinationIntegrityResult(
        integrity_id=integrity_id(state, subject_id),
        source_coordination_references=source_references,
        foundation_context_ids=foundation_context_ids,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_context_ids=scenario_context_ids,
        aggregation_context_ids=aggregation_context_ids,
        integrity_state=state,
        severity=severity,
        explanation=explanation,
        provenance_reference=provenance_reference,
        replay_safe_evidence=replay_evidence,
        rollback_safe_evidence=rollback_evidence,
        deterministic_visibility_status=deterministic_visibility_status,
        non_execution_confirmation=True,
        evidence=evidence,
        violation_codes=violation_codes,
        fail_visible=True,
        hidden=False,
        hidden_risk=False,
        experimental_label_explicit=experimental_label_explicit,
        immutable_audit_evidence_record=True,
        runtime_enforcement_state_machine=False,
        recommendation_behavior_enabled=False,
        optimization_behavior_enabled=False,
        ranking_behavior_enabled=False,
        scoring_behavior_enabled=False,
        selection_behavior_enabled=False,
        execution_behavior_detected=False,
        callable_execution_path_enabled=False,
    )


def _violation_fixture(source: V38CoordinationFoundation) -> V38CoordinationIntegrityResult:
    violation_codes = (
        "missing_required_context",
        "missing_provenance_continuity",
        "missing_replay_evidence",
        "missing_rollback_evidence",
    )
    return _result(
        subject_id="deterministic_missing_context_fixture",
        state=INTEGRITY_STATE_VIOLATED,
        severity=INTEGRITY_SEVERITY_BLOCKED,
        explanation="violated integrity audit evidence is fail-visible for deterministic test fixture coverage",
        source_references=(source.identity.coordination_id,),
        foundation_context_ids=(source.identity.coordination_id,),
        boundary_context_ids=(),
        compatibility_context_ids=(),
        evaluation_context_ids=(),
        session_context_ids=(),
        scenario_context_ids=(),
        aggregation_context_ids=(),
        provenance_reference="",
        replay_evidence=(),
        rollback_evidence=(),
        deterministic_hash_references=("v3_8_coordination_integrity_fixture_hash",),
        violation_codes=violation_codes,
    )


def _detect_violation_codes(
    *,
    source_coordination_references: tuple[str, ...],
    foundation_context_ids: tuple[str, ...],
    boundary_context_ids: tuple[str, ...],
    compatibility_context_ids: tuple[str, ...],
    evaluation_context_ids: tuple[str, ...],
    session_context_ids: tuple[str, ...],
    scenario_context_ids: tuple[str, ...],
    aggregation_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_safe_evidence: tuple[str, ...],
    rollback_safe_evidence: tuple[str, ...],
    hidden: bool,
    aggregation_state: str,
    execution_behavior_detected: bool,
    callable_execution_path_enabled: bool,
    non_execution_confirmation: bool,
    recommendation_behavior_enabled: bool,
    optimization_behavior_enabled: bool,
    ranking_behavior_enabled: bool,
    scoring_behavior_enabled: bool,
    selection_behavior_enabled: bool,
) -> tuple[str, ...]:
    codes: list[str] = []
    if not source_coordination_references:
        codes.append("missing_source_references")
    required_contexts = (
        foundation_context_ids,
        boundary_context_ids,
        compatibility_context_ids,
        evaluation_context_ids,
        session_context_ids,
        scenario_context_ids,
        aggregation_context_ids,
    )
    if any(not values for values in required_contexts):
        codes.append("missing_required_context")
    if not provenance_reference:
        codes.append("missing_provenance_continuity")
    if not replay_safe_evidence:
        codes.append("missing_replay_evidence")
    if not rollback_safe_evidence:
        codes.append("missing_rollback_evidence")
    if hidden and aggregation_state == AGGREGATION_STATE_UNSUPPORTED:
        codes.append("hidden_unsupported_state")
    if hidden and aggregation_state == AGGREGATION_STATE_PROHIBITED:
        codes.append("hidden_prohibited_state")
    if hidden and aggregation_state == AGGREGATION_STATE_UNKNOWN:
        codes.append("hidden_unknown_state")
    if hidden and aggregation_state == AGGREGATION_STATE_BLOCKED:
        codes.append("hidden_blocked_state")
    if execution_behavior_detected or callable_execution_path_enabled or not non_execution_confirmation:
        codes.append("execution_boundary_contamination")
    if recommendation_behavior_enabled:
        codes.append("recommendation_contamination")
    if optimization_behavior_enabled:
        codes.append("optimization_contamination")
    if ranking_behavior_enabled:
        codes.append("ranking_contamination")
    if scoring_behavior_enabled:
        codes.append("scoring_contamination")
    if selection_behavior_enabled:
        codes.append("selection_contamination")
    return tuple(sorted(codes))


def _integrity_explanation(state: str) -> str:
    if state == INTEGRITY_STATE_SATISFIED:
        return "satisfied integrity audit evidence preserves full coordination chain context"
    if state == INTEGRITY_STATE_VIOLATED:
        return "violated integrity audit evidence remains fail-visible"
    if state == INTEGRITY_STATE_BLOCKED:
        return "blocked integrity audit evidence remains fail-visible"
    if state == INTEGRITY_STATE_UNSUPPORTED:
        return "unsupported integrity audit evidence remains fail-visible"
    if state == INTEGRITY_STATE_PROHIBITED:
        return "prohibited integrity audit evidence remains intentionally blocked"
    if state == INTEGRITY_STATE_UNKNOWN:
        return "unknown integrity audit evidence lacks sufficient deterministic support"
    if state == INTEGRITY_STATE_EXPERIMENTAL:
        return "experimental integrity audit is explicitly labeled"
    if state == INTEGRITY_STATE_PLANNING_ONLY:
        return "planning-only integrity audit evidence remains non-executable"
    if state == INTEGRITY_STATE_NON_EXECUTABLE:
        return "non-executable integrity audit evidence confirms execution is absent"
    return "integrity audit evidence remains deterministic"


def _severity_for_state(state: str) -> str:
    if state in (INTEGRITY_STATE_VIOLATED, INTEGRITY_STATE_BLOCKED, INTEGRITY_STATE_PROHIBITED):
        return INTEGRITY_SEVERITY_BLOCKED
    if state in (INTEGRITY_STATE_UNSUPPORTED, INTEGRITY_STATE_UNKNOWN):
        return INTEGRITY_SEVERITY_WARNING
    return INTEGRITY_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationIntegrityResult, ...]) -> dict[str, int]:
    counts = Counter(result.integrity_state for result in results)
    return {state: counts.get(state, 0) for state in INTEGRITY_STATES}


def _visible_count(results: tuple[V38CoordinationIntegrityResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.integrity_state == state
        and result.deterministic_visibility_status == INTEGRITY_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _language_violation_count(
    results: tuple[V38CoordinationIntegrityResult, ...],
    terms: tuple[str, ...],
) -> int:
    return sum(
        _text_violation_count((result.explanation, *result.violation_codes), terms)
        for result in results
    )


def _text_violation_count(values: tuple[str, ...], terms: tuple[str, ...]) -> int:
    text = " ".join(values).lower()
    return sum(1 for term in terms if term.lower() in text)


def _behavior_count(results: tuple[V38CoordinationIntegrityResult, ...], field_name: str) -> int:
    return sum(1 for result in results if getattr(result, field_name))


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    compatibility_audit: object,
    evaluation_audit: object,
    session_audit: object,
    scenario_audit: object,
    aggregation_audit: V38CoordinationAggregationAudit,
    results: tuple[V38CoordinationIntegrityResult, ...],
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
        aggregation_audit.coordination_execution_enabled,
        aggregation_audit.orchestration_execution_enabled,
        aggregation_audit.runtime_enforcement_engine_enabled
        if hasattr(aggregation_audit, "runtime_enforcement_engine_enabled")
        else False,
        aggregation_audit.routing_enabled,
        aggregation_audit.scheduling_enabled,
        aggregation_audit.dispatch_enabled,
        aggregation_audit.traversal_execution_enabled,
        aggregation_audit.optimization_enabled,
        aggregation_audit.recommendation_enabled,
        aggregation_audit.ranking_enabled,
        aggregation_audit.scoring_choice_system_enabled,
        aggregation_audit.selection_engine_enabled,
        aggregation_audit.execution_authorization_enabled,
        aggregation_audit.runtime_engine_enabled,
        aggregation_audit.state_machine_enabled,
        aggregation_audit.aggregation_runtime_state_machine_enabled,
        aggregation_audit.callable_coordination_flow_enabled,
        aggregation_audit.persistent_runtime_mutation_enabled,
        aggregation_audit.hidden_transition_enabled,
        aggregation_audit.silent_fallback_enabled,
    )
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for value in audit_flags if value)
        + sum(
            1
            for result in aggregation_audit.aggregation_results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_state_machine
            or result.evidence.runtime_state_machine
        )
        + sum(
            1
            for summary in aggregation_audit.intelligence_summaries
            if summary.execution_behavior_detected
            or not summary.non_execution_confirmation
            or summary.runtime_state_machine
        )
        + sum(
            1
            for result in results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_enforcement_state_machine
            or result.evidence.runtime_enforcement_state_machine
        )
    )
