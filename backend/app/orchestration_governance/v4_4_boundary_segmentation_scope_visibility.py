"""Visibility helpers for v4.4 boundary segmentation scope."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_segmentation_scope_models import (
    BOUNDARY_SEGMENTATION_SCOPE_STATES,
    FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES,
    SEGMENTATION_SCOPE_STATE_AMBIGUOUS,
    SEGMENTATION_SCOPE_STATE_CONFLICTING,
    SEGMENTATION_SCOPE_STATE_COUPLED,
    SEGMENTATION_SCOPE_STATE_DEGRADED,
    SEGMENTATION_SCOPE_STATE_ISOLATED,
    SEGMENTATION_SCOPE_STATE_OVERLAPPING,
    SEGMENTATION_SCOPE_STATE_SCOPED,
    SEGMENTATION_SCOPE_STATE_SEGMENTED,
    SEGMENTATION_SCOPE_STATE_UNSCOPED,
    SEGMENTATION_SCOPE_STATE_UNSEGMENTED,
    BoundaryScopeRecord,
    BoundarySegmentRecord,
    BoundarySegmentationScopeIntelligence,
    ScopeDiagnosticRecord,
    ScopedBoundaryMembershipRecord,
    SegmentContinuityVisibility,
    SegmentRelationshipRecord,
    SegmentationDiagnosticRecord,
    SegmentationExplainabilityRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_segment_states(records: Iterable[BoundarySegmentRecord]) -> dict[str, int]:
    counts = Counter(record.segment_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES}


def count_scope_states(records: Iterable[BoundaryScopeRecord]) -> dict[str, int]:
    counts = Counter(record.scope_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES}


def count_membership_states(records: Iterable[ScopedBoundaryMembershipRecord]) -> dict[str, int]:
    counts = Counter(record.membership_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES}


def count_relationship_states(records: Iterable[SegmentRelationshipRecord]) -> dict[str, int]:
    counts = Counter(record.relationship_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES}


def count_continuity_states(records: Iterable[SegmentContinuityVisibility]) -> dict[str, int]:
    counts = Counter(record.continuity_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES}


def count_combined_segmentation_scope_states(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, int]:
    counts = Counter(record.segment_state for record in intelligence.segment_records)
    counts.update(record.scope_state for record in intelligence.scope_records)
    counts.update(record.membership_state for record in intelligence.membership_records)
    counts.update(record.relationship_state for record in intelligence.relationship_records)
    counts.update(record.continuity_state for record in intelligence.continuity_visibility)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES}


def segmentation_summaries(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "segment_id": record.segment_id,
            "segment_name": record.segment_name,
            "segment_state": record.segment_state,
            "grouped_boundary_ids": _ordered_ids(record.grouped_boundary_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "segmentation_based_routing_enabled": record.segmentation_based_routing_enabled,
            "boundary_group_execution_lane_enabled": record.boundary_group_execution_lane_enabled,
            "routing_execution_enabled": record.routing_execution_enabled,
            "dispatch_execution_enabled": record.dispatch_execution_enabled,
            "scheduling_execution_enabled": record.scheduling_execution_enabled,
        }
        for record in sorted(
            intelligence.segment_records,
            key=lambda item: (item.deterministic_order, item.segment_id),
        )
    ]


def scope_summaries(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "scope_id": record.scope_id,
            "scope_name": record.scope_name,
            "scope_state": record.scope_state,
            "scoped_governance_ids": _ordered_ids(record.scoped_governance_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "scope_based_authorization_enabled": record.scope_based_authorization_enabled,
            "orchestration_authorization_enabled": record.orchestration_authorization_enabled,
            "orchestration_approval_enabled": record.orchestration_approval_enabled,
        }
        for record in sorted(
            intelligence.scope_records,
            key=lambda item: (item.deterministic_order, item.scope_id),
        )
    ]


def scoped_boundary_membership_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.membership_records)
    state_counts = count_membership_states(records)
    return {
        "membership_count": len(records),
        "scoped_count": state_counts[SEGMENTATION_SCOPE_STATE_SCOPED],
        "unscoped_count": state_counts[SEGMENTATION_SCOPE_STATE_UNSCOPED],
        "segmented_count": state_counts[SEGMENTATION_SCOPE_STATE_SEGMENTED],
        "state_counts": state_counts,
        "membership_ids": _ordered_ids(record.membership_id for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "routing_enabled_count": sum(1 for record in records if record.routing_enabled),
        "dispatch_enabled_count": sum(1 for record in records if record.dispatch_enabled),
        "scheduling_enabled_count": sum(1 for record in records if record.scheduling_enabled),
    }


def isolation_coupling_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.relationship_records)
    state_counts = count_relationship_states(records)
    return {
        "relationship_count": len(records),
        "isolated_count": state_counts[SEGMENTATION_SCOPE_STATE_ISOLATED],
        "coupled_count": state_counts[SEGMENTATION_SCOPE_STATE_COUPLED],
        "overlap_count": state_counts[SEGMENTATION_SCOPE_STATE_OVERLAPPING],
        "state_counts": state_counts,
        "relationship_ids": _ordered_ids(record.relationship_id for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "routing_enabled_count": sum(1 for record in records if record.routing_enabled),
        "dispatch_enabled_count": sum(1 for record in records if record.dispatch_enabled),
        "scheduling_enabled_count": sum(1 for record in records if record.scheduling_enabled),
        "runtime_execution_enabled_count": sum(1 for record in records if record.runtime_execution_enabled),
    }


def overlap_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "relationship_id": record.relationship_id,
            "source_segment_id": record.source_segment_id,
            "target_segment_id": record.target_segment_id,
            "relationship_state": record.relationship_state,
            "relationship_boundary_ids": _ordered_ids(record.relationship_boundary_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
        }
        for record in sorted(
            (
                item
                for item in intelligence.relationship_records
                if item.relationship_state == SEGMENTATION_SCOPE_STATE_OVERLAPPING
            ),
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]


def degraded_scope_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.continuity_visibility)
    state_counts = count_continuity_states(records)
    return {
        "continuity_count": len(records),
        "degraded_count": state_counts[SEGMENTATION_SCOPE_STATE_DEGRADED],
        "stale_count": state_counts["stale"],
        "state_counts": state_counts,
        "continuity_ids": _ordered_ids(record.continuity_id for record in records),
        "fail_visible": all(record.fail_visible for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "mutation_enabled_count": sum(1 for record in records if record.mutation_enabled),
    }


def fail_visible_segmentation_summaries(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for record in intelligence.segment_records:
        if record.segment_state not in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES:
            continue
        summaries.append(
            {
                "record_id": record.segment_id,
                "visibility_state": record.segment_state,
                "reference_ids": _ordered_ids(record.grouped_boundary_ids),
                "fail_visible": record.fail_visible,
                "descriptive_only": record.descriptive_only,
            }
        )
    for record in intelligence.scope_records:
        if record.scope_state not in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES:
            continue
        summaries.append(
            {
                "record_id": record.scope_id,
                "visibility_state": record.scope_state,
                "reference_ids": _ordered_ids(record.scoped_governance_ids),
                "fail_visible": record.fail_visible,
                "descriptive_only": record.descriptive_only,
            }
        )
    return summaries


def ambiguous_scope_totals(intelligence: BoundarySegmentationScopeIntelligence) -> dict[str, Any]:
    combined = count_combined_segmentation_scope_states(intelligence)
    return {
        "ambiguous_count": combined[SEGMENTATION_SCOPE_STATE_AMBIGUOUS],
        "conflicting_count": combined[SEGMENTATION_SCOPE_STATE_CONFLICTING],
        "degraded_count": combined[SEGMENTATION_SCOPE_STATE_DEGRADED],
    }


def scope_provenance_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_visibility
    return {
        "provenance_id": provenance.provenance_id,
        "source_reference_ids": _ordered_ids(provenance.source_reference_ids),
        "source_hash_references": _ordered_ids(provenance.source_hash_references),
        "scope_reference_ids": _ordered_ids(provenance.scope_reference_ids),
        "provenance_visible": provenance.provenance_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "production_consumption_enabled": provenance.production_consumption_enabled,
    }


def scope_lineage_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    lineage = intelligence.lineage_visibility
    return {
        "lineage_id": lineage.lineage_id,
        "lineage_reference_ids": _ordered_ids(lineage.lineage_reference_ids),
        "lineage_hash_references": _ordered_ids(lineage.lineage_hash_references),
        "segment_reference_ids": _ordered_ids(lineage.segment_reference_ids),
        "lineage_visible": lineage.lineage_visible,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def governance_safe_segmentation_explainability(
    explainability: Iterable[SegmentationExplainabilityRecord],
) -> dict[str, Any]:
    records = tuple(explainability)
    by_state = Counter(record.visibility_state for record in records)
    return {
        "explainability_count": len(records),
        "state_counts": {state: int(by_state.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES},
        "explainability_ids": _ordered_ids(record.explainability_id for record in records),
        "explainability_first": all(record.explainability_first for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "routing_enabled_count": sum(1 for record in records if record.routing_enabled),
    }


def aggregate_scope_diagnostics(
    diagnostics: Iterable[ScopeDiagnosticRecord],
) -> dict[str, Any]:
    records = tuple(diagnostics)
    by_state = Counter(record.scope_state for record in records)
    by_severity = Counter(record.severity for record in records)
    return {
        "diagnostic_count": len(records),
        "state_counts": {state: int(by_state.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES},
        "severity_counts": {severity: int(by_severity[severity]) for severity in sorted(by_severity)},
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "fail_visible": all(record.fail_visible for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "scope_based_authorization_enabled_count": sum(
            1 for record in records if record.scope_based_authorization_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(1 for record in records if record.automatic_repair_enabled),
    }


def aggregate_segmentation_diagnostics(
    diagnostics: Iterable[SegmentationDiagnosticRecord],
) -> dict[str, Any]:
    records = tuple(diagnostics)
    by_state = Counter(record.segmentation_state for record in records)
    by_severity = Counter(record.severity for record in records)
    return {
        "diagnostic_count": len(records),
        "state_counts": {state: int(by_state.get(state, 0)) for state in BOUNDARY_SEGMENTATION_SCOPE_STATES},
        "severity_counts": {severity: int(by_severity[severity]) for severity in sorted(by_severity)},
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "fail_visible": all(record.fail_visible for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "segmentation_based_routing_enabled_count": sum(
            1 for record in records if record.segmentation_based_routing_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(1 for record in records if record.automatic_repair_enabled),
    }


def validate_required_segmentation_scope_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    counts = count_combined_segmentation_scope_states(intelligence)
    missing_states = [state for state in BOUNDARY_SEGMENTATION_SCOPE_STATES if counts[state] <= 0]
    fail_visible_missing = [
        state for state in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not fail_visible_missing,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": fail_visible_missing,
    }
