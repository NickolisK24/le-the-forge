"""Deterministic rollback and recovery certification models.

Recovery certification is descriptive evidence only. It does not execute
rollback, execute recovery, repair data, authorize production consumption,
approve deployment, remediate blockers, or mutate runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_RECOVERY_CERTIFICATION_PHASE_ID = "v4_0_rollback_recovery_certification"
V4_0_RECOVERY_CERTIFICATION_SCHEMA_VERSION = "v4_0.rollback_recovery_certification.1"
V4_0_RECOVERY_CERTIFICATION_STATUS_STABLE = "v4_0_rollback_recovery_certification_stable"
V4_0_RECOVERY_CERTIFICATION_STATUS_BLOCKED = "v4_0_rollback_recovery_certification_blocked"
V4_0_RECOVERY_CERTIFICATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_RECOVERY_CERTIFICATION_SCOPE = "rollback_recovery_certification_descriptive_only"

RECOVERY_CERTIFICATION_STATE_CERTIFIABLE = "certifiable"
RECOVERY_CERTIFICATION_STATE_NOT_CERTIFIABLE = "not_certifiable"
RECOVERY_CERTIFICATION_STATE_BLOCKED = "blocked"
RECOVERY_CERTIFICATION_STATE_UNSUPPORTED = "unsupported"
RECOVERY_CERTIFICATION_STATE_EXPERIMENTAL = "experimental"
RECOVERY_CERTIFICATION_STATE_UNKNOWN = "unknown"
RECOVERY_CERTIFICATION_STATE_PROHIBITED = "prohibited"
RECOVERY_CERTIFICATION_STATES: tuple[str, ...] = (
    RECOVERY_CERTIFICATION_STATE_CERTIFIABLE,
    RECOVERY_CERTIFICATION_STATE_NOT_CERTIFIABLE,
    RECOVERY_CERTIFICATION_STATE_BLOCKED,
    RECOVERY_CERTIFICATION_STATE_UNSUPPORTED,
    RECOVERY_CERTIFICATION_STATE_EXPERIMENTAL,
    RECOVERY_CERTIFICATION_STATE_UNKNOWN,
    RECOVERY_CERTIFICATION_STATE_PROHIBITED,
)

RECOVERY_CERTIFICATION_SEVERITY_INFO = "info"
RECOVERY_CERTIFICATION_SEVERITY_WARNING = "warning"
RECOVERY_CERTIFICATION_SEVERITY_BLOCKING = "blocking"
RECOVERY_CERTIFICATION_SEVERITY_CRITICAL = "critical"
RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED = "prohibited"
RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN = "unknown"
RECOVERY_CERTIFICATION_SEVERITIES: tuple[str, ...] = (
    RECOVERY_CERTIFICATION_SEVERITY_INFO,
    RECOVERY_CERTIFICATION_SEVERITY_WARNING,
    RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
    RECOVERY_CERTIFICATION_SEVERITY_CRITICAL,
    RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED,
    RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN,
)

RECOVERY_FINDING_LIFECYCLE_RECOVERY_VISIBILITY = "lifecycle_recovery_visibility"
RECOVERY_FINDING_DRIFT_RECOVERY_VISIBILITY = "drift_recovery_visibility"
RECOVERY_FINDING_BUNDLE_GOVERNANCE_RECOVERY_VISIBILITY = "bundle_governance_recovery_visibility"
RECOVERY_FINDING_OPERATIONAL_VALIDATION_RECOVERY_VISIBILITY = "operational_validation_recovery_visibility"
RECOVERY_FINDING_PRODUCTION_CONSUMPTION_RECOVERY_VISIBILITY = "production_consumption_recovery_visibility"
RECOVERY_FINDING_PROVENANCE_RECOVERY_CONTINUITY = "provenance_recovery_continuity"
RECOVERY_FINDING_LINEAGE_RECOVERY_CONTINUITY = "lineage_recovery_continuity"
RECOVERY_FINDING_REPLAY_RECOVERY_CONTINUITY = "replay_recovery_continuity"
RECOVERY_FINDING_ROLLBACK_RECOVERY_CONTINUITY = "rollback_recovery_continuity"
RECOVERY_FINDING_UNSUPPORTED_RECOVERY_STATE = "unsupported_recovery_state"
RECOVERY_FINDING_PROHIBITED_RECOVERY_STATE = "prohibited_recovery_state"
RECOVERY_FINDING_BLOCKED_RECOVERY_STATE = "blocked_recovery_state"
RECOVERY_FINDING_UNKNOWN_RECOVERY_STATE = "unknown_recovery_state"
RECOVERY_FINDING_RECOVERY_WARNING_VISIBILITY = "recovery_warning_visibility"
RECOVERY_FINDING_CRITICAL_RECOVERY_VISIBILITY = "critical_recovery_visibility"
RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS = "recovery_certification_readiness"
RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED = "rollback_execution_prohibited"
RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED = "recovery_execution_prohibited"
RECOVERY_CERTIFICATION_FINDING_TYPES: tuple[str, ...] = (
    RECOVERY_FINDING_LIFECYCLE_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_DRIFT_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_BUNDLE_GOVERNANCE_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_OPERATIONAL_VALIDATION_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_PRODUCTION_CONSUMPTION_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_PROVENANCE_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_LINEAGE_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_REPLAY_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_ROLLBACK_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_UNSUPPORTED_RECOVERY_STATE,
    RECOVERY_FINDING_PROHIBITED_RECOVERY_STATE,
    RECOVERY_FINDING_BLOCKED_RECOVERY_STATE,
    RECOVERY_FINDING_UNKNOWN_RECOVERY_STATE,
    RECOVERY_FINDING_RECOVERY_WARNING_VISIBILITY,
    RECOVERY_FINDING_CRITICAL_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS,
    RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED,
    RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED,
)


def _as_tuple(
    values: Iterable["RecoveryCertificationFinding"] | tuple["RecoveryCertificationFinding", ...] | None,
) -> tuple["RecoveryCertificationFinding", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class RecoveryCertificationState:
    state: str
    description: str
    descriptive_only: bool = True
    approval_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    rollback_execution_semantics_enabled: bool = False
    recovery_execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class RecoveryCertificationSeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    approval_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class RecoveryCertificationFinding:
    finding_type: str
    severity: str
    lifecycle_reference: str
    drift_reference: str
    governance_reference: str
    validation_reference: str
    production_consumption_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_reference: str
    rollback_reference: str
    recovery_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    recovery_execution_authorized: bool = False
    rollback_execution_authorized: bool = False
    recovery_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class RecoveryCertificationReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_report_hash: str
    production_consumption_report_hash: str
    certification_state: str
    finding_count: int
    findings: tuple[RecoveryCertificationFinding, ...]
    certifiable_finding_count: int
    blocked_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    warning_count: int
    critical_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    recovery_execution_authorized: bool
    rollback_execution_authorized: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_RECOVERY_CERTIFICATION_SCHEMA_VERSION
    phase_id: str = V4_0_RECOVERY_CERTIFICATION_PHASE_ID
    certification_scope: str = V4_0_RECOVERY_CERTIFICATION_SCOPE
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    recovery_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    production_consumption_authorized: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "findings", _as_tuple(self.findings))
        object.__setattr__(self, "recovery_execution_authorized", False)
        object.__setattr__(self, "rollback_execution_authorized", False)
        object.__setattr__(self, "recovery_execution_enabled", False)
        object.__setattr__(self, "rollback_execution_enabled", False)
        object.__setattr__(self, "production_consumption_authorized", False)


SUPPORTED_RECOVERY_CERTIFICATION_STATE_MODELS: tuple[RecoveryCertificationState, ...] = (
    RecoveryCertificationState(
        RECOVERY_CERTIFICATION_STATE_CERTIFIABLE,
        "recovery evidence is visible and internally consistent without authorization or execution semantics",
    ),
    RecoveryCertificationState(RECOVERY_CERTIFICATION_STATE_NOT_CERTIFIABLE, "recovery evidence is not certifiable"),
    RecoveryCertificationState(RECOVERY_CERTIFICATION_STATE_BLOCKED, "recovery evidence exposes blockers"),
    RecoveryCertificationState(RECOVERY_CERTIFICATION_STATE_UNSUPPORTED, "unsupported recovery evidence is visible"),
    RecoveryCertificationState(RECOVERY_CERTIFICATION_STATE_EXPERIMENTAL, "experimental recovery evidence is visible"),
    RecoveryCertificationState(RECOVERY_CERTIFICATION_STATE_UNKNOWN, "unknown recovery evidence is visible"),
    RecoveryCertificationState(RECOVERY_CERTIFICATION_STATE_PROHIBITED, "prohibited recovery evidence is visible"),
)

SUPPORTED_RECOVERY_CERTIFICATION_SEVERITY_MODELS: tuple[RecoveryCertificationSeverity, ...] = (
    RecoveryCertificationSeverity(RECOVERY_CERTIFICATION_SEVERITY_INFO, "descriptive informational recovery evidence"),
    RecoveryCertificationSeverity(RECOVERY_CERTIFICATION_SEVERITY_WARNING, "descriptive warning recovery evidence"),
    RecoveryCertificationSeverity(RECOVERY_CERTIFICATION_SEVERITY_BLOCKING, "descriptive blocking recovery evidence"),
    RecoveryCertificationSeverity(RECOVERY_CERTIFICATION_SEVERITY_CRITICAL, "descriptive critical recovery evidence"),
    RecoveryCertificationSeverity(RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED, "descriptive prohibited recovery evidence"),
    RecoveryCertificationSeverity(RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN, "descriptive unknown recovery evidence"),
)
