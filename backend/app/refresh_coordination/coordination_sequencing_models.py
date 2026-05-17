"""Deterministic v4.2 coordination sequencing intelligence models.

Coordination sequencing intelligence is descriptive governance evidence only.
It does not execute sequences, schedule work, orchestrate refreshes, resolve
dependencies, repair lineage, infer lineage, consume production bundles,
integrate with planners, authorize behavior, remediate blockers, roll back
state, correct state, rank choices, score choices, select options, or mutate
runtime data.
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
from .coordination_lineage_chain_models import (
    CoordinationLineageChain,
    default_coordination_lineage_chain,
)
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest


V4_2_COORDINATION_SEQUENCING_PHASE_ID = "v4_2_coordination_sequencing_intelligence"
V4_2_COORDINATION_SEQUENCING_SCHEMA_VERSION = "v4_2.coordination_sequencing_intelligence.1"
V4_2_COORDINATION_SEQUENCING_REPORT_SCHEMA_VERSION = (
    "v4_2.coordination_sequencing_intelligence_report.1"
)
V4_2_COORDINATION_SEQUENCING_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_COORDINATION_SEQUENCING_STATUS_STABLE = "v4_2_coordination_sequencing_stable"
V4_2_COORDINATION_SEQUENCING_STATUS_BLOCKED = "v4_2_coordination_sequencing_blocked"
V4_2_COORDINATION_SEQUENCING_PURPOSE = (
    "deterministic_refresh_coordination_sequencing_intelligence_only"
)

SEQUENCE_STATE_STABLE = "stable"
SEQUENCE_STATE_BLOCKED = "blocked"
SEQUENCE_STATE_PROHIBITED = "prohibited"
SEQUENCE_STATE_UNSUPPORTED = "unsupported"
SEQUENCE_STATE_STALE = "stale"
SEQUENCE_STATE_MISSING = "missing"
SEQUENCE_STATE_CONFLICTING = "conflicting"
SEQUENCE_STATE_UNKNOWN = "unknown"
SEQUENCE_STATES: tuple[str, ...] = (
    SEQUENCE_STATE_STABLE,
    SEQUENCE_STATE_BLOCKED,
    SEQUENCE_STATE_PROHIBITED,
    SEQUENCE_STATE_UNSUPPORTED,
    SEQUENCE_STATE_STALE,
    SEQUENCE_STATE_MISSING,
    SEQUENCE_STATE_CONFLICTING,
    SEQUENCE_STATE_UNKNOWN,
)
FAIL_VISIBLE_SEQUENCE_STATES: tuple[str, ...] = (
    SEQUENCE_STATE_BLOCKED,
    SEQUENCE_STATE_PROHIBITED,
    SEQUENCE_STATE_UNSUPPORTED,
    SEQUENCE_STATE_STALE,
    SEQUENCE_STATE_MISSING,
    SEQUENCE_STATE_CONFLICTING,
    SEQUENCE_STATE_UNKNOWN,
)

SEQUENCE_RELATIONSHIP_MANIFEST = "manifest_sequence_reference"
SEQUENCE_RELATIONSHIP_DEPENDENCY_GRAPH = "dependency_graph_sequence_reference"
SEQUENCE_RELATIONSHIP_LINEAGE_CHAIN = "lineage_chain_sequence_reference"
SEQUENCE_RELATIONSHIP_RUNTIME_SEQUENCE = "runtime_sequence_visibility"
SEQUENCE_RELATIONSHIP_PRODUCTION_BUNDLE = "production_bundle_visibility"
SEQUENCE_RELATIONSHIP_FUTURE_PROVIDER = "future_provider_visibility"
SEQUENCE_RELATIONSHIP_PRIOR_SNAPSHOT = "prior_snapshot_visibility"
SEQUENCE_RELATIONSHIP_TYPES: tuple[str, ...] = (
    SEQUENCE_RELATIONSHIP_MANIFEST,
    SEQUENCE_RELATIONSHIP_DEPENDENCY_GRAPH,
    SEQUENCE_RELATIONSHIP_LINEAGE_CHAIN,
    SEQUENCE_RELATIONSHIP_RUNTIME_SEQUENCE,
    SEQUENCE_RELATIONSHIP_PRODUCTION_BUNDLE,
    SEQUENCE_RELATIONSHIP_FUTURE_PROVIDER,
    SEQUENCE_RELATIONSHIP_PRIOR_SNAPSHOT,
)

SEQUENCE_DIAGNOSTIC_ORDERING = "non_executable_sequence_ordering_visibility"
SEQUENCE_DIAGNOSTIC_BLOCKED = "blocked_sequence_visibility"
SEQUENCE_DIAGNOSTIC_PROHIBITED = "prohibited_sequence_visibility"
SEQUENCE_DIAGNOSTIC_UNSUPPORTED = "unsupported_sequence_visibility"
SEQUENCE_DIAGNOSTIC_STALE = "stale_sequence_visibility"
SEQUENCE_DIAGNOSTIC_MISSING = "missing_sequence_visibility"
SEQUENCE_DIAGNOSTIC_CONFLICTING = "conflicting_sequence_visibility"
SEQUENCE_DIAGNOSTIC_COMPATIBILITY = "coordination_source_compatibility"
SEQUENCE_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_COORDINATION_SEQUENCING_CAPABILITIES: tuple[str, ...] = (
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
    "hidden_sequence_execution",
    "implicit_execution_pathways",
)

EXPLICIT_COORDINATION_SEQUENCING_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 4 creates deterministic refresh coordination sequencing intelligence only.",
    "v4.2 Phase 4 does not enable sequencing execution.",
    "v4.2 Phase 4 does not enable scheduling execution.",
    "v4.2 Phase 4 does not enable dependency resolution.",
    "v4.2 Phase 4 does not enable lineage repair.",
    "v4.2 Phase 4 does not enable lineage inference.",
    "v4.2 Phase 4 does not enable orchestration execution.",
    "v4.2 Phase 4 does not enable refresh execution.",
    "v4.2 Phase 4 does not enable planner integration.",
    "v4.2 Phase 4 does not enable production consumption.",
    "v4.2 Phase 4 does not enable runtime mutation.",
    "v4.2 Phase 4 does not enable remediation.",
    "v4.2 Phase 4 does not enable automatic correction.",
    "v4.2 Phase 4 does not enable automatic rollback.",
    "v4.2 Phase 4 does not enable ranking scoring or selection.",
    "v4.2 Phase 4 does not enable authorization or approval.",
)

EXPLICIT_COORDINATION_SEQUENCING_PROHIBITIONS: tuple[str, ...] = (
    "No sequencing execution exists.",
    "No scheduling execution exists.",
    "No dependency resolution exists.",
    "No lineage repair exists.",
    "No lineage inference exists.",
    "No orchestration execution exists.",
    "No refresh execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No remediation exists.",
    "No automatic correction exists.",
    "No automatic rollback exists.",
    "No ranking, scoring, or selection behavior exists.",
    "No authorization or approval behavior exists.",
    "No operational execution exists.",
    "No hidden sequence execution exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationSequencingIdentity:
    sequencing_id: str
    coordination_cycle_id: str
    sequencing_version: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_dependency_graph_reference: str
    source_dependency_graph_hash_reference: str
    source_lineage_chain_reference: str
    source_lineage_chain_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    sequence_reference: str
    continuity_reference: str
    diagnostics_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_COORDINATION_SEQUENCING_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_sequence_execution_enabled: bool = False


@dataclass(frozen=True)
class SequenceStepIdentity:
    step_identity_id: str
    step_key: str
    source_reference: str
    sequence_state: str
    deterministic_order: int
    reason: str
    descriptive_only: bool = True
    fail_visible: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class ManifestSequenceReference:
    manifest_sequence_reference_id: str
    manifest_reference: str
    manifest_hash_reference: str
    manifest_sequence_scope: str
    step_identity_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "step_identity_ids")


@dataclass(frozen=True)
class DependencyGraphSequenceReference:
    dependency_graph_sequence_reference_id: str
    dependency_graph_reference: str
    dependency_graph_hash_reference: str
    dependency_graph_sequence_scope: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    step_identity_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("node_references", "edge_references", "step_identity_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageSequenceReference:
    lineage_sequence_reference_id: str
    lineage_chain_reference: str
    lineage_chain_hash_reference: str
    lineage_sequence_scope: str
    lineage_record_references: tuple[str, ...]
    step_identity_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    lineage_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_record_references", "step_identity_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationSequenceRecord:
    sequence_record_id: str
    step_identity_id: str
    manifest_sequence_reference_id: str
    dependency_graph_sequence_reference_id: str
    lineage_sequence_reference_id: str
    relationship_type: str
    sequence_state: str
    ordering_position: int
    non_executable_order_reference: str
    reason: str
    evidence_references: tuple[str, ...]
    deterministic_order: int
    severity: str = "info"
    fail_visible: bool = False
    blocked_visible: bool = False
    prohibited_visible: bool = False
    unsupported_visible: bool = False
    stale_visible: bool = False
    missing_visible: bool = False
    conflicting_visible: bool = False
    descriptive_only: bool = True
    non_authorizing: bool = True
    hidden: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class SequenceStateVisibility:
    visibility_id: str
    sequence_state: str
    sequence_record_ids: tuple[str, ...]
    step_identity_ids: tuple[str, ...]
    reason_visibility: tuple[str, ...]
    deterministic_order: int
    state_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("sequence_record_ids", "step_identity_ids", "reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class NonExecutableSequenceOrderingVisibility:
    ordering_visibility_id: str
    ordered_step_identity_ids: tuple[str, ...]
    ordered_sequence_record_ids: tuple[str, ...]
    blocked_ordering_ids: tuple[str, ...]
    prohibited_ordering_ids: tuple[str, ...]
    unsupported_ordering_ids: tuple[str, ...]
    stale_ordering_ids: tuple[str, ...]
    missing_ordering_ids: tuple[str, ...]
    conflicting_ordering_ids: tuple[str, ...]
    deterministic_order: int
    ordering_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_executable_ordering_only: bool = True
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    hidden_sequence_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "ordered_step_identity_ids",
            "ordered_sequence_record_ids",
            "blocked_ordering_ids",
            "prohibited_ordering_ids",
            "unsupported_ordering_ids",
            "stale_ordering_ids",
            "missing_ordering_ids",
            "conflicting_ordering_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationSequencingDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_sequence_record_ids: tuple[str, ...]
    affected_step_identity_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
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
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_sequence_record_ids", "affected_step_identity_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationSequencingGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
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
class CoordinationSequencingIntelligence:
    identity: CoordinationSequencingIdentity
    step_identities: tuple[SequenceStepIdentity, ...]
    manifest_sequence_references: tuple[ManifestSequenceReference, ...]
    dependency_graph_sequence_references: tuple[DependencyGraphSequenceReference, ...]
    lineage_sequence_references: tuple[LineageSequenceReference, ...]
    sequence_records: tuple[CoordinationSequenceRecord, ...]
    ordering_visibility: NonExecutableSequenceOrderingVisibility
    blocked_sequence_visibility: SequenceStateVisibility
    prohibited_sequence_visibility: SequenceStateVisibility
    unsupported_sequence_visibility: SequenceStateVisibility
    stale_sequence_visibility: SequenceStateVisibility
    missing_sequence_visibility: SequenceStateVisibility
    conflicting_sequence_visibility: SequenceStateVisibility
    diagnostics: tuple[CoordinationSequencingDiagnostic, ...]
    governance_visibility: CoordinationSequencingGovernance
    compatibility_manifest_reference: str
    compatibility_dependency_graph_reference: str
    compatibility_lineage_chain_reference: str
    sequencing_scope: str = V4_2_COORDINATION_SEQUENCING_PURPOSE
    deterministic: bool = True
    governance_first: bool = True
    non_executable: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    continuity_certified: bool = True
    integrity_enforced: bool = True
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
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
    hidden_sequence_execution_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "step_identities",
            "manifest_sequence_references",
            "dependency_graph_sequence_references",
            "lineage_sequence_references",
            "sequence_records",
            "diagnostics",
        ):
            _set_tuple_field(self, field_name)


def default_coordination_sequencing_identity(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
) -> CoordinationSequencingIdentity:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    return CoordinationSequencingIdentity(
        sequencing_id="v4_2_coordination_sequencing_primary",
        coordination_cycle_id="v4_2_refresh_coordination_governance_cycle",
        sequencing_version="v4.2.4",
        source_manifest_reference=source_manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_coordination_manifest(source_manifest),
        source_dependency_graph_reference=source_graph.identity.graph_id,
        source_dependency_graph_hash_reference=hash_coordination_dependency_graph(source_graph),
        source_lineage_chain_reference=source_lineage.identity.chain_id,
        source_lineage_chain_hash_reference=hash_coordination_lineage_chain(source_lineage),
        schema_version=V4_2_COORDINATION_SEQUENCING_SCHEMA_VERSION,
        generated_at=V4_2_COORDINATION_SEQUENCING_GENERATED_AT,
        provenance_reference="v4_2_coordination_sequencing_provenance_primary",
        sequence_reference="v4_2_coordination_sequencing_sequence_primary",
        continuity_reference="v4_2_coordination_sequencing_continuity_primary",
        diagnostics_reference="v4_2_coordination_sequencing_diagnostics_primary",
        governance_reference="v4_2_coordination_sequencing_governance_primary",
    )


def default_sequence_step_identities() -> tuple[SequenceStepIdentity, ...]:
    return (
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_manifest_foundation",
            step_key="manifest_foundation_visibility",
            source_reference="v4_2_coordination_manifest_primary",
            sequence_state=SEQUENCE_STATE_STABLE,
            deterministic_order=10,
            reason="Manifest foundation is visible as sequence evidence.",
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_dependency_graph",
            step_key="dependency_graph_visibility",
            source_reference="v4_2_coordination_dependency_graph_primary",
            sequence_state=SEQUENCE_STATE_STABLE,
            deterministic_order=20,
            reason="Dependency graph is visible as sequence evidence.",
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_lineage_chain",
            step_key="lineage_chain_visibility",
            source_reference="v4_2_coordination_lineage_chain_primary",
            sequence_state=SEQUENCE_STATE_STABLE,
            deterministic_order=30,
            reason="Lineage chain is visible as sequence evidence.",
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_runtime_sequence_blocked",
            step_key="runtime_sequence_blocked_visibility",
            source_reference="future_refresh_sequence",
            sequence_state=SEQUENCE_STATE_BLOCKED,
            deterministic_order=40,
            reason="Runtime sequence remains blocked because sequencing execution is prohibited.",
            fail_visible=True,
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_production_bundle_prohibited",
            step_key="production_bundle_prohibited_visibility",
            source_reference="production_runtime_bundle",
            sequence_state=SEQUENCE_STATE_PROHIBITED,
            deterministic_order=50,
            reason="Production bundle sequencing remains prohibited.",
            fail_visible=True,
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_future_provider_unsupported",
            step_key="future_provider_unsupported_visibility",
            source_reference="future_refresh_provider_contract",
            sequence_state=SEQUENCE_STATE_UNSUPPORTED,
            deterministic_order=60,
            reason="Future provider sequencing remains unsupported.",
            fail_visible=True,
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_v4_1_snapshot_stale",
            step_key="v4_1_snapshot_stale_visibility",
            source_reference="v4_1_refresh_governance_snapshot",
            sequence_state=SEQUENCE_STATE_STALE,
            deterministic_order=70,
            reason="Prior v4.1 snapshot sequencing remains stale read-only evidence.",
            fail_visible=True,
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_future_lineage_missing",
            step_key="future_lineage_missing_visibility",
            source_reference="future_lineage_sequence",
            sequence_state=SEQUENCE_STATE_MISSING,
            deterministic_order=80,
            reason="Future lineage sequence input remains missing.",
            fail_visible=True,
        ),
        SequenceStepIdentity(
            step_identity_id="v4_2_sequence_step_runtime_order_conflicting",
            step_key="runtime_order_conflicting_visibility",
            source_reference="runtime_ordering_request",
            sequence_state=SEQUENCE_STATE_CONFLICTING,
            deterministic_order=90,
            reason="Runtime ordering request conflicts with the non-execution boundary.",
            fail_visible=True,
        ),
    )


def default_manifest_sequence_references(
    identity: CoordinationSequencingIdentity | None = None,
    steps: tuple[SequenceStepIdentity, ...] | None = None,
) -> tuple[ManifestSequenceReference, ...]:
    source = identity or default_coordination_sequencing_identity()
    sequence_steps = steps or default_sequence_step_identities()
    return (
        ManifestSequenceReference(
            manifest_sequence_reference_id="v4_2_manifest_sequence_reference_primary",
            manifest_reference=source.source_manifest_reference,
            manifest_hash_reference=source.source_manifest_hash_reference,
            manifest_sequence_scope="coordination_manifest_sequence_visibility",
            step_identity_ids=tuple(step.step_identity_id for step in sequence_steps),
            deterministic_order=10,
        ),
    )


def default_dependency_graph_sequence_references(
    identity: CoordinationSequencingIdentity | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    steps: tuple[SequenceStepIdentity, ...] | None = None,
) -> tuple[DependencyGraphSequenceReference, ...]:
    source = identity or default_coordination_sequencing_identity()
    graph = dependency_graph or default_coordination_dependency_graph()
    sequence_steps = steps or default_sequence_step_identities()
    return (
        DependencyGraphSequenceReference(
            dependency_graph_sequence_reference_id="v4_2_dependency_graph_sequence_reference_primary",
            dependency_graph_reference=source.source_dependency_graph_reference,
            dependency_graph_hash_reference=source.source_dependency_graph_hash_reference,
            dependency_graph_sequence_scope="coordination_dependency_graph_sequence_visibility",
            node_references=tuple(node.node_id for node in graph.nodes),
            edge_references=tuple(edge.edge_id for edge in graph.edges),
            step_identity_ids=tuple(step.step_identity_id for step in sequence_steps),
            deterministic_order=10,
        ),
    )


def default_lineage_sequence_references(
    identity: CoordinationSequencingIdentity | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    steps: tuple[SequenceStepIdentity, ...] | None = None,
) -> tuple[LineageSequenceReference, ...]:
    source = identity or default_coordination_sequencing_identity()
    lineage = lineage_chain or default_coordination_lineage_chain()
    sequence_steps = steps or default_sequence_step_identities()
    return (
        LineageSequenceReference(
            lineage_sequence_reference_id="v4_2_lineage_sequence_reference_primary",
            lineage_chain_reference=source.source_lineage_chain_reference,
            lineage_chain_hash_reference=source.source_lineage_chain_hash_reference,
            lineage_sequence_scope="coordination_lineage_chain_sequence_visibility",
            lineage_record_references=tuple(record.record_id for record in lineage.records),
            step_identity_ids=tuple(step.step_identity_id for step in sequence_steps),
            deterministic_order=10,
        ),
    )


def default_coordination_sequence_records(
    steps: tuple[SequenceStepIdentity, ...] | None = None,
) -> tuple[CoordinationSequenceRecord, ...]:
    sequence_steps = steps or default_sequence_step_identities()
    state_by_step = {step.step_identity_id: step for step in sequence_steps}

    def build_record(
        record_id: str,
        step_identity_id: str,
        relationship_type: str,
        ordering_position: int,
        evidence_references: tuple[str, ...],
        severity: str = "info",
    ) -> CoordinationSequenceRecord:
        step = state_by_step[step_identity_id]
        return CoordinationSequenceRecord(
            sequence_record_id=record_id,
            step_identity_id=step_identity_id,
            manifest_sequence_reference_id="v4_2_manifest_sequence_reference_primary",
            dependency_graph_sequence_reference_id="v4_2_dependency_graph_sequence_reference_primary",
            lineage_sequence_reference_id="v4_2_lineage_sequence_reference_primary",
            relationship_type=relationship_type,
            sequence_state=step.sequence_state,
            ordering_position=ordering_position,
            non_executable_order_reference="v4_2_non_executable_sequence_ordering_primary",
            reason=step.reason,
            evidence_references=evidence_references,
            deterministic_order=ordering_position,
            severity=severity,
            fail_visible=step.sequence_state in FAIL_VISIBLE_SEQUENCE_STATES,
            blocked_visible=step.sequence_state == SEQUENCE_STATE_BLOCKED,
            prohibited_visible=step.sequence_state == SEQUENCE_STATE_PROHIBITED,
            unsupported_visible=step.sequence_state == SEQUENCE_STATE_UNSUPPORTED,
            stale_visible=step.sequence_state == SEQUENCE_STATE_STALE,
            missing_visible=step.sequence_state == SEQUENCE_STATE_MISSING,
            conflicting_visible=step.sequence_state == SEQUENCE_STATE_CONFLICTING,
        )

    return (
        build_record(
            "v4_2_sequence_record_manifest_foundation",
            "v4_2_sequence_step_manifest_foundation",
            SEQUENCE_RELATIONSHIP_MANIFEST,
            10,
            ("v4_2_coordination_manifest_primary",),
        ),
        build_record(
            "v4_2_sequence_record_dependency_graph",
            "v4_2_sequence_step_dependency_graph",
            SEQUENCE_RELATIONSHIP_DEPENDENCY_GRAPH,
            20,
            ("v4_2_coordination_dependency_graph_primary",),
        ),
        build_record(
            "v4_2_sequence_record_lineage_chain",
            "v4_2_sequence_step_lineage_chain",
            SEQUENCE_RELATIONSHIP_LINEAGE_CHAIN,
            30,
            ("v4_2_coordination_lineage_chain_primary",),
        ),
        build_record(
            "v4_2_sequence_record_runtime_sequence_blocked",
            "v4_2_sequence_step_runtime_sequence_blocked",
            SEQUENCE_RELATIONSHIP_RUNTIME_SEQUENCE,
            40,
            ("future_refresh_sequence", "sequencing_execution_prohibited"),
            "blocked",
        ),
        build_record(
            "v4_2_sequence_record_production_bundle_prohibited",
            "v4_2_sequence_step_production_bundle_prohibited",
            SEQUENCE_RELATIONSHIP_PRODUCTION_BUNDLE,
            50,
            ("production_runtime_bundle", "production_consumption_prohibited"),
            "prohibited",
        ),
        build_record(
            "v4_2_sequence_record_future_provider_unsupported",
            "v4_2_sequence_step_future_provider_unsupported",
            SEQUENCE_RELATIONSHIP_FUTURE_PROVIDER,
            60,
            ("future_refresh_provider_contract",),
            "warning",
        ),
        build_record(
            "v4_2_sequence_record_v4_1_snapshot_stale",
            "v4_2_sequence_step_v4_1_snapshot_stale",
            SEQUENCE_RELATIONSHIP_PRIOR_SNAPSHOT,
            70,
            ("v4_1_refresh_governance_snapshot",),
            "warning",
        ),
        build_record(
            "v4_2_sequence_record_future_lineage_missing",
            "v4_2_sequence_step_future_lineage_missing",
            SEQUENCE_RELATIONSHIP_LINEAGE_CHAIN,
            80,
            ("future_lineage_sequence",),
            "warning",
        ),
        build_record(
            "v4_2_sequence_record_runtime_order_conflicting",
            "v4_2_sequence_step_runtime_order_conflicting",
            SEQUENCE_RELATIONSHIP_RUNTIME_SEQUENCE,
            90,
            ("runtime_ordering_request", "scheduling_execution_prohibited"),
            "blocked",
        ),
    )


def default_sequence_state_visibility(
    sequence_state: str,
    visibility_id: str,
    deterministic_order: int,
    records: tuple[CoordinationSequenceRecord, ...] | None = None,
) -> SequenceStateVisibility:
    sequence_records = records or default_coordination_sequence_records()
    matching_records = tuple(record for record in sequence_records if record.sequence_state == sequence_state)
    return SequenceStateVisibility(
        visibility_id=visibility_id,
        sequence_state=sequence_state,
        sequence_record_ids=tuple(record.sequence_record_id for record in matching_records),
        step_identity_ids=tuple(record.step_identity_id for record in matching_records),
        reason_visibility=tuple(record.reason for record in matching_records),
        deterministic_order=deterministic_order,
    )


def default_non_executable_sequence_ordering_visibility(
    records: tuple[CoordinationSequenceRecord, ...] | None = None,
) -> NonExecutableSequenceOrderingVisibility:
    sequence_records = tuple(sorted(records or default_coordination_sequence_records(), key=lambda item: item.ordering_position))
    return NonExecutableSequenceOrderingVisibility(
        ordering_visibility_id="v4_2_non_executable_sequence_ordering_primary",
        ordered_step_identity_ids=tuple(record.step_identity_id for record in sequence_records),
        ordered_sequence_record_ids=tuple(record.sequence_record_id for record in sequence_records),
        blocked_ordering_ids=tuple(
            record.sequence_record_id for record in sequence_records if record.sequence_state == SEQUENCE_STATE_BLOCKED
        ),
        prohibited_ordering_ids=tuple(
            record.sequence_record_id
            for record in sequence_records
            if record.sequence_state == SEQUENCE_STATE_PROHIBITED
        ),
        unsupported_ordering_ids=tuple(
            record.sequence_record_id
            for record in sequence_records
            if record.sequence_state == SEQUENCE_STATE_UNSUPPORTED
        ),
        stale_ordering_ids=tuple(
            record.sequence_record_id for record in sequence_records if record.sequence_state == SEQUENCE_STATE_STALE
        ),
        missing_ordering_ids=tuple(
            record.sequence_record_id
            for record in sequence_records
            if record.sequence_state == SEQUENCE_STATE_MISSING
        ),
        conflicting_ordering_ids=tuple(
            record.sequence_record_id
            for record in sequence_records
            if record.sequence_state == SEQUENCE_STATE_CONFLICTING
        ),
        deterministic_order=10,
    )


def default_coordination_sequencing_diagnostics(
    records: tuple[CoordinationSequenceRecord, ...] | None = None,
) -> tuple[CoordinationSequencingDiagnostic, ...]:
    sequence_records = records or default_coordination_sequence_records()

    def ids_for(sequence_state: str) -> tuple[str, ...]:
        return tuple(record.sequence_record_id for record in sequence_records if record.sequence_state == sequence_state)

    def steps_for(sequence_state: str) -> tuple[str, ...]:
        return tuple(record.step_identity_id for record in sequence_records if record.sequence_state == sequence_state)

    all_record_ids = tuple(record.sequence_record_id for record in sequence_records)
    all_step_ids = tuple(record.step_identity_id for record in sequence_records)
    return (
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_ordering_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_ORDERING,
            severity="info",
            finding="Sequence ordering is visible as non-executable evidence only.",
            affected_sequence_record_ids=all_record_ids,
            affected_step_identity_ids=all_step_ids,
            deterministic_order=10,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_blocked_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_BLOCKED,
            severity="blocked",
            finding="Blocked sequence states remain fail-visible and unscheduled.",
            affected_sequence_record_ids=ids_for(SEQUENCE_STATE_BLOCKED),
            affected_step_identity_ids=steps_for(SEQUENCE_STATE_BLOCKED),
            deterministic_order=20,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_prohibited_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            finding="Prohibited sequence states remain fail-visible and inactive.",
            affected_sequence_record_ids=ids_for(SEQUENCE_STATE_PROHIBITED),
            affected_step_identity_ids=steps_for(SEQUENCE_STATE_PROHIBITED),
            deterministic_order=30,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_unsupported_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            finding="Unsupported sequence states remain fail-visible and unresolved.",
            affected_sequence_record_ids=ids_for(SEQUENCE_STATE_UNSUPPORTED),
            affected_step_identity_ids=steps_for(SEQUENCE_STATE_UNSUPPORTED),
            deterministic_order=40,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_stale_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_STALE,
            severity="warning",
            finding="Stale sequence states remain fail-visible read-only evidence.",
            affected_sequence_record_ids=ids_for(SEQUENCE_STATE_STALE),
            affected_step_identity_ids=steps_for(SEQUENCE_STATE_STALE),
            deterministic_order=50,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_missing_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_MISSING,
            severity="warning",
            finding="Missing sequence states remain fail-visible and unrepaired.",
            affected_sequence_record_ids=ids_for(SEQUENCE_STATE_MISSING),
            affected_step_identity_ids=steps_for(SEQUENCE_STATE_MISSING),
            deterministic_order=60,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_conflicting_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_CONFLICTING,
            severity="blocked",
            finding="Conflicting sequence states remain fail-visible and unresolved.",
            affected_sequence_record_ids=ids_for(SEQUENCE_STATE_CONFLICTING),
            affected_step_identity_ids=steps_for(SEQUENCE_STATE_CONFLICTING),
            deterministic_order=70,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_compatibility_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_COMPATIBILITY,
            severity="info",
            finding="Manifest, dependency graph, and lineage chain compatibility are visible as deterministic evidence.",
            affected_sequence_record_ids=all_record_ids,
            affected_step_identity_ids=all_step_ids,
            deterministic_order=80,
        ),
        CoordinationSequencingDiagnostic(
            diagnostic_id="v4_2_coordination_sequencing_non_execution_diagnostic",
            category=SEQUENCE_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Sequencing intelligence remains non-executing and non-scheduling.",
            affected_sequence_record_ids=all_record_ids,
            affected_step_identity_ids=(),
            deterministic_order=90,
        ),
    )


def default_coordination_sequencing_governance(
    identity: CoordinationSequencingIdentity | None = None,
) -> CoordinationSequencingGovernance:
    source = identity or default_coordination_sequencing_identity()
    return CoordinationSequencingGovernance(
        governance_id=source.governance_reference,
        governance_references=(
            "v4_2_coordination_manifest_governance_primary",
            "v4_2_coordination_dependency_graph_governance_boundary",
            "v4_2_coordination_lineage_chain_governance_boundary",
            "v4_2_coordination_sequencing_governance_boundary",
        ),
        explicit_limitations=EXPLICIT_COORDINATION_SEQUENCING_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_COORDINATION_SEQUENCING_PROHIBITIONS,
        deterministic_order=10,
    )


def default_coordination_sequencing_intelligence(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
) -> CoordinationSequencingIntelligence:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    identity = default_coordination_sequencing_identity(source_manifest, source_graph, source_lineage)
    steps = default_sequence_step_identities()
    records = default_coordination_sequence_records(steps)
    return CoordinationSequencingIntelligence(
        identity=identity,
        step_identities=steps,
        manifest_sequence_references=default_manifest_sequence_references(identity, steps),
        dependency_graph_sequence_references=default_dependency_graph_sequence_references(
            identity,
            source_graph,
            steps,
        ),
        lineage_sequence_references=default_lineage_sequence_references(identity, source_lineage, steps),
        sequence_records=records,
        ordering_visibility=default_non_executable_sequence_ordering_visibility(records),
        blocked_sequence_visibility=default_sequence_state_visibility(
            SEQUENCE_STATE_BLOCKED,
            "v4_2_coordination_sequence_blocked_visibility_primary",
            20,
            records,
        ),
        prohibited_sequence_visibility=default_sequence_state_visibility(
            SEQUENCE_STATE_PROHIBITED,
            "v4_2_coordination_sequence_prohibited_visibility_primary",
            30,
            records,
        ),
        unsupported_sequence_visibility=default_sequence_state_visibility(
            SEQUENCE_STATE_UNSUPPORTED,
            "v4_2_coordination_sequence_unsupported_visibility_primary",
            40,
            records,
        ),
        stale_sequence_visibility=default_sequence_state_visibility(
            SEQUENCE_STATE_STALE,
            "v4_2_coordination_sequence_stale_visibility_primary",
            50,
            records,
        ),
        missing_sequence_visibility=default_sequence_state_visibility(
            SEQUENCE_STATE_MISSING,
            "v4_2_coordination_sequence_missing_visibility_primary",
            60,
            records,
        ),
        conflicting_sequence_visibility=default_sequence_state_visibility(
            SEQUENCE_STATE_CONFLICTING,
            "v4_2_coordination_sequence_conflicting_visibility_primary",
            70,
            records,
        ),
        diagnostics=default_coordination_sequencing_diagnostics(records),
        governance_visibility=default_coordination_sequencing_governance(identity),
        compatibility_manifest_reference=source_manifest.identity.manifest_id,
        compatibility_dependency_graph_reference=source_graph.identity.graph_id,
        compatibility_lineage_chain_reference=source_lineage.identity.chain_id,
    )
