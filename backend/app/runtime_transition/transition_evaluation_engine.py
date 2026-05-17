"""Deterministic v3.9 transition evaluation reasoning.

This module evaluates transition relationships as evidence only. It does not
execute transitions, traverse orchestration graphs, route, schedule, dispatch,
mutate, optimize, recommend, rank, score, select, authorize, approve, or expose
callable orchestration behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_boundary_classifier import classify_v3_9_transition_boundaries
from .transition_compatibility_engine import evaluate_v3_9_transition_compatibility
from .transition_compatibility_models import (
    COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
)
from .transition_evaluation_models import (
    EVALUATION_CLASSIFICATION_BLOCKED,
    EVALUATION_CLASSIFICATION_INCOMPLETE,
    EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_PROHIBITED,
    EVALUATION_CLASSIFICATION_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNKNOWN,
    EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUPPORTED,
    EVALUATION_CLASSIFICATIONS,
    EVALUATION_FINDING_COMPATIBILITY,
    EVALUATION_FINDING_CONTINUITY,
    EVALUATION_FINDING_CATEGORIES,
    EVALUATION_FINDING_EXPLAINABILITY,
    EVALUATION_FINDING_GOVERNANCE,
    EVALUATION_FINDING_INTEGRITY,
    EVALUATION_FINDING_MISSING_EVIDENCE,
    EVALUATION_FINDING_PROHIBITED,
    EVALUATION_FINDING_PROVENANCE,
    EVALUATION_FINDING_UNCERTAINTY,
    EVALUATION_FINDING_UNSUPPORTED,
    EVALUATION_SEVERITY_BLOCKED,
    EVALUATION_SEVERITY_INFO,
    EVALUATION_SEVERITY_WARNING,
    EVALUATION_VISIBILITY_FAIL_VISIBLE,
    EVALUATION_VISIBILITY_VISIBLE,
    PROHIBITED_EVALUATION_CAPABILITIES,
    SUPPORTED_EVALUATION_CAPABILITIES,
    TransitionEvaluationContinuity,
    TransitionEvaluationEvidence,
    TransitionEvaluationFinding,
    TransitionEvaluationInput,
    TransitionEvaluationReport,
    TransitionEvaluationSummary,
    TransitionEvaluationVisibility,
    V3_9_TRANSITION_EVALUATION_REPORT_BLOCKED,
    V3_9_TRANSITION_EVALUATION_REPORT_STABLE,
    transition_evaluation_finding_id,
)
from .transition_evaluation_serialization import (
    hash_transition_evaluation_report,
    hash_transition_evaluation_summary,
)
from .transition_evaluation_validation import validate_transition_evaluation_report
from .transition_foundation_models import TransitionFoundation, default_v3_9_transition_foundation
from .transition_foundation_continuity import (
    CONTINUITY_TYPE_EXPLAINABILITY,
    CONTINUITY_TYPE_PROVENANCE,
    CONTINUITY_TYPE_REPLAY,
    CONTINUITY_TYPE_ROLLBACK,
)


def default_transition_evaluation_inputs(
    foundation: TransitionFoundation | None = None,
) -> tuple[TransitionEvaluationInput, ...]:
    source = foundation or default_v3_9_transition_foundation()
    compatibility_report = evaluate_v3_9_transition_compatibility(foundation=source)
    provenance_ids = tuple(reference.provenance_reference_id for reference in source.provenance_references)
    replay_ids = tuple(
        reference.continuity_reference_id
        for reference in source.continuity_references
        if reference.continuity_type == CONTINUITY_TYPE_REPLAY
    )
    rollback_ids = tuple(
        reference.continuity_reference_id
        for reference in source.continuity_references
        if reference.continuity_type == CONTINUITY_TYPE_ROLLBACK
    )
    provenance_continuity_ids = tuple(
        reference.continuity_reference_id
        for reference in source.continuity_references
        if reference.continuity_type == CONTINUITY_TYPE_PROVENANCE
    )
    explainability_ids = tuple(
        reference.continuity_reference_id
        for reference in source.continuity_references
        if reference.continuity_type == CONTINUITY_TYPE_EXPLAINABILITY
    )
    evidence_ids = (
        *(record.evidence_record_id for record in source.evidence_records),
        compatibility_report.report_id,
        compatibility_report.deterministic_compatibility_hash,
    )
    base = {
        "source_transition_state_id": "v3_8_coordination_closeout_ready_for_v3_9",
        "destination_transition_state_id": "v3_9_transition_evaluation_intelligence",
        "provenance_reference_ids": provenance_ids,
        "replay_continuity_ids": replay_ids,
        "rollback_continuity_ids": rollback_ids,
        "provenance_continuity_ids": provenance_continuity_ids,
        "explainability_continuity_ids": explainability_ids,
        "evaluation_evidence_ids": evidence_ids,
    }
    return (
        TransitionEvaluationInput(
            input_id="successful_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
            compatibility_conflict_ids=(),
            requested_capabilities=("deterministic_transition_evaluation",),
            explainability_context="compatible transition relationship has all required evaluation continuity",
        ),
        TransitionEvaluationInput(
            input_id="partially_successful_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
            compatibility_conflict_ids=("localized_boundary_warning", "localized_explainability_scope_gap"),
            requested_capabilities=("deterministic_transition_evaluation",),
            partial_success_markers=("provenance_continuity_present", "replay_continuity_present"),
            partial_failure_markers=("localized_evaluation_uncertainty", "localized_explainability_gap"),
            explainability_context="some evaluation guarantees pass while uncertainty remains explicit",
        ),
        TransitionEvaluationInput(
            input_id="unsuccessful_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
            compatibility_conflict_ids=("source_lineage_mismatch", "rollback_chain_mismatch"),
            requested_capabilities=("deterministic_transition_evaluation",),
            unsuccessful_markers=(
                "compatibility_finding_failed",
                "continuity_chain_failed",
                "provenance_chain_failed",
                "explainability_guarantee_failed",
            ),
            governance_policy_ids=("governance_requirement_failed",),
            integrity_policy_ids=("integrity_requirement_failed",),
            explainability_context="deterministic evaluation findings fail and remain fail-visible",
        ),
        TransitionEvaluationInput(
            input_id="unsupported_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
            compatibility_conflict_ids=(),
            requested_capabilities=("cross_domain_transition_evaluation",),
            unsupported_markers=("unsupported_domain:cross_domain_transition_evaluation",),
            explainability_context="evaluation domain is outside supported deterministic scope",
        ),
        TransitionEvaluationInput(
            input_id="prohibited_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
            compatibility_conflict_ids=(),
            requested_capabilities=("orchestration_execution", "routing", "runtime_mutation"),
            prohibited_markers=("prohibited_evaluation_execution_request",),
            explainability_context="evaluation request attempts to introduce prohibited behavior",
        ),
        TransitionEvaluationInput(
            input_id="unknown_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
            compatibility_conflict_ids=(),
            requested_capabilities=("deterministic_transition_evaluation",),
            unknown_markers=("ambiguous_evaluation_semantics",),
            explainability_context="evaluation semantics cannot be deterministically interpreted",
        ),
        TransitionEvaluationInput(
            input_id="incomplete_transition_evaluation",
            source_transition_state_id="",
            destination_transition_state_id="v3_9_transition_evaluation_intelligence",
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
            compatibility_conflict_ids=(),
            provenance_reference_ids=(),
            replay_continuity_ids=(),
            rollback_continuity_ids=(),
            provenance_continuity_ids=(),
            explainability_continuity_ids=(),
            evaluation_evidence_ids=(),
            requested_capabilities=("deterministic_transition_evaluation",),
            incomplete_markers=(
                "missing_evaluation_evidence",
                "missing_continuity_evidence",
                "missing_provenance_evidence",
                "missing_compatibility_evidence",
                "missing_explainability_evidence",
            ),
            explainability_context="required evaluation evidence is missing",
        ),
        TransitionEvaluationInput(
            input_id="blocked_transition_evaluation",
            **base,
            compatibility_classification=COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
            compatibility_conflict_ids=(),
            requested_capabilities=("deterministic_transition_evaluation",),
            blocked_markers=("blocked_by_execution_boundary_preservation",),
            governance_policy_ids=("governance_policy_blocks_evaluation",),
            integrity_policy_ids=("integrity_policy_blocks_evaluation",),
            explainability_context="governance and integrity policy block evaluation",
        ),
    )


def evaluate_v3_9_transition_evaluation(
    evaluation_inputs: Iterable[TransitionEvaluationInput] | None = None,
    foundation: TransitionFoundation | None = None,
) -> TransitionEvaluationReport:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    compatibility_report = evaluate_v3_9_transition_compatibility(foundation=source)
    inputs = tuple(
        sorted(
            tuple(evaluation_inputs or default_transition_evaluation_inputs(source)),
            key=lambda item: item.input_id,
        )
    )
    findings: list[TransitionEvaluationFinding] = []
    evidence_records: list[TransitionEvaluationEvidence] = []
    continuities: list[TransitionEvaluationContinuity] = []
    visibilities: list[TransitionEvaluationVisibility] = []
    for index, evaluation_input in enumerate(inputs, start=1):
        classification, severity, reason = _classify_input(evaluation_input)
        continuity = _continuity_from_input(evaluation_input)
        evidence_id = f"v3_9_evaluation_evidence_{evaluation_input.input_id}"
        input_findings = _findings_from_input(
            evaluation_input,
            classification=classification,
            severity=severity,
            evidence_reference=evidence_id,
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 100,
        )
        evidence = _evidence_from_input(evaluation_input, evidence_id, input_findings, continuity)
        visibility = _visibility_from_input(evaluation_input, classification, reason, evidence, continuity)
        findings.extend(input_findings)
        evidence_records.append(evidence)
        continuities.append(continuity)
        visibilities.append(visibility)
    summary = _summary_from_outputs(tuple(visibilities), tuple(findings))
    summary = replace(summary, deterministic_summary_hash=hash_transition_evaluation_summary(summary))
    base_report = TransitionEvaluationReport(
        report_id="v3_9_transition_evaluation_intelligence_report",
        report_status=V3_9_TRANSITION_EVALUATION_REPORT_STABLE,
        source_foundation_id=source.identity.transition_id,
        source_boundary_report_id=boundary_report.boundary_report_id,
        source_compatibility_report_id=compatibility_report.report_id,
        evaluation_inputs=inputs,
        findings=tuple(sorted(findings, key=lambda item: (item.deterministic_order, item.finding_id))),
        evidence_records=tuple(evidence_records),
        continuities=tuple(continuities),
        visibilities=tuple(visibilities),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_evaluation_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_EVALUATION_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_EVALUATION_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_evaluation_hash=hash_transition_evaluation_report(report))


def _classify_input(source: TransitionEvaluationInput) -> tuple[str, str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_EVALUATION_CAPABILITIES
    )
    if source.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_markers, *prohibited_capabilities)))
        return (
            EVALUATION_CLASSIFICATION_PROHIBITED,
            EVALUATION_SEVERITY_BLOCKED,
            "prohibited transition evaluation behavior requested: " + ", ".join(markers),
        )
    missing_markers = tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source)))))
    if missing_markers:
        return (
            EVALUATION_CLASSIFICATION_INCOMPLETE,
            EVALUATION_SEVERITY_BLOCKED,
            "required transition evaluation evidence is incomplete: " + ", ".join(missing_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_EVALUATION_CAPABILITIES
        and capability not in PROHIBITED_EVALUATION_CAPABILITIES
    )
    if source.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_markers, *unsupported_capabilities)))
        return (
            EVALUATION_CLASSIFICATION_UNSUPPORTED,
            EVALUATION_SEVERITY_WARNING,
            "transition evaluation domain is unsupported: " + ", ".join(markers),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_evaluation_semantics",)))
        return (
            EVALUATION_CLASSIFICATION_UNKNOWN,
            EVALUATION_SEVERITY_WARNING,
            "transition evaluation cannot be deterministically interpreted: " + ", ".join(markers),
        )
    if source.partial_success_markers and source.partial_failure_markers:
        markers = tuple(sorted((*source.partial_success_markers, *source.partial_failure_markers)))
        return (
            EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
            EVALUATION_SEVERITY_WARNING,
            "transition evaluation is partially successful with explicit uncertainty: " + ", ".join(markers),
        )
    if source.unsuccessful_markers or source.compatibility_classification != COMPATIBILITY_CLASSIFICATION_COMPATIBLE:
        markers = tuple(sorted((*source.unsuccessful_markers, *source.compatibility_conflict_ids)))
        return (
            EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
            EVALUATION_SEVERITY_BLOCKED,
            "transition evaluation is unsuccessful: " + ", ".join(markers),
        )
    blocked_markers = tuple(
        sorted((*source.blocked_markers, *source.governance_policy_ids, *source.integrity_policy_ids))
    )
    if blocked_markers:
        return (
            EVALUATION_CLASSIFICATION_BLOCKED,
            EVALUATION_SEVERITY_BLOCKED,
            "transition evaluation is blocked by governance or integrity policy: " + ", ".join(blocked_markers),
        )
    return (
        EVALUATION_CLASSIFICATION_SUCCESSFUL,
        EVALUATION_SEVERITY_INFO,
        "transition evaluation is successful for deterministic evidence reasoning only",
    )


def _findings_from_input(
    source: TransitionEvaluationInput,
    classification: str,
    severity: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionEvaluationFinding, ...]:
    finding_specs: list[tuple[str, str, str, str, bool]] = []
    if classification == EVALUATION_CLASSIFICATION_SUCCESSFUL:
        finding_specs.extend(
            (
                (EVALUATION_FINDING_COMPATIBILITY, "compatibility_verified", "compatible relationship verified", "info", False),
                (EVALUATION_FINDING_CONTINUITY, "continuity_verified", "replay and rollback continuity verified", "info", False),
                (EVALUATION_FINDING_PROVENANCE, "provenance_verified", "provenance continuity verified", "info", False),
                (EVALUATION_FINDING_EXPLAINABILITY, "explainability_verified", "explainability continuity verified", "info", False),
            )
        )
    if source.partial_success_markers or source.partial_failure_markers:
        finding_specs.extend(
            (
                (EVALUATION_FINDING_COMPATIBILITY, marker, "partial compatibility evaluation marker", "warning", False)
                for marker in source.partial_success_markers
            )
        )
        finding_specs.extend(
            (
                (EVALUATION_FINDING_UNCERTAINTY, marker, "partial evaluation uncertainty remains visible", "warning", True)
                for marker in source.partial_failure_markers
            )
        )
        finding_specs.append(
            (
                EVALUATION_FINDING_EXPLAINABILITY,
                "partial_success_requires_visible_explanation",
                "partial evaluation remains explainability-bound",
                "warning",
                True,
            )
        )
    for marker in source.unsuccessful_markers:
        finding_specs.append((_category_for_unsuccessful_marker(marker), marker, "unsuccessful evaluation marker", "blocked", False))
    for marker in source.governance_policy_ids:
        finding_specs.append((EVALUATION_FINDING_GOVERNANCE, marker, "governance evaluation finding", "blocked", False))
    for marker in source.integrity_policy_ids:
        finding_specs.append((EVALUATION_FINDING_INTEGRITY, marker, "integrity evaluation finding", "blocked", False))
    for marker in source.unsupported_markers:
        finding_specs.append((EVALUATION_FINDING_UNSUPPORTED, marker, "unsupported evaluation finding", "warning", False))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_EVALUATION_CAPABILITIES and capability not in PROHIBITED_EVALUATION_CAPABILITIES:
            finding_specs.append((EVALUATION_FINDING_UNSUPPORTED, capability, "unsupported evaluation capability", "warning", False))
    for marker in source.prohibited_markers:
        finding_specs.append((EVALUATION_FINDING_PROHIBITED, marker, "prohibited evaluation finding", "blocked", False))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_EVALUATION_CAPABILITIES:
            finding_specs.append((EVALUATION_FINDING_PROHIBITED, capability, "prohibited evaluation capability", "blocked", False))
    for marker in source.unknown_markers:
        finding_specs.append((EVALUATION_FINDING_UNCERTAINTY, marker, "uncertain evaluation finding", "warning", True))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        finding_specs.append((EVALUATION_FINDING_MISSING_EVIDENCE, marker, "missing evaluation evidence finding", "blocked", False))
    for marker in source.blocked_markers:
        finding_specs.append((EVALUATION_FINDING_GOVERNANCE, marker, "blocked evaluation finding", "blocked", False))
    if not finding_specs:
        finding_specs.append((EVALUATION_FINDING_COMPATIBILITY, classification, "evaluation classification finding", severity, False))
    findings: list[TransitionEvaluationFinding] = []
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    for offset, (category, marker, message, marker_severity, uncertainty_visible) in enumerate(
        sorted(finding_specs, key=lambda item: (_finding_category_order(item[0]), item[1])),
        start=1,
    ):
        finding_severity = {
            "info": EVALUATION_SEVERITY_INFO,
            "warning": EVALUATION_SEVERITY_WARNING,
            "blocked": EVALUATION_SEVERITY_BLOCKED,
        }[marker_severity]
        findings.append(
            TransitionEvaluationFinding(
                finding_id=transition_evaluation_finding_id(source.input_id, category, marker),
                input_id=source.input_id,
                finding_category=category,
                classification=classification,
                severity=finding_severity,
                reason=f"{message}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition evaluation finding for {source.input_id}: "
                    f"{message}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
                uncertainty_visible=uncertainty_visible,
                execution_boundary_violation_detected=category == EVALUATION_FINDING_PROHIBITED
                and marker in PROHIBITED_EVALUATION_CAPABILITIES,
                non_execution_confirmation=True,
            )
        )
    return tuple(findings)


def _continuity_from_input(source: TransitionEvaluationInput) -> TransitionEvaluationContinuity:
    return TransitionEvaluationContinuity(
        continuity_id=f"v3_9_evaluation_continuity_{source.input_id}",
        input_id=source.input_id,
        replay_continuity_ids=_references_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        rollback_continuity_ids=_references_or_missing(source.rollback_continuity_ids, "missing_rollback_continuity_fail_visible"),
        provenance_continuity_ids=_references_or_missing(source.provenance_continuity_ids, "missing_provenance_continuity_fail_visible"),
        explainability_continuity_ids=_references_or_missing(source.explainability_continuity_ids, "missing_explainability_continuity_fail_visible"),
        evidence_continuity_ids=_references_or_missing(source.evaluation_evidence_ids, "missing_evaluation_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_evaluation_hash",
        replay_continuity_preserved=True,
        rollback_continuity_preserved=True,
        provenance_continuity_preserved=True,
        explainability_continuity_preserved=True,
        immutable_continuity=True,
    )


def _evidence_from_input(
    source: TransitionEvaluationInput,
    evidence_id: str,
    findings: tuple[TransitionEvaluationFinding, ...],
    continuity: TransitionEvaluationContinuity,
) -> TransitionEvaluationEvidence:
    continuity_ids = (
        *continuity.replay_continuity_ids,
        *continuity.rollback_continuity_ids,
        *continuity.provenance_continuity_ids,
        *continuity.explainability_continuity_ids,
        *continuity.evidence_continuity_ids,
    )
    return TransitionEvaluationEvidence(
        evidence_id=evidence_id,
        input_id=source.input_id,
        evaluation_evidence_ids=_references_or_missing(source.evaluation_evidence_ids, "missing_evaluation_evidence_fail_visible"),
        compatibility_reference_ids=_references_or_missing(
            (source.compatibility_classification, *source.compatibility_conflict_ids),
            "missing_compatibility_evidence_fail_visible",
        ),
        provenance_reference_ids=_references_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible"),
        continuity_reference_ids=continuity_ids,
        finding_ids=tuple(finding.finding_id for finding in findings),
        deterministic_hash_reference="v3_9_transition_evaluation_hash",
    )


def _visibility_from_input(
    source: TransitionEvaluationInput,
    classification: str,
    reason: str,
    evidence: TransitionEvaluationEvidence,
    continuity: TransitionEvaluationContinuity,
) -> TransitionEvaluationVisibility:
    non_successful = classification != EVALUATION_CLASSIFICATION_SUCCESSFUL
    return TransitionEvaluationVisibility(
        visibility_id=f"v3_9_evaluation_visibility_{source.input_id}",
        input_id=source.input_id,
        classification=classification,
        visibility_status=EVALUATION_VISIBILITY_FAIL_VISIBLE if non_successful else EVALUATION_VISIBILITY_VISIBLE,
        reason=reason,
        deterministic_evidence_reference=evidence.evidence_id,
        provenance_reference=evidence.provenance_reference_ids[0],
        continuity_reference=continuity.continuity_id,
        explainability_message=(
            f"{classification} transition evaluation visibility for {source.input_id}: "
            f"{reason}; context: {source.explainability_context}"
        ),
        fail_visible=True,
        hidden=False,
        uncertainty_visible=classification in (
            EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
            EVALUATION_CLASSIFICATION_UNKNOWN,
        ),
    )


def _summary_from_outputs(
    visibilities: tuple[TransitionEvaluationVisibility, ...],
    findings: tuple[TransitionEvaluationFinding, ...],
) -> TransitionEvaluationSummary:
    classification_counts = Counter(visibility.classification for visibility in visibilities)
    category_counts = Counter(finding.finding_category for finding in findings)
    counts = {classification: classification_counts.get(classification, 0) for classification in EVALUATION_CLASSIFICATIONS}
    categories = {category: category_counts.get(category, 0) for category in EVALUATION_FINDING_CATEGORIES}
    return TransitionEvaluationSummary(
        summary_id="v3_9_transition_evaluation_summary",
        classification_counts=counts,
        finding_category_counts=categories,
        successful_count=counts[EVALUATION_CLASSIFICATION_SUCCESSFUL],
        partially_successful_count=counts[EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL],
        unsuccessful_count=counts[EVALUATION_CLASSIFICATION_UNSUCCESSFUL],
        unsupported_count=counts[EVALUATION_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[EVALUATION_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[EVALUATION_CLASSIFICATION_UNKNOWN],
        incomplete_count=counts[EVALUATION_CLASSIFICATION_INCOMPLETE],
        blocked_count=counts[EVALUATION_CLASSIFICATION_BLOCKED],
        evaluation_finding_count=len(findings),
        governance_finding_count=categories[EVALUATION_FINDING_GOVERNANCE],
        uncertainty_finding_count=categories[EVALUATION_FINDING_UNCERTAINTY],
        missing_evidence_finding_count=categories[EVALUATION_FINDING_MISSING_EVIDENCE],
        execution_boundary_violation_count=sum(
            1 for finding in findings if finding.execution_boundary_violation_detected
        ),
        hidden_finding_count=sum(1 for finding in findings if finding.hidden),
    )


def _missing_required_markers(source: TransitionEvaluationInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.source_transition_state_id:
        markers.append("missing_source_transition_state")
    if not source.destination_transition_state_id:
        markers.append("missing_destination_transition_state")
    if not source.compatibility_classification:
        markers.append("missing_compatibility_evidence")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.replay_continuity_ids or not source.rollback_continuity_ids:
        markers.append("missing_continuity_evidence")
    if not source.explainability_continuity_ids:
        markers.append("missing_explainability_evidence")
    if not source.evaluation_evidence_ids:
        markers.append("missing_evaluation_evidence")
    return tuple(sorted(set(markers)))


def _category_for_unsuccessful_marker(marker: str) -> str:
    if "compatibility" in marker:
        return EVALUATION_FINDING_COMPATIBILITY
    if "continuity" in marker:
        return EVALUATION_FINDING_CONTINUITY
    if "provenance" in marker:
        return EVALUATION_FINDING_PROVENANCE
    if "explainability" in marker:
        return EVALUATION_FINDING_EXPLAINABILITY
    return EVALUATION_FINDING_INTEGRITY


def _semantics_are_unknown(source: TransitionEvaluationInput) -> bool:
    values = (
        source.source_transition_state_id,
        source.destination_transition_state_id,
        source.compatibility_classification,
    )
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
        return EVALUATION_FINDING_CATEGORIES.index(category)
    except ValueError:
        return len(EVALUATION_FINDING_CATEGORIES)
