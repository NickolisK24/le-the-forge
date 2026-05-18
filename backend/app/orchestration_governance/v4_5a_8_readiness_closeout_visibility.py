"""Visibility helpers for v4.5A.8 readiness closeout."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_8_readiness_closeout_models import (
    CLOSEOUT_DIAGNOSTIC_TYPES,
    CONTINUITY_CERTIFICATION_TYPES,
    INHERITED_PROHIBITION_PRESERVATION_TYPES,
    PHASE_COVERAGE_TYPES,
    READINESS_TARGETS,
    READINESS_VISIBILITY_TYPES,
    UNSUPPORTED_READINESS_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_PRESERVATION_TYPES,
    CloseoutDiagnosticRecord,
    CloseoutRecord,
    ContinuityCertification,
    GeneratedReportCoverageCertification,
    InheritedProhibitionPreservationCertification,
    MigrationDocumentCoverageCertification,
    PhaseCoverageCertification,
    ReadinessCertificationRecord,
    ReadinessCloseoutIntelligence,
    ReadinessVisibility,
    UnsupportedReadinessVisibility,
    UnsupportedStatePreservationCertification,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_phase_coverage_types(
    records: Iterable[PhaseCoverageCertification],
) -> dict[str, int]:
    counts = Counter(record.phase_id for record in records)
    return {item: int(counts.get(item, 0)) for item in PHASE_COVERAGE_TYPES}


def count_report_coverage_types(
    records: Iterable[GeneratedReportCoverageCertification],
) -> dict[str, int]:
    counts = Counter(record.phase_id for record in records)
    return {item: int(counts.get(item, 0)) for item in PHASE_COVERAGE_TYPES}


def count_migration_document_types(
    records: Iterable[MigrationDocumentCoverageCertification],
) -> dict[str, int]:
    counts = Counter(record.phase_id for record in records)
    return {item: int(counts.get(item, 0)) for item in PHASE_COVERAGE_TYPES}


def count_continuity_certification_types(
    records: Iterable[ContinuityCertification],
) -> dict[str, int]:
    counts = Counter(record.continuity_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CONTINUITY_CERTIFICATION_TYPES}


def count_unsupported_state_preservation_types(
    records: Iterable[UnsupportedStatePreservationCertification],
) -> dict[str, int]:
    counts = Counter(record.preservation_type for record in records)
    return {item: int(counts.get(item, 0)) for item in UNSUPPORTED_STATE_PRESERVATION_TYPES}


def count_inherited_prohibition_types(
    records: Iterable[InheritedProhibitionPreservationCertification],
) -> dict[str, int]:
    counts = Counter(record.preservation_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in INHERITED_PROHIBITION_PRESERVATION_TYPES
    }


def count_readiness_targets(
    records: Iterable[ReadinessCertificationRecord],
) -> dict[str, int]:
    counts = Counter(record.readiness_target for record in records)
    return {item: int(counts.get(item, 0)) for item in READINESS_TARGETS}


def count_readiness_visibility_types(
    records: Iterable[ReadinessVisibility],
) -> dict[str, int]:
    counts = Counter(record.readiness_visibility_type for record in records)
    return {item: int(counts.get(item, 0)) for item in READINESS_VISIBILITY_TYPES}


def count_closeout_diagnostic_types(
    records: Iterable[CloseoutDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CLOSEOUT_DIAGNOSTIC_TYPES}


def count_unsupported_readiness_states(
    records: Iterable[UnsupportedReadinessVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_READINESS_OPERATIONAL_STATES
    }


def closeout_summary_visibility(
    records: Iterable[CloseoutRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "closeout_record_id": record.closeout_record_id,
            "closeout_id": record.closeout_id,
            "readiness_id": record.readiness_id,
            "phase_chain_id": record.phase_chain_id,
            "certification_chain_id": record.certification_chain_id,
            "evidence_chain_id": record.evidence_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "non_authorizing": record.non_authorizing,
            "non_approving": record.non_approving,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "execution_enabled": record.execution_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.closeout_record_id))
    ]


def readiness_summary_visibility(
    records: Iterable[ReadinessCertificationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "readiness_record_id": record.readiness_record_id,
            "readiness_id": record.readiness_id,
            "readiness_target": record.readiness_target,
            "readiness_classification": record.readiness_classification,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "non_authorizing": record.non_authorizing,
            "non_approving": record.non_approving,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
            "runtime_enablement_enabled": record.runtime_enablement_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.readiness_record_id))
    ]


def phase_coverage_summary_visibility(
    records: Iterable[PhaseCoverageCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "phase_coverage_id": record.phase_coverage_id,
            "phase_id": record.phase_id,
            "report_reference": record.report_reference,
            "report_hash_reference": record.report_hash_reference,
            "migration_document_reference": record.migration_document_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "coverage_certified": record.coverage_certified,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_readiness_enabled": record.operational_readiness_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.phase_coverage_id))
    ]


def report_coverage_summary_visibility(
    records: Iterable[GeneratedReportCoverageCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "report_coverage_id": record.report_coverage_id,
            "phase_id": record.phase_id,
            "report_reference": record.report_reference,
            "report_hash_reference": record.report_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "report_present": record.report_present,
            "report_continuity_preserved": record.report_continuity_preserved,
            "hashing_stability_preserved": record.hashing_stability_preserved,
            "replay_stability_preserved": record.replay_stability_preserved,
            "evidence_continuity_preserved": record.evidence_continuity_preserved,
            "descriptive_only": record.descriptive_only,
            "runtime_authority_enabled": record.runtime_authority_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.report_coverage_id))
    ]


def migration_document_summary_visibility(
    records: Iterable[MigrationDocumentCoverageCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "document_coverage_id": record.document_coverage_id,
            "phase_id": record.phase_id,
            "migration_document_reference": record.migration_document_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "document_present": record.document_present,
            "document_continuity_preserved": record.document_continuity_preserved,
            "coverage_integrity_preserved": record.coverage_integrity_preserved,
            "replay_visibility_preserved": record.replay_visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "operational_readiness_enabled": record.operational_readiness_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.document_coverage_id))
    ]


def continuity_certification_summary_visibility(
    records: Iterable[ContinuityCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_certification_id": record.continuity_certification_id,
            "continuity_type": record.continuity_type,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "continuity_certified": record.continuity_certified,
            "descriptive_only": record.descriptive_only,
            "restoration_enabled": record.restoration_enabled,
            "repair_enabled": record.repair_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.continuity_certification_id))
    ]


def unsupported_state_summary_visibility(
    records: Iterable[UnsupportedStatePreservationCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_certification_id": record.unsupported_certification_id,
            "preservation_type": record.preservation_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "preservation_certified": record.preservation_certified,
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "suppression_enabled": record.suppression_enabled,
            "authorization_enabled": record.authorization_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.unsupported_certification_id))
    ]


def inherited_prohibition_summary_visibility(
    records: Iterable[InheritedProhibitionPreservationCertification],
) -> list[dict[str, Any]]:
    return [
        {
            "prohibition_certification_id": record.prohibition_certification_id,
            "preservation_type": record.preservation_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "preservation_certified": record.preservation_certified,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_behavior_enabled": record.operational_behavior_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.prohibition_certification_id))
    ]


def readiness_visibility_summary(
    records: Iterable[ReadinessVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "readiness_visibility_id": record.readiness_visibility_id,
            "readiness_visibility_type": record.readiness_visibility_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "visibility_preserved": record.visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
            "runtime_enablement_enabled": record.runtime_enablement_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.readiness_visibility_id))
    ]


def fail_visible_closeout_diagnostic_summaries(
    records: Iterable[CloseoutDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "diagnostic_type": record.diagnostic_type,
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


def unsupported_readiness_visibility_summaries(
    records: Iterable[UnsupportedReadinessVisibility],
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


def validate_required_readiness_closeout_visibility(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    phase_counts = count_phase_coverage_types(intelligence.phase_coverage_certifications)
    report_counts = count_report_coverage_types(intelligence.report_coverage_certifications)
    document_counts = count_migration_document_types(
        intelligence.migration_document_certifications
    )
    continuity_counts = count_continuity_certification_types(
        intelligence.continuity_certifications
    )
    unsupported_counts = count_unsupported_state_preservation_types(
        intelligence.unsupported_state_certifications
    )
    prohibition_counts = count_inherited_prohibition_types(
        intelligence.inherited_prohibition_certifications
    )
    readiness_counts = count_readiness_targets(intelligence.readiness_certifications)
    readiness_visibility_counts = count_readiness_visibility_types(
        intelligence.readiness_visibility
    )
    diagnostic_counts = count_closeout_diagnostic_types(
        intelligence.closeout_diagnostics
    )
    unsupported_state_counts = count_unsupported_readiness_states(
        intelligence.unsupported_readiness_visibility
    )
    missing_phase_types = [key for key, count in phase_counts.items() if count <= 0]
    missing_report_types = [key for key, count in report_counts.items() if count <= 0]
    missing_document_types = [key for key, count in document_counts.items() if count <= 0]
    missing_continuity_types = [
        key for key, count in continuity_counts.items() if count <= 0
    ]
    missing_unsupported_types = [
        key for key, count in unsupported_counts.items() if count <= 0
    ]
    missing_prohibition_types = [
        key for key, count in prohibition_counts.items() if count <= 0
    ]
    missing_readiness_targets = [
        key for key, count in readiness_counts.items() if count <= 0
    ]
    missing_readiness_visibility_types = [
        key for key, count in readiness_visibility_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        key for key, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_states = [
        key for key, count in unsupported_state_counts.items() if count <= 0
    ]
    return {
        "valid": not (
            missing_phase_types
            or missing_report_types
            or missing_document_types
            or missing_continuity_types
            or missing_unsupported_types
            or missing_prohibition_types
            or missing_readiness_targets
            or missing_readiness_visibility_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "phase_counts": phase_counts,
        "report_counts": report_counts,
        "document_counts": document_counts,
        "continuity_counts": continuity_counts,
        "unsupported_counts": unsupported_counts,
        "prohibition_counts": prohibition_counts,
        "readiness_counts": readiness_counts,
        "readiness_visibility_counts": readiness_visibility_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_state_counts,
        "missing_phase_types": missing_phase_types,
        "missing_report_types": missing_report_types,
        "missing_document_types": missing_document_types,
        "missing_continuity_types": missing_continuity_types,
        "missing_unsupported_types": missing_unsupported_types,
        "missing_prohibition_types": missing_prohibition_types,
        "missing_readiness_targets": missing_readiness_targets,
        "missing_readiness_visibility_types": missing_readiness_visibility_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_readiness_closeout_summary(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
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
        "readiness_authorization_enabled": intelligence.readiness_authorization_enabled,
        "readiness_approval_enabled": intelligence.readiness_approval_enabled,
        "remediation_enabled": intelligence.remediation_enabled,
        "repair_enabled": intelligence.repair_enabled,
        "mitigation_enabled": intelligence.mitigation_enabled,
        "auto_correction_enabled": intelligence.auto_correction_enabled,
        "ranking_enabled": intelligence.ranking_enabled,
        "recommendation_enabled": intelligence.recommendation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
