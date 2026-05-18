"""Descriptive visibility helpers for v4.5A.2 drift propagation intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_2_drift_propagation_models import (
    CROSS_BOUNDARY_PROPAGATION_TYPES,
    PROPAGATION_ACCUMULATION_TYPES,
    PROPAGATION_CHAIN_TYPES,
    PROPAGATION_DIAGNOSTIC_TYPES,
    PROPAGATION_EVIDENCE_TYPES,
    PROPAGATION_EXPLAINABILITY_TYPES,
    UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES,
    CrossBoundaryPropagationVisibility,
    DriftPropagationIntelligence,
    PropagationChainRecord,
    PropagationClassificationRecord,
    PropagationContinuityRecord,
    PropagationDiagnosticRecord,
    PropagationEvidenceChain,
    PropagationExplainabilityVisibility,
    PropagationSeverityAccumulation,
    UnsupportedPropagationVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_propagation_types(records: Iterable[PropagationChainRecord]) -> dict[str, int]:
    counts = Counter(record.propagation_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PROPAGATION_CHAIN_TYPES}


def count_accumulation_types(
    classifications: Iterable[PropagationClassificationRecord],
    diagnostics: Iterable[PropagationDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.accumulation_type for record in classifications)
    counts.update(record.accumulation_type for record in diagnostics)
    return {item: int(counts.get(item, 0)) for item in PROPAGATION_ACCUMULATION_TYPES}


def count_evidence_types(records: Iterable[PropagationEvidenceChain]) -> dict[str, int]:
    counts = Counter(record.evidence_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PROPAGATION_EVIDENCE_TYPES}


def count_explainability_types(
    records: Iterable[PropagationExplainabilityVisibility],
) -> dict[str, int]:
    counts = Counter(record.explainability_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PROPAGATION_EXPLAINABILITY_TYPES}


def count_cross_boundary_types(
    records: Iterable[CrossBoundaryPropagationVisibility],
) -> dict[str, int]:
    counts = Counter(record.boundary_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CROSS_BOUNDARY_PROPAGATION_TYPES}


def count_diagnostic_types(records: Iterable[PropagationDiagnosticRecord]) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PROPAGATION_DIAGNOSTIC_TYPES}


def count_unsupported_propagation_states(
    records: Iterable[UnsupportedPropagationVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES
    }


def propagation_summary_visibility(
    intelligence: DriftPropagationIntelligence,
) -> list[dict[str, Any]]:
    classification_by_propagation = {
        record.propagation_id: record for record in intelligence.classifications
    }
    return [
        {
            "propagation_id": record.propagation_id,
            "source_drift_id": record.source_drift_id,
            "inherited_drift_id": record.inherited_drift_id,
            "refinement_drift_id": record.refinement_drift_id,
            "propagation_chain_id": record.propagation_chain_id,
            "propagation_scope_id": record.propagation_scope_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "propagation_type": record.propagation_type,
            "accumulation_type": classification_by_propagation[
                record.propagation_id
            ].accumulation_type,
            "descriptive_only": record.descriptive_only,
            "non_operational": record.non_operational,
        }
        for record in sorted(
            intelligence.propagation_chains,
            key=lambda item: (item.deterministic_order, item.propagation_id),
        )
    ]


def propagation_severity_summary_visibility(
    records: Iterable[PropagationSeverityAccumulation],
) -> list[dict[str, Any]]:
    return [
        {
            "severity_id": record.severity_id,
            "accumulation_type": record.accumulation_type,
            "propagation_ids": _ordered_ids(record.propagation_ids),
            "diagnostic_ids": _ordered_ids(record.diagnostic_ids),
            "count": record.count,
            "non_remediating": record.non_remediating,
            "non_operational": record.non_operational,
            "non_authorizing": record.non_authorizing,
            "remediation_enabled": record.remediation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "operational_behavior_enabled": record.operational_behavior_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.severity_id))
    ]


def propagation_continuity_summary_visibility(
    records: Iterable[PropagationContinuityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_id": record.continuity_id,
            "propagation_id": record.propagation_id,
            "propagation_chain_id": record.propagation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "continuity_type": record.continuity_type,
            "continuity_preserved": record.continuity_preserved,
            "lineage_safe": record.lineage_safe,
            "provenance_safe": record.provenance_safe,
            "integrity_safe": record.integrity_safe,
            "repair_enabled": record.repair_enabled,
            "remediation_enabled": record.remediation_enabled,
            "propagation_correction_enabled": record.propagation_correction_enabled,
            "runtime_mutation_enabled": record.runtime_mutation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.continuity_id))
    ]


def propagation_explainability_summary_visibility(
    records: Iterable[PropagationExplainabilityVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_id": record.explainability_id,
            "propagation_id": record.propagation_id,
            "explainability_type": record.explainability_type,
            "visible_reason": record.visible_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "explainability_first": record.explainability_first,
            "descriptive_only": record.descriptive_only,
            "operational_response_enabled": record.operational_response_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "decision_enabled": record.decision_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.explainability_id))
    ]


def propagation_evidence_summary_visibility(
    records: Iterable[PropagationEvidenceChain],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": record.evidence_id,
            "propagation_id": record.propagation_id,
            "evidence_type": record.evidence_type,
            "evidence_chain_id": record.evidence_chain_id,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "replay_safe": record.replay_safe,
            "rollback_safe": record.rollback_safe,
            "provenance_safe": record.provenance_safe,
            "lineage_safe": record.lineage_safe,
            "integrity_safe": record.integrity_safe,
            "hidden_assumption_used": record.hidden_assumption_used,
            "production_consumption_enabled": record.production_consumption_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.evidence_id))
    ]


def fail_visible_propagation_diagnostic_summaries(
    records: Iterable[PropagationDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "propagation_id": record.propagation_id,
            "diagnostic_type": record.diagnostic_type,
            "accumulation_type": record.accumulation_type,
            "message": record.message,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "hidden_assumption_used": record.hidden_assumption_used,
            "silent_suppression_enabled": record.silent_suppression_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "propagation_correction_enabled": record.propagation_correction_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
            "authorization_behavior_enabled": record.authorization_behavior_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]


def unsupported_propagation_visibility_summaries(
    records: Iterable[UnsupportedPropagationVisibility],
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
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "propagation_suppression_enabled": record.propagation_suppression_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def cross_boundary_propagation_summary_visibility(
    records: Iterable[CrossBoundaryPropagationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "cross_boundary_id": record.cross_boundary_id,
            "propagation_id": record.propagation_id,
            "boundary_type": record.boundary_type,
            "source_boundary_reference_id": record.source_boundary_reference_id,
            "target_boundary_reference_id": record.target_boundary_reference_id,
            "visibility_reason": record.visibility_reason,
            "descriptive_only": record.descriptive_only,
            "no_runtime_traversal": record.no_runtime_traversal,
            "no_orchestration_semantics": record.no_orchestration_semantics,
            "traversal_enabled": record.traversal_enabled,
            "routing_enabled": record.routing_enabled,
            "dispatch_enabled": record.dispatch_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.cross_boundary_id))
    ]


def validate_required_propagation_visibility(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    propagation_counts = count_propagation_types(intelligence.propagation_chains)
    accumulation_counts = count_accumulation_types(
        intelligence.classifications,
        intelligence.diagnostics,
    )
    evidence_counts = count_evidence_types(intelligence.evidence_chains)
    explainability_counts = count_explainability_types(
        intelligence.explainability_visibility
    )
    cross_boundary_counts = count_cross_boundary_types(
        intelligence.cross_boundary_visibility
    )
    diagnostic_counts = count_diagnostic_types(intelligence.diagnostics)
    unsupported_counts = count_unsupported_propagation_states(
        intelligence.unsupported_propagation_visibility
    )
    missing_propagation_types = [
        key for key, count in propagation_counts.items() if count <= 0
    ]
    missing_accumulation_types = [
        key for key, count in accumulation_counts.items() if count <= 0
    ]
    missing_evidence_types = [
        key for key, count in evidence_counts.items() if count <= 0
    ]
    missing_explainability_types = [
        key for key, count in explainability_counts.items() if count <= 0
    ]
    missing_cross_boundary_types = [
        key for key, count in cross_boundary_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        key for key, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_states = [
        key for key, count in unsupported_counts.items() if count <= 0
    ]
    return {
        "valid": not (
            missing_propagation_types
            or missing_accumulation_types
            or missing_evidence_types
            or missing_explainability_types
            or missing_cross_boundary_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "propagation_counts": propagation_counts,
        "accumulation_counts": accumulation_counts,
        "evidence_counts": evidence_counts,
        "explainability_counts": explainability_counts,
        "cross_boundary_counts": cross_boundary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_counts,
        "missing_propagation_types": missing_propagation_types,
        "missing_accumulation_types": missing_accumulation_types,
        "missing_evidence_types": missing_evidence_types,
        "missing_explainability_types": missing_explainability_types,
        "missing_cross_boundary_types": missing_cross_boundary_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_propagation_summary(
    intelligence: DriftPropagationIntelligence,
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
        "remediation_enabled": intelligence.remediation_enabled,
        "repair_enabled": intelligence.repair_enabled,
        "mitigation_enabled": intelligence.mitigation_enabled,
        "auto_correction_enabled": intelligence.auto_correction_enabled,
        "propagation_correction_enabled": intelligence.propagation_correction_enabled,
        "propagation_suppression_enabled": intelligence.propagation_suppression_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
    }
