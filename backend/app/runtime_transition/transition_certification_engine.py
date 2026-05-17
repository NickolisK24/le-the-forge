"""Deterministic v3.9 transition continuity certification engine.

Certification is descriptive evidence only. It does not approve, execute,
repair, authorize, mutate, recommend, rank, score, select, route, schedule,
dispatch, traverse, or expose callable behavior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Iterable

from .transition_certification_models import (
    CERTIFICATION_CHOICE_PROHIBITED_CAPABILITIES,
    CERTIFICATION_CLASSIFICATION_BLOCKED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS,
    CERTIFICATION_CLASSIFICATION_INCOMPLETE,
    CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_PROHIBITED,
    CERTIFICATION_CLASSIFICATION_UNKNOWN,
    CERTIFICATION_CLASSIFICATION_UNSUPPORTED,
    CERTIFICATION_CLASSIFICATIONS,
    CERTIFICATION_FINDING_CATEGORIES,
    CERTIFICATION_FINDING_CONTINUITY,
    CERTIFICATION_FINDING_EXPLAINABILITY,
    CERTIFICATION_FINDING_GOVERNANCE,
    CERTIFICATION_FINDING_HIDDEN_BEHAVIOR,
    CERTIFICATION_FINDING_INTEGRITY,
    CERTIFICATION_FINDING_MISSING_EVIDENCE,
    CERTIFICATION_FINDING_NON_EXECUTION,
    CERTIFICATION_FINDING_NON_MUTATION,
    CERTIFICATION_FINDING_NON_RRSS,
    CERTIFICATION_FINDING_PROHIBITED,
    CERTIFICATION_FINDING_PROVENANCE,
    CERTIFICATION_FINDING_REPLAY,
    CERTIFICATION_FINDING_ROLLBACK,
    CERTIFICATION_FINDING_UNCERTAINTY,
    CERTIFICATION_FINDING_UNSUPPORTED,
    CERTIFICATION_FINDING_VISIBILITY,
    CERTIFICATION_GUARANTEE_AGGREGATION,
    CERTIFICATION_GUARANTEE_BOUNDARY,
    CERTIFICATION_GUARANTEE_CATEGORIES,
    CERTIFICATION_GUARANTEE_COMPATIBILITY,
    CERTIFICATION_GUARANTEE_EVALUATION,
    CERTIFICATION_GUARANTEE_EXPLAINABILITY,
    CERTIFICATION_GUARANTEE_FOUNDATION,
    CERTIFICATION_GUARANTEE_INTEGRITY,
    CERTIFICATION_GUARANTEE_NON_EXECUTION,
    CERTIFICATION_GUARANTEE_NON_MUTATION,
    CERTIFICATION_GUARANTEE_NON_RRSS,
    CERTIFICATION_GUARANTEE_PROVENANCE,
    CERTIFICATION_GUARANTEE_REPLAY,
    CERTIFICATION_GUARANTEE_ROLLBACK,
    CERTIFICATION_GUARANTEE_SCENARIO,
    CERTIFICATION_GUARANTEE_SESSION,
    CERTIFICATION_GUARANTEE_VISIBILITY,
    CERTIFICATION_VISIBILITY_CAPABILITY_LEAKAGE,
    CERTIFICATION_VISIBILITY_CATEGORIES,
    CERTIFICATION_VISIBILITY_CERTIFICATION_STATUS,
    CERTIFICATION_VISIBILITY_CONTINUITY,
    CERTIFICATION_VISIBILITY_FAIL_VISIBLE,
    CERTIFICATION_VISIBILITY_GOVERNANCE,
    CERTIFICATION_VISIBILITY_HIDDEN_BEHAVIOR,
    CERTIFICATION_VISIBILITY_INTEGRITY,
    CERTIFICATION_VISIBILITY_MISSING_EVIDENCE,
    CERTIFICATION_VISIBILITY_NON_EXECUTION,
    CERTIFICATION_VISIBILITY_NON_MUTATION,
    CERTIFICATION_VISIBILITY_NON_RRSS,
    CERTIFICATION_VISIBILITY_PROHIBITED,
    CERTIFICATION_VISIBILITY_UNKNOWN,
    CERTIFICATION_VISIBILITY_UNSUPPORTED,
    PROHIBITED_CERTIFICATION_CAPABILITIES,
    REQUIRED_CERTIFICATION_DOMAINS,
    SUPPORTED_CERTIFICATION_CAPABILITIES,
    TransitionCertificationContinuity,
    TransitionCertificationEvidence,
    TransitionCertificationFinding,
    TransitionCertificationGuarantee,
    TransitionCertificationInput,
    TransitionCertificationReport,
    TransitionCertificationSummary,
    TransitionCertificationVisibility,
    V3_9_TRANSITION_CERTIFICATION_REPORT_BLOCKED,
    V3_9_TRANSITION_CERTIFICATION_REPORT_STABLE,
    transition_certification_finding_id,
    transition_certification_guarantee_id,
)
from .transition_certification_serialization import (
    hash_transition_certification_report,
    hash_transition_certification_summary,
)
from .transition_certification_validation import validate_transition_certification_report
from .transition_integrity_audit import audit_v3_9_transition_integrity
from .transition_integrity_models import TransitionIntegrityReport


FAILURE_HIDDEN_FINDING = "hidden_finding"
FAILURE_HIDDEN_RISK = "hidden_risk"
FAILURE_HIDDEN_NON_SAFE_STATE = "hidden_non_safe_state"
FAILURE_EXECUTION_BOUNDARY_LEAKAGE = "execution_boundary_leakage"
FAILURE_RECOMMENDATION_LEAKAGE = "recommendation_leakage"
FAILURE_RANKING_LEAKAGE = "ranking_leakage"
FAILURE_SCORING_LEAKAGE = "scoring_leakage"
FAILURE_SELECTION_LEAKAGE = "selection_leakage"
FAILURE_MUTATION_LEAKAGE = "mutation_leakage"


def default_transition_certification_inputs(
    integrity_report: TransitionIntegrityReport | None = None,
) -> tuple[TransitionCertificationInput, ...]:
    source = integrity_report or audit_v3_9_transition_integrity()
    evidence_ids = (
        source.source_aggregation_report_id,
        source.source_aggregation_hash,
        source.report_id,
        source.deterministic_integrity_hash,
    )
    provenance_ids = tuple(evidence.evidence_id for evidence in source.evidence_records)
    replay_ids = tuple(continuity.continuity_id for continuity in source.continuities)
    rollback_ids = tuple(continuity.continuity_id for continuity in source.continuities)
    provenance_continuity_ids = tuple(continuity.continuity_id for continuity in source.continuities)
    explainability_ids = tuple(continuity.continuity_id for continuity in source.continuities)
    visibility_ids = tuple(visibility.visibility_id for visibility in source.visibilities)
    base = {
        "certification_domain": "coordination_transition_continuity_certification",
        "required_domain_ids": REQUIRED_CERTIFICATION_DOMAINS,
        "present_domain_ids": REQUIRED_CERTIFICATION_DOMAINS,
        "evidence_ids": evidence_ids,
        "integrity_report_id": source.report_id,
        "integrity_hash": source.deterministic_integrity_hash,
        "provenance_reference_ids": provenance_ids,
        "replay_continuity_ids": replay_ids,
        "rollback_continuity_ids": rollback_ids,
        "provenance_continuity_ids": provenance_continuity_ids,
        "explainability_continuity_ids": explainability_ids,
        "visibility_reference_ids": visibility_ids,
    }
    return (
        TransitionCertificationInput(
            input_id="certified_transition_continuity",
            certification_id="v3_9_certified_transition_continuity",
            requested_capabilities=("deterministic_transition_continuity_certification",),
            explainability_context="all continuity and non-capability guarantees are certified as evidence",
            **base,
        ),
        TransitionCertificationInput(
            input_id="certified_with_warnings_transition_continuity",
            certification_id="v3_9_certified_with_warnings_transition_continuity",
            warning_markers=("expected_fail_visible_warnings", "descriptive_integrity_risks_visible"),
            requested_capabilities=("deterministic_transition_continuity_certification",),
            explainability_context="warnings remain fail-visible and do not silently escalate to certified",
            **base,
        ),
        TransitionCertificationInput(
            input_id="not_certified_transition_continuity",
            certification_id="v3_9_not_certified_transition_continuity",
            failure_markers=(
                FAILURE_HIDDEN_FINDING,
                FAILURE_HIDDEN_RISK,
                FAILURE_HIDDEN_NON_SAFE_STATE,
                "provenance_continuity_failed",
                "replay_continuity_failed",
                "rollback_continuity_failed",
                "explainability_continuity_failed",
                "visibility_continuity_failed",
                "non_execution_continuity_failed",
                FAILURE_EXECUTION_BOUNDARY_LEAKAGE,
                FAILURE_RECOMMENDATION_LEAKAGE,
                FAILURE_RANKING_LEAKAGE,
                FAILURE_SCORING_LEAKAGE,
                FAILURE_SELECTION_LEAKAGE,
                FAILURE_MUTATION_LEAKAGE,
                "deterministic_guarantees_failed",
            ),
            requested_capabilities=("deterministic_transition_continuity_certification",),
            explainability_context="certification failures are visible and not repaired",
            **base,
        ),
        TransitionCertificationInput(
            input_id="blocked_transition_continuity_certification",
            certification_id="v3_9_blocked_transition_continuity_certification",
            blocked_markers=("blocked_by_execution_boundary_preservation",),
            governance_policy_ids=("governance_policy_blocks_certification",),
            integrity_policy_ids=("integrity_preconditions_block_certification",),
            requested_capabilities=("deterministic_transition_continuity_certification",),
            explainability_context="governance and integrity preconditions block certification",
            **base,
        ),
        TransitionCertificationInput(
            input_id="unsupported_transition_continuity_certification",
            certification_id="v3_9_unsupported_transition_continuity_certification",
            unsupported_markers=("unsupported_domain:cross_domain_continuity_certification",),
            requested_capabilities=("cross_domain_transition_continuity_certification",),
            explainability_context="certification domain is outside supported deterministic scope",
            **base,
        ),
        TransitionCertificationInput(
            input_id="prohibited_transition_continuity_certification",
            certification_id="v3_9_prohibited_transition_continuity_certification",
            prohibited_markers=("prohibited_certification_approval_request",),
            requested_capabilities=(
                "orchestration_execution",
                "approval",
                "runtime_mutation",
                "remediation",
                "repair",
                "recommendation",
                "ranking",
                "scoring",
                "selection",
            ),
            explainability_context="certification request attempts to introduce prohibited behavior",
            **base,
        ),
        TransitionCertificationInput(
            input_id="unknown_transition_continuity_certification",
            certification_id="v3_9_unknown_transition_continuity_certification",
            unknown_markers=("ambiguous_certification_semantics",),
            requested_capabilities=("deterministic_transition_continuity_certification",),
            explainability_context="certification semantics cannot be deterministically interpreted",
            **base,
        ),
        TransitionCertificationInput(
            input_id="incomplete_transition_continuity_certification",
            certification_id="",
            certification_domain="coordination_transition_continuity_certification",
            required_domain_ids=REQUIRED_CERTIFICATION_DOMAINS,
            present_domain_ids=(),
            evidence_ids=(),
            integrity_report_id="",
            integrity_hash="",
            provenance_reference_ids=(),
            replay_continuity_ids=(),
            rollback_continuity_ids=(),
            provenance_continuity_ids=(),
            explainability_continuity_ids=(),
            visibility_reference_ids=(),
            incomplete_markers=(
                "missing_required_intelligence_domains",
                "missing_required_certification_evidence",
                "missing_integrity_evidence",
                "missing_provenance_evidence",
                "missing_continuity_evidence",
                "missing_explainability_evidence",
            ),
            requested_capabilities=("deterministic_transition_continuity_certification",),
            explainability_context="required certification evidence is missing",
        ),
    )


def certify_v3_9_transition_continuity(
    certification_inputs: Iterable[TransitionCertificationInput] | None = None,
    integrity_report: TransitionIntegrityReport | None = None,
) -> TransitionCertificationReport:
    source = integrity_report or audit_v3_9_transition_integrity()
    inputs = tuple(
        sorted(
            tuple(certification_inputs or default_transition_certification_inputs(source)),
            key=lambda item: item.input_id,
        )
    )
    findings: list[TransitionCertificationFinding] = []
    guarantees: list[TransitionCertificationGuarantee] = []
    evidence_records: list[TransitionCertificationEvidence] = []
    continuities: list[TransitionCertificationContinuity] = []
    visibilities: list[TransitionCertificationVisibility] = []
    for index, certification_input in enumerate(inputs, start=1):
        classification, reason = _classify_input(certification_input)
        continuity = _continuity_from_input(certification_input)
        input_guarantees = _guarantees_from_input(
            certification_input,
            classification,
            reason,
            evidence_reference=f"v3_9_certification_evidence_{certification_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 100000,
        )
        input_findings = _findings_from_input(
            certification_input,
            classification,
            reason,
            evidence_reference=f"v3_9_certification_evidence_{certification_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 10000,
        )
        input_visibilities = _visibilities_from_input(
            certification_input,
            classification,
            reason,
            evidence_reference=f"v3_9_certification_evidence_{certification_input.input_id}",
            continuity_reference=continuity.continuity_id,
            deterministic_order_base=index * 1000,
        )
        evidence = _evidence_from_input(
            certification_input,
            input_findings,
            input_guarantees,
            input_visibilities,
            continuity,
        )
        findings.extend(input_findings)
        guarantees.extend(input_guarantees)
        evidence_records.append(evidence)
        continuities.append(continuity)
        visibilities.extend(input_visibilities)
    summary = _summary_from_outputs(inputs, tuple(findings), tuple(guarantees), tuple(visibilities))
    summary = replace(summary, deterministic_summary_hash=hash_transition_certification_summary(summary))
    base_report = TransitionCertificationReport(
        report_id="v3_9_transition_continuity_certification_report",
        report_status=V3_9_TRANSITION_CERTIFICATION_REPORT_STABLE,
        source_integrity_report_id=source.report_id,
        source_integrity_hash=source.deterministic_integrity_hash,
        certification_inputs=inputs,
        findings=tuple(sorted(findings, key=lambda item: (item.deterministic_order, item.finding_id))),
        guarantees=tuple(sorted(guarantees, key=lambda item: (item.deterministic_order, item.guarantee_id))),
        evidence_records=tuple(evidence_records),
        continuities=tuple(continuities),
        visibilities=tuple(sorted(visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))),
        summary=summary,
        validation_totals={},
        non_executable=True,
    )
    totals = validate_transition_certification_report(base_report)
    report = replace(
        base_report,
        report_status=V3_9_TRANSITION_CERTIFICATION_REPORT_STABLE
        if totals["valid"]
        else V3_9_TRANSITION_CERTIFICATION_REPORT_BLOCKED,
        validation_totals=totals,
    )
    return replace(report, deterministic_certification_hash=hash_transition_certification_report(report))


def _classify_input(source: TransitionCertificationInput) -> tuple[str, str]:
    prohibited_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability in PROHIBITED_CERTIFICATION_CAPABILITIES
    )
    if source.prohibited_markers or prohibited_capabilities:
        markers = tuple(sorted((*source.prohibited_markers, *prohibited_capabilities)))
        return (
            CERTIFICATION_CLASSIFICATION_PROHIBITED,
            "prohibited certification behavior requested: " + ", ".join(markers),
        )
    missing_markers = _missing_required_markers(source)
    if source.incomplete_markers or missing_markers:
        markers = tuple(sorted(set((*source.incomplete_markers, *missing_markers))))
        return (
            CERTIFICATION_CLASSIFICATION_INCOMPLETE,
            "required transition certification evidence is incomplete: " + ", ".join(markers),
        )
    blocked_markers = tuple(sorted((*source.blocked_markers, *source.governance_policy_ids, *source.integrity_policy_ids)))
    if blocked_markers:
        return (
            CERTIFICATION_CLASSIFICATION_BLOCKED,
            "transition continuity certification is blocked: " + ", ".join(blocked_markers),
        )
    unsupported_capabilities = tuple(
        capability
        for capability in sorted(source.requested_capabilities)
        if capability not in SUPPORTED_CERTIFICATION_CAPABILITIES
        and capability not in PROHIBITED_CERTIFICATION_CAPABILITIES
    )
    if source.unsupported_markers or unsupported_capabilities:
        markers = tuple(sorted((*source.unsupported_markers, *unsupported_capabilities)))
        return (
            CERTIFICATION_CLASSIFICATION_UNSUPPORTED,
            "transition continuity certification domain is unsupported: " + ", ".join(markers),
        )
    if source.unknown_markers or _semantics_are_unknown(source):
        markers = tuple(sorted(source.unknown_markers or ("unknown_certification_semantics",)))
        return (
            CERTIFICATION_CLASSIFICATION_UNKNOWN,
            "transition continuity certification cannot be deterministically interpreted: " + ", ".join(markers),
        )
    if source.failure_markers:
        return (
            CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED,
            "transition continuity is not certified due to visible failures: " + ", ".join(sorted(source.failure_markers)),
        )
    if source.warning_markers:
        return (
            CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS,
            "transition continuity is certified with fail-visible warnings: " + ", ".join(sorted(source.warning_markers)),
        )
    return (
        CERTIFICATION_CLASSIFICATION_CERTIFIED,
        "transition continuity is certified as deterministic evidence only",
    )


def _guarantees_from_input(
    source: TransitionCertificationInput,
    classification: str,
    reason: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionCertificationGuarantee, ...]:
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    guarantees: list[TransitionCertificationGuarantee] = []
    failed_categories = _failed_guarantee_categories(source)
    for offset, category in enumerate(CERTIFICATION_GUARANTEE_CATEGORIES, start=1):
        preserved = category not in failed_categories
        guarantees.append(
            TransitionCertificationGuarantee(
                guarantee_id=transition_certification_guarantee_id(source.input_id, category),
                input_id=source.input_id,
                guarantee_category=category,
                classification=classification,
                certification_status="preserved" if preserved else "failed_visible",
                reason=f"{category} guarantee {'preserved' if preserved else 'failed visibly'}: {reason}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} certification guarantee for {source.input_id}: "
                    f"{category}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
                visible=True,
                hidden=False,
                guarantee_preserved=preserved,
            )
        )
    return tuple(guarantees)


def _findings_from_input(
    source: TransitionCertificationInput,
    classification: str,
    reason: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionCertificationFinding, ...]:
    specs: list[tuple[str, str, str]] = []
    if classification == CERTIFICATION_CLASSIFICATION_CERTIFIED:
        specs.extend(
            (
                (CERTIFICATION_FINDING_CONTINUITY, "continuity_certified", "continuity certification finding"),
                (CERTIFICATION_FINDING_PROVENANCE, "provenance_certified", "provenance certification finding"),
                (CERTIFICATION_FINDING_REPLAY, "replay_certified", "replay certification finding"),
                (CERTIFICATION_FINDING_ROLLBACK, "rollback_certified", "rollback certification finding"),
                (CERTIFICATION_FINDING_EXPLAINABILITY, "explainability_certified", "explainability certification finding"),
                (CERTIFICATION_FINDING_VISIBILITY, "visibility_certified", "visibility certification finding"),
                (CERTIFICATION_FINDING_INTEGRITY, "integrity_certified", "integrity certification finding"),
                (CERTIFICATION_FINDING_NON_EXECUTION, "non_execution_certified", "non-execution certification finding"),
                (CERTIFICATION_FINDING_NON_RRSS, "non_recommendation_ranking_scoring_selection_certified", "non-selection certification finding"),
                (CERTIFICATION_FINDING_NON_MUTATION, "non_mutation_certified", "non-mutation certification finding"),
            )
        )
    for marker in source.warning_markers:
        specs.append((CERTIFICATION_FINDING_VISIBILITY, marker, "certification warning finding"))
    for marker in source.failure_markers:
        specs.append((_finding_category_for_failure(marker), marker, "certification failure finding"))
    for marker in source.blocked_markers:
        specs.append((CERTIFICATION_FINDING_GOVERNANCE, marker, "blocked certification finding"))
    for marker in source.governance_policy_ids:
        specs.append((CERTIFICATION_FINDING_GOVERNANCE, marker, "governance certification finding"))
    for marker in source.integrity_policy_ids:
        specs.append((CERTIFICATION_FINDING_INTEGRITY, marker, "integrity certification finding"))
    for marker in source.unsupported_markers:
        specs.append((CERTIFICATION_FINDING_UNSUPPORTED, marker, "unsupported certification finding"))
    for capability in source.requested_capabilities:
        if capability not in SUPPORTED_CERTIFICATION_CAPABILITIES and capability not in PROHIBITED_CERTIFICATION_CAPABILITIES:
            specs.append((CERTIFICATION_FINDING_UNSUPPORTED, capability, "unsupported certification capability"))
    for marker in source.prohibited_markers:
        specs.append((CERTIFICATION_FINDING_PROHIBITED, marker, "prohibited certification finding"))
    for capability in source.requested_capabilities:
        if capability in PROHIBITED_CERTIFICATION_CAPABILITIES:
            specs.append((_finding_category_for_capability(capability), capability, "prohibited certification capability"))
    for marker in source.unknown_markers:
        specs.append((CERTIFICATION_FINDING_UNCERTAINTY, marker, "uncertain certification finding"))
    for marker in tuple(sorted(set((*source.incomplete_markers, *_missing_required_markers(source))))):
        specs.append((CERTIFICATION_FINDING_MISSING_EVIDENCE, marker, "missing certification evidence finding"))
    if not specs:
        specs.append((CERTIFICATION_FINDING_CONTINUITY, classification, reason))
    specs = tuple({(category, marker): (category, marker, message) for category, marker, message in specs}.values())
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    findings: list[TransitionCertificationFinding] = []
    for offset, (category, marker, message) in enumerate(
        sorted(specs, key=lambda item: (_finding_category_order(item[0]), item[1])),
        start=1,
    ):
        findings.append(
            TransitionCertificationFinding(
                finding_id=transition_certification_finding_id(source.input_id, category, marker),
                input_id=source.input_id,
                finding_category=category,
                classification=classification,
                reason=f"{message}: {marker}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} certification finding for {source.input_id}: "
                    f"{message}; marker: {marker}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
            )
        )
    return tuple(findings)


def _visibilities_from_input(
    source: TransitionCertificationInput,
    classification: str,
    reason: str,
    evidence_reference: str,
    continuity_reference: str,
    deterministic_order_base: int,
) -> tuple[TransitionCertificationVisibility, ...]:
    categories = {CERTIFICATION_VISIBILITY_FAIL_VISIBLE, CERTIFICATION_VISIBILITY_CERTIFICATION_STATUS}
    if source.failure_markers:
        categories.add(CERTIFICATION_VISIBILITY_CONTINUITY)
    if source.warning_markers:
        categories.add(CERTIFICATION_VISIBILITY_CONTINUITY)
    if source.failure_markers or source.integrity_policy_ids:
        categories.add(CERTIFICATION_VISIBILITY_INTEGRITY)
    if _failure_count(source, FAILURE_HIDDEN_FINDING) or _failure_count(source, FAILURE_HIDDEN_RISK) or _failure_count(source, FAILURE_HIDDEN_NON_SAFE_STATE):
        categories.add(CERTIFICATION_VISIBILITY_HIDDEN_BEHAVIOR)
    if _failure_count(source, FAILURE_EXECUTION_BOUNDARY_LEAKAGE) or any(
        capability in PROHIBITED_CERTIFICATION_CAPABILITIES for capability in source.requested_capabilities
    ):
        categories.add(CERTIFICATION_VISIBILITY_CAPABILITY_LEAKAGE)
    if _failure_count(source, FAILURE_MUTATION_LEAKAGE) or "runtime_mutation" in source.requested_capabilities:
        categories.add(CERTIFICATION_VISIBILITY_NON_MUTATION)
    if (
        _failure_count(source, FAILURE_RECOMMENDATION_LEAKAGE)
        or _failure_count(source, FAILURE_RANKING_LEAKAGE)
        or _failure_count(source, FAILURE_SCORING_LEAKAGE)
        or _failure_count(source, FAILURE_SELECTION_LEAKAGE)
        or any(capability in CERTIFICATION_CHOICE_PROHIBITED_CAPABILITIES for capability in source.requested_capabilities)
    ):
        categories.add(CERTIFICATION_VISIBILITY_NON_RRSS)
    if _missing_required_markers(source) or source.incomplete_markers:
        categories.add(CERTIFICATION_VISIBILITY_MISSING_EVIDENCE)
    if source.unsupported_markers:
        categories.add(CERTIFICATION_VISIBILITY_UNSUPPORTED)
    if source.prohibited_markers:
        categories.add(CERTIFICATION_VISIBILITY_PROHIBITED)
    if source.unknown_markers:
        categories.add(CERTIFICATION_VISIBILITY_UNKNOWN)
    if source.blocked_markers or source.governance_policy_ids:
        categories.add(CERTIFICATION_VISIBILITY_GOVERNANCE)
    if classification in (CERTIFICATION_CLASSIFICATION_CERTIFIED, CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS):
        categories.add(CERTIFICATION_VISIBILITY_NON_EXECUTION)
    provenance_reference = _reference_or_missing(source.provenance_reference_ids, "missing_provenance_reference_fail_visible")
    visibilities: list[TransitionCertificationVisibility] = []
    for offset, category in enumerate(sorted(categories, key=_visibility_category_order), start=1):
        visibilities.append(
            TransitionCertificationVisibility(
                visibility_id=f"v3_9_certification_visibility_{source.input_id}_{category}",
                input_id=source.input_id,
                visibility_category=category,
                classification=classification,
                reason=f"{category} certification visibility: {reason}",
                evidence_reference=evidence_reference,
                provenance_reference=provenance_reference,
                continuity_reference=continuity_reference,
                explainability_message=(
                    f"{classification} certification visibility for {source.input_id}: "
                    f"{category}; context: {source.explainability_context}"
                ),
                deterministic_order=deterministic_order_base + offset,
            )
        )
    return tuple(visibilities)


def _continuity_from_input(source: TransitionCertificationInput) -> TransitionCertificationContinuity:
    return TransitionCertificationContinuity(
        continuity_id=f"v3_9_certification_continuity_{source.input_id}",
        input_id=source.input_id,
        replay_continuity_ids=_references_or_missing(source.replay_continuity_ids, "missing_replay_continuity_fail_visible"),
        rollback_continuity_ids=_references_or_missing(source.rollback_continuity_ids, "missing_rollback_continuity_fail_visible"),
        provenance_continuity_ids=_references_or_missing(source.provenance_continuity_ids, "missing_provenance_continuity_fail_visible"),
        explainability_continuity_ids=_references_or_missing(source.explainability_continuity_ids, "missing_explainability_continuity_fail_visible"),
        visibility_reference_ids=_references_or_missing(source.visibility_reference_ids, "missing_visibility_reference_fail_visible"),
        evidence_continuity_ids=_references_or_missing(source.evidence_ids, "missing_certification_evidence_fail_visible"),
        deterministic_hash_reference="v3_9_transition_certification_hash",
    )


def _evidence_from_input(
    source: TransitionCertificationInput,
    findings: tuple[TransitionCertificationFinding, ...],
    guarantees: tuple[TransitionCertificationGuarantee, ...],
    visibilities: tuple[TransitionCertificationVisibility, ...],
    continuity: TransitionCertificationContinuity,
) -> TransitionCertificationEvidence:
    continuity_ids = (
        *continuity.replay_continuity_ids,
        *continuity.rollback_continuity_ids,
        *continuity.provenance_continuity_ids,
        *continuity.explainability_continuity_ids,
        *continuity.visibility_reference_ids,
        *continuity.evidence_continuity_ids,
    )
    return TransitionCertificationEvidence(
        evidence_id=f"v3_9_certification_evidence_{source.input_id}",
        input_id=source.input_id,
        certification_id=source.certification_id or "missing_certification_identity_fail_visible",
        source_domain_ids=_references_or_missing(source.present_domain_ids, "missing_source_domain_fail_visible"),
        evidence_ids=_references_or_missing(source.evidence_ids, "missing_certification_evidence_fail_visible"),
        finding_ids=tuple(finding.finding_id for finding in findings),
        guarantee_ids=tuple(guarantee.guarantee_id for guarantee in guarantees),
        visibility_ids=tuple(visibility.visibility_id for visibility in visibilities),
        provenance_reference_ids=_references_or_missing(
            source.provenance_reference_ids,
            "missing_provenance_reference_fail_visible",
        ),
        continuity_reference_ids=continuity_ids,
        deterministic_hash_reference="v3_9_transition_certification_hash",
    )


def _summary_from_outputs(
    inputs: tuple[TransitionCertificationInput, ...],
    findings: tuple[TransitionCertificationFinding, ...],
    guarantees: tuple[TransitionCertificationGuarantee, ...],
    visibilities: tuple[TransitionCertificationVisibility, ...],
) -> TransitionCertificationSummary:
    classification_counts = Counter(_first_classification_for_input(findings, source.input_id) for source in inputs)
    finding_counts = Counter(finding.finding_category for finding in findings)
    guarantee_counts = Counter(guarantee.guarantee_category for guarantee in guarantees)
    visibility_counts = Counter(visibility.visibility_category for visibility in visibilities)
    counts = {classification: classification_counts.get(classification, 0) for classification in CERTIFICATION_CLASSIFICATIONS}
    finding_categories = {category: finding_counts.get(category, 0) for category in CERTIFICATION_FINDING_CATEGORIES}
    guarantee_categories = {category: guarantee_counts.get(category, 0) for category in CERTIFICATION_GUARANTEE_CATEGORIES}
    visibility_categories = {category: visibility_counts.get(category, 0) for category in CERTIFICATION_VISIBILITY_CATEGORIES}
    hidden_finding_count = sum(_failure_count(source, FAILURE_HIDDEN_FINDING) for source in inputs)
    hidden_risk_count = sum(_failure_count(source, FAILURE_HIDDEN_RISK) for source in inputs)
    hidden_non_safe_count = sum(_failure_count(source, FAILURE_HIDDEN_NON_SAFE_STATE) for source in inputs)
    execution_leakage_count = sum(_failure_count(source, FAILURE_EXECUTION_BOUNDARY_LEAKAGE) for source in inputs) + sum(
        1 for source in inputs for capability in source.requested_capabilities if capability in PROHIBITED_CERTIFICATION_CAPABILITIES and capability not in (*CERTIFICATION_CHOICE_PROHIBITED_CAPABILITIES, "runtime_mutation")
    )
    recommendation_count = sum(_failure_count(source, FAILURE_RECOMMENDATION_LEAKAGE) for source in inputs) + sum(
        1 for source in inputs if "recommendation" in source.requested_capabilities
    )
    ranking_count = sum(_failure_count(source, FAILURE_RANKING_LEAKAGE) for source in inputs) + sum(
        1 for source in inputs if "ranking" in source.requested_capabilities
    )
    scoring_count = sum(_failure_count(source, FAILURE_SCORING_LEAKAGE) for source in inputs) + sum(
        1 for source in inputs if "scoring" in source.requested_capabilities
    )
    selection_count = sum(_failure_count(source, FAILURE_SELECTION_LEAKAGE) for source in inputs) + sum(
        1 for source in inputs if "selection" in source.requested_capabilities
    )
    mutation_count = sum(_failure_count(source, FAILURE_MUTATION_LEAKAGE) for source in inputs) + sum(
        1 for source in inputs if "runtime_mutation" in source.requested_capabilities
    )
    return TransitionCertificationSummary(
        summary_id="v3_9_transition_certification_summary",
        classification_counts=counts,
        finding_category_counts=finding_categories,
        guarantee_category_counts=guarantee_categories,
        visibility_category_counts=visibility_categories,
        certified_count=counts[CERTIFICATION_CLASSIFICATION_CERTIFIED],
        certified_with_warnings_count=counts[CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS],
        not_certified_count=counts[CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED],
        blocked_count=counts[CERTIFICATION_CLASSIFICATION_BLOCKED],
        unsupported_count=counts[CERTIFICATION_CLASSIFICATION_UNSUPPORTED],
        prohibited_count=counts[CERTIFICATION_CLASSIFICATION_PROHIBITED],
        unknown_count=counts[CERTIFICATION_CLASSIFICATION_UNKNOWN],
        incomplete_count=counts[CERTIFICATION_CLASSIFICATION_INCOMPLETE],
        certification_finding_count=len(findings),
        certification_guarantee_count=len(guarantees),
        replay_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_REPLAY],
        rollback_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_ROLLBACK],
        provenance_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_PROVENANCE],
        explainability_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_EXPLAINABILITY],
        visibility_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_VISIBILITY],
        integrity_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_INTEGRITY],
        non_execution_continuity_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_NON_EXECUTION],
        recommendation_ranking_scoring_selection_non_capability_guarantee_count=guarantee_categories[
            CERTIFICATION_GUARANTEE_NON_RRSS
        ],
        mutation_non_capability_guarantee_count=guarantee_categories[CERTIFICATION_GUARANTEE_NON_MUTATION],
        hidden_finding_count=hidden_finding_count,
        hidden_risk_count=hidden_risk_count,
        hidden_non_safe_state_count=hidden_non_safe_count,
        execution_boundary_leakage_count=execution_leakage_count,
        recommendation_leakage_count=recommendation_count,
        ranking_leakage_count=ranking_count,
        scoring_leakage_count=scoring_count,
        selection_leakage_count=selection_count,
        mutation_leakage_count=mutation_count,
    )


def _missing_required_markers(source: TransitionCertificationInput) -> tuple[str, ...]:
    markers: list[str] = []
    if not source.certification_id:
        markers.append("missing_certification_identity")
    for domain in tuple(sorted(set(source.required_domain_ids) - set(source.present_domain_ids))):
        markers.append(f"missing_domain:{domain}")
    if not source.evidence_ids:
        markers.append("missing_required_certification_evidence")
    if not source.integrity_report_id or not source.integrity_hash:
        markers.append("missing_integrity_evidence")
    if not source.provenance_reference_ids:
        markers.append("missing_provenance_evidence")
    if not source.replay_continuity_ids or not source.rollback_continuity_ids:
        markers.append("missing_continuity_evidence")
    if not source.explainability_continuity_ids:
        markers.append("missing_explainability_evidence")
    return tuple(sorted(set(markers)))


def _failed_guarantee_categories(source: TransitionCertificationInput) -> set[str]:
    markers = set(source.failure_markers)
    failed: set[str] = set()
    if "replay_continuity_failed" in markers:
        failed.add(CERTIFICATION_GUARANTEE_REPLAY)
    if "rollback_continuity_failed" in markers:
        failed.add(CERTIFICATION_GUARANTEE_ROLLBACK)
    if "provenance_continuity_failed" in markers:
        failed.add(CERTIFICATION_GUARANTEE_PROVENANCE)
    if "explainability_continuity_failed" in markers:
        failed.add(CERTIFICATION_GUARANTEE_EXPLAINABILITY)
    if "visibility_continuity_failed" in markers:
        failed.add(CERTIFICATION_GUARANTEE_VISIBILITY)
    if "non_execution_continuity_failed" in markers or FAILURE_EXECUTION_BOUNDARY_LEAKAGE in markers:
        failed.add(CERTIFICATION_GUARANTEE_NON_EXECUTION)
    if any(marker in markers for marker in (FAILURE_RECOMMENDATION_LEAKAGE, FAILURE_RANKING_LEAKAGE, FAILURE_SCORING_LEAKAGE, FAILURE_SELECTION_LEAKAGE)):
        failed.add(CERTIFICATION_GUARANTEE_NON_RRSS)
    if FAILURE_MUTATION_LEAKAGE in markers:
        failed.add(CERTIFICATION_GUARANTEE_NON_MUTATION)
    if markers:
        failed.add(CERTIFICATION_GUARANTEE_INTEGRITY)
    if _missing_required_markers(source):
        failed.update(CERTIFICATION_GUARANTEE_CATEGORIES)
    return failed


def _finding_category_for_failure(marker: str) -> str:
    if "replay" in marker:
        return CERTIFICATION_FINDING_REPLAY
    if "rollback" in marker:
        return CERTIFICATION_FINDING_ROLLBACK
    if "provenance" in marker:
        return CERTIFICATION_FINDING_PROVENANCE
    if "explainability" in marker:
        return CERTIFICATION_FINDING_EXPLAINABILITY
    if "visibility" in marker:
        return CERTIFICATION_FINDING_VISIBILITY
    if marker in (FAILURE_HIDDEN_FINDING, FAILURE_HIDDEN_RISK, FAILURE_HIDDEN_NON_SAFE_STATE):
        return CERTIFICATION_FINDING_HIDDEN_BEHAVIOR
    if marker == FAILURE_MUTATION_LEAKAGE:
        return CERTIFICATION_FINDING_NON_MUTATION
    if marker in (FAILURE_RECOMMENDATION_LEAKAGE, FAILURE_RANKING_LEAKAGE, FAILURE_SCORING_LEAKAGE, FAILURE_SELECTION_LEAKAGE):
        return CERTIFICATION_FINDING_NON_RRSS
    if marker == FAILURE_EXECUTION_BOUNDARY_LEAKAGE:
        return CERTIFICATION_FINDING_NON_EXECUTION
    return CERTIFICATION_FINDING_INTEGRITY


def _finding_category_for_capability(capability: str) -> str:
    if capability == "runtime_mutation":
        return CERTIFICATION_FINDING_NON_MUTATION
    if capability in CERTIFICATION_CHOICE_PROHIBITED_CAPABILITIES:
        return CERTIFICATION_FINDING_NON_RRSS
    return CERTIFICATION_FINDING_PROHIBITED


def _failure_count(source: TransitionCertificationInput, marker: str) -> int:
    return sum(1 for value in source.failure_markers if value == marker)


def _first_classification_for_input(findings: tuple[TransitionCertificationFinding, ...], input_id: str) -> str:
    for finding in findings:
        if finding.input_id == input_id:
            return finding.classification
    return CERTIFICATION_CLASSIFICATION_UNKNOWN


def _semantics_are_unknown(source: TransitionCertificationInput) -> bool:
    values = (source.certification_id, source.certification_domain)
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
        return CERTIFICATION_FINDING_CATEGORIES.index(category)
    except ValueError:
        return len(CERTIFICATION_FINDING_CATEGORIES)


def _visibility_category_order(category: str) -> int:
    try:
        return CERTIFICATION_VISIBILITY_CATEGORIES.index(category)
    except ValueError:
        return len(CERTIFICATION_VISIBILITY_CATEGORIES)
