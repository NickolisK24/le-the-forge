"""Visibility helpers for v4.5A.7 integrity certification."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_7_integrity_certification_models import (
    CERTIFICATION_DIAGNOSTIC_TYPES,
    CONTINUITY_INTEGRITY_CERTIFICATION_TYPES,
    COVERAGE_CERTIFICATION_TYPES,
    DIAGNOSTICS_INTEGRITY_CERTIFICATION_TYPES,
    HASH_SERIALIZATION_CERTIFICATION_TYPES,
    INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    UNSUPPORTED_CERTIFICATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_PRESERVATION_TYPES,
    CertificationDiagnosticRecord,
    ContinuityIntegrityCertification,
    CoverageCertificationVisibility,
    DiagnosticsIntegrityCertification,
    HashingSerializationIntegrityCertification,
    InheritedProhibitionPreservationCertification,
    IntegrityCertificationIntelligence,
    IntegrityCertificationRecord,
    UnsupportedCertificationVisibility,
    UnsupportedStatePreservationCertification,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_coverage_certification_types(
    records: Iterable[CoverageCertificationVisibility],
) -> dict[str, int]:
    counts = Counter(record.coverage_type for record in records)
    return {item: int(counts.get(item, 0)) for item in COVERAGE_CERTIFICATION_TYPES}


def count_unsupported_state_preservation_types(
    records: Iterable[UnsupportedStatePreservationCertification],
) -> dict[str, int]:
    counts = Counter(record.preservation_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_STATE_PRESERVATION_TYPES
    }


def count_inherited_prohibition_certification_types(
    records: Iterable[InheritedProhibitionPreservationCertification],
) -> dict[str, int]:
    counts = Counter(record.preservation_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in INHERITED_PROHIBITION_CERTIFICATION_TYPES
    }


def count_hashing_serialization_certification_types(
    records: Iterable[HashingSerializationIntegrityCertification],
) -> dict[str, int]:
    counts = Counter(record.certification_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in HASH_SERIALIZATION_CERTIFICATION_TYPES
    }


def count_continuity_certification_types(
    records: Iterable[ContinuityIntegrityCertification],
) -> dict[str, int]:
    counts = Counter(record.continuity_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in CONTINUITY_INTEGRITY_CERTIFICATION_TYPES
    }


def count_diagnostics_certification_types(
    records: Iterable[DiagnosticsIntegrityCertification],
) -> dict[str, int]:
    counts = Counter(record.diagnostics_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in DIAGNOSTICS_INTEGRITY_CERTIFICATION_TYPES
    }


def count_certification_diagnostic_types(
    records: Iterable[CertificationDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CERTIFICATION_DIAGNOSTIC_TYPES}


def count_unsupported_certification_states(
    records: Iterable[UnsupportedCertificationVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_CERTIFICATION_OPERATIONAL_STATES
    }


def certification_summary_visibility(
    records: Iterable[IntegrityCertificationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "certification_record_id": record.certification_record_id,
            "certification_id": record.certification_id,
            "certification_chain_id": record.certification_chain_id,
            "drift_foundation_reference_id": record.drift_foundation_reference_id,
            "propagation_reference_id": record.propagation_reference_id,
            "degradation_reference_id": record.degradation_reference_id,
            "explainability_reference_id": record.explainability_reference_id,
            "continuity_reference_id": record.continuity_reference_id,
            "diagnostics_aggregation_reference_id": (
                record.diagnostics_aggregation_reference_id
            ),
            "evidence_reference_id": record.evidence_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "non_authorizing": record.non_authorizing,
            "non_approving": record.non_approving,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_readiness_enabled": record.operational_readiness_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.certification_record_id),
        )
    ]


def coverage_certification_summary_visibility(
    records: Iterable[CoverageCertificationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "coverage_id": record.coverage_id,
            "certification_id": record.certification_id,
            "coverage_type": record.coverage_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "coverage_preserved": record.coverage_preserved,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_semantics_enabled": record.operational_semantics_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.coverage_id))
    ]


def unsupported_state_certification_summary_visibility(
    records: Iterable[UnsupportedStatePreservationCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_certification_id": record.unsupported_certification_id,
            "certification_id": record.certification_id,
            "preservation_type": record.preservation_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "preservation_certified": record.preservation_certified,
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "suppression_enabled": record.suppression_enabled,
            "remediation_enabled": record.remediation_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.unsupported_certification_id),
        )
    ]


def inherited_prohibition_certification_summary_visibility(
    records: Iterable[InheritedProhibitionPreservationCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "prohibition_certification_id": record.prohibition_certification_id,
            "certification_id": record.certification_id,
            "preservation_type": record.preservation_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "preservation_certified": record.preservation_certified,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_behavior_enabled": record.operational_behavior_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.prohibition_certification_id),
        )
    ]


def hashing_serialization_certification_summary_visibility(
    records: Iterable[HashingSerializationIntegrityCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "hash_serialization_certification_id": (
                record.hash_serialization_certification_id
            ),
            "certification_id": record.certification_id,
            "certification_type": record.certification_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "certification_preserved": record.certification_preserved,
            "replay_safe": record.replay_safe,
            "lineage_safe": record.lineage_safe,
            "provenance_safe": record.provenance_safe,
            "descriptive_only": record.descriptive_only,
            "runtime_authority_enabled": record.runtime_authority_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.hash_serialization_certification_id,
            ),
        )
    ]


def continuity_certification_summary_visibility(
    records: Iterable[ContinuityIntegrityCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_certification_id": record.continuity_certification_id,
            "certification_id": record.certification_id,
            "continuity_type": record.continuity_type,
            "continuity_reference_id": record.continuity_reference_id,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "continuity_certified": record.continuity_certified,
            "descriptive_only": record.descriptive_only,
            "restoration_enabled": record.restoration_enabled,
            "repair_enabled": record.repair_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.continuity_certification_id),
        )
    ]


def diagnostics_certification_summary_visibility(
    records: Iterable[DiagnosticsIntegrityCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostics_certification_id": record.diagnostics_certification_id,
            "certification_id": record.certification_id,
            "diagnostics_type": record.diagnostics_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "diagnostics_certified": record.diagnostics_certified,
            "descriptive_only": record.descriptive_only,
            "automated_triage_enabled": record.automated_triage_enabled,
            "prioritization_enabled": record.prioritization_enabled,
            "ranking_enabled": record.ranking_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostics_certification_id),
        )
    ]


def fail_visible_certification_diagnostic_summaries(
    records: Iterable[CertificationDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "certification_id": record.certification_id,
            "diagnostic_type": record.diagnostic_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "message": record.message,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "silent_fallback_enabled": record.silent_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]


def unsupported_certification_visibility_summaries(
    records: Iterable[UnsupportedCertificationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_enabled": record.operational_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "automated_correction_enabled": record.automated_correction_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def validate_required_integrity_certification_visibility(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    coverage_counts = count_coverage_certification_types(
        intelligence.coverage_certifications
    )
    unsupported_counts = count_unsupported_state_preservation_types(
        intelligence.unsupported_state_certifications
    )
    prohibition_counts = count_inherited_prohibition_certification_types(
        intelligence.inherited_prohibition_certifications
    )
    hash_serialization_counts = count_hashing_serialization_certification_types(
        intelligence.hashing_serialization_certifications
    )
    continuity_counts = count_continuity_certification_types(
        intelligence.continuity_certifications
    )
    diagnostics_counts = count_diagnostics_certification_types(
        intelligence.diagnostics_certifications
    )
    diagnostic_counts = count_certification_diagnostic_types(
        intelligence.certification_diagnostics
    )
    unsupported_state_counts = count_unsupported_certification_states(
        intelligence.unsupported_certification_visibility
    )
    missing_coverage_types = [key for key, count in coverage_counts.items() if count <= 0]
    missing_unsupported_types = [
        key for key, count in unsupported_counts.items() if count <= 0
    ]
    missing_prohibition_types = [
        key for key, count in prohibition_counts.items() if count <= 0
    ]
    missing_hash_serialization_types = [
        key for key, count in hash_serialization_counts.items() if count <= 0
    ]
    missing_continuity_types = [
        key for key, count in continuity_counts.items() if count <= 0
    ]
    missing_diagnostics_types = [
        key for key, count in diagnostics_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        key for key, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_states = [
        key for key, count in unsupported_state_counts.items() if count <= 0
    ]
    return {
        "valid": not (
            missing_coverage_types
            or missing_unsupported_types
            or missing_prohibition_types
            or missing_hash_serialization_types
            or missing_continuity_types
            or missing_diagnostics_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "coverage_counts": coverage_counts,
        "unsupported_counts": unsupported_counts,
        "prohibition_counts": prohibition_counts,
        "hash_serialization_counts": hash_serialization_counts,
        "continuity_counts": continuity_counts,
        "diagnostics_counts": diagnostics_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_state_counts,
        "missing_coverage_types": missing_coverage_types,
        "missing_unsupported_types": missing_unsupported_types,
        "missing_prohibition_types": missing_prohibition_types,
        "missing_hash_serialization_types": missing_hash_serialization_types,
        "missing_continuity_types": missing_continuity_types,
        "missing_diagnostics_types": missing_diagnostics_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_integrity_certification_summary(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_operational_mutating": intelligence.non_operational_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
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
        "authorization_semantics_enabled": intelligence.authorization_semantics_enabled,
        "approval_semantics_enabled": intelligence.approval_semantics_enabled,
        "remediation_enabled": intelligence.remediation_enabled,
        "repair_enabled": intelligence.repair_enabled,
        "mitigation_enabled": intelligence.mitigation_enabled,
        "auto_correction_enabled": intelligence.auto_correction_enabled,
        "ranking_enabled": intelligence.ranking_enabled,
        "recommendation_enabled": intelligence.recommendation_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
    }
