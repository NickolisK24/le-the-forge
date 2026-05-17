"""Fail-visible lifecycle drift visibility helpers."""

from __future__ import annotations

from .lifecycle_drift_models import (
    DRIFT_SEVERITY_BLOCKING,
    DRIFT_SEVERITY_PROHIBITED,
    DRIFT_SEVERITY_UNKNOWN,
    DRIFT_TYPE_INTEGRITY_WARNING,
    DRIFT_TYPE_LINEAGE,
    DRIFT_TYPE_PROVENANCE,
    DRIFT_TYPE_REPLAY_CONTINUITY,
    DRIFT_TYPE_ROLLBACK_CONTINUITY,
    LIFECYCLE_DRIFT_SEVERITIES,
    LIFECYCLE_DRIFT_TYPES,
    LifecycleDriftFinding,
    LifecycleDriftReport,
)


def count_drift_types(findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding]) -> dict[str, int]:
    counts = {drift_type: 0 for drift_type in LIFECYCLE_DRIFT_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.drift_type in counts:
            counts[finding.drift_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_drift_severities(findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding]) -> dict[str, int]:
    counts = {severity: 0 for severity in LIFECYCLE_DRIFT_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def unsupported_drift_count(findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding]) -> int:
    return sum(1 for finding in findings if _finding_contains(finding, "unsupported"))


def prohibited_drift_count(findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding]) -> int:
    return sum(
        1
        for finding in findings
        if finding.severity == DRIFT_SEVERITY_PROHIBITED or _finding_contains(finding, "prohibited")
    )


def unknown_drift_count(findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding]) -> int:
    return sum(
        1 for finding in findings if finding.severity == DRIFT_SEVERITY_UNKNOWN or _finding_contains(finding, "unknown")
    )


def blocking_drift_count(findings: tuple[LifecycleDriftFinding, ...] | list[LifecycleDriftFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == DRIFT_SEVERITY_BLOCKING)


def build_lifecycle_drift_visibility(report: LifecycleDriftReport) -> dict[str, object]:
    findings = report.findings
    return {
        "drift_type_counts": count_drift_types(findings),
        "severity_counts": count_drift_severities(findings),
        "unsupported_drift_count": report.unsupported_drift_count,
        "prohibited_drift_count": report.prohibited_drift_count,
        "unknown_drift_count": report.unknown_drift_count,
        "blocking_drift_count": report.blocking_drift_count,
        "integrity_warning_drift_count": count_drift_types(findings)[DRIFT_TYPE_INTEGRITY_WARNING],
        "replay_continuity_drift_count": count_drift_types(findings)[DRIFT_TYPE_REPLAY_CONTINUITY],
        "rollback_continuity_drift_count": count_drift_types(findings)[DRIFT_TYPE_ROLLBACK_CONTINUITY],
        "provenance_continuity_drift_count": count_drift_types(findings)[DRIFT_TYPE_PROVENANCE],
        "lineage_continuity_drift_count": count_drift_types(findings)[DRIFT_TYPE_LINEAGE],
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "remediation_enabled": any(finding.remediation_enabled for finding in findings),
        "correction_enabled": any(finding.correction_enabled for finding in findings),
        "authorization_enabled": any(finding.authorization_enabled for finding in findings),
        "execution_enabled": any(finding.execution_enabled for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
    }


def validate_lifecycle_drift_visibility(report: LifecycleDriftReport) -> dict[str, object]:
    visibility = build_lifecycle_drift_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.remediation_enabled,
            report.correction_enabled,
            report.authorization_enabled,
            report.approval_enabled,
            report.execution_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.orchestration_execution_enabled,
            report.runtime_mutation_enabled,
            report.callable_operational_workflow_enabled,
            visibility["remediation_enabled"],
            visibility["correction_enabled"],
            visibility["authorization_enabled"],
            visibility["execution_enabled"],
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
            and visibility["visibility_is_descriptive_only"]
            and visibility["hidden_finding_count"] == 0
            and capability_enabled_count == 0
        ),
    }


def _finding_contains(finding: LifecycleDriftFinding, token: str) -> bool:
    needle = token.lower()
    haystack = "|".join(
        (
            str(finding.drift_type),
            str(finding.severity),
            str(finding.before_value),
            str(finding.after_value),
            finding.explanation,
            finding.deterministic_key,
        )
    ).lower()
    return needle in haystack
