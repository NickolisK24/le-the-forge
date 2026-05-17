"""Deterministic operational lifecycle continuity certification models.

Continuity certification is descriptive evidence only. It certifies that
v4.0 operational lifecycle evidence remains connected, reproducible, and
auditable without authorizing execution, remediation, approval, production
consumption, orchestration, or runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_CONTINUITY_CERTIFICATION_PHASE_ID = "v4_0_operational_lifecycle_continuity_certification"
V4_0_CONTINUITY_CERTIFICATION_SCHEMA_VERSION = "v4_0.operational_lifecycle_continuity_certification.1"
V4_0_CONTINUITY_CERTIFICATION_STATUS_STABLE = "v4_0_operational_lifecycle_continuity_certification_stable"
V4_0_CONTINUITY_CERTIFICATION_STATUS_BLOCKED = "v4_0_operational_lifecycle_continuity_certification_blocked"
V4_0_CONTINUITY_CERTIFICATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_CONTINUITY_CERTIFICATION_SCOPE = "operational_lifecycle_continuity_certification_descriptive_only"

CONTINUITY_STATUS_CERTIFIED = "continuity_certified"
CONTINUITY_STATUS_WARNING = "continuity_warning"
CONTINUITY_STATUS_BROKEN = "continuity_broken"
CONTINUITY_STATUS_BLOCKED = "blocked"
CONTINUITY_STATUS_UNKNOWN = "unknown"
CONTINUITY_STATUS_PROHIBITED = "prohibited"
OPERATIONAL_CONTINUITY_STATUSES: tuple[str, ...] = (
    CONTINUITY_STATUS_CERTIFIED,
    CONTINUITY_STATUS_WARNING,
    CONTINUITY_STATUS_BROKEN,
    CONTINUITY_STATUS_BLOCKED,
    CONTINUITY_STATUS_UNKNOWN,
    CONTINUITY_STATUS_PROHIBITED,
)

CONTINUITY_SEVERITY_INFO = "info"
CONTINUITY_SEVERITY_WARNING = "warning"
CONTINUITY_SEVERITY_BLOCKING = "blocking"
CONTINUITY_SEVERITY_CRITICAL = "critical"
CONTINUITY_SEVERITY_PROHIBITED = "prohibited"
CONTINUITY_SEVERITY_UNKNOWN = "unknown"
OPERATIONAL_CONTINUITY_SEVERITIES: tuple[str, ...] = (
    CONTINUITY_SEVERITY_INFO,
    CONTINUITY_SEVERITY_WARNING,
    CONTINUITY_SEVERITY_BLOCKING,
    CONTINUITY_SEVERITY_CRITICAL,
    CONTINUITY_SEVERITY_PROHIBITED,
    CONTINUITY_SEVERITY_UNKNOWN,
)

CONTINUITY_FINDING_LIFECYCLE = "lifecycle_continuity_certification"
CONTINUITY_FINDING_DRIFT = "drift_continuity_certification"
CONTINUITY_FINDING_BUNDLE_GOVERNANCE = "bundle_governance_continuity_certification"
CONTINUITY_FINDING_OPERATIONAL_VALIDATION = "operational_validation_continuity_certification"
CONTINUITY_FINDING_PRODUCTION_CONSUMPTION = "production_consumption_continuity_certification"
CONTINUITY_FINDING_RECOVERY = "recovery_continuity_certification"
CONTINUITY_FINDING_DIAGNOSTICS = "diagnostics_continuity_certification"
CONTINUITY_FINDING_INTEGRITY = "integrity_continuity_certification"
CONTINUITY_FINDING_PROVENANCE = "provenance_continuity_certification"
CONTINUITY_FINDING_LINEAGE = "lineage_continuity_certification"
CONTINUITY_FINDING_REPLAY = "replay_continuity_certification"
CONTINUITY_FINDING_ROLLBACK = "rollback_continuity_certification"
CONTINUITY_FINDING_SERIALIZATION = "serialization_continuity_certification"
CONTINUITY_FINDING_HASHING = "hashing_continuity_certification"
CONTINUITY_FINDING_VISIBILITY = "visibility_continuity_certification"
CONTINUITY_FINDING_NON_EXECUTION = "non_execution_continuity_certification"
CONTINUITY_FINDING_NON_REMEDIATION = "non_remediation_continuity_certification"
CONTINUITY_FINDING_NON_AUTHORIZATION = "non_authorization_continuity_certification"
CONTINUITY_FINDING_PRODUCTION_DISABLED = "production_consumption_disabled_certification"
CONTINUITY_FINDING_PROHIBITED_STATE = "prohibited_state_continuity_certification"
CONTINUITY_FINDING_UNKNOWN_STATE = "unknown_state_continuity_certification"
OPERATIONAL_CONTINUITY_FINDING_TYPES: tuple[str, ...] = (
    CONTINUITY_FINDING_LIFECYCLE,
    CONTINUITY_FINDING_DRIFT,
    CONTINUITY_FINDING_BUNDLE_GOVERNANCE,
    CONTINUITY_FINDING_OPERATIONAL_VALIDATION,
    CONTINUITY_FINDING_PRODUCTION_CONSUMPTION,
    CONTINUITY_FINDING_RECOVERY,
    CONTINUITY_FINDING_DIAGNOSTICS,
    CONTINUITY_FINDING_INTEGRITY,
    CONTINUITY_FINDING_PROVENANCE,
    CONTINUITY_FINDING_LINEAGE,
    CONTINUITY_FINDING_REPLAY,
    CONTINUITY_FINDING_ROLLBACK,
    CONTINUITY_FINDING_SERIALIZATION,
    CONTINUITY_FINDING_HASHING,
    CONTINUITY_FINDING_VISIBILITY,
    CONTINUITY_FINDING_NON_EXECUTION,
    CONTINUITY_FINDING_NON_REMEDIATION,
    CONTINUITY_FINDING_NON_AUTHORIZATION,
    CONTINUITY_FINDING_PRODUCTION_DISABLED,
    CONTINUITY_FINDING_PROHIBITED_STATE,
    CONTINUITY_FINDING_UNKNOWN_STATE,
)


def _as_tuple(
    values: Iterable["OperationalContinuityFinding"] | tuple["OperationalContinuityFinding", ...] | None,
) -> tuple["OperationalContinuityFinding", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class OperationalContinuityStatus:
    status: str
    description: str
    descriptive_only: bool = True
    execution_semantics_enabled: bool = False
    approval_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    remediation_semantics_enabled: bool = False
    production_consumption_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalContinuitySeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    priority_semantics_enabled: bool = False
    scoring_semantics_enabled: bool = False
    remediation_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalContinuityFinding:
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
    integrity_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_reference: str
    rollback_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    execution_authorized: bool = False
    remediation_authorized: bool = False
    production_consumption_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class OperationalContinuityCertificationReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_report_hash: str
    production_consumption_report_hash: str
    recovery_report_hash: str
    diagnostics_report_hash: str
    integrity_report_hash: str
    continuity_status: str
    finding_count: int
    findings: tuple[OperationalContinuityFinding, ...]
    certified_count: int
    warning_count: int
    broken_count: int
    blocked_count: int
    prohibited_count: int
    unknown_count: int
    critical_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    serialization_stable: bool
    hashing_stable: bool
    visibility_preserved: bool
    integrity_preserved: bool
    execution_authorized: bool
    remediation_authorized: bool
    production_consumption_enabled: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_CONTINUITY_CERTIFICATION_SCHEMA_VERSION
    phase_id: str = V4_0_CONTINUITY_CERTIFICATION_PHASE_ID
    certification_scope: str = V4_0_CONTINUITY_CERTIFICATION_SCOPE
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
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
        object.__setattr__(self, "execution_authorized", False)
        object.__setattr__(self, "remediation_authorized", False)
        object.__setattr__(self, "production_consumption_enabled", False)


SUPPORTED_OPERATIONAL_CONTINUITY_STATUS_MODELS: tuple[OperationalContinuityStatus, ...] = (
    OperationalContinuityStatus(CONTINUITY_STATUS_CERTIFIED, "continuity evidence is visible and consistent"),
    OperationalContinuityStatus(CONTINUITY_STATUS_WARNING, "continuity evidence includes warning visibility"),
    OperationalContinuityStatus(CONTINUITY_STATUS_BROKEN, "continuity evidence exposes broken continuity"),
    OperationalContinuityStatus(CONTINUITY_STATUS_BLOCKED, "continuity evidence exposes blockers"),
    OperationalContinuityStatus(CONTINUITY_STATUS_UNKNOWN, "continuity evidence exposes unknown state"),
    OperationalContinuityStatus(CONTINUITY_STATUS_PROHIBITED, "continuity evidence exposes prohibited state"),
)

SUPPORTED_OPERATIONAL_CONTINUITY_SEVERITY_MODELS: tuple[OperationalContinuitySeverity, ...] = (
    OperationalContinuitySeverity(CONTINUITY_SEVERITY_INFO, "descriptive informational continuity evidence"),
    OperationalContinuitySeverity(CONTINUITY_SEVERITY_WARNING, "descriptive warning continuity evidence"),
    OperationalContinuitySeverity(CONTINUITY_SEVERITY_BLOCKING, "descriptive blocking continuity evidence"),
    OperationalContinuitySeverity(CONTINUITY_SEVERITY_CRITICAL, "descriptive critical continuity evidence"),
    OperationalContinuitySeverity(CONTINUITY_SEVERITY_PROHIBITED, "descriptive prohibited continuity evidence"),
    OperationalContinuitySeverity(CONTINUITY_SEVERITY_UNKNOWN, "descriptive unknown continuity evidence"),
)
