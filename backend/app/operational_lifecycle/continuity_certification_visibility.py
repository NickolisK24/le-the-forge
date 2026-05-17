"""Fail-visible operational continuity certification visibility helpers."""

from __future__ import annotations

from .continuity_certification_models import (
    CONTINUITY_FINDING_BUNDLE_GOVERNANCE,
    CONTINUITY_FINDING_DIAGNOSTICS,
    CONTINUITY_FINDING_DRIFT,
    CONTINUITY_FINDING_HASHING,
    CONTINUITY_FINDING_INTEGRITY,
    CONTINUITY_FINDING_LIFECYCLE,
    CONTINUITY_FINDING_LINEAGE,
    CONTINUITY_FINDING_NON_AUTHORIZATION,
    CONTINUITY_FINDING_NON_EXECUTION,
    CONTINUITY_FINDING_NON_REMEDIATION,
    CONTINUITY_FINDING_OPERATIONAL_VALIDATION,
    CONTINUITY_FINDING_PRODUCTION_CONSUMPTION,
    CONTINUITY_FINDING_PRODUCTION_DISABLED,
    CONTINUITY_FINDING_PROHIBITED_STATE,
    CONTINUITY_FINDING_PROVENANCE,
    CONTINUITY_FINDING_RECOVERY,
    CONTINUITY_FINDING_REPLAY,
    CONTINUITY_FINDING_ROLLBACK,
    CONTINUITY_FINDING_SERIALIZATION,
    CONTINUITY_FINDING_UNKNOWN_STATE,
    CONTINUITY_FINDING_VISIBILITY,
    CONTINUITY_SEVERITY_BLOCKING,
    CONTINUITY_SEVERITY_CRITICAL,
    CONTINUITY_SEVERITY_INFO,
    CONTINUITY_SEVERITY_PROHIBITED,
    CONTINUITY_SEVERITY_UNKNOWN,
    CONTINUITY_SEVERITY_WARNING,
    OPERATIONAL_CONTINUITY_FINDING_TYPES,
    OPERATIONAL_CONTINUITY_SEVERITIES,
    OperationalContinuityCertificationReport,
    OperationalContinuityFinding,
)


def count_continuity_finding_types(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> dict[str, int]:
    counts = {finding_type: 0 for finding_type in OPERATIONAL_CONTINUITY_FINDING_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.finding_type in counts:
            counts[finding.finding_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_continuity_severities(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> dict[str, int]:
    counts = {severity: 0 for severity in OPERATIONAL_CONTINUITY_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def certified_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_INFO)


def warning_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_WARNING)


def broken_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_CRITICAL)


def blocked_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_BLOCKING)


def prohibited_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_PROHIBITED)


def unknown_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_UNKNOWN)


def critical_continuity_count(
    findings: tuple[OperationalContinuityFinding, ...] | list[OperationalContinuityFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == CONTINUITY_SEVERITY_CRITICAL)


def build_operational_continuity_visibility(report: OperationalContinuityCertificationReport) -> dict[str, object]:
    findings = report.findings
    finding_type_counts = count_continuity_finding_types(findings)
    return {
        "finding_type_counts": finding_type_counts,
        "severity_counts": count_continuity_severities(findings),
        "certified_count": report.certified_count,
        "warning_count": report.warning_count,
        "broken_count": report.broken_count,
        "blocked_count": report.blocked_count,
        "prohibited_count": report.prohibited_count,
        "unknown_count": report.unknown_count,
        "critical_count": report.critical_count,
        "lifecycle_continuity_visible": finding_type_counts[CONTINUITY_FINDING_LIFECYCLE] > 0,
        "drift_continuity_visible": finding_type_counts[CONTINUITY_FINDING_DRIFT] > 0,
        "bundle_governance_continuity_visible": finding_type_counts[CONTINUITY_FINDING_BUNDLE_GOVERNANCE] > 0,
        "validation_continuity_visible": finding_type_counts[CONTINUITY_FINDING_OPERATIONAL_VALIDATION] > 0,
        "production_consumption_continuity_visible": (
            finding_type_counts[CONTINUITY_FINDING_PRODUCTION_CONSUMPTION] > 0
        ),
        "recovery_continuity_visible": finding_type_counts[CONTINUITY_FINDING_RECOVERY] > 0,
        "diagnostics_continuity_visible": finding_type_counts[CONTINUITY_FINDING_DIAGNOSTICS] > 0,
        "integrity_continuity_visible": finding_type_counts[CONTINUITY_FINDING_INTEGRITY] > 0,
        "provenance_continuity_visible": finding_type_counts[CONTINUITY_FINDING_PROVENANCE] > 0,
        "lineage_continuity_visible": finding_type_counts[CONTINUITY_FINDING_LINEAGE] > 0,
        "replay_continuity_visible": finding_type_counts[CONTINUITY_FINDING_REPLAY] > 0,
        "rollback_continuity_visible": finding_type_counts[CONTINUITY_FINDING_ROLLBACK] > 0,
        "serialization_continuity_visible": finding_type_counts[CONTINUITY_FINDING_SERIALIZATION] > 0,
        "hashing_continuity_visible": finding_type_counts[CONTINUITY_FINDING_HASHING] > 0,
        "visibility_continuity_visible": finding_type_counts[CONTINUITY_FINDING_VISIBILITY] > 0,
        "non_execution_continuity_visible": finding_type_counts[CONTINUITY_FINDING_NON_EXECUTION] > 0,
        "non_remediation_continuity_visible": finding_type_counts[CONTINUITY_FINDING_NON_REMEDIATION] > 0,
        "non_authorization_continuity_visible": finding_type_counts[CONTINUITY_FINDING_NON_AUTHORIZATION] > 0,
        "production_disabled_continuity_visible": finding_type_counts[CONTINUITY_FINDING_PRODUCTION_DISABLED] > 0,
        "prohibited_state_continuity_visible": finding_type_counts[CONTINUITY_FINDING_PROHIBITED_STATE] > 0,
        "unknown_state_continuity_visible": finding_type_counts[CONTINUITY_FINDING_UNKNOWN_STATE] > 0,
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
    }


def validate_operational_continuity_visibility(report: OperationalContinuityCertificationReport) -> dict[str, object]:
    visibility = build_operational_continuity_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.approval_enabled,
            report.authorization_enabled,
            report.remediation_enabled,
            report.repair_enabled,
            report.execution_enabled,
            report.orchestration_execution_enabled,
            report.recommendation_enabled,
            report.ranking_enabled,
            report.scoring_enabled,
            report.selection_enabled,
            report.optimization_enabled,
            report.runtime_mutation_enabled,
            report.execution_authorized,
            report.remediation_authorized,
            report.production_consumption_enabled,
        )
        if enabled
    )
    required_visibility = all(
        visibility[key]
        for key in (
            "lifecycle_continuity_visible",
            "drift_continuity_visible",
            "bundle_governance_continuity_visible",
            "validation_continuity_visible",
            "production_consumption_continuity_visible",
            "recovery_continuity_visible",
            "diagnostics_continuity_visible",
            "integrity_continuity_visible",
            "provenance_continuity_visible",
            "lineage_continuity_visible",
            "replay_continuity_visible",
            "rollback_continuity_visible",
            "serialization_continuity_visible",
            "hashing_continuity_visible",
            "visibility_continuity_visible",
            "non_execution_continuity_visible",
            "non_remediation_continuity_visible",
            "non_authorization_continuity_visible",
            "production_disabled_continuity_visible",
            "prohibited_state_continuity_visible",
            "unknown_state_continuity_visible",
        )
    )
    return {
        **visibility,
        "capability_enabled_count": capability_enabled_count,
        "valid": (
            report.descriptive_only
            and report.replay_safe
            and report.rollback_safe
            and report.provenance_safe
            and report.lineage_safe
            and report.serialization_stable
            and report.hashing_stable
            and report.visibility_preserved
            and report.integrity_preserved
            and visibility["visibility_is_descriptive_only"]
            and visibility["hidden_finding_count"] == 0
            and required_visibility
            and capability_enabled_count == 0
        ),
    }
