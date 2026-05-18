"""Deterministic v4.3 orchestration transition visibility models.

Transition visibility is descriptive governance evidence only. It models
theoretical orchestration transitions, governance-constrained transition
relationships, and fail-visible blocked, prohibited, unsupported, stale, and
conflicting transition states without transition execution, state progression,
activation, routing, traversal, scheduling, dispatch, planner behavior, or
production consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .orchestration_capability_hashing import hash_orchestration_capability_visibility
from .orchestration_capability_models import default_orchestration_capability_visibility
from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import default_orchestration_manifest
from .orchestration_policy_hashing import hash_orchestration_policy_visibility
from .orchestration_policy_models import default_orchestration_policy_visibility
from .orchestration_topology_hashing import hash_orchestration_topology
from .orchestration_topology_models import default_orchestration_topology


V4_3_ORCHESTRATION_TRANSITION_PHASE_ID = "v4_3_orchestration_transition_visibility"
V4_3_ORCHESTRATION_TRANSITION_SCHEMA_VERSION = "v4_3.orchestration_transition_visibility.1"
V4_3_ORCHESTRATION_TRANSITION_REPORT_SCHEMA_VERSION = (
    "v4_3.orchestration_transition_visibility_report.1"
)
V4_3_ORCHESTRATION_TRANSITION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_TRANSITION_STATUS_STABLE = (
    "v4_3_orchestration_transition_visibility_stable"
)
V4_3_ORCHESTRATION_TRANSITION_STATUS_BLOCKED = (
    "v4_3_orchestration_transition_visibility_blocked"
)
V4_3_ORCHESTRATION_TRANSITION_PURPOSE = (
    "deterministic_orchestration_transition_governance_modeling_only"
)

TRANSITION_STATE_SUPPORTED = "supported"
TRANSITION_STATE_PROHIBITED = "prohibited"
TRANSITION_STATE_UNSUPPORTED = "unsupported"
TRANSITION_STATE_BLOCKED = "blocked"
TRANSITION_STATE_STALE = "stale"
TRANSITION_STATE_CONFLICTING = "conflicting"
TRANSITION_STATE_UNKNOWN = "unknown"
TRANSITION_STATES: tuple[str, ...] = (
    TRANSITION_STATE_SUPPORTED,
    TRANSITION_STATE_PROHIBITED,
    TRANSITION_STATE_UNSUPPORTED,
    TRANSITION_STATE_BLOCKED,
    TRANSITION_STATE_STALE,
    TRANSITION_STATE_CONFLICTING,
    TRANSITION_STATE_UNKNOWN,
)
FAIL_VISIBLE_TRANSITION_STATES: tuple[str, ...] = (
    TRANSITION_STATE_PROHIBITED,
    TRANSITION_STATE_UNSUPPORTED,
    TRANSITION_STATE_BLOCKED,
    TRANSITION_STATE_STALE,
    TRANSITION_STATE_CONFLICTING,
    TRANSITION_STATE_UNKNOWN,
)

TRANSITION_RELATIONSHIP_TO_POLICY = "transition_to_policy"
TRANSITION_RELATIONSHIP_TO_CAPABILITY = "transition_to_capability"
TRANSITION_RELATIONSHIP_TO_BOUNDARY = "transition_to_boundary"
TRANSITION_RELATIONSHIP_TO_TOPOLOGY = "transition_to_topology"
TRANSITION_RELATIONSHIP_TO_MANIFEST = "transition_to_manifest"
TRANSITION_RELATIONSHIP_TYPES: tuple[str, ...] = (
    TRANSITION_RELATIONSHIP_TO_POLICY,
    TRANSITION_RELATIONSHIP_TO_CAPABILITY,
    TRANSITION_RELATIONSHIP_TO_BOUNDARY,
    TRANSITION_RELATIONSHIP_TO_TOPOLOGY,
    TRANSITION_RELATIONSHIP_TO_MANIFEST,
)

TRANSITION_TARGET_POLICY = "policy"
TRANSITION_TARGET_CAPABILITY = "capability"
TRANSITION_TARGET_BOUNDARY = "boundary"
TRANSITION_TARGET_TOPOLOGY = "topology"
TRANSITION_TARGET_MANIFEST = "manifest"
TRANSITION_TARGET_TYPES: tuple[str, ...] = (
    TRANSITION_TARGET_POLICY,
    TRANSITION_TARGET_CAPABILITY,
    TRANSITION_TARGET_BOUNDARY,
    TRANSITION_TARGET_TOPOLOGY,
    TRANSITION_TARGET_MANIFEST,
)
TRANSITION_RELATIONSHIP_TARGET_TYPES: dict[str, str] = {
    TRANSITION_RELATIONSHIP_TO_POLICY: TRANSITION_TARGET_POLICY,
    TRANSITION_RELATIONSHIP_TO_CAPABILITY: TRANSITION_TARGET_CAPABILITY,
    TRANSITION_RELATIONSHIP_TO_BOUNDARY: TRANSITION_TARGET_BOUNDARY,
    TRANSITION_RELATIONSHIP_TO_TOPOLOGY: TRANSITION_TARGET_TOPOLOGY,
    TRANSITION_RELATIONSHIP_TO_MANIFEST: TRANSITION_TARGET_MANIFEST,
}

TRANSITION_DIAGNOSTIC_IDENTITY = "transition_identity_visibility"
TRANSITION_DIAGNOSTIC_DUPLICATE = "duplicate_transition_visibility"
TRANSITION_DIAGNOSTIC_STATE = "transition_state_visibility"
TRANSITION_DIAGNOSTIC_RELATIONSHIP = "transition_relationship_visibility"
TRANSITION_DIAGNOSTIC_PROHIBITED = "prohibited_transition_visibility"
TRANSITION_DIAGNOSTIC_UNSUPPORTED = "unsupported_transition_visibility"
TRANSITION_DIAGNOSTIC_BLOCKED = "blocked_transition_visibility"
TRANSITION_DIAGNOSTIC_STALE = "stale_transition_visibility"
TRANSITION_DIAGNOSTIC_CONFLICTING = "conflicting_transition_visibility"
TRANSITION_DIAGNOSTIC_METADATA = "metadata_visibility"
TRANSITION_DIAGNOSTIC_EXPLAINABILITY = "explainability_visibility"
TRANSITION_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"
TRANSITION_DIAGNOSTIC_NON_ACTIVATION = "non_activation_boundary_visibility"

PROHIBITED_TRANSITION_CLASSIFICATIONS: tuple[str, ...] = (
    "orchestration_execution",
    "transition_execution",
    "state_machine_execution",
    "runtime_execution",
    "orchestration_activation",
    "routing_execution",
    "traversal_execution",
    "scheduling_execution",
    "sequencing_execution",
    "dependency_resolution",
    "transition_authorization",
    "readiness_approval",
    "transition_dispatch",
    "operational_coordination",
    "orchestration_remediation",
    "orchestration_repair",
    "orchestration_inference",
    "orchestration_recommendations",
    "orchestration_ranking",
    "orchestration_scoring",
    "orchestration_selection",
    "orchestration_optimization",
    "orchestration_planning_engines",
    "orchestration_decision_engines",
    "planner_integration",
    "production_consumption",
    "runtime_mutation",
    "operational_mutation",
    "hidden_transition_pathways",
    "implicit_operational_authorization",
    "transition_engine",
    "orchestration_runtime",
    "executable_state_machine",
    "orchestration_dispatcher",
)
UNSUPPORTED_TRANSITION_CLASSIFICATIONS: tuple[str, ...] = (
    "future_transition_runtime_contract",
    "future_state_progression_surface",
    "future_planner_transition_consumer",
)

EXPLICIT_ORCHESTRATION_TRANSITION_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 5 creates deterministic orchestration transition governance modeling only.",
    "v4.3 Phase 5 makes theoretical transition relationships visible before execution.",
    "v4.3 Phase 5 does not enable orchestration execution.",
    "v4.3 Phase 5 does not enable transition execution.",
    "v4.3 Phase 5 does not enable state machine execution.",
    "v4.3 Phase 5 does not enable runtime execution or orchestration activation.",
    "v4.3 Phase 5 does not enable routing, traversal, scheduling, sequencing, or dependency resolution.",
    "v4.3 Phase 5 does not enable authorization, readiness approval, dispatch, or operational coordination.",
    "v4.3 Phase 5 does not enable remediation, repair, inference, recommendation, ranking, scoring, selection, or optimization.",
    "v4.3 Phase 5 does not enable planner integration, production consumption, runtime mutation, or operational mutation.",
)

EXPLICIT_ORCHESTRATION_TRANSITION_PROHIBITIONS: tuple[str, ...] = (
    "No transition engine may exist.",
    "No orchestration runtime may exist.",
    "No executable state machine may exist.",
    "No orchestration dispatcher may exist.",
    "No orchestration execution exists.",
    "No transition execution exists.",
    "No state progression exists.",
    "No orchestration activation exists.",
    "No routing execution exists.",
    "No traversal execution exists.",
    "No scheduling execution exists.",
    "No sequencing execution exists.",
    "No dependency resolution exists.",
    "No transition authorization exists.",
    "No readiness approval exists.",
    "No transition dispatch exists.",
    "No operational coordination exists.",
    "No orchestration remediation exists.",
    "No orchestration repair exists.",
    "No orchestration inference exists.",
    "No orchestration recommendation exists.",
    "No orchestration ranking exists.",
    "No orchestration scoring exists.",
    "No orchestration selection exists.",
    "No orchestration optimization exists.",
    "No orchestration planning engine exists.",
    "No orchestration decision engine exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
    "No hidden transition pathway exists.",
    "No implicit operational authorization exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionVisibilityIdentity:
    transition_set_id: str
    transition_set_version: str
    transition_set_classification: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_topology_reference: str
    source_topology_hash_reference: str
    source_capability_reference: str
    source_capability_hash_reference: str
    source_policy_reference: str
    source_policy_hash_reference: str
    schema_version: str
    generated_at: str
    governance_reference: str
    transition_boundary_reference: str
    transition_policy_reference: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    diagnostics_reference: str
    explainability_reference: str
    non_execution_reference: str
    non_activation_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_TRANSITION_PURPOSE
    non_executable: bool = True
    non_activating: bool = True
    descriptive_only: bool = True
    transition_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    state_progression_enabled: bool = False
    runtime_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class TransitionVisibilityMetadata:
    metadata_id: str
    phase_id: str
    transition_set_classification: str
    source_phase_references: tuple[str, ...]
    source_report_references: tuple[str, ...]
    governance_metadata_reference: str
    transition_boundary_metadata_reference: str
    transition_policy_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    non_execution_metadata_reference: str
    non_activation_metadata_reference: str
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_TRANSITION_PURPOSE
    deterministic: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_executing: bool = True
    non_activating: bool = True
    transition_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_phase_references", "source_report_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionRecord:
    transition_id: str
    transition_name: str
    transition_classification: str
    source_state_id: str
    source_state_classification: str
    target_state_id: str
    target_state_classification: str
    support_state: str
    boundary_reference: str
    policy_reference: str
    capability_reference: str
    topology_reference: str
    manifest_reference: str
    deterministic_order: int
    prohibited_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    blocked_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    conflicting_reason_visibility: tuple[str, ...] = ()
    governance_metadata_reference: str = "v4_3_transition_governance_metadata"
    continuity_metadata_reference: str = "v4_3_transition_continuity_metadata"
    provenance_metadata_reference: str = "v4_3_transition_provenance_metadata"
    lineage_metadata_reference: str = "v4_3_transition_lineage_metadata"
    diagnostics_metadata_reference: str = "v4_3_transition_diagnostics_metadata"
    explainability_metadata_reference: str = "v4_3_transition_explainability_metadata"
    transition_visible: bool = True
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    activation_capable: bool = False
    state_progression_enabled: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    operationally_routable: bool = False
    schedulable: bool = False
    transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    transition_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    dispatch_enabled: bool = False
    operational_coordination_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_reason_visibility",
            "unsupported_reason_visibility",
            "blocked_reason_visibility",
            "stale_reason_visibility",
            "conflicting_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionRelationship:
    relationship_id: str
    relationship_type: str
    source_transition_id: str
    target_reference_id: str
    target_reference_type: str
    relationship_state: str
    deterministic_order: int
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    activation_capable: bool = False
    state_progression_enabled: bool = False
    routable: bool = False
    traversable: bool = False
    schedulable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    transition_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    dispatch_enabled: bool = False
    operational_coordination_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class TransitionSupportStateVisibility:
    prohibited_transition_ids: tuple[str, ...]
    unsupported_transition_ids: tuple[str, ...]
    blocked_transition_ids: tuple[str, ...]
    stale_transition_ids: tuple[str, ...]
    conflicting_transition_ids: tuple[str, ...]
    unknown_transition_ids: tuple[str, ...]
    prohibited_classifications: tuple[str, ...]
    unsupported_classifications: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    transition_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_transition_ids",
            "unsupported_transition_ids",
            "blocked_transition_ids",
            "stale_transition_ids",
            "conflicting_transition_ids",
            "unknown_transition_ids",
            "prohibited_classifications",
            "unsupported_classifications",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionContinuityMetadata:
    continuity_id: str
    transition_references: tuple[str, ...]
    relationship_references: tuple[str, ...]
    source_state_references: tuple[str, ...]
    target_state_references: tuple[str, ...]
    replay_evidence_reference: str
    rollback_evidence_reference: str
    provenance_reference: str
    lineage_reference: str
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    descriptive_only: bool = True
    transition_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "transition_references",
            "relationship_references",
            "source_state_references",
            "target_state_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionDiagnostic:
    diagnostic_id: str
    diagnostic_category: str
    severity: str
    message: str
    affected_transition_ids: tuple[str, ...]
    affected_relationship_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    execution_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    authorization_enabled: bool = False
    mutation_enabled: bool = False
    activation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_transition_ids", "affected_relationship_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionExplainability:
    explanation_id: str
    explanation_category: str
    summary: str
    affected_transition_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    transition_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_transition_ids")


@dataclass(frozen=True)
class OrchestrationTransitionVisibility:
    identity: TransitionVisibilityIdentity
    metadata: TransitionVisibilityMetadata
    transitions: tuple[TransitionRecord, ...]
    relationships: tuple[TransitionRelationship, ...]
    support_state_visibility: TransitionSupportStateVisibility
    continuity_metadata: tuple[TransitionContinuityMetadata, ...]
    diagnostics: tuple[TransitionDiagnostic, ...]
    explainability_summaries: tuple[TransitionExplainability, ...]
    transition_visibility_classification: str = "governance_safe_transition_visibility_descriptive_only"
    non_executable: bool = True
    non_activating: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    state_machine_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    state_progression_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    transition_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    transition_dispatch_enabled: bool = False
    operational_coordination_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    planning_engine_enabled: bool = False
    decision_engine_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    hidden_transition_pathway_enabled: bool = False
    implicit_operational_authorization_enabled: bool = False
    transition_engine_enabled: bool = False
    orchestration_runtime_enabled: bool = False
    executable_state_machine_enabled: bool = False
    orchestration_dispatcher_enabled: bool = False
    operational_capability_enabled: bool = False
    policy_enforcement_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "transitions",
            "relationships",
            "continuity_metadata",
            "diagnostics",
            "explainability_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_transition_visibility_identity() -> TransitionVisibilityIdentity:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    return TransitionVisibilityIdentity(
        transition_set_id="v4_3_orchestration_transition_visibility_primary",
        transition_set_version="v4.3.0-phase-5",
        transition_set_classification="descriptive_only_transition_governance_visibility",
        source_manifest_reference=manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_orchestration_manifest(manifest),
        source_topology_reference=topology.identity.topology_id,
        source_topology_hash_reference=hash_orchestration_topology(topology),
        source_capability_reference=capability.identity.capability_set_id,
        source_capability_hash_reference=hash_orchestration_capability_visibility(capability),
        source_policy_reference=policy.identity.policy_set_id,
        source_policy_hash_reference=hash_orchestration_policy_visibility(policy),
        schema_version=V4_3_ORCHESTRATION_TRANSITION_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_TRANSITION_GENERATED_AT,
        governance_reference="v4_3_transition_governance_primary",
        transition_boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
        transition_policy_reference="v4_3_transition_policy_primary",
        lineage_reference="v4_3_transition_lineage_primary",
        provenance_reference="v4_3_transition_provenance_primary",
        continuity_reference="v4_3_transition_continuity_primary",
        diagnostics_reference="v4_3_transition_diagnostics_primary",
        explainability_reference="v4_3_transition_explainability_primary",
        non_execution_reference="v4_3_transition_non_execution_primary",
        non_activation_reference="v4_3_transition_non_activation_primary",
    )


def default_transition_visibility_metadata(
    identity: TransitionVisibilityIdentity,
) -> TransitionVisibilityMetadata:
    return TransitionVisibilityMetadata(
        metadata_id="v4_3_orchestration_transition_visibility_metadata",
        phase_id=V4_3_ORCHESTRATION_TRANSITION_PHASE_ID,
        transition_set_classification=identity.transition_set_classification,
        source_phase_references=(
            "v4_3_orchestration_manifest_foundations",
            "v4_3_orchestration_topology_visibility",
            "v4_3_orchestration_boundary_and_capability_visibility",
            "v4_3_orchestration_policy_visibility",
        ),
        source_report_references=(
            "docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            "docs/generated/v4_3_orchestration_topology_visibility_report.json",
            "docs/generated/v4_3_orchestration_boundary_and_capability_visibility_report.json",
            "docs/generated/v4_3_orchestration_policy_visibility_report.json",
        ),
        governance_metadata_reference="v4_3_transition_governance_metadata",
        transition_boundary_metadata_reference="v4_3_transition_boundary_metadata",
        transition_policy_metadata_reference="v4_3_transition_policy_metadata",
        continuity_metadata_reference="v4_3_transition_continuity_metadata",
        provenance_metadata_reference="v4_3_transition_provenance_metadata",
        lineage_metadata_reference="v4_3_transition_lineage_metadata",
        diagnostics_metadata_reference="v4_3_transition_diagnostics_metadata",
        explainability_metadata_reference="v4_3_transition_explainability_metadata",
        non_execution_metadata_reference="v4_3_transition_non_execution_metadata",
        non_activation_metadata_reference="v4_3_transition_non_activation_metadata",
        deterministic_order=1,
    )


def default_transition_records() -> tuple[TransitionRecord, ...]:
    return (
        TransitionRecord(
            transition_id="v4_3_transition_governance_constraint_visibility",
            transition_name="Governance Constraint Transition Visibility",
            transition_classification="governance_constrained_transition_visibility",
            source_state_id="manifest_visibility_established",
            source_state_classification="descriptive_manifest_state",
            target_state_id="topology_visibility_established",
            target_state_classification="descriptive_topology_state",
            support_state=TRANSITION_STATE_SUPPORTED,
            boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
            policy_reference="v4_3_orchestration_policy_visibility_primary",
            capability_reference="v4_3_orchestration_capability_visibility_primary",
            topology_reference="v4_3_orchestration_topology_primary",
            manifest_reference="v4_3_orchestration_manifest_primary",
            deterministic_order=1,
        ),
        TransitionRecord(
            transition_id="v4_3_transition_future_runtime_contract",
            transition_name="Future Runtime Transition Contract Visibility",
            transition_classification="future_transition_runtime_contract",
            source_state_id="policy_visibility_established",
            source_state_classification="descriptive_policy_state",
            target_state_id="future_runtime_transition_requested",
            target_state_classification="unsupported_future_runtime_state",
            support_state=TRANSITION_STATE_UNSUPPORTED,
            boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
            policy_reference="v4_3_orchestration_policy_visibility_primary",
            capability_reference="v4_3_orchestration_capability_visibility_primary",
            topology_reference="v4_3_orchestration_topology_primary",
            manifest_reference="v4_3_orchestration_manifest_primary",
            deterministic_order=2,
            unsupported_reason_visibility=(
                "future runtime transition contracts are visible but unsupported in Phase 5",
            ),
            fail_visible=True,
        ),
        TransitionRecord(
            transition_id="v4_3_transition_orchestration_activation_block",
            transition_name="Orchestration Activation Transition Block",
            transition_classification="orchestration_activation_block",
            source_state_id="capability_visibility_established",
            source_state_classification="descriptive_capability_state",
            target_state_id="orchestration_activation_requested",
            target_state_classification="blocked_activation_state",
            support_state=TRANSITION_STATE_BLOCKED,
            boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
            policy_reference="v4_3_orchestration_policy_visibility_primary",
            capability_reference="v4_3_orchestration_capability_visibility_primary",
            topology_reference="v4_3_orchestration_topology_primary",
            manifest_reference="v4_3_orchestration_manifest_primary",
            deterministic_order=3,
            blocked_reason_visibility=(
                "transition visibility cannot activate orchestration behavior",
            ),
            fail_visible=True,
        ),
        TransitionRecord(
            transition_id="v4_3_transition_stale_topology_context",
            transition_name="Stale Topology Transition Context",
            transition_classification="stale_topology_transition_context",
            source_state_id="topology_visibility_established",
            source_state_classification="descriptive_topology_state",
            target_state_id="policy_constrained_transition_review",
            target_state_classification="stale_transition_review_state",
            support_state=TRANSITION_STATE_STALE,
            boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
            policy_reference="v4_3_orchestration_policy_visibility_primary",
            capability_reference="v4_3_orchestration_capability_visibility_primary",
            topology_reference="v4_3_orchestration_topology_primary",
            manifest_reference="v4_3_orchestration_manifest_primary",
            deterministic_order=4,
            stale_reason_visibility=(
                "transition context captures stale topology evidence without repair",
            ),
            fail_visible=True,
        ),
        TransitionRecord(
            transition_id="v4_3_transition_conflicting_state_progression_claim",
            transition_name="Conflicting State Progression Claim",
            transition_classification="conflicting_state_progression_claim",
            source_state_id="policy_visibility_established",
            source_state_classification="descriptive_policy_state",
            target_state_id="state_progression_claimed",
            target_state_classification="conflicting_state_progression",
            support_state=TRANSITION_STATE_CONFLICTING,
            boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
            policy_reference="v4_3_orchestration_policy_visibility_primary",
            capability_reference="v4_3_orchestration_capability_visibility_primary",
            topology_reference="v4_3_orchestration_topology_primary",
            manifest_reference="v4_3_orchestration_manifest_primary",
            deterministic_order=5,
            conflicting_reason_visibility=(
                "state progression claims conflict with explicit non-activation boundaries",
            ),
            fail_visible=True,
        ),
        TransitionRecord(
            transition_id="v4_3_transition_execution_prohibited",
            transition_name="Transition Execution Prohibited",
            transition_classification="transition_execution",
            source_state_id="transition_visibility_established",
            source_state_classification="descriptive_transition_state",
            target_state_id="transition_execution_requested",
            target_state_classification="prohibited_execution_state",
            support_state=TRANSITION_STATE_PROHIBITED,
            boundary_reference="v4_3_transition_boundary_non_execution_and_non_activation",
            policy_reference="v4_3_orchestration_policy_visibility_primary",
            capability_reference="v4_3_orchestration_capability_visibility_primary",
            topology_reference="v4_3_orchestration_topology_primary",
            manifest_reference="v4_3_orchestration_manifest_primary",
            deterministic_order=6,
            prohibited_reason_visibility=(
                "Phase 5 transition visibility cannot execute transitions",
                "state progression is explicitly prohibited",
            ),
            fail_visible=True,
        ),
    )


def default_transition_relationships(
    transitions: tuple[TransitionRecord, ...],
) -> tuple[TransitionRelationship, ...]:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    target_refs = {
        TRANSITION_TARGET_MANIFEST: manifest.identity.manifest_id,
        TRANSITION_TARGET_TOPOLOGY: topology.identity.topology_id,
        TRANSITION_TARGET_CAPABILITY: capability.identity.capability_set_id,
        TRANSITION_TARGET_POLICY: policy.identity.policy_set_id,
        TRANSITION_TARGET_BOUNDARY: "v4_3_transition_boundary_non_execution_and_non_activation",
    }
    relationships: list[TransitionRelationship] = []
    relationship_order = 1
    relationship_types = (
        TRANSITION_RELATIONSHIP_TO_MANIFEST,
        TRANSITION_RELATIONSHIP_TO_TOPOLOGY,
        TRANSITION_RELATIONSHIP_TO_CAPABILITY,
        TRANSITION_RELATIONSHIP_TO_POLICY,
        TRANSITION_RELATIONSHIP_TO_BOUNDARY,
    )
    for transition in transitions:
        for relationship_type in relationship_types:
            target_type = TRANSITION_RELATIONSHIP_TARGET_TYPES[relationship_type]
            relationships.append(
                TransitionRelationship(
                    relationship_id=f"{transition.transition_id}_{relationship_type}",
                    relationship_type=relationship_type,
                    source_transition_id=transition.transition_id,
                    target_reference_id=target_refs[target_type],
                    target_reference_type=target_type,
                    relationship_state=transition.support_state,
                    deterministic_order=relationship_order,
                    fail_visible=transition.support_state in FAIL_VISIBLE_TRANSITION_STATES,
                )
            )
            relationship_order += 1
    return tuple(relationships)


def default_transition_support_state_visibility(
    transitions: tuple[TransitionRecord, ...],
) -> TransitionSupportStateVisibility:
    return TransitionSupportStateVisibility(
        prohibited_transition_ids=tuple(
            transition.transition_id
            for transition in transitions
            if transition.support_state == TRANSITION_STATE_PROHIBITED
            or transition.transition_classification in PROHIBITED_TRANSITION_CLASSIFICATIONS
        ),
        unsupported_transition_ids=tuple(
            transition.transition_id
            for transition in transitions
            if transition.support_state == TRANSITION_STATE_UNSUPPORTED
            or transition.transition_classification in UNSUPPORTED_TRANSITION_CLASSIFICATIONS
        ),
        blocked_transition_ids=tuple(
            transition.transition_id
            for transition in transitions
            if transition.support_state == TRANSITION_STATE_BLOCKED
        ),
        stale_transition_ids=tuple(
            transition.transition_id
            for transition in transitions
            if transition.support_state == TRANSITION_STATE_STALE
        ),
        conflicting_transition_ids=tuple(
            transition.transition_id
            for transition in transitions
            if transition.support_state == TRANSITION_STATE_CONFLICTING
        ),
        unknown_transition_ids=tuple(
            transition.transition_id
            for transition in transitions
            if transition.support_state == TRANSITION_STATE_UNKNOWN
        ),
        prohibited_classifications=PROHIBITED_TRANSITION_CLASSIFICATIONS,
        unsupported_classifications=UNSUPPORTED_TRANSITION_CLASSIFICATIONS,
        deterministic_order=1,
    )


def default_transition_continuity_metadata(
    transitions: tuple[TransitionRecord, ...],
    relationships: tuple[TransitionRelationship, ...],
) -> tuple[TransitionContinuityMetadata, ...]:
    return (
        TransitionContinuityMetadata(
            continuity_id="v4_3_transition_continuity_replay_and_rollback",
            transition_references=tuple(transition.transition_id for transition in transitions),
            relationship_references=tuple(relationship.relationship_id for relationship in relationships),
            source_state_references=tuple(transition.source_state_id for transition in transitions),
            target_state_references=tuple(transition.target_state_id for transition in transitions),
            replay_evidence_reference="v4_3_transition_replay_safe_evidence",
            rollback_evidence_reference="v4_3_transition_rollback_safe_evidence",
            provenance_reference="v4_3_transition_provenance_primary",
            lineage_reference="v4_3_transition_lineage_primary",
            deterministic_order=1,
        ),
    )


def default_transition_diagnostics(
    transitions: tuple[TransitionRecord, ...],
) -> tuple[TransitionDiagnostic, ...]:
    prohibited_ids = tuple(
        transition.transition_id
        for transition in transitions
        if transition.support_state == TRANSITION_STATE_PROHIBITED
    )
    unsupported_ids = tuple(
        transition.transition_id
        for transition in transitions
        if transition.support_state == TRANSITION_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        transition.transition_id
        for transition in transitions
        if transition.support_state == TRANSITION_STATE_BLOCKED
    )
    stale_ids = tuple(
        transition.transition_id for transition in transitions if transition.support_state == TRANSITION_STATE_STALE
    )
    conflicting_ids = tuple(
        transition.transition_id
        for transition in transitions
        if transition.support_state == TRANSITION_STATE_CONFLICTING
    )
    all_ids = tuple(transition.transition_id for transition in transitions)
    return (
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_identity_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_IDENTITY,
            severity="info",
            message="Transition identity is modeled as deterministic descriptive governance evidence.",
            affected_transition_ids=(),
            affected_relationship_ids=(),
            deterministic_order=1,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_unsupported_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            message="Unsupported transition classifications are fail-visible and not inferred into runtime behavior.",
            affected_transition_ids=unsupported_ids,
            affected_relationship_ids=(),
            deterministic_order=2,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_blocked_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_BLOCKED,
            severity="blocker",
            message="Blocked transition states remain descriptive and cannot activate orchestration behavior.",
            affected_transition_ids=blocked_ids,
            affected_relationship_ids=(),
            deterministic_order=3,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_stale_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_STALE,
            severity="warning",
            message="Stale transition context is visible without repair or correction.",
            affected_transition_ids=stale_ids,
            affected_relationship_ids=(),
            deterministic_order=4,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_conflicting_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_CONFLICTING,
            severity="blocker",
            message="Conflicting transition metadata is visible without authorization or state progression.",
            affected_transition_ids=conflicting_ids,
            affected_relationship_ids=(),
            deterministic_order=5,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_prohibited_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            message="Transition execution is explicitly prohibited and fail-visible.",
            affected_transition_ids=prohibited_ids,
            affected_relationship_ids=(),
            deterministic_order=6,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_relationship_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_RELATIONSHIP,
            severity="info",
            message="Transition relationships are visible as governance evidence only and cannot route or traverse.",
            affected_transition_ids=all_ids,
            affected_relationship_ids=(),
            deterministic_order=7,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_non_activation_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_NON_ACTIVATION,
            severity="prohibited",
            message="Transition visibility explicitly certifies enabled_transition_execution_count equals 0.",
            affected_transition_ids=all_ids,
            affected_relationship_ids=(),
            deterministic_order=8,
        ),
        TransitionDiagnostic(
            diagnostic_id="v4_3_transition_non_execution_diagnostic",
            diagnostic_category=TRANSITION_DIAGNOSTIC_NON_EXECUTION,
            severity="prohibited",
            message="Transition visibility certifies operational capability and policy enforcement counts remain 0.",
            affected_transition_ids=all_ids,
            affected_relationship_ids=(),
            deterministic_order=9,
        ),
    )


def default_transition_explainability() -> tuple[TransitionExplainability, ...]:
    return (
        TransitionExplainability(
            explanation_id="v4_3_transition_prohibited_explanation",
            explanation_category="prohibited_transition",
            summary="A transition is prohibited when it appears to enable transition execution, state progression, dispatch, or runtime behavior.",
            affected_transition_ids=("v4_3_transition_execution_prohibited",),
            deterministic_order=1,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_unsupported_explanation",
            explanation_category="unsupported_transition",
            summary="Unsupported transition states remain visible as future governance surfaces without inference or activation.",
            affected_transition_ids=("v4_3_transition_future_runtime_contract",),
            deterministic_order=2,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_blocked_explanation",
            explanation_category="blocked_transition",
            summary="A transition is blocked when it would imply orchestration activation, which Phase 5 cannot perform.",
            affected_transition_ids=("v4_3_transition_orchestration_activation_block",),
            deterministic_order=3,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_stale_explanation",
            explanation_category="stale_transition",
            summary="Stale transition context is reported deterministically and cannot be repaired automatically.",
            affected_transition_ids=("v4_3_transition_stale_topology_context",),
            deterministic_order=4,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_conflicting_explanation",
            explanation_category="conflicting_transition",
            summary="Conflicting transition claims are fail-visible because state progression remains unavailable.",
            affected_transition_ids=("v4_3_transition_conflicting_state_progression_claim",),
            deterministic_order=5,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_execution_unavailable_explanation",
            explanation_category="transition_execution_unavailable",
            summary="Transition execution remains unavailable because Phase 5 provides transition visibility only.",
            affected_transition_ids=("v4_3_transition_execution_prohibited",),
            deterministic_order=6,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_activation_unavailable_explanation",
            explanation_category="orchestration_activation_unavailable",
            summary="Orchestration activation remains unavailable because transitions are descriptive governance evidence.",
            affected_transition_ids=("v4_3_transition_orchestration_activation_block",),
            deterministic_order=7,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_state_progression_unavailable_explanation",
            explanation_category="state_progression_unavailable",
            summary="State progression remains unavailable because no executable transition state machine exists.",
            affected_transition_ids=("v4_3_transition_conflicting_state_progression_claim",),
            deterministic_order=8,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_planner_integration_unavailable_explanation",
            explanation_category="planner_integration_unavailable",
            summary="Planner integration remains unavailable because Phase 5 cannot consume or steer operational planning.",
            affected_transition_ids=("v4_3_transition_governance_constraint_visibility",),
            deterministic_order=9,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_production_consumption_unavailable_explanation",
            explanation_category="production_consumption_unavailable",
            summary="Production consumption remains unavailable because transition evidence is replay-safe and rollback-safe descriptive output.",
            affected_transition_ids=("v4_3_transition_governance_constraint_visibility",),
            deterministic_order=10,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_governance_constraint_explanation",
            explanation_category="governance_constraints_exist",
            summary="Governance constraints exist to keep theoretical transitions auditable without operational flow.",
            affected_transition_ids=("v4_3_transition_governance_constraint_visibility",),
            deterministic_order=11,
        ),
        TransitionExplainability(
            explanation_id="v4_3_transition_operational_orchestration_prohibited_explanation",
            explanation_category="operational_orchestration_prohibited",
            summary="Operational orchestration remains prohibited because no transition engine, runtime, state machine, or dispatcher exists.",
            affected_transition_ids=("v4_3_transition_execution_prohibited",),
            deterministic_order=12,
        ),
    )


def default_orchestration_transition_visibility() -> OrchestrationTransitionVisibility:
    identity = default_transition_visibility_identity()
    transitions = default_transition_records()
    relationships = default_transition_relationships(transitions)
    return OrchestrationTransitionVisibility(
        identity=identity,
        metadata=default_transition_visibility_metadata(identity),
        transitions=transitions,
        relationships=relationships,
        support_state_visibility=default_transition_support_state_visibility(transitions),
        continuity_metadata=default_transition_continuity_metadata(transitions, relationships),
        diagnostics=default_transition_diagnostics(transitions),
        explainability_summaries=default_transition_explainability(),
    )
