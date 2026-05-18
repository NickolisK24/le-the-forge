"""Visibility helpers for v4.5B.8 trusted UX closeout."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_8_trusted_ux_closeout_models import (
    CLOSEOUT_DIAGNOSTIC_TYPES,
    FRONTEND_READINESS_TYPES,
    FRONTEND_READINESS_VISIBILITY_TYPES,
    INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    MIGRATION_DOCUMENT_COVERAGE_TYPES,
    PHASE_ARTIFACTS,
    PUBLIC_TRUST_CONTINUITY_TYPES,
    REPORT_COVERAGE_TYPES,
    TRUSTED_UX_CLOSEOUT_TYPES,
    UNSUPPORTED_STATE_CERTIFICATION_TYPES,
    UNSUPPORTED_TRUSTED_UX_OPERATIONAL_STATES,
    FrontendReadinessVisibilityRecord,
    GeneratedReportCoverageRecord,
    InheritedProhibitionCertificationRecord,
    MigrationDocumentCoverageRecord,
    PhaseCoverageRecord,
    PublicTrustContinuityRecord,
    TrustedUxCloseoutCertification,
    TrustedUxCloseoutDiagnosticRecord,
    TrustedUxCloseoutRecord,
    TrustedUxReadinessRecord,
    UnsupportedStateCertificationRecord,
    UnsupportedTrustedUxOperationalStateVisibility,
)


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_closeout_types(records: Iterable[TrustedUxCloseoutRecord]) -> dict[str, int]:
    return _count((record.closeout_type for record in records), TRUSTED_UX_CLOSEOUT_TYPES)


def count_readiness_types(records: Iterable[TrustedUxReadinessRecord]) -> dict[str, int]:
    return _count((record.readiness_type for record in records), FRONTEND_READINESS_TYPES)


def count_phase_labels(records: Iterable[PhaseCoverageRecord]) -> dict[str, int]:
    return _count((record.phase_label for record in records), tuple(item[0] for item in PHASE_ARTIFACTS))


def count_report_coverage_types(
    records: Iterable[GeneratedReportCoverageRecord],
) -> dict[str, int]:
    return _count((record.report_coverage_type for record in records), REPORT_COVERAGE_TYPES)


def count_migration_document_coverage_types(
    records: Iterable[MigrationDocumentCoverageRecord],
) -> dict[str, int]:
    return _count(
        (record.migration_document_coverage_type for record in records),
        MIGRATION_DOCUMENT_COVERAGE_TYPES,
    )


def count_public_trust_continuity_types(
    records: Iterable[PublicTrustContinuityRecord],
) -> dict[str, int]:
    return _count((record.continuity_type for record in records), PUBLIC_TRUST_CONTINUITY_TYPES)


def count_unsupported_state_types(
    records: Iterable[UnsupportedStateCertificationRecord],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state_type for record in records),
        UNSUPPORTED_STATE_CERTIFICATION_TYPES,
    )


def count_inherited_prohibition_types(
    records: Iterable[InheritedProhibitionCertificationRecord],
) -> dict[str, int]:
    return _count(
        (record.inherited_prohibition_type for record in records),
        INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    )


def count_frontend_readiness_types(
    records: Iterable[FrontendReadinessVisibilityRecord],
) -> dict[str, int]:
    return _count(
        (record.frontend_readiness_type for record in records),
        FRONTEND_READINESS_VISIBILITY_TYPES,
    )


def count_closeout_diagnostic_types(
    records: Iterable[TrustedUxCloseoutDiagnosticRecord],
) -> dict[str, int]:
    return _count((record.diagnostic_type for record in records), CLOSEOUT_DIAGNOSTIC_TYPES)


def count_unsupported_operational_states(
    records: Iterable[UnsupportedTrustedUxOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_TRUSTED_UX_OPERATIONAL_STATES,
    )


def trusted_ux_closeout_summary(
    records: Iterable[TrustedUxCloseoutRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "closeout_record_id": record.closeout_record_id,
            "closeout_type": record.closeout_type,
            "certification_state": record.certification_state,
            "descriptive_only": record.descriptive_only,
            "frontend_launch_authorization_enabled": (
                record.frontend_launch_authorization_enabled
            ),
            "production_enablement_enabled": record.production_enablement_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.closeout_record_id))
    ]


def trusted_ux_readiness_summary(
    records: Iterable[TrustedUxReadinessRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "readiness_record_id": record.readiness_record_id,
            "readiness_type": record.readiness_type,
            "readiness_classification": record.readiness_classification,
            "visibility_state": record.visibility_state,
            "descriptive_only": record.descriptive_only,
            "frontend_launch_enabled": record.frontend_launch_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
            "planner_integration_enabled": record.planner_integration_enabled,
            "runtime_enablement_enabled": record.runtime_enablement_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.readiness_record_id))
    ]


def phase_coverage_summary(
    records: Iterable[PhaseCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "phase_coverage_id": record.phase_coverage_id,
            "phase_label": record.phase_label,
            "phase_id": record.phase_id,
            "generated_report_reference": record.generated_report_reference,
            "generated_report_hash": record.generated_report_hash,
            "migration_document_reference": record.migration_document_reference,
            "coverage_state": record.coverage_state,
            "descriptive_only": record.descriptive_only,
            "frontend_launch_authorization_enabled": (
                record.frontend_launch_authorization_enabled
            ),
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.phase_coverage_id))
    ]


def report_coverage_summary(
    records: Iterable[GeneratedReportCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "report_coverage_id": record.report_coverage_id,
            "report_coverage_type": record.report_coverage_type,
            "phase_references": list(record.phase_references),
            "report_references": list(record.report_references),
            "expected_report_hashes": list(record.expected_report_hashes),
            "coverage_state": record.coverage_state,
            "descriptive_only": record.descriptive_only,
            "runtime_authority_enabled": record.runtime_authority_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.report_coverage_id))
    ]


def migration_document_summary(
    records: Iterable[MigrationDocumentCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "migration_document_coverage_id": record.migration_document_coverage_id,
            "migration_document_coverage_type": (
                record.migration_document_coverage_type
            ),
            "phase_references": list(record.phase_references),
            "migration_document_references": list(
                record.migration_document_references
            ),
            "coverage_state": record.coverage_state,
            "descriptive_only": record.descriptive_only,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.migration_document_coverage_id))
    ]


def public_trust_continuity_summary(
    records: Iterable[PublicTrustContinuityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_record_id": record.continuity_record_id,
            "continuity_type": record.continuity_type,
            "source_phase_id": record.source_phase_id,
            "continuity_reference_id": record.continuity_reference_id,
            "continuity_state": record.continuity_state,
            "descriptive_only": record.descriptive_only,
            "restoration_enabled": record.restoration_enabled,
            "repair_enabled": record.repair_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.continuity_record_id))
    ]


def unsupported_state_summary(
    records: Iterable[UnsupportedStateCertificationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_state_record_id": record.unsupported_state_record_id,
            "unsupported_state_type": record.unsupported_state_type,
            "preservation_state": record.preservation_state,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "suppression_enabled": record.suppression_enabled,
            "operational_fallback_enabled": record.operational_fallback_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.unsupported_state_record_id))
    ]


def inherited_prohibition_summary(
    records: Iterable[InheritedProhibitionCertificationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "inherited_prohibition_record_id": (
                record.inherited_prohibition_record_id
            ),
            "inherited_prohibition_type": record.inherited_prohibition_type,
            "preservation_state": record.preservation_state,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.inherited_prohibition_record_id))
    ]


def frontend_readiness_visibility_summary(
    records: Iterable[FrontendReadinessVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "frontend_readiness_id": record.frontend_readiness_id,
            "frontend_readiness_type": record.frontend_readiness_type,
            "visibility_state": record.visibility_state,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "frontend_launch_enabled": record.frontend_launch_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
            "planner_integration_enabled": record.planner_integration_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.frontend_readiness_id))
    ]


def trusted_ux_closeout_diagnostic_summary(
    records: Iterable[TrustedUxCloseoutDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "diagnostic_type": record.diagnostic_type,
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
            "scoring_enabled": record.scoring_enabled,
            "triage_enabled": record.triage_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]


def unsupported_operational_state_summary(
    records: Iterable[UnsupportedTrustedUxOperationalStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
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
            "scoring_enabled": record.scoring_enabled,
            "triage_enabled": record.triage_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
            "frontend_launch_enabled": record.frontend_launch_enabled,
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def readiness_classification_summary(
    records: Iterable[TrustedUxReadinessRecord],
) -> dict[str, str]:
    return {
        record.readiness_type: record.readiness_classification
        for record in sorted(records, key=lambda item: item.readiness_type)
    }


def descriptive_only_trusted_ux_summary(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    return {
        "descriptive_only": certification.descriptive_only,
        "publicly_transparent": certification.publicly_transparent,
        "trusted_ux_readiness_statement": certification.trusted_ux_readiness_statement,
        "trusted_ux_readiness_non_authority_statement": (
            certification.trusted_ux_readiness_non_authority_statement
        ),
        "non_operational": certification.non_operational,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
        "non_executing": certification.non_executing,
        "non_remediating": certification.non_remediating,
        "non_runtime_mutating": certification.non_runtime_mutating,
        "non_ranking": certification.non_ranking,
        "non_recommending": certification.non_recommending,
        "non_scoring": certification.non_scoring,
        "non_triaging": certification.non_triaging,
        "frontend_launch_authorization_enabled": (
            certification.frontend_launch_authorization_enabled
        ),
        "production_enablement_enabled": certification.production_enablement_enabled,
        "ui_authorization_enabled": certification.ui_authorization_enabled,
        "ui_approval_enabled": certification.ui_approval_enabled,
        "scoring_enabled": certification.scoring_enabled,
        "ranking_enabled": certification.ranking_enabled,
        "recommendation_enabled": certification.recommendation_enabled,
        "triage_enabled": certification.triage_enabled,
        "planner_integration_enabled": certification.planner_integration_enabled,
        "production_consumption_enabled": certification.production_consumption_enabled,
        "runtime_mutation_enabled": certification.runtime_mutation_enabled,
        "operational_mutation_enabled": certification.operational_mutation_enabled,
    }


def validate_required_trusted_ux_closeout_visibility(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    closeout_counts = count_closeout_types(certification.closeout_records)
    readiness_counts = count_readiness_types(certification.readiness_records)
    phase_counts = count_phase_labels(certification.phase_coverage_records)
    report_counts = count_report_coverage_types(certification.report_coverage_records)
    migration_counts = count_migration_document_coverage_types(
        certification.migration_document_coverage_records
    )
    continuity_counts = count_public_trust_continuity_types(
        certification.public_trust_continuity_records
    )
    unsupported_counts = count_unsupported_state_types(
        certification.unsupported_state_records
    )
    inherited_counts = count_inherited_prohibition_types(
        certification.inherited_prohibition_records
    )
    frontend_counts = count_frontend_readiness_types(
        certification.frontend_readiness_records
    )
    diagnostic_counts = count_closeout_diagnostic_types(
        certification.closeout_diagnostic_records
    )
    unsupported_operational_counts = count_unsupported_operational_states(
        certification.unsupported_operational_state_visibility
    )
    missing = {
        "missing_closeout_records": sorted(
            key for key, value in closeout_counts.items() if value < 1
        ),
        "missing_readiness_records": sorted(
            key for key, value in readiness_counts.items() if value < 1
        ),
        "missing_phase_coverage": sorted(
            key for key, value in phase_counts.items() if value < 1
        ),
        "missing_report_coverage": sorted(
            key for key, value in report_counts.items() if value < 1
        ),
        "missing_migration_document_coverage": sorted(
            key for key, value in migration_counts.items() if value < 1
        ),
        "missing_public_trust_continuity": sorted(
            key for key, value in continuity_counts.items() if value < 1
        ),
        "missing_unsupported_state_certification": sorted(
            key for key, value in unsupported_counts.items() if value < 1
        ),
        "missing_inherited_prohibition_certification": sorted(
            key for key, value in inherited_counts.items() if value < 1
        ),
        "missing_frontend_readiness_visibility": sorted(
            key for key, value in frontend_counts.items() if value < 1
        ),
        "missing_closeout_diagnostics": sorted(
            key for key, value in diagnostic_counts.items() if value < 1
        ),
        "missing_unsupported_operational_states": sorted(
            key for key, value in unsupported_operational_counts.items() if value < 1
        ),
    }
    return {
        "valid": not any(missing.values()),
        "closeout_counts": closeout_counts,
        "readiness_counts": readiness_counts,
        "phase_counts": phase_counts,
        "report_counts": report_counts,
        "migration_counts": migration_counts,
        "continuity_counts": continuity_counts,
        "unsupported_counts": unsupported_counts,
        "inherited_counts": inherited_counts,
        "frontend_counts": frontend_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }
