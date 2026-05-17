"""Deterministic trusted bundle lifecycle governance models.

Trusted bundle governance is descriptive evidence only. It does not approve,
authorize, consume, deploy, remediate, execute, route, schedule, dispatch,
or mutate trusted bundles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_TRUSTED_BUNDLE_GOVERNANCE_PHASE_ID = "v4_0_trusted_bundle_lifecycle_governance"
V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCHEMA_VERSION = "v4_0.trusted_bundle_lifecycle_governance.1"
V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_STABLE = "v4_0_trusted_bundle_lifecycle_governance_stable"
V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_BLOCKED = "v4_0_trusted_bundle_lifecycle_governance_blocked"
V4_0_TRUSTED_BUNDLE_GOVERNANCE_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCOPE = "trusted_bundle_lifecycle_governance_descriptive_only"

BUNDLE_TRUST_STATUS_TRUSTED = "trusted"
BUNDLE_TRUST_STATUS_UNTRUSTED = "untrusted"
BUNDLE_TRUST_STATUS_EXPERIMENTAL = "experimental"
BUNDLE_TRUST_STATUS_UNSUPPORTED = "unsupported"
BUNDLE_TRUST_STATUS_BLOCKED = "blocked"
BUNDLE_TRUST_STATUS_UNKNOWN = "unknown"
BUNDLE_TRUST_STATUS_PROHIBITED = "prohibited"
TRUSTED_BUNDLE_STATUSES: tuple[str, ...] = (
    BUNDLE_TRUST_STATUS_TRUSTED,
    BUNDLE_TRUST_STATUS_UNTRUSTED,
    BUNDLE_TRUST_STATUS_EXPERIMENTAL,
    BUNDLE_TRUST_STATUS_UNSUPPORTED,
    BUNDLE_TRUST_STATUS_BLOCKED,
    BUNDLE_TRUST_STATUS_UNKNOWN,
    BUNDLE_TRUST_STATUS_PROHIBITED,
)

BUNDLE_VALIDATION_STATUS_VALID = "valid"
BUNDLE_VALIDATION_STATUS_INVALID = "invalid"
BUNDLE_VALIDATION_STATUS_PARTIAL = "partial"
BUNDLE_VALIDATION_STATUS_MISSING = "missing"
BUNDLE_VALIDATION_STATUS_STALE = "stale"
BUNDLE_VALIDATION_STATUS_UNKNOWN = "unknown"
BUNDLE_VALIDATION_STATUS_BLOCKED = "blocked"
BUNDLE_VALIDATION_STATUS_PROHIBITED = "prohibited"
TRUSTED_BUNDLE_VALIDATION_STATUSES: tuple[str, ...] = (
    BUNDLE_VALIDATION_STATUS_VALID,
    BUNDLE_VALIDATION_STATUS_INVALID,
    BUNDLE_VALIDATION_STATUS_PARTIAL,
    BUNDLE_VALIDATION_STATUS_MISSING,
    BUNDLE_VALIDATION_STATUS_STALE,
    BUNDLE_VALIDATION_STATUS_UNKNOWN,
    BUNDLE_VALIDATION_STATUS_BLOCKED,
    BUNDLE_VALIDATION_STATUS_PROHIBITED,
)

BUNDLE_SUPPORT_STATUS_SUPPORTED = "supported"
BUNDLE_SUPPORT_STATUS_PARTIALLY_SUPPORTED = "partially_supported"
BUNDLE_SUPPORT_STATUS_UNSUPPORTED = "unsupported"
BUNDLE_SUPPORT_STATUS_EXPERIMENTAL = "experimental"
BUNDLE_SUPPORT_STATUS_UNKNOWN = "unknown"
BUNDLE_SUPPORT_STATUS_BLOCKED = "blocked"
BUNDLE_SUPPORT_STATUS_PROHIBITED = "prohibited"
TRUSTED_BUNDLE_SUPPORT_STATUSES: tuple[str, ...] = (
    BUNDLE_SUPPORT_STATUS_SUPPORTED,
    BUNDLE_SUPPORT_STATUS_PARTIALLY_SUPPORTED,
    BUNDLE_SUPPORT_STATUS_UNSUPPORTED,
    BUNDLE_SUPPORT_STATUS_EXPERIMENTAL,
    BUNDLE_SUPPORT_STATUS_UNKNOWN,
    BUNDLE_SUPPORT_STATUS_BLOCKED,
    BUNDLE_SUPPORT_STATUS_PROHIBITED,
)

GOVERNANCE_FINDING_BUNDLE_IDENTITY_VISIBILITY = "bundle_identity_visibility"
GOVERNANCE_FINDING_BUNDLE_METADATA_VISIBILITY = "bundle_metadata_visibility"
GOVERNANCE_FINDING_TRUST_STATUS_VISIBILITY = "trust_status_visibility"
GOVERNANCE_FINDING_VALIDATION_STATUS_VISIBILITY = "validation_status_visibility"
GOVERNANCE_FINDING_SUPPORT_STATUS_VISIBILITY = "support_status_visibility"
GOVERNANCE_FINDING_BLOCKED_DOMAIN_VISIBILITY = "blocked_domain_visibility"
GOVERNANCE_FINDING_LIFECYCLE_ALIGNMENT_VISIBILITY = "lifecycle_alignment_visibility"
GOVERNANCE_FINDING_DRIFT_ALIGNMENT_VISIBILITY = "drift_alignment_visibility"
GOVERNANCE_FINDING_PROVENANCE_CONTINUITY_VISIBILITY = "provenance_continuity_visibility"
GOVERNANCE_FINDING_LINEAGE_CONTINUITY_VISIBILITY = "lineage_continuity_visibility"
GOVERNANCE_FINDING_REPLAY_CONTINUITY_VISIBILITY = "replay_continuity_visibility"
GOVERNANCE_FINDING_ROLLBACK_CONTINUITY_VISIBILITY = "rollback_continuity_visibility"
GOVERNANCE_FINDING_INTEGRITY_WARNING_VISIBILITY = "integrity_warning_visibility"
GOVERNANCE_FINDING_PRODUCTION_CONSUMPTION_PROHIBITED = "production_consumption_prohibited"
GOVERNANCE_FINDING_UNKNOWN_GOVERNANCE_STATE = "unknown_governance_state"
TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES: tuple[str, ...] = (
    GOVERNANCE_FINDING_BUNDLE_IDENTITY_VISIBILITY,
    GOVERNANCE_FINDING_BUNDLE_METADATA_VISIBILITY,
    GOVERNANCE_FINDING_TRUST_STATUS_VISIBILITY,
    GOVERNANCE_FINDING_VALIDATION_STATUS_VISIBILITY,
    GOVERNANCE_FINDING_SUPPORT_STATUS_VISIBILITY,
    GOVERNANCE_FINDING_BLOCKED_DOMAIN_VISIBILITY,
    GOVERNANCE_FINDING_LIFECYCLE_ALIGNMENT_VISIBILITY,
    GOVERNANCE_FINDING_DRIFT_ALIGNMENT_VISIBILITY,
    GOVERNANCE_FINDING_PROVENANCE_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_LINEAGE_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_REPLAY_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_ROLLBACK_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_INTEGRITY_WARNING_VISIBILITY,
    GOVERNANCE_FINDING_PRODUCTION_CONSUMPTION_PROHIBITED,
    GOVERNANCE_FINDING_UNKNOWN_GOVERNANCE_STATE,
)

GOVERNANCE_SEVERITY_INFO = "info"
GOVERNANCE_SEVERITY_WARNING = "warning"
GOVERNANCE_SEVERITY_BLOCKING = "blocking"
GOVERNANCE_SEVERITY_PROHIBITED = "prohibited"
GOVERNANCE_SEVERITY_UNKNOWN = "unknown"
TRUSTED_BUNDLE_GOVERNANCE_SEVERITIES: tuple[str, ...] = (
    GOVERNANCE_SEVERITY_INFO,
    GOVERNANCE_SEVERITY_WARNING,
    GOVERNANCE_SEVERITY_BLOCKING,
    GOVERNANCE_SEVERITY_PROHIBITED,
    GOVERNANCE_SEVERITY_UNKNOWN,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TrustedBundleIdentity:
    bundle_id: str
    patch_version: str
    extraction_version: str
    schema_version: str
    generated_timestamp: str
    bundle_hash: str
    manifest_hash: str
    metadata_hash: str
    identity_scope: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCOPE
    descriptive_only: bool = True
    production_consumption_authorized: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class TrustedBundleStatus:
    status: str
    status_reference: str
    explanation: str
    status_scope: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCOPE
    descriptive_only: bool = True
    approval_semantics_enabled: bool = False
    authorization_semantics_enabled: bool = False
    production_semantics_enabled: bool = False
    silent_trust_upgrade_enabled: bool = False


@dataclass(frozen=True)
class TrustedBundleValidationStatus:
    status: str
    status_reference: str
    explanation: str
    validation_scope: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCOPE
    descriptive_only: bool = True
    automatic_validation_enabled: bool = False
    automatic_validation_fix_enabled: bool = False
    approval_semantics_enabled: bool = False


@dataclass(frozen=True)
class TrustedBundleSupportStatus:
    status: str
    status_reference: str
    explanation: str
    support_scope: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCOPE
    descriptive_only: bool = True
    implicit_support_upgrade_enabled: bool = False
    approval_semantics_enabled: bool = False
    production_semantics_enabled: bool = False


@dataclass(frozen=True)
class TrustedBundleGovernanceFinding:
    finding_type: str
    severity: str
    bundle_reference: str
    lifecycle_reference: str
    drift_reference: str
    provenance_reference: str
    lineage_reference: str
    explanation: str
    deterministic_key: str
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    execution_enabled: bool = False
    production_consumption_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class TrustedBundleGovernanceReport:
    bundle_identity: TrustedBundleIdentity
    lifecycle_identity: str
    drift_report_hash: str
    trust_status: str
    validation_status: str
    support_status: str
    blocked_domains: tuple[str, ...]
    finding_count: int
    findings: tuple[TrustedBundleGovernanceFinding, ...]
    unsupported_count: int
    prohibited_count: int
    blocked_count: int
    unknown_count: int
    warning_count: int
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    production_consumption_authorized: bool
    deterministic_report_hash: str
    schema_version: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCHEMA_VERSION
    phase_id: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_PHASE_ID
    governance_scope: str = V4_0_TRUSTED_BUNDLE_GOVERNANCE_SCOPE
    descriptive_only: bool = True
    approval_enabled: bool = False
    authorization_enabled: bool = False
    remediation_enabled: bool = False
    execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    production_bundle_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "blocked_domains")
        object.__setattr__(self, "findings", tuple(self.findings or ()))
        object.__setattr__(self, "production_consumption_authorized", False)
