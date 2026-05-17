"""Deterministic v4.2 refresh coordination manifest foundation models.

Refresh coordination manifests are descriptive governance evidence only. They
do not execute refreshes, orchestrate work, resolve dependencies, consume
production bundles, integrate with planners, authorize behavior, remediate
blockers, roll back state, correct state, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_2_COORDINATION_MANIFEST_PHASE_ID = "v4_2_refresh_coordination_manifest_foundations"
V4_2_COORDINATION_MANIFEST_SCHEMA_VERSION = "v4_2.refresh_coordination_manifest_foundations.1"
V4_2_COORDINATION_MANIFEST_REPORT_SCHEMA_VERSION = "v4_2.refresh_coordination_manifest_foundations_report.1"
V4_2_COORDINATION_MANIFEST_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_COORDINATION_MANIFEST_STATUS_STABLE = "v4_2_coordination_manifest_foundation_stable"
V4_2_COORDINATION_MANIFEST_STATUS_BLOCKED = "v4_2_coordination_manifest_foundation_blocked"
V4_2_COORDINATION_MANIFEST_PURPOSE = "deterministic_refresh_coordination_governance_intelligence_only"

COORDINATION_STATE_SUPPORTED = "supported"
COORDINATION_STATE_UNSUPPORTED = "unsupported"
COORDINATION_STATE_BLOCKED = "blocked"
COORDINATION_STATE_PROHIBITED = "prohibited"
COORDINATION_STATE_STALE = "stale"
COORDINATION_STATE_UNKNOWN = "unknown"
COORDINATION_STATES: tuple[str, ...] = (
    COORDINATION_STATE_SUPPORTED,
    COORDINATION_STATE_UNSUPPORTED,
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_UNKNOWN,
)
FAIL_VISIBLE_COORDINATION_STATES: tuple[str, ...] = (
    COORDINATION_STATE_UNSUPPORTED,
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_UNKNOWN,
)

COORDINATION_DIAGNOSTIC_UNSUPPORTED_STATE = "unsupported_state_visibility"
COORDINATION_DIAGNOSTIC_PROHIBITED_STATE = "prohibited_state_visibility"
COORDINATION_DIAGNOSTIC_BLOCKED_COORDINATION = "blocked_coordination_visibility"
COORDINATION_DIAGNOSTIC_LINEAGE_CONTINUITY = "lineage_continuity_visibility"
COORDINATION_DIAGNOSTIC_CONTINUITY_VISIBILITY = "continuity_visibility"
COORDINATION_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_COORDINATION_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "refresh_execution",
    "planner_integration",
    "production_bundle_consumption",
    "runtime_mutation",
    "remediation",
    "automatic_correction",
    "automatic_rollback",
    "automatic_recovery",
    "dependency_resolution",
    "authorization_systems",
    "approval_systems",
    "recommendation_systems",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "operational_execution",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_COORDINATION_MANIFEST_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 1 creates deterministic refresh coordination manifest governance intelligence only.",
    "v4.2 Phase 1 does not enable orchestration execution.",
    "v4.2 Phase 1 does not enable refresh execution.",
    "v4.2 Phase 1 does not enable planner integration.",
    "v4.2 Phase 1 does not enable production consumption.",
    "v4.2 Phase 1 does not enable runtime mutation.",
    "v4.2 Phase 1 does not enable remediation.",
    "v4.2 Phase 1 does not enable automatic correction.",
    "v4.2 Phase 1 does not enable automatic rollback.",
    "v4.2 Phase 1 does not enable dependency resolution.",
    "v4.2 Phase 1 does not enable authorization or approval.",
    "v4.2 Phase 1 does not enable recommendation, ranking, scoring, or selection.",
)

EXPLICIT_COORDINATION_MANIFEST_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration execution exists.",
    "No refresh execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No remediation exists.",
    "No automatic correction exists.",
    "No automatic rollback exists.",
    "No dependency resolution exists.",
    "No authorization or approval behavior exists.",
    "No recommendation, ranking, scoring, or selection behavior exists.",
    "No operational execution exists.",
    "No hidden execution pathway exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationManifestIdentity:
    manifest_id: str
    coordination_cycle_id: str
    manifest_version: str
    schema_version: str
    generated_at: str
    source_readiness_reference: str
    provenance_reference: str
    lineage_reference: str
    continuity_reference: str
    dependency_reference: str
    diagnostics_reference: str
    replay_reference: str
    rollback_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_COORDINATION_MANIFEST_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    production_bundle_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class CoordinationManifestMetadata:
    metadata_id: str
    phase_id: str
    source_phase_reference: str
    source_report_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    deterministic_order: int
    purpose: str = V4_2_COORDINATION_MANIFEST_PURPOSE
    deterministic: bool = True
    governance_first: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    continuity_certified: bool = True
    integrity_enforced: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    non_remediating: bool = True
    non_executing: bool = True
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_report_references", "evidence_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDependencyReference:
    dependency_id: str
    dependency_type: str
    source_reference: str
    target_reference: str
    dependency_state: str
    visibility_reference: str
    deterministic_order: int
    blocked_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    prohibited_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    dependency_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    dependency_resolution_enabled: bool = False
    automatic_refresh_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    production_consumption_enabled: bool = False
    hidden_dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_reason_visibility",
            "stale_reason_visibility",
            "prohibited_reason_visibility",
            "unsupported_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationLineageReference:
    lineage_id: str
    predecessor_reference: str
    successor_reference: str
    lineage_evidence_references: tuple[str, ...]
    provenance_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    lineage_repair_enabled: bool = False
    inferred_lineage_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "lineage_evidence_references")


@dataclass(frozen=True)
class CoordinationContinuityReference:
    continuity_id: str
    continuity_type: str
    continuity_state: str
    continuity_evidence_references: tuple[str, ...]
    replay_reference: str
    rollback_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    continuity_visible: bool = True
    continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    recovery_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "continuity_evidence_references")


@dataclass(frozen=True)
class CoordinationDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    source_reference: str
    finding: str
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    dependency_resolution_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_reference_ids")


@dataclass(frozen=True)
class CoordinationProhibitedStateVisibility:
    prohibited_visibility_id: str
    prohibited_states: tuple[str, ...]
    prohibited_capabilities: tuple[str, ...]
    blocked_reason_visibility: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    execution_authorized: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("prohibited_states", "prohibited_capabilities", "blocked_reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationUnsupportedStateVisibility:
    unsupported_visibility_id: str
    unsupported_states: tuple[str, ...]
    unknown_states: tuple[str, ...]
    blocked_states: tuple[str, ...]
    stale_states: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    automatic_recovery_enabled: bool = False
    remediation_enabled: bool = False
    hidden_unsupported_state_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("unsupported_states", "unknown_states", "blocked_states", "stale_states"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationGovernanceVisibility:
    governance_visibility_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    dependency_resolution_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    operational_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationManifest:
    identity: CoordinationManifestIdentity
    metadata: CoordinationManifestMetadata
    dependency_references: tuple[CoordinationDependencyReference, ...]
    lineage_references: tuple[CoordinationLineageReference, ...]
    continuity_references: tuple[CoordinationContinuityReference, ...]
    diagnostics: tuple[CoordinationDiagnostic, ...]
    prohibited_state_visibility: CoordinationProhibitedStateVisibility
    unsupported_state_visibility: CoordinationUnsupportedStateVisibility
    governance_visibility: CoordinationGovernanceVisibility
    manifest_scope: str = V4_2_COORDINATION_MANIFEST_PURPOSE
    deterministic: bool = True
    governance_first: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    continuity_certified: bool = True
    integrity_enforced: bool = True
    fail_visible: bool = True
    non_executable: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    production_bundle_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    dependency_resolution_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    operational_execution_enabled: bool = False
    hidden_operational_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("dependency_references", "lineage_references", "continuity_references", "diagnostics"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_coordination_manifest_identity() -> CoordinationManifestIdentity:
    return CoordinationManifestIdentity(
        manifest_id="v4_2_coordination_manifest_primary",
        coordination_cycle_id="v4_2_phase_1_refresh_coordination_manifest_foundations",
        manifest_version="v4.2.0-phase-1",
        schema_version=V4_2_COORDINATION_MANIFEST_SCHEMA_VERSION,
        generated_at=V4_2_COORDINATION_MANIFEST_GENERATED_AT,
        source_readiness_reference="v4_1_closeout_and_v4_2_readiness_report",
        provenance_reference="v4_2_coordination_manifest_provenance_primary",
        lineage_reference="v4_2_coordination_manifest_lineage_primary",
        continuity_reference="v4_2_coordination_manifest_continuity_primary",
        dependency_reference="v4_2_coordination_manifest_dependency_primary",
        diagnostics_reference="v4_2_coordination_manifest_diagnostics_primary",
        replay_reference="v4_2_coordination_manifest_replay_primary",
        rollback_reference="v4_2_coordination_manifest_rollback_primary",
        governance_reference="v4_2_coordination_manifest_governance_primary",
    )


def default_coordination_manifest_metadata(
    identity: CoordinationManifestIdentity | None = None,
) -> CoordinationManifestMetadata:
    source = identity or default_coordination_manifest_identity()
    return CoordinationManifestMetadata(
        metadata_id="v4_2_coordination_manifest_metadata_primary",
        phase_id=V4_2_COORDINATION_MANIFEST_PHASE_ID,
        source_phase_reference="v4_1_closeout_and_v4_2_readiness",
        source_report_references=(
            "docs/generated/v4_1_closeout_and_v4_2_readiness_report.json",
            "docs/generated/v4_2_readiness_certification_report.json",
            "docs/migration/V4_1_CLOSEOUT_AND_V4_2_READINESS.md",
        ),
        evidence_references=(
            source.source_readiness_reference,
            source.provenance_reference,
            source.lineage_reference,
            source.continuity_reference,
            source.diagnostics_reference,
        ),
        deterministic_order=10,
    )


def default_coordination_dependency_references() -> tuple[CoordinationDependencyReference, ...]:
    return (
        CoordinationDependencyReference(
            dependency_id="v4_2_coordination_dependency_v4_1_readiness",
            dependency_type="readiness_evidence",
            source_reference="v4_1_closeout_and_v4_2_readiness_report",
            target_reference="v4_2_coordination_manifest_primary",
            dependency_state=COORDINATION_STATE_SUPPORTED,
            visibility_reference="v4_2_coordination_manifest_unsupported_visibility_primary",
            deterministic_order=10,
            fail_visible=False,
        ),
        CoordinationDependencyReference(
            dependency_id="v4_2_coordination_dependency_future_refresh_provider_contract",
            dependency_type="future_provider_contract",
            source_reference="future_refresh_provider_contract",
            target_reference="v4_2_coordination_manifest_primary",
            dependency_state=COORDINATION_STATE_UNSUPPORTED,
            visibility_reference="v4_2_coordination_manifest_unsupported_visibility_primary",
            deterministic_order=20,
            unsupported_reason_visibility=("future refresh provider contracts are not declared in Phase 1",),
        ),
        CoordinationDependencyReference(
            dependency_id="v4_2_coordination_dependency_future_runtime_sequence",
            dependency_type="runtime_sequence",
            source_reference="future_refresh_sequence",
            target_reference="v4_2_coordination_manifest_primary",
            dependency_state=COORDINATION_STATE_BLOCKED,
            visibility_reference="v4_2_coordination_manifest_unsupported_visibility_primary",
            deterministic_order=30,
            blocked_reason_visibility=("runtime sequencing is prohibited and unavailable in Phase 1",),
        ),
        CoordinationDependencyReference(
            dependency_id="v4_2_coordination_dependency_v4_1_snapshot_stale",
            dependency_type="prior_phase_snapshot",
            source_reference="v4_1_refresh_governance_snapshot",
            target_reference="v4_2_coordination_manifest_primary",
            dependency_state=COORDINATION_STATE_STALE,
            visibility_reference="v4_2_coordination_manifest_unsupported_visibility_primary",
            deterministic_order=40,
            stale_reason_visibility=("prior v4.1 governance snapshot remains read-only evidence",),
        ),
        CoordinationDependencyReference(
            dependency_id="v4_2_coordination_dependency_production_bundle",
            dependency_type="production_runtime_bundle",
            source_reference="production_runtime_bundle",
            target_reference="v4_2_coordination_manifest_primary",
            dependency_state=COORDINATION_STATE_PROHIBITED,
            visibility_reference="v4_2_coordination_manifest_prohibited_visibility_primary",
            deterministic_order=50,
            prohibited_reason_visibility=("production bundle consumption is prohibited",),
        ),
    )


def default_coordination_lineage_references(
    identity: CoordinationManifestIdentity | None = None,
) -> tuple[CoordinationLineageReference, ...]:
    source = identity or default_coordination_manifest_identity()
    return (
        CoordinationLineageReference(
            lineage_id="v4_2_coordination_lineage_v4_1_closeout",
            predecessor_reference="v4_1_closeout_and_v4_2_readiness",
            successor_reference=source.manifest_id,
            lineage_evidence_references=(
                "docs/generated/v4_1_closeout_and_v4_2_readiness_report.json",
                "docs/migration/V4_1_CLOSEOUT_AND_V4_2_READINESS.md",
            ),
            provenance_reference=source.provenance_reference,
            deterministic_hash_reference="v4_2_coordination_lineage_v4_1_closeout_hash",
            deterministic_order=10,
        ),
        CoordinationLineageReference(
            lineage_id="v4_2_coordination_lineage_refresh_governance_stack",
            predecessor_reference="v4_1_refresh_governance_stack",
            successor_reference="v4_2_refresh_coordination_governance_stack",
            lineage_evidence_references=(
                "v4_1_refresh_manifest_foundations",
                "v4_1_refresh_continuity_certification",
                "v4_2_coordination_manifest_foundations",
            ),
            provenance_reference=source.provenance_reference,
            deterministic_hash_reference="v4_2_coordination_lineage_refresh_governance_stack_hash",
            deterministic_order=20,
        ),
    )


def default_coordination_continuity_references(
    identity: CoordinationManifestIdentity | None = None,
) -> tuple[CoordinationContinuityReference, ...]:
    source = identity or default_coordination_manifest_identity()
    return (
        CoordinationContinuityReference(
            continuity_id="v4_2_coordination_continuity_manifest_primary",
            continuity_type="manifest_continuity",
            continuity_state=COORDINATION_STATE_SUPPORTED,
            continuity_evidence_references=(
                source.continuity_reference,
                "v4_1_closeout_and_v4_2_readiness_continuity",
            ),
            replay_reference=source.replay_reference,
            rollback_reference=source.rollback_reference,
            deterministic_hash_reference="v4_2_coordination_manifest_continuity_hash",
            deterministic_order=10,
        ),
        CoordinationContinuityReference(
            continuity_id="v4_2_coordination_continuity_replay_safe",
            continuity_type="replay_safety",
            continuity_state=COORDINATION_STATE_SUPPORTED,
            continuity_evidence_references=(
                "v4_2_coordination_manifest_serialization_snapshot",
                "v4_2_coordination_manifest_hash_snapshot",
            ),
            replay_reference=source.replay_reference,
            rollback_reference=source.rollback_reference,
            deterministic_hash_reference="v4_2_coordination_manifest_replay_continuity_hash",
            deterministic_order=20,
        ),
        CoordinationContinuityReference(
            continuity_id="v4_2_coordination_continuity_rollback_safe",
            continuity_type="rollback_safety",
            continuity_state=COORDINATION_STATE_SUPPORTED,
            continuity_evidence_references=(
                "docs/generated/v4_1_closeout_and_v4_2_readiness_report.json",
                "docs/generated/v4_2_readiness_certification_report.json",
            ),
            replay_reference=source.replay_reference,
            rollback_reference=source.rollback_reference,
            deterministic_hash_reference="v4_2_coordination_manifest_rollback_continuity_hash",
            deterministic_order=30,
        ),
    )


def default_coordination_prohibited_state_visibility(
    dependencies: tuple[CoordinationDependencyReference, ...] | None = None,
) -> CoordinationProhibitedStateVisibility:
    dependency_records = dependencies or default_coordination_dependency_references()
    prohibited_dependency_ids = tuple(
        dependency.dependency_id
        for dependency in dependency_records
        if dependency.dependency_state == COORDINATION_STATE_PROHIBITED
    )
    return CoordinationProhibitedStateVisibility(
        prohibited_visibility_id="v4_2_coordination_manifest_prohibited_visibility_primary",
        prohibited_states=prohibited_dependency_ids
        + tuple(f"v4_2_coordination_capability_{capability}" for capability in PROHIBITED_COORDINATION_CAPABILITIES),
        prohibited_capabilities=PROHIBITED_COORDINATION_CAPABILITIES,
        blocked_reason_visibility=tuple(
            f"v4_2_prohibited_coordination_capability_{capability}"
            for capability in PROHIBITED_COORDINATION_CAPABILITIES
        ),
        deterministic_order=10,
    )


def default_coordination_unsupported_state_visibility(
    dependencies: tuple[CoordinationDependencyReference, ...] | None = None,
) -> CoordinationUnsupportedStateVisibility:
    dependency_records = dependencies or default_coordination_dependency_references()
    return CoordinationUnsupportedStateVisibility(
        unsupported_visibility_id="v4_2_coordination_manifest_unsupported_visibility_primary",
        unsupported_states=tuple(
            dependency.dependency_id
            for dependency in dependency_records
            if dependency.dependency_state == COORDINATION_STATE_UNSUPPORTED
        ),
        unknown_states=("v4_2_coordination_future_manifest_consumer_unknown",),
        blocked_states=tuple(
            dependency.dependency_id
            for dependency in dependency_records
            if dependency.dependency_state == COORDINATION_STATE_BLOCKED
        ),
        stale_states=tuple(
            dependency.dependency_id
            for dependency in dependency_records
            if dependency.dependency_state == COORDINATION_STATE_STALE
        ),
        deterministic_order=10,
    )


def default_coordination_diagnostics(
    dependencies: tuple[CoordinationDependencyReference, ...] | None = None,
) -> tuple[CoordinationDiagnostic, ...]:
    dependency_records = dependencies or default_coordination_dependency_references()
    unsupported_ids = tuple(
        dependency.dependency_id
        for dependency in dependency_records
        if dependency.dependency_state == COORDINATION_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        dependency.dependency_id
        for dependency in dependency_records
        if dependency.dependency_state == COORDINATION_STATE_BLOCKED
    )
    prohibited_ids = tuple(
        dependency.dependency_id
        for dependency in dependency_records
        if dependency.dependency_state == COORDINATION_STATE_PROHIBITED
    )
    stale_ids = tuple(
        dependency.dependency_id
        for dependency in dependency_records
        if dependency.dependency_state == COORDINATION_STATE_STALE
    )
    return (
        CoordinationDiagnostic(
            diagnostic_id="v4_2_coordination_diagnostic_unsupported_dependency_visible",
            category=COORDINATION_DIAGNOSTIC_UNSUPPORTED_STATE,
            severity="warning",
            source_reference="v4_2_coordination_manifest_dependency_primary",
            finding="Unsupported coordination dependencies remain visible and are not resolved.",
            affected_reference_ids=unsupported_ids,
            deterministic_order=10,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_2_coordination_diagnostic_blocked_coordination_visible",
            category=COORDINATION_DIAGNOSTIC_BLOCKED_COORDINATION,
            severity="blocked",
            source_reference="v4_2_coordination_manifest_dependency_primary",
            finding="Blocked coordination references remain visible and do not trigger sequencing.",
            affected_reference_ids=blocked_ids,
            deterministic_order=20,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_2_coordination_diagnostic_stale_snapshot_visible",
            category=COORDINATION_DIAGNOSTIC_CONTINUITY_VISIBILITY,
            severity="warning",
            source_reference="v4_1_refresh_governance_snapshot",
            finding="Stale source snapshot evidence remains read-only and visible.",
            affected_reference_ids=stale_ids,
            deterministic_order=30,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_2_coordination_diagnostic_prohibited_state_visible",
            category=COORDINATION_DIAGNOSTIC_PROHIBITED_STATE,
            severity="prohibited",
            source_reference="v4_2_coordination_manifest_prohibited_visibility_primary",
            finding="Prohibited coordination states remain fail-visible and inactive.",
            affected_reference_ids=prohibited_ids + PROHIBITED_COORDINATION_CAPABILITIES,
            deterministic_order=40,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_2_coordination_diagnostic_lineage_continuity_visible",
            category=COORDINATION_DIAGNOSTIC_LINEAGE_CONTINUITY,
            severity="info",
            source_reference="v4_2_coordination_manifest_lineage_primary",
            finding="Lineage references preserve v4.1 governance ancestry without inference or repair.",
            affected_reference_ids=(
                "v4_2_coordination_lineage_v4_1_closeout",
                "v4_2_coordination_lineage_refresh_governance_stack",
            ),
            deterministic_order=50,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_2_coordination_diagnostic_non_execution_boundary_visible",
            category=COORDINATION_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            source_reference="v4_2_coordination_manifest_governance_primary",
            finding="Coordination manifest evidence remains non-authorizing and non-executing.",
            affected_reference_ids=PROHIBITED_COORDINATION_CAPABILITIES,
            deterministic_order=60,
        ),
    )


def default_coordination_governance_visibility(
    identity: CoordinationManifestIdentity | None = None,
) -> CoordinationGovernanceVisibility:
    source = identity or default_coordination_manifest_identity()
    return CoordinationGovernanceVisibility(
        governance_visibility_id=source.governance_reference,
        governance_references=(
            "v4_1_closeout_and_v4_2_readiness_governance",
            "v4_2_coordination_manifest_governance_boundary",
        ),
        explicit_limitations=EXPLICIT_COORDINATION_MANIFEST_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_COORDINATION_MANIFEST_PROHIBITIONS,
        deterministic_order=10,
    )


def default_coordination_manifest() -> CoordinationManifest:
    identity = default_coordination_manifest_identity()
    dependencies = default_coordination_dependency_references()
    return CoordinationManifest(
        identity=identity,
        metadata=default_coordination_manifest_metadata(identity),
        dependency_references=dependencies,
        lineage_references=default_coordination_lineage_references(identity),
        continuity_references=default_coordination_continuity_references(identity),
        diagnostics=default_coordination_diagnostics(dependencies),
        prohibited_state_visibility=default_coordination_prohibited_state_visibility(dependencies),
        unsupported_state_visibility=default_coordination_unsupported_state_visibility(dependencies),
        governance_visibility=default_coordination_governance_visibility(identity),
    )
