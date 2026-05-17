"""Fail-visible v4.0 closeout and v4.1 readiness visibility helpers."""

from __future__ import annotations

from .v4_closeout_models import (
    CLOSEOUT_FINDING_BUNDLE_GOVERNANCE,
    CLOSEOUT_FINDING_CONTINUITY,
    CLOSEOUT_FINDING_DIAGNOSTICS,
    CLOSEOUT_FINDING_DRIFT,
    CLOSEOUT_FINDING_HASHING,
    CLOSEOUT_FINDING_INTEGRITY,
    CLOSEOUT_FINDING_LIFECYCLE,
    CLOSEOUT_FINDING_LINEAGE,
    CLOSEOUT_FINDING_NON_AUTHORIZATION,
    CLOSEOUT_FINDING_NON_EXECUTION,
    CLOSEOUT_FINDING_NON_REMEDIATION,
    CLOSEOUT_FINDING_ORCHESTRATION_DISABLED,
    CLOSEOUT_FINDING_PLANNER_DISABLED,
    CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION,
    CLOSEOUT_FINDING_PRODUCTION_DISABLED,
    CLOSEOUT_FINDING_PROHIBITED_VISIBILITY,
    CLOSEOUT_FINDING_PROVENANCE,
    CLOSEOUT_FINDING_RECOVERY,
    CLOSEOUT_FINDING_REPLAY,
    CLOSEOUT_FINDING_ROLLBACK,
    CLOSEOUT_FINDING_SERIALIZATION,
    CLOSEOUT_FINDING_UNKNOWN_VISIBILITY,
    CLOSEOUT_FINDING_V41_READINESS,
    CLOSEOUT_FINDING_VALIDATION,
    CLOSEOUT_FINDING_VISIBILITY,
    CLOSEOUT_FINDING_WARNING_VISIBILITY,
    CLOSEOUT_SEVERITY_BLOCKING,
    CLOSEOUT_SEVERITY_CRITICAL,
    CLOSEOUT_SEVERITY_PROHIBITED,
    CLOSEOUT_SEVERITY_UNKNOWN,
    CLOSEOUT_SEVERITY_WARNING,
    V4_CLOSEOUT_FINDING_TYPES,
    V4_CLOSEOUT_SEVERITIES,
    V4CloseoutFinding,
    V4CloseoutReport,
)


def count_v4_closeout_finding_types(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> dict[str, int]:
    counts = {finding_type: 0 for finding_type in V4_CLOSEOUT_FINDING_TYPES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.finding_type in counts:
            counts[finding.finding_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_v4_closeout_severities(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> dict[str, int]:
    counts = {severity: 0 for severity in V4_CLOSEOUT_SEVERITIES}
    counts["invalid"] = 0
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def warning_v4_closeout_count(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == CLOSEOUT_SEVERITY_WARNING)


def blocked_v4_closeout_count(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == CLOSEOUT_SEVERITY_BLOCKING)


def prohibited_v4_closeout_count(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == CLOSEOUT_SEVERITY_PROHIBITED)


def unknown_v4_closeout_count(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == CLOSEOUT_SEVERITY_UNKNOWN)


def critical_v4_closeout_count(findings: tuple[V4CloseoutFinding, ...] | list[V4CloseoutFinding]) -> int:
    return sum(1 for finding in findings if finding.severity == CLOSEOUT_SEVERITY_CRITICAL)


def build_v4_closeout_visibility(report: V4CloseoutReport) -> dict[str, object]:
    findings = report.findings
    finding_type_counts = count_v4_closeout_finding_types(findings)
    return {
        "finding_type_counts": finding_type_counts,
        "severity_counts": count_v4_closeout_severities(findings),
        "warning_count": report.warning_count,
        "blocked_count": report.blocked_count,
        "prohibited_count": report.prohibited_count,
        "unknown_count": report.unknown_count,
        "critical_count": report.critical_count,
        "lifecycle_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_LIFECYCLE] > 0,
        "drift_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_DRIFT] > 0,
        "governance_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_BUNDLE_GOVERNANCE] > 0,
        "validation_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_VALIDATION] > 0,
        "production_consumption_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION] > 0,
        "recovery_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_RECOVERY] > 0,
        "diagnostics_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_DIAGNOSTICS] > 0,
        "integrity_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_INTEGRITY] > 0,
        "continuity_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_CONTINUITY] > 0,
        "provenance_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_PROVENANCE] > 0,
        "lineage_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_LINEAGE] > 0,
        "replay_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_REPLAY] > 0,
        "rollback_closeout_visible": finding_type_counts[CLOSEOUT_FINDING_ROLLBACK] > 0,
        "serialization_visible": finding_type_counts[CLOSEOUT_FINDING_SERIALIZATION] > 0,
        "hashing_visible": finding_type_counts[CLOSEOUT_FINDING_HASHING] > 0,
        "visibility_visible": finding_type_counts[CLOSEOUT_FINDING_VISIBILITY] > 0,
        "non_execution_visible": finding_type_counts[CLOSEOUT_FINDING_NON_EXECUTION] > 0,
        "non_remediation_visible": finding_type_counts[CLOSEOUT_FINDING_NON_REMEDIATION] > 0,
        "non_authorization_visible": finding_type_counts[CLOSEOUT_FINDING_NON_AUTHORIZATION] > 0,
        "production_disabled_visible": finding_type_counts[CLOSEOUT_FINDING_PRODUCTION_DISABLED] > 0,
        "orchestration_disabled_visible": finding_type_counts[CLOSEOUT_FINDING_ORCHESTRATION_DISABLED] > 0,
        "planner_disabled_visible": finding_type_counts[CLOSEOUT_FINDING_PLANNER_DISABLED] > 0,
        "v4_1_readiness_visible": finding_type_counts[CLOSEOUT_FINDING_V41_READINESS] > 0,
        "prohibited_state_visible": finding_type_counts[CLOSEOUT_FINDING_PROHIBITED_VISIBILITY] > 0,
        "unknown_state_visible": finding_type_counts[CLOSEOUT_FINDING_UNKNOWN_VISIBILITY] > 0,
        "warning_visible": finding_type_counts[CLOSEOUT_FINDING_WARNING_VISIBILITY] > 0,
        "visibility_is_descriptive_only": all(finding.descriptive_only for finding in findings),
        "hidden_finding_count": sum(1 for finding in findings if finding.hidden),
    }


def validate_v4_closeout_visibility(report: V4CloseoutReport) -> dict[str, object]:
    visibility = build_v4_closeout_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            report.approval_enabled,
            report.authorization_enabled,
            report.remediation_enabled,
            report.repair_enabled,
            report.execution_enabled,
            report.execution_authorized,
            report.remediation_authorized,
            report.production_consumption_enabled,
            report.orchestration_enabled,
            report.planner_integration_enabled,
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
            "lifecycle_closeout_visible",
            "drift_closeout_visible",
            "governance_closeout_visible",
            "validation_closeout_visible",
            "production_consumption_closeout_visible",
            "recovery_closeout_visible",
            "diagnostics_closeout_visible",
            "integrity_closeout_visible",
            "continuity_closeout_visible",
            "provenance_closeout_visible",
            "lineage_closeout_visible",
            "replay_closeout_visible",
            "rollback_closeout_visible",
            "serialization_visible",
            "hashing_visible",
            "visibility_visible",
            "non_execution_visible",
            "non_remediation_visible",
            "non_authorization_visible",
            "production_disabled_visible",
            "orchestration_disabled_visible",
            "planner_disabled_visible",
            "v4_1_readiness_visible",
            "prohibited_state_visible",
            "unknown_state_visible",
            "warning_visible",
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
            and report.continuity_preserved
            and visibility["visibility_is_descriptive_only"]
            and visibility["hidden_finding_count"] == 0
            and required_visibility
            and capability_enabled_count == 0
        ),
    }
