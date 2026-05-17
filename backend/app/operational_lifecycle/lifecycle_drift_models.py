"""Deterministic v4.0 patch lifecycle drift models.

Drift models are descriptive evidence only. Severity does not authorize,
select, remediate, correct, migrate, refresh, schedule, route, dispatch,
or execute lifecycle behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


V4_0_PATCH_LIFECYCLE_DRIFT_PHASE_ID = "v4_0_patch_lifecycle_drift_foundations"
V4_0_PATCH_LIFECYCLE_DRIFT_SCHEMA_VERSION = "v4_0.patch_lifecycle_drift_foundations.1"
V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_STABLE = "v4_0_patch_lifecycle_drift_foundation_stable"
V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_BLOCKED = "v4_0_patch_lifecycle_drift_foundation_blocked"
V4_0_PATCH_LIFECYCLE_DRIFT_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_PATCH_LIFECYCLE_DRIFT_SCOPE = "deterministic_lifecycle_drift_detection_descriptive_only"

DRIFT_TYPE_IDENTITY = "identity_drift"
DRIFT_TYPE_PATCH_VERSION = "patch_version_drift"
DRIFT_TYPE_EXTRACTION_VERSION = "extraction_version_drift"
DRIFT_TYPE_SCHEMA_VERSION = "schema_version_drift"
DRIFT_TYPE_GENERATION = "generation_drift"
DRIFT_TYPE_PROVENANCE = "provenance_drift"
DRIFT_TYPE_LINEAGE = "lineage_drift"
DRIFT_TYPE_STATE = "state_drift"
DRIFT_TYPE_VISIBILITY = "visibility_drift"
DRIFT_TYPE_REPLAY_CONTINUITY = "replay_continuity_drift"
DRIFT_TYPE_ROLLBACK_CONTINUITY = "rollback_continuity_drift"
DRIFT_TYPE_INTEGRITY_WARNING = "integrity_warning_drift"
DRIFT_TYPE_UNKNOWN = "unknown_drift"
LIFECYCLE_DRIFT_TYPES: tuple[str, ...] = (
    DRIFT_TYPE_IDENTITY,
    DRIFT_TYPE_PATCH_VERSION,
    DRIFT_TYPE_EXTRACTION_VERSION,
    DRIFT_TYPE_SCHEMA_VERSION,
    DRIFT_TYPE_GENERATION,
    DRIFT_TYPE_PROVENANCE,
    DRIFT_TYPE_LINEAGE,
    DRIFT_TYPE_STATE,
    DRIFT_TYPE_VISIBILITY,
    DRIFT_TYPE_REPLAY_CONTINUITY,
    DRIFT_TYPE_ROLLBACK_CONTINUITY,
    DRIFT_TYPE_INTEGRITY_WARNING,
    DRIFT_TYPE_UNKNOWN,
)

DRIFT_SEVERITY_INFO = "info"
DRIFT_SEVERITY_WARNING = "warning"
DRIFT_SEVERITY_BLOCKING = "blocking"
DRIFT_SEVERITY_PROHIBITED = "prohibited"
DRIFT_SEVERITY_UNKNOWN = "unknown"
LIFECYCLE_DRIFT_SEVERITIES: tuple[str, ...] = (
    DRIFT_SEVERITY_INFO,
    DRIFT_SEVERITY_WARNING,
    DRIFT_SEVERITY_BLOCKING,
    DRIFT_SEVERITY_PROHIBITED,
    DRIFT_SEVERITY_UNKNOWN,
)


def _as_tuple(values: Iterable["LifecycleDriftFinding"] | tuple["LifecycleDriftFinding", ...] | None) -> tuple[
    "LifecycleDriftFinding",
    ...
]:
    return tuple(values or ())


@dataclass(frozen=True)
class LifecycleDriftType:
    drift_type: str
    description: str
    descriptive_only: bool = True
    execution_enabled: bool = False
    remediation_enabled: bool = False


@dataclass(frozen=True)
class LifecycleDriftSeverity:
    severity: str
    description: str
    descriptive_only: bool = True
    authorization_semantics_enabled: bool = False
    selection_semantics_enabled: bool = False
    remediation_semantics_enabled: bool = False
    execution_semantics_enabled: bool = False


@dataclass(frozen=True)
class LifecycleDriftFinding:
    drift_type: str
    severity: str
    before_value: Any
    after_value: Any
    provenance_reference: str
    lineage_reference: str
    visibility_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    remediation_enabled: bool = False
    correction_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class LifecycleDriftReport:
    source_lifecycle_identity: str
    target_lifecycle_identity: str
    finding_count: int
    findings: tuple[LifecycleDriftFinding, ...]
    unsupported_drift_count: int
    prohibited_drift_count: int
    unknown_drift_count: int
    blocking_drift_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_PATCH_LIFECYCLE_DRIFT_SCHEMA_VERSION
    phase_id: str = V4_0_PATCH_LIFECYCLE_DRIFT_PHASE_ID
    drift_scope: str = V4_0_PATCH_LIFECYCLE_DRIFT_SCOPE
    descriptive_only: bool = True
    remediation_enabled: bool = False
    correction_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    callable_operational_workflow_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "findings", _as_tuple(self.findings))


SUPPORTED_LIFECYCLE_DRIFT_TYPE_MODELS: tuple[LifecycleDriftType, ...] = (
    LifecycleDriftType(DRIFT_TYPE_IDENTITY, "source and target lifecycle identity differ"),
    LifecycleDriftType(DRIFT_TYPE_PATCH_VERSION, "patch version changed"),
    LifecycleDriftType(DRIFT_TYPE_EXTRACTION_VERSION, "extraction version changed"),
    LifecycleDriftType(DRIFT_TYPE_SCHEMA_VERSION, "schema version changed"),
    LifecycleDriftType(DRIFT_TYPE_GENERATION, "lifecycle generation changed"),
    LifecycleDriftType(DRIFT_TYPE_PROVENANCE, "provenance reference or record changed"),
    LifecycleDriftType(DRIFT_TYPE_LINEAGE, "lineage reference or record changed"),
    LifecycleDriftType(DRIFT_TYPE_STATE, "lifecycle state visibility changed"),
    LifecycleDriftType(DRIFT_TYPE_VISIBILITY, "visibility record changed"),
    LifecycleDriftType(DRIFT_TYPE_REPLAY_CONTINUITY, "replay continuity references changed"),
    LifecycleDriftType(DRIFT_TYPE_ROLLBACK_CONTINUITY, "rollback continuity references changed"),
    LifecycleDriftType(DRIFT_TYPE_INTEGRITY_WARNING, "integrity warning visibility changed"),
    LifecycleDriftType(DRIFT_TYPE_UNKNOWN, "unclassified lifecycle drift remains visible"),
)

SUPPORTED_LIFECYCLE_DRIFT_SEVERITY_MODELS: tuple[LifecycleDriftSeverity, ...] = (
    LifecycleDriftSeverity(DRIFT_SEVERITY_INFO, "descriptive informational drift"),
    LifecycleDriftSeverity(DRIFT_SEVERITY_WARNING, "descriptive warning drift"),
    LifecycleDriftSeverity(DRIFT_SEVERITY_BLOCKING, "descriptive blocking drift"),
    LifecycleDriftSeverity(DRIFT_SEVERITY_PROHIBITED, "descriptive prohibited drift"),
    LifecycleDriftSeverity(DRIFT_SEVERITY_UNKNOWN, "descriptive unknown drift"),
)
