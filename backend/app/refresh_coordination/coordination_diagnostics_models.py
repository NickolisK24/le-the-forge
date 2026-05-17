"""Deterministic v4.2 coordination diagnostics and explainability models.

Diagnostics and explainability aggregation is descriptive evidence only. It
does not remediate, correct drift, route requests, execute orchestration,
execute refreshes, execute sequences, schedule work, resolve dependencies,
repair lineage, infer lineage, consume production bundles, integrate with
planners, authorize behavior, rank choices, score choices, select options, or
mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import (
    CoordinationDependencyGraph,
    default_coordination_dependency_graph,
)
from .coordination_drift_hashing import hash_coordination_drift_certification
from .coordination_drift_models import CoordinationDriftCertification, default_coordination_drift_certification
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


V4_2_COORDINATION_DIAGNOSTICS_PHASE_ID = "v4_2_coordination_diagnostics_explainability"
V4_2_COORDINATION_DIAGNOSTICS_SCHEMA_VERSION = "v4_2.coordination_diagnostics_explainability.1"
V4_2_COORDINATION_DIAGNOSTICS_REPORT_SCHEMA_VERSION = (
    "v4_2.coordination_diagnostics_explainability_report.1"
)
V4_2_COORDINATION_DIAGNOSTICS_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_COORDINATION_DIAGNOSTICS_STATUS_STABLE = "v4_2_coordination_diagnostics_explainability_stable"
V4_2_COORDINATION_DIAGNOSTICS_STATUS_BLOCKED = "v4_2_coordination_diagnostics_explainability_blocked"
V4_2_COORDINATION_DIAGNOSTICS_PURPOSE = (
    "deterministic_refresh_coordination_diagnostics_explainability_only"
)

DIAGNOSTIC_AGGREGATION_UNSUPPORTED = "unsupported"
DIAGNOSTIC_AGGREGATION_PROHIBITED = "prohibited"
DIAGNOSTIC_AGGREGATION_BLOCKED = "blocked"
DIAGNOSTIC_AGGREGATION_STALE = "stale"
DIAGNOSTIC_AGGREGATION_MISSING = "missing"
DIAGNOSTIC_AGGREGATION_CONFLICTING = "conflicting"
DIAGNOSTIC_AGGREGATION_INFO = "info"
DIAGNOSTIC_AGGREGATION_STATES: tuple[str, ...] = (
    DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
    DIAGNOSTIC_AGGREGATION_PROHIBITED,
    DIAGNOSTIC_AGGREGATION_BLOCKED,
    DIAGNOSTIC_AGGREGATION_STALE,
    DIAGNOSTIC_AGGREGATION_MISSING,
    DIAGNOSTIC_AGGREGATION_CONFLICTING,
    DIAGNOSTIC_AGGREGATION_INFO,
)
FAIL_VISIBLE_DIAGNOSTIC_AGGREGATION_STATES: tuple[str, ...] = (
    DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
    DIAGNOSTIC_AGGREGATION_PROHIBITED,
    DIAGNOSTIC_AGGREGATION_BLOCKED,
    DIAGNOSTIC_AGGREGATION_STALE,
    DIAGNOSTIC_AGGREGATION_MISSING,
    DIAGNOSTIC_AGGREGATION_CONFLICTING,
)

DIAGNOSTIC_SEVERITY_INFO = "info"
DIAGNOSTIC_SEVERITY_WARNING = "warning"
DIAGNOSTIC_SEVERITY_BLOCKED = "blocked"
DIAGNOSTIC_SEVERITY_PROHIBITED = "prohibited"
DIAGNOSTIC_SEVERITIES: tuple[str, ...] = (
    DIAGNOSTIC_SEVERITY_INFO,
    DIAGNOSTIC_SEVERITY_WARNING,
    DIAGNOSTIC_SEVERITY_BLOCKED,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
)

PROHIBITED_COORDINATION_DIAGNOSTICS_CAPABILITIES: tuple[str, ...] = (
    "remediation",
    "automatic_correction",
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
    "automatic_rollback",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "authorization_systems",
    "approval_systems",
    "operational_execution",
    "hidden_correction",
    "implicit_execution_pathways",
)

EXPLICIT_COORDINATION_DIAGNOSTICS_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 7 creates deterministic refresh coordination diagnostics and explainability aggregation only.",
    "v4.2 Phase 7 does not enable remediation.",
    "v4.2 Phase 7 does not enable automatic correction.",
    "v4.2 Phase 7 does not enable drift correction.",
    "v4.2 Phase 7 does not enable drift remediation.",
    "v4.2 Phase 7 does not enable routing execution.",
    "v4.2 Phase 7 does not enable orchestration execution.",
    "v4.2 Phase 7 does not enable refresh execution.",
    "v4.2 Phase 7 does not enable sequencing execution.",
    "v4.2 Phase 7 does not enable scheduling execution.",
    "v4.2 Phase 7 does not enable dependency resolution.",
    "v4.2 Phase 7 does not enable lineage repair.",
    "v4.2 Phase 7 does not enable lineage inference.",
    "v4.2 Phase 7 does not enable planner integration.",
    "v4.2 Phase 7 does not enable production consumption.",
    "v4.2 Phase 7 does not enable runtime mutation.",
    "v4.2 Phase 7 does not enable ranking scoring or selection.",
    "v4.2 Phase 7 does not enable authorization or approval.",
)

EXPLICIT_COORDINATION_DIAGNOSTICS_PROHIBITIONS: tuple[str, ...] = (
    "No remediation exists.",
    "No automatic correction exists.",
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
    "No automatic rollback exists.",
    "No ranking, scoring, or selection behavior exists.",
    "No authorization or approval behavior exists.",
    "No operational execution exists.",
    "No hidden correction exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationDiagnosticsIdentity:
    diagnostics_id: str
    coordination_cycle_id: str
    diagnostics_version: str
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
    source_drift_reference: str
    source_drift_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    aggregation_reference: str
    explainability_reference: str
    diagnostics_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_COORDINATION_DIAGNOSTICS_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
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
    hidden_correction_enabled: bool = False


@dataclass(frozen=True)
class ManifestDiagnosticReference:
    manifest_diagnostic_reference_id: str
    manifest_reference: str
    manifest_hash_reference: str
    diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class DependencyGraphDiagnosticReference:
    dependency_graph_diagnostic_reference_id: str
    dependency_graph_reference: str
    dependency_graph_hash_reference: str
    diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class LineageDiagnosticReference:
    lineage_diagnostic_reference_id: str
    lineage_chain_reference: str
    lineage_chain_hash_reference: str
    diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class SequencingDiagnosticReference:
    sequencing_diagnostic_reference_id: str
    sequencing_reference: str
    sequencing_hash_reference: str
    diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class RoutingDiagnosticReference:
    routing_diagnostic_reference_id: str
    routing_reference: str
    routing_hash_reference: str
    diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class DriftDiagnosticReference:
    drift_diagnostic_reference_id: str
    drift_reference: str
    drift_hash_reference: str
    diagnostic_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class CrossLayerCoordinationDiagnosticRecord:
    diagnostic_record_id: str
    aggregation_state: str
    severity: str
    source_layers: tuple[str, ...]
    source_diagnostic_ids: tuple[str, ...]
    layer_references: tuple[str, ...]
    evidence_references: tuple[str, ...]
    explanation_reference: str
    reason: str
    deterministic_order: int
    fail_visible: bool = False
    unsupported_visible: bool = False
    prohibited_visible: bool = False
    blocked_visible: bool = False
    stale_visible: bool = False
    missing_visible: bool = False
    conflicting_visible: bool = False
    descriptive_only: bool = True
    non_authorizing: bool = True
    hidden: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
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
    automatic_rollback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_layers", "source_diagnostic_ids", "layer_references", "evidence_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class StateAggregationVisibility:
    aggregation_id: str
    aggregation_state: str
    diagnostic_record_ids: tuple[str, ...]
    source_layers: tuple[str, ...]
    reason_visibility: tuple[str, ...]
    deterministic_order: int
    state_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("diagnostic_record_ids", "source_layers", "reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class DiagnosticSeverityVisibility:
    severity_visibility_id: str
    severity: str
    diagnostic_record_ids: tuple[str, ...]
    deterministic_order: int
    severity_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "diagnostic_record_ids")


@dataclass(frozen=True)
class CoordinationExplanationRecord:
    explanation_id: str
    diagnostic_record_id: str
    aggregation_state: str
    severity: str
    explanation_summary: str
    evidence_references: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class FailVisibleExplanationSummary:
    summary_id: str
    explanation_ids: tuple[str, ...]
    diagnostic_record_ids: tuple[str, ...]
    aggregation_state_counts: tuple[str, ...]
    summary_lines: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("explanation_ids", "diagnostic_record_ids", "aggregation_state_counts", "summary_lines"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDiagnosticsGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
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
class CoordinationDiagnosticsExplainability:
    identity: CoordinationDiagnosticsIdentity
    manifest_diagnostic_references: tuple[ManifestDiagnosticReference, ...]
    dependency_graph_diagnostic_references: tuple[DependencyGraphDiagnosticReference, ...]
    lineage_diagnostic_references: tuple[LineageDiagnosticReference, ...]
    sequencing_diagnostic_references: tuple[SequencingDiagnosticReference, ...]
    routing_diagnostic_references: tuple[RoutingDiagnosticReference, ...]
    drift_diagnostic_references: tuple[DriftDiagnosticReference, ...]
    diagnostic_records: tuple[CrossLayerCoordinationDiagnosticRecord, ...]
    unsupported_state_aggregation: StateAggregationVisibility
    prohibited_state_aggregation: StateAggregationVisibility
    blocked_state_aggregation: StateAggregationVisibility
    stale_state_aggregation: StateAggregationVisibility
    missing_state_aggregation: StateAggregationVisibility
    conflicting_state_aggregation: StateAggregationVisibility
    severity_visibility: tuple[DiagnosticSeverityVisibility, ...]
    explanation_records: tuple[CoordinationExplanationRecord, ...]
    fail_visible_explanation_summary: FailVisibleExplanationSummary
    governance_visibility: CoordinationDiagnosticsGovernance
    compatibility_manifest_reference: str
    compatibility_dependency_graph_reference: str
    compatibility_lineage_chain_reference: str
    compatibility_sequencing_reference: str
    compatibility_routing_reference: str
    compatibility_drift_reference: str
    diagnostics_scope: str = V4_2_COORDINATION_DIAGNOSTICS_PURPOSE
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
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
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
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    operational_execution_enabled: bool = False
    hidden_correction_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False


def _diagnostic_ids(source: object) -> tuple[str, ...]:
    return tuple(diagnostic.diagnostic_id for diagnostic in getattr(source, "diagnostics", ()))


def default_coordination_diagnostics_identity(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    drift: CoordinationDriftCertification | None = None,
) -> CoordinationDiagnosticsIdentity:
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
    source_drift = drift or default_coordination_drift_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    return CoordinationDiagnosticsIdentity(
        diagnostics_id="v4_2_coordination_diagnostics_explainability_primary",
        coordination_cycle_id="v4_2_refresh_coordination_cycle",
        diagnostics_version="v4_2_phase_7",
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
        source_drift_reference=source_drift.identity.drift_certification_id,
        source_drift_hash_reference=hash_coordination_drift_certification(source_drift),
        schema_version=V4_2_COORDINATION_DIAGNOSTICS_SCHEMA_VERSION,
        generated_at=V4_2_COORDINATION_DIAGNOSTICS_GENERATED_AT,
        provenance_reference="v4_2_coordination_diagnostics_provenance_primary",
        aggregation_reference="v4_2_coordination_diagnostics_aggregation_primary",
        explainability_reference="v4_2_coordination_explainability_primary",
        diagnostics_reference="v4_2_coordination_diagnostics_records_primary",
        governance_reference="v4_2_coordination_diagnostics_governance_primary",
    )


def default_manifest_diagnostic_references(
    identity: CoordinationDiagnosticsIdentity | None = None,
    manifest: CoordinationManifest | None = None,
) -> tuple[ManifestDiagnosticReference, ...]:
    source_identity = identity or default_coordination_diagnostics_identity()
    source_manifest = manifest or default_coordination_manifest()
    return (
        ManifestDiagnosticReference(
            manifest_diagnostic_reference_id="v4_2_manifest_diagnostic_reference_primary",
            manifest_reference=source_identity.source_manifest_reference,
            manifest_hash_reference=source_identity.source_manifest_hash_reference,
            diagnostic_ids=_diagnostic_ids(source_manifest),
            deterministic_order=10,
        ),
    )


def default_dependency_graph_diagnostic_references(
    identity: CoordinationDiagnosticsIdentity | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
) -> tuple[DependencyGraphDiagnosticReference, ...]:
    source_identity = identity or default_coordination_diagnostics_identity()
    graph = dependency_graph or default_coordination_dependency_graph()
    return (
        DependencyGraphDiagnosticReference(
            dependency_graph_diagnostic_reference_id="v4_2_dependency_graph_diagnostic_reference_primary",
            dependency_graph_reference=source_identity.source_dependency_graph_reference,
            dependency_graph_hash_reference=source_identity.source_dependency_graph_hash_reference,
            diagnostic_ids=_diagnostic_ids(graph),
            deterministic_order=20,
        ),
    )


def default_lineage_diagnostic_references(
    identity: CoordinationDiagnosticsIdentity | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
) -> tuple[LineageDiagnosticReference, ...]:
    source_identity = identity or default_coordination_diagnostics_identity()
    lineage = lineage_chain or default_coordination_lineage_chain()
    return (
        LineageDiagnosticReference(
            lineage_diagnostic_reference_id="v4_2_lineage_diagnostic_reference_primary",
            lineage_chain_reference=source_identity.source_lineage_chain_reference,
            lineage_chain_hash_reference=source_identity.source_lineage_chain_hash_reference,
            diagnostic_ids=_diagnostic_ids(lineage),
            deterministic_order=30,
        ),
    )


def default_sequencing_diagnostic_references(
    identity: CoordinationDiagnosticsIdentity | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
) -> tuple[SequencingDiagnosticReference, ...]:
    source_identity = identity or default_coordination_diagnostics_identity()
    source_sequencing = sequencing or default_coordination_sequencing_intelligence()
    return (
        SequencingDiagnosticReference(
            sequencing_diagnostic_reference_id="v4_2_sequencing_diagnostic_reference_primary",
            sequencing_reference=source_identity.source_sequencing_reference,
            sequencing_hash_reference=source_identity.source_sequencing_hash_reference,
            diagnostic_ids=_diagnostic_ids(source_sequencing),
            deterministic_order=40,
        ),
    )


def default_routing_diagnostic_references(
    identity: CoordinationDiagnosticsIdentity | None = None,
    routing: GovernanceRoutingVisibility | None = None,
) -> tuple[RoutingDiagnosticReference, ...]:
    source_identity = identity or default_coordination_diagnostics_identity()
    source_routing = routing or default_governance_routing_visibility()
    return (
        RoutingDiagnosticReference(
            routing_diagnostic_reference_id="v4_2_routing_diagnostic_reference_primary",
            routing_reference=source_identity.source_routing_reference,
            routing_hash_reference=source_identity.source_routing_hash_reference,
            diagnostic_ids=_diagnostic_ids(source_routing),
            deterministic_order=50,
        ),
    )


def default_drift_diagnostic_references(
    identity: CoordinationDiagnosticsIdentity | None = None,
    drift: CoordinationDriftCertification | None = None,
) -> tuple[DriftDiagnosticReference, ...]:
    source_identity = identity or default_coordination_diagnostics_identity()
    source_drift = drift or default_coordination_drift_certification()
    return (
        DriftDiagnosticReference(
            drift_diagnostic_reference_id="v4_2_drift_diagnostic_reference_primary",
            drift_reference=source_identity.source_drift_reference,
            drift_hash_reference=source_identity.source_drift_hash_reference,
            diagnostic_ids=_diagnostic_ids(source_drift),
            deterministic_order=60,
        ),
    )


def default_cross_layer_coordination_diagnostic_records() -> tuple[CrossLayerCoordinationDiagnosticRecord, ...]:
    specs: tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], str, int], ...] = (
        (
            "v4_2_coordination_diagnostics_unsupported_aggregation",
            DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
            DIAGNOSTIC_SEVERITY_WARNING,
            ("dependency_graph", "sequencing", "routing", "drift"),
            (
                "v4_2_coordination_dependency_graph_unsupported_diagnostic",
                "v4_2_coordination_sequencing_unsupported_diagnostic",
                "v4_2_governance_routing_unsupported_diagnostic",
                "v4_2_coordination_drift_unsupported_transition_diagnostic",
            ),
            ("future_provider_contract", "future_drift_transition_contract"),
            ("unsupported_dependency_visible", "unsupported_transition_visible"),
            "Unsupported coordination states remain visible and unresolved.",
            10,
        ),
        (
            "v4_2_coordination_diagnostics_prohibited_aggregation",
            DIAGNOSTIC_AGGREGATION_PROHIBITED,
            DIAGNOSTIC_SEVERITY_PROHIBITED,
            ("manifest", "dependency_graph", "sequencing", "routing", "drift"),
            (
                "v4_2_coordination_diagnostic_prohibited_state_visible",
                "v4_2_coordination_dependency_graph_prohibited_diagnostic",
                "v4_2_coordination_sequencing_prohibited_diagnostic",
                "v4_2_governance_routing_prohibited_diagnostic",
                "v4_2_coordination_drift_prohibited_correction_diagnostic",
            ),
            ("production_consumption_prohibited", "drift_correction_prohibited"),
            ("prohibited_state_visible", "prohibited_correction_visible"),
            "Prohibited coordination states remain visible and inactive.",
            20,
        ),
        (
            "v4_2_coordination_diagnostics_blocked_aggregation",
            DIAGNOSTIC_AGGREGATION_BLOCKED,
            DIAGNOSTIC_SEVERITY_BLOCKED,
            ("manifest", "dependency_graph", "sequencing", "routing"),
            (
                "v4_2_coordination_diagnostic_blocked_coordination_visible",
                "v4_2_coordination_dependency_graph_blocked_diagnostic",
                "v4_2_coordination_sequencing_blocked_diagnostic",
                "v4_2_governance_routing_blocked_diagnostic",
            ),
            ("runtime_sequence_blocked", "runtime_route_blocked"),
            ("blocked_state_visible", "blocked_runtime_visibility"),
            "Blocked coordination states remain fail-visible and non-executing.",
            30,
        ),
        (
            "v4_2_coordination_diagnostics_stale_aggregation",
            DIAGNOSTIC_AGGREGATION_STALE,
            DIAGNOSTIC_SEVERITY_WARNING,
            ("manifest", "lineage", "sequencing", "routing", "drift"),
            (
                "v4_2_coordination_diagnostic_stale_snapshot_visible",
                "v4_2_coordination_lineage_chain_stale_diagnostic",
                "v4_2_coordination_sequencing_stale_diagnostic",
                "v4_2_governance_routing_stale_diagnostic",
                "v4_2_coordination_drift_stale_diagnostic",
            ),
            ("v4_1_refresh_governance_snapshot",),
            ("stale_snapshot_visible", "stale_drift_visible"),
            "Stale coordination states remain read-only evidence.",
            40,
        ),
        (
            "v4_2_coordination_diagnostics_missing_aggregation",
            DIAGNOSTIC_AGGREGATION_MISSING,
            DIAGNOSTIC_SEVERITY_WARNING,
            ("lineage", "sequencing", "routing", "drift"),
            (
                "v4_2_coordination_lineage_chain_missing_diagnostic",
                "v4_2_coordination_sequencing_missing_diagnostic",
                "v4_2_governance_routing_missing_diagnostic",
                "v4_2_coordination_drift_missing_diagnostic",
            ),
            ("future_lineage_missing", "future_route_target_missing", "future_dependency_drift_target_missing"),
            ("missing_state_visible", "missing_drift_visible"),
            "Missing coordination states remain visible and unrepaired.",
            50,
        ),
        (
            "v4_2_coordination_diagnostics_conflicting_aggregation",
            DIAGNOSTIC_AGGREGATION_CONFLICTING,
            DIAGNOSTIC_SEVERITY_BLOCKED,
            ("lineage", "sequencing", "routing", "drift"),
            (
                "v4_2_coordination_lineage_chain_conflicting_diagnostic",
                "v4_2_coordination_sequencing_conflicting_diagnostic",
                "v4_2_governance_routing_conflicting_diagnostic",
                "v4_2_coordination_drift_conflicting_diagnostic",
            ),
            ("runtime_route_conflict_request", "runtime_sequence_order_conflict"),
            ("conflicting_state_visible", "conflicting_drift_visible"),
            "Conflicting coordination states remain visible and unresolved.",
            60,
        ),
        (
            "v4_2_coordination_diagnostics_compatibility_aggregation",
            DIAGNOSTIC_AGGREGATION_INFO,
            DIAGNOSTIC_SEVERITY_INFO,
            ("manifest", "dependency_graph", "lineage", "sequencing", "routing", "drift"),
            (
                "v4_2_coordination_diagnostic_lineage_continuity_visible",
                "v4_2_coordination_dependency_graph_continuity_diagnostic",
                "v4_2_coordination_lineage_chain_compatibility_diagnostic",
                "v4_2_coordination_sequencing_compatibility_diagnostic",
                "v4_2_governance_routing_compatibility_diagnostic",
                "v4_2_coordination_drift_compatibility_diagnostic",
            ),
            (
                "v4_2_coordination_manifest_primary",
                "v4_2_coordination_dependency_graph_primary",
                "v4_2_coordination_lineage_chain_primary",
                "v4_2_coordination_sequencing_primary",
                "v4_2_governance_routing_primary",
                "v4_2_coordination_drift_certification_primary",
            ),
            ("cross_layer_compatibility_visible",),
            "Source compatibility diagnostics remain deterministic evidence.",
            70,
        ),
    )
    records: list[CrossLayerCoordinationDiagnosticRecord] = []
    for record_id, state, severity, layers, diagnostic_ids, layer_refs, evidence_refs, reason, order in specs:
        records.append(
            CrossLayerCoordinationDiagnosticRecord(
                diagnostic_record_id=record_id,
                aggregation_state=state,
                severity=severity,
                source_layers=layers,
                source_diagnostic_ids=diagnostic_ids,
                layer_references=layer_refs,
                evidence_references=evidence_refs,
                explanation_reference=f"{record_id}_explanation",
                reason=reason,
                deterministic_order=order,
                fail_visible=state in FAIL_VISIBLE_DIAGNOSTIC_AGGREGATION_STATES,
                unsupported_visible=state == DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
                prohibited_visible=state == DIAGNOSTIC_AGGREGATION_PROHIBITED,
                blocked_visible=state == DIAGNOSTIC_AGGREGATION_BLOCKED,
                stale_visible=state == DIAGNOSTIC_AGGREGATION_STALE,
                missing_visible=state == DIAGNOSTIC_AGGREGATION_MISSING,
                conflicting_visible=state == DIAGNOSTIC_AGGREGATION_CONFLICTING,
            )
        )
    return tuple(records)


def default_state_aggregation_visibility(
    aggregation_state: str,
    aggregation_id: str,
    deterministic_order: int,
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...] | None = None,
) -> StateAggregationVisibility:
    diagnostic_records = records or default_cross_layer_coordination_diagnostic_records()
    matching = tuple(record for record in diagnostic_records if record.aggregation_state == aggregation_state)
    return StateAggregationVisibility(
        aggregation_id=aggregation_id,
        aggregation_state=aggregation_state,
        diagnostic_record_ids=tuple(record.diagnostic_record_id for record in matching),
        source_layers=tuple(layer for record in matching for layer in record.source_layers),
        reason_visibility=tuple(record.reason for record in matching),
        deterministic_order=deterministic_order,
    )


def default_diagnostic_severity_visibility(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...] | None = None,
) -> tuple[DiagnosticSeverityVisibility, ...]:
    diagnostic_records = records or default_cross_layer_coordination_diagnostic_records()
    return tuple(
        DiagnosticSeverityVisibility(
            severity_visibility_id=f"v4_2_coordination_diagnostics_severity_{severity}",
            severity=severity,
            diagnostic_record_ids=tuple(
                record.diagnostic_record_id for record in diagnostic_records if record.severity == severity
            ),
            deterministic_order=index * 10,
        )
        for index, severity in enumerate(DIAGNOSTIC_SEVERITIES, start=1)
    )


def default_coordination_explanation_records(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...] | None = None,
) -> tuple[CoordinationExplanationRecord, ...]:
    diagnostic_records = records or default_cross_layer_coordination_diagnostic_records()
    return tuple(
        CoordinationExplanationRecord(
            explanation_id=record.explanation_reference,
            diagnostic_record_id=record.diagnostic_record_id,
            aggregation_state=record.aggregation_state,
            severity=record.severity,
            explanation_summary=record.reason,
            evidence_references=record.evidence_references,
            deterministic_order=record.deterministic_order,
            fail_visible=record.fail_visible,
        )
        for record in diagnostic_records
    )


def default_fail_visible_explanation_summary(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...] | None = None,
    explanations: tuple[CoordinationExplanationRecord, ...] | None = None,
) -> FailVisibleExplanationSummary:
    diagnostic_records = records or default_cross_layer_coordination_diagnostic_records()
    explanation_records = explanations or default_coordination_explanation_records(diagnostic_records)
    fail_visible_records = tuple(record for record in diagnostic_records if record.fail_visible)
    explanation_by_record = {record.diagnostic_record_id: record for record in explanation_records}
    counts = tuple(
        f"{state}={sum(1 for record in fail_visible_records if record.aggregation_state == state)}"
        for state in FAIL_VISIBLE_DIAGNOSTIC_AGGREGATION_STATES
    )
    return FailVisibleExplanationSummary(
        summary_id="v4_2_coordination_fail_visible_explanation_summary_primary",
        explanation_ids=tuple(explanation_by_record[record.diagnostic_record_id].explanation_id for record in fail_visible_records),
        diagnostic_record_ids=tuple(record.diagnostic_record_id for record in fail_visible_records),
        aggregation_state_counts=counts,
        summary_lines=tuple(record.reason for record in fail_visible_records),
        deterministic_order=10,
    )


def default_coordination_diagnostics_governance(
    identity: CoordinationDiagnosticsIdentity | None = None,
) -> CoordinationDiagnosticsGovernance:
    source = identity or default_coordination_diagnostics_identity()
    return CoordinationDiagnosticsGovernance(
        governance_id=source.governance_reference,
        governance_references=(
            "v4_2_coordination_manifest_governance_primary",
            "v4_2_coordination_dependency_graph_governance_boundary",
            "v4_2_coordination_lineage_chain_governance_boundary",
            "v4_2_coordination_sequencing_governance_boundary",
            "v4_2_governance_routing_boundary",
            "v4_2_coordination_drift_certification_boundary",
            "v4_2_coordination_diagnostics_explainability_boundary",
        ),
        explicit_limitations=EXPLICIT_COORDINATION_DIAGNOSTICS_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_COORDINATION_DIAGNOSTICS_PROHIBITIONS,
        deterministic_order=10,
    )


def default_coordination_diagnostics_explainability(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    drift: CoordinationDriftCertification | None = None,
) -> CoordinationDiagnosticsExplainability:
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
    source_drift = drift or default_coordination_drift_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    identity = default_coordination_diagnostics_identity(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
        source_drift,
    )
    records = default_cross_layer_coordination_diagnostic_records()
    explanations = default_coordination_explanation_records(records)
    return CoordinationDiagnosticsExplainability(
        identity=identity,
        manifest_diagnostic_references=default_manifest_diagnostic_references(identity, source_manifest),
        dependency_graph_diagnostic_references=default_dependency_graph_diagnostic_references(identity, source_graph),
        lineage_diagnostic_references=default_lineage_diagnostic_references(identity, source_lineage),
        sequencing_diagnostic_references=default_sequencing_diagnostic_references(identity, source_sequencing),
        routing_diagnostic_references=default_routing_diagnostic_references(identity, source_routing),
        drift_diagnostic_references=default_drift_diagnostic_references(identity, source_drift),
        diagnostic_records=records,
        unsupported_state_aggregation=default_state_aggregation_visibility(
            DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
            "v4_2_coordination_diagnostics_unsupported_aggregation_primary",
            10,
            records,
        ),
        prohibited_state_aggregation=default_state_aggregation_visibility(
            DIAGNOSTIC_AGGREGATION_PROHIBITED,
            "v4_2_coordination_diagnostics_prohibited_aggregation_primary",
            20,
            records,
        ),
        blocked_state_aggregation=default_state_aggregation_visibility(
            DIAGNOSTIC_AGGREGATION_BLOCKED,
            "v4_2_coordination_diagnostics_blocked_aggregation_primary",
            30,
            records,
        ),
        stale_state_aggregation=default_state_aggregation_visibility(
            DIAGNOSTIC_AGGREGATION_STALE,
            "v4_2_coordination_diagnostics_stale_aggregation_primary",
            40,
            records,
        ),
        missing_state_aggregation=default_state_aggregation_visibility(
            DIAGNOSTIC_AGGREGATION_MISSING,
            "v4_2_coordination_diagnostics_missing_aggregation_primary",
            50,
            records,
        ),
        conflicting_state_aggregation=default_state_aggregation_visibility(
            DIAGNOSTIC_AGGREGATION_CONFLICTING,
            "v4_2_coordination_diagnostics_conflicting_aggregation_primary",
            60,
            records,
        ),
        severity_visibility=default_diagnostic_severity_visibility(records),
        explanation_records=explanations,
        fail_visible_explanation_summary=default_fail_visible_explanation_summary(records, explanations),
        governance_visibility=default_coordination_diagnostics_governance(identity),
        compatibility_manifest_reference=source_manifest.identity.manifest_id,
        compatibility_dependency_graph_reference=source_graph.identity.graph_id,
        compatibility_lineage_chain_reference=source_lineage.identity.chain_id,
        compatibility_sequencing_reference=source_sequencing.identity.sequencing_id,
        compatibility_routing_reference=source_routing.identity.routing_id,
        compatibility_drift_reference=source_drift.identity.drift_certification_id,
    )
