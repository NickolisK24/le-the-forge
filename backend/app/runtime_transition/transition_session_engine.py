"""Deterministic v3.9 transition session reasoning.

This module records transition review sessions as immutable evidence only. It
does not execute transitions, authorize transitions, traverse graphs, route,
schedule, dispatch, mutate, optimize, recommend, rank, score, select, approve,
or expose callable orchestration behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_boundary_classifier import classify_v3_9_transition_boundaries
from .transition_compatibility_engine import evaluate_v3_9_transition_compatibility
from .transition_evaluation_engine import evaluate_v3_9_transition_evaluation
from .transition_evaluation_models import EVALUATION_CLASSIFICATION_SUCCESSFUL
from .transition_foundation_continuity import (
    CONTINUITY_TYPE_EXPLAINABILITY,
    CONTINUITY_TYPE_PROVENANCE,
    CONTINUITY_TYPE_REPLAY,
    CONTINUITY_TYPE_ROLLBACK,
)
from .transition_foundation_models import TransitionFoundation, default_v3_9_transition_foundation
from .transition_session_models import (
    PROHIBITED_SESSION_CAPABILITIES,
    SESSION_CLASSIFICATION_BLOCKED,
    SESSION_CLASSIFICATION_COMPLETE,
    SESSION_CLASSIFICATION_INCOMPLETE,
    SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
    SESSION_CLASSIFICATION_PROHIBITED,
    SESSION_CLASSIFICATION_UNKNOWN,
    SESSION_CLASSIFICATION_UNSUPPORTED,
    SESSION_CLASSIFICATIONS,
    SESSION_FINDING_COMPLETENESS,
    SESSION_FINDING_CONTINUITY,
    SESSION_FINDING_CATEGORIES,
    SESSION_FINDING_EVALUATION,
    SESSION_FINDING_EXPLAINABILITY,
    SESSION_FINDING_GOVERNANCE,
    SESSION_FINDING_INTEGRITY,
    SESSION_FINDING_MISSING_EVIDENCE,
    SESSION_FINDING_PROHIBITED,
    SESSION_FINDING_PROVENANCE,
    SESSION_FINDING_UNCERTAINTY,
    SESSION_FINDING_UNSUPPORTED,
    SESSION_SEVERITY_BLOCKED,
    SESSION_SEVERITY_INFO,
    SESSION_SEVERITY_WARNING,
    SESSION_VISIBILITY_FAIL_VISIBLE,
    SESSION_VISIBILITY_VISIBLE,
    SUPPORTED_SESSION_CAPABILITIES,
    TransitionSessionContinuity,
    TransitionSessionEntry,
    TransitionSessionEvidence,
    TransitionSessionFinding,
    TransitionSessionInput,
    TransitionSessionRecord,
    TransitionSessionReport,
    TransitionSessionSummary,
    TransitionSessionVisibility,
    V3_9_TRANSITION_SESSION_REPORT_BLOCKED,
    V3_9_TRANSITION_SESSION_REPORT_STABLE,
    transition_session_finding_id,
)
from .transition_session_serialization import hash_transition_session_report, hash_transition_session_summary
from .transition_session_validation import validate_transition_session_report


def default_transition_session_inputs(
    foundation: TransitionFoundation | None = None,
) -> tuple[TransitionSessionInput, ...]:
    source = foundation or default_v3_9_transition_foundation()
    evaluation_report = evaluate_v3_9_transition_evaluation(foundation=source)
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
    successful_evaluation_ids = tuple(
        visibility.input_id
        for visibility in evaluation_report.visibilities
        if visibility.classification == EVALUATION_CLASSIFICATION_SUCCESSFUL
    )
    all_evaluation_ids = tuple(visibility.input_id for visibility in evaluation_report.visibilities)
    session_evidence_ids = (
        evaluation_report.report_id,
        evaluation_report.deterministic_evaluation_hash,
        *(evidence.evidence_id for evidence in evaluation_report.evidence_records),
    )
    base = {
        "session_domain": "coordination_transition_session",
        "provenance_reference_ids": provenance_ids,
        "replay_continuity_ids": replay_ids,
        "rollback_continuity_ids": rollback_ids,
        "provenance_continuity_ids": provenance_continuity_ids,
        "explainability_continuity_ids": explainability_ids,
        "session_evidence_ids": session_evidence_ids,
    }
    return (
        TransitionSessionInput(
            input_id="complete_transition_session",
            session_id="v3_9_complete_transition_review_session",
            evaluation_record_ids=successful_evaluation_ids,
            complete_evaluation_record_ids=successful_evaluation_ids,
            requested_capabilities=("deterministic_transition_session_recording",),
            explainability_context="session identity and complete evaluation records are present",
            **base,
        ),
        TransitionSessionInput(
            input_id="partially_complete_transition_session",
            session_id="v3_9_partially_complete_transition_review_session",
            evaluation_record_ids=all_evaluation_ids,
            complete_evaluation_record_ids=successful_evaluation_ids,
            partial_success_markers=("complete_evaluation_present",),
            partial_failure_markers=("non_complete_evaluation_records_visible",),
            requested_capabilities=("deterministic_transition_session_recording",),
            explainability_context="at least one complete evaluation exists while other session guarantees remain visible",
            **base,
        ),
        TransitionSessionInput(
            input_id="incomplete_transition_session",
            session_id="",
            session_domain="coordination_transition_session",
            evaluation_record_ids=(),
            complete_evaluation_record_ids=(),
            provenance_reference_ids=(),
            replay_continuity_ids=(),
            rollback_continuity_ids=(),
            provenance_continuity_ids=(),
            explainability_continuity_ids=(),
            session_evidence_ids=(),
            incomplete_markers=(
                "missing_session_identity",
                "missing_evaluation_records",
                "missing_provenance_evidence",
                "missing_continuity_evidence",
                "missing_explainability_evidence",
            ),
            requested_capabilities=("deterministic_transition_session_recording",),
            explainability_context="required session identity and evidence are missing",
        ),
        TransitionSessionInput(
            input_id="blocked_transition_session",
            session_id="v3_9_blocked_transition_review_session",
            evaluation_record_ids=successful_evaluation_ids,
            complete_evaluation_record_ids=successful_evaluation_ids,
            blocked_markers=("blocked_by_execution_boundary_preservation",),
            governance_policy_ids=("governance_policy_blocks_session",),
            integrity_policy_ids=("integrity_policy_blocks_session",),
            requested_capabilities=("deterministic_transition_session_recording",),
            explainability_context="governance and integrity policy block session recording",
            **base,
        ),
        TransitionSessionInput(
            input_id="unsupported_transition_session",
            session_id="v3_9_unsupported_transition_review_session",
            evaluation_record_ids=successful_evaluation_ids,
            complete_evaluation_record_ids=successful_evaluation_ids,
            unsupported_markers=("unsupported_domain:cross_domain_session_packaging",),
            requested_capabilities=("cross_domain_transition_session_packaging",),
            explainability_context="session domain is outside supported deterministic scope",
            **base,
        ),
        TransitionSessionInput(
            input_id="prohibited_transition_session",
            session_id="v3_9_prohibited_transition_review_session",
            evaluation_record_ids=successful_evaluation_ids,
            complete_evaluation_record_ids=successful_evaluation_ids,
            prohibited_markers=("prohibited_session_execution_request",),
            requested_capabilities=("orchestration_execution", "routing", "runtime_mutation"),
            explainability_context="session recording request attempts to introduce prohibited behavior",
            **base,
        ),
        TransitionSessionInput(
            input_id="unknown_transition_session",
            session_id="v3_9_unknown_transition_review_session",
            evaluation_record_ids=successful_evaluation_ids,
            complete_evaluation_record_ids=successful_evaluation_ids,
            unknown_markers=("ambiguous_session_semantics",),
            requested_capabilities=("deterministic_transition_session_recording",),
            explainability_context="session semantics cannot be deterministically interpreted",
            **base,
        ),
    )


def build_v3_9_transition_session(
    session_inputs: Iterable[TransitionSessionInput] | None = None,
    foundation: TransitionFoundation | None = None,
) -> TransitionSessionReport:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    compatibility_report = evaluate_v3_9_transition_compatibility(foundation=source)
    evaluation_report = evaluate_v3_9_transition_evaluation(foundation=source)
    inputs = tuple(
        sorted(
            tuple(session_inputs or default_transition_session_inputs(source)),
            key=lambda item: item.input_id,
        )
    )
    records: list[TransitionSessionRecord] = []
    entries: list[TransitionSessionEntry] = []
    findings: list[TransitionSessionFinding] = []
    evidence_records: list[TransitionSessionEvidence] = []
    continuities: list[TransitionSessionContinuity] = []
    visibilities: list[TransitionSessionVisibility] = []
    for index, session_input in enumerate(inputs, start=1):
        classification, severity, reason = _classify_input(session_input)
        continuity = _continuity_from_input(session_input)
        input_entries = _entries_from_input(session_input, index * 100)
        evidence_id = f"v3_9_session_evidence_{session_input.input_id}"
        input_findings = _findings_from_input(
            session_input,
            classification=classification,
            severity=severity,
            evidence_reference=evidence_id,
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 1000,
        )
        evidence = _evidence_from_input(session_input, evidence_id, input_entries, input_findings, continuity)
        visibility = _visibility_from_input(session_input, classification, reason, evidence, continuity)
        record = TransitionSessionRecord(
            record_id=f"v3_9_session_record_{session_input.input_id}",
            input_id=session_input.input_id,
            session_id=session_input.session_id or "missing_session_identity_fail_visible",
            classification=classification,
            entries=input_entries,
            evidence=evidence,
            continuity=continuity,
            visibility=visibility,
            deterministic_order=index,
            immutable_record=True,
            non_executable=True,
        )
        records.append(record)
        entries.extend(input_entries)
        findings.extend(input_findings)
        evidence_records.append(evidence)
        continuities.append(continuity)
        visibilities.append(visibility)
    summary = _summary_from_outputs(tuple(visibilities), tuple(findings), tuple(entries))
    summary = replace(summary, deterministic_summary_hash=hash_transition_session_summary(summary))
    base_report = TransitionSessionReport(
        report_id="v3_9_transition_session_intelligence_report",
        report_status=V3_9_TRANSITION_SESSION_REPORT_STABLE,
        source_foundation_id=source.identity.transition_id,
        source_boundary_report_id=boundary_report.boundary_report_id,
        source_compatibility_report_id=compatibility_report.report_id,
        source_evaluation_report_id=evaluation_report.report_id,
        session_inputs=inputs,
        session_records=tuple(records),
        entries=tuple(sorted(entries, key=lambda item: (item.deterministic_order, item.entry_id))),
        findings=tuple(sorted(findings, key=lambda item: (item.deterministic_order, item.finding_id))),
        evidence_records=tuple(evidence_records),
        continuities=tuple(continuities),
        visibilities=tuple(visibilities),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_session_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_SESSION_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_SESSION_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_session_hash=hash_transition_session_report(report))


def _classify_input(source: TransitionSessionInput) -> tuple[str, str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_SESSION_CAPABILITIES
    )
    if source.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_markers, *prohibited_capabilities)))
        return (
            SESSION_CLASSIFICATION_PROHIBITED,
            SESSION_SEVERITY_BLOCKED,
            "prohibited transition session behavior requested: " + ", ".join(markers),
        )
    missing_markers = tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source)))))
    if missing_markers:
        return (
            SESSION_CLASSIFICATION_INCOMPLETE,
            SESSION_SEVERITY_BLOCKED,
            "required transition session evidence is incomplete: " + ", ".join(missing_markers),
        )
    blocked_markers = tuple(sorted((*source.blocked_markers, *source.governance_policy_ids, *source.integrity_policy_ids)))
    if blocked_markers:
        return (
            SESSION_CLASSIFICATION_BLOCKED,
            SESSION_SEVERITY_BLOCKED,
            "transition session is blocked by governance or integrity policy: " + ", ".join(blocked_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_SESSION_CAPABILITIES and capability not in PROHIBITED_SESSION_CAPABILITIES
    )
    if source.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_markers, *unsupported_capabilities)))
        return (
            SESSION_CLASSIFICATION_UNSUPPORTED,
            SESSION_SEVERITY_WARNING,
            "transition session domain is unsupported: " + ", ".join(markers),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_session_semantics",)))
        return (
            SESSION_CLASSIFICATION_UNKNOWN,
            SESSION_SEVERITY_WARNING,
            "transition session cannot be deterministically interpreted: " + ", ".join(markers),
        )
    if source.partial_success_markers and source.partial_failure_markers:
        markers = tuple(sorted((*source.partial_success_markers, *source.partial_failure_markers)))
        return (
            SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
            SESSION_SEVERITY_WARNING,
            "transition session is partially complete with visible gaps: " + ", ".join(markers),
        )
    return (
        SESSION_CLASSIFICATION_COMPLETE,
        SESSION_SEVERITY_INFO,
        "transition session is complete for deterministic evidence recording only",
    )


def _entries_from_input(source: TransitionSessionInput, deterministic_order_base: int) -> tuple[TransitionSessionEntry, ...]:
    evaluation_ids = source.evaluation_record_ids or ("missing_evaluation_record_fail_visible",)
    entries: list[TransitionSessionEntry] = []
    for offset, evaluation_id in enumerate(sorted(evaluation_ids), start=1):
        complete = evaluation_id in source.complete_evaluation_record_ids
        entries.append(
            TransitionSessionEntry(
                entry_id=f"v3_9_session_entry_{source.input_id}_{offset}",
                input_id=source.input_id,
                evaluation_record_id=evaluation_id,
                entry_status="complete" if complete else "incomplete_visible",
                evidence_reference=_reference_or_missing(source.session_evidence_ids, "missing_session_evidence_fail_visible"),
                provenance_reference=_reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible"),
                continuity_reference=_reference_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
                deterministic_order=deterministic_order_base + offset,
                replay_safe=True,
                rollback_safe=True,
                provenance_preserved=True,
                explainability_safe=True,
                immutable_entry=True,
                hidden=False,
            )
        )
    return tuple(entries)


def _findings_from_input(
    source: TransitionSessionInput,
    classification: str,
    severity: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionSessionFinding, ...]:
    finding_specs: list[tuple[str, str, str, str]] = []
    if classification == SESSION_CLASSIFICATION_COMPLETE:
        finding_specs.extend(
            (
                (SESSION_FINDING_COMPLETENESS, "session_complete", "session completeness verified", "info"),
                (SESSION_FINDING_EVALUATION, "evaluation_records_complete", "evaluation records packaged", "info"),
                (SESSION_FINDING_CONTINUITY, "session_continuity_verified", "session continuity verified", "info"),
                (SESSION_FINDING_PROVENANCE, "session_provenance_verified", "session provenance verified", "info"),
                (SESSION_FINDING_EXPLAINABILITY, "session_explainability_verified", "session explainability verified", "info"),
            )
        )
    for marker in source.partial_success_markers:
        finding_specs.append((SESSION_FINDING_COMPLETENESS, marker, "partial session success marker", "warning"))
    for marker in source.partial_failure_markers:
        finding_specs.append((SESSION_FINDING_MISSING_EVIDENCE, marker, "partial session gap remains visible", "warning"))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        finding_specs.append((SESSION_FINDING_MISSING_EVIDENCE, marker, "missing session evidence finding", "blocked"))
    for marker in source.blocked_markers:
        finding_specs.append((SESSION_FINDING_GOVERNANCE, marker, "blocked session finding", "blocked"))
    for marker in source.governance_policy_ids:
        finding_specs.append((SESSION_FINDING_GOVERNANCE, marker, "governance session finding", "blocked"))
    for marker in source.integrity_policy_ids:
        finding_specs.append((SESSION_FINDING_INTEGRITY, marker, "integrity session finding", "blocked"))
    for marker in source.unsupported_markers:
        finding_specs.append((SESSION_FINDING_UNSUPPORTED, marker, "unsupported session finding", "warning"))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_SESSION_CAPABILITIES and capability not in PROHIBITED_SESSION_CAPABILITIES:
            finding_specs.append((SESSION_FINDING_UNSUPPORTED, capability, "unsupported session capability", "warning"))
    for marker in source.prohibited_markers:
        finding_specs.append((SESSION_FINDING_PROHIBITED, marker, "prohibited session finding", "blocked"))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_SESSION_CAPABILITIES:
            finding_specs.append((SESSION_FINDING_PROHIBITED, capability, "prohibited session capability", "blocked"))
    for marker in source.unknown_markers:
        finding_specs.append((SESSION_FINDING_UNCERTAINTY, marker, "uncertain session finding", "warning"))
    if not finding_specs:
        finding_specs.append((SESSION_FINDING_COMPLETENESS, classification, "session classification finding", severity))
    findings: list[TransitionSessionFinding] = []
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    for offset, (category, marker, message, marker_severity) in enumerate(
        sorted(finding_specs, key=lambda item: (_finding_category_order(item[0]), item[1])),
        start=1,
    ):
        finding_severity = {
            "info": SESSION_SEVERITY_INFO,
            "warning": SESSION_SEVERITY_WARNING,
            "blocked": SESSION_SEVERITY_BLOCKED,
        }[marker_severity]
        findings.append(
            TransitionSessionFinding(
                finding_id=transition_session_finding_id(source.input_id, category, marker),
                input_id=source.input_id,
                finding_category=category,
                classification=classification,
                severity=finding_severity,
                reason=f"{message}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition session finding for {source.input_id}: "
                    f"{message}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
                execution_boundary_violation_detected=category == SESSION_FINDING_PROHIBITED
                and marker in PROHIBITED_SESSION_CAPABILITIES,
                non_execution_confirmation=True,
            )
        )
    return tuple(findings)


def _continuity_from_input(source: TransitionSessionInput) -> TransitionSessionContinuity:
    return TransitionSessionContinuity(
        continuity_id=f"v3_9_session_continuity_{source.input_id}",
        input_id=source.input_id,
        replay_continuity_ids=_references_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        rollback_continuity_ids=_references_or_missing(source.rollback_continuity_ids, "missing_rollback_continuity_fail_visible"),
        provenance_continuity_ids=_references_or_missing(source.provenance_continuity_ids, "missing_provenance_continuity_fail_visible"),
        explainability_continuity_ids=_references_or_missing(source.explainability_continuity_ids, "missing_explainability_continuity_fail_visible"),
        evidence_continuity_ids=_references_or_missing(source.session_evidence_ids, "missing_session_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_session_hash",
    )


def _evidence_from_input(
    source: TransitionSessionInput,
    evidence_id: str,
    entries: tuple[TransitionSessionEntry, ...],
    findings: tuple[TransitionSessionFinding, ...],
    continuity: TransitionSessionContinuity,
) -> TransitionSessionEvidence:
    continuity_ids = (
        *continuity.replay_continuity_ids,
        *continuity.rollback_continuity_ids,
        *continuity.provenance_continuity_ids,
        *continuity.explainability_continuity_ids,
        *continuity.evidence_continuity_ids,
    )
    return TransitionSessionEvidence(
        evidence_id=evidence_id,
        input_id=source.input_id,
        session_id=source.session_id or "missing_session_identity_fail_visible",
        session_evidence_ids=_references_or_missing(source.session_evidence_ids, "missing_session_evidence_fail_visible"),
        evaluation_entry_ids=tuple(entry.entry_id for entry in entries),
        provenance_reference_ids=_references_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible"),
        continuity_reference_ids=continuity_ids,
        finding_ids=tuple(finding.finding_id for finding in findings),
        deterministic_hash_reference="v3_9_transition_session_hash",
    )


def _visibility_from_input(
    source: TransitionSessionInput,
    classification: str,
    reason: str,
    evidence: TransitionSessionEvidence,
    continuity: TransitionSessionContinuity,
) -> TransitionSessionVisibility:
    non_complete = classification != SESSION_CLASSIFICATION_COMPLETE
    return TransitionSessionVisibility(
        visibility_id=f"v3_9_session_visibility_{source.input_id}",
        input_id=source.input_id,
        classification=classification,
        visibility_status=SESSION_VISIBILITY_FAIL_VISIBLE if non_complete else SESSION_VISIBILITY_VISIBLE,
        reason=reason,
        deterministic_evidence_reference=evidence.evidence_id,
        provenance_reference=evidence.provenance_reference_ids[0],
        continuity_reference=continuity.continuity_id,
        explainability_message=(
            f"{classification} transition session visibility for {source.input_id}: "
            f"{reason}; context: {source.explainability_context}"
        ),
        fail_visible=True,
        hidden=False,
        session_state_visible=True,
    )


def _summary_from_outputs(
    visibilities: tuple[TransitionSessionVisibility, ...],
    findings: tuple[TransitionSessionFinding, ...],
    entries: tuple[TransitionSessionEntry, ...],
) -> TransitionSessionSummary:
    classification_counts = Counter(visibility.classification for visibility in visibilities)
    category_counts = Counter(finding.finding_category for finding in findings)
    counts = {classification: classification_counts.get(classification, 0) for classification in SESSION_CLASSIFICATIONS}
    categories = {category: category_counts.get(category, 0) for category in SESSION_FINDING_CATEGORIES}
    return TransitionSessionSummary(
        summary_id="v3_9_transition_session_summary",
        classification_counts=counts,
        finding_category_counts=categories,
        complete_count=counts[SESSION_CLASSIFICATION_COMPLETE],
        partially_complete_count=counts[SESSION_CLASSIFICATION_PARTIALLY_COMPLETE],
        incomplete_count=counts[SESSION_CLASSIFICATION_INCOMPLETE],
        blocked_count=counts[SESSION_CLASSIFICATION_BLOCKED],
        unsupported_count=counts[SESSION_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[SESSION_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[SESSION_CLASSIFICATION_UNKNOWN],
        session_finding_count=len(findings),
        evaluation_entry_count=len(entries),
        governance_finding_count=categories[SESSION_FINDING_GOVERNANCE],
        uncertainty_finding_count=categories[SESSION_FINDING_UNCERTAINTY],
        missing_evidence_finding_count=categories[SESSION_FINDING_MISSING_EVIDENCE],
        hidden_session_finding_count=sum(1 for finding in findings if finding.hidden),
        execution_boundary_violation_count=sum(
            1 for finding in findings if finding.execution_boundary_violation_detected
        ),
    )


def _missing_required_markers(source: TransitionSessionInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.session_id:
        markers.append("missing_session_identity")
    if not source.evaluation_record_ids:
        markers.append("missing_evaluation_records")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.replay_continuity_ids or not source.rollback_continuity_ids:
        markers.append("missing_continuity_evidence")
    if not source.explainability_continuity_ids:
        markers.append("missing_explainability_evidence")
    if not source.session_evidence_ids:
        markers.append("missing_session_evidence")
    return tuple(sorted(set(markers)))


def _semantics_are_unknown(source: TransitionSessionInput) -> bool:
    values = (source.session_id, source.session_domain)
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
        return SESSION_FINDING_CATEGORIES.index(category)
    except ValueError:
        return len(SESSION_FINDING_CATEGORIES)
