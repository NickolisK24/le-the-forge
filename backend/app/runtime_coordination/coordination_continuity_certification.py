"""Deterministic v3.8 coordination continuity certification."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_aggregation_models import V38CoordinationAggregationAudit
from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_certification_models import (
    CERTIFICATION_OPTIMIZATION_LANGUAGE_TERMS,
    CERTIFICATION_RANKING_LANGUAGE_TERMS,
    CERTIFICATION_RECOMMENDATION_LANGUAGE_TERMS,
    CERTIFICATION_SCORING_LANGUAGE_TERMS,
    CERTIFICATION_SELECTION_LANGUAGE_TERMS,
    CERTIFICATION_SEVERITY_BLOCKED,
    CERTIFICATION_SEVERITY_INFO,
    CERTIFICATION_SEVERITY_WARNING,
    CERTIFICATION_STATE_BLOCKED,
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_EXPERIMENTAL,
    CERTIFICATION_STATE_NON_EXECUTABLE,
    CERTIFICATION_STATE_PLANNING_ONLY,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_UNKNOWN,
    CERTIFICATION_STATE_UNSUPPORTED,
    CERTIFICATION_STATES,
    CERTIFICATION_VISIBILITY_FAIL_VISIBLE,
    CERTIFICATION_VISIBILITY_VISIBLE,
    NON_CERTIFIED_STATES,
    V3_8_CERTIFICATION_AUDIT_BLOCKED,
    V3_8_CERTIFICATION_AUDIT_STABLE,
    V38CoordinationCertificationAudit,
    V38CoordinationCertificationEvidence,
    V38CoordinationCertificationResult,
    certification_id,
    export_v3_8_certification_audit,
    hash_v3_8_certification_audit,
)
from .coordination_compatibility_reasoning import reason_v3_8_coordination_compatibility
from .coordination_evaluation_reasoning import reason_v3_8_coordination_evaluation
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation
from .coordination_integrity_enforcement import enforce_v3_8_coordination_integrity
from .coordination_integrity_models import (
    INTEGRITY_STATE_BLOCKED,
    INTEGRITY_STATE_EXPERIMENTAL,
    INTEGRITY_STATE_NON_EXECUTABLE,
    INTEGRITY_STATE_PLANNING_ONLY,
    INTEGRITY_STATE_PROHIBITED,
    INTEGRITY_STATE_SATISFIED,
    INTEGRITY_STATE_UNKNOWN,
    INTEGRITY_STATE_UNSUPPORTED,
    INTEGRITY_STATE_VIOLATED,
    INTEGRITY_VISIBILITY_FAIL_VISIBLE,
    V38CoordinationIntegrityAudit,
    V38CoordinationIntegrityResult,
)
from .coordination_intelligence_aggregation import aggregate_v3_8_coordination_intelligence
from .coordination_scenario_reasoning import reason_v3_8_coordination_scenario
from .coordination_session_reasoning import reason_v3_8_coordination_session


INTEGRITY_TO_CERTIFICATION_STATE = {
    INTEGRITY_STATE_SATISFIED: CERTIFICATION_STATE_CERTIFIED,
    INTEGRITY_STATE_VIOLATED: CERTIFICATION_STATE_UNCERTIFIED,
    INTEGRITY_STATE_BLOCKED: CERTIFICATION_STATE_BLOCKED,
    INTEGRITY_STATE_UNSUPPORTED: CERTIFICATION_STATE_UNSUPPORTED,
    INTEGRITY_STATE_PROHIBITED: CERTIFICATION_STATE_PROHIBITED,
    INTEGRITY_STATE_UNKNOWN: CERTIFICATION_STATE_UNKNOWN,
    INTEGRITY_STATE_EXPERIMENTAL: CERTIFICATION_STATE_EXPERIMENTAL,
    INTEGRITY_STATE_PLANNING_ONLY: CERTIFICATION_STATE_PLANNING_ONLY,
    INTEGRITY_STATE_NON_EXECUTABLE: CERTIFICATION_STATE_NON_EXECUTABLE,
}


def certify_v3_8_coordination_continuity(
    foundation: V38CoordinationFoundation | None = None,
    *,
    include_failure_fixture: bool = False,
) -> V38CoordinationCertificationAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    compatibility_audit = reason_v3_8_coordination_compatibility(source)
    evaluation_audit = reason_v3_8_coordination_evaluation(source)
    session_audit = reason_v3_8_coordination_session(source)
    scenario_audit = reason_v3_8_coordination_scenario(source)
    aggregation_audit = aggregate_v3_8_coordination_intelligence(source)
    integrity_audit = enforce_v3_8_coordination_integrity(source)
    results = _build_certification_results(integrity_audit)
    if include_failure_fixture:
        results = tuple(
            sorted(
                (*results, _failure_fixture(source)),
                key=lambda item: (item.certification_state, item.certification_id),
            )
        )
    state_counts = _count_states(results)
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden)
    runtime_state_machine_count = sum(
        1
        for result in results
        if result.runtime_certification_state_machine
        or result.evidence.runtime_certification_state_machine
    )
    recommendation_language_violation_count = _language_violation_count(
        results,
        CERTIFICATION_RECOMMENDATION_LANGUAGE_TERMS,
    )
    optimization_language_violation_count = _language_violation_count(
        results,
        CERTIFICATION_OPTIMIZATION_LANGUAGE_TERMS,
    )
    ranking_language_violation_count = _language_violation_count(
        results,
        CERTIFICATION_RANKING_LANGUAGE_TERMS,
    )
    scoring_language_violation_count = _language_violation_count(
        results,
        CERTIFICATION_SCORING_LANGUAGE_TERMS,
    )
    selection_language_violation_count = _language_violation_count(
        results,
        CERTIFICATION_SELECTION_LANGUAGE_TERMS,
    )
    recommendation_behavior_violation_count = _behavior_count(results, "recommendation_behavior_enabled")
    optimization_behavior_violation_count = _behavior_count(results, "optimization_behavior_enabled")
    ranking_behavior_violation_count = _behavior_count(results, "ranking_behavior_enabled")
    scoring_behavior_violation_count = _behavior_count(results, "scoring_behavior_enabled")
    selection_behavior_violation_count = _behavior_count(results, "selection_behavior_enabled")
    execution_boundary_violation_count = _execution_boundary_violation_count(
        source,
        boundary_audit,
        compatibility_audit,
        evaluation_audit,
        session_audit,
        scenario_audit,
        aggregation_audit,
        integrity_audit,
        results,
    )
    validation_totals = {
        "certification_result_count": len(results),
        "certified_count": state_counts[CERTIFICATION_STATE_CERTIFIED],
        "uncertified_count": state_counts[CERTIFICATION_STATE_UNCERTIFIED],
        "blocked_count": state_counts[CERTIFICATION_STATE_BLOCKED],
        "unsupported_count": state_counts[CERTIFICATION_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[CERTIFICATION_STATE_PROHIBITED],
        "unknown_count": state_counts[CERTIFICATION_STATE_UNKNOWN],
        "experimental_count": state_counts[CERTIFICATION_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[CERTIFICATION_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[CERTIFICATION_STATE_NON_EXECUTABLE],
        "foundation_context_count": sum(1 for result in results if result.foundation_context_ids),
        "foundation_context_certified_count": sum(
            1 for result in results if result.evidence.foundation_continuity_certified
        ),
        "boundary_context_count": sum(1 for result in results if result.boundary_context_ids),
        "boundary_context_certified_count": sum(
            1 for result in results if result.evidence.boundary_continuity_certified
        ),
        "compatibility_context_count": sum(1 for result in results if result.compatibility_context_ids),
        "compatibility_context_certified_count": sum(
            1 for result in results if result.evidence.compatibility_continuity_certified
        ),
        "evaluation_context_count": sum(1 for result in results if result.evaluation_context_ids),
        "evaluation_context_certified_count": sum(
            1 for result in results if result.evidence.evaluation_continuity_certified
        ),
        "session_context_count": sum(1 for result in results if result.session_context_ids),
        "session_context_certified_count": sum(
            1 for result in results if result.evidence.session_continuity_certified
        ),
        "scenario_context_count": sum(1 for result in results if result.scenario_context_ids),
        "scenario_context_certified_count": sum(
            1 for result in results if result.evidence.scenario_continuity_certified
        ),
        "aggregation_context_count": sum(1 for result in results if result.aggregation_context_ids),
        "aggregation_context_certified_count": sum(
            1 for result in results if result.evidence.aggregation_continuity_certified
        ),
        "integrity_context_count": sum(1 for result in results if result.integrity_context_ids),
        "integrity_context_certified_count": sum(
            1 for result in results if result.evidence.integrity_continuity_certified
        ),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_certified),
        "explainability_continuity_count": sum(
            1 for result in results if result.evidence.explainability_continuity_certified
        ),
        "non_execution_continuity_count": sum(
            1 for result in results if result.evidence.non_execution_continuity_certified
        ),
        "fail_visible_state_continuity_count": sum(
            1 for result in results if result.evidence.fail_visible_state_continuity_certified
        ),
        "continuity_certification_failure_count": sum(
            1 for result in results if result.certification_failure_codes
        ),
        "certification_failure_code_count": sum(
            len(result.certification_failure_codes) for result in results
        ),
        "certified_visible_count": _visible_certified_count(results),
        "fail_visible_uncertified_count": _visible_count(results, CERTIFICATION_STATE_UNCERTIFIED),
        "fail_visible_blocked_count": _visible_count(results, CERTIFICATION_STATE_BLOCKED),
        "fail_visible_unsupported_count": _visible_count(results, CERTIFICATION_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, CERTIFICATION_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, CERTIFICATION_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1
            for result in results
            if result.certification_state == CERTIFICATION_STATE_EXPERIMENTAL
            and result.experimental_label_explicit
        ),
        "immutable_certification_evidence_record_count": sum(
            1
            for result in results
            if result.immutable_certification_evidence_record
            and result.evidence.immutable_certification_evidence_record
        ),
        "hidden_risk_count": hidden_risk_count,
        "runtime_certification_state_machine_count": runtime_state_machine_count,
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
            and result.deterministic_visibility_status == CERTIFICATION_VISIBILITY_FAIL_VISIBLE
            for result in results
            if result.certification_state in NON_CERTIFIED_STATES
        ),
    }
    audit = V38CoordinationCertificationAudit(
        audit_id="v3_8_coordination_continuity_certification_audit",
        audit_status=V3_8_CERTIFICATION_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_CERTIFICATION_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        source_compatibility_audit_id=compatibility_audit.audit_id,
        source_evaluation_audit_id=evaluation_audit.audit_id,
        source_session_audit_id=session_audit.audit_id,
        source_scenario_audit_id=scenario_audit.audit_id,
        source_aggregation_audit_id=aggregation_audit.audit_id,
        source_integrity_audit_id=integrity_audit.audit_id,
        certification_results=results,
        state_counts=state_counts,
        validation_totals=validation_totals,
        immutable_certification_evidence_records=True,
        non_executable=True,
        coordination_execution_enabled=False,
        orchestration_execution_enabled=False,
        runtime_certification_engine_enabled=False,
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
        certification_runtime_state_machine_enabled=False,
        callable_coordination_flow_enabled=False,
        persistent_runtime_mutation_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
    )
    return replace(audit, deterministic_certification_hash=hash_v3_8_certification_audit(audit))


def export_v3_8_coordination_continuity_certification_audit(
    audit: V38CoordinationCertificationAudit,
) -> dict[str, object]:
    return export_v3_8_certification_audit(audit)


def count_v3_8_certification_states(
    results: tuple[V38CoordinationCertificationResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_certification_results(
    integrity_audit: V38CoordinationIntegrityAudit,
) -> tuple[V38CoordinationCertificationResult, ...]:
    results = [
        _result_from_integrity(integrity_result)
        for integrity_result in integrity_audit.integrity_results
    ]
    return tuple(sorted(results, key=lambda item: (item.certification_state, item.certification_id)))


def _result_from_integrity(
    integrity_result: V38CoordinationIntegrityResult,
) -> V38CoordinationCertificationResult:
    state = INTEGRITY_TO_CERTIFICATION_STATE[integrity_result.integrity_state]
    failure_codes = _detect_failure_codes(
        source_coordination_references=integrity_result.source_coordination_references,
        foundation_context_ids=integrity_result.foundation_context_ids,
        boundary_context_ids=integrity_result.boundary_context_ids,
        compatibility_context_ids=integrity_result.compatibility_context_ids,
        evaluation_context_ids=integrity_result.evaluation_context_ids,
        session_context_ids=integrity_result.session_context_ids,
        scenario_context_ids=integrity_result.scenario_context_ids,
        aggregation_context_ids=integrity_result.aggregation_context_ids,
        integrity_context_ids=(integrity_result.integrity_id,),
        provenance_reference=integrity_result.provenance_reference,
        replay_safe_evidence=integrity_result.replay_safe_evidence,
        rollback_safe_evidence=integrity_result.rollback_safe_evidence,
        explanation=integrity_result.explanation,
        visibility_status=integrity_result.deterministic_visibility_status,
        fail_visible=integrity_result.fail_visible,
        hidden=integrity_result.hidden,
        upstream_failure_codes=integrity_result.violation_codes,
        upstream_state=integrity_result.integrity_state,
        execution_behavior_detected=integrity_result.execution_behavior_detected,
        callable_execution_path_enabled=integrity_result.callable_execution_path_enabled,
        non_execution_confirmation=integrity_result.non_execution_confirmation,
        recommendation_behavior_enabled=integrity_result.recommendation_behavior_enabled,
        optimization_behavior_enabled=integrity_result.optimization_behavior_enabled,
        ranking_behavior_enabled=integrity_result.ranking_behavior_enabled,
        scoring_behavior_enabled=integrity_result.scoring_behavior_enabled,
        selection_behavior_enabled=integrity_result.selection_behavior_enabled,
    )
    if failure_codes:
        state = CERTIFICATION_STATE_UNCERTIFIED
    return _result(
        subject_id=integrity_result.integrity_id,
        state=state,
        severity=_severity_for_state(state),
        explanation=_certification_explanation(state),
        source_references=integrity_result.source_coordination_references,
        foundation_context_ids=integrity_result.foundation_context_ids,
        boundary_context_ids=integrity_result.boundary_context_ids,
        compatibility_context_ids=integrity_result.compatibility_context_ids,
        evaluation_context_ids=integrity_result.evaluation_context_ids,
        session_context_ids=integrity_result.session_context_ids,
        scenario_context_ids=integrity_result.scenario_context_ids,
        aggregation_context_ids=integrity_result.aggregation_context_ids,
        integrity_context_ids=(integrity_result.integrity_id,),
        provenance_reference=integrity_result.provenance_reference,
        replay_evidence=integrity_result.replay_safe_evidence,
        rollback_evidence=integrity_result.rollback_safe_evidence,
        deterministic_hash_references=("v3_8_coordination_integrity_hash",),
        certification_failure_codes=failure_codes,
        experimental_label_explicit=state == CERTIFICATION_STATE_EXPERIMENTAL,
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
    integrity_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    certification_failure_codes: tuple[str, ...],
    experimental_label_explicit: bool = False,
) -> V38CoordinationCertificationResult:
    deterministic_visibility_status = (
        CERTIFICATION_VISIBILITY_VISIBLE
        if state == CERTIFICATION_STATE_CERTIFIED
        else CERTIFICATION_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationCertificationEvidence(
        evidence_id=f"evidence_{certification_id(state, subject_id)}",
        source_coordination_references=source_references,
        foundation_context_ids=foundation_context_ids,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_context_ids=scenario_context_ids,
        aggregation_context_ids=aggregation_context_ids,
        integrity_context_ids=integrity_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
        certification_failure_codes=certification_failure_codes,
        replay_safe=bool(replay_evidence),
        rollback_safe=bool(rollback_evidence),
        provenance_certified=bool(provenance_reference),
        foundation_continuity_certified=bool(foundation_context_ids),
        boundary_continuity_certified=bool(boundary_context_ids),
        compatibility_continuity_certified=bool(compatibility_context_ids),
        evaluation_continuity_certified=bool(evaluation_context_ids),
        session_continuity_certified=bool(session_context_ids),
        scenario_continuity_certified=bool(scenario_context_ids),
        aggregation_continuity_certified=bool(aggregation_context_ids),
        integrity_continuity_certified=bool(integrity_context_ids),
        explainability_continuity_certified=bool(explanation and deterministic_visibility_status),
        non_execution_continuity_certified=True,
        fail_visible_state_continuity_certified=(
            state == CERTIFICATION_STATE_CERTIFIED
            or deterministic_visibility_status == CERTIFICATION_VISIBILITY_FAIL_VISIBLE
        ),
    )
    return V38CoordinationCertificationResult(
        certification_id=certification_id(state, subject_id),
        source_coordination_references=source_references,
        foundation_context_ids=foundation_context_ids,
        boundary_context_ids=boundary_context_ids,
        compatibility_context_ids=compatibility_context_ids,
        evaluation_context_ids=evaluation_context_ids,
        session_context_ids=session_context_ids,
        scenario_context_ids=scenario_context_ids,
        aggregation_context_ids=aggregation_context_ids,
        integrity_context_ids=integrity_context_ids,
        certification_state=state,
        severity=severity,
        explanation=explanation,
        provenance_reference=provenance_reference,
        replay_safe_evidence=replay_evidence,
        rollback_safe_evidence=rollback_evidence,
        deterministic_visibility_status=deterministic_visibility_status,
        non_execution_confirmation=True,
        evidence=evidence,
        certification_failure_codes=certification_failure_codes,
        fail_visible=True,
        hidden=False,
        hidden_risk=False,
        experimental_label_explicit=experimental_label_explicit,
        immutable_certification_evidence_record=True,
        runtime_certification_state_machine=False,
        recommendation_behavior_enabled=False,
        optimization_behavior_enabled=False,
        ranking_behavior_enabled=False,
        scoring_behavior_enabled=False,
        selection_behavior_enabled=False,
        execution_behavior_detected=False,
        callable_execution_path_enabled=False,
    )


def _failure_fixture(source: V38CoordinationFoundation) -> V38CoordinationCertificationResult:
    failure_codes = (
        "aggregation_continuity_missing",
        "boundary_continuity_missing",
        "compatibility_continuity_missing",
        "evaluation_continuity_missing",
        "integrity_continuity_missing",
        "provenance_continuity_missing",
        "replay_continuity_missing",
        "rollback_continuity_missing",
        "scenario_continuity_missing",
        "session_continuity_missing",
    )
    return _result(
        subject_id="deterministic_missing_continuity_fixture",
        state=CERTIFICATION_STATE_UNCERTIFIED,
        severity=CERTIFICATION_SEVERITY_BLOCKED,
        explanation="uncertified continuity evidence is fail-visible for deterministic test fixture coverage",
        source_references=(source.identity.coordination_id,),
        foundation_context_ids=(source.identity.coordination_id,),
        boundary_context_ids=(),
        compatibility_context_ids=(),
        evaluation_context_ids=(),
        session_context_ids=(),
        scenario_context_ids=(),
        aggregation_context_ids=(),
        integrity_context_ids=(),
        provenance_reference="",
        replay_evidence=(),
        rollback_evidence=(),
        deterministic_hash_references=("v3_8_coordination_certification_fixture_hash",),
        certification_failure_codes=failure_codes,
    )


def _detect_failure_codes(
    *,
    source_coordination_references: tuple[str, ...],
    foundation_context_ids: tuple[str, ...],
    boundary_context_ids: tuple[str, ...],
    compatibility_context_ids: tuple[str, ...],
    evaluation_context_ids: tuple[str, ...],
    session_context_ids: tuple[str, ...],
    scenario_context_ids: tuple[str, ...],
    aggregation_context_ids: tuple[str, ...],
    integrity_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_safe_evidence: tuple[str, ...],
    rollback_safe_evidence: tuple[str, ...],
    explanation: str,
    visibility_status: str,
    fail_visible: bool,
    hidden: bool,
    upstream_failure_codes: tuple[str, ...],
    upstream_state: str,
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
        codes.append("foundation_continuity_missing")
    if not foundation_context_ids:
        codes.append("foundation_continuity_missing")
    if not boundary_context_ids:
        codes.append("boundary_continuity_missing")
    if not compatibility_context_ids:
        codes.append("compatibility_continuity_missing")
    if not evaluation_context_ids:
        codes.append("evaluation_continuity_missing")
    if not session_context_ids:
        codes.append("session_continuity_missing")
    if not scenario_context_ids:
        codes.append("scenario_continuity_missing")
    if not aggregation_context_ids:
        codes.append("aggregation_continuity_missing")
    if not integrity_context_ids or upstream_failure_codes:
        codes.append("integrity_continuity_missing")
    if not provenance_reference:
        codes.append("provenance_continuity_missing")
    if not replay_safe_evidence:
        codes.append("replay_continuity_missing")
    if not rollback_safe_evidence:
        codes.append("rollback_continuity_missing")
    if not explanation or not visibility_status:
        codes.append("explainability_continuity_missing")
    if upstream_state != INTEGRITY_STATE_SATISFIED and (
        not fail_visible or hidden or visibility_status != INTEGRITY_VISIBILITY_FAIL_VISIBLE
    ):
        codes.append("fail_visible_state_continuity_missing")
    if execution_behavior_detected or callable_execution_path_enabled or not non_execution_confirmation:
        codes.append("non_execution_continuity_missing")
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
    return tuple(sorted(set(codes)))


def _certification_explanation(state: str) -> str:
    if state == CERTIFICATION_STATE_CERTIFIED:
        return "certified continuity evidence preserves full coordination chain context"
    if state == CERTIFICATION_STATE_UNCERTIFIED:
        return "uncertified continuity evidence remains fail-visible"
    if state == CERTIFICATION_STATE_BLOCKED:
        return "blocked continuity certification evidence remains fail-visible"
    if state == CERTIFICATION_STATE_UNSUPPORTED:
        return "unsupported continuity certification evidence remains fail-visible"
    if state == CERTIFICATION_STATE_PROHIBITED:
        return "prohibited continuity certification evidence remains intentionally blocked"
    if state == CERTIFICATION_STATE_UNKNOWN:
        return "unknown continuity certification evidence lacks sufficient deterministic support"
    if state == CERTIFICATION_STATE_EXPERIMENTAL:
        return "experimental continuity certification is explicitly labeled"
    if state == CERTIFICATION_STATE_PLANNING_ONLY:
        return "planning-only continuity certification evidence remains non-executable"
    if state == CERTIFICATION_STATE_NON_EXECUTABLE:
        return "non-executable continuity certification evidence confirms execution is absent"
    return "continuity certification evidence remains deterministic"


def _severity_for_state(state: str) -> str:
    if state in (
        CERTIFICATION_STATE_UNCERTIFIED,
        CERTIFICATION_STATE_BLOCKED,
        CERTIFICATION_STATE_PROHIBITED,
    ):
        return CERTIFICATION_SEVERITY_BLOCKED
    if state in (CERTIFICATION_STATE_UNSUPPORTED, CERTIFICATION_STATE_UNKNOWN):
        return CERTIFICATION_SEVERITY_WARNING
    return CERTIFICATION_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationCertificationResult, ...]) -> dict[str, int]:
    counts = Counter(result.certification_state for result in results)
    return {state: counts.get(state, 0) for state in CERTIFICATION_STATES}


def _visible_certified_count(results: tuple[V38CoordinationCertificationResult, ...]) -> int:
    return sum(
        1
        for result in results
        if result.certification_state == CERTIFICATION_STATE_CERTIFIED
        and result.deterministic_visibility_status == CERTIFICATION_VISIBILITY_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _visible_count(results: tuple[V38CoordinationCertificationResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.certification_state == state
        and result.deterministic_visibility_status == CERTIFICATION_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _language_violation_count(
    results: tuple[V38CoordinationCertificationResult, ...],
    terms: tuple[str, ...],
) -> int:
    return sum(
        _text_violation_count((result.explanation, *result.certification_failure_codes), terms)
        for result in results
    )


def _text_violation_count(values: tuple[str, ...], terms: tuple[str, ...]) -> int:
    text = " ".join(values).lower()
    return sum(1 for term in terms if term.lower() in text)


def _behavior_count(results: tuple[V38CoordinationCertificationResult, ...], field_name: str) -> int:
    return sum(1 for result in results if getattr(result, field_name))


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    compatibility_audit: object,
    evaluation_audit: object,
    session_audit: object,
    scenario_audit: object,
    aggregation_audit: V38CoordinationAggregationAudit,
    integrity_audit: V38CoordinationIntegrityAudit,
    results: tuple[V38CoordinationCertificationResult, ...],
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
    audit_flag_names = (
        "coordination_execution_enabled",
        "orchestration_execution_enabled",
        "runtime_certification_engine_enabled",
        "runtime_enforcement_engine_enabled",
        "routing_enabled",
        "scheduling_enabled",
        "dispatch_enabled",
        "traversal_execution_enabled",
        "optimization_enabled",
        "recommendation_enabled",
        "ranking_enabled",
        "scoring_enabled",
        "scoring_choice_system_enabled",
        "selection_enabled",
        "selection_engine_enabled",
        "execution_authorization_enabled",
        "runtime_engine_enabled",
        "state_machine_enabled",
        "session_runtime_state_machine_enabled",
        "scenario_runtime_state_machine_enabled",
        "aggregation_runtime_state_machine_enabled",
        "integrity_runtime_state_machine_enabled",
        "certification_runtime_state_machine_enabled",
        "callable_coordination_flow_enabled",
        "persistent_runtime_mutation_enabled",
        "hidden_transition_enabled",
        "silent_fallback_enabled",
    )
    audits = (
        boundary_audit,
        compatibility_audit,
        evaluation_audit,
        session_audit,
        scenario_audit,
        aggregation_audit,
        integrity_audit,
    )
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for audit in audits for field_name in audit_flag_names if getattr(audit, field_name, False))
        + sum(
            1
            for result in integrity_audit.integrity_results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_enforcement_state_machine
            or result.evidence.runtime_enforcement_state_machine
        )
        + sum(
            1
            for result in results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
            or result.runtime_certification_state_machine
            or result.evidence.runtime_certification_state_machine
        )
    )
