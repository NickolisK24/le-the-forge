"""Visibility helpers for v4.5B.1 trust visibility foundations."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_1_trust_visibility_foundation_models import (
    GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES,
    PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES,
    PUBLIC_INTEGRITY_VISIBILITY_TYPES,
    PUBLIC_TRUST_DIAGNOSTIC_TYPES,
    PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES,
    TRUST_SUMMARY_TYPES,
    UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_VISIBILITY_TYPES,
    GovernanceTransparencyVisibility,
    PublicExplainabilityVisibility,
    PublicIntegrityVisibility,
    PublicTrustDiagnosticRecord,
    PublicTrustEvidenceVisibility,
    TrustSummaryRecord,
    TrustVisibilityFoundationIntelligence,
    TrustVisibilityRecord,
    UnsupportedPublicTrustVisibility,
    UnsupportedStateVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_evidence_visibility_types(
    records: Iterable[PublicTrustEvidenceVisibility],
) -> dict[str, int]:
    counts = Counter(record.evidence_visibility_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES
    }


def count_unsupported_state_visibility_types(
    records: Iterable[UnsupportedStateVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state_type for record in records)
    return {item: int(counts.get(item, 0)) for item in UNSUPPORTED_STATE_VISIBILITY_TYPES}


def count_governance_transparency_visibility_types(
    records: Iterable[GovernanceTransparencyVisibility],
) -> dict[str, int]:
    counts = Counter(record.transparency_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES
    }


def count_trust_summary_types(
    records: Iterable[TrustSummaryRecord],
) -> dict[str, int]:
    counts = Counter(record.summary_type for record in records)
    return {item: int(counts.get(item, 0)) for item in TRUST_SUMMARY_TYPES}


def count_explainability_visibility_types(
    records: Iterable[PublicExplainabilityVisibility],
) -> dict[str, int]:
    counts = Counter(record.explainability_visibility_type for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES
    }


def count_integrity_visibility_types(
    records: Iterable[PublicIntegrityVisibility],
) -> dict[str, int]:
    counts = Counter(record.integrity_visibility_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PUBLIC_INTEGRITY_VISIBILITY_TYPES}


def count_public_trust_diagnostic_types(
    records: Iterable[PublicTrustDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PUBLIC_TRUST_DIAGNOSTIC_TYPES}


def count_unsupported_public_trust_states(
    records: Iterable[UnsupportedPublicTrustVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES
    }


def trust_visibility_summary(
    records: Iterable[TrustVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "trust_record_id": record.trust_record_id,
            "trust_visibility_id": record.trust_visibility_id,
            "trust_summary_id": record.trust_summary_id,
            "transparency_reference_id": record.transparency_reference_id,
            "evidence_reference_id": record.evidence_reference_id,
            "continuity_reference_id": record.continuity_reference_id,
            "explainability_reference_id": record.explainability_reference_id,
            "integrity_reference_id": record.integrity_reference_id,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "unsupported_state_reference_id": record.unsupported_state_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "descriptive_only": record.descriptive_only,
            "publicly_transparent": record.publicly_transparent,
            "fail_visible": record.fail_visible,
            "trust_authority_enabled": record.trust_authority_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.trust_record_id),
        )
    ]


def evidence_visibility_summary(
    records: Iterable[PublicTrustEvidenceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_visibility_id": record.evidence_visibility_id,
            "evidence_visibility_type": record.evidence_visibility_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "visibility_preserved": record.visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "replay_safe": record.replay_safe,
            "provenance_safe": record.provenance_safe,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "scoring_enabled": record.scoring_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_visibility_id),
        )
    ]


def unsupported_state_summary(
    records: Iterable[UnsupportedStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_visibility_id": record.unsupported_visibility_id,
            "unsupported_state_type": record.unsupported_state_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "visibility_preserved": record.visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "suppression_enabled": record.suppression_enabled,
            "hidden_fallback_enabled": record.hidden_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.unsupported_visibility_id),
        )
    ]


def governance_transparency_summary(
    records: Iterable[GovernanceTransparencyVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "transparency_visibility_id": record.transparency_visibility_id,
            "transparency_type": record.transparency_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "visibility_preserved": record.visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "public_visibility": record.public_visibility,
            "operational_approval_enabled": record.operational_approval_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.transparency_visibility_id,
            ),
        )
    ]


def trust_summary_visibility(
    records: Iterable[TrustSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "trust_summary_record_id": record.trust_summary_record_id,
            "trust_summary_id": record.trust_summary_id,
            "summary_type": record.summary_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "summary_state": record.summary_state,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.trust_summary_record_id),
        )
    ]


def explainability_summary(
    records: Iterable[PublicExplainabilityVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_visibility_id": record.explainability_visibility_id,
            "explainability_visibility_type": record.explainability_visibility_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "visibility_preserved": record.visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "decision_enabled": record.decision_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.explainability_visibility_id,
            ),
        )
    ]


def integrity_summary(
    records: Iterable[PublicIntegrityVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "integrity_visibility_id": record.integrity_visibility_id,
            "integrity_visibility_type": record.integrity_visibility_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "visibility_preserved": record.visibility_preserved,
            "descriptive_only": record.descriptive_only,
            "operational_semantics_enabled": record.operational_semantics_enabled,
            "approval_enabled": record.approval_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.integrity_visibility_id),
        )
    ]


def diagnostics_summary(
    records: Iterable[PublicTrustDiagnosticRecord],
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
            "hidden_fallback_enabled": record.hidden_fallback_enabled,
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
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_public_trust_summary(
    records: Iterable[UnsupportedPublicTrustVisibility],
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
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]


def validate_required_trust_visibility_foundation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    evidence_counts = count_evidence_visibility_types(intelligence.evidence_visibility)
    unsupported_counts = count_unsupported_state_visibility_types(
        intelligence.unsupported_state_visibility
    )
    transparency_counts = count_governance_transparency_visibility_types(
        intelligence.governance_transparency_visibility
    )
    summary_counts = count_trust_summary_types(intelligence.trust_summaries)
    explainability_counts = count_explainability_visibility_types(
        intelligence.explainability_visibility
    )
    integrity_counts = count_integrity_visibility_types(intelligence.integrity_visibility)
    diagnostic_counts = count_public_trust_diagnostic_types(
        intelligence.public_trust_diagnostics
    )
    unsupported_operational_counts = count_unsupported_public_trust_states(
        intelligence.unsupported_public_trust_visibility
    )
    missing_evidence_types = sorted(
        key for key, value in evidence_counts.items() if value < 1
    )
    missing_unsupported_types = sorted(
        key for key, value in unsupported_counts.items() if value < 1
    )
    missing_transparency_types = sorted(
        key for key, value in transparency_counts.items() if value < 1
    )
    missing_summary_types = sorted(
        key for key, value in summary_counts.items() if value < 1
    )
    missing_explainability_types = sorted(
        key for key, value in explainability_counts.items() if value < 1
    )
    missing_integrity_types = sorted(
        key for key, value in integrity_counts.items() if value < 1
    )
    missing_diagnostic_types = sorted(
        key for key, value in diagnostic_counts.items() if value < 1
    )
    missing_unsupported_states = sorted(
        key for key, value in unsupported_operational_counts.items() if value < 1
    )
    return {
        "valid": not (
            missing_evidence_types
            or missing_unsupported_types
            or missing_transparency_types
            or missing_summary_types
            or missing_explainability_types
            or missing_integrity_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "evidence_counts": evidence_counts,
        "unsupported_counts": unsupported_counts,
        "transparency_counts": transparency_counts,
        "summary_counts": summary_counts,
        "explainability_counts": explainability_counts,
        "integrity_counts": integrity_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        "missing_evidence_types": missing_evidence_types,
        "missing_unsupported_types": missing_unsupported_types,
        "missing_transparency_types": missing_transparency_types,
        "missing_summary_types": missing_summary_types,
        "missing_explainability_types": missing_explainability_types,
        "missing_integrity_types": missing_integrity_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_public_trust_summary(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "public_trust_visibility_statement": (
            intelligence.public_trust_visibility_statement
        ),
        "trust_visibility_non_authority_statement": (
            intelligence.trust_visibility_non_authority_statement
        ),
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "trust_authorization_enabled": intelligence.trust_authorization_enabled,
        "trust_approval_enabled": intelligence.trust_approval_enabled,
        "trust_ranking_enabled": intelligence.trust_ranking_enabled,
        "trust_recommendation_enabled": intelligence.trust_recommendation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
