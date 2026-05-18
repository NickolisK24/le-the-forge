"""Deterministic v4.3 orchestration boundary and capability visibility models.

Capability visibility is descriptive governance evidence only. It models what
capabilities exist, where governance boundaries are located, and why capability
activation remains unavailable without execution, routing, traversal,
scheduling, sequencing, authorization, planner integration, dispatch,
coordination, production consumption, or mutation behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import default_orchestration_manifest
from .orchestration_topology_hashing import hash_orchestration_topology
from .orchestration_topology_models import default_orchestration_topology


V4_3_ORCHESTRATION_CAPABILITY_PHASE_ID = "v4_3_orchestration_boundary_and_capability_visibility"
V4_3_ORCHESTRATION_CAPABILITY_SCHEMA_VERSION = (
    "v4_3.orchestration_boundary_and_capability_visibility.1"
)
V4_3_ORCHESTRATION_CAPABILITY_REPORT_SCHEMA_VERSION = (
    "v4_3.orchestration_boundary_and_capability_visibility_report.1"
)
V4_3_ORCHESTRATION_CAPABILITY_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_CAPABILITY_STATUS_STABLE = "v4_3_orchestration_capability_visibility_stable"
V4_3_ORCHESTRATION_CAPABILITY_STATUS_BLOCKED = "v4_3_orchestration_capability_visibility_blocked"
V4_3_ORCHESTRATION_CAPABILITY_PURPOSE = (
    "deterministic_orchestration_capability_governance_modeling_only"
)

CAPABILITY_STATE_SUPPORTED = "supported"
CAPABILITY_STATE_PROHIBITED = "prohibited"
CAPABILITY_STATE_UNSUPPORTED = "unsupported"
CAPABILITY_STATE_BLOCKED = "blocked"
CAPABILITY_STATE_STALE = "stale"
CAPABILITY_STATE_CONFLICTING = "conflicting"
CAPABILITY_STATE_UNKNOWN = "unknown"
CAPABILITY_STATES: tuple[str, ...] = (
    CAPABILITY_STATE_SUPPORTED,
    CAPABILITY_STATE_PROHIBITED,
    CAPABILITY_STATE_UNSUPPORTED,
    CAPABILITY_STATE_BLOCKED,
    CAPABILITY_STATE_STALE,
    CAPABILITY_STATE_CONFLICTING,
    CAPABILITY_STATE_UNKNOWN,
)
FAIL_VISIBLE_CAPABILITY_STATES: tuple[str, ...] = (
    CAPABILITY_STATE_PROHIBITED,
    CAPABILITY_STATE_UNSUPPORTED,
    CAPABILITY_STATE_BLOCKED,
    CAPABILITY_STATE_STALE,
    CAPABILITY_STATE_CONFLICTING,
    CAPABILITY_STATE_UNKNOWN,
)

CAPABILITY_RELATIONSHIP_TO_BOUNDARY = "capability_to_boundary"
CAPABILITY_RELATIONSHIP_TO_POLICY = "capability_to_policy"
CAPABILITY_RELATIONSHIP_TO_TOPOLOGY = "capability_to_topology"
CAPABILITY_RELATIONSHIP_TO_MANIFEST = "capability_to_manifest"
CAPABILITY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    CAPABILITY_RELATIONSHIP_TO_BOUNDARY,
    CAPABILITY_RELATIONSHIP_TO_POLICY,
    CAPABILITY_RELATIONSHIP_TO_TOPOLOGY,
    CAPABILITY_RELATIONSHIP_TO_MANIFEST,
)

CAPABILITY_DIAGNOSTIC_IDENTITY = "capability_identity_visibility"
CAPABILITY_DIAGNOSTIC_DUPLICATE = "duplicate_capability_visibility"
CAPABILITY_DIAGNOSTIC_PROHIBITED = "prohibited_capability_visibility"
CAPABILITY_DIAGNOSTIC_UNSUPPORTED = "unsupported_capability_visibility"
CAPABILITY_DIAGNOSTIC_BLOCKED = "blocked_capability_visibility"
CAPABILITY_DIAGNOSTIC_STALE = "stale_capability_visibility"
CAPABILITY_DIAGNOSTIC_CONFLICTING = "conflicting_capability_visibility"
CAPABILITY_DIAGNOSTIC_METADATA = "metadata_visibility"
CAPABILITY_DIAGNOSTIC_RELATIONSHIP = "relationship_visibility"
CAPABILITY_DIAGNOSTIC_EXPLAINABILITY = "explainability_visibility"
CAPABILITY_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_CAPABILITY_CLASSIFICATIONS: tuple[str, ...] = (
    "orchestration_execution",
    "orchestration_activation",
    "runtime_execution",
    "capability_execution",
    "routing_execution",
    "traversal_execution",
    "dependency_execution",
    "sequencing_execution",
    "scheduling_execution",
    "operational_state_mutation",
    "runtime_mutation",
    "orchestration_authorization",
    "readiness_approval",
    "remediation_systems",
    "automatic_repair",
    "inference_systems",
    "orchestration_recommendations",
    "orchestration_ranking",
    "orchestration_scoring",
    "orchestration_selection",
    "optimization_systems",
    "orchestration_planning_engines",
    "orchestration_decision_systems",
    "orchestration_resolution_systems",
    "planner_integration",
    "production_consumption",
    "orchestration_dispatch",
    "orchestration_runtime_coordination",
    "orchestration_state_machines",
    "hidden_orchestration_pathways",
    "implicit_operational_authorization",
)
UNSUPPORTED_CAPABILITY_CLASSIFICATIONS: tuple[str, ...] = (
    "future_runtime_coordination",
    "future_policy_surface",
    "future_capability_consumer",
)

EXPLICIT_ORCHESTRATION_CAPABILITY_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 3 creates deterministic orchestration capability governance modeling only.",
    "v4.3 Phase 3 makes capability boundaries visible before activation.",
    "v4.3 Phase 3 does not enable orchestration execution.",
    "v4.3 Phase 3 does not enable orchestration activation.",
    "v4.3 Phase 3 does not enable runtime execution.",
    "v4.3 Phase 3 does not enable capability execution.",
    "v4.3 Phase 3 does not enable routing, traversal, dependency, sequencing, or scheduling execution.",
    "v4.3 Phase 3 does not enable authorization or readiness approval.",
    "v4.3 Phase 3 does not enable remediation, repair, inference, recommendation, ranking, scoring, selection, or optimization.",
    "v4.3 Phase 3 does not enable planning, decision, resolution, dispatch, or runtime coordination engines.",
    "v4.3 Phase 3 does not enable planner integration.",
    "v4.3 Phase 3 does not enable production consumption.",
    "v4.3 Phase 3 does not enable runtime or operational state mutation.",
)

EXPLICIT_ORCHESTRATION_CAPABILITY_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration capability may become executable.",
    "No orchestration activation exists.",
    "No orchestration execution exists.",
    "No runtime execution exists.",
    "No capability execution exists.",
    "No routing execution exists.",
    "No traversal execution exists.",
    "No dependency execution exists.",
    "No sequencing execution exists.",
    "No scheduling execution exists.",
    "No operational state mutation exists.",
    "No runtime mutation exists.",
    "No orchestration authorization exists.",
    "No readiness approval exists.",
    "No remediation system exists.",
    "No automatic repair exists.",
    "No inference system exists.",
    "No orchestration recommendation exists.",
    "No orchestration ranking exists.",
    "No orchestration scoring exists.",
    "No orchestration selection exists.",
    "No optimization system exists.",
    "No orchestration planning engine exists.",
    "No orchestration decision engine exists.",
    "No orchestration resolution system exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No orchestration dispatch exists.",
    "No operational runtime coordination exists.",
    "No orchestration state machine exists.",
    "No hidden orchestration pathway exists.",
    "No implicit operational authorization exists.",
    "No operational orchestration engine exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CapabilityVisibilityIdentity:
    capability_set_id: str
    capability_set_version: str
    capability_set_classification: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_topology_reference: str
    source_topology_hash_reference: str
    schema_version: str
    generated_at: str
    governance_reference: str
    operational_boundary_reference: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    diagnostics_reference: str
    explainability_reference: str
    non_execution_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_CAPABILITY_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    capability_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    dependency_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_coordination_enabled: bool = False


@dataclass(frozen=True)
class CapabilityVisibilityMetadata:
    metadata_id: str
    phase_id: str
    capability_set_classification: str
    source_phase_references: tuple[str, ...]
    source_report_references: tuple[str, ...]
    governance_boundary_metadata_reference: str
    operational_boundary_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    non_execution_metadata_reference: str
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_CAPABILITY_PURPOSE
    deterministic: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    non_executing: bool = True
    non_activating: bool = True
    non_routing: bool = True
    non_traversing: bool = True
    non_scheduling: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    capability_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_phase_references", "source_report_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CapabilityRecord:
    capability_id: str
    capability_name: str
    capability_category: str
    capability_classification: str
    support_state: str
    governance_boundary_id: str
    operational_boundary_id: str
    policy_reference: str
    topology_reference: str
    manifest_reference: str
    deterministic_order: int
    prohibited_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    blocked_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    conflicting_reason_visibility: tuple[str, ...] = ()
    governance_metadata_reference: str = "v4_3_capability_governance_metadata"
    operational_boundary_metadata_reference: str = "v4_3_capability_operational_boundary_metadata"
    continuity_metadata_reference: str = "v4_3_capability_continuity_metadata"
    provenance_metadata_reference: str = "v4_3_capability_provenance_metadata"
    lineage_metadata_reference: str = "v4_3_capability_lineage_metadata"
    diagnostics_metadata_reference: str = "v4_3_capability_diagnostics_metadata"
    explainability_metadata_reference: str = "v4_3_capability_explainability_metadata"
    capability_visible: bool = True
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    operationally_enabled: bool = False
    authorized: bool = False
    schedulable: bool = False
    routable: bool = False
    planner_integrated: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    capability_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    dependency_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    remediation_system_enabled: bool = False
    automatic_repair_enabled: bool = False
    inference_system_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    planning_engine_enabled: bool = False
    decision_system_enabled: bool = False
    resolution_system_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_coordination_enabled: bool = False

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
class CapabilityGovernanceBoundary:
    boundary_id: str
    boundary_name: str
    boundary_classification: str
    boundary_state: str
    capability_ids: tuple[str, ...]
    prohibited_capability_ids: tuple[str, ...]
    unsupported_capability_ids: tuple[str, ...]
    deterministic_order: int
    governance_metadata_reference: str
    operational_boundary_metadata_reference: str
    fail_visible: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("capability_ids", "prohibited_capability_ids", "unsupported_capability_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CapabilityRelationship:
    relationship_id: str
    relationship_type: str
    source_capability_id: str
    target_reference_id: str
    target_reference_type: str
    relationship_state: str
    deterministic_order: int
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    routable: bool = False
    traversable: bool = False
    schedulable: bool = False
    authorized: bool = False
    planner_integrated: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class CapabilitySupportStateVisibility:
    visibility_id: str
    prohibited_capability_ids: tuple[str, ...]
    unsupported_capability_ids: tuple[str, ...]
    blocked_capability_ids: tuple[str, ...]
    stale_capability_ids: tuple[str, ...]
    conflicting_capability_ids: tuple[str, ...]
    unknown_capability_ids: tuple[str, ...]
    prohibited_classifications: tuple[str, ...]
    unsupported_classifications: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    correction_enabled: bool = False
    inference_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_capability_ids",
            "unsupported_capability_ids",
            "blocked_capability_ids",
            "stale_capability_ids",
            "conflicting_capability_ids",
            "unknown_capability_ids",
            "prohibited_classifications",
            "unsupported_classifications",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CapabilityContinuityMetadata:
    continuity_id: str
    continuity_type: str
    continuity_state: str
    capability_references: tuple[str, ...]
    boundary_references: tuple[str, ...]
    relationship_references: tuple[str, ...]
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
    capability_continuity_visible: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("capability_references", "boundary_references", "relationship_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CapabilityDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_capability_ids: tuple[str, ...]
    affected_boundary_ids: tuple[str, ...]
    affected_relationship_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    correction_enabled: bool = False
    inference_enabled: bool = False
    authorization_enabled: bool = False
    operational_mutation_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    capability_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    dependency_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_capability_ids", "affected_boundary_ids", "affected_relationship_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CapabilityExplainability:
    explanation_id: str
    category: str
    summary: str
    affected_capability_ids: tuple[str, ...]
    deterministic_order: int
    deterministic: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    correction_enabled: bool = False
    inference_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_capability_ids")


@dataclass(frozen=True)
class OrchestrationCapabilityVisibility:
    identity: CapabilityVisibilityIdentity
    metadata: CapabilityVisibilityMetadata
    capabilities: tuple[CapabilityRecord, ...]
    boundaries: tuple[CapabilityGovernanceBoundary, ...]
    relationships: tuple[CapabilityRelationship, ...]
    support_state_visibility: CapabilitySupportStateVisibility
    continuity_metadata: tuple[CapabilityContinuityMetadata, ...]
    diagnostics: tuple[CapabilityDiagnostic, ...]
    explainability_summaries: tuple[CapabilityExplainability, ...]
    capability_visibility_classification: str = "governance_safe_capability_visibility_descriptive_only"
    non_executable: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_execution_enabled: bool = False
    capability_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    dependency_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    remediation_system_enabled: bool = False
    automatic_repair_enabled: bool = False
    inference_system_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    planning_engine_enabled: bool = False
    decision_system_enabled: bool = False
    resolution_system_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_coordination_enabled: bool = False
    state_machine_enabled: bool = False
    hidden_orchestration_pathway_enabled: bool = False
    implicit_operational_authorization_enabled: bool = False
    operational_orchestration_engine_enabled: bool = False
    orchestration_decision_engine_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "capabilities",
            "boundaries",
            "relationships",
            "continuity_metadata",
            "diagnostics",
            "explainability_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_capability_visibility_identity() -> CapabilityVisibilityIdentity:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    return CapabilityVisibilityIdentity(
        capability_set_id="v4_3_orchestration_capability_visibility_primary",
        capability_set_version="v4.3.0-phase-3",
        capability_set_classification="descriptive_only_capability_governance_visibility",
        source_manifest_reference=manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_orchestration_manifest(manifest),
        source_topology_reference=topology.identity.topology_id,
        source_topology_hash_reference=hash_orchestration_topology(topology),
        schema_version=V4_3_ORCHESTRATION_CAPABILITY_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_CAPABILITY_GENERATED_AT,
        governance_reference="v4_3_capability_governance_primary",
        operational_boundary_reference="v4_3_capability_operational_boundary_primary",
        lineage_reference="v4_3_capability_lineage_primary",
        provenance_reference="v4_3_capability_provenance_primary",
        continuity_reference="v4_3_capability_continuity_primary",
        diagnostics_reference="v4_3_capability_diagnostics_primary",
        explainability_reference="v4_3_capability_explainability_primary",
        non_execution_reference="v4_3_capability_non_execution_primary",
    )


def default_capability_visibility_metadata(
    identity: CapabilityVisibilityIdentity | None = None,
) -> CapabilityVisibilityMetadata:
    source = identity or default_capability_visibility_identity()
    return CapabilityVisibilityMetadata(
        metadata_id="v4_3_capability_metadata_primary",
        phase_id=V4_3_ORCHESTRATION_CAPABILITY_PHASE_ID,
        capability_set_classification=source.capability_set_classification,
        source_phase_references=(
            "v4_3_orchestration_manifest_foundations",
            "v4_3_orchestration_topology_visibility",
        ),
        source_report_references=(
            "docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            "docs/generated/v4_3_orchestration_topology_visibility_report.json",
        ),
        governance_boundary_metadata_reference=source.governance_reference,
        operational_boundary_metadata_reference=source.operational_boundary_reference,
        continuity_metadata_reference=source.continuity_reference,
        provenance_metadata_reference=source.provenance_reference,
        lineage_metadata_reference=source.lineage_reference,
        diagnostics_metadata_reference=source.diagnostics_reference,
        explainability_metadata_reference=source.explainability_reference,
        non_execution_metadata_reference=source.non_execution_reference,
        deterministic_order=10,
    )


def default_capability_records() -> tuple[CapabilityRecord, ...]:
    common = {
        "policy_reference": "v4_3_capability_policy_non_execution",
        "topology_reference": "v4_3_orchestration_topology_primary",
        "manifest_reference": "v4_3_orchestration_manifest_primary",
    }
    return (
        CapabilityRecord(
            capability_id="v4_3_capability_boundary_visibility",
            capability_name="boundary_visibility",
            capability_category="governance_visibility",
            capability_classification="descriptive_governance_boundary_visibility",
            support_state=CAPABILITY_STATE_SUPPORTED,
            governance_boundary_id="v4_3_boundary_non_execution",
            operational_boundary_id="v4_3_operational_boundary_no_activation",
            deterministic_order=10,
            **common,
        ),
        CapabilityRecord(
            capability_id="v4_3_capability_future_runtime_coordination",
            capability_name="future_runtime_coordination",
            capability_category="future_capability_region",
            capability_classification="future_runtime_coordination",
            support_state=CAPABILITY_STATE_UNSUPPORTED,
            governance_boundary_id="v4_3_boundary_unsupported_capabilities",
            operational_boundary_id="v4_3_operational_boundary_no_activation",
            deterministic_order=20,
            fail_visible=True,
            unsupported_reason_visibility=("future runtime coordination remains unsupported",),
            **common,
        ),
        CapabilityRecord(
            capability_id="v4_3_capability_orchestration_activation",
            capability_name="orchestration_activation",
            capability_category="operational_capability_region",
            capability_classification="orchestration_activation",
            support_state=CAPABILITY_STATE_BLOCKED,
            governance_boundary_id="v4_3_boundary_blocked_activation",
            operational_boundary_id="v4_3_operational_boundary_no_activation",
            deterministic_order=30,
            fail_visible=True,
            blocked_reason_visibility=("orchestration activation is blocked by descriptive-only capability governance",),
            **common,
        ),
        CapabilityRecord(
            capability_id="v4_3_capability_prior_topology_context",
            capability_name="prior_topology_context",
            capability_category="topology_context_region",
            capability_classification="prior_topology_context",
            support_state=CAPABILITY_STATE_STALE,
            governance_boundary_id="v4_3_boundary_stale_topology_context",
            operational_boundary_id="v4_3_operational_boundary_read_only_context",
            deterministic_order=40,
            fail_visible=True,
            stale_reason_visibility=("Phase 2 topology evidence is read-only ancestry for capability visibility",),
            **common,
        ),
        CapabilityRecord(
            capability_id="v4_3_capability_execution_authorization",
            capability_name="execution_authorization",
            capability_category="authorization_region",
            capability_classification="orchestration_authorization",
            support_state=CAPABILITY_STATE_CONFLICTING,
            governance_boundary_id="v4_3_boundary_conflicting_authorization",
            operational_boundary_id="v4_3_operational_boundary_no_authorization",
            deterministic_order=50,
            fail_visible=True,
            conflicting_reason_visibility=("execution authorization conflicts with non-execution capability governance",),
            **common,
        ),
        CapabilityRecord(
            capability_id="v4_3_capability_runtime_execution",
            capability_name="runtime_execution",
            capability_category="prohibited_operational_region",
            capability_classification="runtime_execution",
            support_state=CAPABILITY_STATE_PROHIBITED,
            governance_boundary_id="v4_3_boundary_prohibited_execution",
            operational_boundary_id="v4_3_operational_boundary_no_execution",
            deterministic_order=60,
            fail_visible=True,
            prohibited_reason_visibility=("runtime execution capabilities are prohibited",),
            **common,
        ),
    )


def default_capability_boundaries(
    capabilities: tuple[CapabilityRecord, ...] | None = None,
) -> tuple[CapabilityGovernanceBoundary, ...]:
    capability_records = capabilities or default_capability_records()
    capability_ids = tuple(capability.capability_id for capability in capability_records)
    prohibited_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_PROHIBITED
        or capability.capability_classification in PROHIBITED_CAPABILITY_CLASSIFICATIONS
    )
    unsupported_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_UNSUPPORTED
    )
    return (
        CapabilityGovernanceBoundary(
            boundary_id="v4_3_boundary_non_execution",
            boundary_name="non_execution_boundary",
            boundary_classification="governance_boundary",
            boundary_state=CAPABILITY_STATE_SUPPORTED,
            capability_ids=capability_ids,
            prohibited_capability_ids=prohibited_ids,
            unsupported_capability_ids=unsupported_ids,
            deterministic_order=10,
            governance_metadata_reference="v4_3_capability_governance_primary",
            operational_boundary_metadata_reference="v4_3_capability_operational_boundary_primary",
        ),
        CapabilityGovernanceBoundary(
            boundary_id="v4_3_boundary_prohibited_execution",
            boundary_name="prohibited_execution_boundary",
            boundary_classification="prohibited_capability_region",
            boundary_state=CAPABILITY_STATE_PROHIBITED,
            capability_ids=prohibited_ids,
            prohibited_capability_ids=prohibited_ids,
            unsupported_capability_ids=(),
            deterministic_order=20,
            governance_metadata_reference="v4_3_capability_governance_primary",
            operational_boundary_metadata_reference="v4_3_capability_operational_boundary_no_execution",
        ),
        CapabilityGovernanceBoundary(
            boundary_id="v4_3_boundary_unsupported_capabilities",
            boundary_name="unsupported_capability_boundary",
            boundary_classification="unsupported_capability_region",
            boundary_state=CAPABILITY_STATE_UNSUPPORTED,
            capability_ids=unsupported_ids,
            prohibited_capability_ids=(),
            unsupported_capability_ids=unsupported_ids,
            deterministic_order=30,
            governance_metadata_reference="v4_3_capability_governance_primary",
            operational_boundary_metadata_reference="v4_3_capability_operational_boundary_unsupported",
        ),
        CapabilityGovernanceBoundary(
            boundary_id="v4_3_boundary_blocked_activation",
            boundary_name="blocked_activation_boundary",
            boundary_classification="blocked_capability_region",
            boundary_state=CAPABILITY_STATE_BLOCKED,
            capability_ids=tuple(
                capability.capability_id
                for capability in capability_records
                if capability.support_state == CAPABILITY_STATE_BLOCKED
            ),
            prohibited_capability_ids=(),
            unsupported_capability_ids=(),
            deterministic_order=40,
            governance_metadata_reference="v4_3_capability_governance_primary",
            operational_boundary_metadata_reference="v4_3_capability_operational_boundary_blocked",
        ),
        CapabilityGovernanceBoundary(
            boundary_id="v4_3_boundary_stale_topology_context",
            boundary_name="stale_topology_context_boundary",
            boundary_classification="stale_capability_region",
            boundary_state=CAPABILITY_STATE_STALE,
            capability_ids=tuple(
                capability.capability_id
                for capability in capability_records
                if capability.support_state == CAPABILITY_STATE_STALE
            ),
            prohibited_capability_ids=(),
            unsupported_capability_ids=(),
            deterministic_order=50,
            governance_metadata_reference="v4_3_capability_governance_primary",
            operational_boundary_metadata_reference="v4_3_capability_operational_boundary_read_only_context",
        ),
        CapabilityGovernanceBoundary(
            boundary_id="v4_3_boundary_conflicting_authorization",
            boundary_name="conflicting_authorization_boundary",
            boundary_classification="conflicting_capability_region",
            boundary_state=CAPABILITY_STATE_CONFLICTING,
            capability_ids=tuple(
                capability.capability_id
                for capability in capability_records
                if capability.support_state == CAPABILITY_STATE_CONFLICTING
            ),
            prohibited_capability_ids=(),
            unsupported_capability_ids=(),
            deterministic_order=60,
            governance_metadata_reference="v4_3_capability_governance_primary",
            operational_boundary_metadata_reference="v4_3_capability_operational_boundary_no_authorization",
        ),
    )


def default_capability_relationships(
    capabilities: tuple[CapabilityRecord, ...] | None = None,
) -> tuple[CapabilityRelationship, ...]:
    capability_records = capabilities or default_capability_records()
    relationships: list[CapabilityRelationship] = []
    order = 10
    for capability in capability_records:
        relationships.extend(
            [
                CapabilityRelationship(
                    relationship_id=f"{capability.capability_id}_to_boundary",
                    relationship_type=CAPABILITY_RELATIONSHIP_TO_BOUNDARY,
                    source_capability_id=capability.capability_id,
                    target_reference_id=capability.governance_boundary_id,
                    target_reference_type="governance_boundary",
                    relationship_state=capability.support_state,
                    deterministic_order=order,
                    fail_visible=capability.fail_visible,
                ),
                CapabilityRelationship(
                    relationship_id=f"{capability.capability_id}_to_policy",
                    relationship_type=CAPABILITY_RELATIONSHIP_TO_POLICY,
                    source_capability_id=capability.capability_id,
                    target_reference_id=capability.policy_reference,
                    target_reference_type="policy_reference",
                    relationship_state=capability.support_state,
                    deterministic_order=order + 1,
                    fail_visible=capability.fail_visible,
                ),
                CapabilityRelationship(
                    relationship_id=f"{capability.capability_id}_to_topology",
                    relationship_type=CAPABILITY_RELATIONSHIP_TO_TOPOLOGY,
                    source_capability_id=capability.capability_id,
                    target_reference_id=capability.topology_reference,
                    target_reference_type="topology_reference",
                    relationship_state=capability.support_state,
                    deterministic_order=order + 2,
                    fail_visible=capability.fail_visible,
                ),
                CapabilityRelationship(
                    relationship_id=f"{capability.capability_id}_to_manifest",
                    relationship_type=CAPABILITY_RELATIONSHIP_TO_MANIFEST,
                    source_capability_id=capability.capability_id,
                    target_reference_id=capability.manifest_reference,
                    target_reference_type="manifest_reference",
                    relationship_state=capability.support_state,
                    deterministic_order=order + 3,
                    fail_visible=capability.fail_visible,
                ),
            ]
        )
        order += 10
    return tuple(relationships)


def default_capability_support_state_visibility(
    capabilities: tuple[CapabilityRecord, ...] | None = None,
) -> CapabilitySupportStateVisibility:
    capability_records = capabilities or default_capability_records()
    return CapabilitySupportStateVisibility(
        visibility_id="v4_3_capability_support_state_visibility_primary",
        prohibited_capability_ids=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.support_state == CAPABILITY_STATE_PROHIBITED
            or capability.capability_classification in PROHIBITED_CAPABILITY_CLASSIFICATIONS
        ),
        unsupported_capability_ids=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.support_state == CAPABILITY_STATE_UNSUPPORTED
        ),
        blocked_capability_ids=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.support_state == CAPABILITY_STATE_BLOCKED
        ),
        stale_capability_ids=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.support_state == CAPABILITY_STATE_STALE
        ),
        conflicting_capability_ids=tuple(
            capability.capability_id
            for capability in capability_records
            if capability.support_state == CAPABILITY_STATE_CONFLICTING
        ),
        unknown_capability_ids=("v4_3_capability_future_consumer_unknown",),
        prohibited_classifications=PROHIBITED_CAPABILITY_CLASSIFICATIONS,
        unsupported_classifications=UNSUPPORTED_CAPABILITY_CLASSIFICATIONS,
        deterministic_order=10,
    )


def default_capability_continuity_metadata(
    capabilities: tuple[CapabilityRecord, ...] | None = None,
    boundaries: tuple[CapabilityGovernanceBoundary, ...] | None = None,
    relationships: tuple[CapabilityRelationship, ...] | None = None,
) -> tuple[CapabilityContinuityMetadata, ...]:
    capability_records = capabilities or default_capability_records()
    boundary_records = boundaries or default_capability_boundaries(capability_records)
    relationship_records = relationships or default_capability_relationships(capability_records)
    capability_ids = tuple(capability.capability_id for capability in capability_records)
    boundary_ids = tuple(boundary.boundary_id for boundary in boundary_records)
    relationship_ids = tuple(relationship.relationship_id for relationship in relationship_records)
    return (
        CapabilityContinuityMetadata(
            continuity_id="v4_3_capability_continuity_identity",
            continuity_type="capability_identity_continuity",
            continuity_state=CAPABILITY_STATE_SUPPORTED,
            capability_references=capability_ids,
            boundary_references=boundary_ids,
            relationship_references=relationship_ids,
            replay_reference="v4_3_capability_serialization_snapshot",
            rollback_reference="v4_3_capability_hash_snapshot",
            provenance_reference="v4_3_capability_provenance_primary",
            lineage_reference="v4_3_capability_lineage_primary",
            deterministic_hash_reference="v4_3_capability_identity_continuity_hash",
            deterministic_order=10,
        ),
        CapabilityContinuityMetadata(
            continuity_id="v4_3_capability_continuity_manifest_topology",
            continuity_type="manifest_topology_continuity",
            continuity_state=CAPABILITY_STATE_SUPPORTED,
            capability_references=capability_ids,
            boundary_references=boundary_ids,
            relationship_references=relationship_ids,
            replay_reference="docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            rollback_reference="docs/generated/v4_3_orchestration_topology_visibility_report.json",
            provenance_reference="v4_3_capability_provenance_primary",
            lineage_reference="v4_3_capability_lineage_primary",
            deterministic_hash_reference="v4_3_capability_manifest_topology_continuity_hash",
            deterministic_order=20,
        ),
    )


def default_capability_diagnostics(
    capabilities: tuple[CapabilityRecord, ...] | None = None,
) -> tuple[CapabilityDiagnostic, ...]:
    capability_records = capabilities or default_capability_records()
    prohibited_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_PROHIBITED
    )
    unsupported_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_BLOCKED
    )
    stale_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_STALE
    )
    conflicting_ids = tuple(
        capability.capability_id
        for capability in capability_records
        if capability.support_state == CAPABILITY_STATE_CONFLICTING
    )
    return (
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_identity_visible",
            category=CAPABILITY_DIAGNOSTIC_IDENTITY,
            severity="info",
            finding="Capability identity is deterministic and non-executable.",
            affected_capability_ids=(),
            affected_boundary_ids=(),
            affected_relationship_ids=(),
            deterministic_order=10,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_prohibited_visible",
            category=CAPABILITY_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            finding="Prohibited capabilities remain visible and inactive.",
            affected_capability_ids=prohibited_ids,
            affected_boundary_ids=("v4_3_boundary_prohibited_execution",),
            affected_relationship_ids=(),
            deterministic_order=20,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_unsupported_visible",
            category=CAPABILITY_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            finding="Unsupported capabilities remain visible and unavailable.",
            affected_capability_ids=unsupported_ids,
            affected_boundary_ids=("v4_3_boundary_unsupported_capabilities",),
            affected_relationship_ids=(),
            deterministic_order=30,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_blocked_visible",
            category=CAPABILITY_DIAGNOSTIC_BLOCKED,
            severity="blocked",
            finding="Blocked orchestration activation capabilities remain non-operational.",
            affected_capability_ids=blocked_ids,
            affected_boundary_ids=("v4_3_boundary_blocked_activation",),
            affected_relationship_ids=(),
            deterministic_order=40,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_stale_visible",
            category=CAPABILITY_DIAGNOSTIC_STALE,
            severity="warning",
            finding="Stale topology context capabilities remain read-only ancestry.",
            affected_capability_ids=stale_ids,
            affected_boundary_ids=("v4_3_boundary_stale_topology_context",),
            affected_relationship_ids=(),
            deterministic_order=50,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_conflicting_visible",
            category=CAPABILITY_DIAGNOSTIC_CONFLICTING,
            severity="blocked",
            finding="Conflicting authorization capabilities remain blocked by non-execution governance.",
            affected_capability_ids=conflicting_ids,
            affected_boundary_ids=("v4_3_boundary_conflicting_authorization",),
            affected_relationship_ids=(),
            deterministic_order=60,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_relationships_visible",
            category=CAPABILITY_DIAGNOSTIC_RELATIONSHIP,
            severity="info",
            finding="Capability relationships to boundaries, policies, topology, and manifest remain descriptive.",
            affected_capability_ids=tuple(capability.capability_id for capability in capability_records),
            affected_boundary_ids=(),
            affected_relationship_ids=(),
            deterministic_order=70,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_explainability_visible",
            category=CAPABILITY_DIAGNOSTIC_EXPLAINABILITY,
            severity="info",
            finding="Capability explainability documents unavailable activation, execution, planner integration, and operations.",
            affected_capability_ids=tuple(capability.capability_id for capability in capability_records),
            affected_boundary_ids=(),
            affected_relationship_ids=(),
            deterministic_order=80,
        ),
        CapabilityDiagnostic(
            diagnostic_id="v4_3_capability_diagnostic_non_execution_visible",
            category=CAPABILITY_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Enabled operational capability count remains zero.",
            affected_capability_ids=tuple(capability.capability_id for capability in capability_records),
            affected_boundary_ids=(),
            affected_relationship_ids=(),
            deterministic_order=90,
        ),
    )


def default_capability_explainability() -> tuple[CapabilityExplainability, ...]:
    return (
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_prohibited",
            category="prohibited_capability",
            summary="Runtime execution is prohibited because capabilities are governance evidence only.",
            affected_capability_ids=("v4_3_capability_runtime_execution",),
            deterministic_order=10,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_unsupported",
            category="unsupported_capability",
            summary="Future runtime coordination is unsupported until explicitly authorized by a later phase.",
            affected_capability_ids=("v4_3_capability_future_runtime_coordination",),
            deterministic_order=20,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_blocked",
            category="blocked_capability",
            summary="Orchestration activation is blocked because Phase 3 does not activate capabilities.",
            affected_capability_ids=("v4_3_capability_orchestration_activation",),
            deterministic_order=30,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_stale",
            category="stale_capability",
            summary="Prior topology context is stale read-only ancestry, not an operational source.",
            affected_capability_ids=("v4_3_capability_prior_topology_context",),
            deterministic_order=40,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_conflicting",
            category="conflicting_capability",
            summary="Execution authorization conflicts with the explicit non-execution capability boundary.",
            affected_capability_ids=("v4_3_capability_execution_authorization",),
            deterministic_order=50,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_activation_unavailable",
            category="activation_unavailable",
            summary="Capability activation cannot occur because enabled operational capability count is zero.",
            affected_capability_ids=("v4_3_capability_orchestration_activation",),
            deterministic_order=60,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_execution_unavailable",
            category="execution_unavailable",
            summary="Execution remains unavailable across orchestration, runtime, capability, routing, traversal, dependency, sequencing, and scheduling surfaces.",
            affected_capability_ids=("v4_3_capability_runtime_execution",),
            deterministic_order=70,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_planner_unavailable",
            category="planner_integration_unavailable",
            summary="Planner integration remains unavailable because capability visibility does not alter planner behavior.",
            affected_capability_ids=("v4_3_capability_boundary_visibility",),
            deterministic_order=80,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_operational_prohibited",
            category="operational_orchestration_prohibited",
            summary="Operational orchestration remains prohibited without explicit authorization in a later phase.",
            affected_capability_ids=(
                "v4_3_capability_orchestration_activation",
                "v4_3_capability_runtime_execution",
            ),
            deterministic_order=90,
        ),
        CapabilityExplainability(
            explanation_id="v4_3_capability_explainability_governance_boundaries",
            category="governance_boundary",
            summary="Governance boundaries exist to keep capability evidence deterministic, replay-safe, rollback-safe, and non-executable.",
            affected_capability_ids=("v4_3_capability_boundary_visibility",),
            deterministic_order=100,
        ),
    )


def default_orchestration_capability_visibility() -> OrchestrationCapabilityVisibility:
    identity = default_capability_visibility_identity()
    capabilities = default_capability_records()
    boundaries = default_capability_boundaries(capabilities)
    relationships = default_capability_relationships(capabilities)
    return OrchestrationCapabilityVisibility(
        identity=identity,
        metadata=default_capability_visibility_metadata(identity),
        capabilities=capabilities,
        boundaries=boundaries,
        relationships=relationships,
        support_state_visibility=default_capability_support_state_visibility(capabilities),
        continuity_metadata=default_capability_continuity_metadata(capabilities, boundaries, relationships),
        diagnostics=default_capability_diagnostics(capabilities),
        explainability_summaries=default_capability_explainability(),
    )
