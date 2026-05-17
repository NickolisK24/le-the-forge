"""Deterministic v3.9 transition boundary classification logic."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_boundary_models import (
    BOUNDARY_CLASSIFICATION_BLOCKED,
    BOUNDARY_CLASSIFICATION_INCOMPLETE,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SAFE,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_CLASSIFICATIONS,
    BOUNDARY_SEVERITY_BLOCKED,
    BOUNDARY_SEVERITY_INFO,
    BOUNDARY_SEVERITY_WARNING,
    BOUNDARY_VISIBILITY_FAIL_VISIBLE,
    BOUNDARY_VISIBILITY_VISIBLE,
    PROHIBITED_BOUNDARY_CAPABILITIES,
    SUPPORTED_BOUNDARY_CAPABILITIES,
    TransitionBoundaryClassification,
    TransitionBoundaryEvidence,
    TransitionBoundaryFinding,
    TransitionBoundaryInput,
    TransitionBoundaryReport,
    V3_9_TRANSITION_BOUNDARY_REPORT_BLOCKED,
    V3_9_TRANSITION_BOUNDARY_REPORT_STABLE,
    transition_boundary_finding_id,
)
from .transition_boundary_serialization import hash_transition_boundary_report
from .transition_boundary_validation import validate_transition_boundary_report
from .transition_foundation_models import TransitionFoundation, default_v3_9_transition_foundation


def default_transition_boundary_inputs(
    foundation: TransitionFoundation | None = None,
) -> tuple[TransitionBoundaryInput, ...]:
    source = foundation or default_v3_9_transition_foundation()
    transition_id = source.identity.transition_id
    provenance_ids = tuple(reference.provenance_reference_id for reference in source.provenance_references)
    continuity_ids = tuple(reference.continuity_reference_id for reference in source.continuity_references)
    evidence_ids = tuple(record.evidence_record_id for record in source.evidence_records)
    base = {
        "source_state_id": "v3_8_coordination_closeout_ready_for_v3_9",
        "destination_state_id": "v3_9_transition_boundary_intelligence",
        "transition_identity_id": transition_id,
        "transition_domain": "coordination_transition_boundary",
        "transition_intent": "deterministic_boundary_classification",
        "provenance_reference_ids": provenance_ids,
        "continuity_reference_ids": continuity_ids,
        "evidence_reference_ids": evidence_ids,
    }
    return (
        TransitionBoundaryInput(
            input_id="safe_transition_boundary",
            **base,
            requested_capabilities=("deterministic_boundary_classification",),
            explainability_context="all transition boundary prerequisites are present",
        ),
        TransitionBoundaryInput(
            input_id="unsupported_transition_boundary",
            **base,
            requested_capabilities=("cross_domain_transition_prediction",),
            unsupported_markers=("unsupported_domain:cross_domain_transition_prediction",),
            explainability_context="requested transition capability is outside modeled support",
        ),
        TransitionBoundaryInput(
            input_id="prohibited_transition_boundary",
            **base,
            requested_capabilities=("orchestration_execution", "routing", "runtime_mutation"),
            prohibited_markers=("prohibited_execution_request",),
            explainability_context="requested behavior would violate non-execution guarantees",
        ),
        TransitionBoundaryInput(
            input_id="unknown_transition_boundary",
            **base,
            requested_capabilities=("deterministic_boundary_classification",),
            unknown_markers=("ambiguous_transition_intent",),
            explainability_context="transition intent cannot be deterministically interpreted",
        ),
        TransitionBoundaryInput(
            input_id="incomplete_transition_boundary",
            source_state_id="",
            destination_state_id="v3_9_transition_boundary_intelligence",
            transition_identity_id=transition_id,
            transition_domain="coordination_transition_boundary",
            transition_intent="deterministic_boundary_classification",
            provenance_reference_ids=(),
            continuity_reference_ids=continuity_ids,
            evidence_reference_ids=(),
            requested_capabilities=("deterministic_boundary_classification",),
            incomplete_markers=("missing_source_state", "missing_provenance_reference", "missing_evidence_reference"),
            explainability_context="required source state and evidence references are missing",
        ),
        TransitionBoundaryInput(
            input_id="blocked_transition_boundary",
            **base,
            requested_capabilities=("deterministic_boundary_classification",),
            blocked_markers=("blocked_by_governance",),
            governance_blockers=("non_execution_governance_hold",),
            boundary_policy_violation_ids=("boundary_policy:requires_manual_review",),
            integrity_precondition_failures=("integrity_precondition:non_execution_confirmation_required",),
            explainability_context="governance and integrity preconditions block this transition",
        ),
    )


def classify_v3_9_transition_boundaries(
    boundary_inputs: Iterable[TransitionBoundaryInput] | None = None,
    foundation: TransitionFoundation | None = None,
) -> TransitionBoundaryReport:
    source = foundation or default_v3_9_transition_foundation()
    inputs = tuple(sorted(tuple(boundary_inputs or default_transition_boundary_inputs(source)), key=lambda item: item.input_id))
    findings = tuple(
        _finding_from_input(boundary_input, deterministic_order=index)
        for index, boundary_input in enumerate(sorted(inputs, key=lambda item: item.input_id), start=1)
    )
    classifications = tuple(_classification_from_finding(finding) for finding in findings)
    counts = _count_classifications(findings)
    base_report = TransitionBoundaryReport(
        boundary_report_id="v3_9_transition_boundary_intelligence_report",
        report_status=V3_9_TRANSITION_BOUNDARY_REPORT_STABLE,
        source_foundation_id=source.identity.transition_id,
        boundary_inputs=inputs,
        classifications=classifications,
        findings=findings,
        classification_counts=counts,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_boundary_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_BOUNDARY_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_BOUNDARY_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_boundary_hash=hash_transition_boundary_report(report))


def _finding_from_input(
    boundary_input: TransitionBoundaryInput,
    deterministic_order: int,
) -> TransitionBoundaryFinding:
    classification, severity, visibility, reason, markers = _classify_input(boundary_input)
    evidence_reference = _evidence_reference(boundary_input)
    provenance_reference = _reference_or_missing(
        boundary_input.provenance_reference_ids,
        "missing_provenance_reference_fail_visible",
    )
    continuity_reference = _reference_or_missing(
        boundary_input.continuity_reference_ids,
        "missing_continuity_reference_fail_visible",
    )
    evidence = TransitionBoundaryEvidence(
        evidence_id=f"v3_9_boundary_evidence_{boundary_input.input_id}",
        input_id=boundary_input.input_id,
        source_state_id=boundary_input.source_state_id,
        destination_state_id=boundary_input.destination_state_id,
        transition_identity_id=boundary_input.transition_identity_id,
        evidence_reference_ids=(evidence_reference,),
        provenance_reference_ids=(provenance_reference,),
        continuity_reference_ids=(continuity_reference,),
        deterministic_hash_reference="v3_9_transition_boundary_hash",
    )
    non_safe = classification != BOUNDARY_CLASSIFICATION_SAFE
    requested_capabilities = tuple(sorted(boundary_input.requested_capabilities))
    execution_boundary_violation = any(
        capability in PROHIBITED_BOUNDARY_CAPABILITIES for capability in requested_capabilities
    )
    explainability_message = _explainability_message(boundary_input, classification, reason)
    return TransitionBoundaryFinding(
        finding_id=transition_boundary_finding_id(classification, boundary_input.input_id),
        input_id=boundary_input.input_id,
        classification=classification,
        severity=severity,
        reason=reason,
        deterministic_evidence_reference=evidence.evidence_id,
        provenance_reference=provenance_reference,
        continuity_reference=continuity_reference,
        explainability_message=explainability_message,
        evidence=evidence,
        marker_ids=markers,
        requested_capabilities=requested_capabilities,
        deterministic_order=deterministic_order,
        fail_visible=True,
        hidden=False,
        non_safe_state=non_safe,
        execution_boundary_violation_detected=execution_boundary_violation,
        non_execution_confirmation=True,
        replay_safe=evidence.replay_safe,
        rollback_safe=evidence.rollback_safe,
        provenance_preserved=evidence.provenance_preserved,
        explainability_safe=evidence.explainability_safe,
    )


def _classification_from_finding(finding: TransitionBoundaryFinding) -> TransitionBoundaryClassification:
    return TransitionBoundaryClassification(
        classification=finding.classification,
        severity=finding.severity,
        visibility_status=BOUNDARY_VISIBILITY_FAIL_VISIBLE
        if finding.non_safe_state
        else BOUNDARY_VISIBILITY_VISIBLE,
        reason=finding.reason,
        deterministic_evidence_reference=finding.deterministic_evidence_reference,
        provenance_reference=finding.provenance_reference,
        continuity_reference=finding.continuity_reference,
        explainability_message=finding.explainability_message,
        fail_visible=True,
        hidden=False,
    )


def _classify_input(
    boundary_input: TransitionBoundaryInput,
) -> tuple[str, str, str, str, tuple[str, ...]]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(boundary_input.requested_capabilities)
        if capability in PROHIBITED_BOUNDARY_CAPABILITIES
    )
    if boundary_input.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*boundary_input.prohibited_markers, *prohibited_capabilities)))
        return (
            BOUNDARY_CLASSIFICATION_PROHIBITED,
            BOUNDARY_SEVERITY_BLOCKED,
            BOUNDARY_VISIBILITY_FAIL_VISIBLE,
            "prohibited transition behavior requested: " + ", ".join(markers),
            markers,
        )
    missing_markers = tuple(
        sorted(set((*boundary_input.incomplete_markers, *_missing_required_markers(boundary_input))))
    )
    if missing_markers:
        return (
            BOUNDARY_CLASSIFICATION_INCOMPLETE,
            BOUNDARY_SEVERITY_BLOCKED,
            BOUNDARY_VISIBILITY_FAIL_VISIBLE,
            "required transition boundary references are incomplete: " + ", ".join(missing_markers),
            missing_markers,
        )
    blocked_markers = tuple(
        sorted(
            (
                *boundary_input.blocked_markers,
                *boundary_input.governance_blockers,
                *boundary_input.boundary_policy_violation_ids,
                *boundary_input.integrity_precondition_failures,
            )
        )
    )
    if blocked_markers:
        return (
            BOUNDARY_CLASSIFICATION_BLOCKED,
            BOUNDARY_SEVERITY_BLOCKED,
            BOUNDARY_VISIBILITY_FAIL_VISIBLE,
            "transition boundary is blocked by governance or integrity policy: " + ", ".join(blocked_markers),
            blocked_markers,
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(boundary_input.requested_capabilities)
        if capability not in SUPPORTED_BOUNDARY_CAPABILITIES
    )
    if boundary_input.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*boundary_input.unsupported_markers, *unsupported_capabilities)))
        return (
            BOUNDARY_CLASSIFICATION_UNSUPPORTED,
            BOUNDARY_SEVERITY_WARNING,
            BOUNDARY_VISIBILITY_FAIL_VISIBLE,
            "transition boundary capability is unsupported: " + ", ".join(markers),
            markers,
        )
    if boundary_input.unknown_markers or _intent_is_unknown(boundary_input):
        markers = tuple(sorted(boundary_input.unknown_markers or ("unknown_transition_intent",)))
        return (
            BOUNDARY_CLASSIFICATION_UNKNOWN,
            BOUNDARY_SEVERITY_WARNING,
            BOUNDARY_VISIBILITY_FAIL_VISIBLE,
            "transition boundary cannot be deterministically interpreted: " + ", ".join(markers),
            markers,
        )
    return (
        BOUNDARY_CLASSIFICATION_SAFE,
        BOUNDARY_SEVERITY_INFO,
        BOUNDARY_VISIBILITY_VISIBLE,
        "transition boundary is safe for deterministic evidence modeling only",
        (),
    )


def _missing_required_markers(boundary_input: TransitionBoundaryInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not boundary_input.source_state_id:
        markers.append("missing_source_state")
    if not boundary_input.destination_state_id:
        markers.append("missing_destination_state")
    if not boundary_input.transition_identity_id:
        markers.append("missing_transition_identity")
    if not boundary_input.provenance_reference_ids:
        markers.append("missing_provenance_reference")
    if not boundary_input.continuity_reference_ids:
        markers.append("missing_continuity_reference")
    if not boundary_input.evidence_reference_ids:
        markers.append("missing_evidence_reference")
    return tuple(sorted(set(markers)))


def _intent_is_unknown(boundary_input: TransitionBoundaryInput) -> bool:
    intent = boundary_input.transition_intent.strip().lower()
    domain = boundary_input.transition_domain.strip().lower()
    return not intent or "ambiguous" in intent or "unknown" in intent or not domain or "unknown" in domain


def _reference_or_missing(values: tuple[str, ...], missing_reference: str) -> str:
    if values:
        return sorted(values)[0]
    return missing_reference


def _evidence_reference(boundary_input: TransitionBoundaryInput) -> str:
    if boundary_input.evidence_reference_ids:
        return sorted(boundary_input.evidence_reference_ids)[0]
    return "missing_evidence_reference_fail_visible"


def _explainability_message(
    boundary_input: TransitionBoundaryInput,
    classification: str,
    reason: str,
) -> str:
    context = boundary_input.explainability_context or "no additional context"
    return (
        f"{classification} transition boundary classification for {boundary_input.input_id}: "
        f"{reason}; context: {context}"
    )


def _count_classifications(findings: tuple[TransitionBoundaryFinding, ...]) -> dict[str, int]:
    counts = Counter(finding.classification for finding in findings)
    return {classification: counts.get(classification, 0) for classification in BOUNDARY_CLASSIFICATIONS}
