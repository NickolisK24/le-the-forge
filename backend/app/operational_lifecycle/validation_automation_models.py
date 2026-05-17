"""Deterministic operational validation automation models.

Operational validation automation produces descriptive evidence only. It does
not authorize execution, deploy, approve, remediate, route, schedule, dispatch,
or mutate lifecycle, drift, governance, or runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_OPERATIONAL_VALIDATION_AUTOMATION_PHASE_ID = "v4_0_operational_validation_automation"
V4_0_OPERATIONAL_VALIDATION_AUTOMATION_SCHEMA_VERSION = "v4_0.operational_validation_automation.1"
V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_STABLE = "v4_0_operational_validation_automation_stable"
V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_BLOCKED = "v4_0_operational_validation_automation_blocked"
V4_0_OPERATIONAL_VALIDATION_AUTOMATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_OPERATIONAL_VALIDATION_AUTOMATION_SCOPE = "operational_validation_automation_descriptive_only"

OPERATIONAL_VALIDATION_STATE_READY = "ready"
OPERATIONAL_VALIDATION_STATE_NOT_READY = "not_ready"
OPERATIONAL_VALIDATION_STATE_BLOCKED = "blocked"
OPERATIONAL_VALIDATION_STATE_UNSUPPORTED = "unsupported"
OPERATIONAL_VALIDATION_STATE_EXPERIMENTAL = "experimental"
OPERATIONAL_VALIDATION_STATE_UNKNOWN = "unknown"
OPERATIONAL_VALIDATION_STATE_PROHIBITED = "prohibited"
OPERATIONAL_VALIDATION_STATES: tuple[str, ...] = (
    OPERATIONAL_VALIDATION_STATE_READY,
    OPERATIONAL_VALIDATION_STATE_NOT_READY,
    OPERATIONAL_VALIDATION_STATE_BLOCKED,
    OPERATIONAL_VALIDATION_STATE_UNSUPPORTED,
    OPERATIONAL_VALIDATION_STATE_EXPERIMENTAL,
    OPERATIONAL_VALIDATION_STATE_UNKNOWN,
    OPERATIONAL_VALIDATION_STATE_PROHIBITED,
)

OPERATIONAL_VALIDATION_SEVERITY_INFO = "info"
OPERATIONAL_VALIDATION_SEVERITY_WARNING = "warning"
OPERATIONAL_VALIDATION_SEVERITY_BLOCKING = "blocking"
OPERATIONAL_VALIDATION_SEVERITY_CRITICAL = "critical"
OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED = "prohibited"
OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN = "unknown"
OPERATIONAL_VALIDATION_SEVERITIES: tuple[str, ...] = (
    OPERATIONAL_VALIDATION_SEVERITY_INFO,
    OPERATIONAL_VALIDATION_SEVERITY_WARNING,
    OPERATIONAL_VALIDATION_SEVERITY_BLOCKING,
    OPERATIONAL_VALIDATION_SEVERITY_CRITICAL,
    OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED,
    OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN,
)

VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY = "lifecycle_validation_visibility"
VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY = "drift_validation_visibility"
VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY = "governance_validation_visibility"
VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY = "provenance_validation_visibility"
VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY = "lineage_validation_visibility"
VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY = "replay_validation_visibility"
VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY = "rollback_validation_visibility"
VALIDATION_FINDING_UNSUPPORTED_VALIDATION_VISIBILITY = "unsupported_validation_visibility"
VALIDATION_FINDING_PROHIBITED_VALIDATION_VISIBILITY = "prohibited_validation_visibility"
VALIDATION_FINDING_BLOCKED_VALIDATION_VISIBILITY = "blocked_validation_visibility"
VALIDATION_FINDING_VALIDATION_WARNING_VISIBILITY = "validation_warning_visibility"
VALIDATION_FINDING_CRITICAL_VALIDATION_VISIBILITY = "critical_validation_visibility"
VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED = "operational_execution_prohibited"
VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS = "operational_certification_readiness"
VALIDATION_FINDING_UNKNOWN_VALIDATION_STATE = "unknown_validation_state"
OPERATIONAL_VALIDATION_FINDING_TYPES: tuple[str, ...] = (
    VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_UNSUPPORTED_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_PROHIBITED_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_BLOCKED_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_VALIDATION_WARNING_VISIBILITY,
    VALIDATION_FINDING_CRITICAL_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED,
    VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS,
    VALIDATION_FINDING_UNKNOWN_VALIDATION_STATE,
)


def _as_tuple(
    values: Iterable["OperationalValidationFinding"] | tuple["OperationalValidationFinding", ...] | None,
) -> tuple["OperationalValidationFinding", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class OperationalValidationState:
    state: str
    description: str
    descriptive_only: bool = True
    approval_semantics_enabled: bool = False
    deployment_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalValidationSeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    execution_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    remediation_semantics_enabled: bool = False


@dataclass(frozen=True)
class OperationalValidationFinding:
    finding_type: str
    severity: str
    lifecycle_reference: str
    drift_reference: str
    governance_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_reference: str
    rollback_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    authorization_enabled: bool = False
    approval_enabled: bool = False
    deployment_enabled: bool = False
    remediation_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class OperationalValidationReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_state: str
    finding_count: int
    findings: tuple[OperationalValidationFinding, ...]
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
    operational_execution_authorized: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_OPERATIONAL_VALIDATION_AUTOMATION_SCHEMA_VERSION
    phase_id: str = V4_0_OPERATIONAL_VALIDATION_AUTOMATION_PHASE_ID
    validation_scope: str = V4_0_OPERATIONAL_VALIDATION_AUTOMATION_SCOPE
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    deployment_enabled: bool = False
    remediation_enabled: bool = False
    execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    production_consumption_authorized: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "findings", _as_tuple(self.findings))
        object.__setattr__(self, "operational_execution_authorized", False)
        object.__setattr__(self, "production_consumption_authorized", False)


SUPPORTED_OPERATIONAL_VALIDATION_STATE_MODELS: tuple[OperationalValidationState, ...] = (
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_READY, "descriptive validation evidence is ready"),
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_NOT_READY, "descriptive validation evidence is not ready"),
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_BLOCKED, "descriptive validation evidence is blocked"),
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_UNSUPPORTED, "unsupported validation evidence is visible"),
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_EXPERIMENTAL, "experimental validation evidence is visible"),
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_UNKNOWN, "unknown validation evidence is visible"),
    OperationalValidationState(OPERATIONAL_VALIDATION_STATE_PROHIBITED, "prohibited validation evidence is visible"),
)

SUPPORTED_OPERATIONAL_VALIDATION_SEVERITY_MODELS: tuple[OperationalValidationSeverity, ...] = (
    OperationalValidationSeverity(OPERATIONAL_VALIDATION_SEVERITY_INFO, "descriptive informational validation evidence"),
    OperationalValidationSeverity(OPERATIONAL_VALIDATION_SEVERITY_WARNING, "descriptive warning validation evidence"),
    OperationalValidationSeverity(OPERATIONAL_VALIDATION_SEVERITY_BLOCKING, "descriptive blocking validation evidence"),
    OperationalValidationSeverity(OPERATIONAL_VALIDATION_SEVERITY_CRITICAL, "descriptive critical validation evidence"),
    OperationalValidationSeverity(OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED, "descriptive prohibited validation evidence"),
    OperationalValidationSeverity(OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN, "descriptive unknown validation evidence"),
)
