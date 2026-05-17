"""Deterministic operational lifecycle integrity enforcement models.

Integrity enforcement is deterministic audit evidence only. It detects and
exposes prohibited behavior leakage without correcting, remediating, repairing,
authorizing, executing, orchestrating, recommending, or mutating source state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_INTEGRITY_ENFORCEMENT_PHASE_ID = "v4_0_operational_lifecycle_integrity_enforcement"
V4_0_INTEGRITY_ENFORCEMENT_SCHEMA_VERSION = "v4_0.operational_lifecycle_integrity_enforcement.1"
V4_0_INTEGRITY_ENFORCEMENT_STATUS_STABLE = "v4_0_operational_lifecycle_integrity_enforcement_stable"
V4_0_INTEGRITY_ENFORCEMENT_STATUS_BLOCKED = "v4_0_operational_lifecycle_integrity_enforcement_blocked"
V4_0_INTEGRITY_ENFORCEMENT_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_INTEGRITY_ENFORCEMENT_SCOPE = "operational_lifecycle_integrity_enforcement_descriptive_only"

INTEGRITY_STATUS_PRESERVED = "integrity_preserved"
INTEGRITY_STATUS_WARNING = "integrity_warning"
INTEGRITY_STATUS_VIOLATION = "integrity_violation"
INTEGRITY_STATUS_BLOCKED = "blocked"
INTEGRITY_STATUS_UNKNOWN = "unknown"
INTEGRITY_STATUS_PROHIBITED = "prohibited"
OPERATIONAL_INTEGRITY_STATUSES: tuple[str, ...] = (
    INTEGRITY_STATUS_PRESERVED,
    INTEGRITY_STATUS_WARNING,
    INTEGRITY_STATUS_VIOLATION,
    INTEGRITY_STATUS_BLOCKED,
    INTEGRITY_STATUS_UNKNOWN,
    INTEGRITY_STATUS_PROHIBITED,
)

INTEGRITY_SEVERITY_INFO = "info"
INTEGRITY_SEVERITY_WARNING = "warning"
INTEGRITY_SEVERITY_BLOCKING = "blocking"
INTEGRITY_SEVERITY_CRITICAL = "critical"
INTEGRITY_SEVERITY_PROHIBITED = "prohibited"
INTEGRITY_SEVERITY_UNKNOWN = "unknown"
OPERATIONAL_INTEGRITY_SEVERITIES: tuple[str, ...] = (
    INTEGRITY_SEVERITY_INFO,
    INTEGRITY_SEVERITY_WARNING,
    INTEGRITY_SEVERITY_BLOCKING,
    INTEGRITY_SEVERITY_CRITICAL,
    INTEGRITY_SEVERITY_PROHIBITED,
    INTEGRITY_SEVERITY_UNKNOWN,
)

INTEGRITY_FINDING_EXECUTION_LEAKAGE = "execution_leakage_check"
INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE = "orchestration_leakage_check"
INTEGRITY_FINDING_REMEDIATION_LEAKAGE = "remediation_leakage_check"
INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE = "recommendation_leakage_check"
INTEGRITY_FINDING_RANKING_LEAKAGE = "ranking_leakage_check"
INTEGRITY_FINDING_SCORING_LEAKAGE = "scoring_leakage_check"
INTEGRITY_FINDING_SELECTION_LEAKAGE = "selection_leakage_check"
INTEGRITY_FINDING_APPROVAL_LEAKAGE = "approval_leakage_check"
INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE = "authorization_leakage_check"
INTEGRITY_FINDING_MUTATION_LEAKAGE = "mutation_leakage_check"
INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE = "production_consumption_leakage_check"
INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE = "planner_integration_leakage_check"
INTEGRITY_FINDING_FALLBACK_LEAKAGE = "fallback_leakage_check"
INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION = "diagnostic_suppression_check"
INTEGRITY_FINDING_EVIDENCE_CONTINUITY = "evidence_continuity_check"
INTEGRITY_FINDING_PROVENANCE_CONTINUITY = "provenance_continuity_check"
INTEGRITY_FINDING_LINEAGE_CONTINUITY = "lineage_continuity_check"
INTEGRITY_FINDING_REPLAY_CONTINUITY = "replay_continuity_check"
INTEGRITY_FINDING_ROLLBACK_CONTINUITY = "rollback_continuity_check"
INTEGRITY_FINDING_PROHIBITED_STATE = "prohibited_state_check"
INTEGRITY_FINDING_BOUNDARY = "integrity_enforcement_boundary_check"
OPERATIONAL_INTEGRITY_FINDING_TYPES: tuple[str, ...] = (
    INTEGRITY_FINDING_EXECUTION_LEAKAGE,
    INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE,
    INTEGRITY_FINDING_REMEDIATION_LEAKAGE,
    INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE,
    INTEGRITY_FINDING_RANKING_LEAKAGE,
    INTEGRITY_FINDING_SCORING_LEAKAGE,
    INTEGRITY_FINDING_SELECTION_LEAKAGE,
    INTEGRITY_FINDING_APPROVAL_LEAKAGE,
    INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE,
    INTEGRITY_FINDING_MUTATION_LEAKAGE,
    INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE,
    INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE,
    INTEGRITY_FINDING_FALLBACK_LEAKAGE,
    INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION,
    INTEGRITY_FINDING_EVIDENCE_CONTINUITY,
    INTEGRITY_FINDING_PROVENANCE_CONTINUITY,
    INTEGRITY_FINDING_LINEAGE_CONTINUITY,
    INTEGRITY_FINDING_REPLAY_CONTINUITY,
    INTEGRITY_FINDING_ROLLBACK_CONTINUITY,
    INTEGRITY_FINDING_PROHIBITED_STATE,
    INTEGRITY_FINDING_BOUNDARY,
)


def _as_tuple(
    values: Iterable["OperationalIntegrityFinding"] | tuple["OperationalIntegrityFinding", ...] | None,
) -> tuple["OperationalIntegrityFinding", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class OperationalIntegrityStatus:
    status: str
    description: str
    descriptive_only: bool = True
    correction_semantics_enabled: bool = False
    remediation_semantics_enabled: bool = False
    approval_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalIntegritySeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    remediation_priority_enabled: bool = False
    correction_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalIntegrityFinding:
    finding_type: str
    severity: str
    source_phase: str
    lifecycle_reference: str
    drift_reference: str
    governance_reference: str
    validation_reference: str
    production_consumption_reference: str
    recovery_reference: str
    diagnostics_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_reference: str
    rollback_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    remediation_enabled: bool = False
    correction_enabled: bool = False
    repair_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class OperationalIntegrityReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_report_hash: str
    production_consumption_report_hash: str
    recovery_report_hash: str
    diagnostics_report_hash: str
    integrity_status: str
    finding_count: int
    findings: tuple[OperationalIntegrityFinding, ...]
    violation_count: int
    warning_count: int
    blocked_count: int
    prohibited_count: int
    unknown_count: int
    critical_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    execution_leakage_detected: bool
    orchestration_leakage_detected: bool
    remediation_leakage_detected: bool
    recommendation_leakage_detected: bool
    ranking_leakage_detected: bool
    scoring_leakage_detected: bool
    selection_leakage_detected: bool
    approval_leakage_detected: bool
    authorization_leakage_detected: bool
    mutation_leakage_detected: bool
    production_consumption_leakage_detected: bool
    planner_integration_leakage_detected: bool
    integrity_enforcement_performed: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_INTEGRITY_ENFORCEMENT_SCHEMA_VERSION
    phase_id: str = V4_0_INTEGRITY_ENFORCEMENT_PHASE_ID
    integrity_scope: str = V4_0_INTEGRITY_ENFORCEMENT_SCOPE
    descriptive_only: bool = True
    correction_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "findings", _as_tuple(self.findings))
        object.__setattr__(self, "integrity_enforcement_performed", True)


SUPPORTED_OPERATIONAL_INTEGRITY_STATUS_MODELS: tuple[OperationalIntegrityStatus, ...] = (
    OperationalIntegrityStatus(INTEGRITY_STATUS_PRESERVED, "integrity evidence is preserved"),
    OperationalIntegrityStatus(INTEGRITY_STATUS_WARNING, "integrity evidence includes warning visibility"),
    OperationalIntegrityStatus(INTEGRITY_STATUS_VIOLATION, "integrity evidence exposes prohibited leakage"),
    OperationalIntegrityStatus(INTEGRITY_STATUS_BLOCKED, "integrity evidence exposes blocked continuity"),
    OperationalIntegrityStatus(INTEGRITY_STATUS_UNKNOWN, "integrity evidence exposes unknown state"),
    OperationalIntegrityStatus(INTEGRITY_STATUS_PROHIBITED, "integrity evidence exposes prohibited state"),
)

SUPPORTED_OPERATIONAL_INTEGRITY_SEVERITY_MODELS: tuple[OperationalIntegritySeverity, ...] = (
    OperationalIntegritySeverity(INTEGRITY_SEVERITY_INFO, "descriptive informational integrity evidence"),
    OperationalIntegritySeverity(INTEGRITY_SEVERITY_WARNING, "descriptive warning integrity evidence"),
    OperationalIntegritySeverity(INTEGRITY_SEVERITY_BLOCKING, "descriptive blocking integrity evidence"),
    OperationalIntegritySeverity(INTEGRITY_SEVERITY_CRITICAL, "descriptive critical integrity evidence"),
    OperationalIntegritySeverity(INTEGRITY_SEVERITY_PROHIBITED, "descriptive prohibited integrity evidence"),
    OperationalIntegritySeverity(INTEGRITY_SEVERITY_UNKNOWN, "descriptive unknown integrity evidence"),
)
