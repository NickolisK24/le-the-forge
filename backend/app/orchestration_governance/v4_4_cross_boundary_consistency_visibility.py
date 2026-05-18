"""Visibility helpers for v4.4 cross-boundary consistency."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_cross_boundary_consistency_models import (
    CONSISTENCY_STATE_AMBIGUOUS,
    CONSISTENCY_STATE_COMPATIBLE,
    CONSISTENCY_STATE_DEGRADED,
    CONSISTENCY_STATE_INCOMPATIBLE,
    CROSS_BOUNDARY_CONSISTENCY_STATES,
    FAIL_VISIBLE_CROSS_BOUNDARY_CONSISTENCY_STATES,
    CompatibilityConsistencySummary,
    ConsistencyExplainabilityRecord,
    ConsistencyRecord,
    ContinuityConsistencySummary,
    CrossBoundaryConsistencyIntelligence,
    CrossBoundaryDiagnosticRecord,
    MultiBoundaryRelationshipRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_consistency_record_states(records: Iterable[ConsistencyRecord]) -> dict[str, int]:
    counts = Counter(record.consistency_state for record in records)
    return {state: int(counts.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES}


def count_relationship_states(records: Iterable[MultiBoundaryRelationshipRecord]) -> dict[str, int]:
    counts = Counter(record.consistency_state for record in records)
    return {state: int(counts.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES}


def count_compatibility_consistency_states(
    records: Iterable[CompatibilityConsistencySummary],
) -> dict[str, int]:
    counts = Counter(record.consistency_state for record in records)
    return {state: int(counts.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES}


def count_continuity_consistency_states(
    records: Iterable[ContinuityConsistencySummary],
) -> dict[str, int]:
    counts = Counter(record.consistency_state for record in records)
    return {state: int(counts.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES}


def count_combined_consistency_states(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, int]:
    counts = Counter(record.consistency_state for record in intelligence.consistency_records)
    counts.update(record.consistency_state for record in intelligence.relationship_records)
    counts.update(record.consistency_state for record in intelligence.compatibility_consistency)
    counts.update(record.consistency_state for record in intelligence.continuity_consistency)
    return {state: int(counts.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES}


def cross_boundary_consistency_summaries(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "consistency_record_id": record.consistency_record_id,
            "boundary_surface": record.boundary_surface,
            "consistency_state": record.consistency_state,
            "related_boundary_ids": _ordered_ids(record.related_boundary_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "consistency_enforcement_enabled": record.consistency_enforcement_enabled,
            "consistency_auto_resolution_enabled": record.consistency_auto_resolution_enabled,
            "automatic_normalization_enabled": record.automatic_normalization_enabled,
        }
        for record in sorted(
            intelligence.consistency_records,
            key=lambda item: (item.deterministic_order, item.consistency_record_id),
        )
    ]


def relationship_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.relationship_records)
    state_counts = count_relationship_states(records)
    return {
        "relationship_count": len(records),
        "state_counts": state_counts,
        "relationship_ids": _ordered_ids(record.relationship_id for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "runtime_execution_enabled_count": sum(1 for record in records if record.runtime_execution_enabled),
    }


def compatibility_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.compatibility_consistency)
    state_counts = count_compatibility_consistency_states(records)
    return {
        "compatibility_consistency_count": len(records),
        "compatible_count": state_counts[CONSISTENCY_STATE_COMPATIBLE],
        "incompatible_count": state_counts[CONSISTENCY_STATE_INCOMPATIBLE],
        "state_counts": state_counts,
        "compatibility_ids": _ordered_ids(record.compatibility_id for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "authorization_enabled_count": sum(
            1 for record in records if record.orchestration_authorization_enabled
        ),
        "approval_enabled_count": sum(1 for record in records if record.orchestration_approval_enabled),
        "runtime_execution_enabled_count": sum(1 for record in records if record.runtime_execution_enabled),
    }


def incompatibility_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "compatibility_id": record.compatibility_id,
            "source_id": record.source_id,
            "target_id": record.target_id,
            "consistency_state": record.consistency_state,
            "compatibility_reason": record.compatibility_reason,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
        }
        for record in sorted(
            (
                item
                for item in intelligence.compatibility_consistency
                if item.consistency_state == CONSISTENCY_STATE_INCOMPATIBLE
            ),
            key=lambda item: (item.deterministic_order, item.compatibility_id),
        )
    ]


def degraded_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.continuity_consistency)
    state_counts = count_continuity_consistency_states(records)
    return {
        "continuity_consistency_count": len(records),
        "degraded_count": state_counts[CONSISTENCY_STATE_DEGRADED],
        "state_counts": state_counts,
        "continuity_ids": _ordered_ids(record.continuity_id for record in records),
        "fail_visible": all(record.fail_visible for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "mutation_enabled_count": sum(1 for record in records if record.mutation_enabled),
    }


def fail_visible_consistency_ambiguity_summaries(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for record in intelligence.consistency_records:
        if record.consistency_state != CONSISTENCY_STATE_AMBIGUOUS:
            continue
        records.append(
            {
                "record_id": record.consistency_record_id,
                "consistency_state": record.consistency_state,
                "chain_ids": _ordered_ids(record.related_boundary_ids),
                "fail_visible": record.fail_visible,
                "descriptive_only": record.descriptive_only,
            }
        )
    for record in intelligence.relationship_records:
        if record.consistency_state != CONSISTENCY_STATE_AMBIGUOUS:
            continue
        records.append(
            {
                "record_id": record.relationship_id,
                "consistency_state": record.consistency_state,
                "chain_ids": _ordered_ids(record.relationship_chain_ids),
                "fail_visible": record.fail_visible,
                "descriptive_only": record.descriptive_only,
            }
        )
    return records


def provenance_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_consistency
    return {
        "provenance_id": provenance.provenance_id,
        "source_reference_ids": _ordered_ids(provenance.source_reference_ids),
        "source_hash_references": _ordered_ids(provenance.source_hash_references),
        "consistency_reference_ids": _ordered_ids(provenance.consistency_reference_ids),
        "provenance_consistency_visible": provenance.provenance_consistency_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "production_consumption_enabled": provenance.production_consumption_enabled,
    }


def lineage_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    lineage = intelligence.lineage_consistency
    return {
        "lineage_id": lineage.lineage_id,
        "lineage_reference_ids": _ordered_ids(lineage.lineage_reference_ids),
        "lineage_hash_references": _ordered_ids(lineage.lineage_hash_references),
        "consistency_reference_ids": _ordered_ids(lineage.consistency_reference_ids),
        "lineage_consistency_visible": lineage.lineage_consistency_visible,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def governance_safe_consistency_explainability(
    explainability: Iterable[ConsistencyExplainabilityRecord],
) -> dict[str, Any]:
    records = tuple(explainability)
    by_state = Counter(record.consistency_state for record in records)
    return {
        "explainability_count": len(records),
        "state_counts": {state: int(by_state.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES},
        "explainability_ids": _ordered_ids(record.explainability_id for record in records),
        "explainability_first": all(record.explainability_first for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "scoring_enabled_count": sum(1 for record in records if record.scoring_enabled),
    }


def aggregate_cross_boundary_diagnostics(
    diagnostics: Iterable[CrossBoundaryDiagnosticRecord],
) -> dict[str, Any]:
    records = tuple(diagnostics)
    by_state = Counter(record.consistency_state for record in records)
    by_severity = Counter(record.severity for record in records)
    return {
        "diagnostic_count": len(records),
        "state_counts": {state: int(by_state.get(state, 0)) for state in CROSS_BOUNDARY_CONSISTENCY_STATES},
        "severity_counts": {severity: int(by_severity[severity]) for severity in sorted(by_severity)},
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "fail_visible": all(record.fail_visible for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "consistency_auto_resolution_enabled_count": sum(
            1 for record in records if record.consistency_auto_resolution_enabled
        ),
        "automatic_normalization_enabled_count": sum(
            1 for record in records if record.automatic_normalization_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(1 for record in records if record.automatic_repair_enabled),
    }


def validate_required_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    counts = count_combined_consistency_states(intelligence)
    missing_states = [state for state in CROSS_BOUNDARY_CONSISTENCY_STATES if counts[state] <= 0]
    fail_visible_missing = [
        state for state in FAIL_VISIBLE_CROSS_BOUNDARY_CONSISTENCY_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not fail_visible_missing,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": fail_visible_missing,
    }
