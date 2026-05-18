"""Deterministic v4.4 boundary explainability aggregation models.

The v4.4 Phase 6 layer aggregates Phase 1 through Phase 5 boundary
governance evidence into descriptive explainability and diagnostic visibility.
It makes source references, coverage, diagnostics, uncertainty, provenance,
lineage, replay, rollback, and explanation traces inspectable without making
recommendations, decisions, approvals, readiness claims, or runtime changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_PHASE_ID = (
    "v4_4_boundary_explainability_aggregation"
)
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_SCHEMA_VERSION = (
    "v4_4.boundary_explainability_aggregation.1"
)
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_REPORT_SCHEMA_VERSION = (
    "v4_4.boundary_explainability_aggregation_report.1"
)
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_STATUS_STABLE = (
    "v4_4_boundary_explainability_aggregation_stable"
)
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_STATUS_BLOCKED = (
    "v4_4_boundary_explainability_aggregation_blocked"
)
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_PURPOSE = (
    "deterministic_governance_safe_boundary_explainability_diagnostic_aggregation_descriptive_only"
)
V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_CLASSIFICATION = (
    "governance_safe_descriptive_boundary_explainability_diagnostic_aggregation"
)

EXPLAINABILITY_STATE_EXPLAINED = "explained"
EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED = "partially_explained"
EXPLAINABILITY_STATE_UNEXPLAINED = "unexplained"
EXPLAINABILITY_STATE_DIAGNOSTIC = "diagnostic"
EXPLAINABILITY_STATE_INFORMATIONAL = "informational"
EXPLAINABILITY_STATE_WARNING = "warning"
EXPLAINABILITY_STATE_BLOCKED = "blocked"
EXPLAINABILITY_STATE_UNSUPPORTED = "unsupported"
EXPLAINABILITY_STATE_PROHIBITED = "prohibited"
EXPLAINABILITY_STATE_STALE = "stale"
EXPLAINABILITY_STATE_CONFLICTING = "conflicting"
EXPLAINABILITY_STATE_AMBIGUOUS = "ambiguous"
EXPLAINABILITY_STATE_DEGRADED = "degraded"
EXPLAINABILITY_STATE_CONSISTENT = "consistent"
EXPLAINABILITY_STATE_INCONSISTENT = "inconsistent"
BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES: tuple[str, ...] = (
    EXPLAINABILITY_STATE_EXPLAINED,
    EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED,
    EXPLAINABILITY_STATE_UNEXPLAINED,
    EXPLAINABILITY_STATE_DIAGNOSTIC,
    EXPLAINABILITY_STATE_INFORMATIONAL,
    EXPLAINABILITY_STATE_WARNING,
    EXPLAINABILITY_STATE_BLOCKED,
    EXPLAINABILITY_STATE_UNSUPPORTED,
    EXPLAINABILITY_STATE_PROHIBITED,
    EXPLAINABILITY_STATE_STALE,
    EXPLAINABILITY_STATE_CONFLICTING,
    EXPLAINABILITY_STATE_AMBIGUOUS,
    EXPLAINABILITY_STATE_DEGRADED,
    EXPLAINABILITY_STATE_CONSISTENT,
    EXPLAINABILITY_STATE_INCONSISTENT,
)
FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES: tuple[str, ...] = (
    EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED,
    EXPLAINABILITY_STATE_UNEXPLAINED,
    EXPLAINABILITY_STATE_WARNING,
    EXPLAINABILITY_STATE_BLOCKED,
    EXPLAINABILITY_STATE_UNSUPPORTED,
    EXPLAINABILITY_STATE_PROHIBITED,
    EXPLAINABILITY_STATE_STALE,
    EXPLAINABILITY_STATE_CONFLICTING,
    EXPLAINABILITY_STATE_AMBIGUOUS,
    EXPLAINABILITY_STATE_DEGRADED,
    EXPLAINABILITY_STATE_INCONSISTENT,
)

DIAGNOSTIC_SOURCE_FOUNDATIONS = "boundary_foundations"
DIAGNOSTIC_SOURCE_INHERITANCE_REFINEMENT = "inheritance_refinement"
DIAGNOSTIC_SOURCE_CONFLICT_DRIFT = "conflict_drift"
DIAGNOSTIC_SOURCE_CROSS_BOUNDARY_CONSISTENCY = "cross_boundary_consistency"
DIAGNOSTIC_SOURCE_SEGMENTATION_SCOPE = "segmentation_scope"
DIAGNOSTIC_SOURCE_TYPES: tuple[str, ...] = (
    DIAGNOSTIC_SOURCE_FOUNDATIONS,
    DIAGNOSTIC_SOURCE_INHERITANCE_REFINEMENT,
    DIAGNOSTIC_SOURCE_CONFLICT_DRIFT,
    DIAGNOSTIC_SOURCE_CROSS_BOUNDARY_CONSISTENCY,
    DIAGNOSTIC_SOURCE_SEGMENTATION_SCOPE,
)

V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_scheduling_execution_count",
    "enabled_recommendation_count",
    "enabled_decision_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "explainability_ordering_stability",
    "diagnostic_ordering_stability",
    "explainability_serialization_stability",
    "diagnostic_serialization_stability",
    "explainability_hashing_stability",
    "diagnostic_hashing_stability",
    "source_evidence_reference_stability",
    "explainability_coverage_visibility",
    "diagnostic_visibility_preservation",
    "unresolved_diagnostic_preservation",
    "replay_safe_aggregation_evidence",
    "rollback_safe_aggregation_evidence",
    "provenance_visibility",
    "lineage_visibility",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 6 aggregates boundary explainability and diagnostics only.",
    "v4.4 Phase 6 explanations do not become recommendations.",
    "v4.4 Phase 6 diagnostic summaries do not trigger action.",
    "v4.4 Phase 6 aggregation does not imply operational readiness.",
    "v4.4 Phase 6 does not execute orchestration.",
    "v4.4 Phase 6 does not authorize or approve orchestration.",
    "v4.4 Phase 6 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 6 does not recommend, rank, score, select, optimize, or decide orchestration.",
    "v4.4 Phase 6 does not integrate planners or consume production bundles.",
    "v4.4 Phase 6 does not repair, remediate, auto-resolve diagnostics, or mutate runtime or operational state.",
)

V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No explainability system grants runtime authority.",
    "No diagnostic aggregation authorizes orchestration behavior.",
    "No explanation result is a recommendation, decision, approval, or readiness signal.",
    "No orchestration execution exists.",
    "No orchestration authorization exists.",
    "No orchestration approval exists.",
    "No orchestration dispatch exists.",
    "No orchestration routing exists.",
    "No orchestration traversal exists.",
    "No orchestration scheduling exists.",
    "No orchestration sequencing exists.",
    "No orchestration recommendation exists.",
    "No orchestration ranking, scoring, selection, or optimization exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No automatic remediation exists.",
    "No automatic repair exists.",
    "No diagnostic auto-resolution exists.",
    "No explainability-based recommendations exist.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BoundaryExplainabilityAggregationIdentity:
    aggregation_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_evidence_reference: str
    explainability_reference: str
    diagnostics_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_rollback_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_PURPOSE
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    governance_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DiagnosticAggregationIdentity:
    diagnostic_aggregation_id: str
    phase_id: str
    source_count: int
    diagnostic_count: int
    coverage_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    non_operational: bool = True
    diagnostic_auto_resolution_enabled: bool = False
    authorization_enabled: bool = False


@dataclass(frozen=True)
class SourceEvidenceReference:
    source_id: str
    source_phase_id: str
    source_type: str
    source_report_reference: str
    source_hash_reference: str
    coverage_state: str
    diagnostic_state: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    source_available: bool = True
    descriptive_only: bool = True
    non_authoritative: bool = True
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class PhaseEvidenceSummary:
    summary_id: str
    source_id: str
    phase_label: str
    coverage_state: str
    diagnostic_state: str
    explained_reference_ids: tuple[str, ...]
    unresolved_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True

    def __post_init__(self) -> None:
        _set_tuple_field(self, "explained_reference_ids")
        _set_tuple_field(self, "unresolved_reference_ids")


@dataclass(frozen=True)
class ExplainabilityAggregationRecord:
    explanation_id: str
    source_id: str
    coverage_state: str
    explanation_summary: str
    explanation_trace_ids: tuple[str, ...]
    diagnostic_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    runtime_readiness_inferred: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "explanation_trace_ids")
        _set_tuple_field(self, "diagnostic_reference_ids")


@dataclass(frozen=True)
class DiagnosticAggregationRecord:
    diagnostic_id: str
    source_id: str
    diagnostic_state: str
    severity: str
    diagnostic_source_type: str
    diagnostic_summary: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    unresolved: bool
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    diagnostic_auto_resolution_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExplanationCoverageSummary:
    coverage_id: str
    source_id: str
    coverage_state: str
    explained_count: int
    partially_explained_count: int
    unexplained_count: int
    diagnostic_count: int
    deterministic_order: int
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False


@dataclass(frozen=True)
class ExplanationTraceRecord:
    trace_id: str
    source_id: str
    explanation_id: str
    trace_state: str
    trace_reference_ids: tuple[str, ...]
    trace_summary: str
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    runtime_readiness_inferred: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "trace_reference_ids")


@dataclass(frozen=True)
class ProvenanceAggregationSummary:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    diagnostic_reference_ids: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_visible: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_reference_ids", "source_hash_references", "diagnostic_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageAggregationSummary:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    explanation_reference_ids: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_visible: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_reference_ids", "lineage_hash_references", "explanation_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackAggregationSummary:
    evidence_id: str
    source_evidence_ids: tuple[str, ...]
    explanation_record_ids: tuple[str, ...]
    diagnostic_record_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_evidence_ids",
            "explanation_record_ids",
            "diagnostic_record_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BoundaryExplainabilityAggregationIntelligence:
    identity: BoundaryExplainabilityAggregationIdentity
    diagnostic_identity: DiagnosticAggregationIdentity
    source_evidence_references: tuple[SourceEvidenceReference, ...]
    phase_evidence_summaries: tuple[PhaseEvidenceSummary, ...]
    explainability_records: tuple[ExplainabilityAggregationRecord, ...]
    diagnostic_records: tuple[DiagnosticAggregationRecord, ...]
    coverage_summaries: tuple[ExplanationCoverageSummary, ...]
    explanation_traces: tuple[ExplanationTraceRecord, ...]
    provenance_summary: ProvenanceAggregationSummary
    lineage_summary: LineageAggregationSummary
    replay_rollback_summary: ReplayRollbackAggregationSummary
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    non_recommending: bool = True
    non_deciding: bool = True
    non_remediating: bool = True
    non_mutating: bool = True
    runtime_readiness_inference_disabled: bool = True
    runtime_execution_enabled: bool = False
    orchestration_runtime_behavior_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    diagnostic_auto_resolution_enabled: bool = False
    explainability_based_recommendation_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_evidence_references",
            "phase_evidence_summaries",
            "explainability_records",
            "diagnostic_records",
            "coverage_summaries",
            "explanation_traces",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_boundary_explainability_aggregation_identity() -> BoundaryExplainabilityAggregationIdentity:
    return BoundaryExplainabilityAggregationIdentity(
        aggregation_id="v4_4_boundary_explainability_diagnostic_aggregation",
        phase_id=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_PHASE_ID,
        schema_version=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_GENERATED_AT,
        classification=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_CLASSIFICATION,
        source_evidence_reference="v4_4_phase_1_through_5_source_evidence_references",
        explainability_reference="v4_4_boundary_explainability_aggregation_records",
        diagnostics_reference="v4_4_boundary_diagnostic_aggregation_records",
        provenance_reference="v4_4_boundary_explainability_provenance_visibility",
        lineage_reference="v4_4_boundary_explainability_lineage_visibility",
        replay_rollback_reference="v4_4_boundary_explainability_replay_rollback_evidence",
        non_operational_reference="v4_4_boundary_explainability_non_operational_certification",
    )


def default_source_evidence_references() -> tuple[SourceEvidenceReference, ...]:
    definitions = (
        ("source_boundary_foundations", "v4_4_boundary_intelligence_foundations", DIAGNOSTIC_SOURCE_FOUNDATIONS, EXPLAINABILITY_STATE_EXPLAINED, EXPLAINABILITY_STATE_INFORMATIONAL),
        ("source_inheritance_refinement", "v4_4_boundary_inheritance_refinement", DIAGNOSTIC_SOURCE_INHERITANCE_REFINEMENT, EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED, EXPLAINABILITY_STATE_WARNING),
        ("source_conflict_drift", "v4_4_boundary_conflict_drift", DIAGNOSTIC_SOURCE_CONFLICT_DRIFT, EXPLAINABILITY_STATE_DIAGNOSTIC, EXPLAINABILITY_STATE_CONFLICTING),
        ("source_cross_boundary_consistency", "v4_4_cross_boundary_consistency", DIAGNOSTIC_SOURCE_CROSS_BOUNDARY_CONSISTENCY, EXPLAINABILITY_STATE_CONSISTENT, EXPLAINABILITY_STATE_INCONSISTENT),
        ("source_segmentation_scope", "v4_4_boundary_segmentation_scope", DIAGNOSTIC_SOURCE_SEGMENTATION_SCOPE, EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED, EXPLAINABILITY_STATE_AMBIGUOUS),
    )
    return tuple(
        SourceEvidenceReference(
            source_id=source_id,
            source_phase_id=phase_id,
            source_type=source_type,
            source_report_reference=f"docs/generated/{phase_id}_report.json",
            source_hash_reference=f"{phase_id}.deterministic_report_hash",
            coverage_state=coverage_state,
            diagnostic_state=diagnostic_state,
            evidence_reference_ids=(phase_id, source_id, source_type),
            deterministic_order=index,
        )
        for index, (source_id, phase_id, source_type, coverage_state, diagnostic_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_phase_evidence_summaries() -> tuple[PhaseEvidenceSummary, ...]:
    return tuple(
        PhaseEvidenceSummary(
            summary_id=f"summary_{source.source_id}",
            source_id=source.source_id,
            phase_label=source.source_phase_id,
            coverage_state=source.coverage_state,
            diagnostic_state=source.diagnostic_state,
            explained_reference_ids=(source.source_report_reference, source.source_hash_reference),
            unresolved_reference_ids=(
                f"{source.source_phase_id}.fail_visible_diagnostics",
                f"{source.source_phase_id}.unresolved_visibility",
            ),
            deterministic_order=source.deterministic_order,
            fail_visible=(
                source.coverage_state in FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES
                or source.diagnostic_state in FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES
            ),
        )
        for source in default_source_evidence_references()
    )


def default_explainability_records() -> tuple[ExplainabilityAggregationRecord, ...]:
    definitions = (
        ("explain_boundary_foundations", "source_boundary_foundations", EXPLAINABILITY_STATE_EXPLAINED),
        ("explain_inheritance_refinement", "source_inheritance_refinement", EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED),
        ("explain_conflict_drift", "source_conflict_drift", EXPLAINABILITY_STATE_DIAGNOSTIC),
        ("explain_cross_boundary_consistency", "source_cross_boundary_consistency", EXPLAINABILITY_STATE_EXPLAINED),
        ("explain_segmentation_scope_gap", "source_segmentation_scope", EXPLAINABILITY_STATE_UNEXPLAINED),
    )
    return tuple(
        ExplainabilityAggregationRecord(
            explanation_id=explanation_id,
            source_id=source_id,
            coverage_state=coverage_state,
            explanation_summary=f"{coverage_state} source evidence remains visible without recommendation or decision behavior",
            explanation_trace_ids=(f"trace_{explanation_id}", source_id),
            diagnostic_reference_ids=(f"diagnostic_{source_id}",),
            deterministic_order=index,
            fail_visible=coverage_state in FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES,
        )
        for index, (explanation_id, source_id, coverage_state) in enumerate(definitions, start=1)
    )


def default_diagnostic_records() -> tuple[DiagnosticAggregationRecord, ...]:
    definitions = (
        ("diagnostic_foundation_visibility", "source_boundary_foundations", EXPLAINABILITY_STATE_DIAGNOSTIC, "informational", DIAGNOSTIC_SOURCE_FOUNDATIONS, False),
        ("diagnostic_foundation_informational", "source_boundary_foundations", EXPLAINABILITY_STATE_INFORMATIONAL, "informational", DIAGNOSTIC_SOURCE_FOUNDATIONS, False),
        ("diagnostic_inheritance_warning", "source_inheritance_refinement", EXPLAINABILITY_STATE_WARNING, "warning", DIAGNOSTIC_SOURCE_INHERITANCE_REFINEMENT, True),
        ("diagnostic_lineage_blocked", "source_inheritance_refinement", EXPLAINABILITY_STATE_BLOCKED, "blocked", DIAGNOSTIC_SOURCE_INHERITANCE_REFINEMENT, True),
        ("diagnostic_unsupported_boundary", "source_conflict_drift", EXPLAINABILITY_STATE_UNSUPPORTED, "warning", DIAGNOSTIC_SOURCE_CONFLICT_DRIFT, True),
        ("diagnostic_prohibited_authority", "source_conflict_drift", EXPLAINABILITY_STATE_PROHIBITED, "prohibited", DIAGNOSTIC_SOURCE_CONFLICT_DRIFT, True),
        ("diagnostic_stale_scope", "source_segmentation_scope", EXPLAINABILITY_STATE_STALE, "warning", DIAGNOSTIC_SOURCE_SEGMENTATION_SCOPE, True),
        ("diagnostic_conflicting_scope", "source_cross_boundary_consistency", EXPLAINABILITY_STATE_CONFLICTING, "warning", DIAGNOSTIC_SOURCE_CROSS_BOUNDARY_CONSISTENCY, True),
        ("diagnostic_ambiguous_provider", "source_segmentation_scope", EXPLAINABILITY_STATE_AMBIGUOUS, "warning", DIAGNOSTIC_SOURCE_SEGMENTATION_SCOPE, True),
        ("diagnostic_degraded_lineage", "source_segmentation_scope", EXPLAINABILITY_STATE_DEGRADED, "warning", DIAGNOSTIC_SOURCE_SEGMENTATION_SCOPE, True),
        ("diagnostic_inconsistent_consistency", "source_cross_boundary_consistency", EXPLAINABILITY_STATE_INCONSISTENT, "warning", DIAGNOSTIC_SOURCE_CROSS_BOUNDARY_CONSISTENCY, True),
    )
    return tuple(
        DiagnosticAggregationRecord(
            diagnostic_id=diagnostic_id,
            source_id=source_id,
            diagnostic_state=diagnostic_state,
            severity=severity,
            diagnostic_source_type=source_type,
            diagnostic_summary=f"{diagnostic_state} diagnostic remains unresolved visibility, not an action trigger",
            evidence_reference_ids=(source_id, diagnostic_id, source_type),
            deterministic_order=index,
            unresolved=unresolved,
            fail_visible=diagnostic_state in FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES,
        )
        for index, (
            diagnostic_id,
            source_id,
            diagnostic_state,
            severity,
            source_type,
            unresolved,
        ) in enumerate(definitions, start=1)
    )


def default_coverage_summaries() -> tuple[ExplanationCoverageSummary, ...]:
    records = default_explainability_records()
    return tuple(
        ExplanationCoverageSummary(
            coverage_id=f"coverage_{source.source_id}",
            source_id=source.source_id,
            coverage_state=source.coverage_state,
            explained_count=sum(
                1
                for record in records
                if record.source_id == source.source_id
                and record.coverage_state == EXPLAINABILITY_STATE_EXPLAINED
            ),
            partially_explained_count=sum(
                1
                for record in records
                if record.source_id == source.source_id
                and record.coverage_state == EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED
            ),
            unexplained_count=sum(
                1
                for record in records
                if record.source_id == source.source_id
                and record.coverage_state == EXPLAINABILITY_STATE_UNEXPLAINED
            ),
            diagnostic_count=sum(1 for record in records if record.source_id == source.source_id),
            deterministic_order=source.deterministic_order,
        )
        for source in default_source_evidence_references()
    )


def default_explanation_traces() -> tuple[ExplanationTraceRecord, ...]:
    return tuple(
        ExplanationTraceRecord(
            trace_id=f"trace_{record.explanation_id}",
            source_id=record.source_id,
            explanation_id=record.explanation_id,
            trace_state=record.coverage_state,
            trace_reference_ids=(record.source_id, record.explanation_id, *record.diagnostic_reference_ids),
            trace_summary=f"{record.coverage_state} explanation trace remains descriptive and auditable",
            deterministic_order=index,
        )
        for index, record in enumerate(default_explainability_records(), start=1)
    )


def _source_ids() -> tuple[str, ...]:
    return tuple(source.source_id for source in default_source_evidence_references())


def _explanation_ids() -> tuple[str, ...]:
    return tuple(record.explanation_id for record in default_explainability_records())


def _diagnostic_ids() -> tuple[str, ...]:
    return tuple(record.diagnostic_id for record in default_diagnostic_records())


def default_provenance_summary() -> ProvenanceAggregationSummary:
    sources = default_source_evidence_references()
    return ProvenanceAggregationSummary(
        provenance_id="v4_4_boundary_explainability_provenance_visibility",
        source_reference_ids=tuple(source.source_report_reference for source in sources),
        source_hash_references=tuple(source.source_hash_reference for source in sources),
        diagnostic_reference_ids=_diagnostic_ids(),
        provenance_state="explainability_provenance_visible",
        deterministic_order=1,
    )


def default_lineage_summary() -> LineageAggregationSummary:
    return LineageAggregationSummary(
        lineage_id="v4_4_boundary_explainability_lineage_visibility",
        lineage_reference_ids=(
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            "v4_4_boundary_conflict_drift",
            "v4_4_cross_boundary_consistency",
            "v4_4_boundary_segmentation_scope",
            V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_PHASE_ID,
        ),
        lineage_hash_references=(
            "v4_4_boundary_intelligence_hash_reference",
            "v4_4_boundary_inheritance_hash_reference",
            "v4_4_boundary_conflict_drift_hash_reference",
            "v4_4_cross_boundary_consistency_hash_reference",
            "v4_4_boundary_segmentation_scope_hash_reference",
        ),
        explanation_reference_ids=_explanation_ids(),
        lineage_state="explainability_lineage_visible",
        deterministic_order=1,
    )


def default_replay_rollback_summary() -> ReplayRollbackAggregationSummary:
    all_ids = _source_ids() + _explanation_ids() + _diagnostic_ids()
    return ReplayRollbackAggregationSummary(
        evidence_id="v4_4_boundary_explainability_replay_rollback_evidence",
        source_evidence_ids=_source_ids(),
        explanation_record_ids=_explanation_ids(),
        diagnostic_record_ids=_diagnostic_ids(),
        replay_evidence_ids=all_ids,
        rollback_evidence_ids=all_ids,
        deterministic_order=1,
    )


def default_diagnostic_aggregation_identity() -> DiagnosticAggregationIdentity:
    return DiagnosticAggregationIdentity(
        diagnostic_aggregation_id="v4_4_boundary_diagnostic_aggregation",
        phase_id=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_PHASE_ID,
        source_count=len(default_source_evidence_references()),
        diagnostic_count=len(default_diagnostic_records()),
        coverage_reference="v4_4_boundary_explainability_coverage_summary",
        deterministic_order=1,
    )


def default_boundary_explainability_aggregation_intelligence() -> BoundaryExplainabilityAggregationIntelligence:
    return BoundaryExplainabilityAggregationIntelligence(
        identity=default_boundary_explainability_aggregation_identity(),
        diagnostic_identity=default_diagnostic_aggregation_identity(),
        source_evidence_references=default_source_evidence_references(),
        phase_evidence_summaries=default_phase_evidence_summaries(),
        explainability_records=default_explainability_records(),
        diagnostic_records=default_diagnostic_records(),
        coverage_summaries=default_coverage_summaries(),
        explanation_traces=default_explanation_traces(),
        provenance_summary=default_provenance_summary(),
        lineage_summary=default_lineage_summary(),
        replay_rollback_summary=default_replay_rollback_summary(),
        deterministic_guarantees=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_EXPLICIT_PROHIBITIONS,
    )
