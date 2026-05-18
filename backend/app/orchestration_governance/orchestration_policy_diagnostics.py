"""Diagnostics for v4.3 orchestration policy visibility.

Diagnostics expose policy identity, target relationships, support-state
visibility, metadata continuity, explainability, and explicit non-enforcement
and non-execution boundaries. They do not enforce policies, repair metadata,
infer authorization, approve readiness, route, traverse, schedule, execute,
dispatch, coordinate runtime behavior, consume production state, or mutate
state.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .orchestration_policy_hashing import (
    hash_orchestration_policy_visibility,
    hash_policy_diagnostic,
    hash_policy_explainability,
    hash_policy_record,
    hash_policy_relationship,
    hash_policy_target,
)
from .orchestration_policy_models import (
    FAIL_VISIBLE_POLICY_STATES,
    POLICY_RELATIONSHIP_TARGET_TYPES,
    POLICY_RELATIONSHIP_TYPES,
    POLICY_STATE_BLOCKED,
    POLICY_STATE_CONFLICTING,
    POLICY_STATE_PROHIBITED,
    POLICY_STATE_STALE,
    POLICY_STATE_UNSUPPORTED,
    POLICY_STATES,
    POLICY_TARGET_TYPES,
    PROHIBITED_POLICY_CLASSIFICATIONS,
    UNSUPPORTED_POLICY_CLASSIFICATIONS,
    OrchestrationPolicyVisibility,
    PolicyRecord,
    default_orchestration_policy_visibility,
)
from .orchestration_policy_serialization import serialize_orchestration_policy_visibility


POLICY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "policy_enforcement_enabled",
    "policy_enforcement_execution_enabled",
    "orchestration_execution_enabled",
    "runtime_execution_enabled",
    "policy_driven_routing_enabled",
    "policy_driven_traversal_enabled",
    "policy_driven_scheduling_enabled",
    "policy_driven_sequencing_enabled",
    "policy_driven_dependency_resolution_enabled",
    "policy_driven_activation_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "operational_policy_mutation_enabled",
    "runtime_mutation_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "dispatch_enabled",
    "operational_coordination_enabled",
    "state_machine_enabled",
    "hidden_enforcement_path_enabled",
    "implicit_operational_authorization_enabled",
    "policy_engine_execution_enabled",
    "orchestration_engine_enabled",
    "authorization_engine_enabled",
    "activation_pathway_enabled",
    "operational_capability_enabled",
    "executable",
    "enforceable",
    "authorizing",
    "activation_capable",
    "routable",
    "traversable",
    "schedulable",
    "planner_integrated",
    "production_consuming",
    "authorization_enabled",
    "operational_mutation_enabled",
)


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def count_policy_states(policies: tuple[PolicyRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in POLICY_STATES}
    counts["invalid"] = 0
    for policy in policies:
        if policy.support_state in counts:
            counts[policy.support_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_policy_ids(policies: tuple[PolicyRecord, ...]) -> tuple[str, ...]:
    return tuple(
        policy.policy_id
        for policy in policies
        if policy.support_state in FAIL_VISIBLE_POLICY_STATES and policy.fail_visible
    )


def aggregate_prohibited_policies(visibility: OrchestrationPolicyVisibility) -> tuple[str, ...]:
    policy_ids = tuple(
        policy.policy_id
        for policy in visibility.policies
        if policy.support_state == POLICY_STATE_PROHIBITED
        or policy.policy_classification in PROHIBITED_POLICY_CLASSIFICATIONS
    )
    return tuple(sorted(set(policy_ids + visibility.support_state_visibility.prohibited_policy_ids)))


def aggregate_unsupported_policies(visibility: OrchestrationPolicyVisibility) -> tuple[str, ...]:
    policy_ids = tuple(
        policy.policy_id
        for policy in visibility.policies
        if policy.support_state == POLICY_STATE_UNSUPPORTED
        or policy.policy_classification in UNSUPPORTED_POLICY_CLASSIFICATIONS
    )
    return tuple(sorted(set(policy_ids + visibility.support_state_visibility.unsupported_policy_ids)))


def aggregate_blocked_policies(visibility: OrchestrationPolicyVisibility) -> tuple[str, ...]:
    policy_ids = tuple(
        policy.policy_id for policy in visibility.policies if policy.support_state == POLICY_STATE_BLOCKED
    )
    return tuple(sorted(set(policy_ids + visibility.support_state_visibility.blocked_policy_ids)))


def aggregate_stale_policies(visibility: OrchestrationPolicyVisibility) -> tuple[str, ...]:
    policy_ids = tuple(
        policy.policy_id for policy in visibility.policies if policy.support_state == POLICY_STATE_STALE
    )
    return tuple(sorted(set(policy_ids + visibility.support_state_visibility.stale_policy_ids)))


def aggregate_conflicting_policies(visibility: OrchestrationPolicyVisibility) -> tuple[str, ...]:
    policy_ids = tuple(
        policy.policy_id for policy in visibility.policies if policy.support_state == POLICY_STATE_CONFLICTING
    )
    return tuple(sorted(set(policy_ids + visibility.support_state_visibility.conflicting_policy_ids)))


def policy_visibility_flags(visibility: OrchestrationPolicyVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        visibility,
        visibility.identity,
        visibility.metadata,
        visibility.support_state_visibility,
        *visibility.policies,
        *visibility.targets,
        *visibility.relationships,
        *visibility.continuity_metadata,
        *visibility.diagnostics,
        *visibility.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in POLICY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_policy_visibility_flags(visibility: OrchestrationPolicyVisibility) -> dict[str, bool]:
    return {key: value for key, value in policy_visibility_flags(visibility).items() if value}


def policy_visibility_identity_key(visibility: OrchestrationPolicyVisibility) -> str:
    identity = visibility.identity
    return "|".join(
        (
            identity.schema_version,
            identity.policy_set_id,
            identity.policy_set_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
            identity.source_capability_reference,
            identity.source_capability_hash_reference,
            identity.governance_reference,
        )
    )


def policy_visibilities_equal(
    left: OrchestrationPolicyVisibility,
    right: OrchestrationPolicyVisibility,
) -> bool:
    return serialize_orchestration_policy_visibility(left) == serialize_orchestration_policy_visibility(right)


def _policy_has_enforcement_enabled(policy: PolicyRecord) -> bool:
    return (
        policy.executable
        or policy.enforceable
        or policy.authorizing
        or policy.activation_capable
        or policy.planner_integrated
        or policy.production_consuming
        or policy.policy_enforcement_execution_enabled
        or policy.orchestration_execution_enabled
        or policy.runtime_execution_enabled
        or policy.policy_driven_routing_enabled
        or policy.policy_driven_traversal_enabled
        or policy.policy_driven_scheduling_enabled
        or policy.policy_driven_sequencing_enabled
        or policy.policy_driven_dependency_resolution_enabled
        or policy.policy_driven_activation_enabled
        or policy.orchestration_authorization_enabled
        or policy.readiness_approval_enabled
        or policy.planner_integration_enabled
        or policy.production_consumption_enabled
    )


def enabled_policy_enforcement_count(visibility: OrchestrationPolicyVisibility) -> int:
    root_enabled = int(
        visibility.policy_enforcement_enabled
        or visibility.policy_enforcement_execution_enabled
        or visibility.policy_engine_execution_enabled
        or visibility.authorization_engine_enabled
        or visibility.orchestration_authorization_enabled
        or visibility.readiness_approval_enabled
    )
    policy_enabled = sum(1 for policy in visibility.policies if _policy_has_enforcement_enabled(policy))
    relationship_enabled = sum(
        1
        for relationship in visibility.relationships
        if relationship.enforceable
        or relationship.authorizing
        or relationship.activation_capable
        or relationship.policy_enforcement_execution_enabled
        or relationship.orchestration_authorization_enabled
        or relationship.readiness_approval_enabled
    )
    return root_enabled + policy_enabled + relationship_enabled


def enabled_operational_capability_count(visibility: OrchestrationPolicyVisibility) -> int:
    root_enabled = int(
        visibility.operational_capability_enabled
        or visibility.orchestration_execution_enabled
        or visibility.runtime_execution_enabled
        or visibility.policy_driven_routing_enabled
        or visibility.policy_driven_traversal_enabled
        or visibility.policy_driven_scheduling_enabled
        or visibility.policy_driven_sequencing_enabled
        or visibility.policy_driven_dependency_resolution_enabled
        or visibility.policy_driven_activation_enabled
        or visibility.operational_policy_mutation_enabled
        or visibility.runtime_mutation_enabled
        or visibility.planner_integration_enabled
        or visibility.production_consumption_enabled
        or visibility.dispatch_enabled
        or visibility.operational_coordination_enabled
        or visibility.state_machine_enabled
        or visibility.orchestration_engine_enabled
        or visibility.activation_pathway_enabled
    )
    policy_enabled = sum(1 for policy in visibility.policies if _policy_has_enforcement_enabled(policy))
    relationship_enabled = sum(
        1
        for relationship in visibility.relationships
        if relationship.executable
        or relationship.routable
        or relationship.traversable
        or relationship.schedulable
        or relationship.planner_integrated
        or relationship.production_consuming
        or relationship.orchestration_execution_enabled
        or relationship.runtime_execution_enabled
        or relationship.policy_driven_routing_enabled
        or relationship.policy_driven_traversal_enabled
        or relationship.policy_driven_scheduling_enabled
        or relationship.policy_driven_sequencing_enabled
        or relationship.policy_driven_dependency_resolution_enabled
        or relationship.policy_driven_activation_enabled
        or relationship.planner_integration_enabled
        or relationship.production_consumption_enabled
    )
    return root_enabled + policy_enabled + relationship_enabled


def validate_policy_identity(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    fields = {
        "policy_set_id": visibility.identity.policy_set_id,
        "policy_set_version": visibility.identity.policy_set_version,
        "policy_set_classification": visibility.identity.policy_set_classification,
        "source_manifest_reference": visibility.identity.source_manifest_reference,
        "source_manifest_hash_reference": visibility.identity.source_manifest_hash_reference,
        "source_topology_reference": visibility.identity.source_topology_reference,
        "source_topology_hash_reference": visibility.identity.source_topology_hash_reference,
        "source_capability_reference": visibility.identity.source_capability_reference,
        "source_capability_hash_reference": visibility.identity.source_capability_hash_reference,
        "schema_version": visibility.identity.schema_version,
        "governance_reference": visibility.identity.governance_reference,
        "policy_scope_reference": visibility.identity.policy_scope_reference,
        "policy_target_reference": visibility.identity.policy_target_reference,
        "lineage_reference": visibility.identity.lineage_reference,
        "provenance_reference": visibility.identity.provenance_reference,
        "continuity_reference": visibility.identity.continuity_reference,
        "diagnostics_reference": visibility.identity.diagnostics_reference,
        "explainability_reference": visibility.identity.explainability_reference,
        "non_enforcement_reference": visibility.identity.non_enforcement_reference,
        "non_execution_reference": visibility.identity.non_execution_reference,
    }
    missing_fields = tuple(sorted(key for key, value in fields.items() if not value))
    return {
        "valid": len(missing_fields) == 0,
        "missing_identity_fields": missing_fields,
        "identity_key": policy_visibility_identity_key(visibility),
        "policy_set_id": visibility.identity.policy_set_id,
        "schema_version": visibility.identity.schema_version,
        "descriptive_only": visibility.identity.descriptive_only,
        "non_enforceable": visibility.identity.non_enforceable,
        "non_executable": visibility.identity.non_executable,
    }


def validate_policy_support_visibility(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    policy_ids = tuple(policy.policy_id for policy in visibility.policies)
    duplicate_policy_ids = _duplicates(policy_ids)
    missing_policy_ids = tuple(sorted(policy.policy_name for policy in visibility.policies if not policy.policy_id))
    invalid_state_policy_ids = tuple(
        sorted(policy.policy_id for policy in visibility.policies if policy.support_state not in POLICY_STATES)
    )
    hidden_policy_ids = tuple(sorted(policy.policy_id for policy in visibility.policies if policy.hidden))
    prohibited_ids = aggregate_prohibited_policies(visibility)
    unsupported_ids = aggregate_unsupported_policies(visibility)
    blocked_ids = aggregate_blocked_policies(visibility)
    stale_ids = aggregate_stale_policies(visibility)
    conflicting_ids = aggregate_conflicting_policies(visibility)
    enabled_flags = enabled_policy_visibility_flags(visibility)
    enforcement_count = enabled_policy_enforcement_count(visibility)
    operational_count = enabled_operational_capability_count(visibility)
    return {
        "valid": (
            len(duplicate_policy_ids) == 0
            and len(missing_policy_ids) == 0
            and len(invalid_state_policy_ids) == 0
            and len(hidden_policy_ids) == 0
            and enforcement_count == 0
            and operational_count == 0
        ),
        "duplicate_policy_ids": duplicate_policy_ids,
        "missing_policy_ids": missing_policy_ids,
        "invalid_state_policy_ids": invalid_state_policy_ids,
        "hidden_policy_ids": hidden_policy_ids,
        "hidden_count": len(hidden_policy_ids),
        "prohibited_policies_visible": len(prohibited_ids) > 0,
        "unsupported_policies_visible": len(unsupported_ids) > 0,
        "blocked_policies_visible": len(blocked_ids) > 0,
        "stale_policies_visible": len(stale_ids) > 0,
        "conflicting_policies_visible": len(conflicting_ids) > 0,
        "prohibited_policy_ids": prohibited_ids,
        "unsupported_policy_ids": unsupported_ids,
        "blocked_policy_ids": blocked_ids,
        "stale_policy_ids": stale_ids,
        "conflicting_policy_ids": conflicting_ids,
        "unknown_policy_ids": visibility.support_state_visibility.unknown_policy_ids,
        "fail_visible_policy_ids": fail_visible_policy_ids(visibility.policies),
        "state_counts": count_policy_states(visibility.policies),
        "enabled_policy_flags": enabled_flags,
        "enabled_policy_enforcement_count": enforcement_count,
        "enabled_operational_capability_count": operational_count,
    }


def validate_policy_targets(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    policy_ids = {policy.policy_id for policy in visibility.policies}
    target_ids = tuple(target.target_id for target in visibility.targets)
    duplicate_target_ids = _duplicates(target_ids)
    missing_target_ids = tuple(sorted(target.target_reference_id for target in visibility.targets if not target.target_id))
    missing_target_references = tuple(sorted(target.target_id for target in visibility.targets if not target.target_reference_id))
    missing_target_policy_refs = tuple(sorted(target.target_id for target in visibility.targets if not target.policy_ids))
    invalid_target_types = tuple(
        sorted(target.target_id for target in visibility.targets if target.target_type not in POLICY_TARGET_TYPES)
    )
    unknown_policy_target_refs = tuple(
        sorted(
            target.target_id
            for target in visibility.targets
            if any(policy_id not in policy_ids for policy_id in target.policy_ids)
        )
    )
    known_target_ids = {target.target_id for target in visibility.targets}
    missing_policy_target_ids = tuple(
        sorted(
            policy.policy_id
            for policy in visibility.policies
            if not policy.target_ids or any(target_id not in known_target_ids for target_id in policy.target_ids)
        )
    )
    operational_target_ids = tuple(
        sorted(
            target.target_id
            for target in visibility.targets
            if target.executable
            or target.enforceable
            or target.authorizing
            or target.activation_capable
            or target.planner_integrated
            or target.production_consuming
        )
    )
    invalid_target_count = (
        len(duplicate_target_ids)
        + len(missing_target_ids)
        + len(missing_target_references)
        + len(missing_target_policy_refs)
        + len(invalid_target_types)
        + len(unknown_policy_target_refs)
        + len(missing_policy_target_ids)
        + len(operational_target_ids)
    )
    return {
        "valid": invalid_target_count == 0,
        "duplicate_target_ids": duplicate_target_ids,
        "missing_target_ids": missing_target_ids,
        "missing_target_references": missing_target_references,
        "missing_target_policy_refs": missing_target_policy_refs,
        "invalid_target_types": invalid_target_types,
        "unknown_policy_target_refs": unknown_policy_target_refs,
        "missing_policy_target_ids": missing_policy_target_ids,
        "operational_target_ids": operational_target_ids,
        "invalid_target_count": invalid_target_count,
    }


def validate_policy_metadata(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    metadata = visibility.metadata
    missing_metadata_fields = tuple(
        sorted(
            key
            for key, value in {
                "governance_metadata_reference": metadata.governance_metadata_reference,
                "policy_scope_metadata_reference": metadata.policy_scope_metadata_reference,
                "policy_target_metadata_reference": metadata.policy_target_metadata_reference,
                "continuity_metadata_reference": metadata.continuity_metadata_reference,
                "provenance_metadata_reference": metadata.provenance_metadata_reference,
                "lineage_metadata_reference": metadata.lineage_metadata_reference,
                "diagnostics_metadata_reference": metadata.diagnostics_metadata_reference,
                "explainability_metadata_reference": metadata.explainability_metadata_reference,
                "non_enforcement_metadata_reference": metadata.non_enforcement_metadata_reference,
                "non_execution_metadata_reference": metadata.non_execution_metadata_reference,
            }.items()
            if not value
        )
    )
    return {
        "valid": len(missing_metadata_fields) == 0,
        "missing_metadata_fields": missing_metadata_fields,
        "governance_metadata_present": bool(metadata.governance_metadata_reference),
        "policy_scope_metadata_present": bool(metadata.policy_scope_metadata_reference),
        "policy_target_metadata_present": bool(metadata.policy_target_metadata_reference),
        "continuity_metadata_present": bool(metadata.continuity_metadata_reference),
        "provenance_metadata_present": bool(metadata.provenance_metadata_reference),
        "lineage_metadata_present": bool(metadata.lineage_metadata_reference),
        "diagnostics_metadata_present": bool(metadata.diagnostics_metadata_reference),
        "explainability_metadata_present": bool(metadata.explainability_metadata_reference),
        "non_enforcement_metadata_present": bool(metadata.non_enforcement_metadata_reference),
        "non_execution_metadata_present": bool(metadata.non_execution_metadata_reference),
    }


def validate_policy_relationships(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    policy_ids = {policy.policy_id for policy in visibility.policies}
    relationship_ids = tuple(relationship.relationship_id for relationship in visibility.relationships)
    duplicate_relationship_ids = _duplicates(relationship_ids)
    invalid_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type not in POLICY_RELATIONSHIP_TYPES
        )
    )
    unknown_policy_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.source_policy_id not in policy_ids
        )
    )
    target_references_by_type = {
        target_type: {
            target.target_reference_id for target in visibility.targets if target.target_type == target_type
        }
        for target_type in POLICY_TARGET_TYPES
    }
    invalid_target_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.target_reference_type
            != POLICY_RELATIONSHIP_TARGET_TYPES.get(relationship.relationship_type, relationship.target_reference_type)
        )
    )
    invalid_target_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type in POLICY_RELATIONSHIP_TARGET_TYPES
            and relationship.target_reference_id
            not in target_references_by_type[POLICY_RELATIONSHIP_TARGET_TYPES[relationship.relationship_type]]
        )
    )
    invalid_manifest_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "policy_to_manifest"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_topology_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "policy_to_topology"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_capability_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "policy_to_capability"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    invalid_boundary_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "policy_to_boundary"
            and relationship.relationship_id in invalid_target_relationship_ids
        )
    )
    operational_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.executable
            or relationship.enforceable
            or relationship.authorizing
            or relationship.activation_capable
            or relationship.routable
            or relationship.traversable
            or relationship.schedulable
            or relationship.planner_integrated
            or relationship.production_consuming
            or relationship.policy_enforcement_execution_enabled
            or relationship.orchestration_execution_enabled
            or relationship.runtime_execution_enabled
            or relationship.policy_driven_routing_enabled
            or relationship.policy_driven_traversal_enabled
            or relationship.policy_driven_scheduling_enabled
            or relationship.policy_driven_sequencing_enabled
            or relationship.policy_driven_dependency_resolution_enabled
            or relationship.policy_driven_activation_enabled
            or relationship.orchestration_authorization_enabled
            or relationship.readiness_approval_enabled
            or relationship.planner_integration_enabled
            or relationship.production_consumption_enabled
        )
    )
    invalid_relationship_count = (
        len(duplicate_relationship_ids)
        + len(invalid_type_relationship_ids)
        + len(unknown_policy_relationship_ids)
        + len(invalid_target_type_relationship_ids)
        + len(invalid_target_relationship_ids)
        + len(operational_relationship_ids)
    )
    return {
        "valid": invalid_relationship_count == 0,
        "duplicate_relationship_ids": duplicate_relationship_ids,
        "invalid_type_relationship_ids": invalid_type_relationship_ids,
        "unknown_policy_relationship_ids": unknown_policy_relationship_ids,
        "invalid_target_type_relationship_ids": invalid_target_type_relationship_ids,
        "invalid_target_relationship_ids": invalid_target_relationship_ids,
        "invalid_manifest_relationship_ids": invalid_manifest_relationship_ids,
        "invalid_topology_relationship_ids": invalid_topology_relationship_ids,
        "invalid_capability_relationship_ids": invalid_capability_relationship_ids,
        "invalid_boundary_relationship_ids": invalid_boundary_relationship_ids,
        "operational_relationship_ids": operational_relationship_ids,
        "invalid_relationship_count": invalid_relationship_count,
    }


def validate_policy_continuity(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    policy_ids = {policy.policy_id for policy in visibility.policies}
    target_ids = {target.target_id for target in visibility.targets}
    relationship_ids = {relationship.relationship_id for relationship in visibility.relationships}
    missing_continuity_ids = tuple(
        sorted(metadata.continuity_id for metadata in visibility.continuity_metadata if not metadata.continuity_id)
    )
    missing_policy_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in policy_ids for reference in metadata.policy_references)
        )
    )
    missing_target_refs = tuple(
        sorted(
            metadata.continuity_id
            for metadata in visibility.continuity_metadata
            if any(reference not in target_ids for reference in metadata.target_references)
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
            len(missing_continuity_ids) == 0
            and len(missing_policy_refs) == 0
            and len(missing_target_refs) == 0
            and len(missing_relationship_refs) == 0
            and replay_safe
            and rollback_safe
            and provenance_continuity
            and lineage_continuity
        ),
        "missing_continuity_ids": missing_continuity_ids,
        "missing_policy_refs": missing_policy_refs,
        "missing_target_refs": missing_target_refs,
        "missing_relationship_refs": missing_relationship_refs,
        "replay_safe": replay_safe,
        "rollback_safe": rollback_safe,
        "provenance_continuity_preserved": provenance_continuity,
        "lineage_continuity_preserved": lineage_continuity,
        "policy_continuity_visible": len(visibility.continuity_metadata) > 0,
    }


def validate_policy_explainability(visibility: OrchestrationPolicyVisibility) -> dict[str, object]:
    categories = tuple(sorted(summary.explanation_category for summary in visibility.explainability_summaries))
    required_categories = (
        "prohibited_policy",
        "unsupported_policy",
        "blocked_policy",
        "stale_policy",
        "conflicting_policy",
        "policy_enforcement_unavailable",
        "authorization_unavailable",
        "activation_unavailable",
        "execution_unavailable",
        "planner_integration_unavailable",
        "production_consumption_unavailable",
        "governance_constraints_exist",
    )
    missing_categories = tuple(sorted(category for category in required_categories if category not in categories))
    non_descriptive = tuple(
        sorted(summary.explanation_id for summary in visibility.explainability_summaries if not summary.descriptive_only)
    )
    enabled_explanations = tuple(
        sorted(
            summary.explanation_id
            for summary in visibility.explainability_summaries
            if summary.policy_enforcement_enabled
            or summary.authorization_enabled
            or summary.orchestration_execution_enabled
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


def validate_policy_non_execution_and_non_enforcement(
    visibility: OrchestrationPolicyVisibility,
) -> dict[str, object]:
    enabled_flags = enabled_policy_visibility_flags(visibility)
    enforcement_count = enabled_policy_enforcement_count(visibility)
    operational_count = enabled_operational_capability_count(visibility)
    return {
        "valid": (
            len(enabled_flags) == 0
            and enforcement_count == 0
            and operational_count == 0
            and visibility.non_enforceable
            and visibility.non_executable
            and visibility.descriptive_only
        ),
        "enabled_policy_flags": enabled_flags,
        "enabled_policy_enforcement_count": enforcement_count,
        "enabled_operational_capability_count": operational_count,
        "non_enforceable": visibility.non_enforceable,
        "non_executable": visibility.non_executable,
        "descriptive_only": visibility.descriptive_only,
        "policy_enforcement_disabled": not visibility.policy_enforcement_enabled,
        "policy_enforcement_execution_disabled": not visibility.policy_enforcement_execution_enabled,
        "orchestration_execution_disabled": not visibility.orchestration_execution_enabled,
        "runtime_execution_disabled": not visibility.runtime_execution_enabled,
        "policy_driven_routing_disabled": not visibility.policy_driven_routing_enabled,
        "policy_driven_traversal_disabled": not visibility.policy_driven_traversal_enabled,
        "policy_driven_scheduling_disabled": not visibility.policy_driven_scheduling_enabled,
        "policy_driven_sequencing_disabled": not visibility.policy_driven_sequencing_enabled,
        "policy_driven_dependency_resolution_disabled": (
            not visibility.policy_driven_dependency_resolution_enabled
        ),
        "policy_driven_activation_disabled": not visibility.policy_driven_activation_enabled,
        "orchestration_authorization_disabled": not visibility.orchestration_authorization_enabled,
        "readiness_approval_disabled": not visibility.readiness_approval_enabled,
        "operational_policy_mutation_disabled": not visibility.operational_policy_mutation_enabled,
        "runtime_mutation_disabled": not visibility.runtime_mutation_enabled,
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
        "dispatch_disabled": not visibility.dispatch_enabled,
        "operational_coordination_disabled": not visibility.operational_coordination_enabled,
        "state_machine_absent": not visibility.state_machine_enabled,
        "hidden_enforcement_path_absent": not visibility.hidden_enforcement_path_enabled,
        "implicit_operational_authorization_absent": (
            not visibility.implicit_operational_authorization_enabled
        ),
        "policy_engine_execution_absent": not visibility.policy_engine_execution_enabled,
        "orchestration_engine_absent": not visibility.orchestration_engine_enabled,
        "authorization_engine_absent": not visibility.authorization_engine_enabled,
        "activation_pathway_absent": not visibility.activation_pathway_enabled,
    }


def build_policy_visibility_diagnostics(
    visibility: OrchestrationPolicyVisibility | None = None,
) -> dict[str, Any]:
    source = visibility or default_orchestration_policy_visibility()
    identity = validate_policy_identity(source)
    support = validate_policy_support_visibility(source)
    targets = validate_policy_targets(source)
    metadata = validate_policy_metadata(source)
    relationships = validate_policy_relationships(source)
    continuity = validate_policy_continuity(source)
    explainability = validate_policy_explainability(source)
    non_execution = validate_policy_non_execution_and_non_enforcement(source)
    enabled_flags = enabled_policy_visibility_flags(source)
    return {
        "policy_visibility_hash": hash_orchestration_policy_visibility(source),
        "policy_hashes": [hash_policy_record(policy) for policy in source.policies],
        "target_hashes": [hash_policy_target(target) for target in source.targets],
        "relationship_hashes": [hash_policy_relationship(relationship) for relationship in source.relationships],
        "diagnostic_hashes": [hash_policy_diagnostic(diagnostic) for diagnostic in source.diagnostics],
        "explainability_hashes": [
            hash_policy_explainability(summary) for summary in source.explainability_summaries
        ],
        "identity_validation": identity,
        "support_visibility_validation": support,
        "target_validation": targets,
        "metadata_validation": metadata,
        "relationship_validation": relationships,
        "continuity_validation": continuity,
        "explainability_validation": explainability,
        "non_execution_and_non_enforcement_validation": non_execution,
        "enabled_policy_count": len(enabled_flags),
        "enabled_policy_flags": enabled_flags,
        "enabled_policy_enforcement_count": enabled_policy_enforcement_count(source),
        "enabled_operational_capability_count": enabled_operational_capability_count(source),
        "prohibited_policy_ids": aggregate_prohibited_policies(source),
        "unsupported_policy_ids": aggregate_unsupported_policies(source),
        "blocked_policy_ids": aggregate_blocked_policies(source),
        "stale_policy_ids": aggregate_stale_policies(source),
        "conflicting_policy_ids": aggregate_conflicting_policies(source),
        "unknown_policy_ids": source.support_state_visibility.unknown_policy_ids,
        "invalid_target_count": targets["invalid_target_count"],
        "invalid_relationship_count": relationships["invalid_relationship_count"],
        "diagnostic_categories": tuple(sorted(diagnostic.diagnostic_category for diagnostic in source.diagnostics)),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "fail_visible_warning_count": sum(
            1 for diagnostic in source.diagnostics if diagnostic.fail_visible and diagnostic.severity == "warning"
        ),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "remediation_absent": all(not diagnostic.remediation_enabled for diagnostic in source.diagnostics),
        "repair_absent": all(not diagnostic.repair_enabled for diagnostic in source.diagnostics),
        "inference_absent": all(not diagnostic.inference_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(not diagnostic.authorization_enabled for diagnostic in source.diagnostics),
        "operational_mutation_absent": all(
            not diagnostic.operational_mutation_enabled for diagnostic in source.diagnostics
        ),
        "policy_enforcement_absent": all(
            not diagnostic.policy_enforcement_enabled for diagnostic in source.diagnostics
        ),
        "execution_absent": all(not diagnostic.orchestration_execution_enabled for diagnostic in source.diagnostics),
    }
