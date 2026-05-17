"""Deterministic v3.9 transition intelligence aggregation reasoning.

This module aggregates prior transition evidence into descriptive summaries
only. It does not execute, traverse, route, schedule, dispatch, authorize,
approve, mutate, optimize, recommend, rank, score, select, prioritize, weight,
or expose callable orchestration behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_aggregation_models import (
    AGGREGATION_CHOICE_PROHIBITED_CAPABILITIES,
    AGGREGATION_CLASSIFICATION_AGGREGATED,
    AGGREGATION_CLASSIFICATION_BLOCKED,
    AGGREGATION_CLASSIFICATION_INCOMPLETE,
    AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
    AGGREGATION_CLASSIFICATION_PROHIBITED,
    AGGREGATION_CLASSIFICATION_UNKNOWN,
    AGGREGATION_CLASSIFICATION_UNAGGREGATED,
    AGGREGATION_CLASSIFICATION_UNSUPPORTED,
    AGGREGATION_CLASSIFICATIONS,
    AGGREGATION_FINDING_BOUNDARY,
    AGGREGATION_FINDING_CATEGORIES,
    AGGREGATION_FINDING_COMPATIBILITY,
    AGGREGATION_FINDING_CONTINUITY,
    AGGREGATION_FINDING_EVALUATION,
    AGGREGATION_FINDING_EXPLAINABILITY,
    AGGREGATION_FINDING_FOUNDATION,
    AGGREGATION_FINDING_GOVERNANCE,
    AGGREGATION_FINDING_INTEGRITY,
    AGGREGATION_FINDING_MISSING_EVIDENCE,
    AGGREGATION_FINDING_PROHIBITED,
    AGGREGATION_FINDING_PROVENANCE,
    AGGREGATION_FINDING_SCENARIO,
    AGGREGATION_FINDING_SESSION,
    AGGREGATION_FINDING_UNCERTAINTY,
    AGGREGATION_FINDING_UNSUPPORTED,
    AGGREGATION_FINDING_VISIBILITY,
    AGGREGATION_VISIBILITY_CATEGORIES,
    AGGREGATION_VISIBILITY_CONTINUITY,
    AGGREGATION_VISIBILITY_EXPLAINABILITY,
    AGGREGATION_VISIBILITY_FAIL_VISIBLE,
    AGGREGATION_VISIBILITY_GOVERNANCE,
    AGGREGATION_VISIBILITY_INTEGRITY,
    AGGREGATION_VISIBILITY_MISSING_EVIDENCE,
    AGGREGATION_VISIBILITY_PROHIBITED_STATE,
    AGGREGATION_VISIBILITY_PROVENANCE,
    AGGREGATION_VISIBILITY_SCENARIO_RISK,
    AGGREGATION_VISIBILITY_UNCERTAINTY,
    AGGREGATION_VISIBILITY_UNSUPPORTED_STATE,
    PROHIBITED_AGGREGATION_CAPABILITIES,
    REQUIRED_AGGREGATION_DOMAINS,
    SUPPORTED_AGGREGATION_CAPABILITIES,
    AGGREGATION_SEVERITY_BLOCKED,
    AGGREGATION_SEVERITY_INFO,
    AGGREGATION_SEVERITY_WARNING,
    TransitionAggregationContinuity,
    TransitionAggregationEvidence,
    TransitionAggregationFinding,
    TransitionAggregationInput,
    TransitionAggregationProvenance,
    TransitionAggregationRecord,
    TransitionAggregationReport,
    TransitionAggregationRiskVisibility,
    TransitionAggregationSummary,
    TransitionAggregationVisibility,
    V3_9_TRANSITION_AGGREGATION_REPORT_BLOCKED,
    V3_9_TRANSITION_AGGREGATION_REPORT_STABLE,
    transition_aggregation_finding_id,
)
from .transition_aggregation_serialization import (
    hash_transition_aggregation_report,
    hash_transition_aggregation_summary,
)
from .transition_aggregation_validation import validate_transition_aggregation_report
from .transition_boundary_classifier import classify_v3_9_transition_boundaries
from .transition_compatibility_engine import evaluate_v3_9_transition_compatibility
from .transition_evaluation_engine import evaluate_v3_9_transition_evaluation
from .transition_foundation_continuity import (
    CONTINUITY_TYPE_EXPLAINABILITY,
    CONTINUITY_TYPE_PROVENANCE,
    CONTINUITY_TYPE_REPLAY,
    CONTINUITY_TYPE_ROLLBACK,
)
from .transition_foundation_hashing import deterministic_hash
from .transition_foundation_models import TransitionFoundation, default_v3_9_transition_foundation
from .transition_foundation_serialization import serialize_v3_9_transition_foundation
from .transition_scenario_engine import build_v3_9_transition_scenario
from .transition_session_engine import build_v3_9_transition_session


def default_transition_aggregation_inputs(
    foundation: TransitionFoundation | None = None,
) -> tuple[TransitionAggregationInput, ...]:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    compatibility_report = evaluate_v3_9_transition_compatibility(foundation=source)
    evaluation_report = evaluate_v3_9_transition_evaluation(foundation=source)
    session_report = build_v3_9_transition_session(foundation=source)
    scenario_report = build_v3_9_transition_scenario(foundation=source)
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
    all_evidence_ids = (
        source.identity.transition_id,
        deterministic_hash(serialize_v3_9_transition_foundation(source)),
        boundary_report.boundary_report_id,
        boundary_report.deterministic_boundary_hash,
        compatibility_report.report_id,
        compatibility_report.deterministic_compatibility_hash,
        evaluation_report.report_id,
        evaluation_report.deterministic_evaluation_hash,
        session_report.report_id,
        session_report.deterministic_session_hash,
        scenario_report.report_id,
        scenario_report.deterministic_scenario_hash,
    )
    scenario_risk_visibility_ids = tuple(risk.risk_id for risk in scenario_report.risks)
    base = {
        "aggregation_domain": "coordination_transition_intelligence_aggregation",
        "required_domain_ids": REQUIRED_AGGREGATION_DOMAINS,
        "present_domain_ids": REQUIRED_AGGREGATION_DOMAINS,
        "evidence_ids": all_evidence_ids,
        "provenance_reference_ids": provenance_ids,
        "replay_continuity_ids": replay_ids,
        "rollback_continuity_ids": rollback_ids,
        "provenance_continuity_ids": provenance_continuity_ids,
        "explainability_continuity_ids": explainability_ids,
        "risk_visibility_ids": scenario_risk_visibility_ids,
    }
    return (
        TransitionAggregationInput(
            input_id="aggregated_transition_intelligence",
            aggregation_id="v3_9_aggregated_transition_intelligence",
            requested_capabilities=(
                "deterministic_transition_intelligence_aggregation",
                "transition_visibility_aggregation",
                "transition_risk_visibility_aggregation",
            ),
            explainability_context="all required transition intelligence domains and evidence are present",
            **base,
        ),
        TransitionAggregationInput(
            input_id="partially_aggregated_transition_intelligence",
            aggregation_id="v3_9_partially_aggregated_transition_intelligence",
            present_domain_ids=(REQUIRED_AGGREGATION_DOMAINS[0], REQUIRED_AGGREGATION_DOMAINS[1]),
            evidence_ids=all_evidence_ids[:4],
            partial_success_markers=("foundation_and_boundary_domains_present",),
            partial_failure_markers=("missing_compatibility_evidence_visible", "missing_scenario_evidence_visible"),
            requested_capabilities=("deterministic_transition_intelligence_aggregation",),
            explainability_context="some required domains are present while aggregation evidence gaps remain visible",
            **{key: value for key, value in base.items() if key not in ("present_domain_ids", "evidence_ids")},
        ),
        TransitionAggregationInput(
            input_id="unaggregated_transition_intelligence",
            aggregation_id="v3_9_unaggregated_transition_intelligence",
            unaggregated_markers=("aggregation_semantics_outside_deterministic_coverage",),
            requested_capabilities=("deterministic_transition_intelligence_aggregation",),
            explainability_context="aggregation cannot be safely constructed under current deterministic coverage",
            **base,
        ),
        TransitionAggregationInput(
            input_id="blocked_transition_intelligence",
            aggregation_id="v3_9_blocked_transition_intelligence",
            blocked_markers=("blocked_by_execution_boundary_preservation",),
            governance_policy_ids=("governance_policy_blocks_aggregation",),
            integrity_policy_ids=("integrity_policy_blocks_aggregation",),
            requested_capabilities=("deterministic_transition_intelligence_aggregation",),
            explainability_context="governance and integrity policy block aggregation",
            **base,
        ),
        TransitionAggregationInput(
            input_id="unsupported_transition_intelligence",
            aggregation_id="v3_9_unsupported_transition_intelligence",
            unsupported_markers=("unsupported_domain:cross_domain_intelligence_aggregation",),
            requested_capabilities=("cross_domain_transition_intelligence_aggregation",),
            explainability_context="aggregation domain is outside supported deterministic scope",
            **base,
        ),
        TransitionAggregationInput(
            input_id="prohibited_transition_intelligence",
            aggregation_id="v3_9_prohibited_transition_intelligence",
            prohibited_markers=("prohibited_aggregation_execution_request",),
            requested_capabilities=(
                "orchestration_execution",
                "routing",
                "runtime_mutation",
                "recommendation",
                "ranking",
                "scoring",
                "selection",
            ),
            explainability_context="aggregation request attempts to introduce prohibited behavior",
            **base,
        ),
        TransitionAggregationInput(
            input_id="unknown_transition_intelligence",
            aggregation_id="v3_9_unknown_transition_intelligence",
            unknown_markers=("ambiguous_aggregation_semantics",),
            requested_capabilities=("deterministic_transition_intelligence_aggregation",),
            explainability_context="aggregation semantics cannot be deterministically interpreted",
            **base,
        ),
        TransitionAggregationInput(
            input_id="incomplete_transition_intelligence",
            aggregation_id="",
            aggregation_domain="coordination_transition_intelligence_aggregation",
            required_domain_ids=REQUIRED_AGGREGATION_DOMAINS,
            present_domain_ids=(),
            evidence_ids=(),
            provenance_reference_ids=(),
            replay_continuity_ids=(),
            rollback_continuity_ids=(),
            provenance_continuity_ids=(),
            explainability_continuity_ids=(),
            risk_visibility_ids=(),
            incomplete_markers=(
                "missing_required_intelligence_domains",
                "missing_required_evidence",
                "missing_provenance_evidence",
                "missing_continuity_evidence",
                "missing_explainability_evidence",
            ),
            requested_capabilities=("deterministic_transition_intelligence_aggregation",),
            explainability_context="required domains, evidence, provenance, continuity, and explainability are missing",
        ),
    )


def build_v3_9_transition_aggregation(
    aggregation_inputs: Iterable[TransitionAggregationInput] | None = None,
    foundation: TransitionFoundation | None = None,
) -> TransitionAggregationReport:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    compatibility_report = evaluate_v3_9_transition_compatibility(foundation=source)
    evaluation_report = evaluate_v3_9_transition_evaluation(foundation=source)
    session_report = build_v3_9_transition_session(foundation=source)
    scenario_report = build_v3_9_transition_scenario(foundation=source)
    inputs = tuple(
        sorted(
            tuple(aggregation_inputs or default_transition_aggregation_inputs(source)),
            key=lambda item: item.input_id,
        )
    )
    records: list[TransitionAggregationRecord] = []
    findings: list[TransitionAggregationFinding] = []
    visibilities: list[TransitionAggregationVisibility] = []
    evidence_records: list[TransitionAggregationEvidence] = []
    continuities: list[TransitionAggregationContinuity] = []
    provenance_records: list[TransitionAggregationProvenance] = []
    risk_visibility_records: list[TransitionAggregationRiskVisibility] = []
    for index, aggregation_input in enumerate(inputs, start=1):
        classification, severity, reason = _classify_input(aggregation_input)
        continuity = _continuity_from_input(aggregation_input)
        provenance = _provenance_from_input(aggregation_input)
        risk_visibility = _risk_visibility_from_input(aggregation_input, index * 1000)
        evidence_id = f"v3_9_aggregation_evidence_{aggregation_input.input_id}"
        input_findings = _findings_from_input(
            aggregation_input,
            classification=classification,
            severity=severity,
            evidence_reference=evidence_id,
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 100000,
        )
        input_visibilities = _visibilities_from_input(
            aggregation_input,
            classification=classification,
            reason=reason,
            evidence_reference=evidence_id,
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 10000,
        )
        evidence = _evidence_from_input(
            aggregation_input,
            evidence_id,
            input_findings,
            input_visibilities,
            continuity,
        )
        record = TransitionAggregationRecord(
            record_id=f"v3_9_aggregation_record_{aggregation_input.input_id}",
            input_id=aggregation_input.input_id,
            aggregation_id=aggregation_input.aggregation_id or "missing_aggregation_identity_fail_visible",
            classification=classification,
            findings=input_findings,
            visibilities=input_visibilities,
            evidence=evidence,
            continuity=continuity,
            provenance=provenance,
            risk_visibility=risk_visibility,
            deterministic_order=index,
            immutable_record=True,
            non_executable=True,
        )
        records.append(record)
        findings.extend(input_findings)
        visibilities.extend(input_visibilities)
        evidence_records.append(evidence)
        continuities.append(continuity)
        provenance_records.append(provenance)
        risk_visibility_records.append(risk_visibility)
    summary = _summary_from_outputs(tuple(records), tuple(findings), tuple(visibilities))
    summary = replace(summary, deterministic_summary_hash=hash_transition_aggregation_summary(summary))
    base_report = TransitionAggregationReport(
        report_id="v3_9_transition_intelligence_aggregation_report",
        report_status=V3_9_TRANSITION_AGGREGATION_REPORT_STABLE,
        source_foundation_id=source.identity.transition_id,
        source_boundary_report_id=boundary_report.boundary_report_id,
        source_compatibility_report_id=compatibility_report.report_id,
        source_evaluation_report_id=evaluation_report.report_id,
        source_session_report_id=session_report.report_id,
        source_scenario_report_id=scenario_report.report_id,
        aggregation_inputs=inputs,
        aggregation_records=tuple(records),
        findings=tuple(sorted(findings, key=lambda item: (item.deterministic_order, item.finding_id))),
        visibilities=tuple(sorted(visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))),
        evidence_records=tuple(evidence_records),
        continuities=tuple(continuities),
        provenance_records=tuple(provenance_records),
        risk_visibility_records=tuple(risk_visibility_records),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_aggregation_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_AGGREGATION_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_AGGREGATION_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_aggregation_hash=hash_transition_aggregation_report(report))


def _classify_input(source: TransitionAggregationInput) -> tuple[str, str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_AGGREGATION_CAPABILITIES
    )
    if source.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_markers, *prohibited_capabilities)))
        return (
            AGGREGATION_CLASSIFICATION_PROHIBITED,
            AGGREGATION_SEVERITY_BLOCKED,
            "prohibited transition aggregation behavior requested: " + ", ".join(markers),
        )
    missing_domains = tuple(sorted(set(source.required_domain_ids) - set(source.present_domain_ids)))
    if source.partial_success_markers and source.partial_failure_markers:
        markers = tuple(sorted((*source.partial_success_markers, *source.partial_failure_markers)))
        return (
            AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
            AGGREGATION_SEVERITY_WARNING,
            "transition aggregation is partially aggregated with visible gaps: " + ", ".join(markers),
        )
    if source.present_domain_ids and missing_domains:
        return (
            AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
            AGGREGATION_SEVERITY_WARNING,
            "transition aggregation is partially aggregated with missing domains: " + ", ".join(missing_domains),
        )
    missing_markers = tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source)))))
    if missing_markers:
        return (
            AGGREGATION_CLASSIFICATION_INCOMPLETE,
            AGGREGATION_SEVERITY_BLOCKED,
            "required transition aggregation evidence is incomplete: " + ", ".join(missing_markers),
        )
    blocked_markers = tuple(sorted((*source.blocked_markers, *source.governance_policy_ids, *source.integrity_policy_ids)))
    if blocked_markers:
        return (
            AGGREGATION_CLASSIFICATION_BLOCKED,
            AGGREGATION_SEVERITY_BLOCKED,
            "transition aggregation is blocked by governance or integrity policy: " + ", ".join(blocked_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_AGGREGATION_CAPABILITIES
        and capability not in PROHIBITED_AGGREGATION_CAPABILITIES
    )
    if source.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_markers, *unsupported_capabilities)))
        return (
            AGGREGATION_CLASSIFICATION_UNSUPPORTED,
            AGGREGATION_SEVERITY_WARNING,
            "transition aggregation domain is unsupported: " + ", ".join(markers),
        )
    if source.unaggregated_markers:
        return (
            AGGREGATION_CLASSIFICATION_UNAGGREGATED,
            AGGREGATION_SEVERITY_WARNING,
            "transition aggregation cannot be deterministically constructed: "
            + ", ".join(sorted(source.unaggregated_markers)),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_aggregation_semantics",)))
        return (
            AGGREGATION_CLASSIFICATION_UNKNOWN,
            AGGREGATION_SEVERITY_WARNING,
            "transition aggregation cannot be deterministically interpreted: " + ", ".join(markers),
        )
    return (
        AGGREGATION_CLASSIFICATION_AGGREGATED,
        AGGREGATION_SEVERITY_INFO,
        "transition intelligence is aggregated for deterministic descriptive summaries only",
    )


def _findings_from_input(
    source: TransitionAggregationInput,
    classification: str,
    severity: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionAggregationFinding, ...]:
    specs: list[tuple[str, str, str, str]] = []
    if classification == AGGREGATION_CLASSIFICATION_AGGREGATED:
        specs.extend(
            (
                (AGGREGATION_FINDING_FOUNDATION, "foundation_evidence_aggregated", "foundation evidence aggregated", "info"),
                (AGGREGATION_FINDING_BOUNDARY, "boundary_evidence_aggregated", "boundary evidence aggregated", "info"),
                (AGGREGATION_FINDING_COMPATIBILITY, "compatibility_evidence_aggregated", "compatibility evidence aggregated", "info"),
                (AGGREGATION_FINDING_EVALUATION, "evaluation_evidence_aggregated", "evaluation evidence aggregated", "info"),
                (AGGREGATION_FINDING_SESSION, "session_evidence_aggregated", "session evidence aggregated", "info"),
                (AGGREGATION_FINDING_SCENARIO, "scenario_evidence_aggregated", "scenario evidence aggregated", "info"),
                (AGGREGATION_FINDING_VISIBILITY, "visibility_evidence_aggregated", "visibility evidence aggregated", "info"),
                (AGGREGATION_FINDING_CONTINUITY, "continuity_evidence_aggregated", "continuity evidence aggregated", "info"),
                (AGGREGATION_FINDING_PROVENANCE, "provenance_evidence_aggregated", "provenance evidence aggregated", "info"),
                (AGGREGATION_FINDING_EXPLAINABILITY, "explainability_evidence_aggregated", "explainability evidence aggregated", "info"),
            )
        )
    for marker in source.partial_success_markers:
        specs.append((AGGREGATION_FINDING_VISIBILITY, marker, "partial aggregation success marker", "warning"))
    for marker in source.partial_failure_markers:
        specs.append((AGGREGATION_FINDING_MISSING_EVIDENCE, marker, "partial aggregation gap remains visible", "warning"))
    for marker in source.unaggregated_markers:
        specs.append((AGGREGATION_FINDING_UNCERTAINTY, marker, "unaggregated transition intelligence finding", "warning"))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        specs.append((AGGREGATION_FINDING_MISSING_EVIDENCE, marker, "missing aggregation evidence finding", "blocked"))
    for marker in source.blocked_markers:
        specs.append((AGGREGATION_FINDING_GOVERNANCE, marker, "blocked aggregation finding", "blocked"))
    for marker in source.governance_policy_ids:
        specs.append((AGGREGATION_FINDING_GOVERNANCE, marker, "governance aggregation finding", "blocked"))
    for marker in source.integrity_policy_ids:
        specs.append((AGGREGATION_FINDING_INTEGRITY, marker, "integrity aggregation finding", "blocked"))
    for marker in source.unsupported_markers:
        specs.append((AGGREGATION_FINDING_UNSUPPORTED, marker, "unsupported aggregation finding", "warning"))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_AGGREGATION_CAPABILITIES and capability not in PROHIBITED_AGGREGATION_CAPABILITIES:
            specs.append((AGGREGATION_FINDING_UNSUPPORTED, capability, "unsupported aggregation capability", "warning"))
    for marker in source.prohibited_markers:
        specs.append((AGGREGATION_FINDING_PROHIBITED, marker, "prohibited aggregation finding", "blocked"))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_AGGREGATION_CAPABILITIES:
            specs.append((AGGREGATION_FINDING_PROHIBITED, capability, "prohibited aggregation capability", "blocked"))
    for marker in source.unknown_markers:
        specs.append((AGGREGATION_FINDING_UNCERTAINTY, marker, "uncertain aggregation finding", "warning"))
    if not specs:
        specs.append((AGGREGATION_FINDING_VISIBILITY, classification, "aggregation classification finding", severity))
    findings: list[TransitionAggregationFinding] = []
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    for offset, (category, marker, message, marker_severity) in enumerate(
        sorted(specs, key=lambda item: (_finding_category_order(item[0]), item[1])),
        start=1,
    ):
        finding_severity = {
            "info": AGGREGATION_SEVERITY_INFO,
            "warning": AGGREGATION_SEVERITY_WARNING,
            "blocked": AGGREGATION_SEVERITY_BLOCKED,
        }[marker_severity]
        findings.append(
            TransitionAggregationFinding(
                finding_id=transition_aggregation_finding_id(source.input_id, category, marker),
                input_id=source.input_id,
                finding_category=category,
                classification=classification,
                severity=finding_severity,
                reason=f"{message}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition aggregation finding for {source.input_id}: "
                    f"{message}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
                execution_boundary_violation_detected=category == AGGREGATION_FINDING_PROHIBITED
                and marker in PROHIBITED_AGGREGATION_CAPABILITIES,
                recommendation_boundary_violation_detected=category == AGGREGATION_FINDING_PROHIBITED
                and marker in AGGREGATION_CHOICE_PROHIBITED_CAPABILITIES,
                non_execution_confirmation=True,
                no_recommendation_confirmation=True,
            )
        )
    return tuple(findings)


def _visibilities_from_input(
    source: TransitionAggregationInput,
    classification: str,
    reason: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionAggregationVisibility, ...]:
    categories = [AGGREGATION_VISIBILITY_FAIL_VISIBLE]
    if classification == AGGREGATION_CLASSIFICATION_AGGREGATED:
        categories.extend(
            (
                AGGREGATION_VISIBILITY_CONTINUITY,
                AGGREGATION_VISIBILITY_PROVENANCE,
                AGGREGATION_VISIBILITY_EXPLAINABILITY,
                AGGREGATION_VISIBILITY_SCENARIO_RISK,
            )
        )
    if source.partial_failure_markers or source.incomplete_markers or _missing_required_markers(source):
        categories.append(AGGREGATION_VISIBILITY_MISSING_EVIDENCE)
    if source.blocked_markers or source.governance_policy_ids:
        categories.append(AGGREGATION_VISIBILITY_GOVERNANCE)
    if source.integrity_policy_ids:
        categories.append(AGGREGATION_VISIBILITY_INTEGRITY)
    if source.unsupported_markers:
        categories.append(AGGREGATION_VISIBILITY_UNSUPPORTED_STATE)
    if source.prohibited_markers or any(
        capability in PROHIBITED_AGGREGATION_CAPABILITIES for capability in source.requested_capabilities
    ):
        categories.append(AGGREGATION_VISIBILITY_PROHIBITED_STATE)
    if source.unknown_markers or source.unaggregated_markers:
        categories.append(AGGREGATION_VISIBILITY_UNCERTAINTY)
    if source.risk_visibility_ids:
        categories.append(AGGREGATION_VISIBILITY_SCENARIO_RISK)
    visibilities: list[TransitionAggregationVisibility] = []
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    for offset, category in enumerate(sorted(set(categories), key=_visibility_category_order), start=1):
        visibilities.append(
            TransitionAggregationVisibility(
                visibility_id=f"v3_9_aggregation_visibility_{source.input_id}_{category}",
                input_id=source.input_id,
                visibility_category=category,
                classification=classification,
                reason=f"{category} aggregation visibility: {reason}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition aggregation visibility for {source.input_id}: "
                    f"{category}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
                descriptive_only=True,
                prioritization_enabled=False,
                weighting_enabled=False,
                recommendation_enabled=False,
                ranking_enabled=False,
                scoring_enabled=False,
                selection_enabled=False,
            )
        )
    return tuple(visibilities)


def _continuity_from_input(source: TransitionAggregationInput) -> TransitionAggregationContinuity:
    return TransitionAggregationContinuity(
        continuity_id=f"v3_9_aggregation_continuity_{source.input_id}",
        input_id=source.input_id,
        replay_continuity_ids=_references_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        rollback_continuity_ids=_references_or_missing(source.rollback_continuity_ids, "missing_rollback_continuity_fail_visible"),
        provenance_continuity_ids=_references_or_missing(source.provenance_continuity_ids, "missing_provenance_continuity_fail_visible"),
        explainability_continuity_ids=_references_or_missing(source.explainability_continuity_ids, "missing_explainability_continuity_fail_visible"),
        evidence_continuity_ids=_references_or_missing(source.evidence_ids, "missing_aggregation_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_aggregation_hash",
    )


def _provenance_from_input(source: TransitionAggregationInput) -> TransitionAggregationProvenance:
    return TransitionAggregationProvenance(
        provenance_id=f"v3_9_aggregation_provenance_{source.input_id}",
        input_id=source.input_id,
        provenance_reference_ids=_references_or_missing(
            source.provenance_reference_ids,
            "missing_provenance_reference_fail_visible",
        ),
        source_domain_ids=_references_or_missing(source.present_domain_ids, "missing_source_domain_fail_visible"),
        evidence_reference=_reference_or_missing(source.evidence_ids, "missing_aggregation_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_aggregation_hash",
    )


def _risk_visibility_from_input(
    source: TransitionAggregationInput,
    deterministic_order: int,
) -> TransitionAggregationRiskVisibility:
    return TransitionAggregationRiskVisibility(
        risk_visibility_id=f"v3_9_aggregation_risk_visibility_{source.input_id}",
        input_id=source.input_id,
        scenario_risk_visibility_ids=_references_or_missing(
            source.risk_visibility_ids,
            "missing_scenario_risk_visibility_fail_visible",
        ),
        visibility_reference_ids=(
            "aggregation_visibility_fail_visible",
            "aggregation_visibility_scenario_risk",
        ),
        evidence_reference=_reference_or_missing(source.evidence_ids, "missing_aggregation_evidence_fail_visible"),
        provenance_reference=_reference_or_missing(
            source.provenance_reference_ids,
            "missing_provenance_reference_fail_visible",
        ),
        continuity_reference=_reference_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        deterministic_order=deterministic_order,
        descriptive_only=True,
        hidden=False,
        recommendation_enabled=False,
        ranking_enabled=False,
        scoring_enabled=False,
        selection_enabled=False,
    )


def _evidence_from_input(
    source: TransitionAggregationInput,
    evidence_id: str,
    findings: tuple[TransitionAggregationFinding, ...],
    visibilities: tuple[TransitionAggregationVisibility, ...],
    continuity: TransitionAggregationContinuity,
) -> TransitionAggregationEvidence:
    continuity_ids = (
        *continuity.replay_continuity_ids,
        *continuity.rollback_continuity_ids,
        *continuity.provenance_continuity_ids,
        *continuity.explainability_continuity_ids,
        *continuity.evidence_continuity_ids,
    )
    return TransitionAggregationEvidence(
        evidence_id=evidence_id,
        input_id=source.input_id,
        aggregation_id=source.aggregation_id or "missing_aggregation_identity_fail_visible",
        source_domain_ids=_references_or_missing(source.present_domain_ids, "missing_source_domain_fail_visible"),
        evidence_ids=_references_or_missing(source.evidence_ids, "missing_aggregation_evidence_fail_visible"),
        finding_ids=tuple(finding.finding_id for finding in findings),
        visibility_ids=tuple(visibility.visibility_id for visibility in visibilities),
        provenance_reference_ids=_references_or_missing(
            source.provenance_reference_ids,
            "missing_provenance_reference_fail_visible",
        ),
        continuity_reference_ids=continuity_ids,
        risk_visibility_ids=_references_or_missing(
            source.risk_visibility_ids,
            "missing_scenario_risk_visibility_fail_visible",
        ),
        deterministic_hash_reference="v3_9_transition_aggregation_hash",
    )


def _summary_from_outputs(
    records: tuple[TransitionAggregationRecord, ...],
    findings: tuple[TransitionAggregationFinding, ...],
    visibilities: tuple[TransitionAggregationVisibility, ...],
) -> TransitionAggregationSummary:
    classification_counts = Counter(record.classification for record in records)
    finding_counts = Counter(finding.finding_category for finding in findings)
    visibility_counts = Counter(visibility.visibility_category for visibility in visibilities)
    counts = {classification: classification_counts.get(classification, 0) for classification in AGGREGATION_CLASSIFICATIONS}
    finding_categories = {category: finding_counts.get(category, 0) for category in AGGREGATION_FINDING_CATEGORIES}
    visibility_categories = {category: visibility_counts.get(category, 0) for category in AGGREGATION_VISIBILITY_CATEGORIES}
    return TransitionAggregationSummary(
        summary_id="v3_9_transition_aggregation_summary",
        classification_counts=counts,
        finding_category_counts=finding_categories,
        visibility_category_counts=visibility_categories,
        aggregated_count=counts[AGGREGATION_CLASSIFICATION_AGGREGATED],
        partially_aggregated_count=counts[AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED],
        unaggregated_count=counts[AGGREGATION_CLASSIFICATION_UNAGGREGATED],
        blocked_count=counts[AGGREGATION_CLASSIFICATION_BLOCKED],
        unsupported_count=counts[AGGREGATION_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[AGGREGATION_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[AGGREGATION_CLASSIFICATION_UNKNOWN],
        incomplete_count=counts[AGGREGATION_CLASSIFICATION_INCOMPLETE],
        aggregation_finding_count=len(findings),
        aggregation_visibility_count=len(visibilities),
        governance_visibility_count=visibility_categories[AGGREGATION_VISIBILITY_GOVERNANCE],
        integrity_visibility_count=visibility_categories[AGGREGATION_VISIBILITY_INTEGRITY],
        uncertainty_visibility_count=visibility_categories[AGGREGATION_VISIBILITY_UNCERTAINTY],
        missing_evidence_visibility_count=visibility_categories[AGGREGATION_VISIBILITY_MISSING_EVIDENCE],
        hidden_aggregation_finding_count=sum(1 for finding in findings if finding.hidden),
        hidden_visibility_count=sum(1 for visibility in visibilities if visibility.hidden),
        execution_boundary_violation_count=sum(
            1 for finding in findings if finding.execution_boundary_violation_detected
        ),
        recommendation_ranking_scoring_selection_violation_count=sum(
            1 for finding in findings if finding.recommendation_boundary_violation_detected
        ),
    )


def _missing_required_markers(source: TransitionAggregationInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.aggregation_id:
        markers.append("missing_aggregation_identity")
    missing_domains = tuple(sorted(set(source.required_domain_ids) - set(source.present_domain_ids)))
    for domain in missing_domains:
        markers.append(f"missing_domain:{domain}")
    if not source.evidence_ids:
        markers.append("missing_required_evidence")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.replay_continuity_ids or not source.rollback_continuity_ids:
        markers.append("missing_continuity_evidence")
    if not source.explainability_continuity_ids:
        markers.append("missing_explainability_evidence")
    return tuple(sorted(set(markers)))


def _semantics_are_unknown(source: TransitionAggregationInput) -> bool:
    values = (source.aggregation_id, source.aggregation_domain)
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
        return AGGREGATION_FINDING_CATEGORIES.index(category)
    except ValueError:
        return len(AGGREGATION_FINDING_CATEGORIES)


def _visibility_category_order(category: str) -> int:
    try:
        return AGGREGATION_VISIBILITY_CATEGORIES.index(category)
    except ValueError:
        return len(AGGREGATION_VISIBILITY_CATEGORIES)
