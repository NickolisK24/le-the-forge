"""Deterministic v4.3 orchestration manifest governance models.

Orchestration manifests are descriptive governance evidence only. They do not
execute, route, schedule, sequence, resolve dependencies, remediate, repair,
infer, authorize, approve readiness, integrate with planners, consume
production state, roll back state, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_3_ORCHESTRATION_MANIFEST_PHASE_ID = "v4_3_orchestration_manifest_foundations"
V4_3_ORCHESTRATION_MANIFEST_SCHEMA_VERSION = (
    "v4_3.governance_safe_orchestration_manifest_foundations.1"
)
V4_3_ORCHESTRATION_MANIFEST_REPORT_SCHEMA_VERSION = (
    "v4_3.governance_safe_orchestration_manifest_foundations_report.1"
)
V4_3_ORCHESTRATION_MANIFEST_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_MANIFEST_STATUS_STABLE = "v4_3_orchestration_manifest_foundation_stable"
V4_3_ORCHESTRATION_MANIFEST_STATUS_BLOCKED = "v4_3_orchestration_manifest_foundation_blocked"
V4_3_ORCHESTRATION_MANIFEST_PURPOSE = (
    "deterministic_governance_safe_orchestration_modeling_only"
)

ORCHESTRATION_STATE_SUPPORTED = "supported"
ORCHESTRATION_STATE_UNSUPPORTED = "unsupported"
ORCHESTRATION_STATE_BLOCKED = "blocked"
ORCHESTRATION_STATE_PROHIBITED = "prohibited"
ORCHESTRATION_STATE_MISSING_METADATA = "missing_metadata"
ORCHESTRATION_STATE_CONFLICTING_METADATA = "conflicting_metadata"
ORCHESTRATION_STATE_STALE_METADATA = "stale_metadata"
ORCHESTRATION_STATE_UNKNOWN = "unknown"
ORCHESTRATION_STATES: tuple[str, ...] = (
    ORCHESTRATION_STATE_SUPPORTED,
    ORCHESTRATION_STATE_UNSUPPORTED,
    ORCHESTRATION_STATE_BLOCKED,
    ORCHESTRATION_STATE_PROHIBITED,
    ORCHESTRATION_STATE_MISSING_METADATA,
    ORCHESTRATION_STATE_CONFLICTING_METADATA,
    ORCHESTRATION_STATE_STALE_METADATA,
    ORCHESTRATION_STATE_UNKNOWN,
)
FAIL_VISIBLE_ORCHESTRATION_STATES: tuple[str, ...] = (
    ORCHESTRATION_STATE_UNSUPPORTED,
    ORCHESTRATION_STATE_BLOCKED,
    ORCHESTRATION_STATE_PROHIBITED,
    ORCHESTRATION_STATE_MISSING_METADATA,
    ORCHESTRATION_STATE_CONFLICTING_METADATA,
    ORCHESTRATION_STATE_STALE_METADATA,
    ORCHESTRATION_STATE_UNKNOWN,
)

ORCHESTRATION_DIAGNOSTIC_UNSUPPORTED_CAPABILITY = "unsupported_capability_visibility"
ORCHESTRATION_DIAGNOSTIC_PROHIBITED_CAPABILITY = "prohibited_capability_visibility"
ORCHESTRATION_DIAGNOSTIC_BLOCKED_STATE = "blocked_state_visibility"
ORCHESTRATION_DIAGNOSTIC_MISSING_METADATA = "missing_metadata_visibility"
ORCHESTRATION_DIAGNOSTIC_CONFLICTING_METADATA = "conflicting_metadata_visibility"
ORCHESTRATION_DIAGNOSTIC_STALE_METADATA = "stale_metadata_visibility"
ORCHESTRATION_DIAGNOSTIC_EXPLAINABILITY = "explainability_visibility"
ORCHESTRATION_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"
ORCHESTRATION_DIAGNOSTIC_GOVERNANCE_BOUNDARY = "governance_boundary_visibility"

PROHIBITED_ORCHESTRATION_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "runtime_execution",
    "routing_execution",
    "scheduling_execution",
    "sequencing_execution",
    "dependency_resolution",
    "orchestration_remediation",
    "orchestration_repair",
    "orchestration_inference",
    "orchestration_authorization",
    "readiness_approval",
    "planner_integration",
    "production_consumption",
    "automatic_correction",
    "automatic_rollback",
    "runtime_mutation",
    "operational_state_mutation",
    "recommendation_systems",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_ORCHESTRATION_MANIFEST_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 1 creates deterministic governance-safe orchestration manifest modeling only.",
    "v4.3 Phase 1 does not enable orchestration execution.",
    "v4.3 Phase 1 does not enable runtime execution.",
    "v4.3 Phase 1 does not enable routing execution.",
    "v4.3 Phase 1 does not enable scheduling execution.",
    "v4.3 Phase 1 does not enable sequencing execution.",
    "v4.3 Phase 1 does not enable dependency resolution.",
    "v4.3 Phase 1 does not enable orchestration remediation or repair.",
    "v4.3 Phase 1 does not enable orchestration inference.",
    "v4.3 Phase 1 does not enable orchestration authorization or readiness approval.",
    "v4.3 Phase 1 does not enable planner integration.",
    "v4.3 Phase 1 does not enable production consumption.",
    "v4.3 Phase 1 does not enable automatic correction or automatic rollback.",
    "v4.3 Phase 1 does not enable runtime or operational state mutation.",
    "v4.3 Phase 1 does not enable recommendation, ranking, scoring, or selection.",
)

EXPLICIT_ORCHESTRATION_MANIFEST_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration execution exists.",
    "No runtime execution exists.",
    "No routing execution exists.",
    "No scheduling execution exists.",
    "No sequencing execution exists.",
    "No dependency resolution exists.",
    "No orchestration remediation exists.",
    "No orchestration repair exists.",
    "No orchestration inference exists.",
    "No orchestration authorization exists.",
    "No readiness approval exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No automatic correction exists.",
    "No automatic rollback exists.",
    "No runtime mutation exists.",
    "No operational state mutation exists.",
    "No recommendation, ranking, scoring, or selection behavior exists.",
    "No hidden orchestration behavior exists.",
    "No implicit execution pathway exists.",
    "No orchestration engine exists.",
    "No orchestration state machine executes.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class OrchestrationManifestIdentity:
    manifest_id: str
    orchestration_domain_id: str
    manifest_version: str
    schema_version: str
    generated_at: str
    source_readiness_reference: str
    provenance_reference: str
    lineage_reference: str
    explainability_reference: str
    diagnostics_reference: str
    replay_reference: str
    rollback_reference: str
    governance_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_MANIFEST_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationManifestMetadata:
    metadata_id: str
    phase_id: str
    classification: str
    source_phase_reference: str
    source_report_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_MANIFEST_PURPOSE
    deterministic: bool = True
    governance_first: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    explainability_continuity_preserved: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    non_remediating: bool = True
    non_executing: bool = True
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_report_references", "evidence_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationCapabilityVisibility:
    capability_id: str
    capability_name: str
    capability_classification: str
    visibility_state: str
    governance_boundary_reference: str
    diagnostics_reference: str
    deterministic_order: int
    blocked_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    prohibited_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    missing_metadata_visibility: tuple[str, ...] = ()
    conflicting_metadata_visibility: tuple[str, ...] = ()
    capability_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    capability_available: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_remediation_enabled: bool = False
    orchestration_repair_enabled: bool = False
    orchestration_inference_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_reason_visibility",
            "unsupported_reason_visibility",
            "prohibited_reason_visibility",
            "stale_reason_visibility",
            "missing_metadata_visibility",
            "conflicting_metadata_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationBoundaryVisibility:
    boundary_id: str
    boundary_type: str
    boundary_state: str
    boundary_summary: str
    guarantee_references: tuple[str, ...]
    prohibited_capabilities: tuple[str, ...]
    deterministic_order: int
    boundary_visible: bool = True
    non_execution_boundary: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("guarantee_references", "prohibited_capabilities"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationContinuityMetadata:
    continuity_id: str
    continuity_type: str
    continuity_state: str
    evidence_references: tuple[str, ...]
    replay_reference: str
    rollback_reference: str
    provenance_reference: str
    lineage_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    explainability_continuity_preserved: bool = True
    continuity_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class OrchestrationManifestDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    source_reference: str
    finding: str
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_remediation_enabled: bool = False
    orchestration_repair_enabled: bool = False
    orchestration_inference_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_reference_ids")


@dataclass(frozen=True)
class OrchestrationProhibitedStateVisibility:
    prohibited_visibility_id: str
    prohibited_states: tuple[str, ...]
    prohibited_capabilities: tuple[str, ...]
    blocked_reason_visibility: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("prohibited_states", "prohibited_capabilities", "blocked_reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationUnsupportedStateVisibility:
    unsupported_visibility_id: str
    unsupported_states: tuple[str, ...]
    blocked_states: tuple[str, ...]
    stale_metadata_states: tuple[str, ...]
    missing_metadata_states: tuple[str, ...]
    conflicting_metadata_states: tuple[str, ...]
    unknown_states: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_states",
            "blocked_states",
            "stale_metadata_states",
            "missing_metadata_states",
            "conflicting_metadata_states",
            "unknown_states",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationExplainabilitySummary:
    explanation_id: str
    category: str
    summary: str
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    deterministic: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    remediation_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_reference_ids")


@dataclass(frozen=True)
class OrchestrationManifest:
    identity: OrchestrationManifestIdentity
    metadata: OrchestrationManifestMetadata
    capability_visibility: tuple[OrchestrationCapabilityVisibility, ...]
    boundary_visibility: tuple[OrchestrationBoundaryVisibility, ...]
    continuity_metadata: tuple[OrchestrationContinuityMetadata, ...]
    diagnostics: tuple[OrchestrationManifestDiagnostic, ...]
    explainability_summaries: tuple[OrchestrationExplainabilitySummary, ...]
    prohibited_state_visibility: OrchestrationProhibitedStateVisibility
    unsupported_state_visibility: OrchestrationUnsupportedStateVisibility
    manifest_classification: str = "governance_safe_orchestration_modeling_descriptive_only"
    non_executable: bool = True
    descriptive_only: bool = True
    governance_safe: bool = True
    execution_authorized: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_remediation_enabled: bool = False
    orchestration_repair_enabled: bool = False
    orchestration_inference_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    orchestration_engine_enabled: bool = False
    state_machine_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "capability_visibility",
            "boundary_visibility",
            "continuity_metadata",
            "diagnostics",
            "explainability_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_orchestration_manifest_identity() -> OrchestrationManifestIdentity:
    return OrchestrationManifestIdentity(
        manifest_id="v4_3_orchestration_manifest_primary",
        orchestration_domain_id="v4_3_phase_1_governance_safe_orchestration_manifest_foundations",
        manifest_version="v4.3.0-phase-1",
        schema_version=V4_3_ORCHESTRATION_MANIFEST_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_MANIFEST_GENERATED_AT,
        source_readiness_reference="v4_2_closeout_and_v4_3_readiness_report",
        provenance_reference="v4_3_orchestration_manifest_provenance_primary",
        lineage_reference="v4_3_orchestration_manifest_lineage_primary",
        explainability_reference="v4_3_orchestration_manifest_explainability_primary",
        diagnostics_reference="v4_3_orchestration_manifest_diagnostics_primary",
        replay_reference="v4_3_orchestration_manifest_replay_primary",
        rollback_reference="v4_3_orchestration_manifest_rollback_primary",
        governance_reference="v4_3_orchestration_manifest_governance_primary",
    )


def default_orchestration_manifest_metadata(
    identity: OrchestrationManifestIdentity | None = None,
) -> OrchestrationManifestMetadata:
    source = identity or default_orchestration_manifest_identity()
    return OrchestrationManifestMetadata(
        metadata_id="v4_3_orchestration_manifest_metadata_primary",
        phase_id=V4_3_ORCHESTRATION_MANIFEST_PHASE_ID,
        classification="descriptive_only_orchestration_governance_manifest",
        source_phase_reference="v4_2_closeout_and_v4_3_readiness",
        source_report_references=(
            "docs/generated/v4_2_closeout_and_v4_3_readiness_report.json",
            "docs/migration/V4_2_CLOSEOUT_AND_V4_3_READINESS.md",
        ),
        evidence_references=(
            source.provenance_reference,
            source.lineage_reference,
            source.explainability_reference,
            source.diagnostics_reference,
            source.replay_reference,
            source.rollback_reference,
            source.governance_reference,
        ),
        deterministic_order=10,
    )


def default_orchestration_capability_visibility() -> tuple[OrchestrationCapabilityVisibility, ...]:
    return (
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_manifest_identity",
            capability_name="manifest_identity_modeling",
            capability_classification="descriptive_modeling",
            visibility_state=ORCHESTRATION_STATE_SUPPORTED,
            governance_boundary_reference="v4_3_orchestration_boundary_non_execution",
            diagnostics_reference="v4_3_orchestration_diagnostic_non_execution_boundary_visible",
            deterministic_order=10,
            capability_available=True,
        ),
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_future_provider_contracts",
            capability_name="future_orchestration_provider_contracts",
            capability_classification="unsupported_future_contract",
            visibility_state=ORCHESTRATION_STATE_UNSUPPORTED,
            governance_boundary_reference="v4_3_orchestration_boundary_unsupported_capabilities",
            diagnostics_reference="v4_3_orchestration_diagnostic_unsupported_capability_visible",
            deterministic_order=20,
            unsupported_reason_visibility=(
                "future orchestration provider contracts are not modeled as executable contracts",
            ),
        ),
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_operational_activation",
            capability_name="operational_orchestration_activation",
            capability_classification="blocked_operational_state",
            visibility_state=ORCHESTRATION_STATE_BLOCKED,
            governance_boundary_reference="v4_3_orchestration_boundary_operational_activation",
            diagnostics_reference="v4_3_orchestration_diagnostic_blocked_state_visible",
            deterministic_order=30,
            blocked_reason_visibility=(
                "operational activation is blocked because v4.3 Phase 1 is descriptive-only",
            ),
        ),
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_prior_coordination_snapshot",
            capability_name="prior_v4_2_coordination_snapshot",
            capability_classification="stale_metadata_visibility",
            visibility_state=ORCHESTRATION_STATE_STALE_METADATA,
            governance_boundary_reference="v4_3_orchestration_boundary_metadata_visibility",
            diagnostics_reference="v4_3_orchestration_diagnostic_stale_metadata_visible",
            deterministic_order=40,
            stale_reason_visibility=(
                "v4.2 coordination evidence is read-only ancestry and not a live orchestration source",
            ),
        ),
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_runtime_execution_policy",
            capability_name="runtime_execution_policy_metadata",
            capability_classification="missing_metadata_visibility",
            visibility_state=ORCHESTRATION_STATE_MISSING_METADATA,
            governance_boundary_reference="v4_3_orchestration_boundary_metadata_visibility",
            diagnostics_reference="v4_3_orchestration_diagnostic_missing_metadata_visible",
            deterministic_order=50,
            missing_metadata_visibility=(
                "runtime execution policy metadata is intentionally absent because execution is prohibited",
            ),
        ),
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_execution_authorization_conflict",
            capability_name="execution_authorization_metadata",
            capability_classification="conflicting_metadata_visibility",
            visibility_state=ORCHESTRATION_STATE_CONFLICTING_METADATA,
            governance_boundary_reference="v4_3_orchestration_boundary_metadata_visibility",
            diagnostics_reference="v4_3_orchestration_diagnostic_conflicting_metadata_visible",
            deterministic_order=60,
            conflicting_metadata_visibility=(
                "any execution authorization metadata conflicts with non-execution governance",
            ),
        ),
        OrchestrationCapabilityVisibility(
            capability_id="v4_3_orchestration_capability_runtime_orchestration_execution",
            capability_name="runtime_orchestration_execution",
            capability_classification="prohibited_operational_capability",
            visibility_state=ORCHESTRATION_STATE_PROHIBITED,
            governance_boundary_reference="v4_3_orchestration_boundary_prohibited_capabilities",
            diagnostics_reference="v4_3_orchestration_diagnostic_prohibited_capability_visible",
            deterministic_order=70,
            prohibited_reason_visibility=("runtime orchestration execution is prohibited",),
        ),
    )


def default_orchestration_boundary_visibility() -> tuple[OrchestrationBoundaryVisibility, ...]:
    return (
        OrchestrationBoundaryVisibility(
            boundary_id="v4_3_orchestration_boundary_non_execution",
            boundary_type="non_execution_guarantee",
            boundary_state=ORCHESTRATION_STATE_SUPPORTED,
            boundary_summary="Orchestration manifests are non-executable descriptive evidence.",
            guarantee_references=(
                "orchestration_execution_disabled",
                "runtime_execution_disabled",
                "routing_execution_disabled",
                "scheduling_execution_disabled",
                "sequencing_execution_disabled",
            ),
            prohibited_capabilities=(
                "orchestration_execution",
                "runtime_execution",
                "routing_execution",
                "scheduling_execution",
                "sequencing_execution",
            ),
            deterministic_order=10,
        ),
        OrchestrationBoundaryVisibility(
            boundary_id="v4_3_orchestration_boundary_governance_controls",
            boundary_type="governance_boundary",
            boundary_state=ORCHESTRATION_STATE_SUPPORTED,
            boundary_summary="Governance evidence exposes boundaries without authorization or approval.",
            guarantee_references=(
                "orchestration_authorization_disabled",
                "readiness_approval_disabled",
                "planner_integration_disabled",
                "production_consumption_disabled",
            ),
            prohibited_capabilities=(
                "orchestration_authorization",
                "readiness_approval",
                "planner_integration",
                "production_consumption",
            ),
            deterministic_order=20,
        ),
        OrchestrationBoundaryVisibility(
            boundary_id="v4_3_orchestration_boundary_no_correction",
            boundary_type="no_remediation_boundary",
            boundary_state=ORCHESTRATION_STATE_SUPPORTED,
            boundary_summary="Diagnostics expose blocked states without repair, remediation, or rollback.",
            guarantee_references=(
                "dependency_resolution_disabled",
                "orchestration_remediation_disabled",
                "orchestration_repair_disabled",
                "automatic_correction_disabled",
                "automatic_rollback_disabled",
            ),
            prohibited_capabilities=(
                "dependency_resolution",
                "orchestration_remediation",
                "orchestration_repair",
                "automatic_correction",
                "automatic_rollback",
            ),
            deterministic_order=30,
        ),
    )


def default_orchestration_continuity_metadata(
    identity: OrchestrationManifestIdentity | None = None,
) -> tuple[OrchestrationContinuityMetadata, ...]:
    source = identity or default_orchestration_manifest_identity()
    return (
        OrchestrationContinuityMetadata(
            continuity_id="v4_3_orchestration_continuity_manifest_identity",
            continuity_type="manifest_identity_continuity",
            continuity_state=ORCHESTRATION_STATE_SUPPORTED,
            evidence_references=(
                source.provenance_reference,
                source.lineage_reference,
                "docs/generated/v4_2_closeout_and_v4_3_readiness_report.json",
            ),
            replay_reference=source.replay_reference,
            rollback_reference=source.rollback_reference,
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            deterministic_hash_reference="v4_3_orchestration_manifest_identity_continuity_hash",
            deterministic_order=10,
        ),
        OrchestrationContinuityMetadata(
            continuity_id="v4_3_orchestration_continuity_replay_safe",
            continuity_type="replay_safety",
            continuity_state=ORCHESTRATION_STATE_SUPPORTED,
            evidence_references=(
                "v4_3_orchestration_manifest_serialization_snapshot",
                "v4_3_orchestration_manifest_hash_snapshot",
            ),
            replay_reference=source.replay_reference,
            rollback_reference=source.rollback_reference,
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            deterministic_hash_reference="v4_3_orchestration_manifest_replay_continuity_hash",
            deterministic_order=20,
        ),
        OrchestrationContinuityMetadata(
            continuity_id="v4_3_orchestration_continuity_rollback_safe",
            continuity_type="rollback_safety",
            continuity_state=ORCHESTRATION_STATE_SUPPORTED,
            evidence_references=(
                "docs/generated/v4_2_closeout_and_v4_3_readiness_report.json",
                "v4_3_orchestration_governance_boundary_snapshot",
            ),
            replay_reference=source.replay_reference,
            rollback_reference=source.rollback_reference,
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            deterministic_hash_reference="v4_3_orchestration_manifest_rollback_continuity_hash",
            deterministic_order=30,
        ),
    )


def default_orchestration_prohibited_state_visibility(
    capabilities: tuple[OrchestrationCapabilityVisibility, ...] | None = None,
) -> OrchestrationProhibitedStateVisibility:
    capability_records = capabilities or default_orchestration_capability_visibility()
    prohibited_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_PROHIBITED
    )
    return OrchestrationProhibitedStateVisibility(
        prohibited_visibility_id="v4_3_orchestration_manifest_prohibited_visibility_primary",
        prohibited_states=prohibited_ids
        + tuple(f"v4_3_orchestration_capability_{capability}" for capability in PROHIBITED_ORCHESTRATION_CAPABILITIES),
        prohibited_capabilities=PROHIBITED_ORCHESTRATION_CAPABILITIES,
        blocked_reason_visibility=tuple(
            f"v4_3_prohibited_orchestration_capability_{capability}"
            for capability in PROHIBITED_ORCHESTRATION_CAPABILITIES
        ),
        deterministic_order=10,
    )


def default_orchestration_unsupported_state_visibility(
    capabilities: tuple[OrchestrationCapabilityVisibility, ...] | None = None,
) -> OrchestrationUnsupportedStateVisibility:
    capability_records = capabilities or default_orchestration_capability_visibility()
    return OrchestrationUnsupportedStateVisibility(
        unsupported_visibility_id="v4_3_orchestration_manifest_unsupported_visibility_primary",
        unsupported_states=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.visibility_state == ORCHESTRATION_STATE_UNSUPPORTED
        ),
        blocked_states=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.visibility_state == ORCHESTRATION_STATE_BLOCKED
        ),
        stale_metadata_states=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.visibility_state == ORCHESTRATION_STATE_STALE_METADATA
        ),
        missing_metadata_states=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.visibility_state == ORCHESTRATION_STATE_MISSING_METADATA
        ),
        conflicting_metadata_states=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.visibility_state == ORCHESTRATION_STATE_CONFLICTING_METADATA
        ),
        unknown_states=("v4_3_orchestration_future_manifest_consumer_unknown",),
        deterministic_order=10,
    )


def default_orchestration_diagnostics(
    capabilities: tuple[OrchestrationCapabilityVisibility, ...] | None = None,
) -> tuple[OrchestrationManifestDiagnostic, ...]:
    capability_records = capabilities or default_orchestration_capability_visibility()
    unsupported_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_BLOCKED
    )
    prohibited_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_PROHIBITED
    )
    stale_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_STALE_METADATA
    )
    missing_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_MISSING_METADATA
    )
    conflicting_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.visibility_state == ORCHESTRATION_STATE_CONFLICTING_METADATA
    )
    return (
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_unsupported_capability_visible",
            category=ORCHESTRATION_DIAGNOSTIC_UNSUPPORTED_CAPABILITY,
            severity="warning",
            source_reference="v4_3_orchestration_manifest_capability_visibility",
            finding="Unsupported orchestration capabilities remain visible and unavailable.",
            affected_reference_ids=unsupported_ids,
            deterministic_order=10,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_blocked_state_visible",
            category=ORCHESTRATION_DIAGNOSTIC_BLOCKED_STATE,
            severity="blocked",
            source_reference="v4_3_orchestration_manifest_capability_visibility",
            finding="Blocked orchestration states remain visible and do not trigger sequencing.",
            affected_reference_ids=blocked_ids,
            deterministic_order=20,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_prohibited_capability_visible",
            category=ORCHESTRATION_DIAGNOSTIC_PROHIBITED_CAPABILITY,
            severity="prohibited",
            source_reference="v4_3_orchestration_manifest_prohibited_visibility_primary",
            finding="Prohibited orchestration capabilities remain fail-visible and inactive.",
            affected_reference_ids=prohibited_ids + PROHIBITED_ORCHESTRATION_CAPABILITIES,
            deterministic_order=30,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_missing_metadata_visible",
            category=ORCHESTRATION_DIAGNOSTIC_MISSING_METADATA,
            severity="warning",
            source_reference="v4_3_orchestration_manifest_unsupported_visibility_primary",
            finding="Missing execution metadata remains visible because execution metadata is prohibited.",
            affected_reference_ids=missing_ids,
            deterministic_order=40,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_conflicting_metadata_visible",
            category=ORCHESTRATION_DIAGNOSTIC_CONFLICTING_METADATA,
            severity="blocked",
            source_reference="v4_3_orchestration_manifest_unsupported_visibility_primary",
            finding="Conflicting execution authorization metadata remains blocked and descriptive.",
            affected_reference_ids=conflicting_ids,
            deterministic_order=50,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_stale_metadata_visible",
            category=ORCHESTRATION_DIAGNOSTIC_STALE_METADATA,
            severity="warning",
            source_reference="v4_2_coordination_governance_snapshot",
            finding="Stale v4.2 coordination evidence remains read-only ancestry.",
            affected_reference_ids=stale_ids,
            deterministic_order=60,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_explainability_visible",
            category=ORCHESTRATION_DIAGNOSTIC_EXPLAINABILITY,
            severity="info",
            source_reference="v4_3_orchestration_manifest_explainability_primary",
            finding="Explainability summaries describe blocked, unsupported, and prohibited states deterministically.",
            affected_reference_ids=(
                "v4_3_orchestration_explainability_blocked",
                "v4_3_orchestration_explainability_unsupported",
                "v4_3_orchestration_explainability_prohibited",
            ),
            deterministic_order=70,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_non_execution_boundary_visible",
            category=ORCHESTRATION_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            source_reference="v4_3_orchestration_manifest_governance_primary",
            finding="Orchestration manifests remain non-authorizing and non-executing.",
            affected_reference_ids=PROHIBITED_ORCHESTRATION_CAPABILITIES,
            deterministic_order=80,
        ),
        OrchestrationManifestDiagnostic(
            diagnostic_id="v4_3_orchestration_diagnostic_governance_boundary_visible",
            category=ORCHESTRATION_DIAGNOSTIC_GOVERNANCE_BOUNDARY,
            severity="info",
            source_reference="v4_3_orchestration_manifest_governance_primary",
            finding="Governance boundaries are explicit and do not create operational behavior.",
            affected_reference_ids=(
                "v4_3_orchestration_boundary_non_execution",
                "v4_3_orchestration_boundary_governance_controls",
                "v4_3_orchestration_boundary_no_correction",
            ),
            deterministic_order=90,
        ),
    )


def default_orchestration_explainability_summaries() -> tuple[OrchestrationExplainabilitySummary, ...]:
    return (
        OrchestrationExplainabilitySummary(
            explanation_id="v4_3_orchestration_explainability_blocked",
            category="blocked_state",
            summary=(
                "Operational orchestration activation is blocked because Phase 1 only models "
                "manifest governance evidence."
            ),
            affected_reference_ids=("v4_3_orchestration_capability_operational_activation",),
            deterministic_order=10,
        ),
        OrchestrationExplainabilitySummary(
            explanation_id="v4_3_orchestration_explainability_unsupported",
            category="unsupported_state",
            summary=(
                "Future provider contracts are unsupported because no executable orchestration "
                "contract exists in this phase."
            ),
            affected_reference_ids=("v4_3_orchestration_capability_future_provider_contracts",),
            deterministic_order=20,
        ),
        OrchestrationExplainabilitySummary(
            explanation_id="v4_3_orchestration_explainability_prohibited",
            category="prohibited_state",
            summary="Runtime orchestration execution is prohibited by the non-execution governance boundary.",
            affected_reference_ids=("v4_3_orchestration_capability_runtime_orchestration_execution",),
            deterministic_order=30,
        ),
        OrchestrationExplainabilitySummary(
            explanation_id="v4_3_orchestration_explainability_capabilities_unavailable",
            category="capability_unavailable",
            summary=(
                "Routing, scheduling, sequencing, dependency resolution, remediation, repair, "
                "authorization, readiness approval, planner integration, production consumption, "
                "recommendation, ranking, scoring, and selection are unavailable."
            ),
            affected_reference_ids=PROHIBITED_ORCHESTRATION_CAPABILITIES,
            deterministic_order=40,
        ),
        OrchestrationExplainabilitySummary(
            explanation_id="v4_3_orchestration_explainability_governance_boundary",
            category="governance_boundary",
            summary=(
                "Governance boundaries exist to keep orchestration evidence replay-safe, "
                "rollback-safe, provenance-continuous, lineage-continuous, and non-executable."
            ),
            affected_reference_ids=(
                "v4_3_orchestration_boundary_non_execution",
                "v4_3_orchestration_boundary_governance_controls",
                "v4_3_orchestration_boundary_no_correction",
            ),
            deterministic_order=50,
        ),
    )


def default_orchestration_manifest() -> OrchestrationManifest:
    identity = default_orchestration_manifest_identity()
    capabilities = default_orchestration_capability_visibility()
    return OrchestrationManifest(
        identity=identity,
        metadata=default_orchestration_manifest_metadata(identity),
        capability_visibility=capabilities,
        boundary_visibility=default_orchestration_boundary_visibility(),
        continuity_metadata=default_orchestration_continuity_metadata(identity),
        diagnostics=default_orchestration_diagnostics(capabilities),
        explainability_summaries=default_orchestration_explainability_summaries(),
        prohibited_state_visibility=default_orchestration_prohibited_state_visibility(capabilities),
        unsupported_state_visibility=default_orchestration_unsupported_state_visibility(capabilities),
    )
