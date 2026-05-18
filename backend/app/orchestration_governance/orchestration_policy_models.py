"""Deterministic v4.3 orchestration policy visibility models.

Policy visibility is descriptive governance evidence only. It models which
governance policies constrain manifests, topology, capabilities, and
boundaries while preserving explicit non-enforcement and non-execution
guarantees. No policy engine, authorization engine, activation pathway,
runtime behavior, planner behavior, or production consumption is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .orchestration_capability_hashing import hash_orchestration_capability_visibility
from .orchestration_capability_models import default_orchestration_capability_visibility
from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import default_orchestration_manifest
from .orchestration_topology_hashing import hash_orchestration_topology
from .orchestration_topology_models import default_orchestration_topology


V4_3_ORCHESTRATION_POLICY_PHASE_ID = "v4_3_orchestration_policy_visibility"
V4_3_ORCHESTRATION_POLICY_SCHEMA_VERSION = "v4_3.orchestration_policy_visibility.1"
V4_3_ORCHESTRATION_POLICY_REPORT_SCHEMA_VERSION = (
    "v4_3.orchestration_policy_visibility_report.1"
)
V4_3_ORCHESTRATION_POLICY_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_POLICY_STATUS_STABLE = "v4_3_orchestration_policy_visibility_stable"
V4_3_ORCHESTRATION_POLICY_STATUS_BLOCKED = "v4_3_orchestration_policy_visibility_blocked"
V4_3_ORCHESTRATION_POLICY_PURPOSE = "deterministic_orchestration_policy_governance_modeling_only"

POLICY_STATE_SUPPORTED = "supported"
POLICY_STATE_PROHIBITED = "prohibited"
POLICY_STATE_UNSUPPORTED = "unsupported"
POLICY_STATE_BLOCKED = "blocked"
POLICY_STATE_STALE = "stale"
POLICY_STATE_CONFLICTING = "conflicting"
POLICY_STATE_UNKNOWN = "unknown"
POLICY_STATES: tuple[str, ...] = (
    POLICY_STATE_SUPPORTED,
    POLICY_STATE_PROHIBITED,
    POLICY_STATE_UNSUPPORTED,
    POLICY_STATE_BLOCKED,
    POLICY_STATE_STALE,
    POLICY_STATE_CONFLICTING,
    POLICY_STATE_UNKNOWN,
)
FAIL_VISIBLE_POLICY_STATES: tuple[str, ...] = (
    POLICY_STATE_PROHIBITED,
    POLICY_STATE_UNSUPPORTED,
    POLICY_STATE_BLOCKED,
    POLICY_STATE_STALE,
    POLICY_STATE_CONFLICTING,
    POLICY_STATE_UNKNOWN,
)

POLICY_TARGET_MANIFEST = "manifest"
POLICY_TARGET_TOPOLOGY = "topology"
POLICY_TARGET_CAPABILITY = "capability"
POLICY_TARGET_BOUNDARY = "boundary"
POLICY_TARGET_TYPES: tuple[str, ...] = (
    POLICY_TARGET_MANIFEST,
    POLICY_TARGET_TOPOLOGY,
    POLICY_TARGET_CAPABILITY,
    POLICY_TARGET_BOUNDARY,
)

POLICY_RELATIONSHIP_TO_MANIFEST = "policy_to_manifest"
POLICY_RELATIONSHIP_TO_TOPOLOGY = "policy_to_topology"
POLICY_RELATIONSHIP_TO_CAPABILITY = "policy_to_capability"
POLICY_RELATIONSHIP_TO_BOUNDARY = "policy_to_boundary"
POLICY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    POLICY_RELATIONSHIP_TO_MANIFEST,
    POLICY_RELATIONSHIP_TO_TOPOLOGY,
    POLICY_RELATIONSHIP_TO_CAPABILITY,
    POLICY_RELATIONSHIP_TO_BOUNDARY,
)
POLICY_RELATIONSHIP_TARGET_TYPES: dict[str, str] = {
    POLICY_RELATIONSHIP_TO_MANIFEST: POLICY_TARGET_MANIFEST,
    POLICY_RELATIONSHIP_TO_TOPOLOGY: POLICY_TARGET_TOPOLOGY,
    POLICY_RELATIONSHIP_TO_CAPABILITY: POLICY_TARGET_CAPABILITY,
    POLICY_RELATIONSHIP_TO_BOUNDARY: POLICY_TARGET_BOUNDARY,
}

POLICY_DIAGNOSTIC_IDENTITY = "policy_identity_visibility"
POLICY_DIAGNOSTIC_DUPLICATE = "duplicate_policy_visibility"
POLICY_DIAGNOSTIC_TARGET = "policy_target_visibility"
POLICY_DIAGNOSTIC_PROHIBITED = "prohibited_policy_visibility"
POLICY_DIAGNOSTIC_UNSUPPORTED = "unsupported_policy_visibility"
POLICY_DIAGNOSTIC_BLOCKED = "blocked_policy_visibility"
POLICY_DIAGNOSTIC_STALE = "stale_policy_visibility"
POLICY_DIAGNOSTIC_CONFLICTING = "conflicting_policy_visibility"
POLICY_DIAGNOSTIC_METADATA = "metadata_visibility"
POLICY_DIAGNOSTIC_RELATIONSHIP = "relationship_visibility"
POLICY_DIAGNOSTIC_EXPLAINABILITY = "explainability_visibility"
POLICY_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"
POLICY_DIAGNOSTIC_NON_ENFORCEMENT = "non_enforcement_boundary_visibility"

PROHIBITED_POLICY_CLASSIFICATIONS: tuple[str, ...] = (
    "orchestration_execution",
    "policy_enforcement_execution",
    "runtime_execution",
    "policy_driven_routing",
    "policy_driven_traversal",
    "policy_driven_scheduling",
    "policy_driven_sequencing",
    "policy_driven_dependency_resolution",
    "policy_driven_activation",
    "orchestration_authorization",
    "readiness_approval",
    "operational_policy_mutation",
    "runtime_mutation",
    "planner_integration",
    "production_consumption",
    "remediation",
    "repair",
    "inference",
    "recommendations",
    "ranking",
    "scoring",
    "selection",
    "optimization",
    "dispatch",
    "operational_coordination",
    "state_machines",
    "hidden_enforcement_paths",
    "implicit_operational_authorization",
    "policy_engine_execution",
    "orchestration_engine",
    "authorization_engine",
    "activation_pathway",
)
UNSUPPORTED_POLICY_CLASSIFICATIONS: tuple[str, ...] = (
    "future_enforcement_contract",
    "future_policy_consumer",
    "future_authorization_surface",
)

EXPLICIT_ORCHESTRATION_POLICY_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 4 creates deterministic orchestration policy governance modeling only.",
    "v4.3 Phase 4 makes policy constraints visible before enforcement.",
    "v4.3 Phase 4 does not enable policy enforcement execution.",
    "v4.3 Phase 4 does not enable orchestration execution.",
    "v4.3 Phase 4 does not enable runtime execution.",
    "v4.3 Phase 4 does not enable policy-driven routing, traversal, scheduling, sequencing, dependency resolution, or activation.",
    "v4.3 Phase 4 does not enable orchestration authorization or readiness approval.",
    "v4.3 Phase 4 does not enable policy mutation, runtime mutation, planner integration, or production consumption.",
    "v4.3 Phase 4 does not enable remediation, repair, inference, recommendation, ranking, scoring, selection, or optimization.",
    "v4.3 Phase 4 does not enable dispatch, operational coordination, state machines, hidden enforcement paths, or implicit authorization.",
)

EXPLICIT_ORCHESTRATION_POLICY_PROHIBITIONS: tuple[str, ...] = (
    "No policy engine may execute.",
    "No orchestration engine may exist.",
    "No authorization engine may exist.",
    "No activation pathway may exist.",
    "No orchestration execution exists.",
    "No policy enforcement execution exists.",
    "No runtime execution exists.",
    "No policy-driven routing exists.",
    "No policy-driven traversal exists.",
    "No policy-driven scheduling exists.",
    "No policy-driven sequencing exists.",
    "No policy-driven dependency resolution exists.",
    "No policy-driven activation exists.",
    "No orchestration authorization exists.",
    "No readiness approval exists.",
    "No operational policy mutation exists.",
    "No runtime mutation exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No remediation exists.",
    "No repair exists.",
    "No inference exists.",
    "No recommendation exists.",
    "No ranking exists.",
    "No scoring exists.",
    "No selection exists.",
    "No optimization exists.",
    "No dispatch exists.",
    "No operational coordination exists.",
    "No state machine exists.",
    "No hidden enforcement path exists.",
    "No implicit operational authorization exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class PolicyVisibilityIdentity:
    policy_set_id: str
    policy_set_version: str
    policy_set_classification: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_topology_reference: str
    source_topology_hash_reference: str
    source_capability_reference: str
    source_capability_hash_reference: str
    schema_version: str
    generated_at: str
    governance_reference: str
    policy_scope_reference: str
    policy_target_reference: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    diagnostics_reference: str
    explainability_reference: str
    non_enforcement_reference: str
    non_execution_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_POLICY_PURPOSE
    non_enforceable: bool = True
    non_executable: bool = True
    descriptive_only: bool = True
    policy_enforcement_enabled: bool = False
    policy_enforcement_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class PolicyVisibilityMetadata:
    metadata_id: str
    phase_id: str
    policy_set_classification: str
    source_phase_references: tuple[str, ...]
    source_report_references: tuple[str, ...]
    governance_metadata_reference: str
    policy_scope_metadata_reference: str
    policy_target_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    non_enforcement_metadata_reference: str
    non_execution_metadata_reference: str
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_POLICY_PURPOSE
    deterministic: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_enforcing: bool = True
    non_authorizing: bool = True
    non_executing: bool = True
    policy_enforcement_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_phase_references", "source_report_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PolicyRecord:
    policy_id: str
    policy_name: str
    policy_classification: str
    policy_scope: str
    policy_severity: str
    support_state: str
    target_ids: tuple[str, ...]
    deterministic_order: int
    prohibited_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    blocked_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    conflicting_reason_visibility: tuple[str, ...] = ()
    governance_metadata_reference: str = "v4_3_policy_governance_metadata"
    continuity_metadata_reference: str = "v4_3_policy_continuity_metadata"
    provenance_metadata_reference: str = "v4_3_policy_provenance_metadata"
    lineage_metadata_reference: str = "v4_3_policy_lineage_metadata"
    diagnostics_metadata_reference: str = "v4_3_policy_diagnostics_metadata"
    explainability_metadata_reference: str = "v4_3_policy_explainability_metadata"
    policy_visible: bool = True
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    enforceable: bool = False
    authorizing: bool = False
    activation_capable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    orchestration_execution_enabled: bool = False
    policy_enforcement_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    policy_driven_routing_enabled: bool = False
    policy_driven_traversal_enabled: bool = False
    policy_driven_scheduling_enabled: bool = False
    policy_driven_sequencing_enabled: bool = False
    policy_driven_dependency_resolution_enabled: bool = False
    policy_driven_activation_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "target_ids",
            "prohibited_reason_visibility",
            "unsupported_reason_visibility",
            "blocked_reason_visibility",
            "stale_reason_visibility",
            "conflicting_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PolicyTarget:
    target_id: str
    target_type: str
    target_reference_id: str
    policy_ids: tuple[str, ...]
    target_state: str
    deterministic_order: int
    governance_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    enforceable: bool = False
    authorizing: bool = False
    activation_capable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "policy_ids")


@dataclass(frozen=True)
class PolicyRelationship:
    relationship_id: str
    relationship_type: str
    source_policy_id: str
    target_reference_id: str
    target_reference_type: str
    relationship_state: str
    deterministic_order: int
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    enforceable: bool = False
    authorizing: bool = False
    activation_capable: bool = False
    routable: bool = False
    traversable: bool = False
    schedulable: bool = False
    planner_integrated: bool = False
    production_consuming: bool = False
    policy_enforcement_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    policy_driven_routing_enabled: bool = False
    policy_driven_traversal_enabled: bool = False
    policy_driven_scheduling_enabled: bool = False
    policy_driven_sequencing_enabled: bool = False
    policy_driven_dependency_resolution_enabled: bool = False
    policy_driven_activation_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class PolicySupportStateVisibility:
    prohibited_policy_ids: tuple[str, ...]
    unsupported_policy_ids: tuple[str, ...]
    blocked_policy_ids: tuple[str, ...]
    stale_policy_ids: tuple[str, ...]
    conflicting_policy_ids: tuple[str, ...]
    unknown_policy_ids: tuple[str, ...]
    prohibited_classifications: tuple[str, ...]
    unsupported_classifications: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    policy_enforcement_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_policy_ids",
            "unsupported_policy_ids",
            "blocked_policy_ids",
            "stale_policy_ids",
            "conflicting_policy_ids",
            "unknown_policy_ids",
            "prohibited_classifications",
            "unsupported_classifications",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PolicyContinuityMetadata:
    continuity_id: str
    policy_references: tuple[str, ...]
    target_references: tuple[str, ...]
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
    policy_enforcement_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("policy_references", "target_references", "relationship_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PolicyDiagnostic:
    diagnostic_id: str
    diagnostic_category: str
    severity: str
    message: str
    affected_policy_ids: tuple[str, ...]
    affected_target_ids: tuple[str, ...]
    affected_relationship_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    authorization_enabled: bool = False
    operational_mutation_enabled: bool = False
    policy_enforcement_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_policy_ids", "affected_target_ids", "affected_relationship_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class PolicyExplainability:
    explanation_id: str
    explanation_category: str
    summary: str
    affected_policy_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    policy_enforcement_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_policy_ids")


@dataclass(frozen=True)
class OrchestrationPolicyVisibility:
    identity: PolicyVisibilityIdentity
    metadata: PolicyVisibilityMetadata
    policies: tuple[PolicyRecord, ...]
    targets: tuple[PolicyTarget, ...]
    relationships: tuple[PolicyRelationship, ...]
    support_state_visibility: PolicySupportStateVisibility
    continuity_metadata: tuple[PolicyContinuityMetadata, ...]
    diagnostics: tuple[PolicyDiagnostic, ...]
    explainability_summaries: tuple[PolicyExplainability, ...]
    policy_visibility_classification: str = "governance_safe_policy_visibility_descriptive_only"
    non_enforceable: bool = True
    non_executable: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    policy_enforcement_enabled: bool = False
    policy_enforcement_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    policy_driven_routing_enabled: bool = False
    policy_driven_traversal_enabled: bool = False
    policy_driven_scheduling_enabled: bool = False
    policy_driven_sequencing_enabled: bool = False
    policy_driven_dependency_resolution_enabled: bool = False
    policy_driven_activation_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    operational_policy_mutation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    dispatch_enabled: bool = False
    operational_coordination_enabled: bool = False
    state_machine_enabled: bool = False
    hidden_enforcement_path_enabled: bool = False
    implicit_operational_authorization_enabled: bool = False
    policy_engine_execution_enabled: bool = False
    orchestration_engine_enabled: bool = False
    authorization_engine_enabled: bool = False
    activation_pathway_enabled: bool = False
    operational_capability_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "policies",
            "targets",
            "relationships",
            "continuity_metadata",
            "diagnostics",
            "explainability_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_policy_visibility_identity() -> PolicyVisibilityIdentity:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    return PolicyVisibilityIdentity(
        policy_set_id="v4_3_orchestration_policy_visibility_primary",
        policy_set_version="v4.3.0-phase-4",
        policy_set_classification="descriptive_only_policy_governance_visibility",
        source_manifest_reference=manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_orchestration_manifest(manifest),
        source_topology_reference=topology.identity.topology_id,
        source_topology_hash_reference=hash_orchestration_topology(topology),
        source_capability_reference=capability.identity.capability_set_id,
        source_capability_hash_reference=hash_orchestration_capability_visibility(capability),
        schema_version=V4_3_ORCHESTRATION_POLICY_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_POLICY_GENERATED_AT,
        governance_reference="v4_3_policy_governance_primary",
        policy_scope_reference="v4_3_policy_scope_primary",
        policy_target_reference="v4_3_policy_target_primary",
        lineage_reference="v4_3_policy_lineage_primary",
        provenance_reference="v4_3_policy_provenance_primary",
        continuity_reference="v4_3_policy_continuity_primary",
        diagnostics_reference="v4_3_policy_diagnostics_primary",
        explainability_reference="v4_3_policy_explainability_primary",
        non_enforcement_reference="v4_3_policy_non_enforcement_primary",
        non_execution_reference="v4_3_policy_non_execution_primary",
    )


def default_policy_visibility_metadata(identity: PolicyVisibilityIdentity) -> PolicyVisibilityMetadata:
    return PolicyVisibilityMetadata(
        metadata_id="v4_3_orchestration_policy_visibility_metadata",
        phase_id=V4_3_ORCHESTRATION_POLICY_PHASE_ID,
        policy_set_classification=identity.policy_set_classification,
        source_phase_references=(
            "v4_3_orchestration_manifest_foundations",
            "v4_3_orchestration_topology_visibility",
            "v4_3_orchestration_boundary_and_capability_visibility",
        ),
        source_report_references=(
            "docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            "docs/generated/v4_3_orchestration_topology_visibility_report.json",
            "docs/generated/v4_3_orchestration_boundary_and_capability_visibility_report.json",
        ),
        governance_metadata_reference="v4_3_policy_governance_metadata",
        policy_scope_metadata_reference="v4_3_policy_scope_metadata",
        policy_target_metadata_reference="v4_3_policy_target_metadata",
        continuity_metadata_reference="v4_3_policy_continuity_metadata",
        provenance_metadata_reference="v4_3_policy_provenance_metadata",
        lineage_metadata_reference="v4_3_policy_lineage_metadata",
        diagnostics_metadata_reference="v4_3_policy_diagnostics_metadata",
        explainability_metadata_reference="v4_3_policy_explainability_metadata",
        non_enforcement_metadata_reference="v4_3_policy_non_enforcement_metadata",
        non_execution_metadata_reference="v4_3_policy_non_execution_metadata",
        deterministic_order=1,
    )


def default_policy_records() -> tuple[PolicyRecord, ...]:
    all_target_ids = (
        "v4_3_policy_target_manifest_foundations",
        "v4_3_policy_target_topology_visibility",
        "v4_3_policy_target_capability_visibility",
        "v4_3_policy_target_non_execution_boundary",
    )
    return (
        PolicyRecord(
            policy_id="v4_3_policy_governance_constraint_visibility",
            policy_name="Governance Constraint Visibility",
            policy_classification="governance_constraint_visibility",
            policy_scope="manifest_topology_capability_boundary",
            policy_severity="info",
            support_state=POLICY_STATE_SUPPORTED,
            target_ids=all_target_ids,
            deterministic_order=1,
        ),
        PolicyRecord(
            policy_id="v4_3_policy_future_enforcement_contract",
            policy_name="Future Enforcement Contract Visibility",
            policy_classification="future_enforcement_contract",
            policy_scope="policy_surface",
            policy_severity="warning",
            support_state=POLICY_STATE_UNSUPPORTED,
            target_ids=all_target_ids,
            deterministic_order=2,
            unsupported_reason_visibility=(
                "future policy enforcement contracts are visible but unsupported in Phase 4",
            ),
            fail_visible=True,
        ),
        PolicyRecord(
            policy_id="v4_3_policy_orchestration_activation_block",
            policy_name="Orchestration Activation Block",
            policy_classification="orchestration_activation_block",
            policy_scope="capability_boundary",
            policy_severity="blocker",
            support_state=POLICY_STATE_BLOCKED,
            target_ids=all_target_ids,
            deterministic_order=3,
            blocked_reason_visibility=(
                "policy visibility cannot activate orchestration capabilities",
            ),
            fail_visible=True,
        ),
        PolicyRecord(
            policy_id="v4_3_policy_stale_topology_context",
            policy_name="Stale Topology Context Visibility",
            policy_classification="stale_topology_context",
            policy_scope="topology_relationship",
            policy_severity="warning",
            support_state=POLICY_STATE_STALE,
            target_ids=("v4_3_policy_target_topology_visibility",),
            deterministic_order=4,
            stale_reason_visibility=(
                "policy context captures stale topology evidence as descriptive visibility",
            ),
            fail_visible=True,
        ),
        PolicyRecord(
            policy_id="v4_3_policy_conflicting_authorization_claim",
            policy_name="Conflicting Authorization Claim Visibility",
            policy_classification="conflicting_authorization_claim",
            policy_scope="manifest_capability_boundary",
            policy_severity="blocker",
            support_state=POLICY_STATE_CONFLICTING,
            target_ids=(
                "v4_3_policy_target_manifest_foundations",
                "v4_3_policy_target_capability_visibility",
                "v4_3_policy_target_non_execution_boundary",
            ),
            deterministic_order=5,
            conflicting_reason_visibility=(
                "authorization claims conflict with explicit non-enforcement boundaries",
            ),
            fail_visible=True,
        ),
        PolicyRecord(
            policy_id="v4_3_policy_enforcement_execution_prohibited",
            policy_name="Policy Enforcement Execution Prohibited",
            policy_classification="policy_enforcement_execution",
            policy_scope="non_enforcement_boundary",
            policy_severity="prohibited",
            support_state=POLICY_STATE_PROHIBITED,
            target_ids=all_target_ids,
            deterministic_order=6,
            prohibited_reason_visibility=(
                "Phase 4 policy visibility cannot execute policy enforcement",
                "policy engine execution is explicitly prohibited",
            ),
            fail_visible=True,
        ),
    )


def default_policy_targets(policies: tuple[PolicyRecord, ...]) -> tuple[PolicyTarget, ...]:
    policy_ids = tuple(policy.policy_id for policy in policies)
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    return (
        PolicyTarget(
            target_id="v4_3_policy_target_manifest_foundations",
            target_type=POLICY_TARGET_MANIFEST,
            target_reference_id=manifest.identity.manifest_id,
            policy_ids=policy_ids,
            target_state=POLICY_STATE_SUPPORTED,
            deterministic_order=1,
            governance_metadata_reference="v4_3_policy_manifest_target_governance_metadata",
            continuity_metadata_reference="v4_3_policy_manifest_target_continuity_metadata",
            provenance_metadata_reference="v4_3_policy_manifest_target_provenance_metadata",
            lineage_metadata_reference="v4_3_policy_manifest_target_lineage_metadata",
        ),
        PolicyTarget(
            target_id="v4_3_policy_target_topology_visibility",
            target_type=POLICY_TARGET_TOPOLOGY,
            target_reference_id=topology.identity.topology_id,
            policy_ids=policy_ids,
            target_state=POLICY_STATE_STALE,
            deterministic_order=2,
            governance_metadata_reference="v4_3_policy_topology_target_governance_metadata",
            continuity_metadata_reference="v4_3_policy_topology_target_continuity_metadata",
            provenance_metadata_reference="v4_3_policy_topology_target_provenance_metadata",
            lineage_metadata_reference="v4_3_policy_topology_target_lineage_metadata",
        ),
        PolicyTarget(
            target_id="v4_3_policy_target_capability_visibility",
            target_type=POLICY_TARGET_CAPABILITY,
            target_reference_id=capability.identity.capability_set_id,
            policy_ids=policy_ids,
            target_state=POLICY_STATE_BLOCKED,
            deterministic_order=3,
            governance_metadata_reference="v4_3_policy_capability_target_governance_metadata",
            continuity_metadata_reference="v4_3_policy_capability_target_continuity_metadata",
            provenance_metadata_reference="v4_3_policy_capability_target_provenance_metadata",
            lineage_metadata_reference="v4_3_policy_capability_target_lineage_metadata",
        ),
        PolicyTarget(
            target_id="v4_3_policy_target_non_execution_boundary",
            target_type=POLICY_TARGET_BOUNDARY,
            target_reference_id="v4_3_policy_boundary_non_execution_and_non_enforcement",
            policy_ids=policy_ids,
            target_state=POLICY_STATE_PROHIBITED,
            deterministic_order=4,
            governance_metadata_reference="v4_3_policy_boundary_target_governance_metadata",
            continuity_metadata_reference="v4_3_policy_boundary_target_continuity_metadata",
            provenance_metadata_reference="v4_3_policy_boundary_target_provenance_metadata",
            lineage_metadata_reference="v4_3_policy_boundary_target_lineage_metadata",
        ),
    )


def default_policy_relationships(
    policies: tuple[PolicyRecord, ...],
    targets: tuple[PolicyTarget, ...],
) -> tuple[PolicyRelationship, ...]:
    relationships: list[PolicyRelationship] = []
    relationship_order = 1
    relationship_types = (
        POLICY_RELATIONSHIP_TO_MANIFEST,
        POLICY_RELATIONSHIP_TO_TOPOLOGY,
        POLICY_RELATIONSHIP_TO_CAPABILITY,
        POLICY_RELATIONSHIP_TO_BOUNDARY,
    )
    target_by_type = {target.target_type: target for target in targets}
    for policy in policies:
        for relationship_type in relationship_types:
            target_type = POLICY_RELATIONSHIP_TARGET_TYPES[relationship_type]
            target = target_by_type[target_type]
            relationships.append(
                PolicyRelationship(
                    relationship_id=f"{policy.policy_id}_{relationship_type}",
                    relationship_type=relationship_type,
                    source_policy_id=policy.policy_id,
                    target_reference_id=target.target_reference_id,
                    target_reference_type=target.target_type,
                    relationship_state=policy.support_state,
                    deterministic_order=relationship_order,
                    fail_visible=policy.support_state in FAIL_VISIBLE_POLICY_STATES,
                )
            )
            relationship_order += 1
    return tuple(relationships)


def default_policy_support_state_visibility(
    policies: tuple[PolicyRecord, ...],
) -> PolicySupportStateVisibility:
    return PolicySupportStateVisibility(
        prohibited_policy_ids=tuple(
            policy.policy_id
            for policy in policies
            if policy.support_state == POLICY_STATE_PROHIBITED
            or policy.policy_classification in PROHIBITED_POLICY_CLASSIFICATIONS
        ),
        unsupported_policy_ids=tuple(
            policy.policy_id
            for policy in policies
            if policy.support_state == POLICY_STATE_UNSUPPORTED
            or policy.policy_classification in UNSUPPORTED_POLICY_CLASSIFICATIONS
        ),
        blocked_policy_ids=tuple(
            policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_BLOCKED
        ),
        stale_policy_ids=tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_STALE),
        conflicting_policy_ids=tuple(
            policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_CONFLICTING
        ),
        unknown_policy_ids=tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_UNKNOWN),
        prohibited_classifications=PROHIBITED_POLICY_CLASSIFICATIONS,
        unsupported_classifications=UNSUPPORTED_POLICY_CLASSIFICATIONS,
        deterministic_order=1,
    )


def default_policy_continuity_metadata(
    policies: tuple[PolicyRecord, ...],
    targets: tuple[PolicyTarget, ...],
    relationships: tuple[PolicyRelationship, ...],
) -> tuple[PolicyContinuityMetadata, ...]:
    return (
        PolicyContinuityMetadata(
            continuity_id="v4_3_policy_continuity_replay_and_rollback",
            policy_references=tuple(policy.policy_id for policy in policies),
            target_references=tuple(target.target_id for target in targets),
            relationship_references=tuple(relationship.relationship_id for relationship in relationships),
            replay_evidence_reference="v4_3_policy_replay_safe_evidence",
            rollback_evidence_reference="v4_3_policy_rollback_safe_evidence",
            provenance_reference="v4_3_policy_provenance_primary",
            lineage_reference="v4_3_policy_lineage_primary",
            deterministic_order=1,
        ),
    )


def default_policy_diagnostics(policies: tuple[PolicyRecord, ...]) -> tuple[PolicyDiagnostic, ...]:
    prohibited_ids = tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_PROHIBITED)
    unsupported_ids = tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_UNSUPPORTED)
    blocked_ids = tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_BLOCKED)
    stale_ids = tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_STALE)
    conflicting_ids = tuple(policy.policy_id for policy in policies if policy.support_state == POLICY_STATE_CONFLICTING)
    return (
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_identity_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_IDENTITY,
            severity="info",
            message="Policy identity is modeled as deterministic descriptive governance evidence.",
            affected_policy_ids=(),
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=1,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_unsupported_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            message="Unsupported policy classifications are fail-visible and not inferred into enforcement.",
            affected_policy_ids=unsupported_ids,
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=2,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_blocked_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_BLOCKED,
            severity="blocker",
            message="Blocked policy states remain descriptive and cannot activate orchestration behavior.",
            affected_policy_ids=blocked_ids,
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=3,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_stale_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_STALE,
            severity="warning",
            message="Stale policy context is visible without repair or correction.",
            affected_policy_ids=stale_ids,
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=4,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_conflicting_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_CONFLICTING,
            severity="blocker",
            message="Conflicting policy metadata is visible without authorization or mutation.",
            affected_policy_ids=conflicting_ids,
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=5,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_prohibited_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            message="Policy enforcement execution is explicitly prohibited and fail-visible.",
            affected_policy_ids=prohibited_ids,
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=6,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_relationship_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_RELATIONSHIP,
            severity="info",
            message="Policy relationships are visible as target evidence only and cannot route or traverse.",
            affected_policy_ids=tuple(policy.policy_id for policy in policies),
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=7,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_non_enforcement_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_NON_ENFORCEMENT,
            severity="prohibited",
            message="Policy visibility explicitly certifies enabled_policy_enforcement_count equals 0.",
            affected_policy_ids=tuple(policy.policy_id for policy in policies),
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=8,
        ),
        PolicyDiagnostic(
            diagnostic_id="v4_3_policy_non_execution_diagnostic",
            diagnostic_category=POLICY_DIAGNOSTIC_NON_EXECUTION,
            severity="prohibited",
            message="Policy visibility explicitly certifies enabled_operational_capability_count equals 0.",
            affected_policy_ids=tuple(policy.policy_id for policy in policies),
            affected_target_ids=(),
            affected_relationship_ids=(),
            deterministic_order=9,
        ),
    )


def default_policy_explainability() -> tuple[PolicyExplainability, ...]:
    return (
        PolicyExplainability(
            explanation_id="v4_3_policy_prohibited_explanation",
            explanation_category="prohibited_policy",
            summary="A policy is prohibited when it appears to enable enforcement, execution, authorization, activation, or production consumption.",
            affected_policy_ids=("v4_3_policy_enforcement_execution_prohibited",),
            deterministic_order=1,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_unsupported_explanation",
            explanation_category="unsupported_policy",
            summary="Unsupported policy classifications remain visible as future governance surfaces without inference or enforcement.",
            affected_policy_ids=("v4_3_policy_future_enforcement_contract",),
            deterministic_order=2,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_blocked_explanation",
            explanation_category="blocked_policy",
            summary="A policy is blocked when it would imply orchestration activation, which Phase 4 cannot perform.",
            affected_policy_ids=("v4_3_policy_orchestration_activation_block",),
            deterministic_order=3,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_stale_explanation",
            explanation_category="stale_policy",
            summary="Stale policy context is reported deterministically and cannot be repaired automatically.",
            affected_policy_ids=("v4_3_policy_stale_topology_context",),
            deterministic_order=4,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_conflicting_explanation",
            explanation_category="conflicting_policy",
            summary="Conflicting policy claims are fail-visible because authorization remains unavailable.",
            affected_policy_ids=("v4_3_policy_conflicting_authorization_claim",),
            deterministic_order=5,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_enforcement_unavailable_explanation",
            explanation_category="policy_enforcement_unavailable",
            summary="Policy enforcement remains unavailable because Phase 4 provides policy visibility only.",
            affected_policy_ids=("v4_3_policy_enforcement_execution_prohibited",),
            deterministic_order=6,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_authorization_unavailable_explanation",
            explanation_category="authorization_unavailable",
            summary="Authorization remains unavailable because policy models cannot approve readiness or execution.",
            affected_policy_ids=("v4_3_policy_conflicting_authorization_claim",),
            deterministic_order=7,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_activation_unavailable_explanation",
            explanation_category="activation_unavailable",
            summary="Orchestration activation remains unavailable because policies are descriptive governance evidence.",
            affected_policy_ids=("v4_3_policy_orchestration_activation_block",),
            deterministic_order=8,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_execution_unavailable_explanation",
            explanation_category="execution_unavailable",
            summary="Execution remains unavailable because no orchestration engine, policy engine, or activation pathway exists.",
            affected_policy_ids=("v4_3_policy_enforcement_execution_prohibited",),
            deterministic_order=9,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_planner_integration_unavailable_explanation",
            explanation_category="planner_integration_unavailable",
            summary="Planner integration remains unavailable because Phase 4 cannot consume or steer operational planning.",
            affected_policy_ids=("v4_3_policy_governance_constraint_visibility",),
            deterministic_order=10,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_production_consumption_unavailable_explanation",
            explanation_category="production_consumption_unavailable",
            summary="Production consumption remains unavailable because policy evidence is replay-safe and rollback-safe descriptive output.",
            affected_policy_ids=("v4_3_policy_governance_constraint_visibility",),
            deterministic_order=11,
        ),
        PolicyExplainability(
            explanation_id="v4_3_policy_governance_constraint_explanation",
            explanation_category="governance_constraints_exist",
            summary="Governance constraints exist to keep manifests, topology, capabilities, and boundaries auditable without operational control.",
            affected_policy_ids=("v4_3_policy_governance_constraint_visibility",),
            deterministic_order=12,
        ),
    )


def default_orchestration_policy_visibility() -> OrchestrationPolicyVisibility:
    identity = default_policy_visibility_identity()
    policies = default_policy_records()
    targets = default_policy_targets(policies)
    relationships = default_policy_relationships(policies, targets)
    return OrchestrationPolicyVisibility(
        identity=identity,
        metadata=default_policy_visibility_metadata(identity),
        policies=policies,
        targets=targets,
        relationships=relationships,
        support_state_visibility=default_policy_support_state_visibility(policies),
        continuity_metadata=default_policy_continuity_metadata(policies, targets, relationships),
        diagnostics=default_policy_diagnostics(policies),
        explainability_summaries=default_policy_explainability(),
    )
