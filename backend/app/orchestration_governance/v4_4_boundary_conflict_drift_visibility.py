"""Visibility helpers for v4.4 boundary conflict drift."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_conflict_drift_models import (
    BOUNDARY_CONFLICT_DRIFT_STATES,
    CONFLICT_DRIFT_STATE_AMBIGUOUS,
    CONFLICT_DRIFT_STATE_COMPATIBLE,
    CONFLICT_DRIFT_STATE_DEGRADED,
    CONFLICT_DRIFT_STATE_DRIFTED,
    CONFLICT_DRIFT_STATE_INCOMPATIBLE,
    FAIL_VISIBLE_CONFLICT_DRIFT_STATES,
    BoundaryConflictDriftIntelligence,
    BoundaryDriftRecord,
    CompatibilityEvidenceRecord,
    ConflictDiagnosticRecord,
    ConflictExplainabilityRecord,
    ContinuityDegradationSummary,
    RefinementDivergenceRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_drift_states(records: Iterable[BoundaryDriftRecord]) -> dict[str, int]:
    counts = Counter(record.visibility_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES}


def count_divergence_states(records: Iterable[RefinementDivergenceRecord]) -> dict[str, int]:
    counts = Counter(record.visibility_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES}


def count_compatibility_states(records: Iterable[CompatibilityEvidenceRecord]) -> dict[str, int]:
    counts = Counter(record.compatibility_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES}


def count_combined_conflict_drift_states(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, int]:
    counts = Counter(record.visibility_state for record in intelligence.drift_records)
    counts.update(record.visibility_state for record in intelligence.divergence_records)
    counts.update(record.compatibility_state for record in intelligence.compatibility_evidence)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES}


def governance_drift_summaries(
    intelligence: BoundaryConflictDriftIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "drift_id": record.drift_id,
            "boundary_id": record.boundary_id,
            "drift_type": record.drift_type,
            "visibility_state": record.visibility_state,
            "drift_chain_ids": _ordered_ids(record.drift_chain_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "auto_correction_enabled": record.auto_correction_enabled,
            "conflict_auto_resolution_enabled": record.conflict_auto_resolution_enabled,
        }
        for record in sorted(
            intelligence.drift_records,
            key=lambda item: (item.deterministic_order, item.drift_id),
        )
    ]


def refinement_divergence_summaries(
    intelligence: BoundaryConflictDriftIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "divergence_id": record.divergence_id,
            "source_refinement_id": record.source_refinement_id,
            "divergent_refinement_id": record.divergent_refinement_id,
            "visibility_state": record.visibility_state,
            "divergence_chain_ids": _ordered_ids(record.divergence_chain_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "decision_enabled": record.decision_enabled,
            "optimization_enabled": record.optimization_enabled,
        }
        for record in sorted(
            intelligence.divergence_records,
            key=lambda item: (item.deterministic_order, item.divergence_id),
        )
    ]


def compatibility_summaries(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.compatibility_evidence)
    state_counts = count_compatibility_states(records)
    return {
        "compatibility_evidence_count": len(records),
        "compatible_count": state_counts[CONFLICT_DRIFT_STATE_COMPATIBLE],
        "incompatible_count": state_counts[CONFLICT_DRIFT_STATE_INCOMPATIBLE],
        "state_counts": state_counts,
        "compatibility_ids": _ordered_ids(record.compatibility_id for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "authorization_enabled_count": sum(
            1 for record in records if record.orchestration_authorization_enabled
        ),
        "approval_enabled_count": sum(1 for record in records if record.orchestration_approval_enabled),
        "runtime_execution_enabled_count": sum(
            1 for record in records if record.runtime_execution_enabled
        ),
    }


def incompatibility_summaries(
    intelligence: BoundaryConflictDriftIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "compatibility_id": record.compatibility_id,
            "source_id": record.source_id,
            "target_id": record.target_id,
            "compatibility_state": record.compatibility_state,
            "compatibility_reason": record.compatibility_reason,
            "fail_visible": record.fail_visible,
        }
        for record in sorted(
            (
                item
                for item in intelligence.compatibility_evidence
                if item.compatibility_state == CONFLICT_DRIFT_STATE_INCOMPATIBLE
            ),
            key=lambda item: (item.deterministic_order, item.compatibility_id),
        )
    ]


def continuity_degradation_summaries(
    summaries: Iterable[ContinuityDegradationSummary],
) -> dict[str, Any]:
    summary_tuple = tuple(summaries)
    by_state = Counter(summary.degradation_state for summary in summary_tuple)
    return {
        "degradation_count": len(summary_tuple),
        "degraded_count": int(by_state.get(CONFLICT_DRIFT_STATE_DEGRADED, 0)),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES
        },
        "degradation_ids": _ordered_ids(summary.degradation_id for summary in summary_tuple),
        "fail_visible": all(summary.fail_visible for summary in summary_tuple),
        "descriptive_only": all(summary.descriptive_only for summary in summary_tuple),
        "mutation_enabled_count": sum(1 for summary in summary_tuple if summary.mutation_enabled),
    }


def fail_visible_ambiguity_summaries(
    intelligence: BoundaryConflictDriftIntelligence,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for record in (*intelligence.drift_records, *intelligence.divergence_records):
        if record.visibility_state != CONFLICT_DRIFT_STATE_AMBIGUOUS:
            continue
        record_id = getattr(record, "drift_id", None) or getattr(record, "divergence_id")
        chain_ids = getattr(record, "drift_chain_ids", None) or getattr(record, "divergence_chain_ids")
        records.append(
            {
                "record_id": record_id,
                "visibility_state": record.visibility_state,
                "chain_ids": _ordered_ids(chain_ids),
                "fail_visible": record.fail_visible,
                "descriptive_only": record.descriptive_only,
            }
        )
    for record in intelligence.compatibility_evidence:
        if record.compatibility_state == CONFLICT_DRIFT_STATE_AMBIGUOUS:
            records.append(
                {
                    "record_id": record.compatibility_id,
                    "visibility_state": record.compatibility_state,
                    "chain_ids": _ordered_ids((record.source_id, record.target_id)),
                    "fail_visible": record.fail_visible,
                    "descriptive_only": record.descriptive_only,
                }
            )
    return records


def provenance_degradation_visibility(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_degradation_metadata
    return {
        "provenance_id": provenance.provenance_id,
        "source_reference_ids": _ordered_ids(provenance.source_reference_ids),
        "source_hash_references": _ordered_ids(provenance.source_hash_references),
        "degradation_reference_ids": _ordered_ids(provenance.degradation_reference_ids),
        "provenance_continuity_visible": provenance.provenance_continuity_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "production_consumption_enabled": provenance.production_consumption_enabled,
    }


def lineage_degradation_visibility(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    lineage = intelligence.lineage_degradation_metadata
    return {
        "lineage_id": lineage.lineage_id,
        "lineage_reference_ids": _ordered_ids(lineage.lineage_reference_ids),
        "lineage_hash_references": _ordered_ids(lineage.lineage_hash_references),
        "degradation_reference_ids": _ordered_ids(lineage.degradation_reference_ids),
        "lineage_continuity_visible": lineage.lineage_continuity_visible,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def governance_safe_conflict_explainability(
    explainability: Iterable[ConflictExplainabilityRecord],
) -> dict[str, Any]:
    explainability_tuple = tuple(explainability)
    by_state = Counter(record.visibility_state for record in explainability_tuple)
    return {
        "explainability_count": len(explainability_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES
        },
        "explainability_ids": _ordered_ids(
            record.explainability_id for record in explainability_tuple
        ),
        "explainability_first": all(record.explainability_first for record in explainability_tuple),
        "descriptive_only": all(record.descriptive_only for record in explainability_tuple),
        "recommendation_enabled_count": sum(
            1 for record in explainability_tuple if record.recommendation_enabled
        ),
        "decision_enabled_count": sum(1 for record in explainability_tuple if record.decision_enabled),
    }


def aggregate_conflict_diagnostics(
    diagnostics: Iterable[ConflictDiagnosticRecord],
) -> dict[str, Any]:
    diagnostics_tuple = tuple(diagnostics)
    by_state = Counter(record.visibility_state for record in diagnostics_tuple)
    by_severity = Counter(record.severity for record in diagnostics_tuple)
    return {
        "diagnostic_count": len(diagnostics_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_CONFLICT_DRIFT_STATES
        },
        "severity_counts": {
            severity: int(by_severity[severity]) for severity in sorted(by_severity)
        },
        "diagnostic_ids": _ordered_ids(record.conflict_id for record in diagnostics_tuple),
        "fail_visible": all(record.fail_visible for record in diagnostics_tuple),
        "descriptive_only": all(record.descriptive_only for record in diagnostics_tuple),
        "conflict_auto_resolution_enabled_count": sum(
            1 for record in diagnostics_tuple if record.conflict_auto_resolution_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in diagnostics_tuple if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(
            1 for record in diagnostics_tuple if record.automatic_repair_enabled
        ),
    }


def validate_required_conflict_drift_visibility(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    counts = count_combined_conflict_drift_states(intelligence)
    missing_states = [state for state in BOUNDARY_CONFLICT_DRIFT_STATES if counts[state] <= 0]
    fail_visible_missing = [
        state for state in FAIL_VISIBLE_CONFLICT_DRIFT_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not fail_visible_missing,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": fail_visible_missing,
    }
