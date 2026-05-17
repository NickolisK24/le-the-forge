"""Fail-visible operational integrity enforcement visibility helpers."""

from __future__ import annotations

from .integrity_enforcement_models import (
    INTEGRITY_FINDING_APPROVAL_LEAKAGE,
    INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE,
    INTEGRITY_FINDING_BOUNDARY,
    INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION,
    INTEGRITY_FINDING_EVIDENCE_CONTINUITY,
    INTEGRITY_FINDING_EXECUTION_LEAKAGE,
    INTEGRITY_FINDING_FALLBACK_LEAKAGE,
    INTEGRITY_FINDING_LINEAGE_CONTINUITY,
    INTEGRITY_FINDING_MUTATION_LEAKAGE,
    INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE,
    INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE,
    INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE,
    INTEGRITY_FINDING_PROHIBITED_STATE,
    INTEGRITY_FINDING_PROVENANCE_CONTINUITY,
    INTEGRITY_FINDING_RANKING_LEAKAGE,
    INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE,
    INTEGRITY_FINDING_REMEDIATION_LEAKAGE,
    INTEGRITY_FINDING_REPLAY_CONTINUITY,
    INTEGRITY_FINDING_ROLLBACK_CONTINUITY,
    INTEGRITY_FINDING_SCORING_LEAKAGE,
    INTEGRITY_FINDING_SELECTION_LEAKAGE,
    INTEGRITY_SEVERITY_BLOCKING,
    INTEGRITY_SEVERITY_CRITICAL,
    INTEGRITY_SEVERITY_PROHIBITED,
    INTEGRITY_SEVERITY_UNKNOWN,
    INTEGRITY_SEVERITY_WARNING,
    OPERATIONAL_INTEGRITY_FINDING_TYPES,
    OPERATIONAL_INTEGRITY_SEVERITIES,
    OperationalIntegrityFinding,
    OperationalIntegrityReport,
)


def count_integrity_finding_types(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> dict[str, int]:
    counts = {finding_type: 0 for finding_type in OPERATIONAL_INTEGRITY_FINDING_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.finding_type in counts:
            counts[finding.finding_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_integrity_severities(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> dict[str, int]:
    counts = {severity: 0 for severity in OPERATIONAL_INTEGRITY_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def violation_integrity_count(report: OperationalIntegrityReport) -> int:
    leakage_values = (
        report.execution_leakage_detected,
        report.orchestration_leakage_detected,
        report.remediation_leakage_detected,
        report.recommendation_leakage_detected,
        report.ranking_leakage_detected,
        report.scoring_leakage_detected,
        report.selection_leakage_detected,
        report.approval_leakage_detected,
        report.authorization_leakage_detected,
        report.mutation_leakage_detected,
        report.production_consumption_leakage_detected,
        report.planner_integration_leakage_detected,
    )
    return sum(1 for value in leakage_values if value)


def warning_integrity_count(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == INTEGRITY_SEVERITY_WARNING)


def blocked_integrity_count(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == INTEGRITY_SEVERITY_BLOCKING)


def prohibited_integrity_count(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == INTEGRITY_SEVERITY_PROHIBITED)


def unknown_integrity_count(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == INTEGRITY_SEVERITY_UNKNOWN)


def critical_integrity_count(
    findings: tuple[OperationalIntegrityFinding, ...] | list[OperationalIntegrityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == INTEGRITY_SEVERITY_CRITICAL)


def build_operational_integrity_visibility(report: OperationalIntegrityReport) -> dict[str, object]:
    findings = report.findings
    finding_type_counts = count_integrity_finding_types(findings)
    return {
        "finding_type_counts": finding_type_counts,
        "severity_counts": count_integrity_severities(findings),
        "violation_count": report.violation_count,
        "warning_count": report.warning_count,
        "blocked_count": report.blocked_count,
        "prohibited_count": report.prohibited_count,
        "unknown_count": report.unknown_count,
        "critical_count": report.critical_count,
        "execution_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_EXECUTION_LEAKAGE] > 0,
        "orchestration_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE] > 0,
        "remediation_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_REMEDIATION_LEAKAGE] > 0,
        "recommendation_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE] > 0,
        "ranking_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_RANKING_LEAKAGE] > 0,
        "scoring_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_SCORING_LEAKAGE] > 0,
        "selection_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_SELECTION_LEAKAGE] > 0,
        "approval_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_APPROVAL_LEAKAGE] > 0,
        "authorization_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE] > 0,
        "mutation_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_MUTATION_LEAKAGE] > 0,
        "production_consumption_leakage_check_visible": (
            finding_type_counts[INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE] > 0
        ),
        "planner_integration_leakage_check_visible": (
            finding_type_counts[INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE] > 0
        ),
        "fallback_leakage_check_visible": finding_type_counts[INTEGRITY_FINDING_FALLBACK_LEAKAGE] > 0,
        "diagnostic_suppression_check_visible": finding_type_counts[INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION] > 0,
        "evidence_continuity_check_visible": finding_type_counts[INTEGRITY_FINDING_EVIDENCE_CONTINUITY] > 0,
        "provenance_continuity_check_visible": finding_type_counts[INTEGRITY_FINDING_PROVENANCE_CONTINUITY] > 0,
        "lineage_continuity_check_visible": finding_type_counts[INTEGRITY_FINDING_LINEAGE_CONTINUITY] > 0,
        "replay_continuity_check_visible": finding_type_counts[INTEGRITY_FINDING_REPLAY_CONTINUITY] > 0,
        "rollback_continuity_check_visible": finding_type_counts[INTEGRITY_FINDING_ROLLBACK_CONTINUITY] > 0,
        "prohibited_state_check_visible": finding_type_counts[INTEGRITY_FINDING_PROHIBITED_STATE] > 0,
        "integrity_boundary_check_visible": finding_type_counts[INTEGRITY_FINDING_BOUNDARY] > 0,
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
    }


def validate_operational_integrity_visibility(report: OperationalIntegrityReport) -> dict[str, object]:
    visibility = build_operational_integrity_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.correction_enabled,
            report.remediation_enabled,
            report.repair_enabled,
            report.approval_enabled,
            report.authorization_enabled,
            report.execution_enabled,
            report.orchestration_execution_enabled,
            report.recommendation_enabled,
            report.ranking_enabled,
            report.scoring_enabled,
            report.selection_enabled,
            report.optimization_enabled,
            report.runtime_mutation_enabled,
        )
        if enabled
    )
    required_visibility = all(
        visibility[key]
        for key in (
            "execution_leakage_check_visible",
            "orchestration_leakage_check_visible",
            "remediation_leakage_check_visible",
            "recommendation_leakage_check_visible",
            "ranking_leakage_check_visible",
            "scoring_leakage_check_visible",
            "selection_leakage_check_visible",
            "approval_leakage_check_visible",
            "authorization_leakage_check_visible",
            "mutation_leakage_check_visible",
            "production_consumption_leakage_check_visible",
            "planner_integration_leakage_check_visible",
            "fallback_leakage_check_visible",
            "diagnostic_suppression_check_visible",
            "evidence_continuity_check_visible",
            "provenance_continuity_check_visible",
            "lineage_continuity_check_visible",
            "replay_continuity_check_visible",
            "rollback_continuity_check_visible",
            "prohibited_state_check_visible",
            "integrity_boundary_check_visible",
        )
    )
    return {
        **visibility,
        "capability_enabled_count": capability_enabled_count,
        "valid": (
            report.descriptive_only
            and report.integrity_enforcement_performed
            and report.replay_safe
            and report.rollback_safe
            and report.provenance_safe
            and report.lineage_safe
            and visibility["visibility_is_descriptive_only"]
            and visibility["hidden_finding_count"] == 0
            and required_visibility
            and capability_enabled_count == 0
        ),
    }
