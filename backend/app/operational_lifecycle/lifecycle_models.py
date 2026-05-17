"""Deterministic v4.0 patch lifecycle foundation models.

The operational lifecycle layer is descriptive evidence only. It does not
execute patches, apply patches, deploy, schedule, route, dispatch, optimize,
recommend, rank, score, select, authorize, approve, remediate, repair, mutate
runtime state, or create callable operational flows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_0_PATCH_LIFECYCLE_PHASE_ID = "v4_0_patch_lifecycle_foundations"
V4_0_PATCH_LIFECYCLE_SCHEMA_VERSION = "v4_0.patch_lifecycle_foundations.1"
V4_0_PATCH_LIFECYCLE_STATUS_STABLE = "v4_0_patch_lifecycle_foundation_stable"
V4_0_PATCH_LIFECYCLE_STATUS_BLOCKED = "v4_0_patch_lifecycle_foundation_blocked"
V4_0_PATCH_LIFECYCLE_PURPOSE = "deterministic_operational_lifecycle_intelligence_only"
V4_0_PATCH_LIFECYCLE_GENERATED_AT = "2026-05-17T00:00:00+00:00"

PATCH_IDENTITY_SCOPE = "patch_lifecycle_identity_descriptive_only"
LIFECYCLE_STATE_SCOPE = "patch_lifecycle_state_descriptive_only"
LIFECYCLE_PROVENANCE_SCOPE = "patch_lifecycle_provenance_descriptive_only"
LIFECYCLE_LINEAGE_SCOPE = "patch_lifecycle_lineage_descriptive_only"
LIFECYCLE_VISIBILITY_SCOPE = "patch_lifecycle_visibility_descriptive_only"
PATCH_OPERATIONAL_METADATA_SCOPE = "patch_operational_metadata_descriptive_only"

LIFECYCLE_STATE_SUPPORTED = "supported"
LIFECYCLE_STATE_UNSUPPORTED = "unsupported"
LIFECYCLE_STATE_BLOCKED = "blocked"
LIFECYCLE_STATE_EXPERIMENTAL = "experimental"
LIFECYCLE_STATE_UNKNOWN = "unknown"
LIFECYCLE_STATE_DEPRECATED = "deprecated"
LIFECYCLE_STATE_PROHIBITED = "prohibited"
LIFECYCLE_STATES: tuple[str, ...] = (
    LIFECYCLE_STATE_SUPPORTED,
    LIFECYCLE_STATE_UNSUPPORTED,
    LIFECYCLE_STATE_BLOCKED,
    LIFECYCLE_STATE_EXPERIMENTAL,
    LIFECYCLE_STATE_UNKNOWN,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_PROHIBITED,
)
FAIL_VISIBLE_LIFECYCLE_STATES: tuple[str, ...] = (
    LIFECYCLE_STATE_UNSUPPORTED,
    LIFECYCLE_STATE_BLOCKED,
    LIFECYCLE_STATE_EXPERIMENTAL,
    LIFECYCLE_STATE_UNKNOWN,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_PROHIBITED,
)

LIFECYCLE_VISIBILITY_VISIBLE = "visible"
LIFECYCLE_VISIBILITY_FAIL_VISIBLE = "fail_visible"
LIFECYCLE_SEVERITY_INFO = "info"
LIFECYCLE_SEVERITY_WARNING = "warning"
LIFECYCLE_SEVERITY_BLOCKED = "blocked"
LIFECYCLE_SEVERITY_PROHIBITED = "prohibited"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class PatchIdentity:
    patch_version: str
    extraction_version: str
    schema_version: str
    lifecycle_generation: str
    lifecycle_timestamp: str
    provenance_reference: str
    lineage_reference: str
    trusted_bundle_reference: str
    refresh_chain_reference: str
    identity_scope: str = PATCH_IDENTITY_SCOPE
    lifecycle_purpose: str = V4_0_PATCH_LIFECYCLE_PURPOSE
    non_executable: bool = True
    lifecycle_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class LifecycleState:
    state_id: str
    state: str
    reason: str
    provenance_reference: str
    lineage_reference: str
    visibility_reference: str
    deterministic_order: int
    state_scope: str = LIFECYCLE_STATE_SCOPE
    visibility_status: str = LIFECYCLE_VISIBILITY_VISIBLE
    severity: str = LIFECYCLE_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    executable: bool = False
    transition_allowed: bool = False
    authorization_semantics_enabled: bool = False
    auto_transition_enabled: bool = False
    silently_corrected: bool = False
    fallback_applied: bool = False


@dataclass(frozen=True)
class LifecycleProvenanceRecord:
    provenance_reference_id: str
    source_patch_reference: str
    extraction_reference: str
    schema_reference: str
    trusted_bundle_reference: str
    refresh_chain_reference: str
    lineage_reference: str
    continuity_references: tuple[str, ...]
    source_evidence_references: tuple[str, ...]
    deterministic_hash_reference: str
    provenance_scope: str = LIFECYCLE_PROVENANCE_SCOPE
    provenance_preserved: bool = True
    inferred_provenance_allowed: bool = False
    no_inferred_provenance: bool = True
    hidden: bool = False
    fail_visible: bool = True
    descriptive_only: bool = True
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("continuity_references", "source_evidence_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LifecycleLineageRecord:
    lineage_reference_id: str
    prior_bundle_references: tuple[str, ...]
    successor_references: tuple[str, ...]
    continuity_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    provenance_continuity_references: tuple[str, ...]
    trusted_bundle_references: tuple[str, ...]
    refresh_chain_references: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    lineage_scope: str = LIFECYCLE_LINEAGE_SCOPE
    lineage_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    automatic_transition_enabled: bool = False
    execution_enabled: bool = False
    hidden_lineage_gap_correction_enabled: bool = False
    fail_visible_lineage_gap_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "prior_bundle_references",
            "successor_references",
            "continuity_references",
            "rollback_references",
            "provenance_continuity_references",
            "trusted_bundle_references",
            "refresh_chain_references",
            "fail_visible_lineage_gap_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LifecycleVisibilityRecord:
    visibility_reference_id: str
    lifecycle_state: str
    fail_visible_findings: tuple[str, ...]
    unsupported_state_visibility: tuple[str, ...]
    prohibited_state_visibility: tuple[str, ...]
    unknown_state_visibility: tuple[str, ...]
    integrity_warning_visibility: tuple[str, ...]
    lifecycle_continuity_visibility: tuple[str, ...]
    lineage_gap_visibility: tuple[str, ...]
    deterministic_order: int
    visibility_scope: str = LIFECYCLE_VISIBILITY_SCOPE
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden: bool = False
    remediation_enabled: bool = False
    automatic_resolution_enabled: bool = False
    corrective_behavior_enabled: bool = False
    silent_omission_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "fail_visible_findings",
            "unsupported_state_visibility",
            "prohibited_state_visibility",
            "unknown_state_visibility",
            "integrity_warning_visibility",
            "lifecycle_continuity_visibility",
            "lineage_gap_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PatchOperationalMetadata:
    metadata_reference_id: str
    patch_identity_reference: str
    operational_metadata_version: str
    deterministic_generated_at: str
    refresh_chain_reference: str
    lifecycle_state_references: tuple[str, ...]
    visibility_references: tuple[str, ...]
    metadata_scope: str = PATCH_OPERATIONAL_METADATA_SCOPE
    descriptive_only: bool = True
    execution_enabled: bool = False
    scheduling_enabled: bool = False
    routing_enabled: bool = False
    dispatch_enabled: bool = False
    mutation_enabled: bool = False
    automation_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lifecycle_state_references", "visibility_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PatchLifecycleFoundation:
    patch_identity: PatchIdentity
    lifecycle_states: tuple[LifecycleState, ...]
    provenance_records: tuple[LifecycleProvenanceRecord, ...]
    lineage_records: tuple[LifecycleLineageRecord, ...]
    visibility_records: tuple[LifecycleVisibilityRecord, ...]
    operational_metadata: PatchOperationalMetadata
    foundation_scope: str = V4_0_PATCH_LIFECYCLE_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    lifecycle_execution_enabled: bool = False
    patch_execution_enabled: bool = False
    patch_application_enabled: bool = False
    deployment_execution_enabled: bool = False
    scheduling_enabled: bool = False
    routing_enabled: bool = False
    dispatch_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_lifecycle_state_mutation_enabled: bool = False
    implicit_operational_state_transition_enabled: bool = False
    automatic_patch_transition_logic_enabled: bool = False
    callable_operational_flow_enabled: bool = False
    production_automation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "lifecycle_states",
            "provenance_records",
            "lineage_records",
            "visibility_records",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_patch_identity() -> PatchIdentity:
    return PatchIdentity(
        patch_version="v4.0.0-foundation",
        extraction_version="v3.9-closeout",
        schema_version=V4_0_PATCH_LIFECYCLE_SCHEMA_VERSION,
        lifecycle_generation="v4_0_phase_1_patch_lifecycle_foundations",
        lifecycle_timestamp=V4_0_PATCH_LIFECYCLE_GENERATED_AT,
        provenance_reference="v4_0_patch_lifecycle_provenance_primary",
        lineage_reference="v4_0_patch_lifecycle_lineage_primary",
        trusted_bundle_reference="v3_9_transition_continuity_certification_bundle",
        refresh_chain_reference="v4_0_patch_lifecycle_refresh_chain_primary",
    )


def default_lifecycle_states(identity: PatchIdentity | None = None) -> tuple[LifecycleState, ...]:
    source = identity or default_patch_identity()
    provenance = source.provenance_reference
    lineage = source.lineage_reference
    visibility = "v4_0_patch_lifecycle_visibility_primary"
    return (
        LifecycleState(
            state_id="v4_0_lifecycle_state_supported_identity",
            state=LIFECYCLE_STATE_SUPPORTED,
            reason="patch lifecycle identity can be modeled deterministically",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=1,
        ),
        LifecycleState(
            state_id="v4_0_lifecycle_state_unsupported_source",
            state=LIFECYCLE_STATE_UNSUPPORTED,
            reason="unsupported lifecycle state remains visible and descriptive",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=2,
            visibility_status=LIFECYCLE_VISIBILITY_FAIL_VISIBLE,
            severity=LIFECYCLE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        LifecycleState(
            state_id="v4_0_lifecycle_state_blocked_continuity_gap",
            state=LIFECYCLE_STATE_BLOCKED,
            reason="continuity gaps remain blocked evidence until a future phase supplies them",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=3,
            visibility_status=LIFECYCLE_VISIBILITY_FAIL_VISIBLE,
            severity=LIFECYCLE_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        LifecycleState(
            state_id="v4_0_lifecycle_state_experimental_refresh_chain",
            state=LIFECYCLE_STATE_EXPERIMENTAL,
            reason="refresh chain evidence is descriptive and not production-consuming",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=4,
            visibility_status=LIFECYCLE_VISIBILITY_FAIL_VISIBLE,
            severity=LIFECYCLE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        LifecycleState(
            state_id="v4_0_lifecycle_state_unknown_successor",
            state=LIFECYCLE_STATE_UNKNOWN,
            reason="future lifecycle successor state is explicitly unknown",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=5,
            visibility_status=LIFECYCLE_VISIBILITY_FAIL_VISIBLE,
            severity=LIFECYCLE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        LifecycleState(
            state_id="v4_0_lifecycle_state_deprecated_legacy_patch_context",
            state=LIFECYCLE_STATE_DEPRECATED,
            reason="legacy patch context is visible and not silently upgraded",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=6,
            visibility_status=LIFECYCLE_VISIBILITY_FAIL_VISIBLE,
            severity=LIFECYCLE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        LifecycleState(
            state_id="v4_0_lifecycle_state_prohibited_execution",
            state=LIFECYCLE_STATE_PROHIBITED,
            reason="execution-capable lifecycle behavior is prohibited",
            provenance_reference=provenance,
            lineage_reference=lineage,
            visibility_reference=visibility,
            deterministic_order=7,
            visibility_status=LIFECYCLE_VISIBILITY_FAIL_VISIBLE,
            severity=LIFECYCLE_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
    )


def default_lifecycle_provenance_record(identity: PatchIdentity | None = None) -> LifecycleProvenanceRecord:
    source = identity or default_patch_identity()
    return LifecycleProvenanceRecord(
        provenance_reference_id=source.provenance_reference,
        source_patch_reference=source.patch_version,
        extraction_reference=source.extraction_version,
        schema_reference=source.schema_version,
        trusted_bundle_reference=source.trusted_bundle_reference,
        refresh_chain_reference=source.refresh_chain_reference,
        lineage_reference=source.lineage_reference,
        continuity_references=(
            "v3_9_closeout_and_v4_readiness_report",
            "v3_9_transition_continuity_certification_report",
            "v4_0_patch_lifecycle_foundation_replay_reference",
            "v4_0_patch_lifecycle_foundation_rollback_reference",
        ),
        source_evidence_references=(
            "docs/generated/v3_9_closeout_and_v4_readiness_report.json",
            "docs/generated/v3_9_transition_continuity_certification_report.json",
            "docs/migration/V3_9_CLOSEOUT_AND_V4_READINESS.md",
        ),
        deterministic_hash_reference="v4_0_patch_lifecycle_provenance_hash",
    )


def default_lifecycle_lineage_record(identity: PatchIdentity | None = None) -> LifecycleLineageRecord:
    source = identity or default_patch_identity()
    return LifecycleLineageRecord(
        lineage_reference_id=source.lineage_reference,
        prior_bundle_references=(
            "v3_9_transition_continuity_certification_bundle",
            "v3_9_transition_integrity_enforcement_bundle",
            "v3_9_transition_intelligence_aggregation_bundle",
        ),
        successor_references=("v4_0_patch_lifecycle_foundations",),
        continuity_references=(
            "v4_0_patch_lifecycle_foundation_replay_reference",
            "v4_0_patch_lifecycle_foundation_rollback_reference",
            "v4_0_patch_lifecycle_provenance_continuity_reference",
        ),
        rollback_references=("v3_9_closeout_and_v4_readiness_report",),
        provenance_continuity_references=(source.provenance_reference,),
        trusted_bundle_references=(source.trusted_bundle_reference,),
        refresh_chain_references=(source.refresh_chain_reference,),
        deterministic_hash_reference="v4_0_patch_lifecycle_lineage_hash",
        deterministic_order=1,
        fail_visible_lineage_gap_ids=("v4_0_future_successor_lifecycle_not_declared",),
    )


def default_lifecycle_visibility_record(
    states: tuple[LifecycleState, ...] | None = None,
    lineage: LifecycleLineageRecord | None = None,
) -> LifecycleVisibilityRecord:
    lifecycle_states = states or default_lifecycle_states()
    lineage_record = lineage or default_lifecycle_lineage_record()
    unsupported = tuple(state.state_id for state in lifecycle_states if state.state == LIFECYCLE_STATE_UNSUPPORTED)
    prohibited = tuple(state.state_id for state in lifecycle_states if state.state == LIFECYCLE_STATE_PROHIBITED)
    unknown = tuple(state.state_id for state in lifecycle_states if state.state == LIFECYCLE_STATE_UNKNOWN)
    warnings = tuple(
        state.state_id
        for state in lifecycle_states
        if state.state in (LIFECYCLE_STATE_BLOCKED, LIFECYCLE_STATE_EXPERIMENTAL, LIFECYCLE_STATE_DEPRECATED)
    )
    fail_visible = tuple(state.state_id for state in lifecycle_states if state.fail_visible)
    continuity_visibility = tuple(lineage_record.continuity_references) + tuple(lineage_record.fail_visible_lineage_gap_ids)
    return LifecycleVisibilityRecord(
        visibility_reference_id="v4_0_patch_lifecycle_visibility_primary",
        lifecycle_state="v4_0_patch_lifecycle_visibility_descriptive_only",
        fail_visible_findings=fail_visible + tuple(lineage_record.fail_visible_lineage_gap_ids),
        unsupported_state_visibility=unsupported,
        prohibited_state_visibility=prohibited,
        unknown_state_visibility=unknown,
        integrity_warning_visibility=warnings,
        lifecycle_continuity_visibility=continuity_visibility,
        lineage_gap_visibility=lineage_record.fail_visible_lineage_gap_ids,
        deterministic_order=1,
    )


def default_patch_operational_metadata(
    identity: PatchIdentity | None = None,
    states: tuple[LifecycleState, ...] | None = None,
    visibility: LifecycleVisibilityRecord | None = None,
) -> PatchOperationalMetadata:
    source = identity or default_patch_identity()
    lifecycle_states = states or default_lifecycle_states(source)
    visibility_record = visibility or default_lifecycle_visibility_record(lifecycle_states)
    return PatchOperationalMetadata(
        metadata_reference_id="v4_0_patch_operational_metadata_primary",
        patch_identity_reference=source.patch_version,
        operational_metadata_version="v4_0_patch_operational_metadata.1",
        deterministic_generated_at=V4_0_PATCH_LIFECYCLE_GENERATED_AT,
        refresh_chain_reference=source.refresh_chain_reference,
        lifecycle_state_references=tuple(state.state_id for state in lifecycle_states),
        visibility_references=(visibility_record.visibility_reference_id,),
    )


def default_patch_lifecycle_foundation() -> PatchLifecycleFoundation:
    identity = default_patch_identity()
    states = default_lifecycle_states(identity)
    provenance = default_lifecycle_provenance_record(identity)
    lineage = default_lifecycle_lineage_record(identity)
    visibility = default_lifecycle_visibility_record(states, lineage)
    metadata = default_patch_operational_metadata(identity, states, visibility)
    return PatchLifecycleFoundation(
        patch_identity=identity,
        lifecycle_states=states,
        provenance_records=(provenance,),
        lineage_records=(lineage,),
        visibility_records=(visibility,),
        operational_metadata=metadata,
    )
