"""Descriptive visibility helpers for v4.5A.5 cross-boundary drift continuity."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_5_cross_boundary_drift_continuity_models import (
    BOUNDARY_CONTINUITY_TYPES,
    CROSS_BOUNDARY_DIAGNOSTIC_TYPES,
    CROSS_BOUNDARY_EVIDENCE_CONTINUITY_TYPES,
    DEGRADATION_CONTINUITY_PRESERVATION_TYPES,
    DRIFT_CONTINUITY_PRESERVATION_TYPES,
    EXPLANATION_CONTINUITY_PRESERVATION_TYPES,
    PROPAGATION_CONTINUITY_PRESERVATION_TYPES,
    UNSUPPORTED_CROSS_BOUNDARY_OPERATIONAL_STATES,
    BoundaryPairContinuityRecord,
    CrossBoundaryContinuityDiagnostic,
    CrossBoundaryContinuityRecord,
    CrossBoundaryDriftContinuityIntelligence,
    CrossBoundaryEvidenceContinuity,
    DegradationContinuityPreservation,
    DriftContinuityPreservation,
    ExplanationContinuityPreservation,
    PropagationContinuityPreservation,
    UnsupportedCrossBoundaryVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_boundary_continuity_types(
    records: Iterable[CrossBoundaryContinuityRecord],
) -> dict[str, int]:
    counts = Counter(record.boundary_continuity_type for record in records)
    return {item: int(counts.get(item, 0)) for item in BOUNDARY_CONTINUITY_TYPES}


def count_boundary_pair_types(
    records: Iterable[BoundaryPairContinuityRecord],
) -> dict[str, int]:
    counts = Counter(record.boundary_continuity_type for record in records)
    return {item: int(counts.get(item, 0)) for item in BOUNDARY_CONTINUITY_TYPES}


def count_drift_continuity_types(
    records: Iterable[DriftContinuityPreservation],
) -> dict[str, int]:
    counts = Counter(record.drift_continuity_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in DRIFT_CONTINUITY_PRESERVATION_TYPES
    }


def count_propagation_continuity_types(
    records: Iterable[PropagationContinuityPreservation],
) -> dict[str, int]:
    counts = Counter(record.propagation_continuity_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in PROPAGATION_CONTINUITY_PRESERVATION_TYPES
    }


def count_degradation_continuity_types(
    records: Iterable[DegradationContinuityPreservation],
) -> dict[str, int]:
    counts = Counter(record.degradation_continuity_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in DEGRADATION_CONTINUITY_PRESERVATION_TYPES
    }


def count_explanation_continuity_types(
    records: Iterable[ExplanationContinuityPreservation],
) -> dict[str, int]:
    counts = Counter(record.explanation_continuity_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in EXPLANATION_CONTINUITY_PRESERVATION_TYPES
    }


def count_evidence_continuity_types(
    records: Iterable[CrossBoundaryEvidenceContinuity],
) -> dict[str, int]:
    counts = Counter(record.evidence_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in CROSS_BOUNDARY_EVIDENCE_CONTINUITY_TYPES
    }


def count_cross_boundary_diagnostic_types(
    records: Iterable[CrossBoundaryContinuityDiagnostic],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CROSS_BOUNDARY_DIAGNOSTIC_TYPES}


def count_unsupported_cross_boundary_states(
    records: Iterable[UnsupportedCrossBoundaryVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_CROSS_BOUNDARY_OPERATIONAL_STATES
    }


def cross_boundary_continuity_summary_visibility(
    records: Iterable[CrossBoundaryContinuityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "source_boundary_id": record.source_boundary_id,
            "target_boundary_id": record.target_boundary_id,
            "boundary_pair_id": record.boundary_pair_id,
            "drift_chain_id": record.drift_chain_id,
            "propagation_chain_id": record.propagation_chain_id,
            "degradation_chain_id": record.degradation_chain_id,
            "explanation_chain_id": record.explanation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "boundary_continuity_type": record.boundary_continuity_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "routing_enabled": record.routing_enabled,
            "traversal_enabled": record.traversal_enabled,
            "boundary_traversal_enabled": record.boundary_traversal_enabled,
            "continuity_restoration_enabled": record.continuity_restoration_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.cross_boundary_continuity_id),
        )
    ]


def boundary_pair_summary_visibility(
    records: Iterable[BoundaryPairContinuityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "boundary_pair_record_id": record.boundary_pair_record_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "source_boundary_id": record.source_boundary_id,
            "target_boundary_id": record.target_boundary_id,
            "boundary_pair_id": record.boundary_pair_id,
            "boundary_continuity_type": record.boundary_continuity_type,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "no_routing_behavior": record.no_routing_behavior,
            "no_traversal_behavior": record.no_traversal_behavior,
            "routing_enabled": record.routing_enabled,
            "traversal_enabled": record.traversal_enabled,
            "boundary_traversal_enabled": record.boundary_traversal_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.boundary_pair_record_id),
        )
    ]


def drift_continuity_summary_visibility(
    records: Iterable[DriftContinuityPreservation],
) -> list[dict[str, Any]]:
    return [
        {
            "drift_continuity_id": record.drift_continuity_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "drift_continuity_type": record.drift_continuity_type,
            "drift_chain_id": record.drift_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "restoration_enabled": record.restoration_enabled,
            "remediation_enabled": record.remediation_enabled,
            "routing_enabled": record.routing_enabled,
            "traversal_enabled": record.traversal_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.drift_continuity_id),
        )
    ]


def propagation_continuity_summary_visibility(
    records: Iterable[PropagationContinuityPreservation],
) -> list[dict[str, Any]]:
    return [
        {
            "propagation_continuity_id": record.propagation_continuity_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "propagation_continuity_type": record.propagation_continuity_type,
            "propagation_chain_id": record.propagation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "correction_enabled": record.correction_enabled,
            "suppression_enabled": record.suppression_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "routing_enabled": record.routing_enabled,
            "traversal_enabled": record.traversal_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.propagation_continuity_id),
        )
    ]


def degradation_continuity_summary_visibility(
    records: Iterable[DegradationContinuityPreservation],
) -> list[dict[str, Any]]:
    return [
        {
            "degradation_continuity_id": record.degradation_continuity_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "degradation_continuity_type": record.degradation_continuity_type,
            "degradation_chain_id": record.degradation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "correction_enabled": record.correction_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.degradation_continuity_id),
        )
    ]


def explanation_continuity_summary_visibility(
    records: Iterable[ExplanationContinuityPreservation],
) -> list[dict[str, Any]]:
    return [
        {
            "explanation_continuity_id": record.explanation_continuity_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "explanation_continuity_type": record.explanation_continuity_type,
            "explanation_chain_id": record.explanation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "explanation_action_enabled": record.explanation_action_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.explanation_continuity_id),
        )
    ]


def evidence_continuity_summary_visibility(
    records: Iterable[CrossBoundaryEvidenceContinuity],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_continuity_id": record.evidence_continuity_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "evidence_type": record.evidence_type,
            "source_evidence_id": record.source_evidence_id,
            "target_evidence_id": record.target_evidence_id,
            "evidence_chain_id": record.evidence_chain_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "replay_reference": record.replay_reference,
            "replay_safe": record.replay_safe,
            "rollback_safe": record.rollback_safe,
            "provenance_safe": record.provenance_safe,
            "lineage_safe": record.lineage_safe,
            "integrity_safe": record.integrity_safe,
            "hidden_assumption_used": record.hidden_assumption_used,
            "production_consumption_enabled": record.production_consumption_enabled,
            "runtime_mutation_enabled": record.runtime_mutation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_continuity_id),
        )
    ]


def fail_visible_cross_boundary_diagnostic_summaries(
    records: Iterable[CrossBoundaryContinuityDiagnostic],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "diagnostic_type": record.diagnostic_type,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "message": record.message,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "hidden_assumption_used": record.hidden_assumption_used,
            "silent_fallback_enabled": record.silent_fallback_enabled,
            "routing_enabled": record.routing_enabled,
            "traversal_enabled": record.traversal_enabled,
            "boundary_traversal_enabled": record.boundary_traversal_enabled,
            "continuity_restoration_enabled": record.continuity_restoration_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_cross_boundary_visibility_summaries(
    records: Iterable[UnsupportedCrossBoundaryVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "operational_enabled": record.operational_enabled,
            "authorization_enabled": record.authorization_enabled,
            "routing_enabled": record.routing_enabled,
            "traversal_enabled": record.traversal_enabled,
            "boundary_traversal_enabled": record.boundary_traversal_enabled,
            "continuity_restoration_enabled": record.continuity_restoration_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "automated_correction_enabled": record.automated_correction_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def validate_required_cross_boundary_continuity_visibility(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    boundary_counts = count_boundary_continuity_types(
        intelligence.cross_boundary_continuity
    )
    boundary_pair_counts = count_boundary_pair_types(
        intelligence.boundary_pair_continuity
    )
    drift_counts = count_drift_continuity_types(intelligence.drift_continuity)
    propagation_counts = count_propagation_continuity_types(
        intelligence.propagation_continuity
    )
    degradation_counts = count_degradation_continuity_types(
        intelligence.degradation_continuity
    )
    explanation_counts = count_explanation_continuity_types(
        intelligence.explanation_continuity
    )
    evidence_counts = count_evidence_continuity_types(intelligence.evidence_continuity)
    diagnostic_counts = count_cross_boundary_diagnostic_types(intelligence.diagnostics)
    unsupported_counts = count_unsupported_cross_boundary_states(
        intelligence.unsupported_cross_boundary_visibility
    )
    missing_boundary_types = [key for key, count in boundary_counts.items() if count <= 0]
    missing_boundary_pair_types = [
        key for key, count in boundary_pair_counts.items() if count <= 0
    ]
    missing_drift_types = [key for key, count in drift_counts.items() if count <= 0]
    missing_propagation_types = [
        key for key, count in propagation_counts.items() if count <= 0
    ]
    missing_degradation_types = [
        key for key, count in degradation_counts.items() if count <= 0
    ]
    missing_explanation_types = [
        key for key, count in explanation_counts.items() if count <= 0
    ]
    missing_evidence_types = [
        key for key, count in evidence_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        key for key, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_states = [
        key for key, count in unsupported_counts.items() if count <= 0
    ]
    return {
        "valid": not (
            missing_boundary_types
            or missing_boundary_pair_types
            or missing_drift_types
            or missing_propagation_types
            or missing_degradation_types
            or missing_explanation_types
            or missing_evidence_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "boundary_counts": boundary_counts,
        "boundary_pair_counts": boundary_pair_counts,
        "drift_counts": drift_counts,
        "propagation_counts": propagation_counts,
        "degradation_counts": degradation_counts,
        "explanation_counts": explanation_counts,
        "evidence_counts": evidence_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_counts,
        "missing_boundary_types": missing_boundary_types,
        "missing_boundary_pair_types": missing_boundary_pair_types,
        "missing_drift_types": missing_drift_types,
        "missing_propagation_types": missing_propagation_types,
        "missing_degradation_types": missing_degradation_types,
        "missing_explanation_types": missing_explanation_types,
        "missing_evidence_types": missing_evidence_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_cross_boundary_continuity_summary(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_executing": intelligence.non_executing,
        "non_authorizing": intelligence.non_authorizing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_operational_mutating": intelligence.non_operational_mutating,
        "non_routing": intelligence.non_routing,
        "non_dispatching": intelligence.non_dispatching,
        "non_traversing": intelligence.non_traversing,
        "non_scheduling": intelligence.non_scheduling,
        "non_sequencing": intelligence.non_sequencing,
        "non_recommending": intelligence.non_recommending,
        "non_deciding": intelligence.non_deciding,
        "non_restoring": intelligence.non_restoring,
        "runtime_execution_enabled": intelligence.runtime_execution_enabled,
        "orchestration_execution_enabled": intelligence.orchestration_execution_enabled,
        "orchestration_authorization_enabled": intelligence.orchestration_authorization_enabled,
        "orchestration_approval_enabled": intelligence.orchestration_approval_enabled,
        "orchestration_dispatch_enabled": intelligence.orchestration_dispatch_enabled,
        "orchestration_routing_enabled": intelligence.orchestration_routing_enabled,
        "orchestration_traversal_enabled": intelligence.orchestration_traversal_enabled,
        "orchestration_scheduling_enabled": intelligence.orchestration_scheduling_enabled,
        "orchestration_sequencing_enabled": intelligence.orchestration_sequencing_enabled,
        "orchestration_decision_enabled": intelligence.orchestration_decision_enabled,
        "orchestration_recommendation_enabled": intelligence.orchestration_recommendation_enabled,
        "boundary_traversal_enabled": intelligence.boundary_traversal_enabled,
        "continuity_restoration_enabled": intelligence.continuity_restoration_enabled,
        "remediation_enabled": intelligence.remediation_enabled,
        "repair_enabled": intelligence.repair_enabled,
        "mitigation_enabled": intelligence.mitigation_enabled,
        "auto_correction_enabled": intelligence.auto_correction_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
    }
