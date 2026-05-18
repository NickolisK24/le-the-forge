"""Deterministic v4.3 orchestration coordination visibility models.

Coordination visibility is descriptive governance evidence only. It models how
orchestration governance components would theoretically coordinate while
preserving explicit non-execution and non-coordination guarantees. No dispatch,
runtime coordinator, orchestration activation, routing, scheduling, state
machine execution, planner behavior, or production consumption is introduced.
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
from .orchestration_transition_hashing import hash_orchestration_transition_visibility
from .orchestration_transition_models import default_orchestration_transition_visibility


V4_3_ORCHESTRATION_COORDINATION_PHASE_ID = "v4_3_orchestration_coordination_visibility"
V4_3_ORCHESTRATION_COORDINATION_SCHEMA_VERSION = "v4_3.orchestration_coordination_visibility.1"
V4_3_ORCHESTRATION_COORDINATION_REPORT_SCHEMA_VERSION = (
    "v4_3.orchestration_coordination_visibility_report.1"
)
V4_3_ORCHESTRATION_COORDINATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_COORDINATION_STATUS_STABLE = (
    "v4_3_orchestration_coordination_visibility_stable"
)
V4_3_ORCHESTRATION_COORDINATION_STATUS_BLOCKED = (
    "v4_3_orchestration_coordination_visibility_blocked"
)
V4_3_ORCHESTRATION_COORDINATION_PURPOSE = (
    "deterministic_orchestration_coordination_governance_modeling_only"
)

COORDINATION_STATE_SUPPORTED = "supported"
COORDINATION_STATE_PROHIBITED = "prohibited"
COORDINATION_STATE_UNSUPPORTED = "unsupported"
COORDINATION_STATE_BLOCKED = "blocked"
COORDINATION_STATE_STALE = "stale"
COORDINATION_STATE_CONFLICTING = "conflicting"
COORDINATION_STATE_UNKNOWN = "unknown"
COORDINATION_STATES: tuple[str, ...] = (
    COORDINATION_STATE_SUPPORTED,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_UNSUPPORTED,
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_CONFLICTING,
    COORDINATION_STATE_UNKNOWN,
)
FAIL_VISIBLE_COORDINATION_STATES: tuple[str, ...] = (
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_UNSUPPORTED,
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_CONFLICTING,
    COORDINATION_STATE_UNKNOWN,
)

COORDINATION_TARGET_POLICY = "policy"
COORDINATION_TARGET_CAPABILITY = "capability"
COORDINATION_TARGET_TRANSITION = "transition"
COORDINATION_TARGET_BOUNDARY = "boundary"
COORDINATION_TARGET_TOPOLOGY = "topology"
COORDINATION_TARGET_MANIFEST = "manifest"
COORDINATION_TARGET_TYPES: tuple[str, ...] = (
    COORDINATION_TARGET_POLICY,
    COORDINATION_TARGET_CAPABILITY,
    COORDINATION_TARGET_TRANSITION,
    COORDINATION_TARGET_BOUNDARY,
    COORDINATION_TARGET_TOPOLOGY,
    COORDINATION_TARGET_MANIFEST,
)

COORDINATION_RELATIONSHIP_TO_POLICY = "coordination_to_policy"
COORDINATION_RELATIONSHIP_TO_CAPABILITY = "coordination_to_capability"
COORDINATION_RELATIONSHIP_TO_TRANSITION = "coordination_to_transition"
COORDINATION_RELATIONSHIP_TO_BOUNDARY = "coordination_to_boundary"
COORDINATION_RELATIONSHIP_TO_TOPOLOGY = "coordination_to_topology"
COORDINATION_RELATIONSHIP_TO_MANIFEST = "coordination_to_manifest"
COORDINATION_RELATIONSHIP_TYPES: tuple[str, ...] = (
    COORDINATION_RELATIONSHIP_TO_POLICY,
    COORDINATION_RELATIONSHIP_TO_CAPABILITY,
    COORDINATION_RELATIONSHIP_TO_TRANSITION,
    COORDINATION_RELATIONSHIP_TO_BOUNDARY,
    COORDINATION_RELATIONSHIP_TO_TOPOLOGY,
    COORDINATION_RELATIONSHIP_TO_MANIFEST,
)
COORDINATION_RELATIONSHIP_TARGET_TYPES: dict[str, str] = {
    COORDINATION_RELATIONSHIP_TO_POLICY: COORDINATION_TARGET_POLICY,
    COORDINATION_RELATIONSHIP_TO_CAPABILITY: COORDINATION_TARGET_CAPABILITY,
    COORDINATION_RELATIONSHIP_TO_TRANSITION: COORDINATION_TARGET_TRANSITION,
    COORDINATION_RELATIONSHIP_TO_BOUNDARY: COORDINATION_TARGET_BOUNDARY,
    COORDINATION_RELATIONSHIP_TO_TOPOLOGY: COORDINATION_TARGET_TOPOLOGY,
    COORDINATION_RELATIONSHIP_TO_MANIFEST: COORDINATION_TARGET_MANIFEST,
}

COORDINATION_DIAGNOSTIC_IDENTITY = "coordination_identity_visibility"
COORDINATION_DIAGNOSTIC_DUPLICATE = "duplicate_coordination_visibility"
COORDINATION_DIAGNOSTIC_PARTICIPANT = "coordination_participant_visibility"
COORDINATION_DIAGNOSTIC_RELATIONSHIP = "coordination_relationship_visibility"
COORDINATION_DIAGNOSTIC_PROHIBITED = "prohibited_coordination_visibility"
COORDINATION_DIAGNOSTIC_UNSUPPORTED = "unsupported_coordination_visibility"
COORDINATION_DIAGNOSTIC_BLOCKED = "blocked_coordination_visibility"
COORDINATION_DIAGNOSTIC_STALE = "stale_coordination_visibility"
COORDINATION_DIAGNOSTIC_CONFLICTING = "conflicting_coordination_visibility"
COORDINATION_DIAGNOSTIC_METADATA = "metadata_visibility"
COORDINATION_DIAGNOSTIC_EXPLAINABILITY = "explainability_visibility"
COORDINATION_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"
COORDINATION_DIAGNOSTIC_NON_COORDINATION = "non_coordination_boundary_visibility"

PROHIBITED_COORDINATION_CLASSIFICATIONS: tuple[str, ...] = (
    "orchestration_execution",
    "operational_coordination",
    "runtime_coordination",
    "orchestration_dispatch",
    "orchestration_activation",
    "routing_execution",
    "traversal_execution",
    "scheduling_execution",
    "sequencing_execution",
    "dependency_resolution",
    "state_machine_execution",
    "transition_execution",
    "coordination_authorization",
    "readiness_approval",
    "remediation",
    "repair",
    "inference",
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
    "hidden_coordination_pathways",
    "implicit_operational_authorization",
    "orchestration_coordination_engine",
    "dispatcher",
    "runtime_coordinator",
    "operational_state_machine",
)
UNSUPPORTED_COORDINATION_CLASSIFICATIONS: tuple[str, ...] = (
    "future_runtime_coordination_contract",
    "future_dispatch_surface",
    "future_coordination_consumer",
)

EXPLICIT_ORCHESTRATION_COORDINATION_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 6 creates deterministic orchestration coordination governance modeling only.",
    "v4.3 Phase 6 makes theoretical coordination relationships visible before operational coordination.",
    "v4.3 Phase 6 does not enable orchestration execution.",
    "v4.3 Phase 6 does not enable operational or runtime coordination.",
    "v4.3 Phase 6 does not enable orchestration dispatch or activation.",
    "v4.3 Phase 6 does not enable routing, traversal, scheduling, sequencing, or dependency resolution.",
    "v4.3 Phase 6 does not enable state machine execution or transition execution.",
    "v4.3 Phase 6 does not enable authorization or readiness approval.",
    "v4.3 Phase 6 does not enable remediation, repair, inference, recommendation, ranking, scoring, selection, or optimization.",
    "v4.3 Phase 6 does not enable planner integration, production consumption, runtime mutation, or operational mutation.",
)

EXPLICIT_ORCHESTRATION_COORDINATION_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration coordination engine may exist.",
    "No dispatcher may exist.",
    "No runtime coordinator may exist.",
    "No operational state machine may exist.",
    "No orchestration execution exists.",
    "No operational coordination exists.",
    "No runtime coordination exists.",
    "No orchestration dispatch exists.",
    "No orchestration activation exists.",
    "No routing execution exists.",
    "No traversal execution exists.",
    "No scheduling execution exists.",
    "No sequencing execution exists.",
    "No dependency resolution exists.",
    "No state machine execution exists.",
    "No transition execution exists.",
    "No coordination authorization exists.",
    "No readiness approval exists.",
    "No remediation exists.",
    "No repair exists.",
    "No inference exists.",
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
    "No hidden coordination pathway exists.",
    "No implicit operational authorization exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationVisibilityIdentity:
    coordination_set_id: str
    coordination_set_version: str
    coordination_set_classification: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_topology_reference: str
    source_topology_hash_reference: str
    source_capability_reference: str
    source_capability_hash_reference: str
    source_policy_reference: str
    source_policy_hash_reference: str
    source_transition_reference: str
    source_transition_hash_reference: str
    schema_version: str
    generated_at: str
    governance_reference: str
    coordination_boundary_reference: str
    coordination_policy_reference: str
    coordination_transition_reference: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    diagnostics_reference: str
    explainability_reference: str
    non_execution_reference: str
    non_coordination_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_COORDINATION_PURPOSE
    non_executable: bool = True
    non_coordinating: bool = True
    descriptive_only: bool = True
    coordination_execution_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_coordination_enabled: bool = False
    orchestration_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class CoordinationVisibilityMetadata:
    metadata_id: str
    phase_id: str
    coordination_set_classification: str
    source_phase_references: tuple[str, ...]
    source_report_references: tuple[str, ...]
    governance_metadata_reference: str
    coordination_boundary_metadata_reference: str
    coordination_policy_metadata_reference: str
    coordination_transition_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    non_execution_metadata_reference: str
    non_coordination_metadata_reference: str
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_COORDINATION_PURPOSE
    deterministic: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_executing: bool = True
    non_coordinating: bool = True
    coordination_execution_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_coordination_enabled: bool = False
    orchestration_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_phase_references", "source_report_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationParticipant:
    participant_id: str
    participant_type: str
    participant_reference_id: str
    coordination_ids: tuple[str, ...]
    participant_state: str
    deterministic_order: int
    governance_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    dispatch_capable: bool = False
    activation_capable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    operationally_routable: bool = False
    schedulable: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "coordination_ids")


@dataclass(frozen=True)
class CoordinationRecord:
    coordination_id: str
    coordination_name: str
    coordination_classification: str
    coordination_scope: str
    participant_ids: tuple[str, ...]
    support_state: str
    boundary_reference: str
    policy_reference: str
    capability_reference: str
    transition_reference: str
    topology_reference: str
    manifest_reference: str
    deterministic_order: int
    prohibited_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    blocked_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    conflicting_reason_visibility: tuple[str, ...] = ()
    governance_metadata_reference: str = "v4_3_coordination_governance_metadata"
    continuity_metadata_reference: str = "v4_3_coordination_continuity_metadata"
    provenance_metadata_reference: str = "v4_3_coordination_provenance_metadata"
    lineage_metadata_reference: str = "v4_3_coordination_lineage_metadata"
    diagnostics_metadata_reference: str = "v4_3_coordination_diagnostics_metadata"
    explainability_metadata_reference: str = "v4_3_coordination_explainability_metadata"
    coordination_visible: bool = True
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    dispatch_capable: bool = False
    activation_capable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    operationally_routable: bool = False
    schedulable: bool = False
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    operational_coordination_enabled: bool = False
    runtime_coordination_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_activation_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    state_machine_execution_enabled: bool = False
    transition_execution_enabled: bool = False
    coordination_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "participant_ids",
            "prohibited_reason_visibility",
            "unsupported_reason_visibility",
            "blocked_reason_visibility",
            "stale_reason_visibility",
            "conflicting_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationRelationship:
    relationship_id: str
    relationship_type: str
    source_coordination_id: str
    target_reference_id: str
    target_reference_type: str
    relationship_state: str
    deterministic_order: int
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    dispatch_capable: bool = False
    activation_capable: bool = False
    routable: bool = False
    traversable: bool = False
    schedulable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    operational_coordination_enabled: bool = False
    runtime_coordination_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_activation_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    state_machine_execution_enabled: bool = False
    transition_execution_enabled: bool = False
    coordination_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class CoordinationSupportStateVisibility:
    prohibited_coordination_ids: tuple[str, ...]
    unsupported_coordination_ids: tuple[str, ...]
    blocked_coordination_ids: tuple[str, ...]
    stale_coordination_ids: tuple[str, ...]
    conflicting_coordination_ids: tuple[str, ...]
    unknown_coordination_ids: tuple[str, ...]
    prohibited_classifications: tuple[str, ...]
    unsupported_classifications: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    coordination_execution_enabled: bool = False
    operational_coordination_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_coordination_ids",
            "unsupported_coordination_ids",
            "blocked_coordination_ids",
            "stale_coordination_ids",
            "conflicting_coordination_ids",
            "unknown_coordination_ids",
            "prohibited_classifications",
            "unsupported_classifications",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationContinuityMetadata:
    continuity_id: str
    coordination_references: tuple[str, ...]
    participant_references: tuple[str, ...]
    relationship_references: tuple[str, ...]
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
    coordination_execution_enabled: bool = False
    operational_coordination_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("coordination_references", "participant_references", "relationship_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDiagnostic:
    diagnostic_id: str
    diagnostic_category: str
    severity: str
    message: str
    affected_coordination_ids: tuple[str, ...]
    affected_participant_ids: tuple[str, ...]
    affected_relationship_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    execution_enabled: bool = False
    dispatch_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    authorization_enabled: bool = False
    mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_coordination_ids", "affected_participant_ids", "affected_relationship_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationExplainability:
    explanation_id: str
    explanation_category: str
    summary: str
    affected_coordination_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    coordination_execution_enabled: bool = False
    operational_coordination_enabled: bool = False
    orchestration_dispatch_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_coordination_ids")


@dataclass(frozen=True)
class OrchestrationCoordinationVisibility:
    identity: CoordinationVisibilityIdentity
    metadata: CoordinationVisibilityMetadata
    coordinations: tuple[CoordinationRecord, ...]
    participants: tuple[CoordinationParticipant, ...]
    relationships: tuple[CoordinationRelationship, ...]
    support_state_visibility: CoordinationSupportStateVisibility
    continuity_metadata: tuple[CoordinationContinuityMetadata, ...]
    diagnostics: tuple[CoordinationDiagnostic, ...]
    explainability_summaries: tuple[CoordinationExplainability, ...]
    coordination_visibility_classification: str = "governance_safe_coordination_visibility_descriptive_only"
    non_executable: bool = True
    non_coordinating: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    operational_coordination_enabled: bool = False
    runtime_coordination_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_activation_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    state_machine_execution_enabled: bool = False
    transition_execution_enabled: bool = False
    coordination_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
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
    hidden_coordination_pathway_enabled: bool = False
    implicit_operational_authorization_enabled: bool = False
    orchestration_coordination_engine_enabled: bool = False
    dispatcher_enabled: bool = False
    runtime_coordinator_enabled: bool = False
    operational_state_machine_enabled: bool = False
    operational_capability_enabled: bool = False
    policy_enforcement_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "coordinations",
            "participants",
            "relationships",
            "continuity_metadata",
            "diagnostics",
            "explainability_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_coordination_visibility_identity() -> CoordinationVisibilityIdentity:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    transition = default_orchestration_transition_visibility()
    return CoordinationVisibilityIdentity(
        coordination_set_id="v4_3_orchestration_coordination_visibility_primary",
        coordination_set_version="v4.3.0-phase-6",
        coordination_set_classification="descriptive_only_coordination_governance_visibility",
        source_manifest_reference=manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_orchestration_manifest(manifest),
        source_topology_reference=topology.identity.topology_id,
        source_topology_hash_reference=hash_orchestration_topology(topology),
        source_capability_reference=capability.identity.capability_set_id,
        source_capability_hash_reference=hash_orchestration_capability_visibility(capability),
        source_policy_reference=policy.identity.policy_set_id,
        source_policy_hash_reference=hash_orchestration_policy_visibility(policy),
        source_transition_reference=transition.identity.transition_set_id,
        source_transition_hash_reference=hash_orchestration_transition_visibility(transition),
        schema_version=V4_3_ORCHESTRATION_COORDINATION_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_COORDINATION_GENERATED_AT,
        governance_reference="v4_3_coordination_governance_primary",
        coordination_boundary_reference="v4_3_coordination_boundary_non_execution_and_non_coordination",
        coordination_policy_reference=policy.identity.policy_set_id,
        coordination_transition_reference=transition.identity.transition_set_id,
        lineage_reference="v4_3_coordination_lineage_primary",
        provenance_reference="v4_3_coordination_provenance_primary",
        continuity_reference="v4_3_coordination_continuity_primary",
        diagnostics_reference="v4_3_coordination_diagnostics_primary",
        explainability_reference="v4_3_coordination_explainability_primary",
        non_execution_reference="v4_3_coordination_non_execution_primary",
        non_coordination_reference="v4_3_coordination_non_coordination_primary",
    )


def default_coordination_visibility_metadata(
    identity: CoordinationVisibilityIdentity,
) -> CoordinationVisibilityMetadata:
    return CoordinationVisibilityMetadata(
        metadata_id="v4_3_orchestration_coordination_visibility_metadata",
        phase_id=V4_3_ORCHESTRATION_COORDINATION_PHASE_ID,
        coordination_set_classification=identity.coordination_set_classification,
        source_phase_references=(
            "v4_3_orchestration_manifest_foundations",
            "v4_3_orchestration_topology_visibility",
            "v4_3_orchestration_boundary_and_capability_visibility",
            "v4_3_orchestration_policy_visibility",
            "v4_3_orchestration_transition_visibility",
        ),
        source_report_references=(
            "docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            "docs/generated/v4_3_orchestration_topology_visibility_report.json",
            "docs/generated/v4_3_orchestration_boundary_and_capability_visibility_report.json",
            "docs/generated/v4_3_orchestration_policy_visibility_report.json",
            "docs/generated/v4_3_orchestration_transition_visibility_report.json",
        ),
        governance_metadata_reference="v4_3_coordination_governance_metadata",
        coordination_boundary_metadata_reference="v4_3_coordination_boundary_metadata",
        coordination_policy_metadata_reference="v4_3_coordination_policy_metadata",
        coordination_transition_metadata_reference="v4_3_coordination_transition_metadata",
        continuity_metadata_reference="v4_3_coordination_continuity_metadata",
        provenance_metadata_reference="v4_3_coordination_provenance_metadata",
        lineage_metadata_reference="v4_3_coordination_lineage_metadata",
        diagnostics_metadata_reference="v4_3_coordination_diagnostics_metadata",
        explainability_metadata_reference="v4_3_coordination_explainability_metadata",
        non_execution_metadata_reference="v4_3_coordination_non_execution_metadata",
        non_coordination_metadata_reference="v4_3_coordination_non_coordination_metadata",
        deterministic_order=1,
    )


def default_coordination_records() -> tuple[CoordinationRecord, ...]:
    participant_ids = (
        "v4_3_coordination_participant_manifest",
        "v4_3_coordination_participant_topology",
        "v4_3_coordination_participant_capability",
        "v4_3_coordination_participant_policy",
        "v4_3_coordination_participant_transition",
        "v4_3_coordination_participant_boundary",
    )
    refs = {
        "boundary": "v4_3_coordination_boundary_non_execution_and_non_coordination",
        "policy": "v4_3_orchestration_policy_visibility_primary",
        "capability": "v4_3_orchestration_capability_visibility_primary",
        "transition": "v4_3_orchestration_transition_visibility_primary",
        "topology": "v4_3_orchestration_topology_primary",
        "manifest": "v4_3_orchestration_manifest_primary",
    }
    return (
        CoordinationRecord(
            coordination_id="v4_3_coordination_governance_relationship_visibility",
            coordination_name="Governance Relationship Coordination Visibility",
            coordination_classification="governance_constrained_coordination_visibility",
            coordination_scope="manifest_topology_capability_policy_transition_boundary",
            participant_ids=participant_ids,
            support_state=COORDINATION_STATE_SUPPORTED,
            boundary_reference=refs["boundary"],
            policy_reference=refs["policy"],
            capability_reference=refs["capability"],
            transition_reference=refs["transition"],
            topology_reference=refs["topology"],
            manifest_reference=refs["manifest"],
            deterministic_order=1,
        ),
        CoordinationRecord(
            coordination_id="v4_3_coordination_future_runtime_contract",
            coordination_name="Future Runtime Coordination Contract Visibility",
            coordination_classification="future_runtime_coordination_contract",
            coordination_scope="future_coordination_surface",
            participant_ids=participant_ids,
            support_state=COORDINATION_STATE_UNSUPPORTED,
            boundary_reference=refs["boundary"],
            policy_reference=refs["policy"],
            capability_reference=refs["capability"],
            transition_reference=refs["transition"],
            topology_reference=refs["topology"],
            manifest_reference=refs["manifest"],
            deterministic_order=2,
            unsupported_reason_visibility=("future runtime coordination contracts are visible but unsupported in Phase 6",),
            fail_visible=True,
        ),
        CoordinationRecord(
            coordination_id="v4_3_coordination_operational_coordination_block",
            coordination_name="Operational Coordination Block",
            coordination_classification="operational_coordination_block",
            coordination_scope="coordination_boundary",
            participant_ids=participant_ids,
            support_state=COORDINATION_STATE_BLOCKED,
            boundary_reference=refs["boundary"],
            policy_reference=refs["policy"],
            capability_reference=refs["capability"],
            transition_reference=refs["transition"],
            topology_reference=refs["topology"],
            manifest_reference=refs["manifest"],
            deterministic_order=3,
            blocked_reason_visibility=("coordination visibility cannot coordinate runtime behavior",),
            fail_visible=True,
        ),
        CoordinationRecord(
            coordination_id="v4_3_coordination_stale_transition_context",
            coordination_name="Stale Transition Coordination Context",
            coordination_classification="stale_transition_coordination_context",
            coordination_scope="transition_coordination_relationship",
            participant_ids=participant_ids,
            support_state=COORDINATION_STATE_STALE,
            boundary_reference=refs["boundary"],
            policy_reference=refs["policy"],
            capability_reference=refs["capability"],
            transition_reference=refs["transition"],
            topology_reference=refs["topology"],
            manifest_reference=refs["manifest"],
            deterministic_order=4,
            stale_reason_visibility=("coordination context captures stale transition evidence without repair",),
            fail_visible=True,
        ),
        CoordinationRecord(
            coordination_id="v4_3_coordination_conflicting_dispatch_claim",
            coordination_name="Conflicting Dispatch Claim Visibility",
            coordination_classification="conflicting_dispatch_claim",
            coordination_scope="dispatch_coordination_boundary",
            participant_ids=participant_ids,
            support_state=COORDINATION_STATE_CONFLICTING,
            boundary_reference=refs["boundary"],
            policy_reference=refs["policy"],
            capability_reference=refs["capability"],
            transition_reference=refs["transition"],
            topology_reference=refs["topology"],
            manifest_reference=refs["manifest"],
            deterministic_order=5,
            conflicting_reason_visibility=("dispatch claims conflict with explicit non-coordination boundaries",),
            fail_visible=True,
        ),
        CoordinationRecord(
            coordination_id="v4_3_coordination_dispatch_prohibited",
            coordination_name="Coordination Dispatch Prohibited",
            coordination_classification="orchestration_dispatch",
            coordination_scope="non_coordination_boundary",
            participant_ids=participant_ids,
            support_state=COORDINATION_STATE_PROHIBITED,
            boundary_reference=refs["boundary"],
            policy_reference=refs["policy"],
            capability_reference=refs["capability"],
            transition_reference=refs["transition"],
            topology_reference=refs["topology"],
            manifest_reference=refs["manifest"],
            deterministic_order=6,
            prohibited_reason_visibility=(
                "Phase 6 coordination visibility cannot dispatch orchestration behavior",
                "operational coordination is explicitly prohibited",
            ),
            fail_visible=True,
        ),
    )


def default_coordination_participants(
    coordinations: tuple[CoordinationRecord, ...],
) -> tuple[CoordinationParticipant, ...]:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    transition = default_orchestration_transition_visibility()
    coordination_ids = tuple(coordination.coordination_id for coordination in coordinations)
    return (
        CoordinationParticipant(
            participant_id="v4_3_coordination_participant_manifest",
            participant_type=COORDINATION_TARGET_MANIFEST,
            participant_reference_id=manifest.identity.manifest_id,
            coordination_ids=coordination_ids,
            participant_state=COORDINATION_STATE_SUPPORTED,
            deterministic_order=1,
            governance_metadata_reference="v4_3_coordination_manifest_participant_governance_metadata",
            continuity_metadata_reference="v4_3_coordination_manifest_participant_continuity_metadata",
            provenance_metadata_reference="v4_3_coordination_manifest_participant_provenance_metadata",
            lineage_metadata_reference="v4_3_coordination_manifest_participant_lineage_metadata",
        ),
        CoordinationParticipant(
            participant_id="v4_3_coordination_participant_topology",
            participant_type=COORDINATION_TARGET_TOPOLOGY,
            participant_reference_id=topology.identity.topology_id,
            coordination_ids=coordination_ids,
            participant_state=COORDINATION_STATE_SUPPORTED,
            deterministic_order=2,
            governance_metadata_reference="v4_3_coordination_topology_participant_governance_metadata",
            continuity_metadata_reference="v4_3_coordination_topology_participant_continuity_metadata",
            provenance_metadata_reference="v4_3_coordination_topology_participant_provenance_metadata",
            lineage_metadata_reference="v4_3_coordination_topology_participant_lineage_metadata",
        ),
        CoordinationParticipant(
            participant_id="v4_3_coordination_participant_capability",
            participant_type=COORDINATION_TARGET_CAPABILITY,
            participant_reference_id=capability.identity.capability_set_id,
            coordination_ids=coordination_ids,
            participant_state=COORDINATION_STATE_BLOCKED,
            deterministic_order=3,
            governance_metadata_reference="v4_3_coordination_capability_participant_governance_metadata",
            continuity_metadata_reference="v4_3_coordination_capability_participant_continuity_metadata",
            provenance_metadata_reference="v4_3_coordination_capability_participant_provenance_metadata",
            lineage_metadata_reference="v4_3_coordination_capability_participant_lineage_metadata",
        ),
        CoordinationParticipant(
            participant_id="v4_3_coordination_participant_policy",
            participant_type=COORDINATION_TARGET_POLICY,
            participant_reference_id=policy.identity.policy_set_id,
            coordination_ids=coordination_ids,
            participant_state=COORDINATION_STATE_BLOCKED,
            deterministic_order=4,
            governance_metadata_reference="v4_3_coordination_policy_participant_governance_metadata",
            continuity_metadata_reference="v4_3_coordination_policy_participant_continuity_metadata",
            provenance_metadata_reference="v4_3_coordination_policy_participant_provenance_metadata",
            lineage_metadata_reference="v4_3_coordination_policy_participant_lineage_metadata",
        ),
        CoordinationParticipant(
            participant_id="v4_3_coordination_participant_transition",
            participant_type=COORDINATION_TARGET_TRANSITION,
            participant_reference_id=transition.identity.transition_set_id,
            coordination_ids=coordination_ids,
            participant_state=COORDINATION_STATE_STALE,
            deterministic_order=5,
            governance_metadata_reference="v4_3_coordination_transition_participant_governance_metadata",
            continuity_metadata_reference="v4_3_coordination_transition_participant_continuity_metadata",
            provenance_metadata_reference="v4_3_coordination_transition_participant_provenance_metadata",
            lineage_metadata_reference="v4_3_coordination_transition_participant_lineage_metadata",
        ),
        CoordinationParticipant(
            participant_id="v4_3_coordination_participant_boundary",
            participant_type=COORDINATION_TARGET_BOUNDARY,
            participant_reference_id="v4_3_coordination_boundary_non_execution_and_non_coordination",
            coordination_ids=coordination_ids,
            participant_state=COORDINATION_STATE_PROHIBITED,
            deterministic_order=6,
            governance_metadata_reference="v4_3_coordination_boundary_participant_governance_metadata",
            continuity_metadata_reference="v4_3_coordination_boundary_participant_continuity_metadata",
            provenance_metadata_reference="v4_3_coordination_boundary_participant_provenance_metadata",
            lineage_metadata_reference="v4_3_coordination_boundary_participant_lineage_metadata",
        ),
    )


def default_coordination_relationships(
    coordinations: tuple[CoordinationRecord, ...],
    participants: tuple[CoordinationParticipant, ...],
) -> tuple[CoordinationRelationship, ...]:
    participant_by_type = {participant.participant_type: participant for participant in participants}
    relationship_types = (
        COORDINATION_RELATIONSHIP_TO_MANIFEST,
        COORDINATION_RELATIONSHIP_TO_TOPOLOGY,
        COORDINATION_RELATIONSHIP_TO_CAPABILITY,
        COORDINATION_RELATIONSHIP_TO_POLICY,
        COORDINATION_RELATIONSHIP_TO_TRANSITION,
        COORDINATION_RELATIONSHIP_TO_BOUNDARY,
    )
    relationships: list[CoordinationRelationship] = []
    relationship_order = 1
    for coordination in coordinations:
        for relationship_type in relationship_types:
            target_type = COORDINATION_RELATIONSHIP_TARGET_TYPES[relationship_type]
            target = participant_by_type[target_type]
            relationships.append(
                CoordinationRelationship(
                    relationship_id=f"{coordination.coordination_id}_{relationship_type}",
                    relationship_type=relationship_type,
                    source_coordination_id=coordination.coordination_id,
                    target_reference_id=target.participant_reference_id,
                    target_reference_type=target.participant_type,
                    relationship_state=coordination.support_state,
                    deterministic_order=relationship_order,
                    fail_visible=coordination.support_state in FAIL_VISIBLE_COORDINATION_STATES,
                )
            )
            relationship_order += 1
    return tuple(relationships)


def default_coordination_support_state_visibility(
    coordinations: tuple[CoordinationRecord, ...],
) -> CoordinationSupportStateVisibility:
    return CoordinationSupportStateVisibility(
        prohibited_coordination_ids=tuple(
            coordination.coordination_id
            for coordination in coordinations
            if coordination.support_state == COORDINATION_STATE_PROHIBITED
            or coordination.coordination_classification in PROHIBITED_COORDINATION_CLASSIFICATIONS
        ),
        unsupported_coordination_ids=tuple(
            coordination.coordination_id
            for coordination in coordinations
            if coordination.support_state == COORDINATION_STATE_UNSUPPORTED
            or coordination.coordination_classification in UNSUPPORTED_COORDINATION_CLASSIFICATIONS
        ),
        blocked_coordination_ids=tuple(
            coordination.coordination_id
            for coordination in coordinations
            if coordination.support_state == COORDINATION_STATE_BLOCKED
        ),
        stale_coordination_ids=tuple(
            coordination.coordination_id
            for coordination in coordinations
            if coordination.support_state == COORDINATION_STATE_STALE
        ),
        conflicting_coordination_ids=tuple(
            coordination.coordination_id
            for coordination in coordinations
            if coordination.support_state == COORDINATION_STATE_CONFLICTING
        ),
        unknown_coordination_ids=tuple(
            coordination.coordination_id
            for coordination in coordinations
            if coordination.support_state == COORDINATION_STATE_UNKNOWN
        ),
        prohibited_classifications=PROHIBITED_COORDINATION_CLASSIFICATIONS,
        unsupported_classifications=UNSUPPORTED_COORDINATION_CLASSIFICATIONS,
        deterministic_order=1,
    )


def default_coordination_continuity_metadata(
    coordinations: tuple[CoordinationRecord, ...],
    participants: tuple[CoordinationParticipant, ...],
    relationships: tuple[CoordinationRelationship, ...],
) -> tuple[CoordinationContinuityMetadata, ...]:
    return (
        CoordinationContinuityMetadata(
            continuity_id="v4_3_coordination_continuity_replay_and_rollback",
            coordination_references=tuple(coordination.coordination_id for coordination in coordinations),
            participant_references=tuple(participant.participant_id for participant in participants),
            relationship_references=tuple(relationship.relationship_id for relationship in relationships),
            replay_evidence_reference="v4_3_coordination_replay_safe_evidence",
            rollback_evidence_reference="v4_3_coordination_rollback_safe_evidence",
            provenance_reference="v4_3_coordination_provenance_primary",
            lineage_reference="v4_3_coordination_lineage_primary",
            deterministic_order=1,
        ),
    )


def default_coordination_diagnostics(
    coordinations: tuple[CoordinationRecord, ...],
) -> tuple[CoordinationDiagnostic, ...]:
    prohibited_ids = tuple(
        coordination.coordination_id
        for coordination in coordinations
        if coordination.support_state == COORDINATION_STATE_PROHIBITED
    )
    unsupported_ids = tuple(
        coordination.coordination_id
        for coordination in coordinations
        if coordination.support_state == COORDINATION_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        coordination.coordination_id
        for coordination in coordinations
        if coordination.support_state == COORDINATION_STATE_BLOCKED
    )
    stale_ids = tuple(
        coordination.coordination_id
        for coordination in coordinations
        if coordination.support_state == COORDINATION_STATE_STALE
    )
    conflicting_ids = tuple(
        coordination.coordination_id
        for coordination in coordinations
        if coordination.support_state == COORDINATION_STATE_CONFLICTING
    )
    all_ids = tuple(coordination.coordination_id for coordination in coordinations)
    return (
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_identity_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_IDENTITY,
            severity="info",
            message="Coordination identity is modeled as deterministic descriptive governance evidence.",
            affected_coordination_ids=(),
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=1,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_unsupported_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            message="Unsupported coordination classifications are fail-visible and not inferred into runtime coordination.",
            affected_coordination_ids=unsupported_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=2,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_blocked_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_BLOCKED,
            severity="blocker",
            message="Blocked coordination states remain descriptive and cannot activate orchestration behavior.",
            affected_coordination_ids=blocked_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=3,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_stale_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_STALE,
            severity="warning",
            message="Stale coordination context is visible without repair or correction.",
            affected_coordination_ids=stale_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=4,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_conflicting_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_CONFLICTING,
            severity="blocker",
            message="Conflicting coordination claims are visible without dispatch or authorization.",
            affected_coordination_ids=conflicting_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=5,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_prohibited_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            message="Operational coordination and orchestration dispatch are explicitly prohibited.",
            affected_coordination_ids=prohibited_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=6,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_relationship_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_RELATIONSHIP,
            severity="info",
            message="Coordination relationships are visible as governance evidence only and cannot dispatch or route.",
            affected_coordination_ids=all_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=7,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_non_coordination_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_NON_COORDINATION,
            severity="prohibited",
            message="Coordination visibility explicitly certifies enabled_coordination_execution_count equals 0.",
            affected_coordination_ids=all_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=8,
        ),
        CoordinationDiagnostic(
            diagnostic_id="v4_3_coordination_non_execution_diagnostic",
            diagnostic_category=COORDINATION_DIAGNOSTIC_NON_EXECUTION,
            severity="prohibited",
            message="Coordination visibility certifies transition, policy, and operational capability counts remain 0.",
            affected_coordination_ids=all_ids,
            affected_participant_ids=(),
            affected_relationship_ids=(),
            deterministic_order=9,
        ),
    )


def default_coordination_explainability() -> tuple[CoordinationExplainability, ...]:
    return (
        CoordinationExplainability(
            explanation_id="v4_3_coordination_prohibited_explanation",
            explanation_category="prohibited_coordination",
            summary="A coordination relationship is prohibited when it appears to enable dispatch, runtime coordination, orchestration execution, or operational flow.",
            affected_coordination_ids=("v4_3_coordination_dispatch_prohibited",),
            deterministic_order=1,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_unsupported_explanation",
            explanation_category="unsupported_coordination",
            summary="Unsupported coordination states remain visible as future governance surfaces without inference or runtime coordination.",
            affected_coordination_ids=("v4_3_coordination_future_runtime_contract",),
            deterministic_order=2,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_blocked_explanation",
            explanation_category="blocked_coordination",
            summary="A coordination relationship is blocked when it would imply operational coordination, which Phase 6 cannot perform.",
            affected_coordination_ids=("v4_3_coordination_operational_coordination_block",),
            deterministic_order=3,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_stale_explanation",
            explanation_category="stale_coordination",
            summary="Stale coordination context is reported deterministically and cannot be repaired automatically.",
            affected_coordination_ids=("v4_3_coordination_stale_transition_context",),
            deterministic_order=4,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_conflicting_explanation",
            explanation_category="conflicting_coordination",
            summary="Conflicting coordination claims are fail-visible because dispatch and runtime coordination remain unavailable.",
            affected_coordination_ids=("v4_3_coordination_conflicting_dispatch_claim",),
            deterministic_order=5,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_operational_unavailable_explanation",
            explanation_category="operational_coordination_unavailable",
            summary="Operational coordination remains unavailable because Phase 6 provides coordination visibility only.",
            affected_coordination_ids=("v4_3_coordination_operational_coordination_block",),
            deterministic_order=6,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_dispatch_unavailable_explanation",
            explanation_category="orchestration_dispatch_unavailable",
            summary="Orchestration dispatch remains unavailable because no dispatcher or coordination engine exists.",
            affected_coordination_ids=("v4_3_coordination_dispatch_prohibited",),
            deterministic_order=7,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_activation_unavailable_explanation",
            explanation_category="orchestration_activation_unavailable",
            summary="Orchestration activation remains unavailable because coordination records are descriptive governance evidence.",
            affected_coordination_ids=("v4_3_coordination_operational_coordination_block",),
            deterministic_order=8,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_planner_unavailable_explanation",
            explanation_category="planner_integration_unavailable",
            summary="Planner integration remains unavailable because coordination visibility cannot steer operational planning.",
            affected_coordination_ids=("v4_3_coordination_governance_relationship_visibility",),
            deterministic_order=9,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_production_unavailable_explanation",
            explanation_category="production_consumption_unavailable",
            summary="Production consumption remains unavailable because coordination evidence is replay-safe and rollback-safe descriptive output.",
            affected_coordination_ids=("v4_3_coordination_governance_relationship_visibility",),
            deterministic_order=10,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_governance_constraint_explanation",
            explanation_category="governance_constraints_exist",
            summary="Governance constraints exist to keep theoretical coordination auditable without operational runtime behavior.",
            affected_coordination_ids=("v4_3_coordination_governance_relationship_visibility",),
            deterministic_order=11,
        ),
        CoordinationExplainability(
            explanation_id="v4_3_coordination_runtime_prohibited_explanation",
            explanation_category="runtime_coordination_prohibited",
            summary="Runtime coordination remains prohibited because no coordination engine, dispatcher, runtime coordinator, or operational state machine exists.",
            affected_coordination_ids=("v4_3_coordination_dispatch_prohibited",),
            deterministic_order=12,
        ),
    )


def default_orchestration_coordination_visibility() -> OrchestrationCoordinationVisibility:
    identity = default_coordination_visibility_identity()
    coordinations = default_coordination_records()
    participants = default_coordination_participants(coordinations)
    relationships = default_coordination_relationships(coordinations, participants)
    return OrchestrationCoordinationVisibility(
        identity=identity,
        metadata=default_coordination_visibility_metadata(identity),
        coordinations=coordinations,
        participants=participants,
        relationships=relationships,
        support_state_visibility=default_coordination_support_state_visibility(coordinations),
        continuity_metadata=default_coordination_continuity_metadata(
            coordinations,
            participants,
            relationships,
        ),
        diagnostics=default_coordination_diagnostics(coordinations),
        explainability_summaries=default_coordination_explainability(),
    )
