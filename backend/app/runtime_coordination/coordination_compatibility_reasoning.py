"""Deterministic v3.8 coordination compatibility reasoning."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .coordination_boundary_intelligence import audit_v3_8_coordination_boundary_intelligence
from .coordination_boundary_models import (
    BOUNDARY_CLASSIFICATION_EXPERIMENTAL,
    BOUNDARY_CLASSIFICATION_NON_EXECUTABLE,
    BOUNDARY_CLASSIFICATION_PLANNING_ONLY,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SUPPORTED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_VISIBILITY_FAIL_VISIBLE,
)
from .coordination_compatibility_models import (
    COMPATIBILITY_SEVERITY_BLOCKED,
    COMPATIBILITY_SEVERITY_INFO,
    COMPATIBILITY_SEVERITY_WARNING,
    COMPATIBILITY_STATE_COMPATIBLE,
    COMPATIBILITY_STATE_EXPERIMENTAL,
    COMPATIBILITY_STATE_INCOMPATIBLE,
    COMPATIBILITY_STATE_NON_EXECUTABLE,
    COMPATIBILITY_STATE_PLANNING_ONLY,
    COMPATIBILITY_STATE_PROHIBITED,
    COMPATIBILITY_STATE_UNKNOWN,
    COMPATIBILITY_STATE_UNSUPPORTED,
    COMPATIBILITY_STATES,
    COMPATIBILITY_VISIBILITY_FAIL_VISIBLE,
    COMPATIBILITY_VISIBILITY_VISIBLE,
    NON_COMPATIBLE_STATES,
    V3_8_COMPATIBILITY_AUDIT_BLOCKED,
    V3_8_COMPATIBILITY_AUDIT_STABLE,
    V38CoordinationCompatibilityAudit,
    V38CoordinationCompatibilityEvidence,
    V38CoordinationCompatibilityResult,
    compatibility_id,
    export_v3_8_compatibility_audit,
    hash_v3_8_compatibility_audit,
)
from .coordination_foundation_models import V38CoordinationFoundation, default_v3_8_coordination_foundation


BOUNDARY_TO_COMPATIBILITY_STATE = {
    BOUNDARY_CLASSIFICATION_SUPPORTED: COMPATIBILITY_STATE_COMPATIBLE,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED: COMPATIBILITY_STATE_UNSUPPORTED,
    BOUNDARY_CLASSIFICATION_PROHIBITED: COMPATIBILITY_STATE_PROHIBITED,
    BOUNDARY_CLASSIFICATION_UNKNOWN: COMPATIBILITY_STATE_UNKNOWN,
    BOUNDARY_CLASSIFICATION_EXPERIMENTAL: COMPATIBILITY_STATE_EXPERIMENTAL,
    BOUNDARY_CLASSIFICATION_PLANNING_ONLY: COMPATIBILITY_STATE_PLANNING_ONLY,
    BOUNDARY_CLASSIFICATION_NON_EXECUTABLE: COMPATIBILITY_STATE_NON_EXECUTABLE,
}


def reason_v3_8_coordination_compatibility(
    foundation: V38CoordinationFoundation | None = None,
) -> V38CoordinationCompatibilityAudit:
    source = foundation or default_v3_8_coordination_foundation()
    boundary_audit = audit_v3_8_coordination_boundary_intelligence(source)
    results = _build_compatibility_results(source, boundary_audit)
    state_counts = _count_states(results)
    execution_boundary_violation_count = _execution_boundary_violation_count(source, boundary_audit, results)
    hidden_risk_count = sum(1 for result in results if result.hidden_risk or result.hidden)
    validation_totals = {
        "compatibility_result_count": len(results),
        "compatible_count": state_counts[COMPATIBILITY_STATE_COMPATIBLE],
        "incompatible_count": state_counts[COMPATIBILITY_STATE_INCOMPATIBLE],
        "unsupported_count": state_counts[COMPATIBILITY_STATE_UNSUPPORTED],
        "prohibited_count": state_counts[COMPATIBILITY_STATE_PROHIBITED],
        "unknown_count": state_counts[COMPATIBILITY_STATE_UNKNOWN],
        "experimental_count": state_counts[COMPATIBILITY_STATE_EXPERIMENTAL],
        "planning_only_count": state_counts[COMPATIBILITY_STATE_PLANNING_ONLY],
        "non_executable_count": state_counts[COMPATIBILITY_STATE_NON_EXECUTABLE],
        "boundary_context_count": sum(1 for result in results if result.boundary_context_ids),
        "replay_safe_evidence_count": sum(1 for result in results if result.evidence.replay_safe),
        "rollback_safe_evidence_count": sum(1 for result in results if result.evidence.rollback_safe),
        "provenance_continuity_count": sum(1 for result in results if result.evidence.provenance_preserved),
        "boundary_context_preserved_count": sum(1 for result in results if result.evidence.boundary_context_preserved),
        "fail_visible_incompatible_count": _visible_count(results, COMPATIBILITY_STATE_INCOMPATIBLE),
        "fail_visible_unsupported_count": _visible_count(results, COMPATIBILITY_STATE_UNSUPPORTED),
        "fail_visible_prohibited_count": _visible_count(results, COMPATIBILITY_STATE_PROHIBITED),
        "fail_visible_unknown_count": _visible_count(results, COMPATIBILITY_STATE_UNKNOWN),
        "explicit_experimental_count": sum(
            1 for result in results if result.compatibility_state == COMPATIBILITY_STATE_EXPERIMENTAL and result.experimental_label_explicit
        ),
        "hidden_risk_count": hidden_risk_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "non_executable_result_count": sum(1 for result in results if result.non_execution_confirmation),
        "valid": execution_boundary_violation_count == 0
        and hidden_risk_count == 0
        and all(
            result.fail_visible and not result.hidden
            for result in results
            if result.compatibility_state in NON_COMPATIBLE_STATES
        ),
    }
    audit = V38CoordinationCompatibilityAudit(
        audit_id="v3_8_coordination_compatibility_reasoning_audit",
        audit_status=V3_8_COMPATIBILITY_AUDIT_STABLE
        if validation_totals["valid"]
        else V3_8_COMPATIBILITY_AUDIT_BLOCKED,
        source_foundation_id=source.identity.coordination_id,
        source_boundary_audit_id=boundary_audit.audit_id,
        compatibility_results=results,
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
    return replace(audit, deterministic_compatibility_hash=hash_v3_8_compatibility_audit(audit))


def export_v3_8_coordination_compatibility_reasoning_audit(
    audit: V38CoordinationCompatibilityAudit,
) -> dict[str, object]:
    return export_v3_8_compatibility_audit(audit)


def count_v3_8_compatibility_states(
    results: tuple[V38CoordinationCompatibilityResult, ...],
) -> dict[str, int]:
    return _count_states(results)


def _build_compatibility_results(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
) -> tuple[V38CoordinationCompatibilityResult, ...]:
    results: list[V38CoordinationCompatibilityResult] = []
    default_boundary_context = (
        "v3_8_non_execution_coordination_boundary",
        "v3_8_fail_visible_uncertainty_boundary",
    )
    for reference in foundation.coordination_references:
        results.append(
            _result(
                subject_id=reference.reference_id,
                state=COMPATIBILITY_STATE_COMPATIBLE,
                severity=COMPATIBILITY_SEVERITY_INFO,
                explanation=(
                    f"coordination reference {reference.reference_id} is compatible as deterministic planning evidence"
                ),
                source_references=(reference.reference_id,),
                boundary_context_ids=default_boundary_context,
                provenance_reference=reference.provenance_reference_ids[0],
                replay_evidence=reference.replay_reference_ids,
                rollback_evidence=reference.rollback_reference_ids,
                deterministic_hash_references=(reference.deterministic_hash_reference,),
            )
        )
    for chain in foundation.relationship_chains:
        results.append(
            _result(
                subject_id=chain.chain_id,
                state=COMPATIBILITY_STATE_COMPATIBLE,
                severity=COMPATIBILITY_SEVERITY_INFO,
                explanation=f"relationship chain {chain.chain_id} is compatible for planning coordination reasoning",
                source_references=chain.relationship_ids,
                boundary_context_ids=default_boundary_context,
                provenance_reference=chain.provenance_lineage_ids[0],
                replay_evidence=chain.replay_reference_ids,
                rollback_evidence=chain.rollback_reference_ids,
                deterministic_hash_references=("v3_8_coordination_relationship_chain_hash",),
            )
        )
    for finding in boundary_audit.findings:
        state = BOUNDARY_TO_COMPATIBILITY_STATE[finding.boundary_classification]
        results.append(
            _result(
                subject_id=finding.boundary_id,
                state=state,
                severity=_severity_for_state(state),
                explanation=_boundary_explanation(state, finding.explanation),
                source_references=(finding.source_coordination_reference,),
                boundary_context_ids=(finding.boundary_id,),
                provenance_reference=finding.provenance_reference,
                replay_evidence=finding.replay_safe_evidence,
                rollback_evidence=finding.rollback_safe_evidence,
                deterministic_hash_references=("v3_8_coordination_boundary_intelligence_hash",),
                visibility=finding.deterministic_visibility_status
                if state != COMPATIBILITY_STATE_COMPATIBLE
                else COMPATIBILITY_VISIBILITY_VISIBLE,
                experimental_label_explicit=state == COMPATIBILITY_STATE_EXPERIMENTAL,
            )
        )
    results.append(
        _result(
            subject_id="execution_to_non_executable_coordination",
            state=COMPATIBILITY_STATE_INCOMPATIBLE,
            severity=COMPATIBILITY_SEVERITY_BLOCKED,
            explanation=(
                "execution-oriented coordination is incompatible with non-executable planning coordination boundaries"
            ),
            source_references=(
                foundation.identity.coordination_id,
                "v3_8_boundary_non_executable_coordination",
            ),
            boundary_context_ids=(
                "v3_8_boundary_non_executable_coordination",
                "v3_8_prohibited_orchestration_execution",
            ),
            provenance_reference=foundation.provenance_state.provenance_id,
            replay_evidence=(foundation.replay_evidence[0].replay_evidence_id,),
            rollback_evidence=(foundation.rollback_evidence[0].rollback_evidence_id,),
            deterministic_hash_references=("v3_8_coordination_foundation_hash",),
        )
    )
    return tuple(sorted(results, key=lambda item: (item.compatibility_state, item.compatibility_id)))


def _result(
    *,
    subject_id: str,
    state: str,
    severity: str,
    explanation: str,
    source_references: tuple[str, ...],
    boundary_context_ids: tuple[str, ...],
    provenance_reference: str,
    replay_evidence: tuple[str, ...],
    rollback_evidence: tuple[str, ...],
    deterministic_hash_references: tuple[str, ...],
    visibility: str | None = None,
    experimental_label_explicit: bool = False,
) -> V38CoordinationCompatibilityResult:
    deterministic_visibility_status = visibility or (
        COMPATIBILITY_VISIBILITY_VISIBLE
        if state == COMPATIBILITY_STATE_COMPATIBLE
        else COMPATIBILITY_VISIBILITY_FAIL_VISIBLE
    )
    evidence = V38CoordinationCompatibilityEvidence(
        evidence_id=f"evidence_{compatibility_id(state, subject_id)}",
        source_coordination_references=source_references,
        boundary_context_ids=boundary_context_ids,
        provenance_reference=provenance_reference,
        replay_evidence_references=replay_evidence,
        rollback_evidence_references=rollback_evidence,
        deterministic_hash_references=deterministic_hash_references,
    )
    return V38CoordinationCompatibilityResult(
        compatibility_id=compatibility_id(state, subject_id),
        source_coordination_references=source_references,
        compatibility_state=state,
        severity=severity,
        explanation=explanation,
        boundary_context_ids=boundary_context_ids,
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


def _boundary_explanation(state: str, boundary_explanation: str) -> str:
    if state == COMPATIBILITY_STATE_COMPATIBLE:
        return f"boundary context is compatible for deterministic planning reasoning: {boundary_explanation}"
    if state == COMPATIBILITY_STATE_UNSUPPORTED:
        return f"unsupported compatibility state remains fail-visible: {boundary_explanation}"
    if state == COMPATIBILITY_STATE_PROHIBITED:
        return f"prohibited compatibility state remains intentionally blocked: {boundary_explanation}"
    if state == COMPATIBILITY_STATE_UNKNOWN:
        return f"unknown compatibility state lacks deterministic support evidence: {boundary_explanation}"
    if state == COMPATIBILITY_STATE_EXPERIMENTAL:
        return f"experimental compatibility reasoning is explicitly labeled: {boundary_explanation}"
    if state == COMPATIBILITY_STATE_PLANNING_ONLY:
        return f"planning-only compatibility reasoning remains non-executable: {boundary_explanation}"
    if state == COMPATIBILITY_STATE_NON_EXECUTABLE:
        return f"non-executable compatibility reasoning confirms execution is absent: {boundary_explanation}"
    return boundary_explanation


def _severity_for_state(state: str) -> str:
    if state in (COMPATIBILITY_STATE_INCOMPATIBLE, COMPATIBILITY_STATE_PROHIBITED):
        return COMPATIBILITY_SEVERITY_BLOCKED
    if state in (COMPATIBILITY_STATE_UNSUPPORTED, COMPATIBILITY_STATE_UNKNOWN):
        return COMPATIBILITY_SEVERITY_WARNING
    return COMPATIBILITY_SEVERITY_INFO


def _count_states(results: tuple[V38CoordinationCompatibilityResult, ...]) -> dict[str, int]:
    counts = Counter(result.compatibility_state for result in results)
    return {state: counts.get(state, 0) for state in COMPATIBILITY_STATES}


def _visible_count(results: tuple[V38CoordinationCompatibilityResult, ...], state: str) -> int:
    return sum(
        1
        for result in results
        if result.compatibility_state == state
        and result.deterministic_visibility_status == COMPATIBILITY_VISIBILITY_FAIL_VISIBLE
        and result.fail_visible
        and not result.hidden
    )


def _execution_boundary_violation_count(
    foundation: V38CoordinationFoundation,
    boundary_audit: object,
    results: tuple[V38CoordinationCompatibilityResult, ...],
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
    return (
        sum(1 for value in foundation_flags if value)
        + sum(1 for value in boundary_flags if value)
        + sum(
            1
            for result in results
            if result.execution_behavior_detected
            or result.callable_execution_path_enabled
            or not result.non_execution_confirmation
            or not result.evidence.non_executable
        )
    )
