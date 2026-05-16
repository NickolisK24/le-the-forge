"""Deterministic v3.8 coordination foundation models.

The foundation models describe orchestration-planning coordination evidence.
They do not execute coordination, route work, schedule work, dispatch work,
traverse graphs, mutate runtime state, optimize execution, recommend execution,
or authorize execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

try:
    from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize
except ModuleNotFoundError:
    import hashlib
    import json

    def stable_serialize(payload: Any) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)

    def deterministic_hash(payload: Any) -> str:
        return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()

from .coordination_continuity_models import (
    V3_8_COORDINATION_CONTINUITY_PRESERVED,
    V3_8_COORDINATION_EXPLAINABILITY_VISIBLE,
    V3_8_COORDINATION_INTEGRITY_PRESERVED,
    V3_8_COORDINATION_PROVENANCE_PRESERVED,
    V38CoordinationContinuityState,
    V38CoordinationExplainabilityState,
    V38CoordinationIntegrityState,
    V38CoordinationProvenanceState,
    V38CoordinationReplayEvidence,
    V38CoordinationRollbackEvidence,
)
from .coordination_identity_models import (
    V3_8_COORDINATION_BOUNDARY_VISIBLE,
    V3_8_COORDINATION_FOUNDATION_PHASE_ID,
    V3_8_COORDINATION_SCHEMA_VERSION,
    V38CoordinationBoundary,
    V38CoordinationIdentity,
    V38CoordinationReference,
    build_v3_8_coordination_identity,
)
from .coordination_relationship_models import (
    V38CoordinationRelationship,
    V38CoordinationRelationshipChain,
)


V3_8_COORDINATION_FOUNDATION_STATUS_STABLE = "v3_8_coordination_foundation_stable"
V3_8_COORDINATION_FOUNDATION_STATUS_BLOCKED = "v3_8_coordination_foundation_blocked"
V3_8_COORDINATION_UNSUPPORTED_VISIBLE = "coordination_unsupported_state_visible"
V3_8_COORDINATION_PROHIBITED_VISIBLE = "coordination_prohibited_state_visible"
V3_8_COORDINATION_UNKNOWN_FAIL_VISIBLE = "coordination_unknown_state_fail_visible"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class V38CoordinationMetadataEntry:
    metadata_key: str
    metadata_value: str
    included_in_hash: bool = True


@dataclass(frozen=True)
class V38CoordinationUnsupportedState:
    state_id: str
    state_type: str
    visibility_status: str
    reason: str
    provenance_reference_ids: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "provenance_reference_ids")


@dataclass(frozen=True)
class V38CoordinationProhibitedState:
    state_id: str
    state_type: str
    visibility_status: str
    reason: str
    provenance_reference_ids: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "provenance_reference_ids")


@dataclass(frozen=True)
class V38CoordinationUnknownState:
    state_id: str
    state_type: str
    visibility_status: str
    reason: str
    provenance_reference_ids: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "provenance_reference_ids")


@dataclass(frozen=True)
class V38CoordinationFoundation:
    identity: V38CoordinationIdentity
    metadata: tuple[V38CoordinationMetadataEntry, ...]
    coordination_references: tuple[V38CoordinationReference, ...]
    coordination_boundaries: tuple[V38CoordinationBoundary, ...]
    relationships: tuple[V38CoordinationRelationship, ...]
    relationship_chains: tuple[V38CoordinationRelationshipChain, ...]
    continuity_state: V38CoordinationContinuityState
    provenance_state: V38CoordinationProvenanceState
    explainability_state: V38CoordinationExplainabilityState
    integrity_state: V38CoordinationIntegrityState
    replay_evidence: tuple[V38CoordinationReplayEvidence, ...]
    rollback_evidence: tuple[V38CoordinationRollbackEvidence, ...]
    unsupported_states: tuple[V38CoordinationUnsupportedState, ...]
    prohibited_states: tuple[V38CoordinationProhibitedState, ...]
    unknown_states: tuple[V38CoordinationUnknownState, ...]
    planning_coordination_only: bool = True
    non_executable: bool = True
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    execution_authorization_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_execution_enabled: bool = False
    graph_traversal_execution_enabled: bool = False
    runtime_path_selection_enabled: bool = False
    recommendation_enabled: bool = False
    optimization_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    callable_execution_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    hidden_state_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "coordination_references",
            "coordination_boundaries",
            "relationships",
            "relationship_chains",
            "replay_evidence",
            "rollback_evidence",
            "unsupported_states",
            "prohibited_states",
            "unknown_states",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_v3_8_coordination_foundation() -> V38CoordinationFoundation:
    identity = build_v3_8_coordination_identity()
    metadata = (
        V38CoordinationMetadataEntry("deterministic_serializer", "json_sort_keys_stable_tuples"),
        V38CoordinationMetadataEntry("coordination_semantics", "declarative_planning_coordination_only"),
        V38CoordinationMetadataEntry("runtime_capability", "none"),
        V38CoordinationMetadataEntry("mutation_capability", "none"),
        V38CoordinationMetadataEntry("execution_boundary", "strict_non_executable"),
    )
    references = _default_references()
    unsupported_states = _default_unsupported_states()
    prohibited_states = _default_prohibited_states()
    unknown_states = _default_unknown_states()
    boundaries = _default_boundaries(unsupported_states, prohibited_states, unknown_states)
    replay_evidence = _default_replay_evidence(references)
    rollback_evidence = _default_rollback_evidence(references)
    relationships = _default_relationships(
        identity,
        references,
        unsupported_states,
        prohibited_states,
        replay_evidence,
        rollback_evidence,
    )
    relationship_chains = _default_relationship_chains(relationships, replay_evidence, rollback_evidence)
    continuity_state = V38CoordinationContinuityState(
        continuity_id="v3_8_coordination_continuity_state",
        continuity_status=V3_8_COORDINATION_CONTINUITY_PRESERVED,
        preserved_reference_ids=tuple(reference.reference_id for reference in references),
        relationship_chain_ids=tuple(chain.chain_id for chain in relationship_chains),
        replay_evidence_ids=tuple(evidence.replay_evidence_id for evidence in replay_evidence),
        rollback_evidence_ids=tuple(evidence.rollback_evidence_id for evidence in rollback_evidence),
        provenance_reference_ids=("v3_8_coordination_provenance_state",),
        explainability_reference_ids=("v3_8_coordination_explainability_state",),
        deterministic_hash_references=("v3_8_coordination_foundation_hash",),
    )
    provenance_state = V38CoordinationProvenanceState(
        provenance_id="v3_8_coordination_provenance_state",
        provenance_status=V3_8_COORDINATION_PROVENANCE_PRESERVED,
        source_phase_id=V3_8_COORDINATION_FOUNDATION_PHASE_ID,
        source_artifact_id=identity.coordination_id,
        lineage_reference_ids=tuple(reference.reference_id for reference in references),
        prior_phase_reference_ids=(
            "v3_7_closeout_and_v3_8_readiness_report",
            "v3_7_graph_planning_continuity_certification_report",
            "v3_7_graph_planning_intelligence_aggregation_report",
        ),
        continuity_reference_ids=(continuity_state.continuity_id,),
        explainability_reference_ids=("v3_8_coordination_explainability_state",),
        replay_reference_ids=tuple(evidence.replay_evidence_id for evidence in replay_evidence),
        rollback_reference_ids=tuple(evidence.rollback_evidence_id for evidence in rollback_evidence),
        deterministic_lineage_hash_reference="v3_8_coordination_foundation_hash",
    )
    explainability_state = V38CoordinationExplainabilityState(
        explainability_id="v3_8_coordination_explainability_state",
        explainability_status=V3_8_COORDINATION_EXPLAINABILITY_VISIBLE,
        subject_id=identity.coordination_id,
        visibility_chain_ids=tuple(chain.chain_id for chain in relationship_chains),
        unsupported_state_ids=tuple(state.state_id for state in unsupported_states),
        prohibited_state_ids=tuple(state.state_id for state in prohibited_states),
        unknown_state_ids=tuple(state.state_id for state in unknown_states),
        explanation=(
            "v3.8 coordination foundations preserve planning coordination identity, "
            "relationships, continuity, provenance, replay evidence, and rollback "
            "evidence without enabling execution behavior."
        ),
        provenance_reference_ids=(provenance_state.provenance_id,),
    )
    integrity_state = V38CoordinationIntegrityState(
        integrity_id="v3_8_coordination_integrity_state",
        integrity_status=V3_8_COORDINATION_INTEGRITY_PRESERVED,
        unsupported_state_ids=tuple(state.state_id for state in unsupported_states),
        prohibited_state_ids=tuple(state.state_id for state in prohibited_states),
        unknown_state_ids=tuple(state.state_id for state in unknown_states),
        execution_boundary_violation_ids=(),
        provenance_reference_ids=(provenance_state.provenance_id,),
        explainability_reference_ids=(explainability_state.explainability_id,),
    )
    return V38CoordinationFoundation(
        identity=identity,
        metadata=metadata,
        coordination_references=references,
        coordination_boundaries=boundaries,
        relationships=relationships,
        relationship_chains=relationship_chains,
        continuity_state=continuity_state,
        provenance_state=provenance_state,
        explainability_state=explainability_state,
        integrity_state=integrity_state,
        replay_evidence=replay_evidence,
        rollback_evidence=rollback_evidence,
        unsupported_states=unsupported_states,
        prohibited_states=prohibited_states,
        unknown_states=unknown_states,
    )


def export_v3_8_coordination_foundation(foundation: V38CoordinationFoundation) -> dict[str, Any]:
    return {
        "identity": asdict(foundation.identity),
        "metadata": _export_metadata(foundation.metadata),
        "coordination_references": [
            _export_reference(reference)
            for reference in sorted(foundation.coordination_references, key=lambda item: item.reference_id)
        ],
        "coordination_boundaries": [
            _export_boundary(boundary)
            for boundary in sorted(foundation.coordination_boundaries, key=lambda item: item.boundary_id)
        ],
        "relationships": [
            _export_relationship(relationship)
            for relationship in sorted(
                foundation.relationships,
                key=lambda item: (item.deterministic_order, item.relationship_id),
            )
        ],
        "relationship_chains": [
            _export_relationship_chain(chain)
            for chain in sorted(
                foundation.relationship_chains,
                key=lambda item: (item.deterministic_order, item.chain_id),
            )
        ],
        "continuity_state": _export_continuity_state(foundation.continuity_state),
        "provenance_state": _export_provenance_state(foundation.provenance_state),
        "explainability_state": _export_explainability_state(foundation.explainability_state),
        "integrity_state": _export_integrity_state(foundation.integrity_state),
        "replay_evidence": [
            _export_replay_evidence(evidence)
            for evidence in sorted(foundation.replay_evidence, key=lambda item: item.replay_evidence_id)
        ],
        "rollback_evidence": [
            _export_rollback_evidence(evidence)
            for evidence in sorted(foundation.rollback_evidence, key=lambda item: item.rollback_evidence_id)
        ],
        "unsupported_states": [
            _export_visibility_state(state)
            for state in sorted(foundation.unsupported_states, key=lambda item: item.state_id)
        ],
        "prohibited_states": [
            _export_visibility_state(state)
            for state in sorted(foundation.prohibited_states, key=lambda item: item.state_id)
        ],
        "unknown_states": [
            _export_visibility_state(state)
            for state in sorted(foundation.unknown_states, key=lambda item: item.state_id)
        ],
        "planning_coordination_only": foundation.planning_coordination_only,
        "non_executable": foundation.non_executable,
        "coordination_execution_enabled": foundation.coordination_execution_enabled,
        "orchestration_execution_enabled": foundation.orchestration_execution_enabled,
        "execution_authorization_enabled": foundation.execution_authorization_enabled,
        "routing_enabled": foundation.routing_enabled,
        "scheduling_enabled": foundation.scheduling_enabled,
        "dispatch_enabled": foundation.dispatch_enabled,
        "traversal_execution_enabled": foundation.traversal_execution_enabled,
        "graph_traversal_execution_enabled": foundation.graph_traversal_execution_enabled,
        "runtime_path_selection_enabled": foundation.runtime_path_selection_enabled,
        "recommendation_enabled": foundation.recommendation_enabled,
        "optimization_enabled": foundation.optimization_enabled,
        "autonomous_orchestration_enabled": foundation.autonomous_orchestration_enabled,
        "callable_execution_flow_enabled": foundation.callable_execution_flow_enabled,
        "persistent_runtime_mutation_enabled": foundation.persistent_runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": foundation.persistent_runtime_writes_enabled,
        "hidden_state_transition_enabled": foundation.hidden_state_transition_enabled,
        "silent_fallback_enabled": foundation.silent_fallback_enabled,
    }


def serialize_v3_8_coordination_foundation(foundation: V38CoordinationFoundation) -> str:
    return stable_serialize(export_v3_8_coordination_foundation(foundation))


def hash_v3_8_coordination_foundation(foundation: V38CoordinationFoundation) -> str:
    return deterministic_hash(export_v3_8_coordination_foundation(foundation))


def validate_v3_8_coordination_serialization_stability(
    foundation: V38CoordinationFoundation,
) -> dict[str, Any]:
    first = serialize_v3_8_coordination_foundation(foundation)
    second = serialize_v3_8_coordination_foundation(foundation)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_coordination_foundations",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_coordination_hash_stability(foundation: V38CoordinationFoundation) -> dict[str, Any]:
    first = hash_v3_8_coordination_foundation(foundation)
    second = hash_v3_8_coordination_foundation(foundation)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_coordination_foundations",
    }


def validate_v3_8_coordination_foundation_guarantees(
    foundation: V38CoordinationFoundation,
) -> dict[str, Any]:
    serialization = validate_v3_8_coordination_serialization_stability(foundation)
    hashing = validate_v3_8_coordination_hash_stability(foundation)
    relationship_execution_violation_count = sum(
        1
        for relationship in foundation.relationships
        if any(
            (
                relationship.relationship_executable,
                relationship.traversal_enabled,
                relationship.dispatch_enabled,
                relationship.routing_enabled,
                relationship.scheduling_enabled,
            )
        )
    )
    chain_execution_violation_count = sum(
        1
        for chain in foundation.relationship_chains
        if any((chain.chain_executable, chain.traversal_execution_enabled, chain.hidden_transition_enabled))
    )
    execution_boundary_violation_count = sum(
        1
        for value in (
            foundation.coordination_execution_enabled,
            foundation.orchestration_execution_enabled,
            foundation.execution_authorization_enabled,
            foundation.routing_enabled,
            foundation.scheduling_enabled,
            foundation.dispatch_enabled,
            foundation.traversal_execution_enabled,
            foundation.graph_traversal_execution_enabled,
            foundation.runtime_path_selection_enabled,
            foundation.recommendation_enabled,
            foundation.optimization_enabled,
            foundation.autonomous_orchestration_enabled,
            foundation.callable_execution_flow_enabled,
            foundation.persistent_runtime_mutation_enabled,
            foundation.persistent_runtime_writes_enabled,
            foundation.hidden_state_transition_enabled,
            foundation.silent_fallback_enabled,
        )
        if value
    )
    fail_visible_state_count = sum(
        1
        for state in (*foundation.unsupported_states, *foundation.prohibited_states, *foundation.unknown_states)
        if state.fail_visible and not state.hidden
    )
    validation_error_count = sum(
        1
        for value in (
            not foundation.non_executable,
            not foundation.planning_coordination_only,
            not foundation.continuity_state.continuity_preserved,
            not foundation.provenance_state.provenance_preserved,
            not foundation.explainability_state.fail_visible,
            foundation.explainability_state.hidden_state,
            not foundation.integrity_state.integrity_preserved,
            foundation.integrity_state.silent_fallback_detected,
            foundation.integrity_state.hidden_transition_detected,
            execution_boundary_violation_count > 0,
            relationship_execution_violation_count > 0,
            chain_execution_violation_count > 0,
            any(not evidence.replay_safe or evidence.runtime_replay_enabled for evidence in foundation.replay_evidence),
            any(
                not evidence.rollback_safe or evidence.rollback_execution_enabled
                for evidence in foundation.rollback_evidence
            ),
            any(not state.fail_visible or state.hidden for state in foundation.unsupported_states),
            any(not state.fail_visible or state.hidden for state in foundation.prohibited_states),
            any(not state.fail_visible or state.hidden for state in foundation.unknown_states),
            not serialization["stable"],
            not hashing["stable"],
        )
        if value
    )
    return {
        "validation_status": V3_8_COORDINATION_FOUNDATION_STATUS_STABLE
        if validation_error_count == 0
        else V3_8_COORDINATION_FOUNDATION_STATUS_BLOCKED,
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "coordination_reference_count": len(foundation.coordination_references),
        "coordination_boundary_count": len(foundation.coordination_boundaries),
        "relationship_count": len(foundation.relationships),
        "relationship_chain_count": len(foundation.relationship_chains),
        "unsupported_state_count": len(foundation.unsupported_states),
        "prohibited_state_count": len(foundation.prohibited_states),
        "unknown_state_count": len(foundation.unknown_states),
        "fail_visible_state_count": fail_visible_state_count,
        "replay_evidence_count": len(foundation.replay_evidence),
        "rollback_evidence_count": len(foundation.rollback_evidence),
        "deterministic_serialization_stable": serialization["stable"],
        "deterministic_hash_stable": hashing["stable"],
        "deterministic_foundation_hash": hashing["first_hash"],
        "continuity_preserved": foundation.continuity_state.continuity_preserved,
        "provenance_preserved": foundation.provenance_state.provenance_preserved,
        "explainability_fail_visible": foundation.explainability_state.fail_visible,
        "integrity_preserved": foundation.integrity_state.integrity_preserved,
        "replay_safe": all(
            evidence.replay_safe and not evidence.runtime_replay_enabled for evidence in foundation.replay_evidence
        ),
        "rollback_safe": all(
            evidence.rollback_safe and not evidence.rollback_execution_enabled
            for evidence in foundation.rollback_evidence
        ),
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "relationship_execution_violation_count": relationship_execution_violation_count,
        "chain_execution_violation_count": chain_execution_violation_count,
        "hidden_transition_detected": foundation.integrity_state.hidden_transition_detected,
        "silent_fallback_detected": foundation.integrity_state.silent_fallback_detected,
    }


def _default_references() -> tuple[V38CoordinationReference, ...]:
    return (
        V38CoordinationReference(
            reference_id="v3_8_ref_v3_7_closeout_readiness",
            reference_type="prior_phase_closeout",
            subject_id="v3_7_closeout_and_v3_8_readiness",
            source_phase_id="v3_7_closeout_and_v3_8_readiness",
            artifact_id="docs/generated/v3_7_closeout_and_v3_8_readiness_report.json",
            deterministic_hash_reference="v3_7_closeout_report_hash",
            provenance_reference_ids=("v3_7_closeout_provenance",),
            continuity_reference_ids=("v3_7_to_v3_8_coordination_continuity",),
            explainability_reference_ids=("v3_7_closeout_explainability",),
            replay_reference_ids=("v3_7_closeout_replay_evidence",),
            rollback_reference_ids=("v3_7_closeout_rollback_evidence",),
        ),
        V38CoordinationReference(
            reference_id="v3_8_ref_graph_continuity_certification",
            reference_type="continuity_certification",
            subject_id="v3_7_graph_planning_continuity_certification",
            source_phase_id="v3_7_graph_planning_continuity_certification",
            artifact_id="docs/generated/v3_7_graph_planning_continuity_certification_report.json",
            deterministic_hash_reference="v3_7_graph_certification_hash",
            provenance_reference_ids=("v3_7_graph_certification_provenance",),
            continuity_reference_ids=("v3_7_graph_certification_continuity",),
            explainability_reference_ids=("v3_7_graph_certification_explainability",),
            replay_reference_ids=("v3_7_graph_certification_replay_evidence",),
            rollback_reference_ids=("v3_7_graph_certification_rollback_evidence",),
        ),
        V38CoordinationReference(
            reference_id="v3_8_ref_graph_integrity_enforcement",
            reference_type="integrity_evidence",
            subject_id="v3_7_graph_integrity_enforcement",
            source_phase_id="v3_7_graph_integrity_enforcement",
            artifact_id="docs/generated/v3_7_graph_planning_integrity_enforcement_report.json",
            deterministic_hash_reference="v3_7_graph_integrity_hash",
            provenance_reference_ids=("v3_7_graph_integrity_provenance",),
            continuity_reference_ids=("v3_7_graph_integrity_continuity",),
            explainability_reference_ids=("v3_7_graph_integrity_explainability",),
            replay_reference_ids=("v3_7_graph_integrity_replay_evidence",),
            rollback_reference_ids=("v3_7_graph_integrity_rollback_evidence",),
        ),
        V38CoordinationReference(
            reference_id="v3_8_ref_graph_intelligence_aggregation",
            reference_type="planning_intelligence_evidence",
            subject_id="v3_7_graph_planning_intelligence_aggregation",
            source_phase_id="v3_7_graph_planning_intelligence_aggregation",
            artifact_id="docs/generated/v3_7_graph_planning_intelligence_aggregation_report.json",
            deterministic_hash_reference="v3_7_graph_aggregation_hash",
            provenance_reference_ids=("v3_7_graph_aggregation_provenance",),
            continuity_reference_ids=("v3_7_graph_aggregation_continuity",),
            explainability_reference_ids=("v3_7_graph_aggregation_explainability",),
            replay_reference_ids=("v3_7_graph_aggregation_replay_evidence",),
            rollback_reference_ids=("v3_7_graph_aggregation_rollback_evidence",),
        ),
    )


def _default_unsupported_states() -> tuple[V38CoordinationUnsupportedState, ...]:
    return (
        V38CoordinationUnsupportedState(
            state_id="v3_8_unsupported_runtime_coordination_execution",
            state_type="runtime_coordination_execution",
            visibility_status=V3_8_COORDINATION_UNSUPPORTED_VISIBLE,
            reason="runtime coordination execution is outside the v3.8 foundation scope",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationUnsupportedState(
            state_id="v3_8_unsupported_coordination_optimization",
            state_type="coordination_optimization",
            visibility_status=V3_8_COORDINATION_UNSUPPORTED_VISIBLE,
            reason="coordination optimization is not modeled by v3.8 foundations",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationUnsupportedState(
            state_id="v3_8_unsupported_autonomous_orchestration",
            state_type="autonomous_orchestration",
            visibility_status=V3_8_COORDINATION_UNSUPPORTED_VISIBLE,
            reason="autonomous orchestration remains outside deterministic coordination foundations",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
    )


def _default_prohibited_states() -> tuple[V38CoordinationProhibitedState, ...]:
    return (
        V38CoordinationProhibitedState(
            state_id="v3_8_prohibited_orchestration_execution",
            state_type="orchestration_execution",
            visibility_status=V3_8_COORDINATION_PROHIBITED_VISIBLE,
            reason="orchestration execution is prohibited in v3.8 coordination foundations",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationProhibitedState(
            state_id="v3_8_prohibited_routing_scheduling_dispatch",
            state_type="routing_scheduling_dispatch",
            visibility_status=V3_8_COORDINATION_PROHIBITED_VISIBLE,
            reason="routing, scheduling, and dispatch are prohibited",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationProhibitedState(
            state_id="v3_8_prohibited_traversal_execution",
            state_type="traversal_execution",
            visibility_status=V3_8_COORDINATION_PROHIBITED_VISIBLE,
            reason="graph traversal execution is prohibited",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationProhibitedState(
            state_id="v3_8_prohibited_execution_authorization",
            state_type="execution_authorization",
            visibility_status=V3_8_COORDINATION_PROHIBITED_VISIBLE,
            reason="execution authorization is prohibited",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
    )


def _default_unknown_states() -> tuple[V38CoordinationUnknownState, ...]:
    return (
        V38CoordinationUnknownState(
            state_id="v3_8_unknown_coordination_capability_fail_visible",
            state_type="unknown_coordination_capability",
            visibility_status=V3_8_COORDINATION_UNKNOWN_FAIL_VISIBLE,
            reason="unknown coordination capabilities must remain fail-visible until explicitly modeled",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationUnknownState(
            state_id="v3_8_unknown_runtime_state_fail_visible",
            state_type="unknown_runtime_state",
            visibility_status=V3_8_COORDINATION_UNKNOWN_FAIL_VISIBLE,
            reason="unknown runtime states cannot be inferred as supported coordination behavior",
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
    )


def _default_boundaries(
    unsupported_states: tuple[V38CoordinationUnsupportedState, ...],
    prohibited_states: tuple[V38CoordinationProhibitedState, ...],
    unknown_states: tuple[V38CoordinationUnknownState, ...],
) -> tuple[V38CoordinationBoundary, ...]:
    unsupported_ids = tuple(state.state_id for state in unsupported_states)
    prohibited_ids = tuple(state.state_id for state in prohibited_states)
    unknown_ids = tuple(state.state_id for state in unknown_states)
    return (
        V38CoordinationBoundary(
            boundary_id="v3_8_non_execution_coordination_boundary",
            boundary_type="non_execution",
            boundary_status=V3_8_COORDINATION_BOUNDARY_VISIBLE,
            restriction_summary="coordination foundations model planning evidence only",
            unsupported_state_ids=unsupported_ids,
            prohibited_state_ids=prohibited_ids,
            unknown_state_ids=unknown_ids,
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
            explainability_reference_ids=("v3_8_coordination_explainability_state",),
        ),
        V38CoordinationBoundary(
            boundary_id="v3_8_non_routing_scheduling_dispatch_boundary",
            boundary_type="routing_scheduling_dispatch_prohibited",
            boundary_status=V3_8_COORDINATION_BOUNDARY_VISIBLE,
            restriction_summary="coordination relationships do not route, schedule, or dispatch work",
            unsupported_state_ids=unsupported_ids,
            prohibited_state_ids=prohibited_ids,
            unknown_state_ids=unknown_ids,
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
            explainability_reference_ids=("v3_8_coordination_explainability_state",),
        ),
        V38CoordinationBoundary(
            boundary_id="v3_8_fail_visible_uncertainty_boundary",
            boundary_type="fail_visible_uncertainty",
            boundary_status=V3_8_COORDINATION_BOUNDARY_VISIBLE,
            restriction_summary="unsupported, prohibited, and unknown states stay visible",
            unsupported_state_ids=unsupported_ids,
            prohibited_state_ids=prohibited_ids,
            unknown_state_ids=unknown_ids,
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
            explainability_reference_ids=("v3_8_coordination_explainability_state",),
        ),
    )


def _default_replay_evidence(
    references: tuple[V38CoordinationReference, ...],
) -> tuple[V38CoordinationReplayEvidence, ...]:
    reference_ids = tuple(reference.reference_id for reference in references)
    return (
        V38CoordinationReplayEvidence(
            replay_evidence_id="v3_8_coordination_foundation_replay_evidence",
            subject_id="v3-8-deterministic-coordination-foundation",
            replay_scope="planning_coordination_replay_evidence_only",
            evidence_reference_ids=reference_ids,
            deterministic_hash_references=("v3_8_coordination_foundation_hash",),
            continuity_reference_ids=("v3_8_coordination_continuity_state",),
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationReplayEvidence(
            replay_evidence_id="v3_8_coordination_relationship_chain_replay_evidence",
            subject_id="v3_8_coordination_relationship_chain",
            replay_scope="relationship_chain_replay_evidence_only",
            evidence_reference_ids=reference_ids,
            deterministic_hash_references=("v3_8_coordination_relationship_chain_hash",),
            continuity_reference_ids=("v3_8_coordination_continuity_state",),
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
    )


def _default_rollback_evidence(
    references: tuple[V38CoordinationReference, ...],
) -> tuple[V38CoordinationRollbackEvidence, ...]:
    reference_ids = tuple(reference.reference_id for reference in references)
    return (
        V38CoordinationRollbackEvidence(
            rollback_evidence_id="v3_8_coordination_foundation_rollback_evidence",
            subject_id="v3-8-deterministic-coordination-foundation",
            rollback_scope="planning_coordination_rollback_evidence_only",
            rollback_reference_ids=reference_ids,
            deterministic_hash_references=("v3_8_coordination_foundation_hash",),
            continuity_reference_ids=("v3_8_coordination_continuity_state",),
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
        V38CoordinationRollbackEvidence(
            rollback_evidence_id="v3_8_coordination_relationship_chain_rollback_evidence",
            subject_id="v3_8_coordination_relationship_chain",
            rollback_scope="relationship_chain_rollback_evidence_only",
            rollback_reference_ids=reference_ids,
            deterministic_hash_references=("v3_8_coordination_relationship_chain_hash",),
            continuity_reference_ids=("v3_8_coordination_continuity_state",),
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
        ),
    )


def _default_relationships(
    identity: V38CoordinationIdentity,
    references: tuple[V38CoordinationReference, ...],
    unsupported_states: tuple[V38CoordinationUnsupportedState, ...],
    prohibited_states: tuple[V38CoordinationProhibitedState, ...],
    replay_evidence: tuple[V38CoordinationReplayEvidence, ...],
    rollback_evidence: tuple[V38CoordinationRollbackEvidence, ...],
) -> tuple[V38CoordinationRelationship, ...]:
    reference_ids = tuple(reference.reference_id for reference in references)
    unsupported_ids = tuple(state.state_id for state in unsupported_states)
    prohibited_ids = tuple(state.state_id for state in prohibited_states)
    replay_ids = tuple(evidence.replay_evidence_id for evidence in replay_evidence)
    rollback_ids = tuple(evidence.rollback_evidence_id for evidence in rollback_evidence)
    relationship_specs = (
        (
            "v3_8_relationship_identity_to_references",
            "coordination_identity_preserves_references",
            identity.coordination_id,
            "v3_8_coordination_reference_set",
            "coordination identity anchors deterministic reference evidence",
        ),
        (
            "v3_8_relationship_references_to_relationship_chain",
            "coordination_references_preserve_relationship_chain",
            "v3_8_coordination_reference_set",
            "v3_8_coordination_relationship_chain",
            "references feed deterministic relationship continuity",
        ),
        (
            "v3_8_relationship_chain_to_continuity",
            "coordination_relationship_chain_preserves_continuity",
            "v3_8_coordination_relationship_chain",
            "v3_8_coordination_continuity_state",
            "relationship chains preserve continuity evidence",
        ),
        (
            "v3_8_relationship_continuity_to_provenance",
            "coordination_continuity_preserves_provenance",
            "v3_8_coordination_continuity_state",
            "v3_8_coordination_provenance_state",
            "continuity evidence preserves provenance lineage",
        ),
        (
            "v3_8_relationship_provenance_to_explainability",
            "coordination_provenance_preserves_explainability",
            "v3_8_coordination_provenance_state",
            "v3_8_coordination_explainability_state",
            "provenance lineage keeps explainability deterministic",
        ),
        (
            "v3_8_relationship_explainability_to_replay_rollback",
            "coordination_explainability_preserves_replay_and_rollback",
            "v3_8_coordination_explainability_state",
            "v3_8_coordination_replay_rollback_evidence",
            "explainability remains tied to replay and rollback evidence",
        ),
    )
    return tuple(
        V38CoordinationRelationship(
            relationship_id=relationship_id,
            relationship_type=relationship_type,
            source_coordination_id=source_id,
            target_coordination_id=target_id,
            relationship_purpose=purpose,
            continuity_reference_ids=("v3_8_coordination_continuity_state", *reference_ids),
            provenance_reference_ids=("v3_8_coordination_provenance_state",),
            explainability_reference_ids=("v3_8_coordination_explainability_state",),
            replay_reference_ids=replay_ids,
            rollback_reference_ids=rollback_ids,
            unsupported_state_ids=unsupported_ids,
            prohibited_state_ids=prohibited_ids,
            deterministic_order=index,
        )
        for index, (relationship_id, relationship_type, source_id, target_id, purpose) in enumerate(
            relationship_specs,
            start=1,
        )
    )


def _default_relationship_chains(
    relationships: tuple[V38CoordinationRelationship, ...],
    replay_evidence: tuple[V38CoordinationReplayEvidence, ...],
    rollback_evidence: tuple[V38CoordinationRollbackEvidence, ...],
) -> tuple[V38CoordinationRelationshipChain, ...]:
    return (
        V38CoordinationRelationshipChain(
            chain_id="v3_8_coordination_identity_to_rollback_chain",
            chain_purpose=(
                "coordination identity to relationship continuity to provenance to "
                "explainability to replay and rollback evidence"
            ),
            relationship_ids=tuple(relationship.relationship_id for relationship in relationships),
            continuity_reference_ids=("v3_8_coordination_continuity_state",),
            provenance_lineage_ids=("v3_8_coordination_provenance_state",),
            explainability_reference_ids=("v3_8_coordination_explainability_state",),
            replay_reference_ids=tuple(evidence.replay_evidence_id for evidence in replay_evidence),
            rollback_reference_ids=tuple(evidence.rollback_evidence_id for evidence in rollback_evidence),
            deterministic_order=1,
        ),
    )


def _export_metadata(metadata: tuple[V38CoordinationMetadataEntry, ...]) -> list[dict[str, Any]]:
    return [asdict(entry) for entry in sorted(metadata, key=lambda item: item.metadata_key)]


def _export_reference(reference: V38CoordinationReference) -> dict[str, Any]:
    data = asdict(reference)
    for field_name in (
        "provenance_reference_ids",
        "continuity_reference_ids",
        "explainability_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_boundary(boundary: V38CoordinationBoundary) -> dict[str, Any]:
    data = asdict(boundary)
    for field_name in (
        "unsupported_state_ids",
        "prohibited_state_ids",
        "unknown_state_ids",
        "provenance_reference_ids",
        "explainability_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_relationship(relationship: V38CoordinationRelationship) -> dict[str, Any]:
    data = asdict(relationship)
    for field_name in (
        "continuity_reference_ids",
        "provenance_reference_ids",
        "explainability_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
        "unsupported_state_ids",
        "prohibited_state_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_relationship_chain(chain: V38CoordinationRelationshipChain) -> dict[str, Any]:
    data = asdict(chain)
    for field_name in (
        "relationship_ids",
        "continuity_reference_ids",
        "provenance_lineage_ids",
        "explainability_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_continuity_state(state: V38CoordinationContinuityState) -> dict[str, Any]:
    data = asdict(state)
    for field_name in (
        "preserved_reference_ids",
        "relationship_chain_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
        "provenance_reference_ids",
        "explainability_reference_ids",
        "deterministic_hash_references",
        "fail_visible_gap_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_provenance_state(state: V38CoordinationProvenanceState) -> dict[str, Any]:
    data = asdict(state)
    for field_name in (
        "lineage_reference_ids",
        "prior_phase_reference_ids",
        "continuity_reference_ids",
        "explainability_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_explainability_state(state: V38CoordinationExplainabilityState) -> dict[str, Any]:
    data = asdict(state)
    for field_name in (
        "visibility_chain_ids",
        "unsupported_state_ids",
        "prohibited_state_ids",
        "unknown_state_ids",
        "provenance_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_integrity_state(state: V38CoordinationIntegrityState) -> dict[str, Any]:
    data = asdict(state)
    for field_name in (
        "unsupported_state_ids",
        "prohibited_state_ids",
        "unknown_state_ids",
        "execution_boundary_violation_ids",
        "provenance_reference_ids",
        "explainability_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_replay_evidence(evidence: V38CoordinationReplayEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evidence_reference_ids",
        "deterministic_hash_references",
        "continuity_reference_ids",
        "provenance_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_rollback_evidence(evidence: V38CoordinationRollbackEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "rollback_reference_ids",
        "deterministic_hash_references",
        "continuity_reference_ids",
        "provenance_reference_ids",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def _export_visibility_state(
    state: V38CoordinationUnsupportedState | V38CoordinationProhibitedState | V38CoordinationUnknownState,
) -> dict[str, Any]:
    data = asdict(state)
    data["provenance_reference_ids"] = _sorted_entries(data["provenance_reference_ids"])
    return data
