"""Deterministic v3.9 transition scenario reasoning.

This module models hypothetical scenario evidence only. It does not execute,
route, schedule, dispatch, traverse, authorize, approve, mutate, optimize,
recommend, rank, score, select, or expose callable orchestration behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_boundary_classifier import classify_v3_9_transition_boundaries
from .transition_compatibility_engine import evaluate_v3_9_transition_compatibility
from .transition_evaluation_engine import evaluate_v3_9_transition_evaluation
from .transition_foundation_continuity import (
    CONTINUITY_TYPE_EXPLAINABILITY,
    CONTINUITY_TYPE_PROVENANCE,
    CONTINUITY_TYPE_REPLAY,
    CONTINUITY_TYPE_ROLLBACK,
)
from .transition_foundation_models import TransitionFoundation, default_v3_9_transition_foundation
from .transition_scenario_comparison import compare_transition_scenario_variants
from .transition_scenario_models import (
    PROHIBITED_SCENARIO_CAPABILITIES,
    SCENARIO_CHOICE_PROHIBITED_CAPABILITIES,
    SCENARIO_CLASSIFICATION_BLOCKED,
    SCENARIO_CLASSIFICATION_INCOMPLETE,
    SCENARIO_CLASSIFICATION_MODELED,
    SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
    SCENARIO_CLASSIFICATION_PROHIBITED,
    SCENARIO_CLASSIFICATION_UNKNOWN,
    SCENARIO_CLASSIFICATION_UNMODELED,
    SCENARIO_CLASSIFICATION_UNSUPPORTED,
    SCENARIO_CLASSIFICATIONS,
    SCENARIO_FINDING_CATEGORIES,
    SCENARIO_FINDING_COMPARISON,
    SCENARIO_FINDING_CONTINUITY,
    SCENARIO_FINDING_EXPLAINABILITY,
    SCENARIO_FINDING_GOVERNANCE,
    SCENARIO_FINDING_INTEGRITY,
    SCENARIO_FINDING_MISSING_EVIDENCE,
    SCENARIO_FINDING_PROHIBITED,
    SCENARIO_FINDING_PROVENANCE,
    SCENARIO_FINDING_RISK_VISIBILITY,
    SCENARIO_FINDING_SESSION_EVIDENCE,
    SCENARIO_FINDING_UNCERTAINTY,
    SCENARIO_FINDING_UNSUPPORTED,
    SCENARIO_FINDING_VARIANT,
    SCENARIO_RISK_CATEGORIES,
    SCENARIO_RISK_CONTINUITY,
    SCENARIO_RISK_EXPLAINABILITY,
    SCENARIO_RISK_GOVERNANCE,
    SCENARIO_RISK_INTEGRITY,
    SCENARIO_RISK_MISSING_EVIDENCE,
    SCENARIO_RISK_PROHIBITED_CAPABILITY,
    SCENARIO_RISK_PROVENANCE,
    SCENARIO_RISK_UNCERTAINTY,
    SCENARIO_RISK_UNSUPPORTED_DOMAIN,
    SCENARIO_SEVERITY_BLOCKED,
    SCENARIO_SEVERITY_INFO,
    SCENARIO_SEVERITY_WARNING,
    SCENARIO_VISIBILITY_FAIL_VISIBLE,
    SCENARIO_VISIBILITY_VISIBLE,
    SUPPORTED_SCENARIO_CAPABILITIES,
    TransitionScenarioContinuity,
    TransitionScenarioEvidence,
    TransitionScenarioFinding,
    TransitionScenarioInput,
    TransitionScenarioRecord,
    TransitionScenarioReport,
    TransitionScenarioRisk,
    TransitionScenarioSummary,
    TransitionScenarioVariant,
    TransitionScenarioVisibility,
    V3_9_TRANSITION_SCENARIO_REPORT_BLOCKED,
    V3_9_TRANSITION_SCENARIO_REPORT_STABLE,
    transition_scenario_finding_id,
    transition_scenario_risk_id,
)
from .transition_scenario_serialization import hash_transition_scenario_report, hash_transition_scenario_summary
from .transition_scenario_validation import validate_transition_scenario_report
from .transition_session_engine import build_v3_9_transition_session


def default_transition_scenario_inputs(
    foundation: TransitionFoundation | None = None,
) -> tuple[TransitionScenarioInput, ...]:
    source = foundation or default_v3_9_transition_foundation()
    session_report = build_v3_9_transition_session(foundation=source)
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
    session_evidence_ids = (
        session_report.report_id,
        session_report.deterministic_session_hash,
        *(evidence.evidence_id for evidence in session_report.evidence_records),
    )
    base = {
        "scenario_domain": "coordination_transition_scenario",
        "session_evidence_ids": session_evidence_ids,
        "provenance_reference_ids": provenance_ids,
        "replay_continuity_ids": replay_ids,
        "rollback_continuity_ids": rollback_ids,
        "provenance_continuity_ids": provenance_continuity_ids,
        "explainability_continuity_ids": explainability_ids,
    }
    return (
        TransitionScenarioInput(
            input_id="modeled_transition_scenario",
            scenario_id="v3_9_modeled_transition_scenario",
            scenario_variant_ids=("baseline_hypothetical_variant", "continuity_preserved_hypothetical_variant"),
            modeled_variant_ids=("baseline_hypothetical_variant", "continuity_preserved_hypothetical_variant"),
            variant_evidence_ids=("scenario_evidence_baseline_variant", "scenario_evidence_continuity_variant"),
            comparison_variant_pairs=("baseline_hypothetical_variant|continuity_preserved_hypothetical_variant",),
            requested_capabilities=(
                "deterministic_transition_scenario_modeling",
                "scenario_comparison_evidence",
                "scenario_risk_visibility",
            ),
            explainability_context="scenario identity, session evidence, variants, continuity, and provenance are present",
            **base,
        ),
        TransitionScenarioInput(
            input_id="partially_modeled_transition_scenario",
            scenario_id="v3_9_partially_modeled_transition_scenario",
            scenario_variant_ids=("modeled_partial_variant", "missing_evidence_partial_variant"),
            modeled_variant_ids=("modeled_partial_variant",),
            variant_evidence_ids=("scenario_evidence_modeled_partial_variant",),
            partial_success_markers=("modeled_variant_present",),
            partial_failure_markers=(
                "missing_variant_evidence_visible",
                "continuity_difference_visible",
                "provenance_difference_visible",
                "explainability_difference_visible",
            ),
            comparison_variant_pairs=("modeled_partial_variant|missing_evidence_partial_variant",),
            requested_capabilities=("deterministic_transition_scenario_modeling", "scenario_risk_visibility"),
            explainability_context="one scenario variant is modeled while visible evidence gaps remain",
            **base,
        ),
        TransitionScenarioInput(
            input_id="unmodeled_transition_scenario",
            scenario_id="v3_9_unmodeled_transition_scenario",
            scenario_variant_ids=("unmodeled_hypothetical_variant",),
            modeled_variant_ids=(),
            variant_evidence_ids=("scenario_evidence_unmodeled_reference",),
            unmodeled_markers=("scenario_semantics_outside_deterministic_coverage",),
            requested_capabilities=("deterministic_transition_scenario_modeling",),
            explainability_context="scenario cannot be deterministically modeled under current scope",
            **base,
        ),
        TransitionScenarioInput(
            input_id="blocked_transition_scenario",
            scenario_id="v3_9_blocked_transition_scenario",
            scenario_variant_ids=("blocked_hypothetical_variant",),
            modeled_variant_ids=("blocked_hypothetical_variant",),
            variant_evidence_ids=("scenario_evidence_blocked_variant",),
            blocked_markers=("blocked_by_execution_boundary_preservation",),
            governance_policy_ids=("governance_policy_blocks_scenario",),
            integrity_policy_ids=("integrity_policy_blocks_scenario",),
            requested_capabilities=("deterministic_transition_scenario_modeling",),
            explainability_context="governance and integrity policy block scenario modeling",
            **base,
        ),
        TransitionScenarioInput(
            input_id="unsupported_transition_scenario",
            scenario_id="v3_9_unsupported_transition_scenario",
            scenario_variant_ids=("unsupported_domain_variant",),
            modeled_variant_ids=("unsupported_domain_variant",),
            variant_evidence_ids=("scenario_evidence_unsupported_variant",),
            unsupported_markers=("unsupported_domain:cross_domain_scenario_modeling",),
            requested_capabilities=("cross_domain_transition_scenario_modeling",),
            explainability_context="scenario domain is outside supported deterministic scope",
            **base,
        ),
        TransitionScenarioInput(
            input_id="prohibited_transition_scenario",
            scenario_id="v3_9_prohibited_transition_scenario",
            scenario_variant_ids=("prohibited_capability_variant",),
            modeled_variant_ids=("prohibited_capability_variant",),
            variant_evidence_ids=("scenario_evidence_prohibited_variant",),
            prohibited_markers=("prohibited_scenario_execution_request",),
            requested_capabilities=(
                "orchestration_execution",
                "routing",
                "runtime_mutation",
                "recommendation",
                "ranking",
                "scoring",
                "selection",
            ),
            explainability_context="scenario modeling request attempts to introduce prohibited behavior",
            **base,
        ),
        TransitionScenarioInput(
            input_id="unknown_transition_scenario",
            scenario_id="v3_9_unknown_transition_scenario",
            scenario_variant_ids=("unknown_semantics_variant",),
            modeled_variant_ids=("unknown_semantics_variant",),
            variant_evidence_ids=("scenario_evidence_unknown_variant",),
            unknown_markers=("ambiguous_scenario_semantics",),
            requested_capabilities=("deterministic_transition_scenario_modeling",),
            explainability_context="scenario semantics cannot be deterministically interpreted",
            **base,
        ),
        TransitionScenarioInput(
            input_id="incomplete_transition_scenario",
            scenario_id="",
            scenario_domain="coordination_transition_scenario",
            session_evidence_ids=(),
            scenario_variant_ids=(),
            modeled_variant_ids=(),
            variant_evidence_ids=(),
            provenance_reference_ids=(),
            replay_continuity_ids=(),
            rollback_continuity_ids=(),
            provenance_continuity_ids=(),
            explainability_continuity_ids=(),
            incomplete_markers=(
                "missing_scenario_identity",
                "missing_session_evidence",
                "missing_scenario_variants",
                "missing_provenance_evidence",
                "missing_continuity_evidence",
                "missing_explainability_evidence",
            ),
            requested_capabilities=("deterministic_transition_scenario_modeling",),
            explainability_context="required scenario identity, variants, session evidence, and continuity are missing",
        ),
    )


def build_v3_9_transition_scenario(
    scenario_inputs: Iterable[TransitionScenarioInput] | None = None,
    foundation: TransitionFoundation | None = None,
) -> TransitionScenarioReport:
    source = foundation or default_v3_9_transition_foundation()
    boundary_report = classify_v3_9_transition_boundaries(foundation=source)
    compatibility_report = evaluate_v3_9_transition_compatibility(foundation=source)
    evaluation_report = evaluate_v3_9_transition_evaluation(foundation=source)
    session_report = build_v3_9_transition_session(foundation=source)
    inputs = tuple(
        sorted(
            tuple(scenario_inputs or default_transition_scenario_inputs(source)),
            key=lambda item: item.input_id,
        )
    )
    records: list[TransitionScenarioRecord] = []
    variants: list[TransitionScenarioVariant] = []
    comparisons: list = []
    risks: list[TransitionScenarioRisk] = []
    findings: list[TransitionScenarioFinding] = []
    evidence_records: list[TransitionScenarioEvidence] = []
    continuities: list[TransitionScenarioContinuity] = []
    visibilities: list[TransitionScenarioVisibility] = []
    for index, scenario_input in enumerate(inputs, start=1):
        classification, severity, reason = _classify_input(scenario_input)
        continuity = _continuity_from_input(scenario_input)
        input_variants = _variants_from_input(scenario_input, classification, index * 100)
        input_risks = _risks_from_input(
            scenario_input,
            classification=classification,
            evidence_reference=f"v3_9_scenario_evidence_{scenario_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 1000,
        )
        input_comparisons = compare_transition_scenario_variants(
            scenario_input.input_id,
            input_variants,
            input_risks,
            deterministic_order_base=index * 10000,
        )
        evidence_id = f"v3_9_scenario_evidence_{scenario_input.input_id}"
        input_findings = _findings_from_input(
            scenario_input,
            classification=classification,
            severity=severity,
            evidence_reference=evidence_id,
            continuity_reference=continuity.continuity_id,
            risks=input_risks,
            comparisons=input_comparisons,
            deterministic_order_base=index * 100000,
        )
        evidence = _evidence_from_input(
            scenario_input,
            evidence_id,
            input_variants,
            input_comparisons,
            input_risks,
            input_findings,
            continuity,
        )
        visibility = _visibility_from_input(scenario_input, classification, reason, evidence, continuity)
        record = TransitionScenarioRecord(
            record_id=f"v3_9_scenario_record_{scenario_input.input_id}",
            input_id=scenario_input.input_id,
            scenario_id=scenario_input.scenario_id or "missing_scenario_identity_fail_visible",
            classification=classification,
            variants=input_variants,
            comparisons=input_comparisons,
            risks=input_risks,
            findings=input_findings,
            evidence=evidence,
            continuity=continuity,
            visibility=visibility,
            deterministic_order=index,
            immutable_record=True,
            non_executable=True,
        )
        records.append(record)
        variants.extend(input_variants)
        comparisons.extend(input_comparisons)
        risks.extend(input_risks)
        findings.extend(input_findings)
        evidence_records.append(evidence)
        continuities.append(continuity)
        visibilities.append(visibility)
    summary = _summary_from_outputs(tuple(visibilities), tuple(findings), tuple(variants), tuple(comparisons), tuple(risks))
    summary = replace(summary, deterministic_summary_hash=hash_transition_scenario_summary(summary))
    base_report = TransitionScenarioReport(
        report_id="v3_9_transition_scenario_intelligence_report",
        report_status=V3_9_TRANSITION_SCENARIO_REPORT_STABLE,
        source_foundation_id=source.identity.transition_id,
        source_boundary_report_id=boundary_report.boundary_report_id,
        source_compatibility_report_id=compatibility_report.report_id,
        source_evaluation_report_id=evaluation_report.report_id,
        source_session_report_id=session_report.report_id,
        scenario_inputs=inputs,
        scenario_records=tuple(records),
        variants=tuple(sorted(variants, key=lambda item: (item.deterministic_order, item.variant_id))),
        comparisons=tuple(sorted(comparisons, key=lambda item: (item.deterministic_order, item.comparison_id))),
        risks=tuple(sorted(risks, key=lambda item: (item.deterministic_order, item.risk_id))),
        findings=tuple(sorted(findings, key=lambda item: (item.deterministic_order, item.finding_id))),
        evidence_records=tuple(evidence_records),
        continuities=tuple(continuities),
        visibilities=tuple(visibilities),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_scenario_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_SCENARIO_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_SCENARIO_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_scenario_hash=hash_transition_scenario_report(report))


def _classify_input(source: TransitionScenarioInput) -> tuple[str, str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_SCENARIO_CAPABILITIES
    )
    if source.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_markers, *prohibited_capabilities)))
        return (
            SCENARIO_CLASSIFICATION_PROHIBITED,
            SCENARIO_SEVERITY_BLOCKED,
            "prohibited transition scenario behavior requested: " + ", ".join(markers),
        )
    missing_markers = tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source)))))
    if missing_markers:
        return (
            SCENARIO_CLASSIFICATION_INCOMPLETE,
            SCENARIO_SEVERITY_BLOCKED,
            "required transition scenario evidence is incomplete: " + ", ".join(missing_markers),
        )
    blocked_markers = tuple(sorted((*source.blocked_markers, *source.governance_policy_ids, *source.integrity_policy_ids)))
    if blocked_markers:
        return (
            SCENARIO_CLASSIFICATION_BLOCKED,
            SCENARIO_SEVERITY_BLOCKED,
            "transition scenario is blocked by governance or integrity policy: " + ", ".join(blocked_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_SCENARIO_CAPABILITIES and capability not in PROHIBITED_SCENARIO_CAPABILITIES
    )
    if source.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_markers, *unsupported_capabilities)))
        return (
            SCENARIO_CLASSIFICATION_UNSUPPORTED,
            SCENARIO_SEVERITY_WARNING,
            "transition scenario domain is unsupported: " + ", ".join(markers),
        )
    if source.unmodeled_markers:
        return (
            SCENARIO_CLASSIFICATION_UNMODELED,
            SCENARIO_SEVERITY_WARNING,
            "transition scenario cannot be deterministically modeled: " + ", ".join(sorted(source.unmodeled_markers)),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_scenario_semantics",)))
        return (
            SCENARIO_CLASSIFICATION_UNKNOWN,
            SCENARIO_SEVERITY_WARNING,
            "transition scenario cannot be deterministically interpreted: " + ", ".join(markers),
        )
    all_variants_modeled = set(source.scenario_variant_ids) <= set(source.modeled_variant_ids)
    all_variants_have_evidence = len(source.variant_evidence_ids) >= len(source.scenario_variant_ids)
    if source.partial_success_markers and source.partial_failure_markers:
        markers = tuple(sorted((*source.partial_success_markers, *source.partial_failure_markers)))
        return (
            SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
            SCENARIO_SEVERITY_WARNING,
            "transition scenario is partially modeled with visible gaps: " + ", ".join(markers),
        )
    if source.modeled_variant_ids and (not all_variants_modeled or not all_variants_have_evidence):
        return (
            SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
            SCENARIO_SEVERITY_WARNING,
            "transition scenario is partially modeled with visible variant evidence gaps",
        )
    return (
        SCENARIO_CLASSIFICATION_MODELED,
        SCENARIO_SEVERITY_INFO,
        "transition scenario is modeled for deterministic evidence reasoning only",
    )


def _variants_from_input(
    source: TransitionScenarioInput,
    classification: str,
    deterministic_order_base: int,
) -> tuple[TransitionScenarioVariant, ...]:
    variant_ids = source.scenario_variant_ids or ("missing_scenario_variant_fail_visible",)
    evidence_ids = tuple(sorted(source.variant_evidence_ids))
    variants: list[TransitionScenarioVariant] = []
    for offset, variant_id in enumerate(sorted(variant_ids), start=1):
        evidence_reference = _evidence_for_variant(
            variant_id,
            evidence_ids,
            offset,
            total_variant_count=len(variant_ids),
        )
        has_evidence = bool(evidence_reference)
        modeled = variant_id in source.modeled_variant_ids and has_evidence and classification == SCENARIO_CLASSIFICATION_MODELED
        partial_modeled = variant_id in source.modeled_variant_ids and has_evidence
        variants.append(
            TransitionScenarioVariant(
                variant_id=f"v3_9_scenario_variant_{source.input_id}_{variant_id}",
                input_id=source.input_id,
                variant_label=variant_id,
                classification=SCENARIO_CLASSIFICATION_MODELED
                if modeled or partial_modeled
                else "variant_evidence_visible_non_modeled",
                evidence_reference=evidence_reference if has_evidence else "missing_variant_evidence_fail_visible",
                provenance_reference=_reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible"),
                continuity_reference=_reference_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
                explainability_reference=_reference_or_missing(
                    source.explainability_continuity_ids,
                    "missing_explainability_continuity_fail_visible",
                ),
                deterministic_order=deterministic_order_base + offset,
                deterministic_evidence_available=has_evidence,
                modeled=modeled or partial_modeled,
                replay_safe=True,
                rollback_safe=True,
                provenance_preserved=True,
                explainability_safe=True,
                immutable_variant=True,
                hidden=False,
                recommendation_enabled=False,
                ranking_enabled=False,
                scoring_enabled=False,
                selection_enabled=False,
            )
        )
    return tuple(variants)


def _risks_from_input(
    source: TransitionScenarioInput,
    classification: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionScenarioRisk, ...]:
    risk_specs: list[tuple[str, str, str]] = []
    for marker in source.partial_failure_markers:
        category = SCENARIO_RISK_MISSING_EVIDENCE
        if "continuity" in marker:
            category = SCENARIO_RISK_CONTINUITY
        elif "provenance" in marker:
            category = SCENARIO_RISK_PROVENANCE
        elif "explainability" in marker:
            category = SCENARIO_RISK_EXPLAINABILITY
        risk_specs.append((category, marker, "partial scenario guarantee remains visible"))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        risk_specs.append((SCENARIO_RISK_MISSING_EVIDENCE, marker, "missing scenario evidence risk"))
    for marker in source.unmodeled_markers:
        risk_specs.append((SCENARIO_RISK_UNCERTAINTY, marker, "unmodeled scenario semantics risk"))
    for marker in source.blocked_markers:
        risk_specs.append((SCENARIO_RISK_GOVERNANCE, marker, "blocked scenario risk"))
    for marker in source.governance_policy_ids:
        risk_specs.append((SCENARIO_RISK_GOVERNANCE, marker, "governance scenario risk"))
    for marker in source.integrity_policy_ids:
        risk_specs.append((SCENARIO_RISK_INTEGRITY, marker, "integrity scenario risk"))
    for marker in source.unsupported_markers:
        risk_specs.append((SCENARIO_RISK_UNSUPPORTED_DOMAIN, marker, "unsupported scenario domain risk"))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_SCENARIO_CAPABILITIES and capability not in PROHIBITED_SCENARIO_CAPABILITIES:
            risk_specs.append((SCENARIO_RISK_UNSUPPORTED_DOMAIN, capability, "unsupported scenario capability risk"))
    for marker in source.prohibited_markers:
        risk_specs.append((SCENARIO_RISK_PROHIBITED_CAPABILITY, marker, "prohibited scenario marker risk"))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_SCENARIO_CAPABILITIES:
            risk_specs.append((SCENARIO_RISK_PROHIBITED_CAPABILITY, capability, "prohibited scenario capability risk"))
    for marker in source.unknown_markers:
        risk_specs.append((SCENARIO_RISK_UNCERTAINTY, marker, "uncertain scenario evidence risk"))
    if classification == SCENARIO_CLASSIFICATION_MODELED:
        risk_specs.append((SCENARIO_RISK_EXPLAINABILITY, "descriptive_risk_visibility_only", "scenario risks remain descriptive"))
    risks: list[TransitionScenarioRisk] = []
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    for offset, (category, marker, description) in enumerate(
        sorted(risk_specs, key=lambda item: (_risk_category_order(item[0]), item[1])),
        start=1,
    ):
        risks.append(
            TransitionScenarioRisk(
                risk_id=transition_scenario_risk_id(source.input_id, category, marker),
                input_id=source.input_id,
                risk_category=category,
                classification=classification,
                description=f"{description}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition scenario risk for {source.input_id}: "
                    f"{description}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
                descriptive_only=True,
                score_assigned=False,
                ranking_assigned=False,
                recommendation_made=False,
                selection_made=False,
                execution_boundary_violation_detected=marker in PROHIBITED_SCENARIO_CAPABILITIES,
                recommendation_boundary_violation_detected=marker in SCENARIO_CHOICE_PROHIBITED_CAPABILITIES,
                non_execution_confirmation=True,
            )
        )
    return tuple(risks)


def _findings_from_input(
    source: TransitionScenarioInput,
    classification: str,
    severity: str,
    evidence_reference: str,
    continuity_reference: str,
    risks: tuple[TransitionScenarioRisk, ...],
    comparisons: tuple,
    deterministic_order_base: int,
) -> tuple[TransitionScenarioFinding, ...]:
    finding_specs: list[tuple[str, str, str, str]] = []
    if classification == SCENARIO_CLASSIFICATION_MODELED:
        finding_specs.extend(
            (
                (SCENARIO_FINDING_SESSION_EVIDENCE, "session_evidence_present", "session evidence packaged", "info"),
                (SCENARIO_FINDING_VARIANT, "scenario_variants_modeled", "scenario variants modeled", "info"),
                (SCENARIO_FINDING_COMPARISON, "non_selective_comparison_present", "non-selective scenario comparison recorded", "info"),
                (SCENARIO_FINDING_RISK_VISIBILITY, "descriptive_risk_visibility_present", "descriptive risk visibility recorded", "info"),
                (SCENARIO_FINDING_CONTINUITY, "scenario_continuity_verified", "scenario continuity verified", "info"),
                (SCENARIO_FINDING_PROVENANCE, "scenario_provenance_verified", "scenario provenance verified", "info"),
                (SCENARIO_FINDING_EXPLAINABILITY, "scenario_explainability_verified", "scenario explainability verified", "info"),
            )
        )
    for marker in source.partial_success_markers:
        finding_specs.append((SCENARIO_FINDING_VARIANT, marker, "partial scenario variant marker", "warning"))
    for marker in source.partial_failure_markers:
        finding_specs.append((SCENARIO_FINDING_MISSING_EVIDENCE, marker, "partial scenario gap remains visible", "warning"))
    for marker in source.unmodeled_markers:
        finding_specs.append((SCENARIO_FINDING_UNCERTAINTY, marker, "unmodeled scenario finding", "warning"))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        finding_specs.append((SCENARIO_FINDING_MISSING_EVIDENCE, marker, "missing scenario evidence finding", "blocked"))
    for marker in source.blocked_markers:
        finding_specs.append((SCENARIO_FINDING_GOVERNANCE, marker, "blocked scenario finding", "blocked"))
    for marker in source.governance_policy_ids:
        finding_specs.append((SCENARIO_FINDING_GOVERNANCE, marker, "governance scenario finding", "blocked"))
    for marker in source.integrity_policy_ids:
        finding_specs.append((SCENARIO_FINDING_INTEGRITY, marker, "integrity scenario finding", "blocked"))
    for marker in source.unsupported_markers:
        finding_specs.append((SCENARIO_FINDING_UNSUPPORTED, marker, "unsupported scenario finding", "warning"))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_SCENARIO_CAPABILITIES and capability not in PROHIBITED_SCENARIO_CAPABILITIES:
            finding_specs.append((SCENARIO_FINDING_UNSUPPORTED, capability, "unsupported scenario capability", "warning"))
    for marker in source.prohibited_markers:
        finding_specs.append((SCENARIO_FINDING_PROHIBITED, marker, "prohibited scenario finding", "blocked"))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_SCENARIO_CAPABILITIES:
            finding_specs.append((SCENARIO_FINDING_PROHIBITED, capability, "prohibited scenario capability", "blocked"))
    for marker in source.unknown_markers:
        finding_specs.append((SCENARIO_FINDING_UNCERTAINTY, marker, "uncertain scenario finding", "warning"))
    for risk in risks:
        finding_specs.append((SCENARIO_FINDING_RISK_VISIBILITY, risk.risk_id, "descriptive scenario risk visible", "warning"))
    for comparison in comparisons:
        finding_specs.append((SCENARIO_FINDING_COMPARISON, comparison.comparison_id, "non-selective comparison visible", "info"))
    if not finding_specs:
        finding_specs.append((SCENARIO_FINDING_VARIANT, classification, "scenario classification finding", severity))
    findings: list[TransitionScenarioFinding] = []
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    for offset, (category, marker, message, marker_severity) in enumerate(
        sorted(finding_specs, key=lambda item: (_finding_category_order(item[0]), item[1])),
        start=1,
    ):
        finding_severity = {
            "info": SCENARIO_SEVERITY_INFO,
            "warning": SCENARIO_SEVERITY_WARNING,
            "blocked": SCENARIO_SEVERITY_BLOCKED,
        }[marker_severity]
        findings.append(
            TransitionScenarioFinding(
                finding_id=transition_scenario_finding_id(source.input_id, category, marker),
                input_id=source.input_id,
                finding_category=category,
                classification=classification,
                severity=finding_severity,
                reason=f"{message}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} transition scenario finding for {source.input_id}: "
                    f"{message}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                fail_visible=True,
                hidden=False,
                execution_boundary_violation_detected=category == SCENARIO_FINDING_PROHIBITED
                and marker in PROHIBITED_SCENARIO_CAPABILITIES,
                recommendation_boundary_violation_detected=category == SCENARIO_FINDING_PROHIBITED
                and marker in SCENARIO_CHOICE_PROHIBITED_CAPABILITIES,
                non_execution_confirmation=True,
                no_recommendation_confirmation=True,
            )
        )
    return tuple(findings)


def _continuity_from_input(source: TransitionScenarioInput) -> TransitionScenarioContinuity:
    return TransitionScenarioContinuity(
        continuity_id=f"v3_9_scenario_continuity_{source.input_id}",
        input_id=source.input_id,
        replay_continuity_ids=_references_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        rollback_continuity_ids=_references_or_missing(source.rollback_continuity_ids, "missing_rollback_continuity_fail_visible"),
        provenance_continuity_ids=_references_or_missing(source.provenance_continuity_ids, "missing_provenance_continuity_fail_visible"),
        explainability_continuity_ids=_references_or_missing(source.explainability_continuity_ids, "missing_explainability_continuity_fail_visible"),
        evidence_continuity_ids=_references_or_missing(source.session_evidence_ids, "missing_session_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_scenario_hash",
    )


def _evidence_from_input(
    source: TransitionScenarioInput,
    evidence_id: str,
    variants: tuple[TransitionScenarioVariant, ...],
    comparisons: tuple,
    risks: tuple[TransitionScenarioRisk, ...],
    findings: tuple[TransitionScenarioFinding, ...],
    continuity: TransitionScenarioContinuity,
) -> TransitionScenarioEvidence:
    continuity_ids = (
        *continuity.replay_continuity_ids,
        *continuity.rollback_continuity_ids,
        *continuity.provenance_continuity_ids,
        *continuity.explainability_continuity_ids,
        *continuity.evidence_continuity_ids,
    )
    return TransitionScenarioEvidence(
        evidence_id=evidence_id,
        input_id=source.input_id,
        scenario_id=source.scenario_id or "missing_scenario_identity_fail_visible",
        session_evidence_ids=_references_or_missing(source.session_evidence_ids, "missing_session_evidence_fail_visible"),
        variant_ids=tuple(variant.variant_id for variant in variants),
        comparison_ids=tuple(comparison.comparison_id for comparison in comparisons),
        risk_ids=tuple(risk.risk_id for risk in risks),
        finding_ids=tuple(finding.finding_id for finding in findings),
        provenance_reference_ids=_references_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible"),
        continuity_reference_ids=continuity_ids,
        deterministic_hash_reference="v3_9_transition_scenario_hash",
    )


def _visibility_from_input(
    source: TransitionScenarioInput,
    classification: str,
    reason: str,
    evidence: TransitionScenarioEvidence,
    continuity: TransitionScenarioContinuity,
) -> TransitionScenarioVisibility:
    non_modeled = classification != SCENARIO_CLASSIFICATION_MODELED
    return TransitionScenarioVisibility(
        visibility_id=f"v3_9_scenario_visibility_{source.input_id}",
        input_id=source.input_id,
        classification=classification,
        visibility_status=SCENARIO_VISIBILITY_FAIL_VISIBLE if non_modeled else SCENARIO_VISIBILITY_VISIBLE,
        reason=reason,
        deterministic_evidence_reference=evidence.evidence_id,
        provenance_reference=evidence.provenance_reference_ids[0],
        continuity_reference=continuity.continuity_id,
        explainability_message=(
            f"{classification} transition scenario visibility for {source.input_id}: "
            f"{reason}; context: {source.explainability_context}"
        ),
        fail_visible=True,
        hidden=False,
        scenario_state_visible=True,
    )


def _summary_from_outputs(
    visibilities: tuple[TransitionScenarioVisibility, ...],
    findings: tuple[TransitionScenarioFinding, ...],
    variants: tuple[TransitionScenarioVariant, ...],
    comparisons: tuple,
    risks: tuple[TransitionScenarioRisk, ...],
) -> TransitionScenarioSummary:
    classification_counts = Counter(visibility.classification for visibility in visibilities)
    finding_counts = Counter(finding.finding_category for finding in findings)
    risk_counts = Counter(risk.risk_category for risk in risks)
    counts = {classification: classification_counts.get(classification, 0) for classification in SCENARIO_CLASSIFICATIONS}
    finding_categories = {category: finding_counts.get(category, 0) for category in SCENARIO_FINDING_CATEGORIES}
    risk_categories = {category: risk_counts.get(category, 0) for category in SCENARIO_RISK_CATEGORIES}
    return TransitionScenarioSummary(
        summary_id="v3_9_transition_scenario_summary",
        classification_counts=counts,
        finding_category_counts=finding_categories,
        risk_category_counts=risk_categories,
        modeled_count=counts[SCENARIO_CLASSIFICATION_MODELED],
        partially_modeled_count=counts[SCENARIO_CLASSIFICATION_PARTIALLY_MODELED],
        unmodeled_count=counts[SCENARIO_CLASSIFICATION_UNMODELED],
        blocked_count=counts[SCENARIO_CLASSIFICATION_BLOCKED],
        unsupported_count=counts[SCENARIO_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[SCENARIO_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[SCENARIO_CLASSIFICATION_UNKNOWN],
        incomplete_count=counts[SCENARIO_CLASSIFICATION_INCOMPLETE],
        scenario_finding_count=len(findings),
        scenario_variant_count=len(variants),
        scenario_comparison_count=len(comparisons),
        scenario_risk_count=len(risks),
        governance_risk_count=risk_categories[SCENARIO_RISK_GOVERNANCE],
        uncertainty_risk_count=risk_categories[SCENARIO_RISK_UNCERTAINTY],
        missing_evidence_risk_count=risk_categories[SCENARIO_RISK_MISSING_EVIDENCE],
        hidden_scenario_finding_count=sum(1 for finding in findings if finding.hidden),
        hidden_risk_count=sum(1 for risk in risks if risk.hidden),
        execution_boundary_violation_count=sum(
            1 for finding in findings if finding.execution_boundary_violation_detected
        ),
        recommendation_ranking_scoring_selection_violation_count=sum(
            1 for finding in findings if finding.recommendation_boundary_violation_detected
        ),
    )


def _missing_required_markers(source: TransitionScenarioInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.scenario_id:
        markers.append("missing_scenario_identity")
    if not source.session_evidence_ids:
        markers.append("missing_session_evidence")
    if not source.scenario_variant_ids:
        markers.append("missing_scenario_variants")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.replay_continuity_ids or not source.rollback_continuity_ids:
        markers.append("missing_continuity_evidence")
    if not source.explainability_continuity_ids:
        markers.append("missing_explainability_evidence")
    return tuple(sorted(set(markers)))


def _semantics_are_unknown(source: TransitionScenarioInput) -> bool:
    values = (source.scenario_id, source.scenario_domain)
    return any("unknown" in value.strip().lower() or "ambiguous" in value.strip().lower() for value in values)


def _reference_or_missing(values: tuple[str, ...], missing_reference: str) -> str:
    if values:
        return sorted(values)[0]
    return missing_reference


def _references_or_missing(values: tuple[str, ...], missing_reference: str) -> tuple[str, ...]:
    if values:
        return tuple(sorted(values))
    return (missing_reference,)


def _evidence_for_variant(
    variant_id: str,
    evidence_ids: tuple[str, ...],
    offset: int,
    total_variant_count: int,
) -> str:
    matching = tuple(evidence_id for evidence_id in evidence_ids if variant_id in evidence_id)
    if matching:
        return sorted(matching)[0]
    if len(evidence_ids) == total_variant_count and offset <= len(evidence_ids):
        return evidence_ids[offset - 1]
    return ""


def _finding_category_order(category: str) -> int:
    try:
        return SCENARIO_FINDING_CATEGORIES.index(category)
    except ValueError:
        return len(SCENARIO_FINDING_CATEGORIES)


def _risk_category_order(category: str) -> int:
    try:
        return SCENARIO_RISK_CATEGORIES.index(category)
    except ValueError:
        return len(SCENARIO_RISK_CATEGORIES)
