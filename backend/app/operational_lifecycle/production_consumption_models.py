"""Deterministic controlled production consumption governance models.

Production consumption governance is descriptive evidence only. It does not
authorize production consumption, enable production consumption, change planner
behavior, approve bundles, execute refreshes, repair blockers, or mutate
runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_PHASE_ID = "v4_0_controlled_production_consumption_governance"
V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_SCHEMA_VERSION = "v4_0.controlled_production_consumption_governance.1"
V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_STABLE = "v4_0_controlled_production_consumption_governance_stable"
V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_BLOCKED = "v4_0_controlled_production_consumption_governance_blocked"
V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_SCOPE = "controlled_production_consumption_governance_descriptive_only"

PRODUCTION_CONSUMPTION_GATE_STATE_VISIBLE = "visible"
PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED = "satisfied"
PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED = "not_satisfied"
PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED = "blocked"
PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED = "unsupported"
PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN = "unknown"
PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED = "prohibited"
PRODUCTION_CONSUMPTION_GATE_STATES: tuple[str, ...] = (
    PRODUCTION_CONSUMPTION_GATE_STATE_VISIBLE,
    PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN,
    PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED,
)

PRODUCTION_CONSUMPTION_SEVERITY_INFO = "info"
PRODUCTION_CONSUMPTION_SEVERITY_WARNING = "warning"
PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING = "blocking"
PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL = "critical"
PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED = "prohibited"
PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN = "unknown"
PRODUCTION_CONSUMPTION_SEVERITIES: tuple[str, ...] = (
    PRODUCTION_CONSUMPTION_SEVERITY_INFO,
    PRODUCTION_CONSUMPTION_SEVERITY_WARNING,
    PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING,
    PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL,
    PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED,
    PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN,
)

PRODUCTION_CONSUMPTION_GATE_LIFECYCLE_EVIDENCE = "lifecycle_evidence_gate"
PRODUCTION_CONSUMPTION_GATE_DRIFT_EVIDENCE = "drift_evidence_gate"
PRODUCTION_CONSUMPTION_GATE_BUNDLE_GOVERNANCE = "bundle_governance_gate"
PRODUCTION_CONSUMPTION_GATE_OPERATIONAL_VALIDATION = "operational_validation_gate"
PRODUCTION_CONSUMPTION_GATE_PROVENANCE_CONTINUITY = "provenance_continuity_gate"
PRODUCTION_CONSUMPTION_GATE_LINEAGE_CONTINUITY = "lineage_continuity_gate"
PRODUCTION_CONSUMPTION_GATE_REPLAY_CONTINUITY = "replay_continuity_gate"
PRODUCTION_CONSUMPTION_GATE_ROLLBACK_CONTINUITY = "rollback_continuity_gate"
PRODUCTION_CONSUMPTION_GATE_UNSUPPORTED_STATE = "unsupported_state_gate"
PRODUCTION_CONSUMPTION_GATE_PROHIBITED_STATE = "prohibited_state_gate"
PRODUCTION_CONSUMPTION_GATE_BLOCKED_STATE = "blocked_state_gate"
PRODUCTION_CONSUMPTION_GATE_UNKNOWN_STATE = "unknown_state_gate"
PRODUCTION_CONSUMPTION_GATE_INTEGRITY_WARNING = "integrity_warning_gate"
PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION = "production_consumption_prohibition_gate"
PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS = "production_consumption_readiness_gate"
PRODUCTION_CONSUMPTION_GATE_TYPES: tuple[str, ...] = (
    PRODUCTION_CONSUMPTION_GATE_LIFECYCLE_EVIDENCE,
    PRODUCTION_CONSUMPTION_GATE_DRIFT_EVIDENCE,
    PRODUCTION_CONSUMPTION_GATE_BUNDLE_GOVERNANCE,
    PRODUCTION_CONSUMPTION_GATE_OPERATIONAL_VALIDATION,
    PRODUCTION_CONSUMPTION_GATE_PROVENANCE_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_LINEAGE_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_REPLAY_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_ROLLBACK_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_UNSUPPORTED_STATE,
    PRODUCTION_CONSUMPTION_GATE_PROHIBITED_STATE,
    PRODUCTION_CONSUMPTION_GATE_BLOCKED_STATE,
    PRODUCTION_CONSUMPTION_GATE_UNKNOWN_STATE,
    PRODUCTION_CONSUMPTION_GATE_INTEGRITY_WARNING,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS,
)


def _as_tuple(
    values: Iterable["ProductionConsumptionGate"] | tuple["ProductionConsumptionGate", ...] | None,
) -> tuple["ProductionConsumptionGate", ...]:
    return tuple(values or ())


@dataclass(frozen=True)
class ProductionConsumptionGateState:
    state: str
    description: str
    descriptive_only: bool = True
    approval_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    production_enablement_semantics_enabled: bool = False
    planner_behavior_semantics_enabled: bool = False


@dataclass(frozen=True)
class ProductionConsumptionSeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    approval_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class ProductionConsumptionGate:
    gate_type: str
    gate_state: str
    severity: str
    lifecycle_reference: str
    drift_reference: str
    governance_reference: str
    validation_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_reference: str
    rollback_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    production_consumption_authorized: bool = False
    production_consumption_enabled: bool = False
    production_bundle_consumption_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_behavior_changed: bool = False
    remediation_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class ProductionConsumptionGovernanceReport:
    lifecycle_identity: str
    drift_report_hash: str
    governance_report_hash: str
    validation_report_hash: str
    gate_count: int
    gates: tuple[ProductionConsumptionGate, ...]
    satisfied_gate_count: int
    blocked_gate_count: int
    unsupported_gate_count: int
    prohibited_gate_count: int
    unknown_gate_count: int
    warning_count: int
    critical_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    production_consumption_authorized: bool
    production_consumption_enabled: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_SCHEMA_VERSION
    phase_id: str = V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_PHASE_ID
    governance_scope: str = V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_SCOPE
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
    production_bundle_consumption_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_behavior_changed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "gates", _as_tuple(self.gates))
        object.__setattr__(self, "production_consumption_authorized", False)
        object.__setattr__(self, "production_consumption_enabled", False)
        object.__setattr__(self, "production_bundle_consumption_enabled", False)
        object.__setattr__(self, "planner_integration_enabled", False)
        object.__setattr__(self, "planner_behavior_changed", False)


SUPPORTED_PRODUCTION_CONSUMPTION_GATE_STATE_MODELS: tuple[ProductionConsumptionGateState, ...] = (
    ProductionConsumptionGateState(PRODUCTION_CONSUMPTION_GATE_STATE_VISIBLE, "gate evidence is visible"),
    ProductionConsumptionGateState(
        PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
        "gate evidence is present and internally consistent without approval or enablement semantics",
    ),
    ProductionConsumptionGateState(
        PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED,
        "gate evidence is visible but not internally sufficient for readiness",
    ),
    ProductionConsumptionGateState(PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED, "gate evidence exposes blockers"),
    ProductionConsumptionGateState(PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED, "gate evidence exposes unsupported states"),
    ProductionConsumptionGateState(PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN, "gate evidence exposes unknown states"),
    ProductionConsumptionGateState(PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED, "gate evidence exposes prohibited states"),
)

SUPPORTED_PRODUCTION_CONSUMPTION_SEVERITY_MODELS: tuple[ProductionConsumptionSeverity, ...] = (
    ProductionConsumptionSeverity(PRODUCTION_CONSUMPTION_SEVERITY_INFO, "descriptive informational gate evidence"),
    ProductionConsumptionSeverity(PRODUCTION_CONSUMPTION_SEVERITY_WARNING, "descriptive warning gate evidence"),
    ProductionConsumptionSeverity(PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING, "descriptive blocking gate evidence"),
    ProductionConsumptionSeverity(PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL, "descriptive critical gate evidence"),
    ProductionConsumptionSeverity(PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED, "descriptive prohibited gate evidence"),
    ProductionConsumptionSeverity(PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN, "descriptive unknown gate evidence"),
)
