"""Deterministic v3.9 transition integrity enforcement audit.

The audit reports integrity evidence only. It does not execute, repair,
authorize, approve, mutate, recommend, rank, score, select, prioritize,
route, schedule, dispatch, traverse, or expose callable behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_aggregation_engine import build_v3_9_transition_aggregation
from .transition_aggregation_models import REQUIRED_AGGREGATION_DOMAINS, TransitionAggregationReport
from .transition_integrity_models import (
    INTEGRITY_CHOICE_PROHIBITED_CAPABILITIES,
    INTEGRITY_CLASSIFICATION_BLOCKED,
    INTEGRITY_CLASSIFICATION_FAILED,
    INTEGRITY_CLASSIFICATION_INCOMPLETE,
    INTEGRITY_CLASSIFICATION_PROHIBITED,
    INTEGRITY_CLASSIFICATION_SATISFIED,
    INTEGRITY_CLASSIFICATION_UNKNOWN,
    INTEGRITY_CLASSIFICATION_UNSUPPORTED,
    INTEGRITY_CLASSIFICATION_WARNING,
    INTEGRITY_CLASSIFICATIONS,
    INTEGRITY_FINDING_AGGREGATION,
    INTEGRITY_FINDING_BOUNDARY,
    INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
    INTEGRITY_FINDING_CATEGORIES,
    INTEGRITY_FINDING_COMPATIBILITY,
    INTEGRITY_FINDING_EVALUATION,
    INTEGRITY_FINDING_EXPLAINABILITY,
    INTEGRITY_FINDING_FAIL_VISIBLE,
    INTEGRITY_FINDING_FOUNDATION,
    INTEGRITY_FINDING_GOVERNANCE,
    INTEGRITY_FINDING_HIDDEN_FINDING,
    INTEGRITY_FINDING_HIDDEN_NON_SAFE,
    INTEGRITY_FINDING_HIDDEN_RISK,
    INTEGRITY_FINDING_INTEGRITY_PRECONDITION,
    INTEGRITY_FINDING_MISSING_EVIDENCE,
    INTEGRITY_FINDING_PROHIBITED,
    INTEGRITY_FINDING_PROVENANCE,
    INTEGRITY_FINDING_REPLAY,
    INTEGRITY_FINDING_RISK_VISIBILITY,
    INTEGRITY_FINDING_ROLLBACK,
    INTEGRITY_FINDING_SCENARIO,
    INTEGRITY_FINDING_SESSION,
    INTEGRITY_FINDING_UNCERTAINTY,
    INTEGRITY_FINDING_UNSUPPORTED,
    INTEGRITY_FINDING_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP,
    INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK,
    INTEGRITY_VIOLATION_EXPLAINABILITY_GAP,
    INTEGRITY_VIOLATION_HIDDEN_FINDING,
    INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE,
    INTEGRITY_VIOLATION_HIDDEN_RISK,
    INTEGRITY_VIOLATION_MISSING_AGGREGATION_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_BOUNDARY_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_COMPATIBILITY_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_EVALUATION_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP,
    INTEGRITY_VIOLATION_MISSING_FOUNDATION_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_SCENARIO_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_SESSION_EVIDENCE,
    INTEGRITY_VIOLATION_MUTATION_LEAK,
    INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_PROVENANCE_GAP,
    INTEGRITY_VIOLATION_RANKING_LEAK,
    INTEGRITY_VIOLATION_RECOMMENDATION_LEAK,
    INTEGRITY_VIOLATION_REPLAY_GAP,
    INTEGRITY_VIOLATION_ROLLBACK_GAP,
    INTEGRITY_VIOLATION_SCORING_LEAK,
    INTEGRITY_VIOLATION_SELECTION_LEAK,
    INTEGRITY_VIOLATION_TYPES,
    INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP,
    INTEGRITY_VISIBILITY_CAPABILITY_LEAKAGE,
    INTEGRITY_VISIBILITY_CATEGORIES,
    INTEGRITY_VISIBILITY_EXPLAINABILITY,
    INTEGRITY_VISIBILITY_FAIL_VISIBLE,
    INTEGRITY_VISIBILITY_GOVERNANCE,
    INTEGRITY_VISIBILITY_HIDDEN_BEHAVIOR,
    INTEGRITY_VISIBILITY_INTEGRITY,
    INTEGRITY_VISIBILITY_MISSING_EVIDENCE,
    INTEGRITY_VISIBILITY_MUTATION,
    INTEGRITY_VISIBILITY_PROHIBITED,
    INTEGRITY_VISIBILITY_PROVENANCE,
    INTEGRITY_VISIBILITY_RECOMMENDATION_SELECTION,
    INTEGRITY_VISIBILITY_REPLAY,
    INTEGRITY_VISIBILITY_ROLLBACK,
    INTEGRITY_VISIBILITY_UNKNOWN,
    INTEGRITY_VISIBILITY_UNSUPPORTED,
    PROHIBITED_INTEGRITY_CAPABILITIES,
    REQUIRED_INTEGRITY_DOMAINS,
    SUPPORTED_INTEGRITY_CAPABILITIES,
    TransitionIntegrityContinuity,
    TransitionIntegrityEvidence,
    TransitionIntegrityFinding,
    TransitionIntegrityInput,
    TransitionIntegrityReport,
    TransitionIntegritySummary,
    TransitionIntegrityViolation,
    TransitionIntegrityVisibility,
    V3_9_TRANSITION_INTEGRITY_REPORT_BLOCKED,
    V3_9_TRANSITION_INTEGRITY_REPORT_STABLE,
    transition_integrity_finding_id,
    transition_integrity_violation_id,
)
from .transition_integrity_serialization import (
    hash_transition_integrity_report,
    hash_transition_integrity_summary,
)
from .transition_integrity_validation import validate_transition_integrity_report


def default_transition_integrity_inputs(
    aggregation_report: TransitionAggregationReport | None = None,
) -> tuple[TransitionIntegrityInput, ...]:
    source = aggregation_report or build_v3_9_transition_aggregation()
    provenance_ids = tuple(record.provenance_id for record in source.provenance_records)
    replay_ids = tuple(record.continuity_id for record in source.continuities)
    rollback_ids = tuple(record.continuity_id for record in source.continuities)
    provenance_continuity_ids = tuple(record.continuity_id for record in source.continuities)
    explainability_ids = tuple(record.continuity_id for record in source.continuities)
    evidence_ids = (
        source.source_foundation_id,
        source.source_boundary_report_id,
        source.source_compatibility_report_id,
        source.source_evaluation_report_id,
        source.source_session_report_id,
        source.source_scenario_report_id,
        source.report_id,
        source.deterministic_aggregation_hash,
    )
    base = {
        "audit_domain": "coordination_transition_integrity_enforcement",
        "required_domain_ids": REQUIRED_INTEGRITY_DOMAINS,
        "present_domain_ids": REQUIRED_INTEGRITY_DOMAINS,
        "evidence_ids": evidence_ids,
        "provenance_reference_ids": provenance_ids,
        "replay_continuity_ids": replay_ids,
        "rollback_continuity_ids": rollback_ids,
        "provenance_continuity_ids": provenance_continuity_ids,
        "explainability_continuity_ids": explainability_ids,
        "aggregation_report_id": source.report_id,
        "aggregation_hash": source.deterministic_aggregation_hash,
    }
    return (
        TransitionIntegrityInput(
            input_id="integrity_satisfied_transition_chain",
            audit_id="v3_9_integrity_satisfied_transition_chain",
            requested_capabilities=("deterministic_transition_integrity_audit",),
            explainability_context="all required transition intelligence evidence is present and no unresolved violations exist",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="integrity_warning_transition_chain",
            audit_id="v3_9_integrity_warning_transition_chain",
            warning_markers=(
                "expected_fail_visible_unsupported_states",
                "expected_fail_visible_prohibited_states",
                "expected_descriptive_scenario_risks",
            ),
            requested_capabilities=("deterministic_transition_integrity_audit",),
            explainability_context="warnings are fail-visible and deterministic guarantees remain preserved",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="integrity_failed_transition_chain",
            audit_id="v3_9_integrity_failed_transition_chain",
            violation_markers=INTEGRITY_VIOLATION_TYPES,
            requested_capabilities=("deterministic_transition_integrity_audit",),
            explainability_context="integrity violations are explicitly visible and not repaired",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="blocked_transition_integrity_audit",
            audit_id="v3_9_blocked_transition_integrity_audit",
            blocked_markers=("blocked_by_execution_boundary_preservation",),
            governance_policy_ids=("governance_policy_blocks_integrity_certification",),
            integrity_policy_ids=("integrity_preconditions_failed",),
            requested_capabilities=("deterministic_transition_integrity_audit",),
            explainability_context="governance and integrity preconditions block certification",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="unsupported_transition_integrity_audit",
            audit_id="v3_9_unsupported_transition_integrity_audit",
            unsupported_markers=("unsupported_domain:cross_domain_integrity_certification",),
            requested_capabilities=("cross_domain_transition_integrity_certification",),
            explainability_context="integrity audit domain is outside supported deterministic scope",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="prohibited_transition_integrity_audit",
            audit_id="v3_9_prohibited_transition_integrity_audit",
            prohibited_markers=("prohibited_integrity_repair_request",),
            requested_capabilities=(
                "orchestration_execution",
                "routing",
                "runtime_mutation",
                "automatic_remediation",
                "repair",
                "recommendation",
                "ranking",
                "scoring",
                "selection",
            ),
            explainability_context="integrity audit request attempts to introduce prohibited behavior",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="unknown_transition_integrity_audit",
            audit_id="v3_9_unknown_transition_integrity_audit",
            unknown_markers=("ambiguous_integrity_audit_semantics",),
            requested_capabilities=("deterministic_transition_integrity_audit",),
            explainability_context="audit semantics cannot be deterministically interpreted",
            **base,
        ),
        TransitionIntegrityInput(
            input_id="incomplete_transition_integrity_audit",
            audit_id="",
            audit_domain="coordination_transition_integrity_enforcement",
            required_domain_ids=REQUIRED_INTEGRITY_DOMAINS,
            present_domain_ids=(),
            evidence_ids=(),
            provenance_reference_ids=(),
            replay_continuity_ids=(),
            rollback_continuity_ids=(),
            provenance_continuity_ids=(),
            explainability_continuity_ids=(),
            aggregation_report_id="",
            aggregation_hash="",
            incomplete_markers=(
                "missing_required_intelligence_domains",
                "missing_required_audit_evidence",
                "missing_provenance_evidence",
                "missing_continuity_evidence",
                "missing_explainability_evidence",
            ),
            requested_capabilities=("deterministic_transition_integrity_audit",),
            explainability_context="required integrity audit evidence is missing",
        ),
    )


def audit_v3_9_transition_integrity(
    integrity_inputs: Iterable[TransitionIntegrityInput] | None = None,
    aggregation_report: TransitionAggregationReport | None = None,
) -> TransitionIntegrityReport:
    source = aggregation_report or build_v3_9_transition_aggregation()
    inputs = tuple(sorted(tuple(integrity_inputs or default_transition_integrity_inputs(source)), key=lambda item: item.input_id))
    findings: list[TransitionIntegrityFinding] = []
    violations: list[TransitionIntegrityViolation] = []
    evidence_records: list[TransitionIntegrityEvidence] = []
    continuities: list[TransitionIntegrityContinuity] = []
    visibilities: list[TransitionIntegrityVisibility] = []
    for index, integrity_input in enumerate(inputs, start=1):
        classification, reason = _classify_input(integrity_input)
        continuity = _continuity_from_input(integrity_input)
        input_violations = _violations_from_input(
            integrity_input,
            classification,
            evidence_reference=f"v3_9_integrity_evidence_{integrity_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 100000,
        )
        input_findings = _findings_from_input(
            integrity_input,
            classification,
            reason,
            input_violations,
            evidence_reference=f"v3_9_integrity_evidence_{integrity_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 10000,
        )
        input_visibilities = _visibilities_from_input(
            integrity_input,
            classification,
            reason,
            input_violations,
            evidence_reference=f"v3_9_integrity_evidence_{integrity_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 1000,
        )
        evidence = _evidence_from_input(
            integrity_input,
            input_findings,
            input_violations,
            input_visibilities,
            continuity,
        )
        findings.extend(input_findings)
        violations.extend(input_violations)
        evidence_records.append(evidence)
        continuities.append(continuity)
        visibilities.extend(input_visibilities)
    summary = _summary_from_outputs(inputs, tuple(findings), tuple(violations), tuple(visibilities))
    summary = replace(summary, deterministic_summary_hash=hash_transition_integrity_summary(summary))
    base_report = TransitionIntegrityReport(
        report_id="v3_9_transition_integrity_enforcement_report",
        report_status=V3_9_TRANSITION_INTEGRITY_REPORT_STABLE,
        source_aggregation_report_id=source.report_id,
        source_aggregation_hash=source.deterministic_aggregation_hash,
        integrity_inputs=inputs,
        findings=tuple(sorted(findings, key=lambda item: (item.deterministic_order, item.finding_id))),
        violations=tuple(sorted(violations, key=lambda item: (item.deterministic_order, item.violation_id))),
        evidence_records=tuple(evidence_records),
        continuities=tuple(continuities),
        visibilities=tuple(sorted(visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_integrity_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_INTEGRITY_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_INTEGRITY_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_integrity_hash=hash_transition_integrity_report(report))


def _classify_input(source: TransitionIntegrityInput) -> tuple[str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_INTEGRITY_CAPABILITIES
    )
    if source.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_markers, *prohibited_capabilities)))
        return (
            INTEGRITY_CLASSIFICATION_PROHIBITED,
            "prohibited integrity audit behavior requested: " + ", ".join(markers),
        )
    missing_markers = _missing_required_markers(source)
    if source.incomplete_markers or missing_markers:
        markers = tuple(sorted(set((*source.incomplete_markers, *missing_markers))))
        return (
            INTEGRITY_CLASSIFICATION_INCOMPLETE,
            "required transition integrity evidence is incomplete: " + ", ".join(markers),
        )
    blocked_markers = tuple(sorted((*source.blocked_markers, *source.governance_policy_ids, *source.integrity_policy_ids)))
    if blocked_markers:
        return (
            INTEGRITY_CLASSIFICATION_BLOCKED,
            "transition integrity audit is blocked by governance or integrity policy: " + ", ".join(blocked_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_INTEGRITY_CAPABILITIES
        and capability not in PROHIBITED_INTEGRITY_CAPABILITIES
    )
    if source.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_markers, *unsupported_capabilities)))
        return (
            INTEGRITY_CLASSIFICATION_UNSUPPORTED,
            "transition integrity audit domain is unsupported: " + ", ".join(markers),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_integrity_audit_semantics",)))
        return (
            INTEGRITY_CLASSIFICATION_UNKNOWN,
            "transition integrity audit cannot be deterministically interpreted: " + ", ".join(markers),
        )
    if source.violation_markers:
        return (
            INTEGRITY_CLASSIFICATION_FAILED,
            "transition integrity violations are explicitly visible: " + ", ".join(sorted(source.violation_markers)),
        )
    if source.warning_markers:
        return (
            INTEGRITY_CLASSIFICATION_WARNING,
            "transition integrity warnings remain fail-visible: " + ", ".join(sorted(source.warning_markers)),
        )
    return (
        INTEGRITY_CLASSIFICATION_SATISFIED,
        "transition integrity is satisfied for deterministic audit evidence only",
    )


def _findings_from_input(
    source: TransitionIntegrityInput,
    classification: str,
    reason: str,
    violations: tuple[TransitionIntegrityViolation, ...],
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionIntegrityFinding, ...]:
    specs: list[tuple[str, str, str]] = []
    if classification == INTEGRITY_CLASSIFICATION_SATISFIED:
        specs.extend(
            (
                (INTEGRITY_FINDING_FOUNDATION, "foundation_integrity_satisfied", "foundation integrity satisfied"),
                (INTEGRITY_FINDING_BOUNDARY, "boundary_integrity_satisfied", "boundary integrity satisfied"),
                (INTEGRITY_FINDING_COMPATIBILITY, "compatibility_integrity_satisfied", "compatibility integrity satisfied"),
                (INTEGRITY_FINDING_EVALUATION, "evaluation_integrity_satisfied", "evaluation integrity satisfied"),
                (INTEGRITY_FINDING_SESSION, "session_integrity_satisfied", "session integrity satisfied"),
                (INTEGRITY_FINDING_SCENARIO, "scenario_integrity_satisfied", "scenario integrity satisfied"),
                (INTEGRITY_FINDING_AGGREGATION, "aggregation_integrity_satisfied", "aggregation integrity satisfied"),
                (INTEGRITY_FINDING_PROVENANCE, "provenance_continuity_satisfied", "provenance continuity preserved"),
                (INTEGRITY_FINDING_REPLAY, "replay_continuity_satisfied", "replay continuity preserved"),
                (INTEGRITY_FINDING_ROLLBACK, "rollback_continuity_satisfied", "rollback continuity preserved"),
                (INTEGRITY_FINDING_EXPLAINABILITY, "explainability_continuity_satisfied", "explainability continuity preserved"),
                (INTEGRITY_FINDING_FAIL_VISIBLE, "fail_visible_integrity_satisfied", "fail-visible finding integrity satisfied"),
                (INTEGRITY_FINDING_RISK_VISIBILITY, "risk_visibility_integrity_satisfied", "risk visibility integrity satisfied"),
            )
        )
    for marker in source.warning_markers:
        specs.append((INTEGRITY_FINDING_FAIL_VISIBLE, marker, "fail-visible warning marker"))
    for marker in source.blocked_markers:
        specs.append((INTEGRITY_FINDING_GOVERNANCE, marker, "blocked integrity audit marker"))
    for marker in source.governance_policy_ids:
        specs.append((INTEGRITY_FINDING_GOVERNANCE, marker, "governance integrity finding"))
    for marker in source.integrity_policy_ids:
        specs.append((INTEGRITY_FINDING_INTEGRITY_PRECONDITION, marker, "integrity precondition finding"))
    for marker in source.unsupported_markers:
        specs.append((INTEGRITY_FINDING_UNSUPPORTED, marker, "unsupported integrity finding"))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_INTEGRITY_CAPABILITIES and capability not in PROHIBITED_INTEGRITY_CAPABILITIES:
            specs.append((INTEGRITY_FINDING_UNSUPPORTED, capability, "unsupported integrity capability"))
    for marker in source.prohibited_markers:
        specs.append((INTEGRITY_FINDING_PROHIBITED, marker, "prohibited integrity finding"))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_INTEGRITY_CAPABILITIES:
            specs.append((INTEGRITY_FINDING_CAPABILITY_LEAKAGE, capability, "prohibited capability leakage finding"))
    for marker in source.unknown_markers:
        specs.append((INTEGRITY_FINDING_UNCERTAINTY, marker, "uncertain integrity finding"))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        specs.append((INTEGRITY_FINDING_MISSING_EVIDENCE, marker, "missing integrity evidence finding"))
    for violation in violations:
        specs.append((_finding_category_for_violation(violation.violation_type), violation.violation_type, "integrity violation finding"))
    if not specs:
        specs.append((INTEGRITY_FINDING_FAIL_VISIBLE, classification, reason))
    specs = tuple({(category, marker): (category, marker, message) for category, marker, message in specs}.values())
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    findings: list[TransitionIntegrityFinding] = []
    for offset, (category, marker, message) in enumerate(
        sorted(specs, key=lambda item: (_finding_category_order(item[0]), item[1])),
        start=1,
    ):
        findings.append(
            TransitionIntegrityFinding(
                finding_id=transition_integrity_finding_id(source.input_id, category, marker),
                input_id=source.input_id,
                finding_category=category,
                classification=classification,
                reason=f"{message}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition integrity finding for {source.input_id}: "
                    f"{message}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
            )
        )
    return tuple(findings)


def _violations_from_input(
    source: TransitionIntegrityInput,
    classification: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionIntegrityViolation, ...]:
    violation_types = set(source.violation_markers)
    violation_types.update(_missing_required_violation_types(source))
    for capability in source.requested_capabilities:
        violation_types.update(_violation_types_for_capability(capability))
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    violations: list[TransitionIntegrityViolation] = []
    for offset, violation_type in enumerate(sorted(violation_types, key=_violation_type_order), start=1):
        violations.append(
            TransitionIntegrityViolation(
                violation_id=transition_integrity_violation_id(source.input_id, violation_type),
                input_id=source.input_id,
                violation_type=violation_type,
                classification=classification,
                reason=f"{violation_type} detected as explicit integrity audit evidence",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{violation_type} remains visible for {source.input_id}; "
                    "the audit does not repair or approve the transition chain"
                ),
                deterministic_order=deterministic_order_base + offset,
            )
        )
    return tuple(violations)


def _visibilities_from_input(
    source: TransitionIntegrityInput,
    classification: str,
    reason: str,
    violations: tuple[TransitionIntegrityViolation, ...],
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionIntegrityVisibility, ...]:
    categories = {INTEGRITY_VISIBILITY_FAIL_VISIBLE}
    violation_types = {violation.violation_type for violation in violations}
    if violation_types.intersection(
        {
            INTEGRITY_VIOLATION_HIDDEN_FINDING,
            INTEGRITY_VIOLATION_HIDDEN_RISK,
            INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE,
        }
    ):
        categories.add(INTEGRITY_VISIBILITY_HIDDEN_BEHAVIOR)
    if INTEGRITY_VIOLATION_PROVENANCE_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_PROVENANCE)
    if INTEGRITY_VIOLATION_REPLAY_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_REPLAY)
    if INTEGRITY_VIOLATION_ROLLBACK_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_ROLLBACK)
    if INTEGRITY_VIOLATION_EXPLAINABILITY_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_EXPLAINABILITY)
    if INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK in violation_types:
        categories.add(INTEGRITY_VISIBILITY_CAPABILITY_LEAKAGE)
    if violation_types.intersection(
        {
            INTEGRITY_VIOLATION_RECOMMENDATION_LEAK,
            INTEGRITY_VIOLATION_RANKING_LEAK,
            INTEGRITY_VIOLATION_SCORING_LEAK,
            INTEGRITY_VIOLATION_SELECTION_LEAK,
        }
    ):
        categories.add(INTEGRITY_VISIBILITY_RECOMMENDATION_SELECTION)
    if INTEGRITY_VIOLATION_MUTATION_LEAK in violation_types:
        categories.add(INTEGRITY_VISIBILITY_MUTATION)
    if any(violation_type.startswith("missing_") for violation_type in violation_types):
        categories.add(INTEGRITY_VISIBILITY_MISSING_EVIDENCE)
    if source.unsupported_markers or INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_UNSUPPORTED)
    if source.prohibited_markers or INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_PROHIBITED)
    if source.unknown_markers or INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_UNKNOWN)
    if source.blocked_markers or source.governance_policy_ids:
        categories.add(INTEGRITY_VISIBILITY_GOVERNANCE)
    if source.integrity_policy_ids or INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP in violation_types:
        categories.add(INTEGRITY_VISIBILITY_INTEGRITY)
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    visibilities: list[TransitionIntegrityVisibility] = []
    for offset, category in enumerate(sorted(categories, key=_visibility_category_order), start=1):
        visibilities.append(
            TransitionIntegrityVisibility(
                visibility_id=f"v3_9_integrity_visibility_{source.input_id}_{category}",
                input_id=source.input_id,
                visibility_category=category,
                classification=classification,
                reason=f"{category} integrity visibility: {reason}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition integrity visibility for {source.input_id}: "
                    f"{category}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
            )
        )
    return tuple(visibilities)


def _continuity_from_input(source: TransitionIntegrityInput) -> TransitionIntegrityContinuity:
    return TransitionIntegrityContinuity(
        continuity_id=f"v3_9_integrity_continuity_{source.input_id}",
        input_id=source.input_id,
        replay_continuity_ids=_references_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        rollback_continuity_ids=_references_or_missing(source.rollback_continuity_ids, "missing_rollback_continuity_fail_visible"),
        provenance_continuity_ids=_references_or_missing(source.provenance_continuity_ids, "missing_provenance_continuity_fail_visible"),
        explainability_continuity_ids=_references_or_missing(source.explainability_continuity_ids, "missing_explainability_continuity_fail_visible"),
        evidence_continuity_ids=_references_or_missing(source.evidence_ids, "missing_integrity_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_integrity_hash",
    )


def _evidence_from_input(
    source: TransitionIntegrityInput,
    findings: tuple[TransitionIntegrityFinding, ...],
    violations: tuple[TransitionIntegrityViolation, ...],
    visibilities: tuple[TransitionIntegrityVisibility, ...],
    continuity: TransitionIntegrityContinuity,
) -> TransitionIntegrityEvidence:
    continuity_ids = (
        *continuity.replay_continuity_ids,
        *continuity.rollback_continuity_ids,
        *continuity.provenance_continuity_ids,
        *continuity.explainability_continuity_ids,
        *continuity.evidence_continuity_ids,
    )
    return TransitionIntegrityEvidence(
        evidence_id=f"v3_9_integrity_evidence_{source.input_id}",
        input_id=source.input_id,
        audit_id=source.audit_id or "missing_integrity_audit_identity_fail_visible",
        source_domain_ids=_references_or_missing(source.present_domain_ids, "missing_source_domain_fail_visible"),
        evidence_ids=_references_or_missing(source.evidence_ids, "missing_integrity_evidence_fail_visible"),
        finding_ids=tuple(finding.finding_id for finding in findings),
        violation_ids=tuple(violation.violation_id for violation in violations),
        visibility_ids=tuple(visibility.visibility_id for visibility in visibilities),
        provenance_reference_ids=_references_or_missing(
            source.provenance_reference_ids,
            "missing_provenance_reference_fail_visible",
        ),
        continuity_reference_ids=continuity_ids,
        deterministic_hash_reference="v3_9_transition_integrity_hash",
    )


def _summary_from_outputs(
    inputs: tuple[TransitionIntegrityInput, ...],
    findings: tuple[TransitionIntegrityFinding, ...],
    violations: tuple[TransitionIntegrityViolation, ...],
    visibilities: tuple[TransitionIntegrityVisibility, ...],
) -> TransitionIntegritySummary:
    classification_counts = Counter(_first_classification_for_input(findings, source.input_id) for source in inputs)
    finding_counts = Counter(finding.finding_category for finding in findings)
    violation_counts = Counter(violation.violation_type for violation in violations)
    visibility_counts = Counter(visibility.visibility_category for visibility in visibilities)
    counts = {classification: classification_counts.get(classification, 0) for classification in INTEGRITY_CLASSIFICATIONS}
    finding_categories = {category: finding_counts.get(category, 0) for category in INTEGRITY_FINDING_CATEGORIES}
    violation_types = {violation_type: violation_counts.get(violation_type, 0) for violation_type in INTEGRITY_VIOLATION_TYPES}
    visibility_categories = {category: visibility_counts.get(category, 0) for category in INTEGRITY_VISIBILITY_CATEGORIES}
    missing_evidence_count = sum(
        count
        for violation_type, count in violation_types.items()
        if violation_type.startswith("missing_") and violation_type.endswith("_evidence")
    ) + violation_types[INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP]
    visibility_gap_count = (
        violation_types[INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP]
        + violation_types[INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP]
        + violation_types[INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP]
    )
    return TransitionIntegritySummary(
        summary_id="v3_9_transition_integrity_summary",
        classification_counts=counts,
        finding_category_counts=finding_categories,
        violation_type_counts=violation_types,
        visibility_category_counts=visibility_categories,
        integrity_satisfied_count=counts[INTEGRITY_CLASSIFICATION_SATISFIED],
        integrity_warning_count=counts[INTEGRITY_CLASSIFICATION_WARNING],
        integrity_failed_count=counts[INTEGRITY_CLASSIFICATION_FAILED],
        blocked_count=counts[INTEGRITY_CLASSIFICATION_BLOCKED],
        unsupported_count=counts[INTEGRITY_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[INTEGRITY_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[INTEGRITY_CLASSIFICATION_UNKNOWN],
        incomplete_count=counts[INTEGRITY_CLASSIFICATION_INCOMPLETE],
        integrity_finding_count=len(findings),
        integrity_violation_count=len(violations),
        hidden_finding_violation_count=violation_types[INTEGRITY_VIOLATION_HIDDEN_FINDING],
        hidden_risk_violation_count=violation_types[INTEGRITY_VIOLATION_HIDDEN_RISK],
        hidden_non_safe_state_violation_count=violation_types[INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE],
        missing_evidence_violation_count=missing_evidence_count,
        provenance_gap_count=violation_types[INTEGRITY_VIOLATION_PROVENANCE_GAP],
        replay_gap_count=violation_types[INTEGRITY_VIOLATION_REPLAY_GAP],
        rollback_gap_count=violation_types[INTEGRITY_VIOLATION_ROLLBACK_GAP],
        explainability_gap_count=violation_types[INTEGRITY_VIOLATION_EXPLAINABILITY_GAP],
        aggregation_integrity_gap_count=violation_types[INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP],
        execution_boundary_leakage_count=violation_types[INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK],
        recommendation_leakage_count=violation_types[INTEGRITY_VIOLATION_RECOMMENDATION_LEAK],
        ranking_leakage_count=violation_types[INTEGRITY_VIOLATION_RANKING_LEAK],
        scoring_leakage_count=violation_types[INTEGRITY_VIOLATION_SCORING_LEAK],
        selection_leakage_count=violation_types[INTEGRITY_VIOLATION_SELECTION_LEAK],
        mutation_leakage_count=violation_types[INTEGRITY_VIOLATION_MUTATION_LEAK],
        visibility_gap_count=visibility_gap_count,
    )


def _missing_required_markers(source: TransitionIntegrityInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.audit_id:
        markers.append("missing_integrity_audit_identity")
    missing_domains = tuple(sorted(set(source.required_domain_ids) - set(source.present_domain_ids)))
    for domain in missing_domains:
        markers.append(f"missing_domain:{domain}")
    if not source.evidence_ids:
        markers.append("missing_required_audit_evidence")
    if not source.aggregation_report_id or not source.aggregation_hash:
        markers.append("missing_aggregation_evidence")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.replay_continuity_ids:
        markers.append("missing_replay_continuity")
    if not source.rollback_continuity_ids:
        markers.append("missing_rollback_continuity")
    if not source.explainability_continuity_ids:
        markers.append("missing_explainability_evidence")
    return tuple(sorted(set(markers)))


def _missing_required_violation_types(source: TransitionIntegrityInput) -> tuple[str, ...]:
    violation_types: list[str] = []
    missing_domains = set(source.required_domain_ids) - set(source.present_domain_ids)
    domain_violation_map = {
        REQUIRED_AGGREGATION_DOMAINS[0]: INTEGRITY_VIOLATION_MISSING_FOUNDATION_EVIDENCE,
        REQUIRED_AGGREGATION_DOMAINS[1]: INTEGRITY_VIOLATION_MISSING_BOUNDARY_EVIDENCE,
        REQUIRED_AGGREGATION_DOMAINS[2]: INTEGRITY_VIOLATION_MISSING_COMPATIBILITY_EVIDENCE,
        REQUIRED_AGGREGATION_DOMAINS[3]: INTEGRITY_VIOLATION_MISSING_EVALUATION_EVIDENCE,
        REQUIRED_AGGREGATION_DOMAINS[4]: INTEGRITY_VIOLATION_MISSING_SESSION_EVIDENCE,
        REQUIRED_AGGREGATION_DOMAINS[5]: INTEGRITY_VIOLATION_MISSING_SCENARIO_EVIDENCE,
        "aggregation_intelligence": INTEGRITY_VIOLATION_MISSING_AGGREGATION_EVIDENCE,
    }
    for domain in missing_domains:
        violation_types.append(domain_violation_map.get(domain, INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP))
    if not source.evidence_ids:
        violation_types.append(INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP)
    if not source.aggregation_report_id or not source.aggregation_hash:
        violation_types.append(INTEGRITY_VIOLATION_MISSING_AGGREGATION_EVIDENCE)
    if not source.provenance_reference_ids:
        violation_types.append(INTEGRITY_VIOLATION_PROVENANCE_GAP)
    if not source.replay_continuity_ids:
        violation_types.append(INTEGRITY_VIOLATION_REPLAY_GAP)
    if not source.rollback_continuity_ids:
        violation_types.append(INTEGRITY_VIOLATION_ROLLBACK_GAP)
    if not source.explainability_continuity_ids:
        violation_types.append(INTEGRITY_VIOLATION_EXPLAINABILITY_GAP)
    return tuple(sorted(set(violation_types), key=_violation_type_order))


def _violation_types_for_capability(capability: str) -> tuple[str, ...]:
    if capability not in PROHIBITED_INTEGRITY_CAPABILITIES:
        return ()
    if capability == "runtime_mutation":
        return (INTEGRITY_VIOLATION_MUTATION_LEAK,)
    if capability == "recommendation":
        return (INTEGRITY_VIOLATION_RECOMMENDATION_LEAK,)
    if capability == "ranking":
        return (INTEGRITY_VIOLATION_RANKING_LEAK,)
    if capability == "scoring":
        return (INTEGRITY_VIOLATION_SCORING_LEAK,)
    if capability == "selection":
        return (INTEGRITY_VIOLATION_SELECTION_LEAK,)
    return (INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK,)


def _finding_category_for_violation(violation_type: str) -> str:
    mapping = {
        INTEGRITY_VIOLATION_HIDDEN_FINDING: INTEGRITY_FINDING_HIDDEN_FINDING,
        INTEGRITY_VIOLATION_HIDDEN_RISK: INTEGRITY_FINDING_HIDDEN_RISK,
        INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE: INTEGRITY_FINDING_HIDDEN_NON_SAFE,
        INTEGRITY_VIOLATION_PROVENANCE_GAP: INTEGRITY_FINDING_PROVENANCE,
        INTEGRITY_VIOLATION_REPLAY_GAP: INTEGRITY_FINDING_REPLAY,
        INTEGRITY_VIOLATION_ROLLBACK_GAP: INTEGRITY_FINDING_ROLLBACK,
        INTEGRITY_VIOLATION_EXPLAINABILITY_GAP: INTEGRITY_FINDING_EXPLAINABILITY,
        INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP: INTEGRITY_FINDING_AGGREGATION,
        INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK: INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
        INTEGRITY_VIOLATION_RECOMMENDATION_LEAK: INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
        INTEGRITY_VIOLATION_RANKING_LEAK: INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
        INTEGRITY_VIOLATION_SCORING_LEAK: INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
        INTEGRITY_VIOLATION_SELECTION_LEAK: INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
        INTEGRITY_VIOLATION_MUTATION_LEAK: INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
        INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP: INTEGRITY_FINDING_VISIBILITY_GAP,
        INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP: INTEGRITY_FINDING_VISIBILITY_GAP,
        INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP: INTEGRITY_FINDING_VISIBILITY_GAP,
    }
    if violation_type.startswith("missing_"):
        return INTEGRITY_FINDING_MISSING_EVIDENCE
    return mapping.get(violation_type, INTEGRITY_FINDING_INTEGRITY_PRECONDITION)


def _first_classification_for_input(findings: tuple[TransitionIntegrityFinding, ...], input_id: str) -> str:
    for finding in findings:
        if finding.input_id == input_id:
            return finding.classification
    return INTEGRITY_CLASSIFICATION_UNKNOWN


def _semantics_are_unknown(source: TransitionIntegrityInput) -> bool:
    values = (source.audit_id, source.audit_domain)
    return any("unknown" in value.strip().lower() or "ambiguous" in value.strip().lower() for value in values)


def _reference_or_missing(values: tuple[str, ...], missing_reference: str) -> str:
    if values:
        return sorted(values)[0]
    return missing_reference


def _references_or_missing(values: tuple[str, ...], missing_reference: str) -> tuple[str, ...]:
    if values:
        return tuple(sorted(values))
    return (missing_reference,)


def _finding_category_order(category: str) -> int:
    try:
        return INTEGRITY_FINDING_CATEGORIES.index(category)
    except ValueError:
        return len(INTEGRITY_FINDING_CATEGORIES)


def _violation_type_order(violation_type: str) -> int:
    try:
        return INTEGRITY_VIOLATION_TYPES.index(violation_type)
    except ValueError:
        return len(INTEGRITY_VIOLATION_TYPES)


def _visibility_category_order(category: str) -> int:
    try:
        return INTEGRITY_VISIBILITY_CATEGORIES.index(category)
    except ValueError:
        return len(INTEGRITY_VISIBILITY_CATEGORIES)
