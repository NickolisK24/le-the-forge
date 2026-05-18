"""Diagnostics for v4.3 orchestration boundary and capability visibility.

Diagnostics expose capability identity, duplicate identifiers, boundary
metadata, relationship validity, support-state visibility, and any operational
capability flags. They do not correct, infer, authorize, activate, route,
traverse, schedule, execute, dispatch, coordinate runtime behavior, or mutate
state.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .orchestration_capability_hashing import (
    hash_capability_boundary,
    hash_capability_diagnostic,
    hash_capability_explainability,
    hash_capability_record,
    hash_capability_relationship,
    hash_orchestration_capability_visibility,
)
from .orchestration_capability_models import (
    CAPABILITY_RELATIONSHIP_TYPES,
    CAPABILITY_STATE_BLOCKED,
    CAPABILITY_STATE_CONFLICTING,
    CAPABILITY_STATE_PROHIBITED,
    CAPABILITY_STATE_STALE,
    CAPABILITY_STATE_UNSUPPORTED,
    CAPABILITY_STATES,
    FAIL_VISIBLE_CAPABILITY_STATES,
    PROHIBITED_CAPABILITY_CLASSIFICATIONS,
    UNSUPPORTED_CAPABILITY_CLASSIFICATIONS,
    CapabilityRecord,
    OrchestrationCapabilityVisibility,
    default_orchestration_capability_visibility,
)
from .orchestration_capability_serialization import serialize_orchestration_capability_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "orchestration_activation_enabled",
    "runtime_execution_enabled",
    "capability_execution_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "dependency_execution_enabled",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "operational_state_mutation_enabled",
    "runtime_mutation_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "remediation_system_enabled",
    "automatic_repair_enabled",
    "inference_system_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "planning_engine_enabled",
    "decision_system_enabled",
    "resolution_system_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "orchestration_dispatch_enabled",
    "runtime_coordination_enabled",
    "state_machine_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "operational_orchestration_engine_enabled",
    "orchestration_decision_engine_enabled",
    "executable",
    "operationally_enabled",
    "authorized",
    "schedulable",
    "routable",
    "planner_integrated",
    "traversable",
    "correction_enabled",
    "inference_enabled",
    "authorization_enabled",
    "operational_mutation_enabled",
)


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def count_capability_states(capabilities: tuple[CapabilityRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in CAPABILITY_STATES}
    counts["invalid"] = 0
    for capability in capabilities:
        if capability.support_state in counts:
            counts[capability.support_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_capability_ids(capabilities: tuple[CapabilityRecord, ...]) -> tuple[str, ...]:
    return tuple(
        capability.capability_id
        for capability in capabilities
        if capability.support_state in FAIL_VISIBLE_CAPABILITY_STATES and capability.fail_visible
    )


def aggregate_prohibited_capabilities(visibility: OrchestrationCapabilityVisibility) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_PROHIBITED
        or capability.capability_classification in PROHIBITED_CAPABILITY_CLASSIFICATIONS
    )
    return tuple(sorted(set(capability_ids + visibility.support_state_visibility.prohibited_capability_ids)))


def aggregate_unsupported_capabilities(visibility: OrchestrationCapabilityVisibility) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_UNSUPPORTED
        or capability.capability_classification in UNSUPPORTED_CAPABILITY_CLASSIFICATIONS
    )
    return tuple(sorted(set(capability_ids + visibility.support_state_visibility.unsupported_capability_ids)))


def aggregate_blocked_capabilities(visibility: OrchestrationCapabilityVisibility) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_BLOCKED
    )
    return tuple(sorted(set(capability_ids + visibility.support_state_visibility.blocked_capability_ids)))


def aggregate_stale_capabilities(visibility: OrchestrationCapabilityVisibility) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_STALE
    )
    return tuple(sorted(set(capability_ids + visibility.support_state_visibility.stale_capability_ids)))


def aggregate_conflicting_capabilities(visibility: OrchestrationCapabilityVisibility) -> tuple[str, ...]:
    capability_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_CONFLICTING
    )
    return tuple(sorted(set(capability_ids + visibility.support_state_visibility.conflicting_capability_ids)))


def capability_visibility_flags(visibility: OrchestrationCapabilityVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        visibility,
        visibility.identity,
        visibility.metadata,
        visibility.support_state_visibility,
        *visibility.capabilities,
        *visibility.boundaries,
        *visibility.relationships,
        *visibility.continuity_metadata,
        *visibility.diagnostics,
        *visibility.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_capability_visibility_flags(visibility: OrchestrationCapabilityVisibility) -> dict[str, bool]:
    return {key: value for key, value in capability_visibility_flags(visibility).items() if value}


def capability_visibility_identity_key(visibility: OrchestrationCapabilityVisibility) -> str:
    identity = visibility.identity
    return "|".join(
        (
            identity.schema_version,
            identity.capability_set_id,
            identity.capability_set_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
            identity.governance_reference,
        )
    )


def capability_visibilities_equal(
    left: OrchestrationCapabilityVisibility,
    right: OrchestrationCapabilityVisibility,
) -> bool:
    return serialize_orchestration_capability_visibility(left) == serialize_orchestration_capability_visibility(right)


def enabled_operational_capability_count(visibility: OrchestrationCapabilityVisibility) -> int:
    return sum(
        1
        for capability in visibility.capabilities
        if capability.executable
        or capability.operationally_enabled
        or capability.authorized
        or capability.schedulable
        or capability.routable
        or capability.planner_integrated
        or capability.orchestration_execution_enabled
        or capability.orchestration_activation_enabled
        or capability.runtime_execution_enabled
        or capability.capability_execution_enabled
        or capability.routing_execution_enabled
        or capability.traversal_execution_enabled
        or capability.dependency_execution_enabled
        or capability.sequencing_execution_enabled
        or capability.scheduling_execution_enabled
        or capability.operational_state_mutation_enabled
        or capability.runtime_mutation_enabled
        or capability.orchestration_authorization_enabled
        or capability.readiness_approval_enabled
        or capability.planner_integration_enabled
        or capability.production_consumption_enabled
        or capability.orchestration_dispatch_enabled
        or capability.runtime_coordination_enabled
    )


def validate_capability_identity(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    fields = {
        "capability_set_id": visibility.identity.capability_set_id,
        "capability_set_version": visibility.identity.capability_set_version,
        "capability_set_classification": visibility.identity.capability_set_classification,
        "source_manifest_reference": visibility.identity.source_manifest_reference,
        "source_manifest_hash_reference": visibility.identity.source_manifest_hash_reference,
        "source_topology_reference": visibility.identity.source_topology_reference,
        "source_topology_hash_reference": visibility.identity.source_topology_hash_reference,
        "schema_version": visibility.identity.schema_version,
        "governance_reference": visibility.identity.governance_reference,
        "operational_boundary_reference": visibility.identity.operational_boundary_reference,
        "lineage_reference": visibility.identity.lineage_reference,
        "provenance_reference": visibility.identity.provenance_reference,
        "continuity_reference": visibility.identity.continuity_reference,
        "diagnostics_reference": visibility.identity.diagnostics_reference,
        "explainability_reference": visibility.identity.explainability_reference,
        "non_execution_reference": visibility.identity.non_execution_reference,
    }
    missing_fields = tuple(sorted(key for key, value in fields.items() if not value))
    return {
        "valid": len(missing_fields) == 0,
        "missing_capability_identity_fields": missing_fields,
        "identity_key": capability_visibility_identity_key(visibility),
    }


def validate_capability_support_visibility(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    capability_ids = tuple(capability.capability_id for capability in visibility.capabilities)
    duplicate_capability_ids = _duplicates(capability_ids)
    invalid_state_ids = tuple(
        sorted(capability.capability_id for capability in visibility.capabilities if capability.support_state not in CAPABILITY_STATES)
    )
    prohibited_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_PROHIBITED
        or capability.capability_classification in PROHIBITED_CAPABILITY_CLASSIFICATIONS
    )
    unsupported_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_UNSUPPORTED
        or capability.capability_classification in UNSUPPORTED_CAPABILITY_CLASSIFICATIONS
    )
    blocked_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_BLOCKED
    )
    stale_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_STALE
    )
    conflicting_ids = tuple(
        capability.capability_id
        for capability in visibility.capabilities
        if capability.support_state == CAPABILITY_STATE_CONFLICTING
    )
    prohibited_visible = set(prohibited_ids).issubset(
        set(visibility.support_state_visibility.prohibited_capability_ids)
    )
    unsupported_visible = set(unsupported_ids).issubset(
        set(visibility.support_state_visibility.unsupported_capability_ids)
    )
    blocked_visible = set(blocked_ids).issubset(set(visibility.support_state_visibility.blocked_capability_ids))
    stale_visible = set(stale_ids).issubset(set(visibility.support_state_visibility.stale_capability_ids))
    conflicting_visible = set(conflicting_ids).issubset(
        set(visibility.support_state_visibility.conflicting_capability_ids)
    )
    prohibited_classifications_visible = set(PROHIBITED_CAPABILITY_CLASSIFICATIONS).issubset(
        set(visibility.support_state_visibility.prohibited_classifications)
    )
    unsupported_classifications_visible = set(UNSUPPORTED_CAPABILITY_CLASSIFICATIONS).issubset(
        set(visibility.support_state_visibility.unsupported_classifications)
    )
    hidden_count = sum(1 for capability in visibility.capabilities if capability.hidden)
    operational_count = enabled_operational_capability_count(visibility)
    return {
        "valid": (
            len(duplicate_capability_ids) == 0
            and len(invalid_state_ids) == 0
            and prohibited_visible
            and unsupported_visible
            and blocked_visible
            and stale_visible
            and conflicting_visible
            and prohibited_classifications_visible
            and unsupported_classifications_visible
            and hidden_count == 0
            and operational_count == 0
        ),
        "capability_state_counts": count_capability_states(visibility.capabilities),
        "duplicate_capability_ids": duplicate_capability_ids,
        "invalid_state_ids": invalid_state_ids,
        "fail_visible_capability_ids": fail_visible_capability_ids(visibility.capabilities),
        "prohibited_capability_ids": prohibited_ids,
        "unsupported_capability_ids": unsupported_ids,
        "blocked_capability_ids": blocked_ids,
        "stale_capability_ids": stale_ids,
        "conflicting_capability_ids": conflicting_ids,
        "unknown_capability_ids": visibility.support_state_visibility.unknown_capability_ids,
        "prohibited_capabilities_visible": prohibited_visible,
        "unsupported_capabilities_visible": unsupported_visible,
        "blocked_capabilities_visible": blocked_visible,
        "stale_capabilities_visible": stale_visible,
        "conflicting_capabilities_visible": conflicting_visible,
        "prohibited_classifications_visible": prohibited_classifications_visible,
        "unsupported_classifications_visible": unsupported_classifications_visible,
        "hidden_count": hidden_count,
        "enabled_operational_capability_count": operational_count,
    }


def validate_capability_metadata(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    fields = {
        "governance_boundary_metadata_reference": visibility.metadata.governance_boundary_metadata_reference,
        "operational_boundary_metadata_reference": visibility.metadata.operational_boundary_metadata_reference,
        "continuity_metadata_reference": visibility.metadata.continuity_metadata_reference,
        "provenance_metadata_reference": visibility.metadata.provenance_metadata_reference,
        "lineage_metadata_reference": visibility.metadata.lineage_metadata_reference,
        "diagnostics_metadata_reference": visibility.metadata.diagnostics_metadata_reference,
        "explainability_metadata_reference": visibility.metadata.explainability_metadata_reference,
        "non_execution_metadata_reference": visibility.metadata.non_execution_metadata_reference,
    }
    missing_fields = tuple(sorted(key for key, value in fields.items() if not value))
    capability_missing_metadata_ids = tuple(
        sorted(
            capability.capability_id
            for capability in visibility.capabilities
            if not capability.governance_metadata_reference
            or not capability.operational_boundary_metadata_reference
            or not capability.continuity_metadata_reference
            or not capability.provenance_metadata_reference
            or not capability.lineage_metadata_reference
            or not capability.diagnostics_metadata_reference
            or not capability.explainability_metadata_reference
        )
    )
    boundary_missing_metadata_ids = tuple(
        sorted(
            boundary.boundary_id
            for boundary in visibility.boundaries
            if not boundary.governance_metadata_reference
            or not boundary.operational_boundary_metadata_reference
        )
    )
    return {
        "valid": (
            len(missing_fields) == 0
            and len(capability_missing_metadata_ids) == 0
            and len(boundary_missing_metadata_ids) == 0
        ),
        "missing_metadata_fields": missing_fields,
        "capability_missing_metadata_ids": capability_missing_metadata_ids,
        "boundary_missing_metadata_ids": boundary_missing_metadata_ids,
        "governance_boundary_metadata_present": bool(visibility.metadata.governance_boundary_metadata_reference),
        "operational_boundary_metadata_present": bool(visibility.metadata.operational_boundary_metadata_reference),
        "continuity_metadata_present": bool(visibility.metadata.continuity_metadata_reference),
        "provenance_metadata_present": bool(visibility.metadata.provenance_metadata_reference),
        "lineage_metadata_present": bool(visibility.metadata.lineage_metadata_reference),
        "diagnostics_metadata_present": bool(visibility.metadata.diagnostics_metadata_reference),
        "explainability_metadata_present": bool(visibility.metadata.explainability_metadata_reference),
    }


def validate_capability_relationships(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    capability_ids = {capability.capability_id for capability in visibility.capabilities}
    boundary_ids = {boundary.boundary_id for boundary in visibility.boundaries}
    relationship_ids = tuple(relationship.relationship_id for relationship in visibility.relationships)
    duplicate_relationship_ids = _duplicates(relationship_ids)
    invalid_type_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type not in CAPABILITY_RELATIONSHIP_TYPES
        )
    )
    unknown_capability_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.source_capability_id not in capability_ids
        )
    )
    invalid_boundary_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "capability_to_boundary"
            and relationship.target_reference_id not in boundary_ids
        )
    )
    invalid_policy_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.relationship_type == "capability_to_policy"
            and not relationship.target_reference_id.startswith("v4_3_capability_policy_")
        )
    )
    operational_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in visibility.relationships
            if relationship.executable
            or relationship.routable
            or relationship.traversable
            or relationship.schedulable
            or relationship.authorized
            or relationship.planner_integrated
            or relationship.orchestration_execution_enabled
            or relationship.orchestration_activation_enabled
            or relationship.runtime_execution_enabled
            or relationship.routing_execution_enabled
            or relationship.traversal_execution_enabled
            or relationship.scheduling_execution_enabled
            or relationship.sequencing_execution_enabled
            or relationship.planner_integration_enabled
            or relationship.production_consumption_enabled
            or relationship.runtime_mutation_enabled
        )
    )
    return {
        "valid": (
            len(duplicate_relationship_ids) == 0
            and len(invalid_type_relationship_ids) == 0
            and len(unknown_capability_relationship_ids) == 0
            and len(invalid_boundary_relationship_ids) == 0
            and len(invalid_policy_relationship_ids) == 0
            and len(operational_relationship_ids) == 0
        ),
        "duplicate_relationship_ids": duplicate_relationship_ids,
        "invalid_type_relationship_ids": invalid_type_relationship_ids,
        "unknown_capability_relationship_ids": unknown_capability_relationship_ids,
        "invalid_boundary_relationship_ids": invalid_boundary_relationship_ids,
        "invalid_policy_relationship_ids": invalid_policy_relationship_ids,
        "operational_relationship_ids": operational_relationship_ids,
        "invalid_relationship_count": (
            len(duplicate_relationship_ids)
            + len(invalid_type_relationship_ids)
            + len(unknown_capability_relationship_ids)
            + len(invalid_boundary_relationship_ids)
            + len(invalid_policy_relationship_ids)
            + len(operational_relationship_ids)
        ),
    }


def validate_capability_continuity(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    capability_ids = {capability.capability_id for capability in visibility.capabilities}
    boundary_ids = {boundary.boundary_id for boundary in visibility.boundaries}
    relationship_ids = {relationship.relationship_id for relationship in visibility.relationships}
    missing_capability_refs = tuple(
        sorted(
            ref
            for metadata in visibility.continuity_metadata
            for ref in metadata.capability_references
            if ref not in capability_ids
        )
    )
    missing_boundary_refs = tuple(
        sorted(
            ref
            for metadata in visibility.continuity_metadata
            for ref in metadata.boundary_references
            if ref not in boundary_ids
        )
    )
    missing_relationship_refs = tuple(
        sorted(
            ref
            for metadata in visibility.continuity_metadata
            for ref in metadata.relationship_references
            if ref not in relationship_ids
        )
    )
    corrective_count = sum(
        1
        for metadata in visibility.continuity_metadata
        if metadata.orchestration_execution_enabled
        or metadata.orchestration_activation_enabled
        or metadata.runtime_execution_enabled
        or metadata.runtime_mutation_enabled
    )
    return {
        "valid": (
            len(visibility.continuity_metadata) > 0
            and len(missing_capability_refs) == 0
            and len(missing_boundary_refs) == 0
            and len(missing_relationship_refs) == 0
            and all(metadata.replay_safe for metadata in visibility.continuity_metadata)
            and all(metadata.rollback_safe for metadata in visibility.continuity_metadata)
            and all(metadata.provenance_continuity_preserved for metadata in visibility.continuity_metadata)
            and all(metadata.lineage_continuity_preserved for metadata in visibility.continuity_metadata)
            and all(metadata.capability_continuity_visible for metadata in visibility.continuity_metadata)
            and corrective_count == 0
        ),
        "continuity_metadata_count": len(visibility.continuity_metadata),
        "missing_capability_references": missing_capability_refs,
        "missing_boundary_references": missing_boundary_refs,
        "missing_relationship_references": missing_relationship_refs,
        "replay_safe": all(metadata.replay_safe for metadata in visibility.continuity_metadata),
        "rollback_safe": all(metadata.rollback_safe for metadata in visibility.continuity_metadata),
        "provenance_continuity_preserved": all(
            metadata.provenance_continuity_preserved for metadata in visibility.continuity_metadata
        ),
        "lineage_continuity_preserved": all(
            metadata.lineage_continuity_preserved for metadata in visibility.continuity_metadata
        ),
        "capability_continuity_visible": all(
            metadata.capability_continuity_visible for metadata in visibility.continuity_metadata
        ),
        "corrective_continuity_count": corrective_count,
    }


def validate_capability_explainability(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    categories = tuple(sorted(set(summary.category for summary in visibility.explainability_summaries)))
    required_categories = (
        "prohibited_capability",
        "unsupported_capability",
        "blocked_capability",
        "stale_capability",
        "conflicting_capability",
        "activation_unavailable",
        "execution_unavailable",
        "planner_integration_unavailable",
        "operational_orchestration_prohibited",
        "governance_boundary",
    )
    corrective_count = sum(
        1
        for summary in visibility.explainability_summaries
        if summary.recommendation_enabled
        or summary.ranking_enabled
        or summary.scoring_enabled
        or summary.selection_enabled
        or summary.optimization_enabled
        or summary.correction_enabled
        or summary.inference_enabled
        or summary.orchestration_execution_enabled
        or summary.orchestration_activation_enabled
        or summary.runtime_execution_enabled
    )
    return {
        "valid": (
            set(required_categories).issubset(set(categories))
            and all(summary.deterministic for summary in visibility.explainability_summaries)
            and all(summary.fail_visible for summary in visibility.explainability_summaries)
            and all(summary.descriptive_only for summary in visibility.explainability_summaries)
            and all(summary.replay_safe for summary in visibility.explainability_summaries)
            and all(summary.rollback_safe for summary in visibility.explainability_summaries)
            and corrective_count == 0
        ),
        "explainability_summary_count": len(visibility.explainability_summaries),
        "explainability_categories": categories,
        "required_categories": required_categories,
        "deterministic": all(summary.deterministic for summary in visibility.explainability_summaries),
        "fail_visible": all(summary.fail_visible for summary in visibility.explainability_summaries),
        "descriptive_only": all(summary.descriptive_only for summary in visibility.explainability_summaries),
        "replay_safe": all(summary.replay_safe for summary in visibility.explainability_summaries),
        "rollback_safe": all(summary.rollback_safe for summary in visibility.explainability_summaries),
        "corrective_explainability_count": corrective_count,
    }


def validate_capability_non_execution(visibility: OrchestrationCapabilityVisibility) -> dict[str, object]:
    enabled_flags = enabled_capability_visibility_flags(visibility)
    operational_count = enabled_operational_capability_count(visibility)
    return {
        "valid": len(enabled_flags) == 0 and operational_count == 0 and visibility.non_executable and visibility.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "enabled_operational_capability_count": operational_count,
        "non_executable": visibility.non_executable,
        "descriptive_only": visibility.descriptive_only,
        "orchestration_execution_disabled": not visibility.orchestration_execution_enabled,
        "orchestration_activation_disabled": not visibility.orchestration_activation_enabled,
        "runtime_execution_disabled": not visibility.runtime_execution_enabled,
        "capability_execution_disabled": not visibility.capability_execution_enabled,
        "routing_execution_disabled": not visibility.routing_execution_enabled,
        "traversal_execution_disabled": not visibility.traversal_execution_enabled,
        "dependency_execution_disabled": not visibility.dependency_execution_enabled,
        "sequencing_execution_disabled": not visibility.sequencing_execution_enabled,
        "scheduling_execution_disabled": not visibility.scheduling_execution_enabled,
        "operational_state_mutation_disabled": not visibility.operational_state_mutation_enabled,
        "runtime_mutation_disabled": not visibility.runtime_mutation_enabled,
        "orchestration_authorization_disabled": not visibility.orchestration_authorization_enabled,
        "readiness_approval_disabled": not visibility.readiness_approval_enabled,
        "remediation_system_disabled": not visibility.remediation_system_enabled,
        "automatic_repair_disabled": not visibility.automatic_repair_enabled,
        "inference_system_disabled": not visibility.inference_system_enabled,
        "recommendation_disabled": not visibility.recommendation_enabled,
        "ranking_disabled": not visibility.ranking_enabled,
        "scoring_disabled": not visibility.scoring_enabled,
        "selection_disabled": not visibility.selection_enabled,
        "optimization_disabled": not visibility.optimization_enabled,
        "planning_engine_absent": not visibility.planning_engine_enabled,
        "decision_system_absent": not visibility.decision_system_enabled,
        "resolution_system_absent": not visibility.resolution_system_enabled,
        "planner_integration_disabled": not visibility.planner_integration_enabled,
        "production_consumption_disabled": not visibility.production_consumption_enabled,
        "orchestration_dispatch_disabled": not visibility.orchestration_dispatch_enabled,
        "runtime_coordination_disabled": not visibility.runtime_coordination_enabled,
        "state_machine_absent": not visibility.state_machine_enabled,
        "hidden_orchestration_pathway_absent": not visibility.hidden_orchestration_pathway_enabled,
        "implicit_operational_authorization_absent": not visibility.implicit_operational_authorization_enabled,
        "operational_orchestration_engine_absent": not visibility.operational_orchestration_engine_enabled,
        "orchestration_decision_engine_absent": not visibility.orchestration_decision_engine_enabled,
    }


def build_capability_visibility_diagnostics(
    visibility: OrchestrationCapabilityVisibility | None = None,
) -> dict[str, Any]:
    source = visibility or default_orchestration_capability_visibility()
    identity = validate_capability_identity(source)
    support = validate_capability_support_visibility(source)
    metadata = validate_capability_metadata(source)
    relationships = validate_capability_relationships(source)
    continuity = validate_capability_continuity(source)
    explainability = validate_capability_explainability(source)
    non_execution = validate_capability_non_execution(source)
    enabled_flags = enabled_capability_visibility_flags(source)
    return {
        "capability_visibility_hash": hash_orchestration_capability_visibility(source),
        "capability_hashes": [hash_capability_record(capability) for capability in source.capabilities],
        "boundary_hashes": [hash_capability_boundary(boundary) for boundary in source.boundaries],
        "relationship_hashes": [
            hash_capability_relationship(relationship) for relationship in source.relationships
        ],
        "diagnostic_hashes": [hash_capability_diagnostic(diagnostic) for diagnostic in source.diagnostics],
        "explainability_hashes": [
            hash_capability_explainability(summary) for summary in source.explainability_summaries
        ],
        "identity_validation": identity,
        "support_visibility_validation": support,
        "metadata_validation": metadata,
        "relationship_validation": relationships,
        "continuity_validation": continuity,
        "explainability_validation": explainability,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "enabled_operational_capability_count": enabled_operational_capability_count(source),
        "prohibited_capability_ids": aggregate_prohibited_capabilities(source),
        "unsupported_capability_ids": aggregate_unsupported_capabilities(source),
        "blocked_capability_ids": aggregate_blocked_capabilities(source),
        "stale_capability_ids": aggregate_stale_capabilities(source),
        "conflicting_capability_ids": aggregate_conflicting_capabilities(source),
        "unknown_capability_ids": tuple(sorted(source.support_state_visibility.unknown_capability_ids)),
        "invalid_relationship_count": relationships["invalid_relationship_count"],
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "correction_absent": all(not diagnostic.correction_enabled for diagnostic in source.diagnostics),
        "inference_absent": all(not diagnostic.inference_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(not diagnostic.authorization_enabled for diagnostic in source.diagnostics),
        "operational_mutation_absent": all(
            not diagnostic.operational_mutation_enabled for diagnostic in source.diagnostics
        ),
        "execution_absent": all(
            not diagnostic.orchestration_execution_enabled
            and not diagnostic.orchestration_activation_enabled
            and not diagnostic.runtime_execution_enabled
            and not diagnostic.capability_execution_enabled
            and not diagnostic.routing_execution_enabled
            and not diagnostic.traversal_execution_enabled
            and not diagnostic.dependency_execution_enabled
            and not diagnostic.sequencing_execution_enabled
            and not diagnostic.scheduling_execution_enabled
            for diagnostic in source.diagnostics
        ),
        "selection_systems_absent": all(
            not diagnostic.recommendation_enabled
            and not diagnostic.ranking_enabled
            and not diagnostic.scoring_enabled
            and not diagnostic.selection_enabled
            and not diagnostic.optimization_enabled
            for diagnostic in source.diagnostics
        ),
        "fail_visible_warning_count": (
            len(support["prohibited_capability_ids"])
            + len(support["unsupported_capability_ids"])
            + len(support["blocked_capability_ids"])
            + len(support["stale_capability_ids"])
            + len(support["conflicting_capability_ids"])
            + len(support["unknown_capability_ids"])
        ),
    }
