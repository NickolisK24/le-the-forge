"""Descriptive visibility helpers for v4.4 boundary intelligence foundations."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_intelligence_foundations_models import (
    BOUNDARY_INTELLIGENCE_STATES,
    BOUNDARY_STATE_BLOCKED,
    BOUNDARY_STATE_CONFLICTING,
    BOUNDARY_STATE_PROHIBITED,
    BOUNDARY_STATE_STALE,
    BOUNDARY_STATE_UNSUPPORTED,
    BoundaryDiagnosticRecord,
    BoundaryExplainabilityRecord,
    BoundaryFailVisibleFinding,
    BoundaryGovernanceVisibilitySummary,
    BoundaryIntelligenceFoundations,
    BoundaryIntelligenceRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_boundary_visibility_states(
    records: Iterable[BoundaryIntelligenceRecord],
) -> dict[str, int]:
    counts = Counter(record.visibility_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_INTELLIGENCE_STATES}


def count_boundary_classification_states(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, int]:
    counts = Counter(classification.visibility_state for classification in foundations.classifications)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_INTELLIGENCE_STATES}


def governance_safe_boundary_summaries(
    foundations: BoundaryIntelligenceFoundations,
) -> list[dict[str, Any]]:
    return [
        {
            "summary_id": summary.summary_id,
            "state_type": summary.state_type,
            "boundary_ids": _ordered_ids(summary.boundary_ids),
            "classification_ids": _ordered_ids(summary.classification_ids),
            "count": summary.count,
            "fail_visible": summary.fail_visible,
            "governance_safe": summary.governance_safe,
            "descriptive_only": summary.descriptive_only,
            "operational_authority": summary.operational_authority,
        }
        for summary in sorted(
            foundations.governance_visibility_summaries,
            key=lambda item: (item.deterministic_order, item.state_type),
        )
    ]


def aggregate_boundary_diagnostics(
    diagnostics: Iterable[BoundaryDiagnosticRecord],
) -> dict[str, Any]:
    diagnostics_tuple = tuple(diagnostics)
    by_state = Counter(diagnostic.visibility_state for diagnostic in diagnostics_tuple)
    by_severity = Counter(diagnostic.severity for diagnostic in diagnostics_tuple)
    return {
        "diagnostic_count": len(diagnostics_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_INTELLIGENCE_STATES
        },
        "severity_counts": {
            severity: int(by_severity[severity]) for severity in sorted(by_severity)
        },
        "diagnostic_ids": _ordered_ids(diagnostic.diagnostic_id for diagnostic in diagnostics_tuple),
        "fail_visible": all(diagnostic.fail_visible for diagnostic in diagnostics_tuple),
        "descriptive_only": all(diagnostic.descriptive_only for diagnostic in diagnostics_tuple),
        "auto_remediation_enabled_count": sum(
            1 for diagnostic in diagnostics_tuple if diagnostic.auto_remediation_enabled
        ),
        "repair_enabled_count": sum(1 for diagnostic in diagnostics_tuple if diagnostic.repair_enabled),
    }


def aggregate_explainability_visibility(
    explainability: Iterable[BoundaryExplainabilityRecord],
) -> dict[str, Any]:
    explainability_tuple = tuple(explainability)
    by_state = Counter(record.visibility_state for record in explainability_tuple)
    return {
        "explainability_count": len(explainability_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_INTELLIGENCE_STATES
        },
        "explainability_ids": _ordered_ids(
            record.explainability_id for record in explainability_tuple
        ),
        "explainability_first": all(record.explainability_first for record in explainability_tuple),
        "descriptive_only": all(record.descriptive_only for record in explainability_tuple),
        "recommendation_enabled_count": sum(
            1 for record in explainability_tuple if record.recommendation_enabled
        ),
        "decision_enabled_count": sum(1 for record in explainability_tuple if record.decision_enabled),
    }


def aggregate_fail_visible_findings(
    findings: Iterable[BoundaryFailVisibleFinding],
) -> dict[str, Any]:
    findings_tuple = tuple(findings)
    by_state = Counter(finding.visibility_state for finding in findings_tuple)
    return {
        "finding_count": len(findings_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_INTELLIGENCE_STATES
        },
        "finding_ids": _ordered_ids(finding.finding_id for finding in findings_tuple),
        "fail_visible": all(finding.fail_visible for finding in findings_tuple),
        "descriptive_only": all(finding.descriptive_only for finding in findings_tuple),
        "hidden_inference_used_count": sum(
            1 for finding in findings_tuple if finding.hidden_inference_used
        ),
        "remediation_enabled_count": sum(
            1 for finding in findings_tuple if finding.remediation_enabled
        ),
    }


def _findings_for_state(
    findings: Iterable[BoundaryFailVisibleFinding],
    state: str,
) -> list[dict[str, Any]]:
    return [
        {
            "finding_id": finding.finding_id,
            "boundary_id": finding.boundary_id,
            "finding_type": finding.finding_type,
            "visibility_state": finding.visibility_state,
            "finding_message": finding.finding_message,
            "evidence_reference_ids": _ordered_ids(finding.evidence_reference_ids),
            "fail_visible": finding.fail_visible,
            "hidden_inference_used": finding.hidden_inference_used,
            "remediation_enabled": finding.remediation_enabled,
        }
        for finding in sorted(
            (item for item in findings if item.visibility_state == state),
            key=lambda item: (item.deterministic_order, item.finding_id),
        )
    ]


def prohibited_state_visibility(
    foundations: BoundaryIntelligenceFoundations,
) -> list[dict[str, Any]]:
    return _findings_for_state(foundations.fail_visible_findings, BOUNDARY_STATE_PROHIBITED)


def unsupported_state_visibility(
    foundations: BoundaryIntelligenceFoundations,
) -> list[dict[str, Any]]:
    return _findings_for_state(foundations.fail_visible_findings, BOUNDARY_STATE_UNSUPPORTED)


def conflicting_state_visibility(
    foundations: BoundaryIntelligenceFoundations,
) -> list[dict[str, Any]]:
    return _findings_for_state(foundations.fail_visible_findings, BOUNDARY_STATE_CONFLICTING)


def stale_state_visibility(foundations: BoundaryIntelligenceFoundations) -> list[dict[str, Any]]:
    return _findings_for_state(foundations.fail_visible_findings, BOUNDARY_STATE_STALE)


def blocked_state_visibility(foundations: BoundaryIntelligenceFoundations) -> list[dict[str, Any]]:
    return _findings_for_state(foundations.fail_visible_findings, BOUNDARY_STATE_BLOCKED)


def fail_visible_summary(foundations: BoundaryIntelligenceFoundations) -> dict[str, Any]:
    findings = aggregate_fail_visible_findings(foundations.fail_visible_findings)
    return {
        "fail_visible_finding_count": findings["finding_count"],
        "prohibited_visibility_count": findings["state_counts"][BOUNDARY_STATE_PROHIBITED],
        "unsupported_visibility_count": findings["state_counts"][BOUNDARY_STATE_UNSUPPORTED],
        "blocked_visibility_count": findings["state_counts"][BOUNDARY_STATE_BLOCKED],
        "stale_visibility_count": findings["state_counts"][BOUNDARY_STATE_STALE],
        "conflicting_visibility_count": findings["state_counts"][BOUNDARY_STATE_CONFLICTING],
        "hidden_inference_used_count": findings["hidden_inference_used_count"],
        "remediation_enabled_count": findings["remediation_enabled_count"],
        "fail_visible": findings["fail_visible"],
        "descriptive_only": findings["descriptive_only"],
    }


def validate_governance_visibility_summaries(
    summaries: Iterable[BoundaryGovernanceVisibilitySummary],
    records: Iterable[BoundaryIntelligenceRecord],
) -> dict[str, Any]:
    records_tuple = tuple(records)
    summaries_tuple = tuple(summaries)
    record_counts = count_boundary_visibility_states(records_tuple)
    summary_counts = {summary.state_type: summary.count for summary in summaries_tuple}
    missing_states = [
        state
        for state in BOUNDARY_INTELLIGENCE_STATES
        if state not in summary_counts or summary_counts[state] != record_counts[state]
    ]
    return {
        "valid": not missing_states,
        "missing_or_mismatched_states": missing_states,
        "record_counts": record_counts,
        "summary_counts": {
            state: int(summary_counts.get(state, 0)) for state in BOUNDARY_INTELLIGENCE_STATES
        },
        "governance_safe": all(summary.governance_safe for summary in summaries_tuple),
        "descriptive_only": all(summary.descriptive_only for summary in summaries_tuple),
        "operational_authority_count": sum(
            1 for summary in summaries_tuple if summary.operational_authority
        ),
    }
