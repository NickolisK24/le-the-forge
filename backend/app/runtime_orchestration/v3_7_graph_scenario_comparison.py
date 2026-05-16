"""Deterministic comparison evidence for v3.7 graph planning scenarios."""

from __future__ import annotations

from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_scenario_models import (
    V37GraphScenarioComparisonEvidence,
    V37GraphScenarioVariation,
    export_v3_7_graph_scenario_comparison_evidence,
)


def build_v3_7_graph_scenario_comparison_evidence(
    scenario_id: str,
    variations: tuple[V37GraphScenarioVariation, ...],
    baseline_scenario_reference: str = "v3_7_graph_planning_scenario_baseline",
) -> tuple[V37GraphScenarioComparisonEvidence, ...]:
    variation_ids = tuple(sorted(variation.variation_id for variation in variations))
    comparison_payload = {
        "baseline_scenario_reference": baseline_scenario_reference,
        "comparison_id": "v3_7_graph_scenario_comparison_default",
        "compared_variation_ids": variation_ids,
        "scenario_id": scenario_id,
        "selection_enabled": False,
    }
    return (
        V37GraphScenarioComparisonEvidence(
            comparison_id="v3_7_graph_scenario_comparison_default",
            scenario_id=scenario_id,
            baseline_scenario_reference=baseline_scenario_reference,
            compared_variation_ids=variation_ids,
            compatibility_delta_references=tuple(
                sorted(
                    variation.variation_id
                    for variation in variations
                    if variation.compatibility_classification
                )
            ),
            governance_delta_references=tuple(
                sorted(
                    variation.variation_id
                    for variation in variations
                    if variation.governance_classification
                )
            ),
            evaluation_delta_references=tuple(
                sorted(
                    variation.variation_id
                    for variation in variations
                    if variation.evaluation_classification
                )
            ),
            prohibited_state_delta_references=tuple(
                sorted(
                    variation.variation_id
                    for variation in variations
                    if "prohibited" in {
                        variation.governance_classification,
                        variation.compatibility_classification,
                        variation.evaluation_classification,
                    }
                )
            ),
            unsupported_state_delta_references=tuple(
                sorted(
                    variation.variation_id
                    for variation in variations
                    if "unsupported" in {
                        variation.governance_classification,
                        variation.compatibility_classification,
                        variation.evaluation_classification,
                    }
                )
            ),
            unknown_state_delta_references=tuple(
                sorted(
                    variation.variation_id
                    for variation in variations
                    if "unknown" in {
                        variation.governance_classification,
                        variation.compatibility_classification,
                        variation.evaluation_classification,
                    }
                )
            ),
            continuity_delta_references=tuple(
                sorted(f"{variation.variation_id}:continuity" for variation in variations)
            ),
            provenance_delta_references=tuple(
                sorted(variation.provenance.provenance_id for variation in variations)
            ),
            explainability_delta_references=tuple(
                sorted(f"{variation.variation_id}:explainability" for variation in variations)
            ),
            deterministic_comparison_hash=deterministic_hash(comparison_payload),
            comparison_implies_orchestration_selection=False,
        ),
    )


def validate_v3_7_graph_scenario_comparison_stability(
    comparisons: tuple[V37GraphScenarioComparisonEvidence, ...],
) -> dict[str, Any]:
    first = [export_v3_7_graph_scenario_comparison_evidence(item) for item in comparisons]
    second = [export_v3_7_graph_scenario_comparison_evidence(item) for item in comparisons]
    return {
        "comparison_count": len(comparisons),
        "deterministic_comparison_stable": first == second,
        "comparison_selection_enabled": any(
            comparison.comparison_implies_orchestration_selection for comparison in comparisons
        ),
        "prohibited_delta_count": sum(
            len(comparison.prohibited_state_delta_references) for comparison in comparisons
        ),
        "unsupported_delta_count": sum(
            len(comparison.unsupported_state_delta_references) for comparison in comparisons
        ),
        "unknown_delta_count": sum(
            len(comparison.unknown_state_delta_references) for comparison in comparisons
        ),
    }


def export_v3_7_graph_scenario_comparison_records(
    comparisons: tuple[V37GraphScenarioComparisonEvidence, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_scenario_comparison_evidence(item)
        for item in sorted(comparisons, key=lambda record: record.comparison_id)
    ]
