"""Deterministic v4.2 coordination lineage chain governance models.

Coordination lineage chains are descriptive governance evidence only. They do
not repair lineage, infer lineage, execute refreshes, resolve dependencies,
orchestrate operations, consume production bundles, integrate with planners,
authorize behavior, remediate blockers, roll back state, correct state, rank
choices, score choices, select options, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import (
    CoordinationDependencyGraph,
    default_coordination_dependency_graph,
)
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest


V4_2_COORDINATION_LINEAGE_CHAIN_PHASE_ID = "v4_2_coordination_lineage_chain_governance"
V4_2_COORDINATION_LINEAGE_CHAIN_SCHEMA_VERSION = "v4_2.coordination_lineage_chain_governance.1"
V4_2_COORDINATION_LINEAGE_CHAIN_REPORT_SCHEMA_VERSION = (
    "v4_2.coordination_lineage_chain_governance_report.1"
)
V4_2_COORDINATION_LINEAGE_CHAIN_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_STABLE = "v4_2_coordination_lineage_chain_stable"
V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_BLOCKED = "v4_2_coordination_lineage_chain_blocked"
V4_2_COORDINATION_LINEAGE_CHAIN_PURPOSE = (
    "deterministic_refresh_coordination_lineage_chain_governance_intelligence_only"
)

LINEAGE_STATE_STABLE = "stable"
LINEAGE_STATE_STALE = "stale"
LINEAGE_STATE_MISSING = "missing"
LINEAGE_STATE_CONFLICTING = "conflicting"
LINEAGE_STATE_PROHIBITED_MUTATION = "prohibited_mutation"
LINEAGE_STATE_UNSUPPORTED_TRANSITION = "unsupported_transition"
LINEAGE_STATE_UNKNOWN = "unknown"
LINEAGE_STATES: tuple[str, ...] = (
    LINEAGE_STATE_STABLE,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_MISSING,
    LINEAGE_STATE_CONFLICTING,
    LINEAGE_STATE_PROHIBITED_MUTATION,
    LINEAGE_STATE_UNSUPPORTED_TRANSITION,
    LINEAGE_STATE_UNKNOWN,
)
FAIL_VISIBLE_LINEAGE_STATES: tuple[str, ...] = (
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_MISSING,
    LINEAGE_STATE_CONFLICTING,
    LINEAGE_STATE_PROHIBITED_MUTATION,
    LINEAGE_STATE_UNSUPPORTED_TRANSITION,
    LINEAGE_STATE_UNKNOWN,
)

LINEAGE_TRANSITION_MANIFEST_TO_GRAPH = "manifest_to_dependency_graph"
LINEAGE_TRANSITION_GRAPH_TO_CHAIN = "dependency_graph_to_lineage_chain"
LINEAGE_TRANSITION_PRIOR_SNAPSHOT = "prior_snapshot_to_lineage_chain"
LINEAGE_TRANSITION_UNDECLARED_PROVIDER = "undeclared_provider_lineage"
LINEAGE_TRANSITION_RUNTIME_SEQUENCE = "runtime_sequence_lineage"
LINEAGE_TRANSITION_PRODUCTION_MUTATION = "production_mutation_lineage"
LINEAGE_TRANSITION_FUTURE_UNSUPPORTED = "future_unsupported_lineage_transition"
LINEAGE_TRANSITION_TYPES: tuple[str, ...] = (
    LINEAGE_TRANSITION_MANIFEST_TO_GRAPH,
    LINEAGE_TRANSITION_GRAPH_TO_CHAIN,
    LINEAGE_TRANSITION_PRIOR_SNAPSHOT,
    LINEAGE_TRANSITION_UNDECLARED_PROVIDER,
    LINEAGE_TRANSITION_RUNTIME_SEQUENCE,
    LINEAGE_TRANSITION_PRODUCTION_MUTATION,
    LINEAGE_TRANSITION_FUTURE_UNSUPPORTED,
)

LINEAGE_DIAGNOSTIC_STALE = "stale_lineage_visibility"
LINEAGE_DIAGNOSTIC_MISSING = "missing_lineage_visibility"
LINEAGE_DIAGNOSTIC_CONFLICTING = "conflicting_lineage_visibility"
LINEAGE_DIAGNOSTIC_PROHIBITED_MUTATION = "prohibited_lineage_mutation_visibility"
LINEAGE_DIAGNOSTIC_UNSUPPORTED_TRANSITION = "unsupported_lineage_transition_visibility"
LINEAGE_DIAGNOSTIC_CONTINUITY = "lineage_continuity_visibility"
LINEAGE_DIAGNOSTIC_MANIFEST_COMPATIBILITY = "manifest_lineage_compatibility"
LINEAGE_DIAGNOSTIC_GRAPH_COMPATIBILITY = "dependency_graph_lineage_compatibility"
LINEAGE_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_COORDINATION_LINEAGE_CHAIN_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "refresh_execution",
    "dependency_resolution",
    "lineage_repair",
    "lineage_inference",
    "lineage_mutation",
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
    "hidden_lineage_resolution",
    "implicit_execution_pathways",
)

EXPLICIT_COORDINATION_LINEAGE_CHAIN_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 3 creates deterministic refresh coordination lineage chain governance intelligence only.",
    "v4.2 Phase 3 does not enable lineage repair.",
    "v4.2 Phase 3 does not enable lineage inference.",
    "v4.2 Phase 3 does not enable dependency resolution.",
    "v4.2 Phase 3 does not enable orchestration execution.",
    "v4.2 Phase 3 does not enable refresh execution.",
    "v4.2 Phase 3 does not enable planner integration.",
    "v4.2 Phase 3 does not enable production consumption.",
    "v4.2 Phase 3 does not enable runtime mutation.",
    "v4.2 Phase 3 does not enable remediation.",
    "v4.2 Phase 3 does not enable automatic correction.",
    "v4.2 Phase 3 does not enable automatic rollback.",
    "v4.2 Phase 3 does not enable ranking scoring or selection.",
    "v4.2 Phase 3 does not enable authorization or approval.",
)

EXPLICIT_COORDINATION_LINEAGE_CHAIN_PROHIBITIONS: tuple[str, ...] = (
    "No lineage repair exists.",
    "No lineage inference exists.",
    "No dependency resolution exists.",
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
    "No hidden lineage resolution exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationLineageChainIdentity:
    chain_id: str
    coordination_cycle_id: str
    chain_version: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_dependency_graph_reference: str
    source_dependency_graph_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    lineage_reference: str
    continuity_reference: str
    diagnostics_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_COORDINATION_LINEAGE_CHAIN_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    lineage_mutation_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class LineageSourceReference:
    source_reference_id: str
    source_type: str
    source_id: str
    source_hash_reference: str
    source_lineage_reference: str
    source_continuity_reference: str
    evidence_references: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class LineagePredecessorReference:
    predecessor_reference_id: str
    predecessor_id: str
    predecessor_type: str
    predecessor_lineage_reference: str
    predecessor_hash_reference: str
    predecessor_state: str
    deterministic_order: int
    stale_visible: bool = False
    missing_visible: bool = False
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class LineageSuccessorReference:
    successor_reference_id: str
    successor_id: str
    successor_type: str
    successor_lineage_reference: str
    successor_hash_reference: str
    successor_state: str
    deterministic_order: int
    unsupported_transition_visible: bool = False
    missing_visible: bool = False
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class ManifestLineageChainReference:
    manifest_lineage_reference_id: str
    manifest_reference: str
    manifest_hash_reference: str
    manifest_lineage_reference: str
    manifest_continuity_reference: str
    record_references: tuple[str, ...]
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "record_references")


@dataclass(frozen=True)
class DependencyGraphLineageChainReference:
    dependency_graph_lineage_reference_id: str
    dependency_graph_reference: str
    dependency_graph_hash_reference: str
    dependency_graph_lineage_reference: str
    dependency_graph_continuity_reference: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    record_references: tuple[str, ...]
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    dependency_graph_compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("node_references", "edge_references", "record_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationLineageChainRecord:
    record_id: str
    source_reference_id: str
    predecessor_reference_id: str
    successor_reference_id: str
    manifest_lineage_reference_id: str
    dependency_graph_lineage_reference_id: str
    lineage_state: str
    transition_type: str
    lineage_scope: str
    reason: str
    evidence_references: tuple[str, ...]
    deterministic_order: int
    severity: str = "info"
    fail_visible: bool = False
    stale_visible: bool = False
    missing_visible: bool = False
    conflicting_visible: bool = False
    prohibited_mutation_visible: bool = False
    unsupported_transition_visible: bool = False
    descriptive_only: bool = True
    non_authorizing: bool = True
    hidden: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    lineage_mutation_enabled: bool = False
    dependency_resolution_enabled: bool = False
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
class StaleLineageVisibility:
    stale_visibility_id: str
    stale_record_ids: tuple[str, ...]
    stale_source_reference_ids: tuple[str, ...]
    stale_predecessor_reference_ids: tuple[str, ...]
    stale_reason_visibility: tuple[str, ...]
    deterministic_order: int
    stale_lineage_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "stale_record_ids",
            "stale_source_reference_ids",
            "stale_predecessor_reference_ids",
            "stale_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class MissingLineageVisibility:
    missing_visibility_id: str
    missing_record_ids: tuple[str, ...]
    missing_successor_reference_ids: tuple[str, ...]
    missing_reference_ids: tuple[str, ...]
    missing_reason_visibility: tuple[str, ...]
    deterministic_order: int
    missing_lineage_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "missing_record_ids",
            "missing_successor_reference_ids",
            "missing_reference_ids",
            "missing_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ConflictingLineageVisibility:
    conflicting_visibility_id: str
    conflicting_record_ids: tuple[str, ...]
    conflict_pair_visibility: tuple[str, ...]
    conflict_reason_visibility: tuple[str, ...]
    deterministic_order: int
    conflicting_lineage_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("conflicting_record_ids", "conflict_pair_visibility", "conflict_reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ProhibitedLineageMutationVisibility:
    prohibited_mutation_visibility_id: str
    prohibited_record_ids: tuple[str, ...]
    prohibited_capabilities: tuple[str, ...]
    prohibited_reason_visibility: tuple[str, ...]
    deterministic_order: int
    prohibited_lineage_mutation_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    lineage_mutation_enabled: bool = False
    execution_authorized: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
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

    def __post_init__(self) -> None:
        for field_name in ("prohibited_record_ids", "prohibited_capabilities", "prohibited_reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class UnsupportedLineageTransitionVisibility:
    unsupported_transition_visibility_id: str
    unsupported_record_ids: tuple[str, ...]
    unsupported_transition_ids: tuple[str, ...]
    unknown_transition_visibility: tuple[str, ...]
    unsupported_reason_visibility: tuple[str, ...]
    deterministic_order: int
    unsupported_lineage_transition_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False
    remediation_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_record_ids",
            "unsupported_transition_ids",
            "unknown_transition_visibility",
            "unsupported_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationLineageChainDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_record_ids: tuple[str, ...]
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    lineage_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    dependency_resolution_enabled: bool = False
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
        for field_name in ("affected_record_ids", "affected_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationLineageChainGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    lineage_mutation_enabled: bool = False
    dependency_resolution_enabled: bool = False
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
class CoordinationLineageChain:
    identity: CoordinationLineageChainIdentity
    source_references: tuple[LineageSourceReference, ...]
    predecessor_references: tuple[LineagePredecessorReference, ...]
    successor_references: tuple[LineageSuccessorReference, ...]
    manifest_lineage_references: tuple[ManifestLineageChainReference, ...]
    dependency_graph_lineage_references: tuple[DependencyGraphLineageChainReference, ...]
    records: tuple[CoordinationLineageChainRecord, ...]
    stale_lineage_visibility: StaleLineageVisibility
    missing_lineage_visibility: MissingLineageVisibility
    conflicting_lineage_visibility: ConflictingLineageVisibility
    prohibited_lineage_mutation_visibility: ProhibitedLineageMutationVisibility
    unsupported_lineage_transition_visibility: UnsupportedLineageTransitionVisibility
    diagnostics: tuple[CoordinationLineageChainDiagnostic, ...]
    governance_visibility: CoordinationLineageChainGovernance
    compatibility_manifest_reference: str
    compatibility_dependency_graph_reference: str
    chain_scope: str = V4_2_COORDINATION_LINEAGE_CHAIN_PURPOSE
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
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    lineage_mutation_enabled: bool = False
    dependency_resolution_enabled: bool = False
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
    hidden_lineage_resolution_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_references",
            "predecessor_references",
            "successor_references",
            "manifest_lineage_references",
            "dependency_graph_lineage_references",
            "records",
            "diagnostics",
        ):
            _set_tuple_field(self, field_name)


def default_coordination_lineage_chain_identity(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
) -> CoordinationLineageChainIdentity:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    return CoordinationLineageChainIdentity(
        chain_id="v4_2_coordination_lineage_chain_primary",
        coordination_cycle_id="v4_2_refresh_coordination_governance_cycle",
        chain_version="v4.2.3",
        source_manifest_reference=source_manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_coordination_manifest(source_manifest),
        source_dependency_graph_reference=source_graph.identity.graph_id,
        source_dependency_graph_hash_reference=hash_coordination_dependency_graph(source_graph),
        schema_version=V4_2_COORDINATION_LINEAGE_CHAIN_SCHEMA_VERSION,
        generated_at=V4_2_COORDINATION_LINEAGE_CHAIN_GENERATED_AT,
        provenance_reference="v4_2_coordination_lineage_chain_provenance_primary",
        lineage_reference="v4_2_coordination_lineage_chain_lineage_primary",
        continuity_reference="v4_2_coordination_lineage_chain_continuity_primary",
        diagnostics_reference="v4_2_coordination_lineage_chain_diagnostics_primary",
        governance_reference="v4_2_coordination_lineage_chain_governance_primary",
    )


def default_lineage_source_references(
    identity: CoordinationLineageChainIdentity | None = None,
) -> tuple[LineageSourceReference, ...]:
    source = identity or default_coordination_lineage_chain_identity()
    return (
        LineageSourceReference(
            source_reference_id="v4_2_lineage_source_manifest_foundation",
            source_type="coordination_manifest",
            source_id=source.source_manifest_reference,
            source_hash_reference=source.source_manifest_hash_reference,
            source_lineage_reference="v4_2_coordination_manifest_lineage_primary",
            source_continuity_reference="v4_2_coordination_manifest_continuity_primary",
            evidence_references=("v4_2_coordination_manifest_foundations_report",),
            deterministic_order=10,
        ),
        LineageSourceReference(
            source_reference_id="v4_2_lineage_source_dependency_graph",
            source_type="coordination_dependency_graph",
            source_id=source.source_dependency_graph_reference,
            source_hash_reference=source.source_dependency_graph_hash_reference,
            source_lineage_reference="v4_2_coordination_dependency_graph_lineage_primary",
            source_continuity_reference="v4_2_coordination_dependency_graph_continuity_primary",
            evidence_references=("v4_2_coordination_dependency_graph_governance_report",),
            deterministic_order=20,
        ),
        LineageSourceReference(
            source_reference_id="v4_2_lineage_source_v4_1_snapshot",
            source_type="prior_phase_snapshot",
            source_id="v4_1_refresh_governance_snapshot",
            source_hash_reference="v4_1_snapshot_hash_read_only",
            source_lineage_reference="v4_1_refresh_governance_lineage_snapshot",
            source_continuity_reference="v4_1_refresh_governance_continuity_snapshot",
            evidence_references=("v4_1_readiness_evidence",),
            deterministic_order=30,
        ),
        LineageSourceReference(
            source_reference_id="v4_2_lineage_source_future_provider",
            source_type="future_provider_contract",
            source_id="future_refresh_provider_contract",
            source_hash_reference="future_provider_hash_not_declared",
            source_lineage_reference="future_provider_lineage_not_declared",
            source_continuity_reference="future_provider_continuity_not_declared",
            evidence_references=("future_provider_visibility_only",),
            deterministic_order=40,
        ),
        LineageSourceReference(
            source_reference_id="v4_2_lineage_source_runtime_sequence",
            source_type="runtime_sequence",
            source_id="future_refresh_sequence",
            source_hash_reference="runtime_sequence_hash_not_applicable",
            source_lineage_reference="runtime_sequence_lineage_conflict_visible",
            source_continuity_reference="runtime_sequence_continuity_blocked",
            evidence_references=("runtime_sequence_blocked_visibility",),
            deterministic_order=50,
        ),
        LineageSourceReference(
            source_reference_id="v4_2_lineage_source_production_bundle",
            source_type="production_bundle",
            source_id="production_runtime_bundle",
            source_hash_reference="production_bundle_hash_not_consumed",
            source_lineage_reference="production_bundle_lineage_prohibited",
            source_continuity_reference="production_bundle_continuity_prohibited",
            evidence_references=("production_consumption_prohibited_visibility",),
            deterministic_order=60,
        ),
    )


def default_lineage_predecessor_references() -> tuple[LineagePredecessorReference, ...]:
    return (
        LineagePredecessorReference(
            predecessor_reference_id="v4_2_lineage_predecessor_manifest_foundation",
            predecessor_id="v4_2_coordination_manifest_primary",
            predecessor_type="coordination_manifest",
            predecessor_lineage_reference="v4_2_coordination_manifest_lineage_primary",
            predecessor_hash_reference="v4_2_coordination_manifest_hash",
            predecessor_state=LINEAGE_STATE_STABLE,
            deterministic_order=10,
        ),
        LineagePredecessorReference(
            predecessor_reference_id="v4_2_lineage_predecessor_dependency_graph",
            predecessor_id="v4_2_coordination_dependency_graph_primary",
            predecessor_type="coordination_dependency_graph",
            predecessor_lineage_reference="v4_2_coordination_dependency_graph_lineage_primary",
            predecessor_hash_reference="v4_2_coordination_dependency_graph_hash",
            predecessor_state=LINEAGE_STATE_STABLE,
            deterministic_order=20,
        ),
        LineagePredecessorReference(
            predecessor_reference_id="v4_2_lineage_predecessor_v4_1_snapshot",
            predecessor_id="v4_1_refresh_governance_snapshot",
            predecessor_type="prior_phase_snapshot",
            predecessor_lineage_reference="v4_1_refresh_governance_lineage_snapshot",
            predecessor_hash_reference="v4_1_snapshot_hash_read_only",
            predecessor_state=LINEAGE_STATE_STALE,
            deterministic_order=30,
            stale_visible=True,
        ),
        LineagePredecessorReference(
            predecessor_reference_id="v4_2_lineage_predecessor_future_provider_missing",
            predecessor_id="future_refresh_provider_contract",
            predecessor_type="future_provider_contract",
            predecessor_lineage_reference="future_provider_lineage_not_declared",
            predecessor_hash_reference="future_provider_hash_not_declared",
            predecessor_state=LINEAGE_STATE_MISSING,
            deterministic_order=40,
            missing_visible=True,
        ),
        LineagePredecessorReference(
            predecessor_reference_id="v4_2_lineage_predecessor_runtime_sequence_conflict",
            predecessor_id="future_refresh_sequence",
            predecessor_type="runtime_sequence",
            predecessor_lineage_reference="runtime_sequence_lineage_conflict_visible",
            predecessor_hash_reference="runtime_sequence_hash_not_applicable",
            predecessor_state=LINEAGE_STATE_CONFLICTING,
            deterministic_order=50,
        ),
        LineagePredecessorReference(
            predecessor_reference_id="v4_2_lineage_predecessor_production_mutation",
            predecessor_id="production_runtime_bundle",
            predecessor_type="production_bundle",
            predecessor_lineage_reference="production_bundle_lineage_prohibited",
            predecessor_hash_reference="production_bundle_hash_not_consumed",
            predecessor_state=LINEAGE_STATE_PROHIBITED_MUTATION,
            deterministic_order=60,
        ),
    )


def default_lineage_successor_references() -> tuple[LineageSuccessorReference, ...]:
    return (
        LineageSuccessorReference(
            successor_reference_id="v4_2_lineage_successor_dependency_graph",
            successor_id="v4_2_coordination_dependency_graph_primary",
            successor_type="coordination_dependency_graph",
            successor_lineage_reference="v4_2_coordination_dependency_graph_lineage_primary",
            successor_hash_reference="v4_2_coordination_dependency_graph_hash",
            successor_state=LINEAGE_STATE_STABLE,
            deterministic_order=10,
        ),
        LineageSuccessorReference(
            successor_reference_id="v4_2_lineage_successor_lineage_chain",
            successor_id="v4_2_coordination_lineage_chain_primary",
            successor_type="coordination_lineage_chain",
            successor_lineage_reference="v4_2_coordination_lineage_chain_lineage_primary",
            successor_hash_reference="v4_2_coordination_lineage_chain_hash",
            successor_state=LINEAGE_STATE_STABLE,
            deterministic_order=20,
        ),
        LineageSuccessorReference(
            successor_reference_id="v4_2_lineage_successor_stale_snapshot_visibility",
            successor_id="v4_1_snapshot_visibility_only",
            successor_type="visibility_only_snapshot",
            successor_lineage_reference="v4_1_snapshot_lineage_visibility_only",
            successor_hash_reference="v4_1_snapshot_hash_read_only",
            successor_state=LINEAGE_STATE_STALE,
            deterministic_order=30,
        ),
        LineageSuccessorReference(
            successor_reference_id="v4_2_lineage_successor_missing_provider_visibility",
            successor_id="future_provider_visibility_only",
            successor_type="visibility_only_provider",
            successor_lineage_reference="future_provider_lineage_visibility_only",
            successor_hash_reference="future_provider_hash_not_declared",
            successor_state=LINEAGE_STATE_MISSING,
            deterministic_order=40,
            missing_visible=True,
        ),
        LineageSuccessorReference(
            successor_reference_id="v4_2_lineage_successor_conflict_visibility",
            successor_id="runtime_sequence_conflict_visibility_only",
            successor_type="visibility_only_conflict",
            successor_lineage_reference="runtime_sequence_conflict_visibility_only",
            successor_hash_reference="runtime_sequence_hash_not_applicable",
            successor_state=LINEAGE_STATE_CONFLICTING,
            deterministic_order=50,
        ),
        LineageSuccessorReference(
            successor_reference_id="v4_2_lineage_successor_unsupported_transition",
            successor_id="future_refresh_execution_transition",
            successor_type="unsupported_transition",
            successor_lineage_reference="future_refresh_execution_lineage_unsupported",
            successor_hash_reference="future_refresh_execution_hash_not_applicable",
            successor_state=LINEAGE_STATE_UNSUPPORTED_TRANSITION,
            deterministic_order=60,
            unsupported_transition_visible=True,
        ),
    )


def default_coordination_lineage_chain_records(
    identity: CoordinationLineageChainIdentity | None = None,
) -> tuple[CoordinationLineageChainRecord, ...]:
    source = identity or default_coordination_lineage_chain_identity()
    manifest_ref = "v4_2_manifest_lineage_chain_reference_primary"
    graph_ref = "v4_2_dependency_graph_lineage_chain_reference_primary"
    return (
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_manifest_to_dependency_graph",
            source_reference_id="v4_2_lineage_source_manifest_foundation",
            predecessor_reference_id="v4_2_lineage_predecessor_manifest_foundation",
            successor_reference_id="v4_2_lineage_successor_dependency_graph",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_STABLE,
            transition_type=LINEAGE_TRANSITION_MANIFEST_TO_GRAPH,
            lineage_scope="manifest_foundation_to_dependency_graph_governance",
            reason="Manifest lineage is visible as dependency graph source evidence.",
            evidence_references=(source.source_manifest_reference, source.source_dependency_graph_reference),
            deterministic_order=10,
        ),
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_dependency_graph_to_chain",
            source_reference_id="v4_2_lineage_source_dependency_graph",
            predecessor_reference_id="v4_2_lineage_predecessor_dependency_graph",
            successor_reference_id="v4_2_lineage_successor_lineage_chain",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_STABLE,
            transition_type=LINEAGE_TRANSITION_GRAPH_TO_CHAIN,
            lineage_scope="dependency_graph_to_lineage_chain_governance",
            reason="Dependency graph lineage is preserved as descriptive chain evidence.",
            evidence_references=(source.source_dependency_graph_reference,),
            deterministic_order=20,
        ),
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_stale_v4_1_snapshot",
            source_reference_id="v4_2_lineage_source_v4_1_snapshot",
            predecessor_reference_id="v4_2_lineage_predecessor_v4_1_snapshot",
            successor_reference_id="v4_2_lineage_successor_stale_snapshot_visibility",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_STALE,
            transition_type=LINEAGE_TRANSITION_PRIOR_SNAPSHOT,
            lineage_scope="prior_phase_snapshot_visibility",
            reason="Prior v4.1 snapshot lineage remains stale read-only evidence.",
            evidence_references=("v4_1_refresh_governance_snapshot",),
            deterministic_order=30,
            severity="warning",
            fail_visible=True,
            stale_visible=True,
        ),
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_missing_future_provider",
            source_reference_id="v4_2_lineage_source_future_provider",
            predecessor_reference_id="v4_2_lineage_predecessor_future_provider_missing",
            successor_reference_id="v4_2_lineage_successor_missing_provider_visibility",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_MISSING,
            transition_type=LINEAGE_TRANSITION_UNDECLARED_PROVIDER,
            lineage_scope="future_provider_lineage_visibility",
            reason="Future provider lineage is not declared and remains missing.",
            evidence_references=("future_refresh_provider_contract",),
            deterministic_order=40,
            severity="warning",
            fail_visible=True,
            missing_visible=True,
        ),
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_conflicting_runtime_sequence",
            source_reference_id="v4_2_lineage_source_runtime_sequence",
            predecessor_reference_id="v4_2_lineage_predecessor_runtime_sequence_conflict",
            successor_reference_id="v4_2_lineage_successor_conflict_visibility",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_CONFLICTING,
            transition_type=LINEAGE_TRANSITION_RUNTIME_SEQUENCE,
            lineage_scope="runtime_sequence_conflict_visibility",
            reason="Runtime sequence lineage conflicts with the non-execution boundary.",
            evidence_references=("future_refresh_sequence", "orchestration_execution_prohibited"),
            deterministic_order=50,
            severity="blocked",
            fail_visible=True,
            conflicting_visible=True,
        ),
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_prohibited_production_mutation",
            source_reference_id="v4_2_lineage_source_production_bundle",
            predecessor_reference_id="v4_2_lineage_predecessor_production_mutation",
            successor_reference_id="v4_2_lineage_successor_unsupported_transition",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_PROHIBITED_MUTATION,
            transition_type=LINEAGE_TRANSITION_PRODUCTION_MUTATION,
            lineage_scope="production_lineage_mutation_visibility",
            reason="Production lineage mutation is prohibited and remains fail-visible.",
            evidence_references=("production_runtime_bundle", "runtime_mutation_prohibited"),
            deterministic_order=60,
            severity="prohibited",
            fail_visible=True,
            prohibited_mutation_visible=True,
        ),
        CoordinationLineageChainRecord(
            record_id="v4_2_lineage_record_unsupported_future_transition",
            source_reference_id="v4_2_lineage_source_future_provider",
            predecessor_reference_id="v4_2_lineage_predecessor_future_provider_missing",
            successor_reference_id="v4_2_lineage_successor_unsupported_transition",
            manifest_lineage_reference_id=manifest_ref,
            dependency_graph_lineage_reference_id=graph_ref,
            lineage_state=LINEAGE_STATE_UNSUPPORTED_TRANSITION,
            transition_type=LINEAGE_TRANSITION_FUTURE_UNSUPPORTED,
            lineage_scope="future_refresh_transition_visibility",
            reason="Future refresh transition lineage is unsupported and does not execute.",
            evidence_references=("future_refresh_execution_transition",),
            deterministic_order=70,
            severity="warning",
            fail_visible=True,
            unsupported_transition_visible=True,
        ),
    )


def default_manifest_lineage_chain_references(
    identity: CoordinationLineageChainIdentity | None = None,
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> tuple[ManifestLineageChainReference, ...]:
    source = identity or default_coordination_lineage_chain_identity()
    chain_records = records or default_coordination_lineage_chain_records(source)
    return (
        ManifestLineageChainReference(
            manifest_lineage_reference_id="v4_2_manifest_lineage_chain_reference_primary",
            manifest_reference=source.source_manifest_reference,
            manifest_hash_reference=source.source_manifest_hash_reference,
            manifest_lineage_reference="v4_2_coordination_manifest_lineage_primary",
            manifest_continuity_reference="v4_2_coordination_manifest_continuity_primary",
            record_references=tuple(record.record_id for record in chain_records),
            deterministic_order=10,
        ),
    )


def default_dependency_graph_lineage_chain_references(
    identity: CoordinationLineageChainIdentity | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> tuple[DependencyGraphLineageChainReference, ...]:
    source = identity or default_coordination_lineage_chain_identity()
    graph = dependency_graph
    if graph is None:
        manifest = default_coordination_manifest()
        graph = default_coordination_dependency_graph(manifest)
    chain_records = records or default_coordination_lineage_chain_records(source)
    return (
        DependencyGraphLineageChainReference(
            dependency_graph_lineage_reference_id="v4_2_dependency_graph_lineage_chain_reference_primary",
            dependency_graph_reference=source.source_dependency_graph_reference,
            dependency_graph_hash_reference=source.source_dependency_graph_hash_reference,
            dependency_graph_lineage_reference=graph.identity.lineage_reference,
            dependency_graph_continuity_reference=graph.identity.continuity_reference,
            node_references=tuple(node.node_id for node in graph.nodes),
            edge_references=tuple(edge.edge_id for edge in graph.edges),
            record_references=tuple(record.record_id for record in chain_records),
            deterministic_order=10,
        ),
    )


def default_stale_lineage_visibility(
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> StaleLineageVisibility:
    chain_records = records or default_coordination_lineage_chain_records()
    stale_records = tuple(record for record in chain_records if record.lineage_state == LINEAGE_STATE_STALE)
    return StaleLineageVisibility(
        stale_visibility_id="v4_2_coordination_lineage_chain_stale_visibility_primary",
        stale_record_ids=tuple(record.record_id for record in stale_records),
        stale_source_reference_ids=tuple(record.source_reference_id for record in stale_records),
        stale_predecessor_reference_ids=tuple(record.predecessor_reference_id for record in stale_records),
        stale_reason_visibility=tuple(record.reason for record in stale_records),
        deterministic_order=10,
    )


def default_missing_lineage_visibility(
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> MissingLineageVisibility:
    chain_records = records or default_coordination_lineage_chain_records()
    missing_records = tuple(record for record in chain_records if record.lineage_state == LINEAGE_STATE_MISSING)
    return MissingLineageVisibility(
        missing_visibility_id="v4_2_coordination_lineage_chain_missing_visibility_primary",
        missing_record_ids=tuple(record.record_id for record in missing_records),
        missing_successor_reference_ids=tuple(record.successor_reference_id for record in missing_records),
        missing_reference_ids=tuple(record.predecessor_reference_id for record in missing_records),
        missing_reason_visibility=tuple(record.reason for record in missing_records),
        deterministic_order=20,
    )


def default_conflicting_lineage_visibility(
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> ConflictingLineageVisibility:
    chain_records = records or default_coordination_lineage_chain_records()
    conflicting_records = tuple(record for record in chain_records if record.lineage_state == LINEAGE_STATE_CONFLICTING)
    return ConflictingLineageVisibility(
        conflicting_visibility_id="v4_2_coordination_lineage_chain_conflicting_visibility_primary",
        conflicting_record_ids=tuple(record.record_id for record in conflicting_records),
        conflict_pair_visibility=tuple(
            f"{record.predecessor_reference_id}->{record.successor_reference_id}" for record in conflicting_records
        ),
        conflict_reason_visibility=tuple(record.reason for record in conflicting_records),
        deterministic_order=30,
    )


def default_prohibited_lineage_mutation_visibility(
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> ProhibitedLineageMutationVisibility:
    chain_records = records or default_coordination_lineage_chain_records()
    prohibited_records = tuple(
        record for record in chain_records if record.lineage_state == LINEAGE_STATE_PROHIBITED_MUTATION
    )
    return ProhibitedLineageMutationVisibility(
        prohibited_mutation_visibility_id="v4_2_coordination_lineage_chain_prohibited_mutation_visibility_primary",
        prohibited_record_ids=tuple(record.record_id for record in prohibited_records),
        prohibited_capabilities=PROHIBITED_COORDINATION_LINEAGE_CHAIN_CAPABILITIES,
        prohibited_reason_visibility=tuple(
            f"v4_2_prohibited_lineage_chain_capability_{capability}"
            for capability in PROHIBITED_COORDINATION_LINEAGE_CHAIN_CAPABILITIES
        ),
        deterministic_order=40,
    )


def default_unsupported_lineage_transition_visibility(
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> UnsupportedLineageTransitionVisibility:
    chain_records = records or default_coordination_lineage_chain_records()
    unsupported_records = tuple(
        record for record in chain_records if record.lineage_state == LINEAGE_STATE_UNSUPPORTED_TRANSITION
    )
    return UnsupportedLineageTransitionVisibility(
        unsupported_transition_visibility_id=(
            "v4_2_coordination_lineage_chain_unsupported_transition_visibility_primary"
        ),
        unsupported_record_ids=tuple(record.record_id for record in unsupported_records),
        unsupported_transition_ids=tuple(record.transition_type for record in unsupported_records),
        unknown_transition_visibility=("future_lineage_transition_unknown_until_declared",),
        unsupported_reason_visibility=tuple(record.reason for record in unsupported_records),
        deterministic_order=50,
    )


def default_coordination_lineage_chain_diagnostics(
    records: tuple[CoordinationLineageChainRecord, ...] | None = None,
) -> tuple[CoordinationLineageChainDiagnostic, ...]:
    chain_records = records or default_coordination_lineage_chain_records()
    stale_record_ids = tuple(record.record_id for record in chain_records if record.lineage_state == LINEAGE_STATE_STALE)
    missing_record_ids = tuple(
        record.record_id for record in chain_records if record.lineage_state == LINEAGE_STATE_MISSING
    )
    conflicting_record_ids = tuple(
        record.record_id for record in chain_records if record.lineage_state == LINEAGE_STATE_CONFLICTING
    )
    prohibited_record_ids = tuple(
        record.record_id for record in chain_records if record.lineage_state == LINEAGE_STATE_PROHIBITED_MUTATION
    )
    unsupported_record_ids = tuple(
        record.record_id for record in chain_records if record.lineage_state == LINEAGE_STATE_UNSUPPORTED_TRANSITION
    )
    all_record_ids = tuple(record.record_id for record in chain_records)
    all_reference_ids = tuple(
        reference
        for record in chain_records
        for reference in (
            record.source_reference_id,
            record.predecessor_reference_id,
            record.successor_reference_id,
            record.manifest_lineage_reference_id,
            record.dependency_graph_lineage_reference_id,
        )
    )
    return (
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_stale_diagnostic",
            category=LINEAGE_DIAGNOSTIC_STALE,
            severity="warning",
            finding="Stale lineage remains fail-visible read-only evidence.",
            affected_record_ids=stale_record_ids,
            affected_reference_ids=(),
            deterministic_order=10,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_missing_diagnostic",
            category=LINEAGE_DIAGNOSTIC_MISSING,
            severity="warning",
            finding="Missing lineage remains fail-visible and unrepaired.",
            affected_record_ids=missing_record_ids,
            affected_reference_ids=(),
            deterministic_order=20,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_conflicting_diagnostic",
            category=LINEAGE_DIAGNOSTIC_CONFLICTING,
            severity="blocked",
            finding="Conflicting lineage remains fail-visible and unresolved.",
            affected_record_ids=conflicting_record_ids,
            affected_reference_ids=(),
            deterministic_order=30,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_prohibited_mutation_diagnostic",
            category=LINEAGE_DIAGNOSTIC_PROHIBITED_MUTATION,
            severity="prohibited",
            finding="Prohibited lineage mutation remains visible and inactive.",
            affected_record_ids=prohibited_record_ids,
            affected_reference_ids=(),
            deterministic_order=40,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_unsupported_transition_diagnostic",
            category=LINEAGE_DIAGNOSTIC_UNSUPPORTED_TRANSITION,
            severity="warning",
            finding="Unsupported lineage transitions remain fail-visible and non-executing.",
            affected_record_ids=unsupported_record_ids,
            affected_reference_ids=(),
            deterministic_order=50,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_continuity_diagnostic",
            category=LINEAGE_DIAGNOSTIC_CONTINUITY,
            severity="info",
            finding="Lineage continuity is preserved without repair or inference.",
            affected_record_ids=all_record_ids,
            affected_reference_ids=all_reference_ids,
            deterministic_order=60,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_manifest_compatibility_diagnostic",
            category=LINEAGE_DIAGNOSTIC_MANIFEST_COMPATIBILITY,
            severity="info",
            finding="Manifest lineage compatibility is visible as deterministic evidence.",
            affected_record_ids=all_record_ids,
            affected_reference_ids=("v4_2_manifest_lineage_chain_reference_primary",),
            deterministic_order=70,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_dependency_graph_compatibility_diagnostic",
            category=LINEAGE_DIAGNOSTIC_GRAPH_COMPATIBILITY,
            severity="info",
            finding="Dependency graph lineage compatibility is visible as deterministic evidence.",
            affected_record_ids=all_record_ids,
            affected_reference_ids=("v4_2_dependency_graph_lineage_chain_reference_primary",),
            deterministic_order=80,
        ),
        CoordinationLineageChainDiagnostic(
            diagnostic_id="v4_2_coordination_lineage_chain_non_execution_diagnostic",
            category=LINEAGE_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Lineage chain governance remains non-executing and non-authorizing.",
            affected_record_ids=all_record_ids,
            affected_reference_ids=(),
            deterministic_order=90,
        ),
    )


def default_coordination_lineage_chain_governance(
    identity: CoordinationLineageChainIdentity | None = None,
) -> CoordinationLineageChainGovernance:
    source = identity or default_coordination_lineage_chain_identity()
    return CoordinationLineageChainGovernance(
        governance_id=source.governance_reference,
        governance_references=(
            "v4_2_coordination_manifest_governance_primary",
            "v4_2_coordination_dependency_graph_governance_boundary",
            "v4_2_coordination_lineage_chain_governance_boundary",
        ),
        explicit_limitations=EXPLICIT_COORDINATION_LINEAGE_CHAIN_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_COORDINATION_LINEAGE_CHAIN_PROHIBITIONS,
        deterministic_order=10,
    )


def default_coordination_lineage_chain(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
) -> CoordinationLineageChain:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    identity = default_coordination_lineage_chain_identity(source_manifest, source_graph)
    records = default_coordination_lineage_chain_records(identity)
    return CoordinationLineageChain(
        identity=identity,
        source_references=default_lineage_source_references(identity),
        predecessor_references=default_lineage_predecessor_references(),
        successor_references=default_lineage_successor_references(),
        manifest_lineage_references=default_manifest_lineage_chain_references(identity, records),
        dependency_graph_lineage_references=default_dependency_graph_lineage_chain_references(
            identity,
            source_graph,
            records,
        ),
        records=records,
        stale_lineage_visibility=default_stale_lineage_visibility(records),
        missing_lineage_visibility=default_missing_lineage_visibility(records),
        conflicting_lineage_visibility=default_conflicting_lineage_visibility(records),
        prohibited_lineage_mutation_visibility=default_prohibited_lineage_mutation_visibility(records),
        unsupported_lineage_transition_visibility=default_unsupported_lineage_transition_visibility(records),
        diagnostics=default_coordination_lineage_chain_diagnostics(records),
        governance_visibility=default_coordination_lineage_chain_governance(identity),
        compatibility_manifest_reference=source_manifest.identity.manifest_id,
        compatibility_dependency_graph_reference=source_graph.identity.graph_id,
    )
