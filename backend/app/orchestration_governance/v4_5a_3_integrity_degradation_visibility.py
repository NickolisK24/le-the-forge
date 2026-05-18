"""Descriptive visibility helpers for v4.5A.3 integrity degradation intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_3_integrity_degradation_models import (
    CONTINUITY_DEGRADATION_TYPES,
    CROSS_BOUNDARY_INTEGRITY_TYPES,
    DEGRADATION_CLASSIFICATION_TYPES,
    DEGRADATION_DIAGNOSTIC_TYPES,
    DEGRADATION_EVIDENCE_TYPES,
    DEGRADATION_SEVERITY_TYPES,
    EXPLAINABILITY_DEGRADATION_TYPES,
    UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES,
    ContinuityDegradationVisibility,
    CrossBoundaryIntegrityVisibility,
    DegradationClassificationRecord,
    DegradationEvidenceChain,
    DegradationRecord,
    DegradationSeverityAccumulation,
    ExplainabilityDegradationVisibility,
    IntegrityDegradationDiagnostic,
    IntegrityDegradationIntelligence,
    UnsupportedDegradationVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_degradation_classifications(
    records: Iterable[DegradationClassificationRecord],
) -> dict[str, int]:
    counts = Counter(record.classification_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DEGRADATION_CLASSIFICATION_TYPES}


def count_degradation_severity_types(
    classifications: Iterable[DegradationClassificationRecord],
    diagnostics: Iterable[IntegrityDegradationDiagnostic],
) -> dict[str, int]:
    counts = Counter(record.severity_type for record in classifications)
    counts.update(record.severity_type for record in diagnostics)
    return {item: int(counts.get(item, 0)) for item in DEGRADATION_SEVERITY_TYPES}


def count_degradation_evidence_types(
    records: Iterable[DegradationEvidenceChain],
) -> dict[str, int]:
    counts = Counter(record.evidence_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DEGRADATION_EVIDENCE_TYPES}


def count_continuity_degradation_types(
    records: Iterable[ContinuityDegradationVisibility],
) -> dict[str, int]:
    counts = Counter(record.continuity_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CONTINUITY_DEGRADATION_TYPES}


def count_explainability_degradation_types(
    records: Iterable[ExplainabilityDegradationVisibility],
) -> dict[str, int]:
    counts = Counter(record.explainability_type for record in records)
    return {item: int(counts.get(item, 0)) for item in EXPLAINABILITY_DEGRADATION_TYPES}


def count_cross_boundary_integrity_types(
    records: Iterable[CrossBoundaryIntegrityVisibility],
) -> dict[str, int]:
    counts = Counter(record.boundary_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CROSS_BOUNDARY_INTEGRITY_TYPES}


def count_degradation_diagnostic_types(
    records: Iterable[IntegrityDegradationDiagnostic],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DEGRADATION_DIAGNOSTIC_TYPES}


def count_unsupported_degradation_states(
    records: Iterable[UnsupportedDegradationVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES
    }


def degradation_summary_visibility(
    intelligence: IntegrityDegradationIntelligence,
) -> list[dict[str, Any]]:
    classification_by_degradation = {
        record.degradation_id: record for record in intelligence.classifications
    }
    return [
        {
            "degradation_id": record.degradation_id,
            "degradation_chain_id": record.degradation_chain_id,
            "degradation_scope_id": record.degradation_scope_id,
            "source_drift_id": record.source_drift_id,
            "propagation_chain_id": record.propagation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "integrity_reference_id": record.integrity_reference_id,
            "classification_type": classification_by_degradation[
                record.degradation_id
            ].classification_type,
            "severity_type": classification_by_degradation[
                record.degradation_id
            ].severity_type,
            "descriptive_only": record.descriptive_only,
            "non_operational": record.non_operational,
        }
        for record in sorted(
            intelligence.degradation_records,
            key=lambda item: (item.deterministic_order, item.degradation_id),
        )
    ]


def degradation_severity_summary_visibility(
    records: Iterable[DegradationSeverityAccumulation],
) -> list[dict[str, Any]]:
    return [
        {
            "severity_id": record.severity_id,
            "severity_type": record.severity_type,
            "degradation_ids": _ordered_ids(record.degradation_ids),
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


def continuity_degradation_summary_visibility(
    records: Iterable[ContinuityDegradationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_id": record.continuity_id,
            "degradation_id": record.degradation_id,
            "continuity_type": record.continuity_type,
            "degradation_chain_id": record.degradation_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "continuity_preserved": record.continuity_preserved,
            "lineage_safe": record.lineage_safe,
            "provenance_safe": record.provenance_safe,
            "integrity_safe": record.integrity_safe,
            "restoration_enabled": record.restoration_enabled,
            "repair_enabled": record.repair_enabled,
            "remediation_enabled": record.remediation_enabled,
            "degradation_correction_enabled": record.degradation_correction_enabled,
            "runtime_mutation_enabled": record.runtime_mutation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.continuity_id))
    ]


def explainability_degradation_summary_visibility(
    records: Iterable[ExplainabilityDegradationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_id": record.explainability_id,
            "degradation_id": record.degradation_id,
            "explainability_type": record.explainability_type,
            "visible_reason": record.visible_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "explainability_first": record.explainability_first,
            "descriptive_only": record.descriptive_only,
            "automated_response_enabled": record.automated_response_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "decision_enabled": record.decision_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.explainability_id))
    ]


def degradation_evidence_summary_visibility(
    records: Iterable[DegradationEvidenceChain],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": record.evidence_id,
            "degradation_id": record.degradation_id,
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


def fail_visible_degradation_diagnostic_summaries(
    records: Iterable[IntegrityDegradationDiagnostic],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "degradation_id": record.degradation_id,
            "diagnostic_type": record.diagnostic_type,
            "severity_type": record.severity_type,
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
            "degradation_correction_enabled": record.degradation_correction_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
            "authorization_behavior_enabled": record.authorization_behavior_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]


def unsupported_degradation_visibility_summaries(
    records: Iterable[UnsupportedDegradationVisibility],
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
            "degradation_suppression_enabled": record.degradation_suppression_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def cross_boundary_integrity_summary_visibility(
    records: Iterable[CrossBoundaryIntegrityVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "cross_boundary_id": record.cross_boundary_id,
            "degradation_id": record.degradation_id,
            "boundary_type": record.boundary_type,
            "source_boundary_reference_id": record.source_boundary_reference_id,
            "target_boundary_reference_id": record.target_boundary_reference_id,
            "visibility_reason": record.visibility_reason,
            "descriptive_only": record.descriptive_only,
            "no_orchestration_traversal": record.no_orchestration_traversal,
            "no_operational_routing": record.no_operational_routing,
            "traversal_enabled": record.traversal_enabled,
            "routing_enabled": record.routing_enabled,
            "dispatch_enabled": record.dispatch_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.cross_boundary_id))
    ]


def validate_required_degradation_visibility(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    classification_counts = count_degradation_classifications(intelligence.classifications)
    severity_counts = count_degradation_severity_types(
        intelligence.classifications,
        intelligence.diagnostics,
    )
    evidence_counts = count_degradation_evidence_types(intelligence.evidence_chains)
    continuity_counts = count_continuity_degradation_types(
        intelligence.continuity_degradation
    )
    explainability_counts = count_explainability_degradation_types(
        intelligence.explainability_degradation
    )
    cross_boundary_counts = count_cross_boundary_integrity_types(
        intelligence.cross_boundary_integrity
    )
    diagnostic_counts = count_degradation_diagnostic_types(intelligence.diagnostics)
    unsupported_counts = count_unsupported_degradation_states(
        intelligence.unsupported_degradation_visibility
    )
    missing_classification_types = [
        key for key, count in classification_counts.items() if count <= 0
    ]
    missing_severity_types = [
        key for key, count in severity_counts.items() if count <= 0
    ]
    missing_evidence_types = [
        key for key, count in evidence_counts.items() if count <= 0
    ]
    missing_continuity_types = [
        key for key, count in continuity_counts.items() if count <= 0
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
            missing_classification_types
            or missing_severity_types
            or missing_evidence_types
            or missing_continuity_types
            or missing_explainability_types
            or missing_cross_boundary_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "classification_counts": classification_counts,
        "severity_counts": severity_counts,
        "evidence_counts": evidence_counts,
        "continuity_counts": continuity_counts,
        "explainability_counts": explainability_counts,
        "cross_boundary_counts": cross_boundary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_counts,
        "missing_classification_types": missing_classification_types,
        "missing_severity_types": missing_severity_types,
        "missing_evidence_types": missing_evidence_types,
        "missing_continuity_types": missing_continuity_types,
        "missing_explainability_types": missing_explainability_types,
        "missing_cross_boundary_types": missing_cross_boundary_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_degradation_summary(
    intelligence: IntegrityDegradationIntelligence,
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
        "degradation_correction_enabled": intelligence.degradation_correction_enabled,
        "degradation_suppression_enabled": intelligence.degradation_suppression_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
    }
