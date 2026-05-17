"""Deterministic non-selective scenario comparison helpers."""

from __future__ import annotations

from itertools import combinations

from .transition_scenario_models import (
    SCENARIO_COMPARISON_CLASSIFICATION_DIFFERENCE,
    SCENARIO_COMPARISON_DIFFERING_EVIDENCE,
    SCENARIO_COMPARISON_MATCHING_EVIDENCE,
    SCENARIO_COMPARISON_MISSING_EVIDENCE,
    SCENARIO_RISK_CATEGORIES,
    TransitionScenarioComparison,
    TransitionScenarioRisk,
    TransitionScenarioVariant,
)


def compare_transition_scenario_variants(
    input_id: str,
    variants: tuple[TransitionScenarioVariant, ...],
    risks: tuple[TransitionScenarioRisk, ...],
    deterministic_order_base: int,
) -> tuple[TransitionScenarioComparison, ...]:
    """Compare variants without selecting, ranking, scoring, or recommending."""

    sorted_variants = tuple(sorted(variants, key=lambda item: (item.deterministic_order, item.variant_id)))
    comparisons: list[TransitionScenarioComparison] = []
    risk_categories = tuple(sorted({risk.risk_category for risk in risks if risk.risk_category in SCENARIO_RISK_CATEGORIES}))
    for offset, (left, right) in enumerate(combinations(sorted_variants, 2), start=1):
        missing_evidence = tuple(
            sorted(
                variant.variant_id
                for variant in (left, right)
                if not variant.deterministic_evidence_available or "missing" in variant.evidence_reference
            )
        )
        matching_evidence = (
            (left.evidence_reference,)
            if left.evidence_reference == right.evidence_reference and not missing_evidence
            else ()
        )
        differing_evidence = tuple(
            sorted({left.evidence_reference, right.evidence_reference})
            if not matching_evidence and not missing_evidence
            else ()
        )
        classification_differences = (
            tuple(sorted({left.classification, right.classification}))
            if left.classification != right.classification
            else ()
        )
        comparison_category = _comparison_category(
            matching_evidence=matching_evidence,
            differing_evidence=differing_evidence,
            missing_evidence=missing_evidence,
            classification_differences=classification_differences,
        )
        comparisons.append(
            TransitionScenarioComparison(
                comparison_id=f"v3_9_scenario_comparison_{input_id}_{offset}",
                input_id=input_id,
                left_variant_id=left.variant_id,
                right_variant_id=right.variant_id,
                comparison_category=comparison_category,
                matching_evidence=matching_evidence,
                differing_evidence=differing_evidence,
                missing_evidence=missing_evidence,
                continuity_differences=(
                    tuple(sorted({left.continuity_reference, right.continuity_reference}))
                    if left.continuity_reference != right.continuity_reference
                    else ()
                ),
                provenance_differences=(
                    tuple(sorted({left.provenance_reference, right.provenance_reference}))
                    if left.provenance_reference != right.provenance_reference
                    else ()
                ),
                explainability_differences=(
                    tuple(sorted({left.explainability_reference, right.explainability_reference}))
                    if left.explainability_reference != right.explainability_reference
                    else ()
                ),
                risk_differences=risk_categories,
                classification_differences=classification_differences,
                deterministic_order=deterministic_order_base + offset,
                descriptive_only=True,
                winner_selected=False,
                recommendation_made=False,
                ranking_assigned=False,
                scoring_assigned=False,
                selection_made=False,
                hidden=False,
            )
        )
    return tuple(comparisons)


def _comparison_category(
    matching_evidence: tuple[str, ...],
    differing_evidence: tuple[str, ...],
    missing_evidence: tuple[str, ...],
    classification_differences: tuple[str, ...],
) -> str:
    if missing_evidence:
        return SCENARIO_COMPARISON_MISSING_EVIDENCE
    if classification_differences:
        return SCENARIO_COMPARISON_CLASSIFICATION_DIFFERENCE
    if differing_evidence:
        return SCENARIO_COMPARISON_DIFFERING_EVIDENCE
    return SCENARIO_COMPARISON_MATCHING_EVIDENCE
