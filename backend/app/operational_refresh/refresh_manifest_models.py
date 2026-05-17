"""Deterministic v4.1 refresh manifest foundation models.

Refresh manifests are descriptive governance evidence only. They do not
execute refreshes, orchestrate work, migrate data, consume production bundles,
integrate with planners, authorize behavior, remediate blockers, recover state,
roll back state, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_MANIFEST_PHASE_ID = "v4_1_refresh_manifest_foundations"
V4_1_REFRESH_MANIFEST_SCHEMA_VERSION = "v4_1.refresh_manifest_foundations.1"
V4_1_REFRESH_MANIFEST_REPORT_SCHEMA_VERSION = "v4_1.refresh_manifest_foundations_report.1"
V4_1_REFRESH_MANIFEST_DIAGNOSTICS_SCHEMA_VERSION = "v4_1.refresh_manifest_diagnostics_report.1"
V4_1_REFRESH_MANIFEST_STATUS_STABLE = "v4_1_refresh_manifest_foundation_stable"
V4_1_REFRESH_MANIFEST_STATUS_BLOCKED = "v4_1_refresh_manifest_foundation_blocked"
V4_1_REFRESH_MANIFEST_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_MANIFEST_PURPOSE = "deterministic_operational_refresh_governance_intelligence_only"

REFRESH_MANIFEST_IDENTITY_SCOPE = "refresh_manifest_identity_descriptive_only"
REFRESH_MANIFEST_SOURCE_LINEAGE_SCOPE = "refresh_manifest_source_lineage_descriptive_only"
REFRESH_MANIFEST_EXTRACTION_LINEAGE_SCOPE = "refresh_manifest_extraction_lineage_descriptive_only"
REFRESH_MANIFEST_PATCH_LINEAGE_SCOPE = "refresh_manifest_patch_lineage_descriptive_only"
REFRESH_MANIFEST_SCHEMA_VISIBILITY_SCOPE = "refresh_manifest_schema_version_visibility_descriptive_only"
REFRESH_MANIFEST_DEPENDENCY_VISIBILITY_SCOPE = "refresh_manifest_dependency_visibility_descriptive_only"
REFRESH_MANIFEST_TRUST_VISIBILITY_SCOPE = "refresh_manifest_trust_visibility_descriptive_only"
REFRESH_MANIFEST_VALIDATION_VISIBILITY_SCOPE = "refresh_manifest_validation_visibility_descriptive_only"
REFRESH_MANIFEST_PROHIBITED_DOMAIN_SCOPE = "refresh_manifest_prohibited_domain_visibility_descriptive_only"
REFRESH_MANIFEST_UNSUPPORTED_STATE_SCOPE = "refresh_manifest_unsupported_state_visibility_descriptive_only"
REFRESH_MANIFEST_CONTINUITY_SCOPE = "refresh_manifest_continuity_metadata_descriptive_only"
REFRESH_MANIFEST_REPLAY_SCOPE = "refresh_manifest_replay_metadata_descriptive_only"
REFRESH_MANIFEST_ROLLBACK_SCOPE = "refresh_manifest_rollback_metadata_descriptive_only"
REFRESH_MANIFEST_DIAGNOSTICS_SCOPE = "refresh_manifest_diagnostics_visibility_descriptive_only"
REFRESH_MANIFEST_GOVERNANCE_SCOPE = "refresh_manifest_governance_visibility_descriptive_only"

REFRESH_MANIFEST_STATE_SUPPORTED = "supported"
REFRESH_MANIFEST_STATE_UNSUPPORTED = "unsupported"
REFRESH_MANIFEST_STATE_BLOCKED = "blocked"
REFRESH_MANIFEST_STATE_UNKNOWN = "unknown"
REFRESH_MANIFEST_STATE_PROHIBITED = "prohibited"
REFRESH_MANIFEST_STATE_STALE = "stale"
REFRESH_MANIFEST_STATES: tuple[str, ...] = (
    REFRESH_MANIFEST_STATE_SUPPORTED,
    REFRESH_MANIFEST_STATE_UNSUPPORTED,
    REFRESH_MANIFEST_STATE_BLOCKED,
    REFRESH_MANIFEST_STATE_UNKNOWN,
    REFRESH_MANIFEST_STATE_PROHIBITED,
    REFRESH_MANIFEST_STATE_STALE,
)
FAIL_VISIBLE_REFRESH_MANIFEST_STATES: tuple[str, ...] = (
    REFRESH_MANIFEST_STATE_UNSUPPORTED,
    REFRESH_MANIFEST_STATE_BLOCKED,
    REFRESH_MANIFEST_STATE_UNKNOWN,
    REFRESH_MANIFEST_STATE_PROHIBITED,
    REFRESH_MANIFEST_STATE_STALE,
)

REFRESH_MANIFEST_VISIBILITY_VISIBLE = "visible"
REFRESH_MANIFEST_VISIBILITY_FAIL_VISIBLE = "fail_visible"
REFRESH_MANIFEST_SEVERITY_INFO = "info"
REFRESH_MANIFEST_SEVERITY_WARNING = "warning"
REFRESH_MANIFEST_SEVERITY_BLOCKED = "blocked"
REFRESH_MANIFEST_SEVERITY_PROHIBITED = "prohibited"
REFRESH_MANIFEST_SEVERITY_UNKNOWN = "unknown"

PROHIBITED_REFRESH_DOMAINS: tuple[str, ...] = (
    "refresh_execution",
    "orchestration_execution",
    "deployment_execution",
    "automatic_refresh_behavior",
    "automatic_migration_behavior",
    "planner_integration",
    "production_bundle_consumption",
    "remediation_systems",
    "recommendation_ranking_scoring_selection",
    "authorization_approval_systems",
    "runtime_mutation",
    "automatic_rollback",
    "automatic_recovery",
    "hidden_operational_behavior",
)

EXPLICIT_REFRESH_MANIFEST_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 1 creates deterministic refresh manifest governance metadata only.",
    "v4.1 Phase 1 does not enable refresh execution.",
    "v4.1 Phase 1 does not enable orchestration.",
    "v4.1 Phase 1 does not enable deployment execution.",
    "v4.1 Phase 1 does not enable automatic refresh behavior.",
    "v4.1 Phase 1 does not enable automatic migration behavior.",
    "v4.1 Phase 1 does not enable planner integration.",
    "v4.1 Phase 1 does not enable production consumption.",
    "v4.1 Phase 1 does not enable remediation.",
    "v4.1 Phase 1 does not enable runtime mutation.",
)

EXPLICIT_REFRESH_MANIFEST_PROHIBITIONS: tuple[str, ...] = (
    "No execution behavior exists.",
    "No orchestration exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No remediation exists.",
    "No mutation behavior exists.",
    "No recommendation, ranking, scoring, or selection behavior exists.",
    "No approval or authorization behavior exists.",
    "No automatic rollback or automatic recovery behavior exists.",
    "No silent fallback behavior exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshManifestIdentity:
    manifest_id: str
    refresh_cycle_id: str
    manifest_version: str
    source_bundle_reference: str
    extraction_reference: str
    patch_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    lineage_reference: str
    trust_reference: str
    validation_reference: str
    diagnostics_reference: str
    governance_reference: str
    identity_scope: str = REFRESH_MANIFEST_IDENTITY_SCOPE
    governance_purpose: str = V4_1_REFRESH_MANIFEST_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshManifestState:
    state_id: str
    state: str
    reason: str
    provenance_reference: str
    lineage_reference: str
    visibility_reference: str
    deterministic_order: int
    visibility_status: str = REFRESH_MANIFEST_VISIBILITY_VISIBLE
    severity: str = REFRESH_MANIFEST_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    executable: bool = False
    automatic_resolution_enabled: bool = False
    silent_fallback_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class RefreshManifestSourceLineage:
    source_lineage_id: str
    source_system_reference: str
    source_bundle_reference: str
    source_evidence_references: tuple[str, ...]
    prior_manifest_references: tuple[str, ...]
    unsupported_source_visibility: tuple[str, ...]
    provenance_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    source_lineage_scope: str = REFRESH_MANIFEST_SOURCE_LINEAGE_SCOPE
    source_lineage_preserved: bool = True
    provenance_preserved: bool = True
    inferred_source_allowed: bool = False
    fail_visible: bool = True
    descriptive_only: bool = True
    execution_enabled: bool = False
    automatic_source_refresh_enabled: bool = False
    hidden_source_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_evidence_references",
            "prior_manifest_references",
            "unsupported_source_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestExtractionLineage:
    extraction_lineage_id: str
    extractor_reference: str
    extraction_snapshot_reference: str
    extraction_evidence_references: tuple[str, ...]
    unsupported_extraction_states: tuple[str, ...]
    provenance_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    extraction_lineage_scope: str = REFRESH_MANIFEST_EXTRACTION_LINEAGE_SCOPE
    extraction_lineage_preserved: bool = True
    no_implicit_extraction: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    extraction_execution_enabled: bool = False
    automatic_extraction_enabled: bool = False
    hidden_extraction_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("extraction_evidence_references", "unsupported_extraction_states"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestPatchLineage:
    patch_lineage_id: str
    patch_reference: str
    patch_evidence_references: tuple[str, ...]
    prior_patch_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    provenance_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    patch_lineage_scope: str = REFRESH_MANIFEST_PATCH_LINEAGE_SCOPE
    patch_lineage_preserved: bool = True
    rollback_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    patch_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    hidden_patch_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("patch_evidence_references", "prior_patch_references", "rollback_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestSchemaVersionVisibility:
    schema_visibility_id: str
    manifest_schema_version: str
    source_schema_version: str
    extraction_schema_version: str
    patch_schema_version: str
    visible_schema_constraints: tuple[str, ...]
    unsupported_schema_versions: tuple[str, ...]
    deterministic_order: int
    schema_visibility_scope: str = REFRESH_MANIFEST_SCHEMA_VISIBILITY_SCOPE
    schema_version_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    schema_migration_enabled: bool = False
    hidden_schema_inference_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("visible_schema_constraints", "unsupported_schema_versions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestDependencyVisibility:
    dependency_visibility_id: str
    dependency_references: tuple[str, ...]
    missing_dependency_visibility: tuple[str, ...]
    stale_dependency_visibility: tuple[str, ...]
    prohibited_dependency_visibility: tuple[str, ...]
    deterministic_order: int
    dependency_visibility_scope: str = REFRESH_MANIFEST_DEPENDENCY_VISIBILITY_SCOPE
    dependencies_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_dependency_refresh_enabled: bool = False
    hidden_dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "dependency_references",
            "missing_dependency_visibility",
            "stale_dependency_visibility",
            "prohibited_dependency_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestTrustVisibility:
    trust_visibility_id: str
    trusted_source_references: tuple[str, ...]
    untrusted_source_visibility: tuple[str, ...]
    ambiguous_trust_visibility: tuple[str, ...]
    deterministic_order: int
    trust_visibility_scope: str = REFRESH_MANIFEST_TRUST_VISIBILITY_SCOPE
    trust_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    trust_inference_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("trusted_source_references", "untrusted_source_visibility", "ambiguous_trust_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestValidationVisibility:
    validation_visibility_id: str
    validation_references: tuple[str, ...]
    validation_warning_visibility: tuple[str, ...]
    validation_blocker_visibility: tuple[str, ...]
    unsupported_validation_visibility: tuple[str, ...]
    deterministic_order: int
    validation_visibility_scope: str = REFRESH_MANIFEST_VALIDATION_VISIBILITY_SCOPE
    validation_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_validation_execution_enabled: bool = False
    remediation_enabled: bool = False
    silent_validation_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "validation_references",
            "validation_warning_visibility",
            "validation_blocker_visibility",
            "unsupported_validation_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestProhibitedDomainVisibility:
    prohibited_domain_visibility_id: str
    prohibited_domains: tuple[str, ...]
    visible_blocked_reasons: tuple[str, ...]
    deterministic_order: int
    prohibited_domain_scope: str = REFRESH_MANIFEST_PROHIBITED_DOMAIN_SCOPE
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden_operational_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("prohibited_domains", "visible_blocked_reasons"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestUnsupportedStateVisibility:
    unsupported_state_visibility_id: str
    unsupported_states: tuple[str, ...]
    unknown_states: tuple[str, ...]
    blocked_states: tuple[str, ...]
    prohibited_states: tuple[str, ...]
    stale_states: tuple[str, ...]
    deterministic_order: int
    unsupported_state_scope: str = REFRESH_MANIFEST_UNSUPPORTED_STATE_SCOPE
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_recovery_enabled: bool = False
    remediation_enabled: bool = False
    hidden_unsupported_state_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_states",
            "unknown_states",
            "blocked_states",
            "prohibited_states",
            "stale_states",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestContinuityMetadata:
    continuity_metadata_id: str
    provenance_continuity_references: tuple[str, ...]
    lineage_continuity_references: tuple[str, ...]
    replay_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    diagnostics_references: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    continuity_scope: str = REFRESH_MANIFEST_CONTINUITY_SCOPE
    continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_continuity_references",
            "lineage_continuity_references",
            "replay_references",
            "rollback_references",
            "diagnostics_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestReplayMetadata:
    replay_metadata_id: str
    replay_reference: str
    replay_evidence_references: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    replay_scope: str = REFRESH_MANIFEST_REPLAY_SCOPE
    replay_safe: bool = True
    descriptive_only: bool = True
    live_replay_enabled: bool = False
    runtime_execution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "replay_evidence_references")


@dataclass(frozen=True)
class RefreshManifestRollbackMetadata:
    rollback_metadata_id: str
    rollback_reference: str
    rollback_evidence_references: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    rollback_scope: str = REFRESH_MANIFEST_ROLLBACK_SCOPE
    rollback_safe: bool = True
    descriptive_only: bool = True
    automatic_rollback_enabled: bool = False
    recovery_execution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "rollback_evidence_references")


@dataclass(frozen=True)
class RefreshManifestDiagnosticsVisibility:
    diagnostics_visibility_id: str
    diagnostic_references: tuple[str, ...]
    warning_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    unsupported_state_visibility: tuple[str, ...]
    prohibited_domain_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_scope: str = REFRESH_MANIFEST_DIAGNOSTICS_SCOPE
    diagnostics_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    silent_fallback_enabled: bool = False
    automatic_recovery_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "unsupported_state_visibility",
            "prohibited_domain_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifestGovernanceVisibility:
    governance_visibility_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_scope: str = REFRESH_MANIFEST_GOVERNANCE_SCOPE
    governance_visible: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    mutation_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshManifest:
    identity: RefreshManifestIdentity
    states: tuple[RefreshManifestState, ...]
    source_lineage: tuple[RefreshManifestSourceLineage, ...]
    extraction_lineage: tuple[RefreshManifestExtractionLineage, ...]
    patch_lineage: tuple[RefreshManifestPatchLineage, ...]
    schema_version_visibility: tuple[RefreshManifestSchemaVersionVisibility, ...]
    dependency_visibility: tuple[RefreshManifestDependencyVisibility, ...]
    trust_visibility: tuple[RefreshManifestTrustVisibility, ...]
    validation_visibility: tuple[RefreshManifestValidationVisibility, ...]
    prohibited_domain_visibility: tuple[RefreshManifestProhibitedDomainVisibility, ...]
    unsupported_state_visibility: tuple[RefreshManifestUnsupportedStateVisibility, ...]
    continuity_metadata: RefreshManifestContinuityMetadata
    replay_metadata: RefreshManifestReplayMetadata
    rollback_metadata: RefreshManifestRollbackMetadata
    diagnostics_visibility: tuple[RefreshManifestDiagnosticsVisibility, ...]
    governance_visibility: RefreshManifestGovernanceVisibility
    manifest_scope: str = V4_1_REFRESH_MANIFEST_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    deployment_execution_enabled: bool = False
    automatic_refresh_enabled: bool = False
    automatic_migration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    mutation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    hidden_operational_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "states",
            "source_lineage",
            "extraction_lineage",
            "patch_lineage",
            "schema_version_visibility",
            "dependency_visibility",
            "trust_visibility",
            "validation_visibility",
            "prohibited_domain_visibility",
            "unsupported_state_visibility",
            "diagnostics_visibility",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_refresh_manifest_identity() -> RefreshManifestIdentity:
    return RefreshManifestIdentity(
        manifest_id="v4_1_refresh_manifest_primary",
        refresh_cycle_id="v4_1_phase_1_refresh_manifest_foundations",
        manifest_version="v4.1.0-foundation",
        source_bundle_reference="v4_0_closeout_and_v4_1_readiness_report",
        extraction_reference="v4_1_refresh_manifest_extraction_primary",
        patch_reference="v4_1_refresh_manifest_patch_lineage_primary",
        schema_version=V4_1_REFRESH_MANIFEST_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_MANIFEST_GENERATED_AT,
        provenance_reference="v4_1_refresh_manifest_provenance_primary",
        lineage_reference="v4_1_refresh_manifest_lineage_primary",
        trust_reference="v4_1_refresh_manifest_trust_visibility_primary",
        validation_reference="v4_1_refresh_manifest_validation_visibility_primary",
        diagnostics_reference="v4_1_refresh_manifest_diagnostics_primary",
        governance_reference="v4_1_refresh_manifest_governance_primary",
    )


def default_refresh_manifest_states(
    identity: RefreshManifestIdentity | None = None,
) -> tuple[RefreshManifestState, ...]:
    source = identity or default_refresh_manifest_identity()
    visibility = "v4_1_refresh_manifest_unsupported_state_visibility_primary"
    return (
        RefreshManifestState(
            state_id="v4_1_refresh_manifest_state_supported_identity",
            state=REFRESH_MANIFEST_STATE_SUPPORTED,
            reason="refresh manifest identity is deterministic and descriptive",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            visibility_reference=visibility,
            deterministic_order=1,
        ),
        RefreshManifestState(
            state_id="v4_1_refresh_manifest_state_unsupported_source_provider",
            state=REFRESH_MANIFEST_STATE_UNSUPPORTED,
            reason="unsupported refresh source providers remain visible and blocked from execution",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            visibility_reference=visibility,
            deterministic_order=2,
            visibility_status=REFRESH_MANIFEST_VISIBILITY_FAIL_VISIBLE,
            severity=REFRESH_MANIFEST_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshManifestState(
            state_id="v4_1_refresh_manifest_state_blocked_dependency_gap",
            state=REFRESH_MANIFEST_STATE_BLOCKED,
            reason="missing refresh dependencies remain blocked evidence until a future phase supplies them",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            visibility_reference=visibility,
            deterministic_order=3,
            visibility_status=REFRESH_MANIFEST_VISIBILITY_FAIL_VISIBLE,
            severity=REFRESH_MANIFEST_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshManifestState(
            state_id="v4_1_refresh_manifest_state_unknown_future_source",
            state=REFRESH_MANIFEST_STATE_UNKNOWN,
            reason="future refresh source state is explicitly unknown and not inferred",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            visibility_reference=visibility,
            deterministic_order=4,
            visibility_status=REFRESH_MANIFEST_VISIBILITY_FAIL_VISIBLE,
            severity=REFRESH_MANIFEST_SEVERITY_UNKNOWN,
            fail_visible=True,
        ),
        RefreshManifestState(
            state_id="v4_1_refresh_manifest_state_stale_lifecycle_dependency",
            state=REFRESH_MANIFEST_STATE_STALE,
            reason="v4.0 lifecycle dependency context remains visible as a read-only stale reference",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            visibility_reference=visibility,
            deterministic_order=5,
            visibility_status=REFRESH_MANIFEST_VISIBILITY_FAIL_VISIBLE,
            severity=REFRESH_MANIFEST_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshManifestState(
            state_id="v4_1_refresh_manifest_state_prohibited_execution_domain",
            state=REFRESH_MANIFEST_STATE_PROHIBITED,
            reason="execution-capable refresh behavior is prohibited",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            visibility_reference=visibility,
            deterministic_order=6,
            visibility_status=REFRESH_MANIFEST_VISIBILITY_FAIL_VISIBLE,
            severity=REFRESH_MANIFEST_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
    )


def default_refresh_manifest_source_lineage(
    identity: RefreshManifestIdentity | None = None,
) -> RefreshManifestSourceLineage:
    source = identity or default_refresh_manifest_identity()
    return RefreshManifestSourceLineage(
        source_lineage_id="v4_1_refresh_manifest_source_lineage_primary",
        source_system_reference="epochforge_v4_0_closeout_governance_evidence",
        source_bundle_reference=source.source_bundle_reference,
        source_evidence_references=(
            "docs/generated/v4_0_closeout_and_v4_1_readiness_report.json",
            "docs/generated/v4_0_patch_lifecycle_foundations_report.json",
            "docs/migration/V4_0_CLOSEOUT_AND_V4_1_READINESS.md",
        ),
        prior_manifest_references=(
            "v4_0_closeout_and_v4_1_readiness",
            "v4_0_patch_lifecycle_foundations",
        ),
        unsupported_source_visibility=("v4_1_future_refresh_source_provider_not_declared",),
        provenance_reference=source.provenance_reference,
        deterministic_hash_reference="v4_1_refresh_manifest_source_lineage_hash",
        deterministic_order=1,
    )


def default_refresh_manifest_extraction_lineage(
    identity: RefreshManifestIdentity | None = None,
) -> RefreshManifestExtractionLineage:
    source = identity or default_refresh_manifest_identity()
    return RefreshManifestExtractionLineage(
        extraction_lineage_id=source.extraction_reference,
        extractor_reference="v4_1_refresh_manifest_foundation_extractor_descriptive_only",
        extraction_snapshot_reference="v4_1_refresh_manifest_foundation_snapshot",
        extraction_evidence_references=(
            "v4_1_refresh_manifest_identity_fields",
            "v4_1_refresh_manifest_lineage_fields",
            "v4_1_refresh_manifest_governance_visibility_fields",
        ),
        unsupported_extraction_states=("v4_1_live_refresh_extraction_not_supported",),
        provenance_reference=source.provenance_reference,
        deterministic_hash_reference="v4_1_refresh_manifest_extraction_lineage_hash",
        deterministic_order=1,
    )


def default_refresh_manifest_patch_lineage(
    identity: RefreshManifestIdentity | None = None,
) -> RefreshManifestPatchLineage:
    source = identity or default_refresh_manifest_identity()
    return RefreshManifestPatchLineage(
        patch_lineage_id=source.patch_reference,
        patch_reference="v4_1_refresh_manifest_foundation_patch_reference",
        patch_evidence_references=(
            "v4_0_closeout_and_v4_1_readiness_report_hash",
            "v4_1_refresh_manifest_foundation_model_hash",
        ),
        prior_patch_references=(
            "v4_0_patch_lifecycle_foundations",
            "v4_0_closeout_and_v4_1_readiness",
        ),
        rollback_references=("v4_0_closeout_and_v4_1_readiness_report",),
        provenance_reference=source.provenance_reference,
        deterministic_hash_reference="v4_1_refresh_manifest_patch_lineage_hash",
        deterministic_order=1,
    )


def default_schema_version_visibility(
    identity: RefreshManifestIdentity | None = None,
) -> RefreshManifestSchemaVersionVisibility:
    source = identity or default_refresh_manifest_identity()
    return RefreshManifestSchemaVersionVisibility(
        schema_visibility_id="v4_1_refresh_manifest_schema_visibility_primary",
        manifest_schema_version=source.schema_version,
        source_schema_version="v4_0.closeout_and_v4_1_readiness_report.1",
        extraction_schema_version="v4_1.refresh_manifest_extraction_lineage.1",
        patch_schema_version="v4_1.refresh_manifest_patch_lineage.1",
        visible_schema_constraints=(
            "deterministic_serialization_required",
            "deterministic_hashing_required",
            "unsupported_states_must_be_fail_visible",
            "execution_semantics_must_remain_disabled",
        ),
        unsupported_schema_versions=("future_refresh_manifest_schema_not_declared",),
        deterministic_order=1,
    )


def default_dependency_visibility() -> RefreshManifestDependencyVisibility:
    return RefreshManifestDependencyVisibility(
        dependency_visibility_id="v4_1_refresh_manifest_dependency_visibility_primary",
        dependency_references=(
            "v4_0_closeout_and_v4_1_readiness_report",
            "v4_0_patch_lifecycle_foundations_report",
            "v4_1_refresh_manifest_schema_visibility_primary",
        ),
        missing_dependency_visibility=("future_refresh_provider_contract_not_declared",),
        stale_dependency_visibility=("v4_0_lifecycle_dependency_snapshot_read_only",),
        prohibited_dependency_visibility=("production_runtime_bundle_dependency",),
        deterministic_order=1,
    )


def default_trust_visibility() -> RefreshManifestTrustVisibility:
    return RefreshManifestTrustVisibility(
        trust_visibility_id="v4_1_refresh_manifest_trust_visibility_primary",
        trusted_source_references=(
            "v4_0_closeout_and_v4_1_readiness_report",
            "v4_0_patch_lifecycle_foundations_report",
        ),
        untrusted_source_visibility=("live_production_bundle_source_not_trusted",),
        ambiguous_trust_visibility=("future_refresh_provider_trust_unknown",),
        deterministic_order=1,
    )


def default_validation_visibility() -> RefreshManifestValidationVisibility:
    return RefreshManifestValidationVisibility(
        validation_visibility_id="v4_1_refresh_manifest_validation_visibility_primary",
        validation_references=(
            "deterministic_serialization_validation",
            "deterministic_hashing_validation",
            "deterministic_equality_validation",
            "non_execution_boundary_validation",
            "planner_integration_disabled_validation",
            "production_consumption_disabled_validation",
        ),
        validation_warning_visibility=("future_refresh_provider_contract_not_declared",),
        validation_blocker_visibility=("production_runtime_bundle_dependency",),
        unsupported_validation_visibility=("live_refresh_execution_validation_not_supported",),
        deterministic_order=1,
    )


def default_prohibited_domain_visibility() -> RefreshManifestProhibitedDomainVisibility:
    return RefreshManifestProhibitedDomainVisibility(
        prohibited_domain_visibility_id="v4_1_refresh_manifest_prohibited_domain_visibility_primary",
        prohibited_domains=PROHIBITED_REFRESH_DOMAINS,
        visible_blocked_reasons=tuple(f"v4_1_prohibited_domain_{domain}" for domain in PROHIBITED_REFRESH_DOMAINS),
        deterministic_order=1,
    )


def default_unsupported_state_visibility(
    states: tuple[RefreshManifestState, ...] | None = None,
) -> RefreshManifestUnsupportedStateVisibility:
    manifest_states = states or default_refresh_manifest_states()
    return RefreshManifestUnsupportedStateVisibility(
        unsupported_state_visibility_id="v4_1_refresh_manifest_unsupported_state_visibility_primary",
        unsupported_states=tuple(
            state.state_id for state in manifest_states if state.state == REFRESH_MANIFEST_STATE_UNSUPPORTED
        ),
        unknown_states=tuple(state.state_id for state in manifest_states if state.state == REFRESH_MANIFEST_STATE_UNKNOWN),
        blocked_states=tuple(state.state_id for state in manifest_states if state.state == REFRESH_MANIFEST_STATE_BLOCKED),
        prohibited_states=tuple(
            state.state_id for state in manifest_states if state.state == REFRESH_MANIFEST_STATE_PROHIBITED
        ),
        stale_states=tuple(state.state_id for state in manifest_states if state.state == REFRESH_MANIFEST_STATE_STALE),
        deterministic_order=1,
    )


def default_continuity_metadata(identity: RefreshManifestIdentity | None = None) -> RefreshManifestContinuityMetadata:
    source = identity or default_refresh_manifest_identity()
    return RefreshManifestContinuityMetadata(
        continuity_metadata_id="v4_1_refresh_manifest_continuity_primary",
        provenance_continuity_references=(
            source.provenance_reference,
            "v4_0_closeout_and_v4_1_readiness_provenance_safe",
        ),
        lineage_continuity_references=(
            source.lineage_reference,
            "v4_0_closeout_and_v4_1_readiness_lineage_safe",
        ),
        replay_references=("v4_1_refresh_manifest_replay_primary",),
        rollback_references=("v4_1_refresh_manifest_rollback_primary",),
        diagnostics_references=(source.diagnostics_reference,),
        deterministic_hash_reference="v4_1_refresh_manifest_continuity_hash",
        deterministic_order=1,
    )


def default_replay_metadata() -> RefreshManifestReplayMetadata:
    return RefreshManifestReplayMetadata(
        replay_metadata_id="v4_1_refresh_manifest_replay_primary",
        replay_reference="v4_1_refresh_manifest_replay_safe_descriptive_reference",
        replay_evidence_references=(
            "v4_1_refresh_manifest_serialization_snapshot",
            "v4_1_refresh_manifest_hash_snapshot",
        ),
        deterministic_hash_reference="v4_1_refresh_manifest_replay_hash",
        deterministic_order=1,
    )


def default_rollback_metadata() -> RefreshManifestRollbackMetadata:
    return RefreshManifestRollbackMetadata(
        rollback_metadata_id="v4_1_refresh_manifest_rollback_primary",
        rollback_reference="v4_0_closeout_and_v4_1_readiness_report",
        rollback_evidence_references=(
            "docs/generated/v4_0_closeout_and_v4_1_readiness_report.json",
            "docs/migration/V4_0_CLOSEOUT_AND_V4_1_READINESS.md",
        ),
        deterministic_hash_reference="v4_1_refresh_manifest_rollback_hash",
        deterministic_order=1,
    )


def default_diagnostics_visibility(
    unsupported: RefreshManifestUnsupportedStateVisibility | None = None,
    prohibited: RefreshManifestProhibitedDomainVisibility | None = None,
) -> RefreshManifestDiagnosticsVisibility:
    unsupported_visibility = unsupported or default_unsupported_state_visibility()
    prohibited_visibility = prohibited or default_prohibited_domain_visibility()
    return RefreshManifestDiagnosticsVisibility(
        diagnostics_visibility_id="v4_1_refresh_manifest_diagnostics_primary",
        diagnostic_references=(
            "v4_1_refresh_manifest_visibility_validation",
            "v4_1_refresh_manifest_integrity_validation",
            "v4_1_refresh_manifest_non_execution_validation",
        ),
        warning_visibility=unsupported_visibility.unsupported_states + unsupported_visibility.stale_states,
        blocker_visibility=unsupported_visibility.blocked_states,
        unsupported_state_visibility=unsupported_visibility.unsupported_states + unsupported_visibility.unknown_states,
        prohibited_domain_visibility=prohibited_visibility.prohibited_domains,
        deterministic_order=1,
    )


def default_governance_visibility() -> RefreshManifestGovernanceVisibility:
    return RefreshManifestGovernanceVisibility(
        governance_visibility_id="v4_1_refresh_manifest_governance_primary",
        governance_references=(
            "v4_0_closeout_and_v4_1_readiness_governance_chain",
            "v4_1_refresh_manifest_foundation_governance_boundary",
        ),
        explicit_limitations=EXPLICIT_REFRESH_MANIFEST_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_REFRESH_MANIFEST_PROHIBITIONS,
        deterministic_order=1,
    )


def default_refresh_manifest() -> RefreshManifest:
    identity = default_refresh_manifest_identity()
    states = default_refresh_manifest_states(identity)
    prohibited = default_prohibited_domain_visibility()
    unsupported = default_unsupported_state_visibility(states)
    return RefreshManifest(
        identity=identity,
        states=states,
        source_lineage=(default_refresh_manifest_source_lineage(identity),),
        extraction_lineage=(default_refresh_manifest_extraction_lineage(identity),),
        patch_lineage=(default_refresh_manifest_patch_lineage(identity),),
        schema_version_visibility=(default_schema_version_visibility(identity),),
        dependency_visibility=(default_dependency_visibility(),),
        trust_visibility=(default_trust_visibility(),),
        validation_visibility=(default_validation_visibility(),),
        prohibited_domain_visibility=(prohibited,),
        unsupported_state_visibility=(unsupported,),
        continuity_metadata=default_continuity_metadata(identity),
        replay_metadata=default_replay_metadata(),
        rollback_metadata=default_rollback_metadata(),
        diagnostics_visibility=(default_diagnostics_visibility(unsupported, prohibited),),
        governance_visibility=default_governance_visibility(),
    )
