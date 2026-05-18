"""Deterministic v4.3 orchestration diagnostics aggregation models.

Diagnostics and explainability aggregation is descriptive governance evidence
only. It aggregates the visible diagnostics from orchestration manifests,
topology, capabilities, policies, transitions, and coordination without adding
orchestration intelligence, recommendations, decisions, activation, runtime
coordination, planner behavior, execution, or production consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .orchestration_capability_hashing import hash_orchestration_capability_visibility
from .orchestration_capability_models import default_orchestration_capability_visibility
from .orchestration_coordination_hashing import hash_orchestration_coordination_visibility
from .orchestration_coordination_models import default_orchestration_coordination_visibility
from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import default_orchestration_manifest
from .orchestration_policy_hashing import hash_orchestration_policy_visibility
from .orchestration_policy_models import default_orchestration_policy_visibility
from .orchestration_topology_hashing import hash_orchestration_topology
from .orchestration_topology_models import default_orchestration_topology
from .orchestration_transition_hashing import hash_orchestration_transition_visibility
from .orchestration_transition_models import default_orchestration_transition_visibility


V4_3_ORCHESTRATION_DIAGNOSTICS_PHASE_ID = (
    "v4_3_orchestration_diagnostics_and_explainability"
)
V4_3_ORCHESTRATION_DIAGNOSTICS_SCHEMA_VERSION = (
    "v4_3.orchestration_diagnostics_and_explainability.1"
)
V4_3_ORCHESTRATION_DIAGNOSTICS_REPORT_SCHEMA_VERSION = (
    "v4_3.orchestration_diagnostics_and_explainability_report.1"
)
V4_3_ORCHESTRATION_DIAGNOSTICS_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_STABLE = (
    "v4_3_orchestration_diagnostics_and_explainability_stable"
)
V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_BLOCKED = (
    "v4_3_orchestration_diagnostics_and_explainability_blocked"
)
V4_3_ORCHESTRATION_DIAGNOSTICS_PURPOSE = (
    "deterministic_orchestration_governance_diagnostics_aggregation_only"
)

GOVERNANCE_LAYER_MANIFEST = "manifest"
GOVERNANCE_LAYER_TOPOLOGY = "topology"
GOVERNANCE_LAYER_CAPABILITY = "capability"
GOVERNANCE_LAYER_POLICY = "policy"
GOVERNANCE_LAYER_TRANSITION = "transition"
GOVERNANCE_LAYER_COORDINATION = "coordination"
GOVERNANCE_LAYER_IDS: tuple[str, ...] = (
    GOVERNANCE_LAYER_MANIFEST,
    GOVERNANCE_LAYER_TOPOLOGY,
    GOVERNANCE_LAYER_CAPABILITY,
    GOVERNANCE_LAYER_POLICY,
    GOVERNANCE_LAYER_TRANSITION,
    GOVERNANCE_LAYER_COORDINATION,
)

CROSS_LAYER_STATE_PROHIBITED = "prohibited"
CROSS_LAYER_STATE_UNSUPPORTED = "unsupported"
CROSS_LAYER_STATE_BLOCKED = "blocked"
CROSS_LAYER_STATE_STALE = "stale"
CROSS_LAYER_STATE_CONFLICTING = "conflicting"
CROSS_LAYER_STATE_TYPES: tuple[str, ...] = (
    CROSS_LAYER_STATE_PROHIBITED,
    CROSS_LAYER_STATE_UNSUPPORTED,
    CROSS_LAYER_STATE_BLOCKED,
    CROSS_LAYER_STATE_STALE,
    CROSS_LAYER_STATE_CONFLICTING,
)

DIAGNOSTICS_AGGREGATION_SEVERITY_ORDER: tuple[str, ...] = (
    "info",
    "warning",
    "blocker",
    "prohibited",
)

EXPLICIT_ORCHESTRATION_DIAGNOSTICS_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 7 creates deterministic orchestration diagnostics aggregation only.",
    "v4.3 Phase 7 aggregates explainability before orchestration intelligence.",
    "v4.3 Phase 7 does not execute orchestration.",
    "v4.3 Phase 7 does not recommend orchestration actions.",
    "v4.3 Phase 7 does not rank, score, select, or optimize orchestration states.",
    "v4.3 Phase 7 does not make orchestration decisions.",
    "v4.3 Phase 7 does not authorize orchestration or approve readiness.",
    "v4.3 Phase 7 does not dispatch, activate, route, traverse, schedule, sequence, or resolve dependencies.",
    "v4.3 Phase 7 does not remediate, repair, infer, mutate runtime state, or mutate operational state.",
    "v4.3 Phase 7 does not integrate with planner systems or consume production bundles.",
)

EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration intelligence engine may exist.",
    "No orchestration recommendation engine may exist.",
    "No orchestration decision engine may exist.",
    "No orchestration execution exists.",
    "No orchestration intelligence execution exists.",
    "No orchestration recommendation exists.",
    "No orchestration ranking exists.",
    "No orchestration scoring exists.",
    "No orchestration selection exists.",
    "No orchestration optimization exists.",
    "No orchestration planning engine exists.",
    "No orchestration decision engine exists.",
    "No orchestration authorization exists.",
    "No readiness approval exists.",
    "No orchestration dispatch exists.",
    "No orchestration activation exists.",
    "No runtime coordination exists.",
    "No scheduling execution exists.",
    "No sequencing execution exists.",
    "No routing execution exists.",
    "No traversal execution exists.",
    "No dependency resolution exists.",
    "No remediation exists.",
    "No repair exists.",
    "No inference exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
    "No hidden orchestration pathway exists.",
    "No implicit operational authorization exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class DiagnosticsAggregationIdentity:
    aggregation_id: str
    aggregation_version: str
    aggregation_classification: str
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
    source_coordination_reference: str
    source_coordination_hash_reference: str
    schema_version: str
    generated_at: str
    governance_reference: str
    governance_layer_reference: str
    cross_layer_diagnostics_reference: str
    cross_layer_explainability_reference: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    non_execution_reference: str
    non_decision_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_DIAGNOSTICS_PURPOSE
    non_executable: bool = True
    non_decisioning: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_intelligence_execution_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DiagnosticsAggregationMetadata:
    metadata_id: str
    phase_id: str
    source_layer_ids: tuple[str, ...]
    source_phase_references: tuple[str, ...]
    source_report_references: tuple[str, ...]
    governance_metadata_reference: str
    continuity_metadata_reference: str
    provenance_metadata_reference: str
    lineage_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    non_execution_metadata_reference: str
    non_decision_metadata_reference: str
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_DIAGNOSTICS_PURPOSE
    deterministic: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_executing: bool = True
    non_decisioning: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_layer_ids", "source_phase_references", "source_report_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class GovernanceLayerDiagnosticSummary:
    layer_id: str
    layer_name: str
    source_reference_id: str
    source_hash_reference: str
    diagnostic_count: int
    explainability_count: int
    prohibited_state_count: int
    unsupported_state_count: int
    blocked_state_count: int
    stale_state_count: int
    conflicting_state_count: int
    continuity_diagnostic_count: int
    provenance_diagnostic_count: int
    lineage_diagnostic_count: int
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class AggregatedDiagnosticFinding:
    aggregated_diagnostic_id: str
    source_layer_id: str
    source_diagnostic_id: str
    diagnostic_category: str
    severity: str
    message: str
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    authorization_enabled: bool = False
    mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_reference_ids")


@dataclass(frozen=True)
class AggregatedExplainabilitySummary:
    aggregated_explanation_id: str
    source_layer_id: str
    source_explanation_id: str
    explanation_category: str
    summary: str
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_reference_ids")


@dataclass(frozen=True)
class CrossLayerStateSummary:
    state_summary_id: str
    state_type: str
    source_layer_ids: tuple[str, ...]
    affected_reference_ids: tuple[str, ...]
    diagnostic_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    state_count: int
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    orchestration_execution_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_layer_ids",
            "affected_reference_ids",
            "diagnostic_reference_ids",
            "explainability_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationDiagnosticsAggregation:
    identity: DiagnosticsAggregationIdentity
    metadata: DiagnosticsAggregationMetadata
    governance_layer_summaries: tuple[GovernanceLayerDiagnosticSummary, ...]
    diagnostics: tuple[AggregatedDiagnosticFinding, ...]
    explainability_summaries: tuple[AggregatedExplainabilitySummary, ...]
    cross_layer_state_summaries: tuple[CrossLayerStateSummary, ...]
    aggregation_classification: str = "governance_safe_diagnostics_aggregation_descriptive_only"
    non_executable: bool = True
    non_decisioning: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_intelligence_execution_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_activation_enabled: bool = False
    runtime_coordination_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
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
    hidden_orchestration_pathway_enabled: bool = False
    implicit_operational_authorization_enabled: bool = False
    enabled_coordination_execution_count: int = 0
    enabled_transition_execution_count: int = 0
    enabled_policy_enforcement_count: int = 0
    enabled_operational_capability_count: int = 0
    enabled_orchestration_decision_count: int = 0
    enabled_orchestration_recommendation_count: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "governance_layer_summaries",
            "diagnostics",
            "explainability_summaries",
            "cross_layer_state_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_diagnostics_aggregation_identity() -> DiagnosticsAggregationIdentity:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    transition = default_orchestration_transition_visibility()
    coordination = default_orchestration_coordination_visibility()
    return DiagnosticsAggregationIdentity(
        aggregation_id="v4_3_orchestration_diagnostics_and_explainability_primary",
        aggregation_version="v4.3.0-phase-7",
        aggregation_classification="descriptive_only_cross_layer_governance_diagnostics_aggregation",
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
        source_coordination_reference=coordination.identity.coordination_set_id,
        source_coordination_hash_reference=hash_orchestration_coordination_visibility(coordination),
        schema_version=V4_3_ORCHESTRATION_DIAGNOSTICS_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_DIAGNOSTICS_GENERATED_AT,
        governance_reference="v4_3_diagnostics_aggregation_governance_primary",
        governance_layer_reference="v4_3_diagnostics_aggregation_governance_layers_primary",
        cross_layer_diagnostics_reference="v4_3_cross_layer_diagnostics_primary",
        cross_layer_explainability_reference="v4_3_cross_layer_explainability_primary",
        lineage_reference="v4_3_diagnostics_aggregation_lineage_primary",
        provenance_reference="v4_3_diagnostics_aggregation_provenance_primary",
        continuity_reference="v4_3_diagnostics_aggregation_continuity_primary",
        non_execution_reference="v4_3_diagnostics_aggregation_non_execution_primary",
        non_decision_reference="v4_3_diagnostics_aggregation_non_decision_primary",
    )


def default_diagnostics_aggregation_metadata(
    identity: DiagnosticsAggregationIdentity,
) -> DiagnosticsAggregationMetadata:
    return DiagnosticsAggregationMetadata(
        metadata_id="v4_3_diagnostics_aggregation_metadata_primary",
        phase_id=V4_3_ORCHESTRATION_DIAGNOSTICS_PHASE_ID,
        source_layer_ids=GOVERNANCE_LAYER_IDS,
        source_phase_references=(
            "v4_3_phase_1_manifest_foundations",
            "v4_3_phase_2_topology_visibility",
            "v4_3_phase_3_boundary_and_capability_visibility",
            "v4_3_phase_4_policy_visibility",
            "v4_3_phase_5_transition_visibility",
            "v4_3_phase_6_coordination_visibility",
        ),
        source_report_references=(
            "docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            "docs/generated/v4_3_orchestration_topology_visibility_report.json",
            "docs/generated/v4_3_orchestration_boundary_and_capability_visibility_report.json",
            "docs/generated/v4_3_orchestration_policy_visibility_report.json",
            "docs/generated/v4_3_orchestration_transition_visibility_report.json",
            "docs/generated/v4_3_orchestration_coordination_visibility_report.json",
        ),
        governance_metadata_reference=identity.governance_reference,
        continuity_metadata_reference=identity.continuity_reference,
        provenance_metadata_reference=identity.provenance_reference,
        lineage_metadata_reference=identity.lineage_reference,
        diagnostics_metadata_reference=identity.cross_layer_diagnostics_reference,
        explainability_metadata_reference=identity.cross_layer_explainability_reference,
        non_execution_metadata_reference=identity.non_execution_reference,
        non_decision_metadata_reference=identity.non_decision_reference,
        deterministic_order=1,
    )
