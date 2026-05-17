"""Deterministic v4.0 closeout and v4.1 readiness certification models.

Closeout certification is descriptive evidence only. It proves the v4.0
operational lifecycle governance chain remained deterministic and safe without
authorizing execution, remediation, production consumption, orchestration,
planner integration, approval, or runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_CLOSEOUT_PHASE_ID = "v4_0_closeout_and_v4_1_readiness"
V4_0_CLOSEOUT_SCHEMA_VERSION = "v4_0.closeout_and_v4_1_readiness.1"
V4_0_CLOSEOUT_STATUS_STABLE = "v4_0_closeout_and_v4_1_readiness_stable"
V4_0_CLOSEOUT_STATUS_BLOCKED = "v4_0_closeout_and_v4_1_readiness_blocked"
V4_0_CLOSEOUT_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_CLOSEOUT_SCOPE = "v4_0_closeout_and_v4_1_readiness_descriptive_only"

CLOSEOUT_STATUS_CLOSED_OUT = "closed_out"
CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS = "closed_out_with_warnings"
CLOSEOUT_STATUS_BLOCKED = "blocked"
CLOSEOUT_STATUS_UNKNOWN = "unknown"
CLOSEOUT_STATUS_PROHIBITED = "prohibited"
V4_CLOSEOUT_STATUSES: tuple[str, ...] = (
    CLOSEOUT_STATUS_CLOSED_OUT,
    CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS,
    CLOSEOUT_STATUS_BLOCKED,
    CLOSEOUT_STATUS_UNKNOWN,
    CLOSEOUT_STATUS_PROHIBITED,
)

V41_READINESS_READY = "ready_for_v4_1_planning"
V41_READINESS_READY_WITH_WARNINGS = "ready_for_v4_1_planning_with_warnings"
V41_READINESS_NOT_READY = "not_ready"
V41_READINESS_BLOCKED = "blocked"
V41_READINESS_UNKNOWN = "unknown"
V41_READINESS_PROHIBITED = "prohibited"
V41_READINESS_STATUSES: tuple[str, ...] = (
    V41_READINESS_READY,
    V41_READINESS_READY_WITH_WARNINGS,
    V41_READINESS_NOT_READY,
    V41_READINESS_BLOCKED,
    V41_READINESS_UNKNOWN,
    V41_READINESS_PROHIBITED,
)

CLOSEOUT_SEVERITY_INFO = "info"
CLOSEOUT_SEVERITY_WARNING = "warning"
CLOSEOUT_SEVERITY_BLOCKING = "blocking"
CLOSEOUT_SEVERITY_CRITICAL = "critical"
CLOSEOUT_SEVERITY_PROHIBITED = "prohibited"
CLOSEOUT_SEVERITY_UNKNOWN = "unknown"
V4_CLOSEOUT_SEVERITIES: tuple[str, ...] = (
    CLOSEOUT_SEVERITY_INFO,
    CLOSEOUT_SEVERITY_WARNING,
    CLOSEOUT_SEVERITY_BLOCKING,
    CLOSEOUT_SEVERITY_CRITICAL,
    CLOSEOUT_SEVERITY_PROHIBITED,
    CLOSEOUT_SEVERITY_UNKNOWN,
)

CLOSEOUT_FINDING_LIFECYCLE = "lifecycle_closeout_certification"
CLOSEOUT_FINDING_DRIFT = "drift_closeout_certification"
CLOSEOUT_FINDING_BUNDLE_GOVERNANCE = "bundle_governance_closeout_certification"
CLOSEOUT_FINDING_VALIDATION = "validation_closeout_certification"
CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION = "production_consumption_closeout_certification"
CLOSEOUT_FINDING_RECOVERY = "recovery_closeout_certification"
CLOSEOUT_FINDING_DIAGNOSTICS = "diagnostics_closeout_certification"
CLOSEOUT_FINDING_INTEGRITY = "integrity_closeout_certification"
CLOSEOUT_FINDING_CONTINUITY = "continuity_closeout_certification"
CLOSEOUT_FINDING_PROVENANCE = "provenance_closeout_certification"
CLOSEOUT_FINDING_LINEAGE = "lineage_closeout_certification"
CLOSEOUT_FINDING_REPLAY = "replay_closeout_certification"
CLOSEOUT_FINDING_ROLLBACK = "rollback_closeout_certification"
CLOSEOUT_FINDING_SERIALIZATION = "serialization_stability_certification"
CLOSEOUT_FINDING_HASHING = "hashing_stability_certification"
CLOSEOUT_FINDING_VISIBILITY = "visibility_preservation_certification"
CLOSEOUT_FINDING_NON_EXECUTION = "non_execution_certification"
CLOSEOUT_FINDING_NON_REMEDIATION = "non_remediation_certification"
CLOSEOUT_FINDING_NON_AUTHORIZATION = "non_authorization_certification"
CLOSEOUT_FINDING_PRODUCTION_DISABLED = "production_consumption_disabled_certification"
CLOSEOUT_FINDING_ORCHESTRATION_DISABLED = "orchestration_disabled_certification"
CLOSEOUT_FINDING_PLANNER_DISABLED = "planner_integration_disabled_certification"
CLOSEOUT_FINDING_V41_READINESS = "v4_1_readiness_certification"
CLOSEOUT_FINDING_PROHIBITED_VISIBILITY = "prohibited_state_visibility"
CLOSEOUT_FINDING_UNKNOWN_VISIBILITY = "unknown_state_visibility"
CLOSEOUT_FINDING_WARNING_VISIBILITY = "warning_visibility"
V4_CLOSEOUT_FINDING_TYPES: tuple[str, ...] = (
    CLOSEOUT_FINDING_LIFECYCLE,
    CLOSEOUT_FINDING_DRIFT,
    CLOSEOUT_FINDING_BUNDLE_GOVERNANCE,
    CLOSEOUT_FINDING_VALIDATION,
    CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION,
    CLOSEOUT_FINDING_RECOVERY,
    CLOSEOUT_FINDING_DIAGNOSTICS,
    CLOSEOUT_FINDING_INTEGRITY,
    CLOSEOUT_FINDING_CONTINUITY,
    CLOSEOUT_FINDING_PROVENANCE,
    CLOSEOUT_FINDING_LINEAGE,
    CLOSEOUT_FINDING_REPLAY,
    CLOSEOUT_FINDING_ROLLBACK,
    CLOSEOUT_FINDING_SERIALIZATION,
    CLOSEOUT_FINDING_HASHING,
    CLOSEOUT_FINDING_VISIBILITY,
    CLOSEOUT_FINDING_NON_EXECUTION,
    CLOSEOUT_FINDING_NON_REMEDIATION,
    CLOSEOUT_FINDING_NON_AUTHORIZATION,
    CLOSEOUT_FINDING_PRODUCTION_DISABLED,
    CLOSEOUT_FINDING_ORCHESTRATION_DISABLED,
    CLOSEOUT_FINDING_PLANNER_DISABLED,
    CLOSEOUT_FINDING_V41_READINESS,
    CLOSEOUT_FINDING_PROHIBITED_VISIBILITY,
    CLOSEOUT_FINDING_UNKNOWN_VISIBILITY,
    CLOSEOUT_FINDING_WARNING_VISIBILITY,
)


def _as_tuple(values: Iterable["V4CloseoutFinding"] | tuple["V4CloseoutFinding", ...] | None) -> tuple["V4CloseoutFinding", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class V4CloseoutStatus:
    status: str
    description: str
    descriptive_only: bool = True
    execution_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    production_consumption_semantics_enabled: bool = False


@dataclass(frozen=True)
class V41ReadinessStatus:
    status: str
    description: str
    planning_only: bool = True
    execution_readiness_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    production_consumption_semantics_enabled: bool = False


@dataclass(frozen=True)
class V4CloseoutFinding:
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
    continuity_reference: str
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
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class V4CloseoutReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_report_hash: str
    production_consumption_report_hash: str
    recovery_report_hash: str
    diagnostics_report_hash: str
    integrity_report_hash: str
    continuity_report_hash: str
    closeout_status: str
    v4_1_readiness_status: str
    finding_count: int
    findings: tuple[V4CloseoutFinding, ...]
    warning_count: int
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
    continuity_preserved: bool
    execution_authorized: bool
    remediation_authorized: bool
    production_consumption_enabled: bool
    orchestration_enabled: bool
    planner_integration_enabled: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_CLOSEOUT_SCHEMA_VERSION
    phase_id: str = V4_0_CLOSEOUT_PHASE_ID
    closeout_scope: str = V4_0_CLOSEOUT_SCOPE
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    execution_enabled: bool = False
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
        object.__setattr__(self, "orchestration_enabled", False)
        object.__setattr__(self, "planner_integration_enabled", False)


SUPPORTED_V4_CLOSEOUT_STATUS_MODELS: tuple[V4CloseoutStatus, ...] = (
    V4CloseoutStatus(CLOSEOUT_STATUS_CLOSED_OUT, "v4.0 closeout evidence is preserved"),
    V4CloseoutStatus(CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS, "v4.0 closeout evidence includes visible warnings"),
    V4CloseoutStatus(CLOSEOUT_STATUS_BLOCKED, "v4.0 closeout evidence exposes blockers"),
    V4CloseoutStatus(CLOSEOUT_STATUS_UNKNOWN, "v4.0 closeout evidence exposes unknown state"),
    V4CloseoutStatus(CLOSEOUT_STATUS_PROHIBITED, "v4.0 closeout evidence exposes prohibited state"),
)

SUPPORTED_V41_READINESS_STATUS_MODELS: tuple[V41ReadinessStatus, ...] = (
    V41ReadinessStatus(V41_READINESS_READY, "governance evidence is stable for v4.1 planning only"),
    V41ReadinessStatus(V41_READINESS_READY_WITH_WARNINGS, "governance evidence is stable for v4.1 planning with warnings"),
    V41ReadinessStatus(V41_READINESS_NOT_READY, "governance evidence is not ready for v4.1 planning"),
    V41ReadinessStatus(V41_READINESS_BLOCKED, "governance evidence exposes planning blockers"),
    V41ReadinessStatus(V41_READINESS_UNKNOWN, "governance evidence exposes unknown planning state"),
    V41ReadinessStatus(V41_READINESS_PROHIBITED, "governance evidence exposes prohibited planning state"),
)
