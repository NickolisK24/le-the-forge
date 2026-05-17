"""Deterministic v4.2 coordination drift certification models.

Coordination drift certification is descriptive evidence only. It does not
correct drift, remediate drift, route requests, execute orchestration, execute
refreshes, execute sequences, schedule work, resolve dependencies, repair
lineage, infer lineage, consume production bundles, integrate with planners,
authorize behavior, roll back state, rank choices, score choices, select
options, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import (
    CoordinationDependencyGraph,
    default_coordination_dependency_graph,
)
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import CoordinationLineageChain, default_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .governance_routing_hashing import hash_governance_routing_visibility
from .governance_routing_models import GovernanceRoutingVisibility, default_governance_routing_visibility


V4_2_COORDINATION_DRIFT_PHASE_ID = "v4_2_coordination_drift_certification"
V4_2_COORDINATION_DRIFT_SCHEMA_VERSION = "v4_2.coordination_drift_certification.1"
V4_2_COORDINATION_DRIFT_REPORT_SCHEMA_VERSION = "v4_2.coordination_drift_certification_report.1"
V4_2_COORDINATION_DRIFT_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_COORDINATION_DRIFT_STATUS_STABLE = "v4_2_coordination_drift_certification_stable"
V4_2_COORDINATION_DRIFT_STATUS_BLOCKED = "v4_2_coordination_drift_certification_blocked"
V4_2_COORDINATION_DRIFT_PURPOSE = "deterministic_refresh_coordination_drift_certification_only"

DRIFT_STATE_STABLE = "stable"
DRIFT_STATE_STALE = "stale"
DRIFT_STATE_MISSING = "missing"
DRIFT_STATE_CONFLICTING = "conflicting"
DRIFT_STATE_PROHIBITED_CORRECTION = "prohibited_correction"
DRIFT_STATE_UNSUPPORTED_TRANSITION = "unsupported_transition"
DRIFT_STATE_CROSS_LAYER = "cross_layer"
DRIFT_STATE_UNKNOWN = "unknown"
DRIFT_STATES: tuple[str, ...] = (
    DRIFT_STATE_STABLE,
    DRIFT_STATE_STALE,
    DRIFT_STATE_MISSING,
    DRIFT_STATE_CONFLICTING,
    DRIFT_STATE_PROHIBITED_CORRECTION,
    DRIFT_STATE_UNSUPPORTED_TRANSITION,
    DRIFT_STATE_CROSS_LAYER,
    DRIFT_STATE_UNKNOWN,
)
FAIL_VISIBLE_DRIFT_STATES: tuple[str, ...] = (
    DRIFT_STATE_STALE,
    DRIFT_STATE_MISSING,
    DRIFT_STATE_CONFLICTING,
    DRIFT_STATE_PROHIBITED_CORRECTION,
    DRIFT_STATE_UNSUPPORTED_TRANSITION,
    DRIFT_STATE_CROSS_LAYER,
    DRIFT_STATE_UNKNOWN,
)

DRIFT_RELATIONSHIP_MANIFEST = "manifest_drift_reference"
DRIFT_RELATIONSHIP_DEPENDENCY_GRAPH = "dependency_graph_drift_reference"
DRIFT_RELATIONSHIP_LINEAGE_CHAIN = "lineage_chain_drift_reference"
DRIFT_RELATIONSHIP_SEQUENCING = "sequencing_drift_reference"
DRIFT_RELATIONSHIP_ROUTING = "routing_drift_reference"
DRIFT_RELATIONSHIP_CROSS_LAYER = "cross_layer_drift_reference"
DRIFT_RELATIONSHIP_TYPES: tuple[str, ...] = (
    DRIFT_RELATIONSHIP_MANIFEST,
    DRIFT_RELATIONSHIP_DEPENDENCY_GRAPH,
    DRIFT_RELATIONSHIP_LINEAGE_CHAIN,
    DRIFT_RELATIONSHIP_SEQUENCING,
    DRIFT_RELATIONSHIP_ROUTING,
    DRIFT_RELATIONSHIP_CROSS_LAYER,
)

DRIFT_DIAGNOSTIC_STALE = "stale_drift_visibility"
DRIFT_DIAGNOSTIC_MISSING = "missing_drift_visibility"
DRIFT_DIAGNOSTIC_CONFLICTING = "conflicting_drift_visibility"
DRIFT_DIAGNOSTIC_PROHIBITED_CORRECTION = "prohibited_drift_correction_visibility"
DRIFT_DIAGNOSTIC_UNSUPPORTED_TRANSITION = "unsupported_drift_transition_visibility"
DRIFT_DIAGNOSTIC_CROSS_LAYER = "cross_layer_drift_visibility"
DRIFT_DIAGNOSTIC_COMPATIBILITY = "coordination_drift_source_compatibility"
DRIFT_DIAGNOSTIC_NON_EXECUTION = "non_execution_and_non_remediation_boundary_visibility"

PROHIBITED_COORDINATION_DRIFT_CAPABILITIES: tuple[str, ...] = (
    "drift_correction",
    "drift_remediation",
    "routing_execution",
    "orchestration_execution",
    "refresh_execution",
    "sequencing_execution",
    "scheduling_execution",
    "dependency_resolution",
    "lineage_repair",
    "lineage_inference",
    "planner_integration",
    "production_bundle_consumption",
    "runtime_mutation",
    "remediation",
    "automatic_correction",
    "automatic_rollback",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "authorization_systems",
    "approval_systems",
    "operational_execution",
    "hidden_drift_correction",
    "implicit_execution_pathways",
)

EXPLICIT_COORDINATION_DRIFT_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 6 creates deterministic refresh coordination drift certification only.",
    "v4.2 Phase 6 does not enable drift correction.",
    "v4.2 Phase 6 does not enable drift remediation.",
    "v4.2 Phase 6 does not enable routing execution.",
    "v4.2 Phase 6 does not enable orchestration execution.",
    "v4.2 Phase 6 does not enable refresh execution.",
    "v4.2 Phase 6 does not enable sequencing execution.",
    "v4.2 Phase 6 does not enable scheduling execution.",
    "v4.2 Phase 6 does not enable dependency resolution.",
    "v4.2 Phase 6 does not enable lineage repair.",
    "v4.2 Phase 6 does not enable lineage inference.",
    "v4.2 Phase 6 does not enable planner integration.",
    "v4.2 Phase 6 does not enable production consumption.",
    "v4.2 Phase 6 does not enable runtime mutation.",
    "v4.2 Phase 6 does not enable automatic rollback.",
    "v4.2 Phase 6 does not enable ranking scoring or selection.",
    "v4.2 Phase 6 does not enable authorization or approval.",
)

EXPLICIT_COORDINATION_DRIFT_PROHIBITIONS: tuple[str, ...] = (
    "No drift correction exists.",
    "No drift remediation exists.",
    "No routing execution exists.",
    "No orchestration execution exists.",
    "No refresh execution exists.",
    "No sequencing execution exists.",
    "No scheduling execution exists.",
    "No dependency resolution exists.",
    "No lineage repair exists.",
    "No lineage inference exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No remediation exists.",
    "No automatic correction exists.",
    "No automatic rollback exists.",
    "No ranking, scoring, or selection behavior exists.",
    "No authorization or approval behavior exists.",
    "No operational execution exists.",
    "No hidden drift correction exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationDriftIdentity:
    drift_certification_id: str
    coordination_cycle_id: str
    drift_version: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_dependency_graph_reference: str
    source_dependency_graph_hash_reference: str
    source_lineage_chain_reference: str
    source_lineage_chain_hash_reference: str
    source_sequencing_reference: str
    source_sequencing_hash_reference: str
    source_routing_reference: str
    source_routing_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    certification_reference: str
    continuity_reference: str
    diagnostics_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_COORDINATION_DRIFT_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_drift_correction_enabled: bool = False


@dataclass(frozen=True)
class ManifestDriftReference:
    manifest_drift_reference_id: str
    manifest_reference: str
    manifest_hash_reference: str
    drift_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "drift_record_ids")


@dataclass(frozen=True)
class DependencyGraphDriftReference:
    dependency_graph_drift_reference_id: str
    dependency_graph_reference: str
    dependency_graph_hash_reference: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    drift_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("node_references", "edge_references", "drift_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageDriftReference:
    lineage_drift_reference_id: str
    lineage_chain_reference: str
    lineage_chain_hash_reference: str
    lineage_record_references: tuple[str, ...]
    drift_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_record_references", "drift_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SequencingDriftReference:
    sequencing_drift_reference_id: str
    sequencing_reference: str
    sequencing_hash_reference: str
    sequence_record_references: tuple[str, ...]
    drift_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("sequence_record_references", "drift_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RoutingDriftReference:
    routing_drift_reference_id: str
    routing_reference: str
    routing_hash_reference: str
    route_record_references: tuple[str, ...]
    drift_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("route_record_references", "drift_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDriftRecord:
    drift_record_id: str
    layer: str
    relationship_type: str
    drift_state: str
    manifest_drift_reference_id: str
    dependency_graph_drift_reference_id: str
    lineage_drift_reference_id: str
    sequencing_drift_reference_id: str
    routing_drift_reference_id: str
    layer_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    reason: str
    deterministic_order: int
    severity: str = "info"
    fail_visible: bool = False
    stale_visible: bool = False
    missing_visible: bool = False
    conflicting_visible: bool = False
    prohibited_correction_visible: bool = False
    unsupported_transition_visible: bool = False
    cross_layer_visible: bool = False
    descriptive_only: bool = True
    non_authorizing: bool = True
    hidden: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("layer_references", "evidence_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class DriftStateVisibility:
    visibility_id: str
    drift_state: str
    drift_record_ids: tuple[str, ...]
    layer_references: tuple[str, ...]
    reason_visibility: tuple[str, ...]
    deterministic_order: int
    state_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False
    routing_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("drift_record_ids", "layer_references", "reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CrossLayerDriftVisibility:
    visibility_id: str
    drift_record_ids: tuple[str, ...]
    involved_layer_references: tuple[str, ...]
    layer_pairs: tuple[str, ...]
    reason_visibility: tuple[str, ...]
    deterministic_order: int
    cross_layer_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("drift_record_ids", "involved_layer_references", "layer_pairs", "reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDriftDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_drift_record_ids: tuple[str, ...]
    affected_layer_references: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_drift_record_ids", "affected_layer_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDriftGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDriftCertification:
    identity: CoordinationDriftIdentity
    manifest_drift_references: tuple[ManifestDriftReference, ...]
    dependency_graph_drift_references: tuple[DependencyGraphDriftReference, ...]
    lineage_drift_references: tuple[LineageDriftReference, ...]
    sequencing_drift_references: tuple[SequencingDriftReference, ...]
    routing_drift_references: tuple[RoutingDriftReference, ...]
    drift_records: tuple[CoordinationDriftRecord, ...]
    stale_drift_visibility: DriftStateVisibility
    missing_drift_visibility: DriftStateVisibility
    conflicting_drift_visibility: DriftStateVisibility
    prohibited_correction_visibility: DriftStateVisibility
    unsupported_transition_visibility: DriftStateVisibility
    cross_layer_drift_visibility: CrossLayerDriftVisibility
    diagnostics: tuple[CoordinationDriftDiagnostic, ...]
    governance_visibility: CoordinationDriftGovernance
    compatibility_manifest_reference: str
    compatibility_dependency_graph_reference: str
    compatibility_lineage_chain_reference: str
    compatibility_sequencing_reference: str
    compatibility_routing_reference: str
    certification_scope: str = V4_2_COORDINATION_DRIFT_PURPOSE
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    continuity_certified: bool = True
    integrity_enforced: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    non_authorizing: bool = True
    non_remediating: bool = True
    execution_authorized: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    production_bundle_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    operational_execution_enabled: bool = False
    hidden_drift_correction_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False


def default_coordination_drift_identity(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
) -> CoordinationDriftIdentity:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    return CoordinationDriftIdentity(
        drift_certification_id="v4_2_coordination_drift_certification_primary",
        coordination_cycle_id="v4_2_refresh_coordination_cycle",
        drift_version="v4_2_phase_6",
        source_manifest_reference=source_manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_coordination_manifest(source_manifest),
        source_dependency_graph_reference=source_graph.identity.graph_id,
        source_dependency_graph_hash_reference=hash_coordination_dependency_graph(source_graph),
        source_lineage_chain_reference=source_lineage.identity.chain_id,
        source_lineage_chain_hash_reference=hash_coordination_lineage_chain(source_lineage),
        source_sequencing_reference=source_sequencing.identity.sequencing_id,
        source_sequencing_hash_reference=hash_coordination_sequencing_intelligence(source_sequencing),
        source_routing_reference=source_routing.identity.routing_id,
        source_routing_hash_reference=hash_governance_routing_visibility(source_routing),
        schema_version=V4_2_COORDINATION_DRIFT_SCHEMA_VERSION,
        generated_at=V4_2_COORDINATION_DRIFT_GENERATED_AT,
        provenance_reference="v4_2_coordination_drift_provenance_primary",
        certification_reference="v4_2_coordination_drift_certification_evidence_primary",
        continuity_reference="v4_2_coordination_drift_continuity_primary",
        diagnostics_reference="v4_2_coordination_drift_diagnostics_primary",
        governance_reference="v4_2_coordination_drift_governance_primary",
    )


def default_coordination_drift_records() -> tuple[CoordinationDriftRecord, ...]:
    drift_specs: tuple[tuple[str, str, str, str, int, str, tuple[str, ...], tuple[str, ...], str], ...] = (
        (
            "v4_2_drift_record_manifest_stable",
            "manifest",
            DRIFT_RELATIONSHIP_MANIFEST,
            DRIFT_STATE_STABLE,
            10,
            "Manifest drift reference is stable and descriptive.",
            ("v4_2_coordination_manifest_primary",),
            ("v4_2_coordination_manifest_primary",),
            "info",
        ),
        (
            "v4_2_drift_record_dependency_graph_stable",
            "dependency_graph",
            DRIFT_RELATIONSHIP_DEPENDENCY_GRAPH,
            DRIFT_STATE_STABLE,
            20,
            "Dependency graph drift reference is stable and descriptive.",
            ("v4_2_coordination_dependency_graph_primary",),
            ("v4_2_coordination_dependency_graph_primary",),
            "info",
        ),
        (
            "v4_2_drift_record_lineage_chain_stable",
            "lineage_chain",
            DRIFT_RELATIONSHIP_LINEAGE_CHAIN,
            DRIFT_STATE_STABLE,
            30,
            "Lineage chain drift reference is stable and descriptive.",
            ("v4_2_coordination_lineage_chain_primary",),
            ("v4_2_coordination_lineage_chain_primary",),
            "info",
        ),
        (
            "v4_2_drift_record_sequencing_stable",
            "sequencing",
            DRIFT_RELATIONSHIP_SEQUENCING,
            DRIFT_STATE_STABLE,
            40,
            "Sequencing drift reference is stable and non-scheduling.",
            ("v4_2_coordination_sequencing_primary",),
            ("v4_2_coordination_sequencing_primary",),
            "info",
        ),
        (
            "v4_2_drift_record_routing_stable",
            "routing",
            DRIFT_RELATIONSHIP_ROUTING,
            DRIFT_STATE_STABLE,
            50,
            "Governance routing drift reference is stable and non-routing.",
            ("v4_2_governance_routing_visibility_primary",),
            ("v4_2_governance_routing_visibility_primary",),
            "info",
        ),
        (
            "v4_2_drift_record_v4_1_snapshot_stale",
            "prior_phase_snapshot",
            DRIFT_RELATIONSHIP_MANIFEST,
            DRIFT_STATE_STALE,
            60,
            "Prior v4.1 refresh drift evidence remains stale read-only visibility.",
            ("v4_1_refresh_governance_snapshot",),
            ("v4_1_refresh_governance_snapshot",),
            "warning",
        ),
        (
            "v4_2_drift_record_future_dependency_missing",
            "future_dependency",
            DRIFT_RELATIONSHIP_DEPENDENCY_GRAPH,
            DRIFT_STATE_MISSING,
            70,
            "Future dependency drift target remains missing.",
            ("future_dependency_drift_target_missing",),
            ("future_dependency_drift_target_missing",),
            "warning",
        ),
        (
            "v4_2_drift_record_route_sequence_conflicting",
            "routing_sequencing_boundary",
            DRIFT_RELATIONSHIP_CROSS_LAYER,
            DRIFT_STATE_CONFLICTING,
            80,
            "Routing and sequencing drift requests conflict with non-execution boundaries.",
            ("v4_2_governance_routing_visibility_primary", "v4_2_coordination_sequencing_primary"),
            ("routing_execution_prohibited", "sequencing_execution_prohibited"),
            "blocked",
        ),
        (
            "v4_2_drift_record_correction_prohibited",
            "drift_correction_boundary",
            DRIFT_RELATIONSHIP_CROSS_LAYER,
            DRIFT_STATE_PROHIBITED_CORRECTION,
            90,
            "Drift correction remains prohibited and visible.",
            ("v4_2_coordination_drift_certification_primary",),
            ("drift_correction_prohibited",),
            "prohibited",
        ),
        (
            "v4_2_drift_record_future_transition_unsupported",
            "future_transition",
            DRIFT_RELATIONSHIP_CROSS_LAYER,
            DRIFT_STATE_UNSUPPORTED_TRANSITION,
            100,
            "Future drift transition remains unsupported.",
            ("future_drift_transition_contract",),
            ("future_drift_transition_contract",),
            "warning",
        ),
        (
            "v4_2_drift_record_manifest_routing_cross_layer",
            "cross_layer",
            DRIFT_RELATIONSHIP_CROSS_LAYER,
            DRIFT_STATE_CROSS_LAYER,
            110,
            "Manifest, graph, lineage, sequencing, and routing drift visibility is cross-layer evidence only.",
            (
                "v4_2_coordination_manifest_primary",
                "v4_2_coordination_dependency_graph_primary",
                "v4_2_coordination_lineage_chain_primary",
                "v4_2_coordination_sequencing_primary",
                "v4_2_governance_routing_visibility_primary",
            ),
            ("cross_layer_drift_visibility", "non_execution_boundary"),
            "info",
        ),
    )
    return tuple(
        CoordinationDriftRecord(
            drift_record_id=record_id,
            layer=layer,
            relationship_type=relationship,
            drift_state=state,
            manifest_drift_reference_id="v4_2_manifest_drift_reference_primary",
            dependency_graph_drift_reference_id="v4_2_dependency_graph_drift_reference_primary",
            lineage_drift_reference_id="v4_2_lineage_drift_reference_primary",
            sequencing_drift_reference_id="v4_2_sequencing_drift_reference_primary",
            routing_drift_reference_id="v4_2_routing_drift_reference_primary",
            layer_references=layer_refs,
            evidence_references=evidence,
            reason=reason,
            deterministic_order=order,
            severity=severity,
            fail_visible=state in FAIL_VISIBLE_DRIFT_STATES,
            stale_visible=state == DRIFT_STATE_STALE,
            missing_visible=state == DRIFT_STATE_MISSING,
            conflicting_visible=state == DRIFT_STATE_CONFLICTING,
            prohibited_correction_visible=state == DRIFT_STATE_PROHIBITED_CORRECTION,
            unsupported_transition_visible=state == DRIFT_STATE_UNSUPPORTED_TRANSITION,
            cross_layer_visible=state == DRIFT_STATE_CROSS_LAYER,
        )
        for record_id, layer, relationship, state, order, reason, layer_refs, evidence, severity in drift_specs
    )


def default_manifest_drift_references(
    identity: CoordinationDriftIdentity | None = None,
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> tuple[ManifestDriftReference, ...]:
    source = identity or default_coordination_drift_identity()
    drift_records = records or default_coordination_drift_records()
    return (
        ManifestDriftReference(
            manifest_drift_reference_id="v4_2_manifest_drift_reference_primary",
            manifest_reference=source.source_manifest_reference,
            manifest_hash_reference=source.source_manifest_hash_reference,
            drift_record_ids=tuple(record.drift_record_id for record in drift_records),
            deterministic_order=10,
        ),
    )


def default_dependency_graph_drift_references(
    identity: CoordinationDriftIdentity | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> tuple[DependencyGraphDriftReference, ...]:
    source = identity or default_coordination_drift_identity()
    graph = dependency_graph or default_coordination_dependency_graph()
    drift_records = records or default_coordination_drift_records()
    return (
        DependencyGraphDriftReference(
            dependency_graph_drift_reference_id="v4_2_dependency_graph_drift_reference_primary",
            dependency_graph_reference=source.source_dependency_graph_reference,
            dependency_graph_hash_reference=source.source_dependency_graph_hash_reference,
            node_references=tuple(node.node_id for node in graph.nodes),
            edge_references=tuple(edge.edge_id for edge in graph.edges),
            drift_record_ids=tuple(record.drift_record_id for record in drift_records),
            deterministic_order=10,
        ),
    )


def default_lineage_drift_references(
    identity: CoordinationDriftIdentity | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> tuple[LineageDriftReference, ...]:
    source = identity or default_coordination_drift_identity()
    lineage = lineage_chain or default_coordination_lineage_chain()
    drift_records = records or default_coordination_drift_records()
    return (
        LineageDriftReference(
            lineage_drift_reference_id="v4_2_lineage_drift_reference_primary",
            lineage_chain_reference=source.source_lineage_chain_reference,
            lineage_chain_hash_reference=source.source_lineage_chain_hash_reference,
            lineage_record_references=tuple(record.record_id for record in lineage.records),
            drift_record_ids=tuple(record.drift_record_id for record in drift_records),
            deterministic_order=10,
        ),
    )


def default_sequencing_drift_references(
    identity: CoordinationDriftIdentity | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> tuple[SequencingDriftReference, ...]:
    source = identity or default_coordination_drift_identity()
    source_sequencing = sequencing or default_coordination_sequencing_intelligence()
    drift_records = records or default_coordination_drift_records()
    return (
        SequencingDriftReference(
            sequencing_drift_reference_id="v4_2_sequencing_drift_reference_primary",
            sequencing_reference=source.source_sequencing_reference,
            sequencing_hash_reference=source.source_sequencing_hash_reference,
            sequence_record_references=tuple(record.sequence_record_id for record in source_sequencing.sequence_records),
            drift_record_ids=tuple(record.drift_record_id for record in drift_records),
            deterministic_order=10,
        ),
    )


def default_routing_drift_references(
    identity: CoordinationDriftIdentity | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> tuple[RoutingDriftReference, ...]:
    source = identity or default_coordination_drift_identity()
    source_routing = routing or default_governance_routing_visibility()
    drift_records = records or default_coordination_drift_records()
    return (
        RoutingDriftReference(
            routing_drift_reference_id="v4_2_routing_drift_reference_primary",
            routing_reference=source.source_routing_reference,
            routing_hash_reference=source.source_routing_hash_reference,
            route_record_references=tuple(record.route_record_id for record in source_routing.route_records),
            drift_record_ids=tuple(record.drift_record_id for record in drift_records),
            deterministic_order=10,
        ),
    )


def default_drift_state_visibility(
    drift_state: str,
    visibility_id: str,
    deterministic_order: int,
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> DriftStateVisibility:
    drift_records = records or default_coordination_drift_records()
    matching = tuple(record for record in drift_records if record.drift_state == drift_state)
    return DriftStateVisibility(
        visibility_id=visibility_id,
        drift_state=drift_state,
        drift_record_ids=tuple(record.drift_record_id for record in matching),
        layer_references=tuple(reference for record in matching for reference in record.layer_references),
        reason_visibility=tuple(record.reason for record in matching),
        deterministic_order=deterministic_order,
    )


def default_cross_layer_drift_visibility(
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> CrossLayerDriftVisibility:
    drift_records = records or default_coordination_drift_records()
    matching = tuple(record for record in drift_records if record.drift_state == DRIFT_STATE_CROSS_LAYER)
    return CrossLayerDriftVisibility(
        visibility_id="v4_2_coordination_drift_cross_layer_visibility_primary",
        drift_record_ids=tuple(record.drift_record_id for record in matching),
        involved_layer_references=tuple(reference for record in matching for reference in record.layer_references),
        layer_pairs=(
            "manifest->dependency_graph",
            "dependency_graph->lineage_chain",
            "lineage_chain->sequencing",
            "sequencing->governance_routing",
            "manifest->governance_routing",
        ),
        reason_visibility=tuple(record.reason for record in matching),
        deterministic_order=60,
    )


def default_coordination_drift_diagnostics(
    records: tuple[CoordinationDriftRecord, ...] | None = None,
) -> tuple[CoordinationDriftDiagnostic, ...]:
    drift_records = records or default_coordination_drift_records()

    def ids_for(drift_state: str) -> tuple[str, ...]:
        return tuple(record.drift_record_id for record in drift_records if record.drift_state == drift_state)

    def refs_for(drift_state: str) -> tuple[str, ...]:
        return tuple(
            reference
            for record in drift_records
            if record.drift_state == drift_state
            for reference in record.layer_references
        )

    all_record_ids = tuple(record.drift_record_id for record in drift_records)
    all_layer_refs = tuple(reference for record in drift_records for reference in record.layer_references)
    return (
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_stale_diagnostic",
            category=DRIFT_DIAGNOSTIC_STALE,
            severity="warning",
            finding="Stale drift states remain fail-visible read-only evidence.",
            affected_drift_record_ids=ids_for(DRIFT_STATE_STALE),
            affected_layer_references=refs_for(DRIFT_STATE_STALE),
            deterministic_order=10,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_missing_diagnostic",
            category=DRIFT_DIAGNOSTIC_MISSING,
            severity="warning",
            finding="Missing drift states remain fail-visible and unrepaired.",
            affected_drift_record_ids=ids_for(DRIFT_STATE_MISSING),
            affected_layer_references=refs_for(DRIFT_STATE_MISSING),
            deterministic_order=20,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_conflicting_diagnostic",
            category=DRIFT_DIAGNOSTIC_CONFLICTING,
            severity="blocked",
            finding="Conflicting drift states remain fail-visible and unresolved.",
            affected_drift_record_ids=ids_for(DRIFT_STATE_CONFLICTING),
            affected_layer_references=refs_for(DRIFT_STATE_CONFLICTING),
            deterministic_order=30,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_prohibited_correction_diagnostic",
            category=DRIFT_DIAGNOSTIC_PROHIBITED_CORRECTION,
            severity="prohibited",
            finding="Prohibited drift correction remains fail-visible and inactive.",
            affected_drift_record_ids=ids_for(DRIFT_STATE_PROHIBITED_CORRECTION),
            affected_layer_references=refs_for(DRIFT_STATE_PROHIBITED_CORRECTION),
            deterministic_order=40,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_unsupported_transition_diagnostic",
            category=DRIFT_DIAGNOSTIC_UNSUPPORTED_TRANSITION,
            severity="warning",
            finding="Unsupported drift transitions remain fail-visible and unresolved.",
            affected_drift_record_ids=ids_for(DRIFT_STATE_UNSUPPORTED_TRANSITION),
            affected_layer_references=refs_for(DRIFT_STATE_UNSUPPORTED_TRANSITION),
            deterministic_order=50,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_cross_layer_diagnostic",
            category=DRIFT_DIAGNOSTIC_CROSS_LAYER,
            severity="info",
            finding="Cross-layer drift visibility is descriptive evidence only.",
            affected_drift_record_ids=ids_for(DRIFT_STATE_CROSS_LAYER),
            affected_layer_references=refs_for(DRIFT_STATE_CROSS_LAYER),
            deterministic_order=60,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_compatibility_diagnostic",
            category=DRIFT_DIAGNOSTIC_COMPATIBILITY,
            severity="info",
            finding="Manifest, dependency graph, lineage chain, sequencing, and routing compatibility are deterministic evidence.",
            affected_drift_record_ids=all_record_ids,
            affected_layer_references=all_layer_refs,
            deterministic_order=70,
        ),
        CoordinationDriftDiagnostic(
            diagnostic_id="v4_2_coordination_drift_non_execution_diagnostic",
            category=DRIFT_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Coordination drift certification remains non-executing and non-remediating.",
            affected_drift_record_ids=all_record_ids,
            affected_layer_references=(),
            deterministic_order=80,
        ),
    )


def default_coordination_drift_governance(
    identity: CoordinationDriftIdentity | None = None,
) -> CoordinationDriftGovernance:
    source = identity or default_coordination_drift_identity()
    return CoordinationDriftGovernance(
        governance_id=source.governance_reference,
        governance_references=(
            "v4_2_coordination_manifest_governance_primary",
            "v4_2_coordination_dependency_graph_governance_boundary",
            "v4_2_coordination_lineage_chain_governance_boundary",
            "v4_2_coordination_sequencing_governance_boundary",
            "v4_2_governance_routing_boundary",
            "v4_2_coordination_drift_certification_boundary",
        ),
        explicit_limitations=EXPLICIT_COORDINATION_DRIFT_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_COORDINATION_DRIFT_PROHIBITIONS,
        deterministic_order=10,
    )


def default_coordination_drift_certification(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
) -> CoordinationDriftCertification:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    identity = default_coordination_drift_identity(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    records = default_coordination_drift_records()
    return CoordinationDriftCertification(
        identity=identity,
        manifest_drift_references=default_manifest_drift_references(identity, records),
        dependency_graph_drift_references=default_dependency_graph_drift_references(identity, source_graph, records),
        lineage_drift_references=default_lineage_drift_references(identity, source_lineage, records),
        sequencing_drift_references=default_sequencing_drift_references(identity, source_sequencing, records),
        routing_drift_references=default_routing_drift_references(identity, source_routing, records),
        drift_records=records,
        stale_drift_visibility=default_drift_state_visibility(
            DRIFT_STATE_STALE,
            "v4_2_coordination_drift_stale_visibility_primary",
            10,
            records,
        ),
        missing_drift_visibility=default_drift_state_visibility(
            DRIFT_STATE_MISSING,
            "v4_2_coordination_drift_missing_visibility_primary",
            20,
            records,
        ),
        conflicting_drift_visibility=default_drift_state_visibility(
            DRIFT_STATE_CONFLICTING,
            "v4_2_coordination_drift_conflicting_visibility_primary",
            30,
            records,
        ),
        prohibited_correction_visibility=default_drift_state_visibility(
            DRIFT_STATE_PROHIBITED_CORRECTION,
            "v4_2_coordination_drift_prohibited_correction_visibility_primary",
            40,
            records,
        ),
        unsupported_transition_visibility=default_drift_state_visibility(
            DRIFT_STATE_UNSUPPORTED_TRANSITION,
            "v4_2_coordination_drift_unsupported_transition_visibility_primary",
            50,
            records,
        ),
        cross_layer_drift_visibility=default_cross_layer_drift_visibility(records),
        diagnostics=default_coordination_drift_diagnostics(records),
        governance_visibility=default_coordination_drift_governance(identity),
        compatibility_manifest_reference=source_manifest.identity.manifest_id,
        compatibility_dependency_graph_reference=source_graph.identity.graph_id,
        compatibility_lineage_chain_reference=source_lineage.identity.chain_id,
        compatibility_sequencing_reference=source_sequencing.identity.sequencing_id,
        compatibility_routing_reference=source_routing.identity.routing_id,
    )
