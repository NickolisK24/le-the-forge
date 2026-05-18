"""Deterministic v4.4 boundary inheritance and refinement models.

The v4.4 Phase 2 layer models boundary inheritance, refinement ancestry,
continuity propagation, diagnostics, and explainability as descriptive
governance evidence only. It does not grant operational authority, execution
capability, authorization, approval, routing, scheduling, planner integration,
production consumption, or mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_INHERITANCE_PHASE_ID = "v4_4_boundary_inheritance_refinement"
V4_4_BOUNDARY_INHERITANCE_SCHEMA_VERSION = "v4_4.boundary_inheritance_refinement.1"
V4_4_BOUNDARY_INHERITANCE_REPORT_SCHEMA_VERSION = (
    "v4_4.boundary_inheritance_refinement_report.1"
)
V4_4_BOUNDARY_INHERITANCE_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_INHERITANCE_STATUS_STABLE = "v4_4_boundary_inheritance_refinement_stable"
V4_4_BOUNDARY_INHERITANCE_STATUS_BLOCKED = "v4_4_boundary_inheritance_refinement_blocked"
V4_4_BOUNDARY_INHERITANCE_PURPOSE = (
    "deterministic_governance_safe_boundary_inheritance_and_refinement_intelligence_descriptive_only"
)
V4_4_BOUNDARY_INHERITANCE_CLASSIFICATION = (
    "governance_safe_descriptive_boundary_inheritance_refinement_intelligence"
)

INHERITANCE_STATE_SUPPORTED = "supported"
INHERITANCE_STATE_UNSUPPORTED = "unsupported"
INHERITANCE_STATE_PROHIBITED = "prohibited"
INHERITANCE_STATE_BLOCKED = "blocked"
INHERITANCE_STATE_STALE = "stale"
INHERITANCE_STATE_CONFLICTING = "conflicting"
INHERITANCE_STATE_AMBIGUOUS = "ambiguous"
INHERITANCE_STATE_INHERITED = "inherited"
INHERITANCE_STATE_REFINED = "refined"
BOUNDARY_INHERITANCE_STATES: tuple[str, ...] = (
    INHERITANCE_STATE_SUPPORTED,
    INHERITANCE_STATE_UNSUPPORTED,
    INHERITANCE_STATE_PROHIBITED,
    INHERITANCE_STATE_BLOCKED,
    INHERITANCE_STATE_STALE,
    INHERITANCE_STATE_CONFLICTING,
    INHERITANCE_STATE_AMBIGUOUS,
    INHERITANCE_STATE_INHERITED,
    INHERITANCE_STATE_REFINED,
)
FAIL_VISIBLE_INHERITANCE_STATES: tuple[str, ...] = (
    INHERITANCE_STATE_UNSUPPORTED,
    INHERITANCE_STATE_PROHIBITED,
    INHERITANCE_STATE_BLOCKED,
    INHERITANCE_STATE_STALE,
    INHERITANCE_STATE_CONFLICTING,
    INHERITANCE_STATE_AMBIGUOUS,
)

RELATIONSHIP_TYPE_DIRECT_INHERITANCE = "direct_inheritance_visibility"
RELATIONSHIP_TYPE_MULTI_LEVEL_ANCESTRY = "multi_level_refinement_ancestry_visibility"
RELATIONSHIP_TYPE_GOVERNANCE_PROPAGATION = "governance_safe_lineage_propagation"
RELATIONSHIP_TYPE_CONTINUITY_PROPAGATION = "deterministic_continuity_propagation"
RELATIONSHIP_TYPE_PROVENANCE_PROPAGATION = "deterministic_provenance_propagation"
RELATIONSHIP_TYPE_REFINEMENT_EXPLAINABILITY = "boundary_refinement_explainability_chain"
RELATIONSHIP_TYPE_CONFLICT_DIAGNOSTIC = "inheritance_conflict_diagnostic_visibility"
RELATIONSHIP_TYPE_DRIFT_VISIBILITY = "refinement_drift_visibility"
RELATIONSHIP_TYPE_SEGMENTATION_VISIBILITY = "refinement_segmentation_visibility"
BOUNDARY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    RELATIONSHIP_TYPE_DIRECT_INHERITANCE,
    RELATIONSHIP_TYPE_MULTI_LEVEL_ANCESTRY,
    RELATIONSHIP_TYPE_GOVERNANCE_PROPAGATION,
    RELATIONSHIP_TYPE_CONTINUITY_PROPAGATION,
    RELATIONSHIP_TYPE_PROVENANCE_PROPAGATION,
    RELATIONSHIP_TYPE_REFINEMENT_EXPLAINABILITY,
    RELATIONSHIP_TYPE_CONFLICT_DIAGNOSTIC,
    RELATIONSHIP_TYPE_DRIFT_VISIBILITY,
    RELATIONSHIP_TYPE_SEGMENTATION_VISIBILITY,
)

V4_4_BOUNDARY_INHERITANCE_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_INHERITANCE_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "inheritance_ordering_stability",
    "refinement_ordering_stability",
    "inheritance_serialization_stability",
    "refinement_hashing_stability",
    "ancestry_depth_visibility_stability",
    "replay_safe_inheritance_evidence",
    "rollback_safe_refinement_evidence",
    "provenance_propagation_continuity",
    "lineage_propagation_continuity",
    "continuity_propagation_visibility",
    "fail_visible_ambiguity_preservation",
    "fail_visible_conflict_preservation",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_BOUNDARY_INHERITANCE_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 2 models boundary inheritance and refinement intelligence only.",
    "v4.4 Phase 2 inheritance relationships are descriptive-only and non-authoritative.",
    "v4.4 Phase 2 refinement relationships are descriptive-only and non-operational.",
    "v4.4 Phase 2 does not execute orchestration.",
    "v4.4 Phase 2 does not authorize or approve orchestration.",
    "v4.4 Phase 2 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 2 does not recommend, decide, rank, score, select, or optimize orchestration.",
    "v4.4 Phase 2 does not integrate planners or consume production bundles.",
    "v4.4 Phase 2 does not repair, remediate, infer hidden authority, or mutate runtime or operational state.",
)

V4_4_BOUNDARY_INHERITANCE_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No inheritance relationship grants operational authority.",
    "No refinement relationship grants orchestration execution capability.",
    "No orchestration execution exists.",
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
    "No automatic repair exists.",
    "No automatic remediation exists.",
    "No implicit operational authority exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BoundaryInheritanceIdentity:
    inheritance_intelligence_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_boundary_foundation_reference: str
    source_boundary_foundation_hash_reference: str
    inheritance_reference: str
    refinement_reference: str
    ancestry_reference: str
    continuity_propagation_reference: str
    provenance_propagation_reference: str
    lineage_propagation_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_INHERITANCE_PURPOSE
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
class InheritanceRelationshipRecord:
    inheritance_id: str
    parent_boundary_id: str
    child_boundary_id: str
    relationship_type: str
    visibility_state: str
    inheritance_reason: str
    ancestry_depth: int
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    operational_authority: bool = False
    execution_authority: bool = False
    authorization_capability: bool = False
    approval_capability: bool = False
    routing_capability: bool = False
    scheduling_capability: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class RefinementRelationshipRecord:
    refinement_id: str
    source_boundary_id: str
    refined_boundary_id: str
    relationship_type: str
    visibility_state: str
    refinement_reason: str
    refinement_depth: int
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    execution_capability: bool = False
    recommendation_capability: bool = False
    decision_capability: bool = False
    optimization_capability: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class BoundaryAncestryVisibility:
    ancestry_id: str
    boundary_id: str
    ancestor_boundary_ids: tuple[str, ...]
    ancestry_depth: int
    visibility_state: str
    ancestry_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    operational_authority: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "ancestor_boundary_ids")


@dataclass(frozen=True)
class ParentChildRefinementVisibility:
    parent_child_id: str
    parent_boundary_id: str
    child_boundary_id: str
    refinement_id: str
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    execution_capability: bool = False
    routing_capability: bool = False


@dataclass(frozen=True)
class RefinementLineageContinuity:
    lineage_id: str
    refinement_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_state: str
    propagation_state: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    descriptive_only: bool = True
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "lineage_reference_ids")


@dataclass(frozen=True)
class RefinementDiagnosticRecord:
    diagnostic_id: str
    relationship_id: str
    diagnostic_type: str
    visibility_state: str
    severity: str
    diagnostic_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_repair_enabled: bool = False
    automatic_remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class RefinementExplainabilityRecord:
    explainability_id: str
    relationship_id: str
    explanation_type: str
    visibility_state: str
    explanation_chain_ids: tuple[str, ...]
    explanation: str
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "explanation_chain_ids")


@dataclass(frozen=True)
class InheritanceFailVisibleFinding:
    finding_id: str
    relationship_id: str
    finding_type: str
    visibility_state: str
    finding_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden_inference_used: bool = False
    automatic_repair_enabled: bool = False
    automatic_remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ContinuityPropagationMetadata:
    continuity_id: str
    source_phase_id: str
    source_report_reference: str
    source_report_hash_reference: str
    propagated_relationship_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    continuity_propagation_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "propagated_relationship_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ProvenancePropagationMetadata:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    propagated_relationship_ids: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_continuity_preserved: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_reference_ids",
            "source_hash_references",
            "propagated_relationship_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineagePropagationMetadata:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    propagated_relationship_ids: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "lineage_reference_ids",
            "lineage_hash_references",
            "propagated_relationship_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BoundaryInheritanceRefinementIntelligence:
    identity: BoundaryInheritanceIdentity
    inheritance_relationships: tuple[InheritanceRelationshipRecord, ...]
    refinement_relationships: tuple[RefinementRelationshipRecord, ...]
    ancestry_visibility: tuple[BoundaryAncestryVisibility, ...]
    parent_child_refinement_visibility: tuple[ParentChildRefinementVisibility, ...]
    refinement_lineage_continuity: tuple[RefinementLineageContinuity, ...]
    diagnostics: tuple[RefinementDiagnosticRecord, ...]
    explainability: tuple[RefinementExplainabilityRecord, ...]
    fail_visible_findings: tuple[InheritanceFailVisibleFinding, ...]
    continuity_propagation_metadata: ContinuityPropagationMetadata
    provenance_propagation_metadata: ProvenancePropagationMetadata
    lineage_propagation_metadata: LineagePropagationMetadata
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
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
            "inheritance_relationships",
            "refinement_relationships",
            "ancestry_visibility",
            "parent_child_refinement_visibility",
            "refinement_lineage_continuity",
            "diagnostics",
            "explainability",
            "fail_visible_findings",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_boundary_inheritance_identity() -> BoundaryInheritanceIdentity:
    return BoundaryInheritanceIdentity(
        inheritance_intelligence_id="v4_4_boundary_inheritance_refinement_intelligence",
        phase_id=V4_4_BOUNDARY_INHERITANCE_PHASE_ID,
        schema_version=V4_4_BOUNDARY_INHERITANCE_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_INHERITANCE_GENERATED_AT,
        classification=V4_4_BOUNDARY_INHERITANCE_CLASSIFICATION,
        source_boundary_foundation_reference="v4_4_boundary_intelligence_foundations",
        source_boundary_foundation_hash_reference="v4_4_boundary_intelligence_foundations.deterministic_report_hash",
        inheritance_reference="v4_4_boundary_inheritance_relationships",
        refinement_reference="v4_4_boundary_refinement_relationships",
        ancestry_reference="v4_4_boundary_ancestry_visibility",
        continuity_propagation_reference="v4_4_boundary_continuity_propagation",
        provenance_propagation_reference="v4_4_boundary_provenance_propagation",
        lineage_propagation_reference="v4_4_boundary_lineage_propagation",
        non_operational_reference="v4_4_boundary_inheritance_non_operational_certification",
    )


def default_inheritance_relationships() -> tuple[InheritanceRelationshipRecord, ...]:
    definitions = (
        ("inheritance_governance_scope", "v4_4_boundary_intelligence_foundations", "boundary_governance_scope_visibility", RELATIONSHIP_TYPE_DIRECT_INHERITANCE, INHERITANCE_STATE_INHERITED, 1),
        ("inheritance_segmentation_scope", "boundary_governance_scope_visibility", "boundary_deterministic_segmentation", RELATIONSHIP_TYPE_MULTI_LEVEL_ANCESTRY, INHERITANCE_STATE_INHERITED, 2),
        ("inheritance_lineage_propagation", "boundary_governance_scope_visibility", "boundary_missing_lineage_evidence", RELATIONSHIP_TYPE_GOVERNANCE_PROPAGATION, INHERITANCE_STATE_SUPPORTED, 2),
        ("inheritance_external_runtime_semantics", "boundary_governance_scope_visibility", "boundary_external_runtime_semantics", RELATIONSHIP_TYPE_CONFLICT_DIAGNOSTIC, INHERITANCE_STATE_UNSUPPORTED, 1),
        ("inheritance_runtime_execution", "boundary_governance_scope_visibility", "boundary_runtime_execution", RELATIONSHIP_TYPE_DIRECT_INHERITANCE, INHERITANCE_STATE_PROHIBITED, 1),
        ("inheritance_missing_lineage", "boundary_governance_scope_visibility", "boundary_missing_lineage_evidence", RELATIONSHIP_TYPE_CONTINUITY_PROPAGATION, INHERITANCE_STATE_BLOCKED, 3),
        ("inheritance_implicit_provider_identity", "boundary_governance_scope_visibility", "boundary_implicit_provider_identity", RELATIONSHIP_TYPE_PROVENANCE_PROPAGATION, INHERITANCE_STATE_AMBIGUOUS, 2),
        ("inheritance_conflicting_scope_signal", "boundary_governance_scope_visibility", "boundary_conflicting_scope_signal", RELATIONSHIP_TYPE_CONFLICT_DIAGNOSTIC, INHERITANCE_STATE_CONFLICTING, 2),
    )
    return tuple(
        InheritanceRelationshipRecord(
            inheritance_id=inheritance_id,
            parent_boundary_id=parent_boundary_id,
            child_boundary_id=child_boundary_id,
            relationship_type=relationship_type,
            visibility_state=visibility_state,
            inheritance_reason=f"{visibility_state} inheritance relationship remains visible and non-authoritative",
            ancestry_depth=ancestry_depth,
            evidence_reference_ids=(
                "v4_4_boundary_intelligence_foundations_report",
                parent_boundary_id,
                child_boundary_id,
            ),
            deterministic_order=index,
            fail_visible=visibility_state in FAIL_VISIBLE_INHERITANCE_STATES,
        )
        for index, (
            inheritance_id,
            parent_boundary_id,
            child_boundary_id,
            relationship_type,
            visibility_state,
            ancestry_depth,
        ) in enumerate(definitions, start=1)
    )


def default_refinement_relationships() -> tuple[RefinementRelationshipRecord, ...]:
    definitions = (
        ("refinement_scope_to_ancestry", "boundary_governance_scope_visibility", "refined_boundary_ancestry_visibility", RELATIONSHIP_TYPE_REFINEMENT_EXPLAINABILITY, INHERITANCE_STATE_REFINED, 1),
        ("refinement_segmentation_to_lineage", "boundary_deterministic_segmentation", "refined_boundary_lineage_visibility", RELATIONSHIP_TYPE_SEGMENTATION_VISIBILITY, INHERITANCE_STATE_REFINED, 2),
        ("refinement_diagnostics_continuity", "boundary_governance_scope_visibility", "refined_boundary_diagnostics_continuity", RELATIONSHIP_TYPE_CONTINUITY_PROPAGATION, INHERITANCE_STATE_SUPPORTED, 2),
        ("refinement_external_runtime_semantics", "boundary_external_runtime_semantics", "refined_external_runtime_visibility", RELATIONSHIP_TYPE_REFINEMENT_EXPLAINABILITY, INHERITANCE_STATE_UNSUPPORTED, 1),
        ("refinement_planner_production", "boundary_planner_production", "refined_planner_production_prohibition", RELATIONSHIP_TYPE_DIRECT_INHERITANCE, INHERITANCE_STATE_PROHIBITED, 1),
        ("refinement_stale_source_evidence", "boundary_stale_source_evidence", "refined_stale_source_visibility", RELATIONSHIP_TYPE_DRIFT_VISIBILITY, INHERITANCE_STATE_STALE, 2),
        ("refinement_conflicting_scope_signal", "boundary_conflicting_scope_signal", "refined_conflicting_scope_visibility", RELATIONSHIP_TYPE_CONFLICT_DIAGNOSTIC, INHERITANCE_STATE_CONFLICTING, 2),
        ("refinement_implicit_provider_identity", "boundary_implicit_provider_identity", "refined_ambiguous_provider_visibility", RELATIONSHIP_TYPE_PROVENANCE_PROPAGATION, INHERITANCE_STATE_AMBIGUOUS, 2),
    )
    return tuple(
        RefinementRelationshipRecord(
            refinement_id=refinement_id,
            source_boundary_id=source_boundary_id,
            refined_boundary_id=refined_boundary_id,
            relationship_type=relationship_type,
            visibility_state=visibility_state,
            refinement_reason=f"{visibility_state} refinement relationship remains descriptive-only and non-operational",
            refinement_depth=refinement_depth,
            evidence_reference_ids=(
                "v4_4_boundary_intelligence_foundations_report",
                source_boundary_id,
                refined_boundary_id,
            ),
            deterministic_order=index,
            fail_visible=visibility_state in FAIL_VISIBLE_INHERITANCE_STATES,
        )
        for index, (
            refinement_id,
            source_boundary_id,
            refined_boundary_id,
            relationship_type,
            visibility_state,
            refinement_depth,
        ) in enumerate(definitions, start=1)
    )


def default_boundary_ancestry_visibility() -> tuple[BoundaryAncestryVisibility, ...]:
    return tuple(
        BoundaryAncestryVisibility(
            ancestry_id=f"ancestry_{relationship.inheritance_id}",
            boundary_id=relationship.child_boundary_id,
            ancestor_boundary_ids=(
                relationship.parent_boundary_id,
                "v4_4_boundary_intelligence_foundations",
            )
            if relationship.ancestry_depth > 1
            else (relationship.parent_boundary_id,),
            ancestry_depth=relationship.ancestry_depth,
            visibility_state=relationship.visibility_state,
            ancestry_reason="Ancestry visibility is deterministic and does not grant operational authority",
            deterministic_order=relationship.deterministic_order,
        )
        for relationship in default_inheritance_relationships()
    )


def default_parent_child_refinement_visibility() -> tuple[ParentChildRefinementVisibility, ...]:
    return tuple(
        ParentChildRefinementVisibility(
            parent_child_id=f"parent_child_{relationship.refinement_id}",
            parent_boundary_id=relationship.source_boundary_id,
            child_boundary_id=relationship.refined_boundary_id,
            refinement_id=relationship.refinement_id,
            visibility_state=relationship.visibility_state,
            deterministic_order=relationship.deterministic_order,
        )
        for relationship in default_refinement_relationships()
    )


def default_refinement_lineage_continuity() -> tuple[RefinementLineageContinuity, ...]:
    return tuple(
        RefinementLineageContinuity(
            lineage_id=f"lineage_{relationship.refinement_id}",
            refinement_id=relationship.refinement_id,
            lineage_reference_ids=(
                relationship.source_boundary_id,
                relationship.refined_boundary_id,
                "v4_4_boundary_inheritance_refinement",
            ),
            lineage_state=relationship.visibility_state,
            propagation_state="lineage_propagation_visible",
            deterministic_order=relationship.deterministic_order,
        )
        for relationship in default_refinement_relationships()
    )


def default_refinement_diagnostics() -> tuple[RefinementDiagnosticRecord, ...]:
    severity_by_state = {
        INHERITANCE_STATE_SUPPORTED: "info",
        INHERITANCE_STATE_UNSUPPORTED: "warning",
        INHERITANCE_STATE_PROHIBITED: "prohibited",
        INHERITANCE_STATE_BLOCKED: "blocker",
        INHERITANCE_STATE_STALE: "warning",
        INHERITANCE_STATE_CONFLICTING: "warning",
        INHERITANCE_STATE_AMBIGUOUS: "warning",
        INHERITANCE_STATE_INHERITED: "info",
        INHERITANCE_STATE_REFINED: "info",
    }
    diagnostics: list[RefinementDiagnosticRecord] = []
    for relationship in default_inheritance_relationships():
        diagnostics.append(
            RefinementDiagnosticRecord(
                diagnostic_id=f"diagnostic_{relationship.inheritance_id}",
                relationship_id=relationship.inheritance_id,
                diagnostic_type=f"{relationship.visibility_state}_inheritance_visibility",
                visibility_state=relationship.visibility_state,
                severity=severity_by_state[relationship.visibility_state],
                diagnostic_message=(
                    f"{relationship.visibility_state} inheritance is visible without runtime authority"
                ),
                evidence_reference_ids=relationship.evidence_reference_ids,
                deterministic_order=relationship.deterministic_order,
            )
        )
    offset = len(diagnostics)
    for relationship in default_refinement_relationships():
        diagnostics.append(
            RefinementDiagnosticRecord(
                diagnostic_id=f"diagnostic_{relationship.refinement_id}",
                relationship_id=relationship.refinement_id,
                diagnostic_type=f"{relationship.visibility_state}_refinement_visibility",
                visibility_state=relationship.visibility_state,
                severity=severity_by_state[relationship.visibility_state],
                diagnostic_message=(
                    f"{relationship.visibility_state} refinement is visible without execution capability"
                ),
                evidence_reference_ids=relationship.evidence_reference_ids,
                deterministic_order=offset + relationship.deterministic_order,
            )
        )
    return tuple(diagnostics)


def default_refinement_explainability() -> tuple[RefinementExplainabilityRecord, ...]:
    explanations: list[RefinementExplainabilityRecord] = []
    for relationship in default_inheritance_relationships():
        explanations.append(
            RefinementExplainabilityRecord(
                explainability_id=f"explainability_{relationship.inheritance_id}",
                relationship_id=relationship.inheritance_id,
                explanation_type=f"{relationship.visibility_state}_inheritance_explainability",
                visibility_state=relationship.visibility_state,
                explanation_chain_ids=(
                    relationship.parent_boundary_id,
                    relationship.child_boundary_id,
                    relationship.inheritance_id,
                ),
                explanation=(
                    "Inheritance chain is visible for governance analysis only and does not create authority"
                ),
                deterministic_order=relationship.deterministic_order,
            )
        )
    offset = len(explanations)
    for relationship in default_refinement_relationships():
        explanations.append(
            RefinementExplainabilityRecord(
                explainability_id=f"explainability_{relationship.refinement_id}",
                relationship_id=relationship.refinement_id,
                explanation_type=f"{relationship.visibility_state}_refinement_explainability",
                visibility_state=relationship.visibility_state,
                explanation_chain_ids=(
                    relationship.source_boundary_id,
                    relationship.refined_boundary_id,
                    relationship.refinement_id,
                ),
                explanation=(
                    "Refinement chain is visible for deterministic explainability only and does not create execution capability"
                ),
                deterministic_order=offset + relationship.deterministic_order,
            )
        )
    return tuple(explanations)


def default_inheritance_fail_visible_findings() -> tuple[InheritanceFailVisibleFinding, ...]:
    findings: list[InheritanceFailVisibleFinding] = []
    for relationship in (*default_inheritance_relationships(), *default_refinement_relationships()):
        relationship_id = getattr(relationship, "inheritance_id", None) or getattr(
            relationship,
            "refinement_id",
        )
        if relationship.visibility_state not in FAIL_VISIBLE_INHERITANCE_STATES:
            continue
        findings.append(
            InheritanceFailVisibleFinding(
                finding_id=f"finding_{relationship_id}",
                relationship_id=str(relationship_id),
                finding_type=f"{relationship.visibility_state}_inheritance_refinement_visibility",
                visibility_state=relationship.visibility_state,
                finding_message=(
                    f"{relationship.visibility_state} inheritance/refinement state remains visible and cannot imply operational authority"
                ),
                evidence_reference_ids=relationship.evidence_reference_ids,
                deterministic_order=len(findings) + 1,
            )
        )
    return tuple(findings)


def _all_relationship_ids() -> tuple[str, ...]:
    inheritance_ids = tuple(
        relationship.inheritance_id for relationship in default_inheritance_relationships()
    )
    refinement_ids = tuple(
        relationship.refinement_id for relationship in default_refinement_relationships()
    )
    return inheritance_ids + refinement_ids


def default_continuity_propagation_metadata() -> ContinuityPropagationMetadata:
    relationship_ids = _all_relationship_ids()
    return ContinuityPropagationMetadata(
        continuity_id="v4_4_boundary_inheritance_continuity_propagation",
        source_phase_id="v4_4_boundary_intelligence_foundations",
        source_report_reference="docs/generated/v4_4_boundary_intelligence_foundations_report.json",
        source_report_hash_reference="v4_4_boundary_intelligence_foundations.deterministic_report_hash",
        propagated_relationship_ids=relationship_ids,
        replay_evidence_ids=relationship_ids,
        rollback_evidence_ids=relationship_ids,
        deterministic_order=1,
    )


def default_provenance_propagation_metadata() -> ProvenancePropagationMetadata:
    return ProvenancePropagationMetadata(
        provenance_id="v4_4_boundary_inheritance_provenance_propagation",
        source_reference_ids=(
            "v4_3_closeout_and_v4_4_readiness",
            "v4_4_boundary_intelligence_foundations",
            V4_4_BOUNDARY_INHERITANCE_PHASE_ID,
        ),
        source_hash_references=(
            "v4_3_closeout_and_v4_4_readiness.deterministic_report_hash",
            "v4_4_boundary_intelligence_foundations.deterministic_report_hash",
        ),
        propagated_relationship_ids=_all_relationship_ids(),
        provenance_state="provenance_propagation_visible",
        deterministic_order=1,
    )


def default_lineage_propagation_metadata() -> LineagePropagationMetadata:
    return LineagePropagationMetadata(
        lineage_id="v4_4_boundary_inheritance_lineage_propagation",
        lineage_reference_ids=(
            "v4_3_orchestration_boundary_and_capability_visibility",
            "v4_3_orchestration_continuity_and_integrity_certification",
            "v4_4_boundary_intelligence_foundations",
            V4_4_BOUNDARY_INHERITANCE_PHASE_ID,
        ),
        lineage_hash_references=(
            "v4_3_boundary_capability_visibility_hash_reference",
            "v4_3_continuity_integrity_hash_reference",
            "v4_4_boundary_intelligence_foundations_hash_reference",
        ),
        propagated_relationship_ids=_all_relationship_ids(),
        lineage_state="lineage_propagation_visible",
        deterministic_order=1,
    )


def default_boundary_inheritance_refinement_intelligence() -> BoundaryInheritanceRefinementIntelligence:
    return BoundaryInheritanceRefinementIntelligence(
        identity=default_boundary_inheritance_identity(),
        inheritance_relationships=default_inheritance_relationships(),
        refinement_relationships=default_refinement_relationships(),
        ancestry_visibility=default_boundary_ancestry_visibility(),
        parent_child_refinement_visibility=default_parent_child_refinement_visibility(),
        refinement_lineage_continuity=default_refinement_lineage_continuity(),
        diagnostics=default_refinement_diagnostics(),
        explainability=default_refinement_explainability(),
        fail_visible_findings=default_inheritance_fail_visible_findings(),
        continuity_propagation_metadata=default_continuity_propagation_metadata(),
        provenance_propagation_metadata=default_provenance_propagation_metadata(),
        lineage_propagation_metadata=default_lineage_propagation_metadata(),
        deterministic_guarantees=V4_4_BOUNDARY_INHERITANCE_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_INHERITANCE_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_INHERITANCE_EXPLICIT_PROHIBITIONS,
    )
