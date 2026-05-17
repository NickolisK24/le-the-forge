"""Fail-visible rollback and recovery certification visibility helpers."""

from __future__ import annotations

from .recovery_certification_models import (
    RECOVERY_CERTIFICATION_FINDING_TYPES,
    RECOVERY_CERTIFICATION_SEVERITIES,
    RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
    RECOVERY_CERTIFICATION_SEVERITY_CRITICAL,
    RECOVERY_CERTIFICATION_SEVERITY_INFO,
    RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED,
    RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN,
    RECOVERY_CERTIFICATION_SEVERITY_WARNING,
    RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS,
    RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED,
    RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED,
    RecoveryCertificationFinding,
    RecoveryCertificationReport,
)


def count_recovery_finding_types(
    findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding],
) -> dict[str, int]:
    counts = {finding_type: 0 for finding_type in RECOVERY_CERTIFICATION_FINDING_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.finding_type in counts:
            counts[finding.finding_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_recovery_severities(
    findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding],
) -> dict[str, int]:
    counts = {severity: 0 for severity in RECOVERY_CERTIFICATION_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def certifiable_recovery_count(
    findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity in (RECOVERY_CERTIFICATION_SEVERITY_INFO, RECOVERY_CERTIFICATION_SEVERITY_WARNING)
    )


def blocked_recovery_count(findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING)


def unsupported_recovery_count(
    findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding],
) -> int:
    return sum(1 for finding in findings if _finding_contains(finding, "unsupported"))


def prohibited_recovery_count(
    findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED or _finding_contains(finding, "prohibited")
    )


def unknown_recovery_count(findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding]) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN or _finding_contains(finding, "unknown")
    )


def warning_recovery_count(findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING)


def critical_recovery_count(findings: tuple[RecoveryCertificationFinding, ...] | list[RecoveryCertificationFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == RECOVERY_CERTIFICATION_SEVERITY_CRITICAL)


def build_recovery_certification_visibility(report: RecoveryCertificationReport) -> dict[str, object]:
    findings = report.findings
    finding_type_counts = count_recovery_finding_types(findings)
    return {
        "finding_type_counts": finding_type_counts,
        "severity_counts": count_recovery_severities(findings),
        "certifiable_finding_count": report.certifiable_finding_count,
        "blocked_count": report.blocked_count,
        "unsupported_count": report.unsupported_count,
        "prohibited_count": report.prohibited_count,
        "unknown_count": report.unknown_count,
        "warning_count": report.warning_count,
        "critical_count": report.critical_count,
        "recovery_certification_readiness_visible": (
            finding_type_counts[RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS] > 0
        ),
        "rollback_execution_prohibition_visible": (
            finding_type_counts[RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED] > 0
        ),
        "recovery_execution_prohibition_visible": (
            finding_type_counts[RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED] > 0
        ),
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "approval_enabled": any(finding.approval_enabled for finding in findings),
        "authorization_enabled": any(finding.authorization_enabled for finding in findings),
        "remediation_enabled": any(finding.remediation_enabled for finding in findings),
        "recovery_execution_authorized": any(finding.recovery_execution_authorized for finding in findings),
        "rollback_execution_authorized": any(finding.rollback_execution_authorized for finding in findings),
        "recovery_execution_enabled": any(finding.recovery_execution_enabled for finding in findings),
        "rollback_execution_enabled": any(finding.rollback_execution_enabled for finding in findings),
        "execution_enabled": any(finding.execution_enabled for finding in findings),
        "orchestration_execution_enabled": any(finding.orchestration_execution_enabled for finding in findings),
        "runtime_mutation_enabled": any(finding.runtime_mutation_enabled for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
    }


def validate_recovery_certification_visibility(report: RecoveryCertificationReport) -> dict[str, object]:
    visibility = build_recovery_certification_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.approval_enabled,
            report.authorization_enabled,
            report.remediation_enabled,
            report.recovery_execution_authorized,
            report.rollback_execution_authorized,
            report.recovery_execution_enabled,
            report.rollback_execution_enabled,
            report.execution_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.orchestration_execution_enabled,
            report.runtime_mutation_enabled,
            report.production_consumption_authorized,
            visibility["approval_enabled"],
            visibility["authorization_enabled"],
            visibility["remediation_enabled"],
            visibility["recovery_execution_authorized"],
            visibility["rollback_execution_authorized"],
            visibility["recovery_execution_enabled"],
            visibility["rollback_execution_enabled"],
            visibility["execution_enabled"],
            visibility["orchestration_execution_enabled"],
            visibility["runtime_mutation_enabled"],
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
            and not report.recovery_execution_authorized
            and not report.rollback_execution_authorized
            and visibility["visibility_is_descriptive_only"]
            and visibility["recovery_certification_readiness_visible"]
            and visibility["rollback_execution_prohibition_visible"]
            and visibility["recovery_execution_prohibition_visible"]
            and visibility["hidden_finding_count"] == 0
            and capability_enabled_count == 0
        ),
    }


def _finding_contains(finding: RecoveryCertificationFinding, token: str) -> bool:
    needle = token.lower()
    haystack = "|".join(
        (
            str(finding.finding_type),
            str(finding.severity),
            finding.lifecycle_reference,
            finding.drift_reference,
            finding.governance_reference,
            finding.validation_reference,
            finding.production_consumption_reference,
            finding.provenance_reference,
            finding.lineage_reference,
            finding.replay_reference,
            finding.rollback_reference,
            finding.recovery_reference,
            finding.explanation,
            finding.deterministic_key,
        )
    ).lower()
    return needle in haystack
