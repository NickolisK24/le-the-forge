"""Deterministic operational explainability and diagnostics models.

Diagnostics are descriptive evidence only. They explain visible lifecycle
evidence without recommendations, ranking, scoring, selection, optimization,
authorization, remediation, execution, orchestration, or runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_OPERATIONAL_DIAGNOSTICS_PHASE_ID = "v4_0_operational_explainability_diagnostics"
V4_0_OPERATIONAL_DIAGNOSTICS_SCHEMA_VERSION = "v4_0.operational_explainability_diagnostics.1"
V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_STABLE = "v4_0_operational_explainability_diagnostics_stable"
V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_BLOCKED = "v4_0_operational_explainability_diagnostics_blocked"
V4_0_OPERATIONAL_DIAGNOSTICS_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_OPERATIONAL_DIAGNOSTICS_SCOPE = "operational_explainability_diagnostics_descriptive_only"

DIAGNOSTIC_CATEGORY_LIFECYCLE = "lifecycle"
DIAGNOSTIC_CATEGORY_DRIFT = "drift"
DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE = "bundle_governance"
DIAGNOSTIC_CATEGORY_VALIDATION = "validation"
DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION = "production_consumption"
DIAGNOSTIC_CATEGORY_RECOVERY = "recovery"
DIAGNOSTIC_CATEGORY_PROVENANCE = "provenance"
DIAGNOSTIC_CATEGORY_LINEAGE = "lineage"
DIAGNOSTIC_CATEGORY_REPLAY = "replay"
DIAGNOSTIC_CATEGORY_ROLLBACK = "rollback"
DIAGNOSTIC_CATEGORY_UNSUPPORTED = "unsupported"
DIAGNOSTIC_CATEGORY_PROHIBITED = "prohibited"
DIAGNOSTIC_CATEGORY_BLOCKED = "blocked"
DIAGNOSTIC_CATEGORY_UNKNOWN = "unknown"
DIAGNOSTIC_CATEGORY_WARNING = "warning"
DIAGNOSTIC_CATEGORY_CRITICAL = "critical"
DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY = "execution_boundary"
OPERATIONAL_DIAGNOSTIC_CATEGORIES: tuple[str, ...] = (
    DIAGNOSTIC_CATEGORY_LIFECYCLE,
    DIAGNOSTIC_CATEGORY_DRIFT,
    DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE,
    DIAGNOSTIC_CATEGORY_VALIDATION,
    DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION,
    DIAGNOSTIC_CATEGORY_RECOVERY,
    DIAGNOSTIC_CATEGORY_PROVENANCE,
    DIAGNOSTIC_CATEGORY_LINEAGE,
    DIAGNOSTIC_CATEGORY_REPLAY,
    DIAGNOSTIC_CATEGORY_ROLLBACK,
    DIAGNOSTIC_CATEGORY_UNSUPPORTED,
    DIAGNOSTIC_CATEGORY_PROHIBITED,
    DIAGNOSTIC_CATEGORY_BLOCKED,
    DIAGNOSTIC_CATEGORY_UNKNOWN,
    DIAGNOSTIC_CATEGORY_WARNING,
    DIAGNOSTIC_CATEGORY_CRITICAL,
    DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY,
)

DIAGNOSTIC_SEVERITY_INFO = "info"
DIAGNOSTIC_SEVERITY_WARNING = "warning"
DIAGNOSTIC_SEVERITY_BLOCKING = "blocking"
DIAGNOSTIC_SEVERITY_CRITICAL = "critical"
DIAGNOSTIC_SEVERITY_PROHIBITED = "prohibited"
DIAGNOSTIC_SEVERITY_UNKNOWN = "unknown"
OPERATIONAL_DIAGNOSTIC_SEVERITIES: tuple[str, ...] = (
    DIAGNOSTIC_SEVERITY_INFO,
    DIAGNOSTIC_SEVERITY_WARNING,
    DIAGNOSTIC_SEVERITY_BLOCKING,
    DIAGNOSTIC_SEVERITY_CRITICAL,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
    DIAGNOSTIC_SEVERITY_UNKNOWN,
)

DIAGNOSTIC_TYPE_LIFECYCLE = "lifecycle_diagnostic"
DIAGNOSTIC_TYPE_DRIFT = "drift_diagnostic"
DIAGNOSTIC_TYPE_BUNDLE_GOVERNANCE = "bundle_governance_diagnostic"
DIAGNOSTIC_TYPE_VALIDATION = "validation_diagnostic"
DIAGNOSTIC_TYPE_PRODUCTION_CONSUMPTION = "production_consumption_diagnostic"
DIAGNOSTIC_TYPE_RECOVERY = "recovery_diagnostic"
DIAGNOSTIC_TYPE_PROVENANCE = "provenance_diagnostic"
DIAGNOSTIC_TYPE_LINEAGE = "lineage_diagnostic"
DIAGNOSTIC_TYPE_REPLAY = "replay_diagnostic"
DIAGNOSTIC_TYPE_ROLLBACK = "rollback_diagnostic"
DIAGNOSTIC_TYPE_UNSUPPORTED_STATE = "unsupported_state_diagnostic"
DIAGNOSTIC_TYPE_PROHIBITED_STATE = "prohibited_state_diagnostic"
DIAGNOSTIC_TYPE_BLOCKED_STATE = "blocked_state_diagnostic"
DIAGNOSTIC_TYPE_UNKNOWN_STATE = "unknown_state_diagnostic"
DIAGNOSTIC_TYPE_WARNING = "warning_diagnostic"
DIAGNOSTIC_TYPE_CRITICAL = "critical_diagnostic"
DIAGNOSTIC_TYPE_EXECUTION_BOUNDARY = "execution_boundary_diagnostic"
OPERATIONAL_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    DIAGNOSTIC_TYPE_LIFECYCLE,
    DIAGNOSTIC_TYPE_DRIFT,
    DIAGNOSTIC_TYPE_BUNDLE_GOVERNANCE,
    DIAGNOSTIC_TYPE_VALIDATION,
    DIAGNOSTIC_TYPE_PRODUCTION_CONSUMPTION,
    DIAGNOSTIC_TYPE_RECOVERY,
    DIAGNOSTIC_TYPE_PROVENANCE,
    DIAGNOSTIC_TYPE_LINEAGE,
    DIAGNOSTIC_TYPE_REPLAY,
    DIAGNOSTIC_TYPE_ROLLBACK,
    DIAGNOSTIC_TYPE_UNSUPPORTED_STATE,
    DIAGNOSTIC_TYPE_PROHIBITED_STATE,
    DIAGNOSTIC_TYPE_BLOCKED_STATE,
    DIAGNOSTIC_TYPE_UNKNOWN_STATE,
    DIAGNOSTIC_TYPE_WARNING,
    DIAGNOSTIC_TYPE_CRITICAL,
    DIAGNOSTIC_TYPE_EXECUTION_BOUNDARY,
)

DIAGNOSTIC_TYPE_CATEGORY_MAP: dict[str, str] = {
    DIAGNOSTIC_TYPE_LIFECYCLE: DIAGNOSTIC_CATEGORY_LIFECYCLE,
    DIAGNOSTIC_TYPE_DRIFT: DIAGNOSTIC_CATEGORY_DRIFT,
    DIAGNOSTIC_TYPE_BUNDLE_GOVERNANCE: DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE,
    DIAGNOSTIC_TYPE_VALIDATION: DIAGNOSTIC_CATEGORY_VALIDATION,
    DIAGNOSTIC_TYPE_PRODUCTION_CONSUMPTION: DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION,
    DIAGNOSTIC_TYPE_RECOVERY: DIAGNOSTIC_CATEGORY_RECOVERY,
    DIAGNOSTIC_TYPE_PROVENANCE: DIAGNOSTIC_CATEGORY_PROVENANCE,
    DIAGNOSTIC_TYPE_LINEAGE: DIAGNOSTIC_CATEGORY_LINEAGE,
    DIAGNOSTIC_TYPE_REPLAY: DIAGNOSTIC_CATEGORY_REPLAY,
    DIAGNOSTIC_TYPE_ROLLBACK: DIAGNOSTIC_CATEGORY_ROLLBACK,
    DIAGNOSTIC_TYPE_UNSUPPORTED_STATE: DIAGNOSTIC_CATEGORY_UNSUPPORTED,
    DIAGNOSTIC_TYPE_PROHIBITED_STATE: DIAGNOSTIC_CATEGORY_PROHIBITED,
    DIAGNOSTIC_TYPE_BLOCKED_STATE: DIAGNOSTIC_CATEGORY_BLOCKED,
    DIAGNOSTIC_TYPE_UNKNOWN_STATE: DIAGNOSTIC_CATEGORY_UNKNOWN,
    DIAGNOSTIC_TYPE_WARNING: DIAGNOSTIC_CATEGORY_WARNING,
    DIAGNOSTIC_TYPE_CRITICAL: DIAGNOSTIC_CATEGORY_CRITICAL,
    DIAGNOSTIC_TYPE_EXECUTION_BOUNDARY: DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY,
}


def _as_tuple(
    values: Iterable["OperationalDiagnosticEntry"] | tuple["OperationalDiagnosticEntry", ...] | None,
) -> tuple["OperationalDiagnosticEntry", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class OperationalDiagnosticCategory:
    category: str
    description: str
    descriptive_only: bool = True
    recommendation_semantics_enabled: bool = False
    ranking_semantics_enabled: bool = False
    scoring_semantics_enabled: bool = False
    selection_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalDiagnosticSeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    ranking_semantics_enabled: bool = False
    scoring_semantics_enabled: bool = False
    selection_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalDiagnosticEntry:
    diagnostic_type: str
    category: str
    severity: str
    lifecycle_reference: str
    drift_reference: str
    governance_reference: str
    validation_reference: str
    production_consumption_reference: str
    recovery_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_reference: str
    rollback_reference: str
    title: str
    explanation: str
    limitation: str
    deterministic_key: str
    descriptive_only: bool = True
    recommendations_present: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    execution_authorized: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class OperationalDiagnosticsReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_report_hash: str
    production_consumption_report_hash: str
    recovery_report_hash: str
    entry_count: int
    entries: tuple[OperationalDiagnosticEntry, ...]
    category_counts: dict[str, int]
    severity_counts: dict[str, int]
    unsupported_count: int
    prohibited_count: int
    blocked_count: int
    unknown_count: int
    warning_count: int
    critical_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    recommendations_present: bool
    execution_authorized: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_OPERATIONAL_DIAGNOSTICS_SCHEMA_VERSION
    phase_id: str = V4_0_OPERATIONAL_DIAGNOSTICS_PHASE_ID
    diagnostics_scope: str = V4_0_OPERATIONAL_DIAGNOSTICS_SCOPE
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", _as_tuple(self.entries))
        object.__setattr__(self, "category_counts", dict(sorted((self.category_counts or {}).items())))
        object.__setattr__(self, "severity_counts", dict(sorted((self.severity_counts or {}).items())))
        object.__setattr__(self, "recommendations_present", False)
        object.__setattr__(self, "execution_authorized", False)


SUPPORTED_OPERATIONAL_DIAGNOSTIC_CATEGORY_MODELS: tuple[OperationalDiagnosticCategory, ...] = (
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_LIFECYCLE, "lifecycle evidence diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_DRIFT, "drift evidence diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE, "bundle governance diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_VALIDATION, "validation evidence diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION, "production consumption diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_RECOVERY, "rollback and recovery diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_PROVENANCE, "provenance diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_LINEAGE, "lineage diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_REPLAY, "replay diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_ROLLBACK, "rollback diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_UNSUPPORTED, "unsupported-state diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_PROHIBITED, "prohibited-state diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_BLOCKED, "blocked-state diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_UNKNOWN, "unknown-state diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_WARNING, "warning diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_CRITICAL, "critical diagnostics"),
    OperationalDiagnosticCategory(DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY, "execution-boundary diagnostics"),
)

SUPPORTED_OPERATIONAL_DIAGNOSTIC_SEVERITY_MODELS: tuple[OperationalDiagnosticSeverity, ...] = (
    OperationalDiagnosticSeverity(DIAGNOSTIC_SEVERITY_INFO, "descriptive informational diagnostic evidence"),
    OperationalDiagnosticSeverity(DIAGNOSTIC_SEVERITY_WARNING, "descriptive warning diagnostic evidence"),
    OperationalDiagnosticSeverity(DIAGNOSTIC_SEVERITY_BLOCKING, "descriptive blocking diagnostic evidence"),
    OperationalDiagnosticSeverity(DIAGNOSTIC_SEVERITY_CRITICAL, "descriptive critical diagnostic evidence"),
    OperationalDiagnosticSeverity(DIAGNOSTIC_SEVERITY_PROHIBITED, "descriptive prohibited diagnostic evidence"),
    OperationalDiagnosticSeverity(DIAGNOSTIC_SEVERITY_UNKNOWN, "descriptive unknown diagnostic evidence"),
)
