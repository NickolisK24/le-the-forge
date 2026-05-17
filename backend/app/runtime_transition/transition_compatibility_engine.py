"""Deterministic v3.9 transition compatibility reasoning.

This module produces compatibility evidence only. It does not execute,
traverse, route, schedule, dispatch, mutate, optimize, recommend, rank, score,
select, authorize, approve, or expose callable orchestration behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_boundary_classifier import classify_v3_9_transition_boundaries
from .transition_boundary_models import (
    BOUNDARY_CLASSIFICATION_SAFE,
)
from .transition_compatibility_models import (
    COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PROHIBITED,
    COMPATIBILITY_CLASSIFICATION_UNKNOWN,
    COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
    COMPATIBILITY_CLASSIFICATIONS,
    COMPATIBILITY_CONFLICT_BOUNDARY,
    COMPATIBILITY_CONFLICT_CONTINUITY,
    COMPATIBILITY_CONFLICT_EXPLAINABILITY,
    COMPATIBILITY_CONFLICT_MISSING_EVIDENCE,
    COMPATIBILITY_CONFLICT_PROHIBITED_STATE,
    COMPATIBILITY_CONFLICT_PROVENANCE,
    COMPATIBILITY_CONFLICT_TRANSITION_STATE,
    COMPATIBILITY_CONFLICT_TYPES,
    COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE,
    COMPATIBILITY_SEVERITY_BLOCKED,
    COMPATIBILITY_SEVERITY_INFO,
    COMPATIBILITY_SEVERITY_WARNING,
    COMPATIBILITY_VISIBILITY_FAIL_VISIBLE,
    PROHIBITED_COMPATIBILITY_CAPABILITIES,
    SUPPORTED_COMPATIBILITY_CAPABILITIES,
    TransitionCompatibilityConflict,
    TransitionCompatibilityEvidence,
    TransitionCompatibilityFinding,
    TransitionCompatibilityInput,
    TransitionCompatibilityReport,
    TransitionCompatibilitySummary,
    V3_9_TRANSITION_COMPATIBILITY_REPORT_BLOCKED,
    V3_9_TRANSITION_COMPATIBILITY_REPORT_STABLE,
    transition_compatibility_conflict_id,
    transition_compatibility_finding_id,
)
from .transition_compatibility_serialization import (
    hash_transition_compatibility_report,
    hash_transition_compatibility_summary,
)
from .transition_compatibility_validation import validate_transition_compatibility_report
from .transition_foundation_models import (
    TRANSITION_CLASSIFICATION_SUPPORTED,
    TransitionFoundation,
    default_v3_9_transition_foundation,
)


def default_transition_compatibility_inputs(
    foundation: TransitionFoundation | None = None,
) -> tuple[TransitionCompatibilityInput, ...]:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    provenance_ids = tuple(reference.provenance_reference_id for reference in source.provenance_references)
    continuity_ids = tuple(reference.continuity_reference_id for reference in source.continuity_references)
    evidence_ids = (
        *(record.evidence_record_id for record in source.evidence_records),
        boundary_report.boundary_report_id,
    )
    base = {
        "source_transition_state_id": "v3_8_coordination_closeout_ready_for_v3_9",
        "destination_transition_state_id": "v3_9_transition_compatibility_intelligence",
        "source_boundary_classification": BOUNDARY_CLASSIFICATION_SAFE,
        "destination_boundary_classification": BOUNDARY_CLASSIFICATION_SAFE,
        "source_transition_classification": TRANSITION_CLASSIFICATION_SUPPORTED,
        "destination_transition_classification": TRANSITION_CLASSIFICATION_SUPPORTED,
        "provenance_reference_ids": provenance_ids,
        "continuity_reference_ids": continuity_ids,
        "compatibility_evidence_ids": evidence_ids,
    }
    return (
        TransitionCompatibilityInput(
            input_id="compatible_transition_compatibility",
            **base,
            requested_capabilities=("deterministic_compatibility_reasoning",),
            explainability_context="all compatibility prerequisites are present with no conflicts",
        ),
        TransitionCompatibilityInput(
            input_id="incompatible_transition_compatibility",
            **base,
            requested_capabilities=("deterministic_compatibility_reasoning",),
            provenance_conflict_markers=("source_lineage_mismatch",),
            continuity_conflict_markers=("rollback_chain_mismatch",),
            boundary_conflict_markers=("boundary_safe_to_blocked_mismatch",),
            transition_state_conflict_markers=("source_supported_destination_prohibited",),
            governance_requirement_ids=("governance_requirement_conflict",),
            explainability_context="deterministic conflicts exist between transition compatibility references",
        ),
        TransitionCompatibilityInput(
            input_id="partially_compatible_transition_compatibility",
            **base,
            requested_capabilities=("deterministic_compatibility_reasoning",),
            boundary_conflict_markers=("localized_boundary_warning",),
            explainability_conflict_markers=("localized_explainability_scope_gap",),
            partial_success_markers=("provenance_aligned", "replay_continuity_present"),
            partial_failure_markers=("localized_boundary_warning", "localized_explainability_scope_gap"),
            explainability_context="some compatibility guarantees pass while localized conflicts remain visible",
        ),
        TransitionCompatibilityInput(
            input_id="unsupported_transition_compatibility",
            **base,
            requested_capabilities=("cross_domain_compatibility_prediction",),
            unsupported_state_markers=("unsupported_state:cross_domain_compatibility_prediction",),
            explainability_context="compatibility reasoning domain is outside current deterministic scope",
        ),
        TransitionCompatibilityInput(
            input_id="prohibited_transition_compatibility",
            **base,
            requested_capabilities=("orchestration_execution", "routing", "runtime_mutation"),
            prohibited_state_markers=("prohibited_compatibility_execution_request",),
            explainability_context="requested compatibility behavior would violate non-execution boundaries",
        ),
        TransitionCompatibilityInput(
            input_id="unknown_transition_compatibility",
            **base,
            requested_capabilities=("deterministic_compatibility_reasoning",),
            unknown_markers=("ambiguous_compatibility_semantics",),
            explainability_context="compatibility semantics cannot be deterministically interpreted",
        ),
        TransitionCompatibilityInput(
            input_id="incomplete_transition_compatibility",
            source_transition_state_id="",
            destination_transition_state_id="v3_9_transition_compatibility_intelligence",
            source_boundary_classification=BOUNDARY_CLASSIFICATION_SAFE,
            destination_boundary_classification=BOUNDARY_CLASSIFICATION_SAFE,
            source_transition_classification=TRANSITION_CLASSIFICATION_SUPPORTED,
            destination_transition_classification=TRANSITION_CLASSIFICATION_SUPPORTED,
            provenance_reference_ids=(),
            continuity_reference_ids=(),
            compatibility_evidence_ids=(),
            requested_capabilities=("deterministic_compatibility_reasoning",),
            incomplete_markers=(
                "missing_source_transition_state",
                "missing_provenance_evidence",
                "missing_continuity_evidence",
                "missing_compatibility_evidence",
            ),
            explainability_context="required compatibility references are missing",
        ),
    )


def evaluate_v3_9_transition_compatibility(
    compatibility_inputs: Iterable[TransitionCompatibilityInput] | None = None,
    foundation: TransitionFoundation | None = None,
) -> TransitionCompatibilityReport:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    inputs = tuple(
        sorted(
            tuple(compatibility_inputs or default_transition_compatibility_inputs(source)),
            key=lambda item: item.input_id,
        )
    )
    findings: list[TransitionCompatibilityFinding] = []
    conflicts: list[TransitionCompatibilityConflict] = []
    for index, compatibility_input in enumerate(inputs, start=1):
        input_conflicts = _conflicts_from_input(compatibility_input, deterministic_order_base=index * 100)
        finding = _finding_from_input(
            compatibility_input,
            conflicts=input_conflicts,
            deterministic_order=index,
        )
        findings.append(finding)
        conflicts.extend(input_conflicts)
    summary = _summary_from_findings(tuple(findings), tuple(conflicts))
    summary = replace(summary, deterministic_summary_hash=hash_transition_compatibility_summary(summary))
    base_report = TransitionCompatibilityReport(
        report_id="v3_9_transition_compatibility_intelligence_report",
        report_status=V3_9_TRANSITION_COMPATIBILITY_REPORT_STABLE,
        source_foundation_id=source.identity.transition_id,
        source_boundary_report_id=boundary_report.boundary_report_id,
        compatibility_inputs=inputs,
        findings=tuple(findings),
        conflicts=tuple(sorted(conflicts, key=lambda item: (item.deterministic_order, item.conflict_id))),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_compatibility_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_COMPATIBILITY_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_COMPATIBILITY_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_compatibility_hash=hash_transition_compatibility_report(report))


def _finding_from_input(
    compatibility_input: TransitionCompatibilityInput,
    conflicts: tuple[TransitionCompatibilityConflict, ...],
    deterministic_order: int,
) -> TransitionCompatibilityFinding:
    classification, severity, reason = _classify_input(compatibility_input)
    evidence = TransitionCompatibilityEvidence(
        evidence_id=f"v3_9_compatibility_evidence_{compatibility_input.input_id}",
        input_id=compatibility_input.input_id,
        source_transition_state_id=compatibility_input.source_transition_state_id,
        destination_transition_state_id=compatibility_input.destination_transition_state_id,
        compatibility_evidence_ids=_evidence_references(compatibility_input),
        provenance_reference_ids=(
            _reference_or_missing(
                compatibility_input.provenance_reference_ids,
                "missing_provenance_reference_fail_visible",
            ),
        ),
        continuity_reference_ids=(
            _reference_or_missing(
                compatibility_input.continuity_reference_ids,
                "missing_continuity_reference_fail_visible",
            ),
        ),
        conflict_ids=tuple(conflict.conflict_id for conflict in conflicts),
        deterministic_hash_reference="v3_9_transition_compatibility_hash",
    )
    requested_capabilities = tuple(sorted(compatibility_input.requested_capabilities))
    execution_boundary_violation = any(
        capability in PROHIBITED_COMPATIBILITY_CAPABILITIES for capability in requested_capabilities
    )
    return TransitionCompatibilityFinding(
        finding_id=transition_compatibility_finding_id(classification, compatibility_input.input_id),
        input_id=compatibility_input.input_id,
        classification=classification,
        severity=severity,
        reason=reason,
        evidence=evidence,
        conflicts=conflicts,
        deterministic_order=deterministic_order,
        fail_visible=True,
        hidden=False,
        compatible_state=classification == COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
        execution_boundary_violation_detected=execution_boundary_violation,
        non_execution_confirmation=True,
        replay_safe=evidence.replay_safe,
        rollback_safe=evidence.rollback_safe,
        provenance_preserved=evidence.provenance_preserved,
        explainability_safe=evidence.explainability_safe,
    )


def _classify_input(source: TransitionCompatibilityInput) -> tuple[str, str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_COMPATIBILITY_CAPABILITIES
    )
    if source.prohibited_state_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_state_markers, *prohibited_capabilities)))
        return (
            COMPATIBILITY_CLASSIFICATION_PROHIBITED,
            COMPATIBILITY_SEVERITY_BLOCKED,
            "prohibited compatibility behavior requested: " + ", ".join(markers),
        )
    missing_markers = tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source)))))
    if missing_markers:
        return (
            COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
            COMPATIBILITY_SEVERITY_BLOCKED,
            "required transition compatibility references are incomplete: " + ", ".join(missing_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_COMPATIBILITY_CAPABILITIES
        and capability not in PROHIBITED_COMPATIBILITY_CAPABILITIES
    )
    if source.unsupported_state_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_state_markers, *unsupported_capabilities)))
        return (
            COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
            COMPATIBILITY_SEVERITY_WARNING,
            "transition compatibility domain is unsupported: " + ", ".join(markers),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_compatibility_semantics",)))
        return (
            COMPATIBILITY_CLASSIFICATION_UNKNOWN,
            COMPATIBILITY_SEVERITY_WARNING,
            "transition compatibility cannot be deterministically interpreted: " + ", ".join(markers),
        )
    if source.partial_success_markers and source.partial_failure_markers:
        markers = tuple(sorted((*source.partial_success_markers, *source.partial_failure_markers)))
        return (
            COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
            COMPATIBILITY_SEVERITY_WARNING,
            "transition compatibility is partial with localized visible results: " + ", ".join(markers),
        )
    if _has_conflict_markers(source):
        markers = tuple(sorted(_all_conflict_markers(source)))
        return (
            COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
            COMPATIBILITY_SEVERITY_BLOCKED,
            "deterministic transition compatibility conflicts exist: " + ", ".join(markers),
        )
    return (
        COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
        COMPATIBILITY_SEVERITY_INFO,
        "transition states are compatible for deterministic evidence reasoning only",
    )


def _conflicts_from_input(
    source: TransitionCompatibilityInput,
    deterministic_order_base: int,
) -> tuple[TransitionCompatibilityConflict, ...]:
    conflict_specs: list[tuple[str, str, str]] = []
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_PROVENANCE, marker, "provenance conflict detected")
        for marker in source.provenance_conflict_markers
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_CONTINUITY, marker, "continuity conflict detected")
        for marker in source.continuity_conflict_markers
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_BOUNDARY, marker, "boundary conflict detected")
        for marker in source.boundary_conflict_markers
    )
    if source.source_boundary_classification != BOUNDARY_CLASSIFICATION_SAFE:
        conflict_specs.append(
            (
                COMPATIBILITY_CONFLICT_BOUNDARY,
                f"source_boundary_classification:{source.source_boundary_classification}",
                "source boundary classification conflict detected",
            )
        )
    if source.destination_boundary_classification != BOUNDARY_CLASSIFICATION_SAFE:
        conflict_specs.append(
            (
                COMPATIBILITY_CONFLICT_BOUNDARY,
                f"destination_boundary_classification:{source.destination_boundary_classification}",
                "destination boundary classification conflict detected",
            )
        )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_TRANSITION_STATE, marker, "transition-state conflict detected")
        for marker in source.transition_state_conflict_markers
    )
    if source.source_transition_classification != TRANSITION_CLASSIFICATION_SUPPORTED:
        conflict_specs.append(
            (
                COMPATIBILITY_CONFLICT_TRANSITION_STATE,
                f"source_transition_classification:{source.source_transition_classification}",
                "source transition-state classification conflict detected",
            )
        )
    if source.destination_transition_classification != TRANSITION_CLASSIFICATION_SUPPORTED:
        conflict_specs.append(
            (
                COMPATIBILITY_CONFLICT_TRANSITION_STATE,
                f"destination_transition_classification:{source.destination_transition_classification}",
                "destination transition-state classification conflict detected",
            )
        )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE, marker, "unsupported-state conflict detected")
        for marker in source.unsupported_state_markers
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE, capability, "unsupported compatibility capability detected")
        for capability in source.requested_capabilities
        if capability not in SUPPORTED_COMPATIBILITY_CAPABILITIES
        and capability not in PROHIBITED_COMPATIBILITY_CAPABILITIES
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_PROHIBITED_STATE, marker, "prohibited-state conflict detected")
        for marker in source.prohibited_state_markers
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_PROHIBITED_STATE, capability, "prohibited capability requested")
        for capability in source.requested_capabilities
        if capability in PROHIBITED_COMPATIBILITY_CAPABILITIES
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_EXPLAINABILITY, marker, "explainability conflict detected")
        for marker in (*source.explainability_conflict_markers, *source.unknown_markers)
    )
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_BOUNDARY, marker, "governance requirement conflict detected")
        for marker in source.governance_requirement_ids
    )
    missing_markers = tuple(sorted(set((*source.missing_evidence_markers, *_missing_required_markers(source)))))
    conflict_specs.extend(
        (COMPATIBILITY_CONFLICT_MISSING_EVIDENCE, marker, "missing evidence conflict detected")
        for marker in missing_markers
    )
    conflicts: list[TransitionCompatibilityConflict] = []
    for offset, (conflict_type, marker, message) in enumerate(
        sorted(conflict_specs, key=lambda item: (_conflict_order(item[0]), item[1])),
        start=1,
    ):
        evidence_reference = _reference_or_missing(
            source.compatibility_evidence_ids,
            "missing_compatibility_evidence_fail_visible",
        )
        provenance_reference = _reference_or_missing(
            source.provenance_reference_ids,
            "missing_provenance_reference_fail_visible",
        )
        continuity_reference = _reference_or_missing(
            source.continuity_reference_ids,
            "missing_continuity_reference_fail_visible",
        )
        conflicts.append(
            TransitionCompatibilityConflict(
                conflict_id=transition_compatibility_conflict_id(source.input_id, conflict_type, marker),
                input_id=source.input_id,
                conflict_type=conflict_type,
                conflict_marker=marker,
                severity=COMPATIBILITY_SEVERITY_BLOCKED
                if conflict_type in (COMPATIBILITY_CONFLICT_PROHIBITED_STATE, COMPATIBILITY_CONFLICT_MISSING_EVIDENCE)
                else COMPATIBILITY_SEVERITY_WARNING,
                visibility_status=COMPATIBILITY_VISIBILITY_FAIL_VISIBLE,
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=f"{message} for {source.input_id}: {marker}",
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
            )
        )
    return tuple(conflicts)


def _summary_from_findings(
    findings: tuple[TransitionCompatibilityFinding, ...],
    conflicts: tuple[TransitionCompatibilityConflict, ...],
) -> TransitionCompatibilitySummary:
    classification_counts = Counter(finding.classification for finding in findings)
    conflict_counts = Counter(conflict.conflict_type for conflict in conflicts)
    counts = {classification: classification_counts.get(classification, 0) for classification in COMPATIBILITY_CLASSIFICATIONS}
    conflicts_by_type = {conflict_type: conflict_counts.get(conflict_type, 0) for conflict_type in COMPATIBILITY_CONFLICT_TYPES}
    return TransitionCompatibilitySummary(
        summary_id="v3_9_transition_compatibility_summary",
        classification_counts=counts,
        conflict_counts=conflicts_by_type,
        compatible_count=counts[COMPATIBILITY_CLASSIFICATION_COMPATIBLE],
        incompatible_count=counts[COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE],
        partially_compatible_count=counts[COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE],
        unsupported_count=counts[COMPATIBILITY_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[COMPATIBILITY_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[COMPATIBILITY_CLASSIFICATION_UNKNOWN],
        incomplete_count=counts[COMPATIBILITY_CLASSIFICATION_INCOMPLETE],
        compatibility_conflict_count=len(conflicts),
        provenance_conflict_count=conflicts_by_type[COMPATIBILITY_CONFLICT_PROVENANCE],
        continuity_conflict_count=conflicts_by_type[COMPATIBILITY_CONFLICT_CONTINUITY],
        boundary_conflict_count=conflicts_by_type[COMPATIBILITY_CONFLICT_BOUNDARY],
        hidden_conflict_count=sum(1 for conflict in conflicts if conflict.hidden),
        execution_boundary_violation_count=sum(
            1
            for conflict in conflicts
            if conflict.conflict_type == COMPATIBILITY_CONFLICT_PROHIBITED_STATE
            and conflict.conflict_marker in PROHIBITED_COMPATIBILITY_CAPABILITIES
        ),
    )


def _missing_required_markers(source: TransitionCompatibilityInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.source_transition_state_id:
        markers.append("missing_source_transition_state")
    if not source.destination_transition_state_id:
        markers.append("missing_destination_transition_state")
    if not source.source_boundary_classification:
        markers.append("missing_source_boundary_classification")
    if not source.destination_boundary_classification:
        markers.append("missing_destination_boundary_classification")
    if not source.source_transition_classification:
        markers.append("missing_source_transition_classification")
    if not source.destination_transition_classification:
        markers.append("missing_destination_transition_classification")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.continuity_reference_ids:
        markers.append("missing_continuity_evidence")
    if not source.compatibility_evidence_ids:
        markers.append("missing_compatibility_evidence")
    return tuple(sorted(set(markers)))


def _all_conflict_markers(source: TransitionCompatibilityInput) -> tuple[str, ...]:
    return tuple(
        sorted(
            (
                *source.provenance_conflict_markers,
                *source.continuity_conflict_markers,
                *source.boundary_conflict_markers,
                *source.transition_state_conflict_markers,
                *source.unsupported_state_markers,
                *source.prohibited_state_markers,
                *source.explainability_conflict_markers,
                *source.missing_evidence_markers,
                *source.governance_requirement_ids,
            )
        )
    )


def _has_conflict_markers(source: TransitionCompatibilityInput) -> bool:
    return bool(_all_conflict_markers(source)) or (
        source.source_boundary_classification != BOUNDARY_CLASSIFICATION_SAFE
        or source.destination_boundary_classification != BOUNDARY_CLASSIFICATION_SAFE
        or source.source_transition_classification != TRANSITION_CLASSIFICATION_SUPPORTED
        or source.destination_transition_classification != TRANSITION_CLASSIFICATION_SUPPORTED
    )


def _semantics_are_unknown(source: TransitionCompatibilityInput) -> bool:
    values = (
        source.source_transition_state_id,
        source.destination_transition_state_id,
        source.source_boundary_classification,
        source.destination_boundary_classification,
    )
    return any("unknown" in value.strip().lower() or "ambiguous" in value.strip().lower() for value in values)


def _reference_or_missing(values: tuple[str, ...], missing_reference: str) -> str:
    if values:
        return sorted(values)[0]
    return missing_reference


def _evidence_references(source: TransitionCompatibilityInput) -> tuple[str, ...]:
    if source.compatibility_evidence_ids:
        return tuple(sorted(source.compatibility_evidence_ids))
    return ("missing_compatibility_evidence_fail_visible",)


def _conflict_order(conflict_type: str) -> int:
    try:
        return COMPATIBILITY_CONFLICT_TYPES.index(conflict_type)
    except ValueError:
        return len(COMPATIBILITY_CONFLICT_TYPES)
