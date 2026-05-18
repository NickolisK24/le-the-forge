"""Diagnostics for v4.3 orchestration transition visibility.

Diagnostics expose transition identity, source/target-state visibility,
relationship validity, continuity, explainability, and explicit non-execution
and non-activation boundaries. They do not execute transitions, progress state,
repair, infer, authorize, mutate, route, traverse, schedule, dispatch,
coordinate runtime behavior, integrate with planners, or consume production
state.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .orchestration_transition_hashing import (
    hash_orchestration_transition_visibility,
    hash_transition_diagnostic,
    hash_transition_explainability,
    hash_transition_record,
    hash_transition_relationship,
)
from .orchestration_transition_models import (
    FAIL_VISIBLE_TRANSITION_STATES,
    PROHIBITED_TRANSITION_CLASSIFICATIONS,
    TRANSITION_RELATIONSHIP_TARGET_TYPES,
    TRANSITION_RELATIONSHIP_TYPES,
    TRANSITION_STATE_BLOCKED,
    TRANSITION_STATE_CONFLICTING,
    TRANSITION_STATE_PROHIBITED,
    TRANSITION_STATE_STALE,
    TRANSITION_STATE_UNSUPPORTED,
    TRANSITION_STATES,
    UNSUPPORTED_TRANSITION_CLASSIFICATIONS,
    OrchestrationTransitionVisibility,
    TransitionRecord,
    default_orchestration_transition_visibility,
)
from .orchestration_transition_serialization import serialize_orchestration_transition_visibility


TRANSITION_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "transition_execution_enabled",
    "orchestration_execution_enabled",
    "state_machine_execution_enabled",
    "runtime_execution_enabled",
    "orchestration_activation_enabled",
    "state_progression_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "transition_authorization_enabled",
    "readiness_approval_enabled",
    "transition_dispatch_enabled",
    "operational_coordination_enabled",
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
    "hidden_transition_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "transition_engine_enabled",
    "orchestration_runtime_enabled",
    "executable_state_machine_enabled",
    "orchestration_dispatcher_enabled",
    "operational_capability_enabled",
    "policy_enforcement_enabled",
    "executable",
    "activation_capable",
    "planner_integrated",
    "production_consuming",
    "operationally_routable",
    "schedulable",
    "routable",
    "traversable",
    "execution_enabled",
    "authorization_enabled",
    "mutation_enabled",
    "activation_enabled",
)


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def count_transition_states(transitions: tuple[TransitionRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in TRANSITION_STATES}
    counts["invalid"] = 0
    for transition in transitions:
        if transition.support_state in counts:
            counts[transition.support_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_transition_ids(transitions: tuple[TransitionRecord, ...]) -> tuple[str, ...]:
    return tuple(
        transition.transition_id
        for transition in transitions
        if transition.support_state in FAIL_VISIBLE_TRANSITION_STATES and transition.fail_visible
    )


def aggregate_prohibited_transitions(visibility: OrchestrationTransitionVisibility) -> tuple[str, ...]:
    transition_ids = tuple(
        transition.transition_id
        for transition in visibility.transitions
        if transition.support_state == TRANSITION_STATE_PROHIBITED
        or transition.transition_classification in PROHIBITED_TRANSITION_CLASSIFICATIONS
    )
    return tuple(sorted(set(transition_ids + visibility.support_state_visibility.prohibited_transition_ids)))


def aggregate_unsupported_transitions(visibility: OrchestrationTransitionVisibility) -> tuple[str, ...]:
    transition_ids = tuple(
        transition.transition_id
        for transition in visibility.transitions
        if transition.support_state == TRANSITION_STATE_UNSUPPORTED
        or transition.transition_classification in UNSUPPORTED_TRANSITION_CLASSIFICATIONS
    )
    return tuple(sorted(set(transition_ids + visibility.support_state_visibility.unsupported_transition_ids)))


def aggregate_blocked_transitions(visibility: OrchestrationTransitionVisibility) -> tuple[str, ...]:
    transition_ids = tuple(
        transition.transition_id
        for transition in visibility.transitions
        if transition.support_state == TRANSITION_STATE_BLOCKED
    )
    return tuple(sorted(set(transition_ids + visibility.support_state_visibility.blocked_transition_ids)))


def aggregate_stale_transitions(visibility: OrchestrationTransitionVisibility) -> tuple[str, ...]:
    transition_ids = tuple(
        transition.transition_id
        for transition in visibility.transitions
        if transition.support_state == TRANSITION_STATE_STALE
    )
    return tuple(sorted(set(transition_ids + visibility.support_state_visibility.stale_transition_ids)))


def aggregate_conflicting_transitions(visibility: OrchestrationTransitionVisibility) -> tuple[str, ...]:
    transition_ids = tuple(
        transition.transition_id
        for transition in visibility.transitions
        if transition.support_state == TRANSITION_STATE_CONFLICTING
    )
    return tuple(sorted(set(transition_ids + visibility.support_state_visibility.conflicting_transition_ids)))


def transition_visibility_flags(visibility: OrchestrationTransitionVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        visibility,
        visibility.identity,
        visibility.metadata,
        visibility.support_state_visibility,
        *visibility.transitions,
        *visibility.relationships,
        *visibility.continuity_metadata,
        *visibility.diagnostics,
        *visibility.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in TRANSITION_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_transition_visibility_flags(visibility: OrchestrationTransitionVisibility) -> dict[str, bool]:
    return {key: value for key, value in transition_visibility_flags(visibility).items() if value}


def transition_visibility_identity_key(visibility: OrchestrationTransitionVisibility) -> str:
    identity = visibility.identity
    return "|".join(
        (
            identity.schema_version,
            identity.transition_set_id,
            identity.transition_set_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
            identity.source_capability_reference,
            identity.source_capability_hash_reference,
            identity.source_policy_reference,
            identity.source_policy_hash_reference,
            identity.governance_reference,
        )
    )


def transition_visibilities_equal(
    left: OrchestrationTransitionVisibility,
    right: OrchestrationTransitionVisibility,
) -> bool:
    return serialize_orchestration_transition_visibility(left) == serialize_orchestration_transition_visibility(
        right
    )


def _transition_has_operational_flags(transition: TransitionRecord) -> bool:
    return (
        transition.executable
        or transition.activation_capable
        or transition.state_progression_enabled
        or transition.planner_integrated
        or transition.production_consuming
        or transition.operationally_routable
        or transition.schedulable
        or transition.transition_execution_enabled
        or transition.orchestration_execution_enabled
        or transition.runtime_execution_enabled
        or transition.orchestration_activation_enabled
        or transition.routing_execution_enabled
        or transition.traversal_execution_enabled
        or transition.scheduling_execution_enabled
        or transition.sequencing_execution_enabled
        or transition.dependency_resolution_enabled
        or transition.transition_authorization_enabled
        or transition.readiness_approval_enabled
        or transition.dispatch_enabled
        or transition.operational_coordination_enabled
        or transition.planner_integration_enabled
        or transition.production_consumption_enabled
    )


def enabled_transition_execution_count(visibility: OrchestrationTransitionVisibility) -> int:
    root_enabled = int(
        visibility.transition_execution_enabled
        or visibility.state_machine_execution_enabled
        or visibility.state_progression_enabled
        or visibility.transition_engine_enabled
        or visibility.executable_state_machine_enabled
        or visibility.orchestration_dispatcher_enabled
    )
    transition_enabled = sum(1 for transition in visibility.transitions if _transition_has_operational_flags(transition))
    relationship_enabled = sum(
        1
        for relationship in visibility.relationships
        if relationship.executable
        or relationship.transition_execution_enabled
        or relationship.state_progression_enabled
        or relationship.orchestration_execution_enabled
        or relationship.runtime_execution_enabled
        or relationship.dispatch_enabled
    )
    return root_enabled + transition_enabled + relationship_enabled


def enabled_operational_capability_count(visibility: OrchestrationTransitionVisibility) -> int:
    root_enabled = int(
        visibility.operational_capability_enabled
        or visibility.orchestration_execution_enabled
        or visibility.runtime_execution_enabled
        or visibility.orchestration_activation_enabled
        or visibility.routing_execution_enabled
        or visibility.traversal_execution_enabled
        or visibility.scheduling_execution_enabled
        or visibility.sequencing_execution_enabled
        or visibility.dependency_resolution_enabled
        or visibility.transition_dispatch_enabled
        or visibility.operational_coordination_enabled
        or visibility.runtime_mutation_enabled
        or visibility.operational_mutation_enabled
        or visibility.planner_integration_enabled
        or visibility.production_consumption_enabled
        or visibility.orchestration_runtime_enabled
    )
    transition_enabled = sum(1 for transition in visibility.transitions if _transition_has_operational_flags(transition))
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
    return root_enabled + transition_enabled + relationship_enabled


def enabled_policy_enforcement_count(visibility: OrchestrationTransitionVisibility) -> int:
    return int(
        visibility.policy_enforcement_enabled
        or visibility.transition_authorization_enabled
        or visibility.readiness_approval_enabled
        or any(transition.transition_authorization_enabled for transition in visibility.transitions)
        or any(relationship.transition_authorization_enabled for relationship in visibility.relationships)
    )


def validate_transition_identity(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    fields = {
        "transition_set_id": visibility.identity.transition_set_id,
        "transition_set_version": visibility.identity.transition_set_version,
        "transition_set_classification": visibility.identity.transition_set_classification,
        "source_manifest_reference": visibility.identity.source_manifest_reference,
        "source_manifest_hash_reference": visibility.identity.source_manifest_hash_reference,
        "source_topology_reference": visibility.identity.source_topology_reference,
        "source_topology_hash_reference": visibility.identity.source_topology_hash_reference,
        "source_capability_reference": visibility.identity.source_capability_reference,
        "source_capability_hash_reference": visibility.identity.source_capability_hash_reference,
        "source_policy_reference": visibility.identity.source_policy_reference,
        "source_policy_hash_reference": visibility.identity.source_policy_hash_reference,
        "schema_version": visibility.identity.schema_version,
        "governance_reference": visibility.identity.governance_reference,
        "transition_boundary_reference": visibility.identity.transition_boundary_reference,
        "transition_policy_reference": visibility.identity.transition_policy_reference,
        "lineage_reference": visibility.identity.lineage_reference,
        "provenance_reference": visibility.identity.provenance_reference,
        "continuity_reference": visibility.identity.continuity_reference,
        "diagnostics_reference": visibility.identity.diagnostics_reference,
        "explainability_reference": visibility.identity.explainability_reference,
        "non_execution_reference": visibility.identity.non_execution_reference,
        "non_activation_reference": visibility.identity.non_activation_reference,
    }
    missing_fields = tuple(sorted(key for key, value in fields.items() if not value))
    return {
        "valid": len(missing_fields) == 0,
        "missing_identity_fields": missing_fields,
        "identity_key": transition_visibility_identity_key(visibility),
        "transition_set_id": visibility.identity.transition_set_id,
        "schema_version": visibility.identity.schema_version,
        "descriptive_only": visibility.identity.descriptive_only,
        "non_executable": visibility.identity.non_executable,
        "non_activating": visibility.identity.non_activating,
    }


def validate_transition_support_visibility(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    transition_ids = tuple(transition.transition_id for transition in visibility.transitions)
    duplicate_transition_ids = _duplicates(transition_ids)
    missing_transition_ids = tuple(
        sorted(transition.transition_name for transition in visibility.transitions if not transition.transition_id)
    )
    invalid_state_transition_ids = tuple(
        sorted(
            transition.transition_id
            for transition in visibility.transitions
            if transition.support_state not in TRANSITION_STATES
        )
    )
    hidden_transition_ids = tuple(sorted(transition.transition_id for transition in visibility.transitions if transition.hidden))
    prohibited_ids = aggregate_prohibited_transitions(visibility)
    unsupported_ids = aggregate_unsupported_transitions(visibility)
    blocked_ids = aggregate_blocked_transitions(visibility)
    stale_ids = aggregate_stale_transitions(visibility)
    conflicting_ids = aggregate_conflicting_transitions(visibility)
    return {
        "valid": (
            len(duplicate_transition_ids) == 0
            and len(missing_transition_ids) == 0
            and len(invalid_state_transition_ids) == 0
            and len(hidden_transition_ids) == 0
            and enabled_transition_execution_count(visibility) == 0
            and enabled_operational_capability_count(visibility) == 0
            and enabled_policy_enforcement_count(visibility) == 0
        ),
        "duplicate_transition_ids": duplicate_transition_ids,
        "missing_transition_ids": missing_transition_ids,
        "invalid_state_transition_ids": invalid_state_transition_ids,
        "hidden_transition_ids": hidden_transition_ids,
        "hidden_count": len(hidden_transition_ids),
        "prohibited_transitions_visible": len(prohibited_ids) > 0,
        "unsupported_transitions_visible": len(unsupported_ids) > 0,
        "blocked_transitions_visible": len(blocked_ids) > 0,
        "stale_transitions_visible": len(stale_ids) > 0,
        "conflicting_transitions_visible": len(conflicting_ids) > 0,
        "prohibited_transition_ids": prohibited_ids,
        "unsupported_transition_ids": unsupported_ids,
        "blocked_transition_ids": blocked_ids,
        "stale_transition_ids": stale_ids,
        "conflicting_transition_ids": conflicting_ids,
        "unknown_transition_ids": visibility.support_state_visibility.unknown_transition_ids,
        "fail_visible_transition_ids": fail_visible_transition_ids(visibility.transitions),
        "state_counts": count_transition_states(visibility.transitions),
        "enabled_transition_execution_count": enabled_transition_execution_count(visibility),
        "enabled_operational_capability_count": enabled_operational_capability_count(visibility),
        "enabled_policy_enforcement_count": enabled_policy_enforcement_count(visibility),
    }


def validate_transition_state_visibility(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    missing_source_state_ids = tuple(
        sorted(transition.transition_id for transition in visibility.transitions if not transition.source_state_id)
    )
    missing_target_state_ids = tuple(
        sorted(transition.transition_id for transition in visibility.transitions if not transition.target_state_id)
    )
    missing_source_state_classifications = tuple(
        sorted(
            transition.transition_id
            for transition in visibility.transitions
            if not transition.source_state_classification
        )
    )
    missing_target_state_classifications = tuple(
        sorted(
            transition.transition_id
            for transition in visibility.transitions
            if not transition.target_state_classification
        )
    )
    self_referential_transition_ids = tuple(
        sorted(
            transition.transition_id
            for transition in visibility.transitions
            if transition.source_state_id and transition.source_state_id == transition.target_state_id
        )
    )
    invalid_source_to_target_count = (
        len(missing_source_state_ids)
        + len(missing_target_state_ids)
        + len(missing_source_state_classifications)
        + len(missing_target_state_classifications)
        + len(self_referential_transition_ids)
    )
    return {
        "valid": invalid_source_to_target_count == 0,
        "missing_source_state_ids": missing_source_state_ids,
        "missing_target_state_ids": missing_target_state_ids,
        "missing_source_state_classifications": missing_source_state_classifications,
        "missing_target_state_classifications": missing_target_state_classifications,
        "self_referential_transition_ids": self_referential_transition_ids,
        "invalid_source_to_target_count": invalid_source_to_target_count,
    }


def validate_transition_metadata(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    metadata = visibility.metadata
    missing_metadata_fields = tuple(
        sorted(
            key
            for key, value in {
                "governance_metadata_reference": metadata.governance_metadata_reference,
                "transition_boundary_metadata_reference": metadata.transition_boundary_metadata_reference,
                "transition_policy_metadata_reference": metadata.transition_policy_metadata_reference,
                "continuity_metadata_reference": metadata.continuity_metadata_reference,
                "provenance_metadata_reference": metadata.provenance_metadata_reference,
                "lineage_metadata_reference": metadata.lineage_metadata_reference,
                "diagnostics_metadata_reference": metadata.diagnostics_metadata_reference,
                "explainability_metadata_reference": metadata.explainability_metadata_reference,
                "non_execution_metadata_reference": metadata.non_execution_metadata_reference,
                "non_activation_metadata_reference": metadata.non_activation_metadata_reference,
            }.items()
            if not value
        )
    )
    return {
        "valid": len(missing_metadata_fields) == 0,
        "missing_metadata_fields": missing_metadata_fields,
        "governance_metadata_present": bool(metadata.governance_metadata_reference),
        "transition_boundary_metadata_present": bool(metadata.transition_boundary_metadata_reference),
        "transition_policy_metadata_present": bool(metadata.transition_policy_metadata_reference),
        "continuity_metadata_present": bool(metadata.continuity_metadata_reference),
        "provenance_metadata_present": bool(metadata.provenance_metadata_reference),
        "lineage_metadata_present": bool(metadata.lineage_metadata_reference),
        "diagnostics_metadata_present": bool(metadata.diagnostics_metadata_reference),
        "explainability_metadata_present": bool(metadata.explainability_metadata_reference),
        "non_execution_metadata_present": bool(metadata.non_execution_metadata_reference),
        "non_activation_metadata_present": bool(metadata.non_activation_metadata_reference),
    }


def validate_transition_relationships(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    transition_ids = {transition.transition_id for transition in visibility.transitions}
    relationship_ids = tuple(relationship.relationship_id for relationship in visibility.relationships)
    duplicate_relationship_ids = _duplicates(relationship_ids)
    invalid_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type not in TRANSITION_RELATIONSHIP_TYPES
        )
    )
    unknown_transition_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.source_transition_id not in transition_ids
        )
    )
    valid_references = {
        "manifest": {visibility.identity.source_manifest_reference},
        "topology": {visibility.identity.source_topology_reference},
        "capability": {visibility.identity.source_capability_reference},
        "policy": {visibility.identity.source_policy_reference},
        "boundary": {visibility.identity.transition_boundary_reference},
    }
    invalid_target_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.target_reference_type
            != TRANSITION_RELATIONSHIP_TARGET_TYPES.get(
                relationship.relationship_type,
                relationship.target_reference_type,
            )
        )
    )
    invalid_target_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type in TRANSITION_RELATIONSHIP_TARGET_TYPES
            and relationship.target_reference_id
            not in valid_references[
                TRANSITION_RELATIONSHIP_TARGET_TYPES[relationship.relationship_type]
            ]
        )
    )
    invalid_policy_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "transition_to_policy"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_capability_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "transition_to_capability"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_boundary_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "transition_to_boundary"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_topology_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "transition_to_topology"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_manifest_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "transition_to_manifest"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    operational_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.executable
            or relationship.activation_capable
            or relationship.state_progression_enabled
            or relationship.routable
            or relationship.traversable
            or relationship.schedulable
            or relationship.planner_integrated
            or relationship.production_consuming
            or relationship.transition_execution_enabled
            or relationship.orchestration_execution_enabled
            or relationship.runtime_execution_enabled
            or relationship.orchestration_activation_enabled
            or relationship.routing_execution_enabled
            or relationship.traversal_execution_enabled
            or relationship.scheduling_execution_enabled
            or relationship.sequencing_execution_enabled
            or relationship.dependency_resolution_enabled
            or relationship.transition_authorization_enabled
            or relationship.readiness_approval_enabled
            or relationship.dispatch_enabled
            or relationship.operational_coordination_enabled
            or relationship.planner_integration_enabled
            or relationship.production_consumption_enabled
        )
    )
    invalid_relationship_count = (
        len(duplicate_relationship_ids)
        + len(invalid_type_relationship_ids)
        + len(unknown_transition_relationship_ids)
        + len(invalid_target_type_relationship_ids)
        + len(invalid_target_relationship_ids)
        + len(operational_relationship_ids)
    )
    return {
        "valid": invalid_relationship_count == 0,
        "duplicate_relationship_ids": duplicate_relationship_ids,
        "invalid_type_relationship_ids": invalid_type_relationship_ids,
        "unknown_transition_relationship_ids": unknown_transition_relationship_ids,
        "invalid_target_type_relationship_ids": invalid_target_type_relationship_ids,
        "invalid_target_relationship_ids": invalid_target_relationship_ids,
        "invalid_policy_relationship_ids": invalid_policy_relationship_ids,
        "invalid_capability_relationship_ids": invalid_capability_relationship_ids,
        "invalid_boundary_relationship_ids": invalid_boundary_relationship_ids,
        "invalid_topology_relationship_ids": invalid_topology_relationship_ids,
        "invalid_manifest_relationship_ids": invalid_manifest_relationship_ids,
        "operational_relationship_ids": operational_relationship_ids,
        "invalid_relationship_count": invalid_relationship_count,
    }


def validate_transition_continuity(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    transition_ids = {transition.transition_id for transition in visibility.transitions}
    relationship_ids = {relationship.relationship_id for relationship in visibility.relationships}
    source_state_ids = {transition.source_state_id for transition in visibility.transitions}
    target_state_ids = {transition.target_state_id for transition in visibility.transitions}
    missing_transition_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in transition_ids for reference in metadata.transition_references)
        )
    )
    missing_relationship_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in relationship_ids for reference in metadata.relationship_references)
        )
    )
    missing_source_state_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in source_state_ids for reference in metadata.source_state_references)
        )
    )
    missing_target_state_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in target_state_ids for reference in metadata.target_state_references)
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
            len(missing_transition_refs) == 0
            and len(missing_relationship_refs) == 0
            and len(missing_source_state_refs) == 0
            and len(missing_target_state_refs) == 0
            and replay_safe
            and rollback_safe
            and provenance_continuity
            and lineage_continuity
        ),
        "missing_transition_refs": missing_transition_refs,
        "missing_relationship_refs": missing_relationship_refs,
        "missing_source_state_refs": missing_source_state_refs,
        "missing_target_state_refs": missing_target_state_refs,
        "replay_safe": replay_safe,
        "rollback_safe": rollback_safe,
        "provenance_continuity_preserved": provenance_continuity,
        "lineage_continuity_preserved": lineage_continuity,
        "transition_continuity_visible": len(visibility.continuity_metadata) > 0,
    }


def validate_transition_explainability(visibility: OrchestrationTransitionVisibility) -> dict[str, object]:
    categories = tuple(
        sorted(summary.explanation_category for summary in visibility.explainability_summaries)
    )
    required_categories = (
        "prohibited_transition",
        "unsupported_transition",
        "blocked_transition",
        "stale_transition",
        "conflicting_transition",
        "transition_execution_unavailable",
        "orchestration_activation_unavailable",
        "state_progression_unavailable",
        "planner_integration_unavailable",
        "production_consumption_unavailable",
        "governance_constraints_exist",
        "operational_orchestration_prohibited",
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
            if summary.transition_execution_enabled
            or summary.orchestration_activation_enabled
            or summary.authorization_enabled
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


def validate_transition_non_execution_and_non_activation(
    visibility: OrchestrationTransitionVisibility,
) -> dict[str, object]:
    enabled_flags = enabled_transition_visibility_flags(visibility)
    transition_count = enabled_transition_execution_count(visibility)
    operational_count = enabled_operational_capability_count(visibility)
    policy_count = enabled_policy_enforcement_count(visibility)
    return {
        "valid": (
            len(enabled_flags) == 0
            and transition_count == 0
            and operational_count == 0
            and policy_count == 0
            and visibility.non_executable
            and visibility.non_activating
            and visibility.descriptive_only
        ),
        "enabled_transition_flags": enabled_flags,
        "enabled_transition_execution_count": transition_count,
        "enabled_operational_capability_count": operational_count,
        "enabled_policy_enforcement_count": policy_count,
        "non_executable": visibility.non_executable,
        "non_activating": visibility.non_activating,
        "descriptive_only": visibility.descriptive_only,
        "transition_execution_disabled": not visibility.transition_execution_enabled,
        "orchestration_execution_disabled": not visibility.orchestration_execution_enabled,
        "state_machine_execution_disabled": not visibility.state_machine_execution_enabled,
        "runtime_execution_disabled": not visibility.runtime_execution_enabled,
        "orchestration_activation_disabled": not visibility.orchestration_activation_enabled,
        "state_progression_disabled": not visibility.state_progression_enabled,
        "routing_execution_disabled": not visibility.routing_execution_enabled,
        "traversal_execution_disabled": not visibility.traversal_execution_enabled,
        "scheduling_execution_disabled": not visibility.scheduling_execution_enabled,
        "sequencing_execution_disabled": not visibility.sequencing_execution_enabled,
        "dependency_resolution_disabled": not visibility.dependency_resolution_enabled,
        "transition_authorization_disabled": not visibility.transition_authorization_enabled,
        "readiness_approval_disabled": not visibility.readiness_approval_enabled,
        "transition_dispatch_disabled": not visibility.transition_dispatch_enabled,
        "operational_coordination_disabled": not visibility.operational_coordination_enabled,
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
        "hidden_transition_pathway_absent": not visibility.hidden_transition_pathway_enabled,
        "implicit_operational_authorization_absent": (
            not visibility.implicit_operational_authorization_enabled
        ),
        "transition_engine_absent": not visibility.transition_engine_enabled,
        "orchestration_runtime_absent": not visibility.orchestration_runtime_enabled,
        "executable_state_machine_absent": not visibility.executable_state_machine_enabled,
        "orchestration_dispatcher_absent": not visibility.orchestration_dispatcher_enabled,
        "policy_enforcement_disabled": not visibility.policy_enforcement_enabled,
    }


def build_transition_visibility_diagnostics(
    visibility: OrchestrationTransitionVisibility | None = None,
) -> dict[str, Any]:
    source = visibility or default_orchestration_transition_visibility()
    identity = validate_transition_identity(source)
    support = validate_transition_support_visibility(source)
    states = validate_transition_state_visibility(source)
    metadata = validate_transition_metadata(source)
    relationships = validate_transition_relationships(source)
    continuity = validate_transition_continuity(source)
    explainability = validate_transition_explainability(source)
    non_execution = validate_transition_non_execution_and_non_activation(source)
    enabled_flags = enabled_transition_visibility_flags(source)
    return {
        "transition_visibility_hash": hash_orchestration_transition_visibility(source),
        "transition_hashes": [hash_transition_record(transition) for transition in source.transitions],
        "relationship_hashes": [
            hash_transition_relationship(relationship) for relationship in source.relationships
        ],
        "diagnostic_hashes": [hash_transition_diagnostic(diagnostic) for diagnostic in source.diagnostics],
        "explainability_hashes": [
            hash_transition_explainability(summary) for summary in source.explainability_summaries
        ],
        "identity_validation": identity,
        "support_visibility_validation": support,
        "state_visibility_validation": states,
        "metadata_validation": metadata,
        "relationship_validation": relationships,
        "continuity_validation": continuity,
        "explainability_validation": explainability,
        "non_execution_and_non_activation_validation": non_execution,
        "enabled_transition_count": len(enabled_flags),
        "enabled_transition_flags": enabled_flags,
        "enabled_transition_execution_count": enabled_transition_execution_count(source),
        "enabled_operational_capability_count": enabled_operational_capability_count(source),
        "enabled_policy_enforcement_count": enabled_policy_enforcement_count(source),
        "prohibited_transition_ids": aggregate_prohibited_transitions(source),
        "unsupported_transition_ids": aggregate_unsupported_transitions(source),
        "blocked_transition_ids": aggregate_blocked_transitions(source),
        "stale_transition_ids": aggregate_stale_transitions(source),
        "conflicting_transition_ids": aggregate_conflicting_transitions(source),
        "unknown_transition_ids": source.support_state_visibility.unknown_transition_ids,
        "invalid_source_to_target_count": states["invalid_source_to_target_count"],
        "invalid_relationship_count": relationships["invalid_relationship_count"],
        "diagnostic_categories": tuple(sorted(diagnostic.diagnostic_category for diagnostic in source.diagnostics)),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "fail_visible_warning_count": sum(
            1 for diagnostic in source.diagnostics if diagnostic.fail_visible and diagnostic.severity == "warning"
        ),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "execution_absent": all(not diagnostic.execution_enabled for diagnostic in source.diagnostics),
        "repair_absent": all(not diagnostic.repair_enabled for diagnostic in source.diagnostics),
        "inference_absent": all(not diagnostic.inference_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(not diagnostic.authorization_enabled for diagnostic in source.diagnostics),
        "mutation_absent": all(not diagnostic.mutation_enabled for diagnostic in source.diagnostics),
        "activation_absent": all(not diagnostic.activation_enabled for diagnostic in source.diagnostics),
    }
