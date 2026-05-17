"""Fail-visible trusted bundle governance visibility helpers."""

from __future__ import annotations

from .bundle_governance_models import (
    GOVERNANCE_SEVERITY_BLOCKING,
    GOVERNANCE_SEVERITY_PROHIBITED,
    GOVERNANCE_SEVERITY_UNKNOWN,
    GOVERNANCE_SEVERITY_WARNING,
    TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES,
    TRUSTED_BUNDLE_GOVERNANCE_SEVERITIES,
    TrustedBundleGovernanceFinding,
    TrustedBundleGovernanceReport,
)


def count_governance_finding_types(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> dict[str, int]:
    counts = {finding_type: 0 for finding_type in TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.finding_type in counts:
            counts[finding.finding_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_governance_severities(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> dict[str, int]:
    counts = {severity: 0 for severity in TRUSTED_BUNDLE_GOVERNANCE_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def unsupported_governance_count(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> int:
    return sum(1 for finding in findings if _finding_contains(finding, "unsupported"))


def prohibited_governance_count(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == GOVERNANCE_SEVERITY_PROHIBITED or _finding_contains(finding, "prohibited")
    )


def blocked_governance_count(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == GOVERNANCE_SEVERITY_BLOCKING or _finding_contains(finding, "blocked")
    )


def unknown_governance_count(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == GOVERNANCE_SEVERITY_UNKNOWN or _finding_contains(finding, "unknown")
    )


def warning_governance_count(
    findings: tuple[TrustedBundleGovernanceFinding, ...] | list[TrustedBundleGovernanceFinding],
) -> int:
    return sum(1 for finding in findings if finding.severity == GOVERNANCE_SEVERITY_WARNING)


def build_trusted_bundle_governance_visibility(report: TrustedBundleGovernanceReport) -> dict[str, object]:
    findings = report.findings
    finding_type_counts = count_governance_finding_types(findings)
    return {
        "finding_type_counts": finding_type_counts,
        "severity_counts": count_governance_severities(findings),
        "unsupported_count": report.unsupported_count,
        "prohibited_count": report.prohibited_count,
        "blocked_count": report.blocked_count,
        "unknown_count": report.unknown_count,
        "warning_count": report.warning_count,
        "blocked_domain_count": len(report.blocked_domains),
        "production_consumption_authorized": report.production_consumption_authorized,
        "production_consumption_prohibition_visible": finding_type_counts["production_consumption_prohibited"] > 0,
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "approval_enabled": any(finding.approval_enabled for finding in findings),
        "authorization_enabled": any(finding.authorization_enabled for finding in findings),
        "remediation_enabled": any(finding.remediation_enabled for finding in findings),
        "execution_enabled": any(finding.execution_enabled for finding in findings),
        "production_consumption_enabled": any(finding.production_consumption_enabled for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
    }


def validate_trusted_bundle_governance_visibility(report: TrustedBundleGovernanceReport) -> dict[str, object]:
    visibility = build_trusted_bundle_governance_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.approval_enabled,
            report.authorization_enabled,
            report.remediation_enabled,
            report.execution_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.orchestration_execution_enabled,
            report.runtime_mutation_enabled,
            report.production_bundle_consumption_enabled,
            visibility["approval_enabled"],
            visibility["authorization_enabled"],
            visibility["remediation_enabled"],
            visibility["execution_enabled"],
            visibility["production_consumption_enabled"],
            visibility["production_consumption_authorized"],
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
            and not report.production_consumption_authorized
            and visibility["visibility_is_descriptive_only"]
            and visibility["production_consumption_prohibition_visible"]
            and visibility["hidden_finding_count"] == 0
            and capability_enabled_count == 0
        ),
    }


def _finding_contains(finding: TrustedBundleGovernanceFinding, token: str) -> bool:
    needle = token.lower()
    haystack = "|".join(
        (
            str(finding.finding_type),
            str(finding.severity),
            finding.bundle_reference,
            finding.lifecycle_reference,
            finding.drift_reference,
            finding.provenance_reference,
            finding.lineage_reference,
            finding.explanation,
            finding.deterministic_key,
        )
    ).lower()
    return needle in haystack
