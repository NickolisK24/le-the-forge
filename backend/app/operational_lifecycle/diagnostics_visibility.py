"""Fail-visible operational diagnostics visibility helpers."""

from __future__ import annotations

from .diagnostics_models import (
    DIAGNOSTIC_CATEGORY_BLOCKED,
    DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE,
    DIAGNOSTIC_CATEGORY_CRITICAL,
    DIAGNOSTIC_CATEGORY_DRIFT,
    DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY,
    DIAGNOSTIC_CATEGORY_LIFECYCLE,
    DIAGNOSTIC_CATEGORY_LINEAGE,
    DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION,
    DIAGNOSTIC_CATEGORY_PROHIBITED,
    DIAGNOSTIC_CATEGORY_PROVENANCE,
    DIAGNOSTIC_CATEGORY_RECOVERY,
    DIAGNOSTIC_CATEGORY_REPLAY,
    DIAGNOSTIC_CATEGORY_ROLLBACK,
    DIAGNOSTIC_CATEGORY_UNKNOWN,
    DIAGNOSTIC_CATEGORY_UNSUPPORTED,
    DIAGNOSTIC_CATEGORY_VALIDATION,
    DIAGNOSTIC_CATEGORY_WARNING,
    DIAGNOSTIC_SEVERITY_BLOCKING,
    DIAGNOSTIC_SEVERITY_CRITICAL,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
    DIAGNOSTIC_SEVERITY_UNKNOWN,
    DIAGNOSTIC_SEVERITY_WARNING,
    OPERATIONAL_DIAGNOSTIC_CATEGORIES,
    OPERATIONAL_DIAGNOSTIC_SEVERITIES,
    OPERATIONAL_DIAGNOSTIC_TYPES,
    OperationalDiagnosticEntry,
    OperationalDiagnosticsReport,
)


def count_diagnostic_categories(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> dict[str, int]:
    counts = {category: 0 for category in OPERATIONAL_DIAGNOSTIC_CATEGORIES}
    counts["invalid"] = 0
    for entry in entries:
        if entry.category in counts:
            counts[entry.category] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_diagnostic_types(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> dict[str, int]:
    counts = {diagnostic_type: 0 for diagnostic_type in OPERATIONAL_DIAGNOSTIC_TYPES}
    counts["invalid"] = 0
    for entry in entries:
        if entry.diagnostic_type in counts:
            counts[entry.diagnostic_type] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_diagnostic_severities(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> dict[str, int]:
    counts = {severity: 0 for severity in OPERATIONAL_DIAGNOSTIC_SEVERITIES}
    counts["invalid"] = 0
    for entry in entries:
        if entry.severity in counts:
            counts[entry.severity] += 1
        else:
            counts["invalid"] += 1
    return counts


def unsupported_diagnostic_count(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> int:
    return sum(1 for entry in entries if entry.category == DIAGNOSTIC_CATEGORY_UNSUPPORTED)


def prohibited_diagnostic_count(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> int:
    return sum(
        1
        for entry in entries
        if entry.category == DIAGNOSTIC_CATEGORY_PROHIBITED or entry.severity == DIAGNOSTIC_SEVERITY_PROHIBITED
    )


def blocked_diagnostic_count(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> int:
    return sum(
        1
        for entry in entries
        if entry.category == DIAGNOSTIC_CATEGORY_BLOCKED or entry.severity == DIAGNOSTIC_SEVERITY_BLOCKING
    )


def unknown_diagnostic_count(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> int:
    return sum(
        1
        for entry in entries
        if entry.category == DIAGNOSTIC_CATEGORY_UNKNOWN or entry.severity == DIAGNOSTIC_SEVERITY_UNKNOWN
    )


def warning_diagnostic_count(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> int:
    return sum(1 for entry in entries if entry.severity == DIAGNOSTIC_SEVERITY_WARNING)


def critical_diagnostic_count(
    entries: tuple[OperationalDiagnosticEntry, ...] | list[OperationalDiagnosticEntry],
) -> int:
    return sum(
        1
        for entry in entries
        if entry.category == DIAGNOSTIC_CATEGORY_CRITICAL or entry.severity == DIAGNOSTIC_SEVERITY_CRITICAL
    )


def build_operational_diagnostics_visibility(report: OperationalDiagnosticsReport) -> dict[str, object]:
    entries = report.entries
    category_counts = count_diagnostic_categories(entries)
    type_counts = count_diagnostic_types(entries)
    return {
        "category_counts": category_counts,
        "diagnostic_type_counts": type_counts,
        "severity_counts": count_diagnostic_severities(entries),
        "unsupported_count": report.unsupported_count,
        "prohibited_count": report.prohibited_count,
        "blocked_count": report.blocked_count,
        "unknown_count": report.unknown_count,
        "warning_count": report.warning_count,
        "critical_count": report.critical_count,
        "lifecycle_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_LIFECYCLE] > 0,
        "drift_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_DRIFT] > 0,
        "bundle_governance_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE] > 0,
        "validation_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_VALIDATION] > 0,
        "production_consumption_diagnostic_visible": (
            category_counts[DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION] > 0
        ),
        "recovery_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_RECOVERY] > 0,
        "provenance_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_PROVENANCE] > 0,
        "lineage_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_LINEAGE] > 0,
        "replay_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_REPLAY] > 0,
        "rollback_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_ROLLBACK] > 0,
        "unsupported_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_UNSUPPORTED] > 0,
        "prohibited_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_PROHIBITED] > 0,
        "blocked_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_BLOCKED] > 0,
        "unknown_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_UNKNOWN] > 0,
        "warning_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_WARNING] > 0,
        "critical_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_CRITICAL] > 0,
        "execution_boundary_diagnostic_visible": category_counts[DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY] > 0,
        "visibility_is_descriptive_only": all(entry.descriptive_only for entry in entries),
        "hidden_entry_count": sum(1 for entry in entries if entry.hidden),
        "recommendations_present": report.recommendations_present
        or any(entry.recommendations_present or entry.recommendation_enabled for entry in entries),
        "ranking_enabled": report.ranking_enabled or any(entry.ranking_enabled for entry in entries),
        "scoring_enabled": report.scoring_enabled or any(entry.scoring_enabled for entry in entries),
        "selection_enabled": report.selection_enabled or any(entry.selection_enabled for entry in entries),
        "optimization_enabled": report.optimization_enabled or any(entry.optimization_enabled for entry in entries),
        "approval_enabled": report.approval_enabled or any(entry.approval_enabled for entry in entries),
        "authorization_enabled": report.authorization_enabled or any(entry.authorization_enabled for entry in entries),
        "remediation_enabled": report.remediation_enabled or any(entry.remediation_enabled for entry in entries),
        "execution_authorized": report.execution_authorized or any(entry.execution_authorized for entry in entries),
        "execution_enabled": report.execution_enabled or any(entry.execution_enabled for entry in entries),
        "orchestration_execution_enabled": report.orchestration_execution_enabled
        or any(entry.orchestration_execution_enabled for entry in entries),
        "runtime_mutation_enabled": report.runtime_mutation_enabled
        or any(entry.runtime_mutation_enabled for entry in entries),
    }


def validate_operational_diagnostics_visibility(report: OperationalDiagnosticsReport) -> dict[str, object]:
    visibility = build_operational_diagnostics_visibility(report)
    capability_enabled_count = sum(
        1
        for enabled in (
            visibility["recommendations_present"],
            visibility["ranking_enabled"],
            visibility["scoring_enabled"],
            visibility["selection_enabled"],
            visibility["optimization_enabled"],
            visibility["approval_enabled"],
            visibility["authorization_enabled"],
            visibility["remediation_enabled"],
            visibility["execution_authorized"],
            visibility["execution_enabled"],
            visibility["orchestration_execution_enabled"],
            visibility["runtime_mutation_enabled"],
        )
        if enabled
    )
    required_visibility = all(
        visibility[key]
        for key in (
            "lifecycle_diagnostic_visible",
            "drift_diagnostic_visible",
            "bundle_governance_diagnostic_visible",
            "validation_diagnostic_visible",
            "production_consumption_diagnostic_visible",
            "recovery_diagnostic_visible",
            "provenance_diagnostic_visible",
            "lineage_diagnostic_visible",
            "replay_diagnostic_visible",
            "rollback_diagnostic_visible",
            "unsupported_diagnostic_visible",
            "prohibited_diagnostic_visible",
            "blocked_diagnostic_visible",
            "unknown_diagnostic_visible",
            "warning_diagnostic_visible",
            "critical_diagnostic_visible",
            "execution_boundary_diagnostic_visible",
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
            and visibility["visibility_is_descriptive_only"]
            and required_visibility
            and visibility["hidden_entry_count"] == 0
            and capability_enabled_count == 0
        ),
    }
