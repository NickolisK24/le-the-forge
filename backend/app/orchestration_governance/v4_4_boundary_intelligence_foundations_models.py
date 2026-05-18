"""Deterministic v4.4 boundary intelligence foundation models.

The v4.4 Phase 1 layer is descriptive governance evidence only. It models
orchestration boundary intelligence visibility without authorizing, approving,
executing, dispatching, routing, traversing, scheduling, sequencing, deciding,
recommending, integrating planners, consuming production bundles, or mutating
runtime or operational state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_INTELLIGENCE_PHASE_ID = "v4_4_boundary_intelligence_foundations"
V4_4_BOUNDARY_INTELLIGENCE_SCHEMA_VERSION = "v4_4.boundary_intelligence_foundations.1"
V4_4_BOUNDARY_INTELLIGENCE_REPORT_SCHEMA_VERSION = (
    "v4_4.boundary_intelligence_foundations_report.1"
)
V4_4_BOUNDARY_INTELLIGENCE_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_INTELLIGENCE_STATUS_STABLE = "v4_4_boundary_intelligence_foundations_stable"
V4_4_BOUNDARY_INTELLIGENCE_STATUS_BLOCKED = "v4_4_boundary_intelligence_foundations_blocked"
V4_4_BOUNDARY_INTELLIGENCE_PURPOSE = (
    "deterministic_governance_safe_orchestration_boundary_intelligence_refinement_descriptive_only"
)
V4_4_BOUNDARY_INTELLIGENCE_CLASSIFICATION = (
    "governance_safe_descriptive_orchestration_boundary_intelligence_foundation"
)

BOUNDARY_STATE_SUPPORTED = "supported"
BOUNDARY_STATE_UNSUPPORTED = "unsupported"
BOUNDARY_STATE_PROHIBITED = "prohibited"
BOUNDARY_STATE_BLOCKED = "blocked"
BOUNDARY_STATE_STALE = "stale"
BOUNDARY_STATE_CONFLICTING = "conflicting"
BOUNDARY_INTELLIGENCE_STATES: tuple[str, ...] = (
    BOUNDARY_STATE_SUPPORTED,
    BOUNDARY_STATE_UNSUPPORTED,
    BOUNDARY_STATE_PROHIBITED,
    BOUNDARY_STATE_BLOCKED,
    BOUNDARY_STATE_STALE,
    BOUNDARY_STATE_CONFLICTING,
)
FAIL_VISIBLE_BOUNDARY_STATES: tuple[str, ...] = (
    BOUNDARY_STATE_UNSUPPORTED,
    BOUNDARY_STATE_PROHIBITED,
    BOUNDARY_STATE_BLOCKED,
    BOUNDARY_STATE_STALE,
    BOUNDARY_STATE_CONFLICTING,
)

BOUNDARY_CLASSIFICATION_GOVERNANCE_SCOPE = "governance_scope_visibility"
BOUNDARY_CLASSIFICATION_SEGMENTATION = "deterministic_boundary_segmentation_visibility"
BOUNDARY_CLASSIFICATION_DIAGNOSTICS = "boundary_diagnostics_visibility"
BOUNDARY_CLASSIFICATION_EXPLAINABILITY = "boundary_explainability_visibility"
BOUNDARY_CLASSIFICATION_INTEGRITY = "boundary_integrity_visibility"
BOUNDARY_CLASSIFICATION_PROHIBITED_STATE = "fail_visible_prohibited_state_visibility"
BOUNDARY_CLASSIFICATION_UNSUPPORTED_STATE = "fail_visible_unsupported_state_visibility"
BOUNDARY_CLASSIFICATION_PROVENANCE = "provenance_continuity_visibility"
BOUNDARY_CLASSIFICATION_LINEAGE = "lineage_continuity_visibility"
BOUNDARY_INTELLIGENCE_CLASSIFICATION_TYPES: tuple[str, ...] = (
    BOUNDARY_CLASSIFICATION_GOVERNANCE_SCOPE,
    BOUNDARY_CLASSIFICATION_SEGMENTATION,
    BOUNDARY_CLASSIFICATION_DIAGNOSTICS,
    BOUNDARY_CLASSIFICATION_EXPLAINABILITY,
    BOUNDARY_CLASSIFICATION_INTEGRITY,
    BOUNDARY_CLASSIFICATION_PROHIBITED_STATE,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED_STATE,
    BOUNDARY_CLASSIFICATION_PROVENANCE,
    BOUNDARY_CLASSIFICATION_LINEAGE,
)

V4_4_BOUNDARY_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_ordering_stability",
    "deterministic_serialization_stability",
    "deterministic_hashing_stability",
    "deterministic_replay_stability",
    "deterministic_rollback_stability",
    "deterministic_explainability_visibility",
    "deterministic_diagnostics_visibility",
    "deterministic_provenance_continuity",
    "deterministic_lineage_continuity",
    "deterministic_integrity_safe_evidence",
    "governance_safe_descriptive_only_enforcement",
    "fail_visible_unsupported_state_preservation",
    "fail_visible_prohibited_state_preservation",
    "non_operational_certification",
)

V4_4_BOUNDARY_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 1 models governance-safe boundary intelligence foundations only.",
    "v4.4 Phase 1 is descriptive-only and non-operational.",
    "v4.4 Phase 1 does not execute orchestration.",
    "v4.4 Phase 1 does not authorize or approve orchestration.",
    "v4.4 Phase 1 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 1 does not recommend, decide, rank, score, select, or optimize orchestration.",
    "v4.4 Phase 1 does not integrate planners or consume production bundles.",
    "v4.4 Phase 1 does not infer hidden operational semantics.",
    "v4.4 Phase 1 does not mutate runtime state or operational state.",
)

V4_4_BOUNDARY_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration execution behavior exists.",
    "No runtime orchestration behavior exists.",
    "No orchestration authorization exists.",
    "No orchestration approval exists.",
    "No orchestration dispatch exists.",
    "No orchestration routing exists.",
    "No orchestration traversal exists.",
    "No orchestration scheduling exists.",
    "No orchestration sequencing exists.",
    "No orchestration recommendation exists.",
    "No orchestration decision exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No automatic remediation or repair exists.",
    "No hidden inference exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BoundaryIntelligenceIdentity:
    boundary_intelligence_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    governance_reference: str
    boundary_scope_reference: str
    diagnostics_reference: str
    explainability_reference: str
    provenance_reference: str
    lineage_reference: str
    integrity_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_INTELLIGENCE_PURPOSE
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
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class BoundaryIntelligenceClassification:
    classification_id: str
    boundary_id: str
    classification_type: str
    visibility_state: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    operational_authority: bool = False
    runtime_capability: bool = False
    orchestration_activation_authority: bool = False
    recommendation_authority: bool = False
    decision_authority: bool = False


@dataclass(frozen=True)
class BoundaryIntelligenceRecord:
    boundary_id: str
    boundary_name: str
    classification_id: str
    visibility_state: str
    scope_id: str
    segment_id: str
    diagnostic_id: str
    explainability_id: str
    integrity_id: str
    provenance_reference_id: str
    lineage_reference_id: str
    deterministic_order: int
    fail_visible: bool
    governance_safe: bool = True
    descriptive_only: bool = True
    unknown_state_inferred: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False


@dataclass(frozen=True)
class BoundaryScopeVisibility:
    scope_id: str
    boundary_id: str
    scope_name: str
    visibility_state: str
    visible_scope_reason: str
    deterministic_order: int
    governance_safe: bool = True
    descriptive_only: bool = True
    operational_authority: bool = False


@dataclass(frozen=True)
class BoundarySegmentationVisibility:
    segment_id: str
    boundary_id: str
    segment_name: str
    segment_state: str
    segment_reason: str
    deterministic_order: int
    segmentation_executable: bool = False
    traversal_enabled: bool = False
    routing_enabled: bool = False
    descriptive_only: bool = True


@dataclass(frozen=True)
class BoundaryDiagnosticRecord:
    diagnostic_id: str
    boundary_id: str
    diagnostic_type: str
    visibility_state: str
    severity: str
    message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    auto_remediation_enabled: bool = False
    repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class BoundaryExplainabilityRecord:
    explainability_id: str
    boundary_id: str
    explanation_type: str
    visibility_state: str
    explanation: str
    visible_reason_ids: tuple[str, ...]
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "visible_reason_ids")


@dataclass(frozen=True)
class BoundaryIntegrityVisibility:
    integrity_id: str
    boundary_id: str
    visibility_state: str
    integrity_status: str
    provenance_reference_id: str
    lineage_reference_id: str
    deterministic_order: int
    integrity_safe_evidence: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    mutation_enabled: bool = False


@dataclass(frozen=True)
class BoundaryGovernanceVisibilitySummary:
    summary_id: str
    state_type: str
    boundary_ids: tuple[str, ...]
    classification_ids: tuple[str, ...]
    count: int
    deterministic_order: int
    fail_visible: bool
    governance_safe: bool = True
    descriptive_only: bool = True
    operational_authority: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "boundary_ids")
        _set_tuple_field(self, "classification_ids")


@dataclass(frozen=True)
class BoundaryFailVisibleFinding:
    finding_id: str
    boundary_id: str
    finding_type: str
    visibility_state: str
    finding_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    hidden_inference_used: bool = False
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class BoundaryContinuityMetadata:
    continuity_id: str
    source_phase_id: str
    source_report_reference: str
    source_report_hash_reference: str
    deterministic_evidence_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    continuity_guarantees: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "deterministic_evidence_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
            "continuity_guarantees",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BoundaryProvenanceMetadata:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    provenance_chain_status: str
    deterministic_order: int
    provenance_continuity_preserved: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "source_reference_ids")
        _set_tuple_field(self, "source_hash_references")


@dataclass(frozen=True)
class BoundaryLineageMetadata:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    lineage_status: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "lineage_reference_ids")
        _set_tuple_field(self, "lineage_hash_references")


@dataclass(frozen=True)
class BoundaryIntelligenceFoundations:
    identity: BoundaryIntelligenceIdentity
    classifications: tuple[BoundaryIntelligenceClassification, ...]
    boundary_records: tuple[BoundaryIntelligenceRecord, ...]
    scope_visibility: tuple[BoundaryScopeVisibility, ...]
    segmentation_visibility: tuple[BoundarySegmentationVisibility, ...]
    diagnostics: tuple[BoundaryDiagnosticRecord, ...]
    explainability: tuple[BoundaryExplainabilityRecord, ...]
    integrity_visibility: tuple[BoundaryIntegrityVisibility, ...]
    governance_visibility_summaries: tuple[BoundaryGovernanceVisibilitySummary, ...]
    fail_visible_findings: tuple[BoundaryFailVisibleFinding, ...]
    continuity_metadata: BoundaryContinuityMetadata
    provenance_metadata: BoundaryProvenanceMetadata
    lineage_metadata: BoundaryLineageMetadata
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_executing: bool = True
    non_authorizing: bool = True
    non_approving: bool = True
    non_dispatching: bool = True
    non_routing: bool = True
    non_mutating: bool = True
    runtime_execution_enabled: bool = False
    orchestration_runtime_behavior_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "classifications",
            "boundary_records",
            "scope_visibility",
            "segmentation_visibility",
            "diagnostics",
            "explainability",
            "integrity_visibility",
            "governance_visibility_summaries",
            "fail_visible_findings",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_boundary_intelligence_identity() -> BoundaryIntelligenceIdentity:
    return BoundaryIntelligenceIdentity(
        boundary_intelligence_id="v4_4_governance_safe_boundary_intelligence_foundations",
        phase_id=V4_4_BOUNDARY_INTELLIGENCE_PHASE_ID,
        schema_version=V4_4_BOUNDARY_INTELLIGENCE_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_INTELLIGENCE_GENERATED_AT,
        classification=V4_4_BOUNDARY_INTELLIGENCE_CLASSIFICATION,
        governance_reference="v4_3_closeout_and_v4_4_readiness",
        boundary_scope_reference="v4_4_boundary_scope_visibility",
        diagnostics_reference="v4_4_boundary_diagnostics_visibility",
        explainability_reference="v4_4_boundary_explainability_visibility",
        provenance_reference="v4_4_boundary_provenance_continuity",
        lineage_reference="v4_4_boundary_lineage_continuity",
        integrity_reference="v4_4_boundary_integrity_safe_evidence",
        non_operational_reference="v4_4_boundary_non_operational_certification",
    )


def default_boundary_intelligence_classifications() -> tuple[BoundaryIntelligenceClassification, ...]:
    definitions = (
        ("classification_governance_scope", "boundary_governance_scope_visibility", BOUNDARY_CLASSIFICATION_GOVERNANCE_SCOPE, BOUNDARY_STATE_SUPPORTED),
        ("classification_segmentation", "boundary_deterministic_segmentation", BOUNDARY_CLASSIFICATION_SEGMENTATION, BOUNDARY_STATE_SUPPORTED),
        ("classification_runtime_execution", "boundary_runtime_execution", BOUNDARY_CLASSIFICATION_PROHIBITED_STATE, BOUNDARY_STATE_PROHIBITED),
        ("classification_authorization_approval", "boundary_authorization_approval", BOUNDARY_CLASSIFICATION_PROHIBITED_STATE, BOUNDARY_STATE_PROHIBITED),
        ("classification_dispatch_routing", "boundary_dispatch_routing", BOUNDARY_CLASSIFICATION_PROHIBITED_STATE, BOUNDARY_STATE_PROHIBITED),
        ("classification_planner_production", "boundary_planner_production", BOUNDARY_CLASSIFICATION_PROHIBITED_STATE, BOUNDARY_STATE_PROHIBITED),
        ("classification_external_runtime_semantics", "boundary_external_runtime_semantics", BOUNDARY_CLASSIFICATION_UNSUPPORTED_STATE, BOUNDARY_STATE_UNSUPPORTED),
        ("classification_implicit_provider_identity", "boundary_implicit_provider_identity", BOUNDARY_CLASSIFICATION_UNSUPPORTED_STATE, BOUNDARY_STATE_UNSUPPORTED),
        ("classification_stale_source_evidence", "boundary_stale_source_evidence", BOUNDARY_CLASSIFICATION_PROVENANCE, BOUNDARY_STATE_STALE),
        ("classification_conflicting_scope_signal", "boundary_conflicting_scope_signal", BOUNDARY_CLASSIFICATION_GOVERNANCE_SCOPE, BOUNDARY_STATE_CONFLICTING),
        ("classification_missing_lineage_evidence", "boundary_missing_lineage_evidence", BOUNDARY_CLASSIFICATION_LINEAGE, BOUNDARY_STATE_BLOCKED),
    )
    return tuple(
        BoundaryIntelligenceClassification(
            classification_id=classification_id,
            boundary_id=boundary_id,
            classification_type=classification_type,
            visibility_state=visibility_state,
            classification_reason=(
                f"{visibility_state} boundary intelligence classification remains visible and descriptive-only"
            ),
            deterministic_order=index,
        )
        for index, (classification_id, boundary_id, classification_type, visibility_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_boundary_intelligence_records() -> tuple[BoundaryIntelligenceRecord, ...]:
    return tuple(
        BoundaryIntelligenceRecord(
            boundary_id=classification.boundary_id,
            boundary_name=classification.boundary_id.replace("boundary_", "").replace("_", " "),
            classification_id=classification.classification_id,
            visibility_state=classification.visibility_state,
            scope_id=f"scope_{classification.boundary_id}",
            segment_id=f"segment_{classification.boundary_id}",
            diagnostic_id=f"diagnostic_{classification.boundary_id}",
            explainability_id=f"explainability_{classification.boundary_id}",
            integrity_id=f"integrity_{classification.boundary_id}",
            provenance_reference_id="v4_3_closeout_and_v4_4_readiness_report",
            lineage_reference_id="v4_4_boundary_intelligence_lineage",
            deterministic_order=classification.deterministic_order,
            fail_visible=classification.visibility_state in FAIL_VISIBLE_BOUNDARY_STATES,
        )
        for classification in default_boundary_intelligence_classifications()
    )


def default_boundary_scope_visibility() -> tuple[BoundaryScopeVisibility, ...]:
    return tuple(
        BoundaryScopeVisibility(
            scope_id=record.scope_id,
            boundary_id=record.boundary_id,
            scope_name=f"{record.boundary_name} scope",
            visibility_state=record.visibility_state,
            visible_scope_reason=(
                f"{record.visibility_state} boundary scope is preserved without operational authority"
            ),
            deterministic_order=record.deterministic_order,
        )
        for record in default_boundary_intelligence_records()
    )


def default_boundary_segmentation_visibility() -> tuple[BoundarySegmentationVisibility, ...]:
    return tuple(
        BoundarySegmentationVisibility(
            segment_id=record.segment_id,
            boundary_id=record.boundary_id,
            segment_name=f"{record.boundary_name} segment",
            segment_state=record.visibility_state,
            segment_reason=(
                "Segment visibility is deterministic and does not enable traversal or routing"
            ),
            deterministic_order=record.deterministic_order,
        )
        for record in default_boundary_intelligence_records()
    )


def default_boundary_diagnostics() -> tuple[BoundaryDiagnosticRecord, ...]:
    severity_by_state = {
        BOUNDARY_STATE_SUPPORTED: "info",
        BOUNDARY_STATE_UNSUPPORTED: "warning",
        BOUNDARY_STATE_PROHIBITED: "prohibited",
        BOUNDARY_STATE_BLOCKED: "blocker",
        BOUNDARY_STATE_STALE: "warning",
        BOUNDARY_STATE_CONFLICTING: "warning",
    }
    return tuple(
        BoundaryDiagnosticRecord(
            diagnostic_id=record.diagnostic_id,
            boundary_id=record.boundary_id,
            diagnostic_type=f"{record.visibility_state}_boundary_visibility",
            visibility_state=record.visibility_state,
            severity=severity_by_state[record.visibility_state],
            message=(
                f"{record.visibility_state} boundary state remains explicit and non-operational"
            ),
            evidence_reference_ids=(record.provenance_reference_id, record.lineage_reference_id),
            deterministic_order=record.deterministic_order,
        )
        for record in default_boundary_intelligence_records()
    )


def default_boundary_explainability() -> tuple[BoundaryExplainabilityRecord, ...]:
    return tuple(
        BoundaryExplainabilityRecord(
            explainability_id=record.explainability_id,
            boundary_id=record.boundary_id,
            explanation_type=f"{record.visibility_state}_boundary_explainability",
            visibility_state=record.visibility_state,
            explanation=(
                f"{record.boundary_name} is visible for governance analysis only; no orchestration action is enabled"
            ),
            visible_reason_ids=(record.classification_id, record.diagnostic_id),
            deterministic_order=record.deterministic_order,
        )
        for record in default_boundary_intelligence_records()
    )


def default_boundary_integrity_visibility() -> tuple[BoundaryIntegrityVisibility, ...]:
    return tuple(
        BoundaryIntegrityVisibility(
            integrity_id=record.integrity_id,
            boundary_id=record.boundary_id,
            visibility_state=record.visibility_state,
            integrity_status="integrity_safe_visible_evidence",
            provenance_reference_id=record.provenance_reference_id,
            lineage_reference_id=record.lineage_reference_id,
            deterministic_order=record.deterministic_order,
        )
        for record in default_boundary_intelligence_records()
    )


def default_boundary_governance_visibility_summaries() -> tuple[BoundaryGovernanceVisibilitySummary, ...]:
    records = default_boundary_intelligence_records()
    summaries: list[BoundaryGovernanceVisibilitySummary] = []
    for index, state in enumerate(BOUNDARY_INTELLIGENCE_STATES, start=1):
        state_records = tuple(record for record in records if record.visibility_state == state)
        summaries.append(
            BoundaryGovernanceVisibilitySummary(
                summary_id=f"summary_{state}_boundary_visibility",
                state_type=state,
                boundary_ids=tuple(record.boundary_id for record in state_records),
                classification_ids=tuple(record.classification_id for record in state_records),
                count=len(state_records),
                deterministic_order=index,
                fail_visible=state in FAIL_VISIBLE_BOUNDARY_STATES,
            )
        )
    return tuple(summaries)


def default_boundary_fail_visible_findings() -> tuple[BoundaryFailVisibleFinding, ...]:
    findings: list[BoundaryFailVisibleFinding] = []
    for record in default_boundary_intelligence_records():
        if record.visibility_state not in FAIL_VISIBLE_BOUNDARY_STATES:
            continue
        findings.append(
            BoundaryFailVisibleFinding(
                finding_id=f"finding_{record.boundary_id}",
                boundary_id=record.boundary_id,
                finding_type=f"{record.visibility_state}_boundary_state",
                visibility_state=record.visibility_state,
                finding_message=(
                    f"{record.visibility_state} state is visible and cannot be inferred into operational authority"
                ),
                evidence_reference_ids=(record.diagnostic_id, record.explainability_id),
                deterministic_order=record.deterministic_order,
            )
        )
    return tuple(findings)


def default_boundary_continuity_metadata() -> BoundaryContinuityMetadata:
    evidence_ids = tuple(record.boundary_id for record in default_boundary_intelligence_records())
    return BoundaryContinuityMetadata(
        continuity_id="v4_4_boundary_intelligence_continuity",
        source_phase_id="v4_3_closeout_and_v4_4_readiness",
        source_report_reference="docs/generated/v4_3_closeout_and_v4_4_readiness_report.json",
        source_report_hash_reference="v4_3_closeout_and_v4_4_readiness.deterministic_report_hash",
        deterministic_evidence_ids=evidence_ids,
        replay_evidence_ids=evidence_ids,
        rollback_evidence_ids=evidence_ids,
        continuity_guarantees=(
            "provenance_continuity_preserved",
            "lineage_continuity_preserved",
            "replay_safe_evidence_preserved",
            "rollback_safe_evidence_preserved",
        ),
        deterministic_order=1,
    )


def default_boundary_provenance_metadata() -> BoundaryProvenanceMetadata:
    return BoundaryProvenanceMetadata(
        provenance_id="v4_4_boundary_intelligence_provenance",
        source_reference_ids=(
            "v4_3_closeout_and_v4_4_readiness",
            "v4_3_orchestration_readiness_certification",
            V4_4_BOUNDARY_INTELLIGENCE_PHASE_ID,
        ),
        source_hash_references=(
            "v4_3_closeout_and_v4_4_readiness.deterministic_report_hash",
            "v4_3_orchestration_readiness_certification.deterministic_report_hash",
        ),
        provenance_chain_status="provenance_continuity_visible",
        deterministic_order=1,
    )


def default_boundary_lineage_metadata() -> BoundaryLineageMetadata:
    return BoundaryLineageMetadata(
        lineage_id="v4_4_boundary_intelligence_lineage",
        lineage_reference_ids=(
            "v4_3_orchestration_manifest_foundations",
            "v4_3_orchestration_boundary_and_capability_visibility",
            "v4_3_orchestration_continuity_and_integrity_certification",
            "v4_3_closeout_and_v4_4_readiness",
            V4_4_BOUNDARY_INTELLIGENCE_PHASE_ID,
        ),
        lineage_hash_references=(
            "manifest_foundations_hash_reference",
            "boundary_capability_visibility_hash_reference",
            "continuity_integrity_certification_hash_reference",
            "closeout_readiness_hash_reference",
        ),
        lineage_status="lineage_continuity_visible",
        deterministic_order=1,
    )


def default_boundary_intelligence_foundations() -> BoundaryIntelligenceFoundations:
    return BoundaryIntelligenceFoundations(
        identity=default_boundary_intelligence_identity(),
        classifications=default_boundary_intelligence_classifications(),
        boundary_records=default_boundary_intelligence_records(),
        scope_visibility=default_boundary_scope_visibility(),
        segmentation_visibility=default_boundary_segmentation_visibility(),
        diagnostics=default_boundary_diagnostics(),
        explainability=default_boundary_explainability(),
        integrity_visibility=default_boundary_integrity_visibility(),
        governance_visibility_summaries=default_boundary_governance_visibility_summaries(),
        fail_visible_findings=default_boundary_fail_visible_findings(),
        continuity_metadata=default_boundary_continuity_metadata(),
        provenance_metadata=default_boundary_provenance_metadata(),
        lineage_metadata=default_boundary_lineage_metadata(),
        deterministic_guarantees=V4_4_BOUNDARY_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_EXPLICIT_PROHIBITIONS,
    )
