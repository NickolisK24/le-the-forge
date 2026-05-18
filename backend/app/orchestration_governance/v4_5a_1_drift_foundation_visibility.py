"""Descriptive visibility helpers for v4.5A.1 drift foundations."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_1_drift_foundation_models import (
    DRIFT_CLASSIFICATION_CATEGORIES,
    DRIFT_CONTINUITY_TYPES,
    DRIFT_DIAGNOSTIC_TYPES,
    DRIFT_EVIDENCE_TYPES,
    DRIFT_SEVERITY_LEVELS,
    UNSUPPORTED_DRIFT_OPERATIONAL_STATES,
    DriftClassificationRecord,
    DriftContinuityVisibility,
    DriftDiagnosticRecord,
    DriftEvidenceReference,
    DriftFoundationIntelligence,
    DriftIdentityRecord,
    DriftSeverityVisibility,
    UnsupportedDriftStateVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_drift_categories(
    classifications: Iterable[DriftClassificationRecord],
) -> dict[str, int]:
    counts = Counter(record.category for record in classifications)
    return {category: int(counts.get(category, 0)) for category in DRIFT_CLASSIFICATION_CATEGORIES}


def count_drift_severity_levels(
    classifications: Iterable[DriftClassificationRecord],
    diagnostics: Iterable[DriftDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.severity for record in classifications)
    counts.update(record.severity for record in diagnostics)
    return {severity: int(counts.get(severity, 0)) for severity in DRIFT_SEVERITY_LEVELS}


def count_evidence_types(
    evidence_references: Iterable[DriftEvidenceReference],
) -> dict[str, int]:
    counts = Counter(record.evidence_type for record in evidence_references)
    return {evidence_type: int(counts.get(evidence_type, 0)) for evidence_type in DRIFT_EVIDENCE_TYPES}


def count_continuity_types(
    continuity_records: Iterable[DriftContinuityVisibility],
) -> dict[str, int]:
    counts = Counter(record.continuity_type for record in continuity_records)
    return {continuity_type: int(counts.get(continuity_type, 0)) for continuity_type in DRIFT_CONTINUITY_TYPES}


def count_diagnostic_types(
    diagnostics: Iterable[DriftDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in diagnostics)
    return {diagnostic_type: int(counts.get(diagnostic_type, 0)) for diagnostic_type in DRIFT_DIAGNOSTIC_TYPES}


def count_unsupported_operational_states(
    states: Iterable[UnsupportedDriftStateVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in states)
    return {
        unsupported_state: int(counts.get(unsupported_state, 0))
        for unsupported_state in UNSUPPORTED_DRIFT_OPERATIONAL_STATES
    }


def drift_summary_visibility(
    foundations: DriftFoundationIntelligence,
) -> list[dict[str, Any]]:
    classification_by_drift = {
        classification.drift_id: classification
        for classification in foundations.classifications
    }
    return [
        {
            "drift_id": record.drift_id,
            "boundary_id": record.boundary_id,
            "source_boundary_id": record.source_boundary_id,
            "inherited_boundary_id": record.inherited_boundary_id,
            "refinement_boundary_id": record.refinement_boundary_id,
            "governance_scope_id": record.governance_scope_id,
            "continuity_chain_id": record.continuity_chain_id,
            "category": classification_by_drift[record.drift_id].category,
            "severity": classification_by_drift[record.drift_id].severity,
            "descriptive_only": record.descriptive_only,
            "non_operational": record.non_operational,
        }
        for record in sorted(
            foundations.drift_identities,
            key=lambda item: (item.deterministic_order, item.drift_id),
        )
    ]


def severity_summary_visibility(
    severity_records: Iterable[DriftSeverityVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "severity_id": record.severity_id,
            "severity": record.severity,
            "drift_ids": _ordered_ids(record.drift_ids),
            "diagnostic_ids": _ordered_ids(record.diagnostic_ids),
            "count": record.count,
            "non_remediating": record.non_remediating,
            "non_authorizing": record.non_authorizing,
            "non_operational": record.non_operational,
            "remediation_enabled": record.remediation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "operational_behavior_enabled": record.operational_behavior_enabled,
        }
        for record in sorted(
            severity_records,
            key=lambda item: (item.deterministic_order, item.severity_id),
        )
    ]


def evidence_summary_visibility(
    evidence_references: Iterable[DriftEvidenceReference],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": record.evidence_id,
            "drift_id": record.drift_id,
            "evidence_type": record.evidence_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "replay_safe": record.replay_safe,
            "rollback_safe": record.rollback_safe,
            "provenance_safe": record.provenance_safe,
            "lineage_safe": record.lineage_safe,
            "integrity_safe": record.integrity_safe,
            "hidden_inference_used": record.hidden_inference_used,
            "production_consumption_enabled": record.production_consumption_enabled,
        }
        for record in sorted(
            evidence_references,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]


def continuity_summary_visibility(
    continuity_records: Iterable[DriftContinuityVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_id": record.continuity_id,
            "drift_id": record.drift_id,
            "continuity_type": record.continuity_type,
            "continuity_chain_id": record.continuity_chain_id,
            "source_reference_id": record.source_reference_id,
            "target_reference_id": record.target_reference_id,
            "visibility_state": record.visibility_state,
            "continuity_preserved": record.continuity_preserved,
            "lineage_safe": record.lineage_safe,
            "provenance_safe": record.provenance_safe,
            "integrity_safe": record.integrity_safe,
            "repair_enabled": record.repair_enabled,
            "remediation_enabled": record.remediation_enabled,
            "runtime_mutation_enabled": record.runtime_mutation_enabled,
        }
        for record in sorted(
            continuity_records,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]


def fail_visible_diagnostic_summaries(
    diagnostics: Iterable[DriftDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "drift_id": record.drift_id,
            "diagnostic_type": record.diagnostic_type,
            "severity": record.severity,
            "visibility_state": record.visibility_state,
            "message": record.message,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "hidden_fallback_used": record.hidden_fallback_used,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
            "authorization_behavior_enabled": record.authorization_behavior_enabled,
        }
        for record in sorted(
            diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_state_visibility_summaries(
    unsupported_states: Iterable[UnsupportedDriftStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "visibility_state": record.visibility_state,
            "explicit_reason": record.explicit_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "operational_enabled": record.operational_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            unsupported_states,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]


def validate_required_drift_visibility(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    category_counts = count_drift_categories(foundations.classifications)
    severity_counts = count_drift_severity_levels(
        foundations.classifications,
        foundations.diagnostics,
    )
    evidence_counts = count_evidence_types(foundations.evidence_references)
    continuity_counts = count_continuity_types(foundations.continuity_visibility)
    diagnostic_counts = count_diagnostic_types(foundations.diagnostics)
    unsupported_counts = count_unsupported_operational_states(
        foundations.unsupported_state_visibility
    )
    missing_categories = [
        category for category, count in category_counts.items() if count <= 0
    ]
    missing_severities = [
        severity for severity, count in severity_counts.items() if count <= 0
    ]
    missing_evidence_types = [
        evidence_type for evidence_type, count in evidence_counts.items() if count <= 0
    ]
    missing_continuity_types = [
        continuity_type for continuity_type, count in continuity_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        diagnostic_type for diagnostic_type, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_states = [
        unsupported_state
        for unsupported_state, count in unsupported_counts.items()
        if count <= 0
    ]
    return {
        "valid": not (
            missing_categories
            or missing_severities
            or missing_evidence_types
            or missing_continuity_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "category_counts": category_counts,
        "severity_counts": severity_counts,
        "evidence_counts": evidence_counts,
        "continuity_counts": continuity_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_counts,
        "missing_categories": missing_categories,
        "missing_severities": missing_severities,
        "missing_evidence_types": missing_evidence_types,
        "missing_continuity_types": missing_continuity_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_visibility_summary(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": foundations.descriptive_only,
        "non_operational": foundations.non_operational,
        "non_executing": foundations.non_executing,
        "non_authorizing": foundations.non_authorizing,
        "non_remediating": foundations.non_remediating,
        "non_runtime_mutating": foundations.non_runtime_mutating,
        "non_operational_mutating": foundations.non_operational_mutating,
        "non_routing": foundations.non_routing,
        "non_dispatching": foundations.non_dispatching,
        "non_scheduling": foundations.non_scheduling,
        "non_sequencing": foundations.non_sequencing,
        "non_recommending": foundations.non_recommending,
        "non_deciding": foundations.non_deciding,
        "planner_integration_enabled": foundations.planner_integration_enabled,
        "planner_execution_enabled": foundations.planner_execution_enabled,
        "production_consumption_enabled": foundations.production_consumption_enabled,
        "runtime_execution_enabled": foundations.runtime_execution_enabled,
        "runtime_mutation_enabled": foundations.runtime_mutation_enabled,
        "operational_mutation_enabled": foundations.operational_mutation_enabled,
        "remediation_enabled": foundations.remediation_enabled,
        "repair_enabled": foundations.repair_enabled,
        "auto_correction_enabled": foundations.auto_correction_enabled,
    }
