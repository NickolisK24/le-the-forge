"""Fail-visible operational validation automation visibility helpers."""

from __future__ import annotations

from .validation_automation_models import (
    OPERATIONAL_VALIDATION_FINDING_TYPES,
    OPERATIONAL_VALIDATION_SEVERITIES,
    OPERATIONAL_VALIDATION_SEVERITY_BLOCKING,
    OPERATIONAL_VALIDATION_SEVERITY_CRITICAL,
    OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED,
    OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN,
    OPERATIONAL_VALIDATION_SEVERITY_WARNING,
    VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS,
    VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED,
    VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY,
    OperationalValidationFinding,
    OperationalValidationReport,
)


def count_validation_finding_types(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> dict[str, int]:
    counts = {finding_type: 0 for finding_type in OPERATIONAL_VALIDATION_FINDING_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.finding_type in counts:
            counts[finding.finding_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_validation_severities(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> dict[str, int]:
    counts = {severity: 0 for severity in OPERATIONAL_VALIDATION_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def unsupported_validation_count(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> int:
    return sum(1 for finding in findings if _finding_contains(finding, "unsupported"))


def prohibited_validation_count(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED or _finding_contains(finding, "prohibited")
    )


def blocked_validation_count(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == OPERATIONAL_VALIDATION_SEVERITY_BLOCKING or _finding_contains(finding, "blocked")
    )


def unknown_validation_count(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN or _finding_contains(finding, "unknown")
    )


def warning_validation_count(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == OPERATIONAL_VALIDATION_SEVERITY_WARNING)


def critical_validation_count(
    findings: tuple[OperationalValidationFinding, ...] | list[OperationalValidationFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == OPERATIONAL_VALIDATION_SEVERITY_CRITICAL or _finding_contains(finding, "critical")
    )


def build_operational_validation_visibility(report: OperationalValidationReport) -> dict[str, object]:
    findings = report.findings
    finding_type_counts = count_validation_finding_types(findings)
    return {
        "finding_type_counts": finding_type_counts,
        "severity_counts": count_validation_severities(findings),
        "unsupported_count": report.unsupported_count,
        "prohibited_count": report.prohibited_count,
        "blocked_count": report.blocked_count,
        "unknown_count": report.unknown_count,
        "warning_count": report.warning_count,
        "critical_count": report.critical_count,
        "lifecycle_validation_visible": finding_type_counts[VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY] > 0,
        "drift_validation_visible": finding_type_counts[VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY] > 0,
        "governance_validation_visible": finding_type_counts[VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY] > 0,
        "provenance_validation_visible": finding_type_counts[VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY] > 0,
        "lineage_validation_visible": finding_type_counts[VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY] > 0,
        "replay_validation_visible": finding_type_counts[VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY] > 0,
        "rollback_validation_visible": finding_type_counts[VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY] > 0,
        "operational_execution_prohibition_visible": (
            finding_type_counts[VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED] > 0
        ),
        "operational_certification_readiness_visible": (
            finding_type_counts[VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS] > 0
        ),
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "authorization_enabled": any(finding.authorization_enabled for finding in findings),
        "approval_enabled": any(finding.approval_enabled for finding in findings),
        "deployment_enabled": any(finding.deployment_enabled for finding in findings),
        "remediation_enabled": any(finding.remediation_enabled for finding in findings),
        "execution_enabled": any(finding.execution_enabled for finding in findings),
        "orchestration_execution_enabled": any(finding.orchestration_execution_enabled for finding in findings),
        "runtime_mutation_enabled": any(finding.runtime_mutation_enabled for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
        "operational_execution_authorized": report.operational_execution_authorized,
    }


def validate_operational_validation_visibility(report: OperationalValidationReport) -> dict[str, object]:
    visibility = build_operational_validation_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.approval_enabled,
            report.authorization_enabled,
            report.deployment_enabled,
            report.remediation_enabled,
            report.execution_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.orchestration_execution_enabled,
            report.runtime_mutation_enabled,
            report.production_consumption_authorized,
            report.operational_execution_authorized,
            visibility["approval_enabled"],
            visibility["authorization_enabled"],
            visibility["deployment_enabled"],
            visibility["remediation_enabled"],
            visibility["execution_enabled"],
            visibility["orchestration_execution_enabled"],
            visibility["runtime_mutation_enabled"],
            visibility["operational_execution_authorized"],
        )
        if enabled
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
            and not report.operational_execution_authorized
            and not report.production_consumption_authorized
            and visibility["visibility_is_descriptive_only"]
            and visibility["operational_execution_prohibition_visible"]
            and visibility["operational_certification_readiness_visible"]
            and visibility["hidden_finding_count"] == 0
            and capability_enabled_count == 0
        ),
    }


def _finding_contains(finding: OperationalValidationFinding, token: str) -> bool:
    needle = token.lower()
    haystack = "|".join(
        (
            str(finding.finding_type),
            str(finding.severity),
            finding.lifecycle_reference,
            finding.drift_reference,
            finding.governance_reference,
            finding.provenance_reference,
            finding.lineage_reference,
            finding.replay_reference,
            finding.rollback_reference,
            finding.explanation,
            finding.deterministic_key,
        )
    ).lower()
    return needle in haystack
