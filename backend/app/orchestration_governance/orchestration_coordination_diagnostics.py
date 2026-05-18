"""Diagnostics for v4.3 orchestration coordination visibility.

Diagnostics expose coordination identity, participants, relationships,
continuity, explainability, and explicit non-execution and non-coordination
boundaries. They do not execute, dispatch, repair, infer, authorize, mutate,
activate, route, schedule, coordinate runtime behavior, integrate with planners,
or consume production state.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .orchestration_coordination_hashing import (
    hash_coordination_diagnostic,
    hash_coordination_explainability,
    hash_coordination_participant,
    hash_coordination_record,
    hash_coordination_relationship,
    hash_orchestration_coordination_visibility,
)
from .orchestration_coordination_models import (
    COORDINATION_RELATIONSHIP_TARGET_TYPES,
    COORDINATION_RELATIONSHIP_TYPES,
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_CONFLICTING,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_UNSUPPORTED,
    COORDINATION_STATES,
    COORDINATION_TARGET_TYPES,
    FAIL_VISIBLE_COORDINATION_STATES,
    PROHIBITED_COORDINATION_CLASSIFICATIONS,
    UNSUPPORTED_COORDINATION_CLASSIFICATIONS,
    CoordinationRecord,
    OrchestrationCoordinationVisibility,
    default_orchestration_coordination_visibility,
)
from .orchestration_coordination_serialization import serialize_orchestration_coordination_visibility


COORDINATION_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "coordination_execution_enabled",
    "orchestration_execution_enabled",
    "operational_coordination_enabled",
    "runtime_coordination_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_activation_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "state_machine_execution_enabled",
    "transition_execution_enabled",
    "coordination_authorization_enabled",
    "readiness_approval_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "planning_engine_enabled",
    "decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_coordination_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "orchestration_coordination_engine_enabled",
    "dispatcher_enabled",
    "runtime_coordinator_enabled",
    "operational_state_machine_enabled",
    "operational_capability_enabled",
    "policy_enforcement_enabled",
    "executable",
    "dispatch_capable",
    "activation_capable",
    "planner_integrated",
    "production_consuming",
    "operationally_routable",
    "schedulable",
    "routable",
    "traversable",
    "execution_enabled",
    "dispatch_enabled",
    "authorization_enabled",
    "mutation_enabled",
)


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def count_coordination_states(coordinations: tuple[CoordinationRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in COORDINATION_STATES}
    counts["invalid"] = 0
    for coordination in coordinations:
        if coordination.support_state in counts:
            counts[coordination.support_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_coordination_ids(coordinations: tuple[CoordinationRecord, ...]) -> tuple[str, ...]:
    return tuple(
        coordination.coordination_id
        for coordination in coordinations
        if coordination.support_state in FAIL_VISIBLE_COORDINATION_STATES and coordination.fail_visible
    )


def aggregate_prohibited_coordinations(visibility: OrchestrationCoordinationVisibility) -> tuple[str, ...]:
    coordination_ids = tuple(
        coordination.coordination_id
        for coordination in visibility.coordinations
        if coordination.support_state == COORDINATION_STATE_PROHIBITED
        or coordination.coordination_classification in PROHIBITED_COORDINATION_CLASSIFICATIONS
    )
    return tuple(
        sorted(set(coordination_ids + visibility.support_state_visibility.prohibited_coordination_ids))
    )


def aggregate_unsupported_coordinations(visibility: OrchestrationCoordinationVisibility) -> tuple[str, ...]:
    coordination_ids = tuple(
        coordination.coordination_id
        for coordination in visibility.coordinations
        if coordination.support_state == COORDINATION_STATE_UNSUPPORTED
        or coordination.coordination_classification in UNSUPPORTED_COORDINATION_CLASSIFICATIONS
    )
    return tuple(
        sorted(set(coordination_ids + visibility.support_state_visibility.unsupported_coordination_ids))
    )


def aggregate_blocked_coordinations(visibility: OrchestrationCoordinationVisibility) -> tuple[str, ...]:
    coordination_ids = tuple(
        coordination.coordination_id
        for coordination in visibility.coordinations
        if coordination.support_state == COORDINATION_STATE_BLOCKED
    )
    return tuple(sorted(set(coordination_ids + visibility.support_state_visibility.blocked_coordination_ids)))


def aggregate_stale_coordinations(visibility: OrchestrationCoordinationVisibility) -> tuple[str, ...]:
    coordination_ids = tuple(
        coordination.coordination_id
        for coordination in visibility.coordinations
        if coordination.support_state == COORDINATION_STATE_STALE
    )
    return tuple(sorted(set(coordination_ids + visibility.support_state_visibility.stale_coordination_ids)))


def aggregate_conflicting_coordinations(visibility: OrchestrationCoordinationVisibility) -> tuple[str, ...]:
    coordination_ids = tuple(
        coordination.coordination_id
        for coordination in visibility.coordinations
        if coordination.support_state == COORDINATION_STATE_CONFLICTING
    )
    return tuple(
        sorted(set(coordination_ids + visibility.support_state_visibility.conflicting_coordination_ids))
    )


def coordination_visibility_flags(visibility: OrchestrationCoordinationVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        visibility,
        visibility.identity,
        visibility.metadata,
        visibility.support_state_visibility,
        *visibility.coordinations,
        *visibility.participants,
        *visibility.relationships,
        *visibility.continuity_metadata,
        *visibility.diagnostics,
        *visibility.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in COORDINATION_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_visibility_flags(visibility: OrchestrationCoordinationVisibility) -> dict[str, bool]:
    return {key: value for key, value in coordination_visibility_flags(visibility).items() if value}


def coordination_visibility_identity_key(visibility: OrchestrationCoordinationVisibility) -> str:
    identity = visibility.identity
    return "|".join(
        (
            identity.schema_version,
            identity.coordination_set_id,
            identity.coordination_set_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
            identity.source_capability_reference,
            identity.source_capability_hash_reference,
            identity.source_policy_reference,
            identity.source_policy_hash_reference,
            identity.source_transition_reference,
            identity.source_transition_hash_reference,
            identity.governance_reference,
        )
    )


def coordination_visibilities_equal(
    left: OrchestrationCoordinationVisibility,
    right: OrchestrationCoordinationVisibility,
) -> bool:
    return serialize_orchestration_coordination_visibility(left) == serialize_orchestration_coordination_visibility(
        right
    )


def _coordination_has_operational_flags(coordination: CoordinationRecord) -> bool:
    return (
        coordination.executable
        or coordination.dispatch_capable
        or coordination.activation_capable
        or coordination.planner_integrated
        or coordination.production_consuming
        or coordination.operationally_routable
        or coordination.schedulable
        or coordination.coordination_execution_enabled
        or coordination.orchestration_execution_enabled
        or coordination.operational_coordination_enabled
        or coordination.runtime_coordination_enabled
        or coordination.orchestration_dispatch_enabled
        or coordination.orchestration_activation_enabled
        or coordination.routing_execution_enabled
        or coordination.traversal_execution_enabled
        or coordination.scheduling_execution_enabled
        or coordination.sequencing_execution_enabled
        or coordination.dependency_resolution_enabled
        or coordination.state_machine_execution_enabled
        or coordination.transition_execution_enabled
        or coordination.coordination_authorization_enabled
        or coordination.readiness_approval_enabled
        or coordination.planner_integration_enabled
        or coordination.production_consumption_enabled
    )


def enabled_coordination_execution_count(visibility: OrchestrationCoordinationVisibility) -> int:
    root_enabled = int(
        visibility.coordination_execution_enabled
        or visibility.operational_coordination_enabled
        or visibility.runtime_coordination_enabled
        or visibility.orchestration_dispatch_enabled
        or visibility.orchestration_coordination_engine_enabled
        or visibility.dispatcher_enabled
        or visibility.runtime_coordinator_enabled
        or visibility.operational_state_machine_enabled
    )
    coordination_enabled = sum(
        1 for coordination in visibility.coordinations if _coordination_has_operational_flags(coordination)
    )
    relationship_enabled = sum(
        1
        for relationship in visibility.relationships
        if relationship.executable
        or relationship.dispatch_capable
        or relationship.coordination_execution_enabled
        or relationship.operational_coordination_enabled
        or relationship.runtime_coordination_enabled
        or relationship.orchestration_dispatch_enabled
    )
    return root_enabled + coordination_enabled + relationship_enabled


def enabled_transition_execution_count(visibility: OrchestrationCoordinationVisibility) -> int:
    return int(
        visibility.transition_execution_enabled
        or any(coordination.transition_execution_enabled for coordination in visibility.coordinations)
        or any(relationship.transition_execution_enabled for relationship in visibility.relationships)
    )


def enabled_policy_enforcement_count(visibility: OrchestrationCoordinationVisibility) -> int:
    return int(
        visibility.policy_enforcement_enabled
        or visibility.coordination_authorization_enabled
        or visibility.readiness_approval_enabled
        or any(coordination.coordination_authorization_enabled for coordination in visibility.coordinations)
        or any(relationship.coordination_authorization_enabled for relationship in visibility.relationships)
    )


def enabled_operational_capability_count(visibility: OrchestrationCoordinationVisibility) -> int:
    root_enabled = int(
        visibility.operational_capability_enabled
        or visibility.orchestration_execution_enabled
        or visibility.orchestration_activation_enabled
        or visibility.routing_execution_enabled
        or visibility.traversal_execution_enabled
        or visibility.scheduling_execution_enabled
        or visibility.sequencing_execution_enabled
        or visibility.dependency_resolution_enabled
        or visibility.state_machine_execution_enabled
        or visibility.runtime_mutation_enabled
        or visibility.operational_mutation_enabled
        or visibility.planner_integration_enabled
        or visibility.production_consumption_enabled
    )
    coordination_enabled = sum(
        1 for coordination in visibility.coordinations if _coordination_has_operational_flags(coordination)
    )
    relationship_enabled = sum(
        1
        for relationship in visibility.relationships
        if relationship.activation_capable
        or relationship.routable
        or relationship.traversable
        or relationship.schedulable
        or relationship.planner_integrated
        or relationship.production_consuming
        or relationship.orchestration_activation_enabled
        or relationship.routing_execution_enabled
        or relationship.traversal_execution_enabled
        or relationship.scheduling_execution_enabled
        or relationship.sequencing_execution_enabled
        or relationship.dependency_resolution_enabled
        or relationship.planner_integration_enabled
        or relationship.production_consumption_enabled
    )
    return root_enabled + coordination_enabled + relationship_enabled


def validate_coordination_identity(visibility: OrchestrationCoordinationVisibility) -> dict[str, object]:
    fields = {
        "coordination_set_id": visibility.identity.coordination_set_id,
        "coordination_set_version": visibility.identity.coordination_set_version,
        "coordination_set_classification": visibility.identity.coordination_set_classification,
        "source_manifest_reference": visibility.identity.source_manifest_reference,
        "source_manifest_hash_reference": visibility.identity.source_manifest_hash_reference,
        "source_topology_reference": visibility.identity.source_topology_reference,
        "source_topology_hash_reference": visibility.identity.source_topology_hash_reference,
        "source_capability_reference": visibility.identity.source_capability_reference,
        "source_capability_hash_reference": visibility.identity.source_capability_hash_reference,
        "source_policy_reference": visibility.identity.source_policy_reference,
        "source_policy_hash_reference": visibility.identity.source_policy_hash_reference,
        "source_transition_reference": visibility.identity.source_transition_reference,
        "source_transition_hash_reference": visibility.identity.source_transition_hash_reference,
        "schema_version": visibility.identity.schema_version,
        "governance_reference": visibility.identity.governance_reference,
        "coordination_boundary_reference": visibility.identity.coordination_boundary_reference,
        "coordination_policy_reference": visibility.identity.coordination_policy_reference,
        "coordination_transition_reference": visibility.identity.coordination_transition_reference,
        "lineage_reference": visibility.identity.lineage_reference,
        "provenance_reference": visibility.identity.provenance_reference,
        "continuity_reference": visibility.identity.continuity_reference,
        "diagnostics_reference": visibility.identity.diagnostics_reference,
        "explainability_reference": visibility.identity.explainability_reference,
        "non_execution_reference": visibility.identity.non_execution_reference,
        "non_coordination_reference": visibility.identity.non_coordination_reference,
    }
    missing_fields = tuple(sorted(key for key, value in fields.items() if not value))
    return {
        "valid": len(missing_fields) == 0,
        "missing_identity_fields": missing_fields,
        "identity_key": coordination_visibility_identity_key(visibility),
        "coordination_set_id": visibility.identity.coordination_set_id,
        "schema_version": visibility.identity.schema_version,
        "descriptive_only": visibility.identity.descriptive_only,
        "non_executable": visibility.identity.non_executable,
        "non_coordinating": visibility.identity.non_coordinating,
    }


def validate_coordination_support_visibility(
    visibility: OrchestrationCoordinationVisibility,
) -> dict[str, object]:
    coordination_ids = tuple(coordination.coordination_id for coordination in visibility.coordinations)
    duplicate_coordination_ids = _duplicates(coordination_ids)
    missing_coordination_ids = tuple(
        sorted(coordination.coordination_name for coordination in visibility.coordinations if not coordination.coordination_id)
    )
    invalid_state_coordination_ids = tuple(
        sorted(
            coordination.coordination_id
            for coordination in visibility.coordinations
            if coordination.support_state not in COORDINATION_STATES
        )
    )
    hidden_coordination_ids = tuple(
        sorted(coordination.coordination_id for coordination in visibility.coordinations if coordination.hidden)
    )
    prohibited_ids = aggregate_prohibited_coordinations(visibility)
    unsupported_ids = aggregate_unsupported_coordinations(visibility)
    blocked_ids = aggregate_blocked_coordinations(visibility)
    stale_ids = aggregate_stale_coordinations(visibility)
    conflicting_ids = aggregate_conflicting_coordinations(visibility)
    return {
        "valid": (
            len(duplicate_coordination_ids) == 0
            and len(missing_coordination_ids) == 0
            and len(invalid_state_coordination_ids) == 0
            and len(hidden_coordination_ids) == 0
            and enabled_coordination_execution_count(visibility) == 0
            and enabled_transition_execution_count(visibility) == 0
            and enabled_policy_enforcement_count(visibility) == 0
            and enabled_operational_capability_count(visibility) == 0
        ),
        "duplicate_coordination_ids": duplicate_coordination_ids,
        "missing_coordination_ids": missing_coordination_ids,
        "invalid_state_coordination_ids": invalid_state_coordination_ids,
        "hidden_coordination_ids": hidden_coordination_ids,
        "hidden_count": len(hidden_coordination_ids),
        "prohibited_coordinations_visible": len(prohibited_ids) > 0,
        "unsupported_coordinations_visible": len(unsupported_ids) > 0,
        "blocked_coordinations_visible": len(blocked_ids) > 0,
        "stale_coordinations_visible": len(stale_ids) > 0,
        "conflicting_coordinations_visible": len(conflicting_ids) > 0,
        "prohibited_coordination_ids": prohibited_ids,
        "unsupported_coordination_ids": unsupported_ids,
        "blocked_coordination_ids": blocked_ids,
        "stale_coordination_ids": stale_ids,
        "conflicting_coordination_ids": conflicting_ids,
        "unknown_coordination_ids": visibility.support_state_visibility.unknown_coordination_ids,
        "fail_visible_coordination_ids": fail_visible_coordination_ids(visibility.coordinations),
        "state_counts": count_coordination_states(visibility.coordinations),
        "enabled_coordination_execution_count": enabled_coordination_execution_count(visibility),
        "enabled_transition_execution_count": enabled_transition_execution_count(visibility),
        "enabled_policy_enforcement_count": enabled_policy_enforcement_count(visibility),
        "enabled_operational_capability_count": enabled_operational_capability_count(visibility),
    }


def validate_coordination_participants(visibility: OrchestrationCoordinationVisibility) -> dict[str, object]:
    coordination_ids = {coordination.coordination_id for coordination in visibility.coordinations}
    participant_ids = tuple(participant.participant_id for participant in visibility.participants)
    duplicate_participant_ids = _duplicates(participant_ids)
    missing_participant_ids = tuple(
        sorted(participant.participant_reference_id for participant in visibility.participants if not participant.participant_id)
    )
    missing_participant_references = tuple(
        sorted(participant.participant_id for participant in visibility.participants if not participant.participant_reference_id)
    )
    invalid_participant_types = tuple(
        sorted(participant.participant_id for participant in visibility.participants if participant.participant_type not in COORDINATION_TARGET_TYPES)
    )
    missing_participant_coordination_refs = tuple(
        sorted(participant.participant_id for participant in visibility.participants if not participant.coordination_ids)
    )
    unknown_coordination_refs = tuple(
        sorted(
            participant.participant_id
            for participant in visibility.participants
            if any(coordination_id not in coordination_ids for coordination_id in participant.coordination_ids)
        )
    )
    known_participant_ids = {participant.participant_id for participant in visibility.participants}
    missing_coordination_participant_refs = tuple(
        sorted(
            coordination.coordination_id
            for coordination in visibility.coordinations
            if not coordination.participant_ids
            or any(participant_id not in known_participant_ids for participant_id in coordination.participant_ids)
        )
    )
    operational_participant_ids = tuple(
        sorted(
            participant.participant_id
            for participant in visibility.participants
            if participant.executable
            or participant.dispatch_capable
            or participant.activation_capable
            or participant.planner_integrated
            or participant.production_consuming
            or participant.operationally_routable
            or participant.schedulable
        )
    )
    invalid_participant_count = (
        len(duplicate_participant_ids)
        + len(missing_participant_ids)
        + len(missing_participant_references)
        + len(invalid_participant_types)
        + len(missing_participant_coordination_refs)
        + len(unknown_coordination_refs)
        + len(missing_coordination_participant_refs)
        + len(operational_participant_ids)
    )
    return {
        "valid": invalid_participant_count == 0,
        "duplicate_participant_ids": duplicate_participant_ids,
        "missing_participant_ids": missing_participant_ids,
        "missing_participant_references": missing_participant_references,
        "invalid_participant_types": invalid_participant_types,
        "missing_participant_coordination_refs": missing_participant_coordination_refs,
        "unknown_coordination_refs": unknown_coordination_refs,
        "missing_coordination_participant_refs": missing_coordination_participant_refs,
        "operational_participant_ids": operational_participant_ids,
        "invalid_participant_count": invalid_participant_count,
    }


def validate_coordination_metadata(visibility: OrchestrationCoordinationVisibility) -> dict[str, object]:
    metadata = visibility.metadata
    missing_metadata_fields = tuple(
        sorted(
            key
            for key, value in {
                "governance_metadata_reference": metadata.governance_metadata_reference,
                "coordination_boundary_metadata_reference": metadata.coordination_boundary_metadata_reference,
                "coordination_policy_metadata_reference": metadata.coordination_policy_metadata_reference,
                "coordination_transition_metadata_reference": metadata.coordination_transition_metadata_reference,
                "continuity_metadata_reference": metadata.continuity_metadata_reference,
                "provenance_metadata_reference": metadata.provenance_metadata_reference,
                "lineage_metadata_reference": metadata.lineage_metadata_reference,
                "diagnostics_metadata_reference": metadata.diagnostics_metadata_reference,
                "explainability_metadata_reference": metadata.explainability_metadata_reference,
                "non_execution_metadata_reference": metadata.non_execution_metadata_reference,
                "non_coordination_metadata_reference": metadata.non_coordination_metadata_reference,
            }.items()
            if not value
        )
    )
    return {
        "valid": len(missing_metadata_fields) == 0,
        "missing_metadata_fields": missing_metadata_fields,
        "governance_metadata_present": bool(metadata.governance_metadata_reference),
        "coordination_boundary_metadata_present": bool(metadata.coordination_boundary_metadata_reference),
        "coordination_policy_metadata_present": bool(metadata.coordination_policy_metadata_reference),
        "coordination_transition_metadata_present": bool(metadata.coordination_transition_metadata_reference),
        "continuity_metadata_present": bool(metadata.continuity_metadata_reference),
        "provenance_metadata_present": bool(metadata.provenance_metadata_reference),
        "lineage_metadata_present": bool(metadata.lineage_metadata_reference),
        "diagnostics_metadata_present": bool(metadata.diagnostics_metadata_reference),
        "explainability_metadata_present": bool(metadata.explainability_metadata_reference),
        "non_execution_metadata_present": bool(metadata.non_execution_metadata_reference),
        "non_coordination_metadata_present": bool(metadata.non_coordination_metadata_reference),
    }


def validate_coordination_relationships(visibility: OrchestrationCoordinationVisibility) -> dict[str, object]:
    coordination_ids = {coordination.coordination_id for coordination in visibility.coordinations}
    relationship_ids = tuple(relationship.relationship_id for relationship in visibility.relationships)
    duplicate_relationship_ids = _duplicates(relationship_ids)
    invalid_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type not in COORDINATION_RELATIONSHIP_TYPES
        )
    )
    unknown_coordination_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.source_coordination_id not in coordination_ids
        )
    )
    valid_references = {
        participant.participant_type: {participant.participant_reference_id}
        for participant in visibility.participants
    }
    invalid_target_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.target_reference_type
            != COORDINATION_RELATIONSHIP_TARGET_TYPES.get(
                relationship.relationship_type,
                relationship.target_reference_type,
            )
        )
    )
    invalid_target_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type in COORDINATION_RELATIONSHIP_TARGET_TYPES
            and relationship.target_reference_id
            not in valid_references[
                COORDINATION_RELATIONSHIP_TARGET_TYPES[relationship.relationship_type]
            ]
        )
    )
    invalid_policy_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "coordination_to_policy"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_capability_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "coordination_to_capability"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_transition_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "coordination_to_transition"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_boundary_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "coordination_to_boundary"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_topology_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "coordination_to_topology"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_manifest_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "coordination_to_manifest"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    operational_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.executable
            or relationship.dispatch_capable
            or relationship.activation_capable
            or relationship.routable
            or relationship.traversable
            or relationship.schedulable
            or relationship.planner_integrated
            or relationship.production_consuming
            or relationship.coordination_execution_enabled
            or relationship.orchestration_execution_enabled
            or relationship.operational_coordination_enabled
            or relationship.runtime_coordination_enabled
            or relationship.orchestration_dispatch_enabled
            or relationship.orchestration_activation_enabled
            or relationship.routing_execution_enabled
            or relationship.traversal_execution_enabled
            or relationship.scheduling_execution_enabled
            or relationship.sequencing_execution_enabled
            or relationship.dependency_resolution_enabled
            or relationship.state_machine_execution_enabled
            or relationship.transition_execution_enabled
            or relationship.coordination_authorization_enabled
            or relationship.readiness_approval_enabled
            or relationship.planner_integration_enabled
            or relationship.production_consumption_enabled
        )
    )
    invalid_relationship_count = (
        len(duplicate_relationship_ids)
        + len(invalid_type_relationship_ids)
        + len(unknown_coordination_relationship_ids)
        + len(invalid_target_type_relationship_ids)
        + len(invalid_target_relationship_ids)
        + len(operational_relationship_ids)
    )
    return {
        "valid": invalid_relationship_count == 0,
        "duplicate_relationship_ids": duplicate_relationship_ids,
        "invalid_type_relationship_ids": invalid_type_relationship_ids,
        "unknown_coordination_relationship_ids": unknown_coordination_relationship_ids,
        "invalid_target_type_relationship_ids": invalid_target_type_relationship_ids,
        "invalid_target_relationship_ids": invalid_target_relationship_ids,
        "invalid_policy_relationship_ids": invalid_policy_relationship_ids,
        "invalid_capability_relationship_ids": invalid_capability_relationship_ids,
        "invalid_transition_relationship_ids": invalid_transition_relationship_ids,
        "invalid_boundary_relationship_ids": invalid_boundary_relationship_ids,
        "invalid_topology_relationship_ids": invalid_topology_relationship_ids,
        "invalid_manifest_relationship_ids": invalid_manifest_relationship_ids,
        "operational_relationship_ids": operational_relationship_ids,
        "invalid_relationship_count": invalid_relationship_count,
    }


def validate_coordination_continuity(visibility: OrchestrationCoordinationVisibility) -> dict[str, object]:
    coordination_ids = {coordination.coordination_id for coordination in visibility.coordinations}
    participant_ids = {participant.participant_id for participant in visibility.participants}
    relationship_ids = {relationship.relationship_id for relationship in visibility.relationships}
    missing_coordination_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in coordination_ids for reference in metadata.coordination_references)
        )
    )
    missing_participant_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in participant_ids for reference in metadata.participant_references)
        )
    )
    missing_relationship_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in relationship_ids for reference in metadata.relationship_references)
        )
    )
    replay_safe = all(metadata.replay_safe for metadata in visibility.continuity_metadata)
    rollback_safe = all(metadata.rollback_safe for metadata in visibility.continuity_metadata)
    provenance_continuity = all(
        metadata.provenance_continuity_preserved for metadata in visibility.continuity_metadata
    )
    lineage_continuity = all(metadata.lineage_continuity_preserved for metadata in visibility.continuity_metadata)
    return {
        "valid": (
            len(missing_coordination_refs) == 0
            and len(missing_participant_refs) == 0
            and len(missing_relationship_refs) == 0
            and replay_safe
            and rollback_safe
            and provenance_continuity
            and lineage_continuity
        ),
        "missing_coordination_refs": missing_coordination_refs,
        "missing_participant_refs": missing_participant_refs,
        "missing_relationship_refs": missing_relationship_refs,
        "replay_safe": replay_safe,
        "rollback_safe": rollback_safe,
        "provenance_continuity_preserved": provenance_continuity,
        "lineage_continuity_preserved": lineage_continuity,
        "coordination_continuity_visible": len(visibility.continuity_metadata) > 0,
    }


def validate_coordination_explainability(visibility: OrchestrationCoordinationVisibility) -> dict[str, object]:
    categories = tuple(
        sorted(summary.explanation_category for summary in visibility.explainability_summaries)
    )
    required_categories = (
        "prohibited_coordination",
        "unsupported_coordination",
        "blocked_coordination",
        "stale_coordination",
        "conflicting_coordination",
        "operational_coordination_unavailable",
        "orchestration_dispatch_unavailable",
        "orchestration_activation_unavailable",
        "planner_integration_unavailable",
        "production_consumption_unavailable",
        "governance_constraints_exist",
        "runtime_coordination_prohibited",
    )
    missing_categories = tuple(sorted(category for category in required_categories if category not in categories))
    non_descriptive = tuple(
        sorted(
            summary.explanation_id
            for summary in visibility.explainability_summaries
            if not summary.descriptive_only
        )
    )
    enabled_explanations = tuple(
        sorted(
            summary.explanation_id
            for summary in visibility.explainability_summaries
            if summary.coordination_execution_enabled
            or summary.operational_coordination_enabled
            or summary.orchestration_dispatch_enabled
        )
    )
    return {
        "valid": len(missing_categories) == 0 and len(non_descriptive) == 0 and len(enabled_explanations) == 0,
        "explainability_categories": categories,
        "missing_explainability_categories": missing_categories,
        "non_descriptive_explanations": non_descriptive,
        "enabled_explanations": enabled_explanations,
        "deterministic": all(summary.deterministic for summary in visibility.explainability_summaries),
        "replay_safe": all(summary.replay_safe for summary in visibility.explainability_summaries),
        "rollback_safe": all(summary.rollback_safe for summary in visibility.explainability_summaries),
    }


def validate_coordination_non_execution_and_non_coordination(
    visibility: OrchestrationCoordinationVisibility,
) -> dict[str, object]:
    enabled_flags = enabled_coordination_visibility_flags(visibility)
    coordination_count = enabled_coordination_execution_count(visibility)
    transition_count = enabled_transition_execution_count(visibility)
    policy_count = enabled_policy_enforcement_count(visibility)
    operational_count = enabled_operational_capability_count(visibility)
    return {
        "valid": (
            len(enabled_flags) == 0
            and coordination_count == 0
            and transition_count == 0
            and policy_count == 0
            and operational_count == 0
            and visibility.non_executable
            and visibility.non_coordinating
            and visibility.descriptive_only
        ),
        "enabled_coordination_flags": enabled_flags,
        "enabled_coordination_execution_count": coordination_count,
        "enabled_transition_execution_count": transition_count,
        "enabled_policy_enforcement_count": policy_count,
        "enabled_operational_capability_count": operational_count,
        "non_executable": visibility.non_executable,
        "non_coordinating": visibility.non_coordinating,
        "descriptive_only": visibility.descriptive_only,
        "coordination_execution_disabled": not visibility.coordination_execution_enabled,
        "orchestration_execution_disabled": not visibility.orchestration_execution_enabled,
        "operational_coordination_disabled": not visibility.operational_coordination_enabled,
        "runtime_coordination_disabled": not visibility.runtime_coordination_enabled,
        "orchestration_dispatch_disabled": not visibility.orchestration_dispatch_enabled,
        "orchestration_activation_disabled": not visibility.orchestration_activation_enabled,
        "routing_execution_disabled": not visibility.routing_execution_enabled,
        "traversal_execution_disabled": not visibility.traversal_execution_enabled,
        "scheduling_execution_disabled": not visibility.scheduling_execution_enabled,
        "sequencing_execution_disabled": not visibility.sequencing_execution_enabled,
        "dependency_resolution_disabled": not visibility.dependency_resolution_enabled,
        "state_machine_execution_disabled": not visibility.state_machine_execution_enabled,
        "transition_execution_disabled": not visibility.transition_execution_enabled,
        "coordination_authorization_disabled": not visibility.coordination_authorization_enabled,
        "readiness_approval_disabled": not visibility.readiness_approval_enabled,
        "runtime_mutation_disabled": not visibility.runtime_mutation_enabled,
        "operational_mutation_disabled": not visibility.operational_mutation_enabled,
        "planner_integration_disabled": not visibility.planner_integration_enabled,
        "production_consumption_disabled": not visibility.production_consumption_enabled,
        "remediation_disabled": not visibility.remediation_enabled,
        "repair_disabled": not visibility.repair_enabled,
        "inference_disabled": not visibility.inference_enabled,
        "recommendation_disabled": not visibility.recommendation_enabled,
        "ranking_disabled": not visibility.ranking_enabled,
        "scoring_disabled": not visibility.scoring_enabled,
        "selection_disabled": not visibility.selection_enabled,
        "optimization_disabled": not visibility.optimization_enabled,
        "planning_engine_absent": not visibility.planning_engine_enabled,
        "decision_engine_absent": not visibility.decision_engine_enabled,
        "hidden_coordination_pathway_absent": not visibility.hidden_coordination_pathway_enabled,
        "implicit_operational_authorization_absent": (
            not visibility.implicit_operational_authorization_enabled
        ),
        "orchestration_coordination_engine_absent": not visibility.orchestration_coordination_engine_enabled,
        "dispatcher_absent": not visibility.dispatcher_enabled,
        "runtime_coordinator_absent": not visibility.runtime_coordinator_enabled,
        "operational_state_machine_absent": not visibility.operational_state_machine_enabled,
        "policy_enforcement_disabled": not visibility.policy_enforcement_enabled,
    }


def build_coordination_visibility_diagnostics(
    visibility: OrchestrationCoordinationVisibility | None = None,
) -> dict[str, Any]:
    source = visibility or default_orchestration_coordination_visibility()
    identity = validate_coordination_identity(source)
    support = validate_coordination_support_visibility(source)
    participants = validate_coordination_participants(source)
    metadata = validate_coordination_metadata(source)
    relationships = validate_coordination_relationships(source)
    continuity = validate_coordination_continuity(source)
    explainability = validate_coordination_explainability(source)
    non_execution = validate_coordination_non_execution_and_non_coordination(source)
    enabled_flags = enabled_coordination_visibility_flags(source)
    return {
        "coordination_visibility_hash": hash_orchestration_coordination_visibility(source),
        "coordination_hashes": [
            hash_coordination_record(coordination) for coordination in source.coordinations
        ],
        "participant_hashes": [
            hash_coordination_participant(participant) for participant in source.participants
        ],
        "relationship_hashes": [
            hash_coordination_relationship(relationship) for relationship in source.relationships
        ],
        "diagnostic_hashes": [hash_coordination_diagnostic(diagnostic) for diagnostic in source.diagnostics],
        "explainability_hashes": [
            hash_coordination_explainability(summary) for summary in source.explainability_summaries
        ],
        "identity_validation": identity,
        "support_visibility_validation": support,
        "participant_validation": participants,
        "metadata_validation": metadata,
        "relationship_validation": relationships,
        "continuity_validation": continuity,
        "explainability_validation": explainability,
        "non_execution_and_non_coordination_validation": non_execution,
        "enabled_coordination_count": len(enabled_flags),
        "enabled_coordination_flags": enabled_flags,
        "enabled_coordination_execution_count": enabled_coordination_execution_count(source),
        "enabled_transition_execution_count": enabled_transition_execution_count(source),
        "enabled_policy_enforcement_count": enabled_policy_enforcement_count(source),
        "enabled_operational_capability_count": enabled_operational_capability_count(source),
        "prohibited_coordination_ids": aggregate_prohibited_coordinations(source),
        "unsupported_coordination_ids": aggregate_unsupported_coordinations(source),
        "blocked_coordination_ids": aggregate_blocked_coordinations(source),
        "stale_coordination_ids": aggregate_stale_coordinations(source),
        "conflicting_coordination_ids": aggregate_conflicting_coordinations(source),
        "unknown_coordination_ids": source.support_state_visibility.unknown_coordination_ids,
        "invalid_participant_count": participants["invalid_participant_count"],
        "invalid_relationship_count": relationships["invalid_relationship_count"],
        "diagnostic_categories": tuple(sorted(diagnostic.diagnostic_category for diagnostic in source.diagnostics)),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "fail_visible_warning_count": sum(
            1 for diagnostic in source.diagnostics if diagnostic.fail_visible and diagnostic.severity == "warning"
        ),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "execution_absent": all(not diagnostic.execution_enabled for diagnostic in source.diagnostics),
        "dispatch_absent": all(not diagnostic.dispatch_enabled for diagnostic in source.diagnostics),
        "repair_absent": all(not diagnostic.repair_enabled for diagnostic in source.diagnostics),
        "inference_absent": all(not diagnostic.inference_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(not diagnostic.authorization_enabled for diagnostic in source.diagnostics),
        "mutation_absent": all(not diagnostic.mutation_enabled for diagnostic in source.diagnostics),
    }
