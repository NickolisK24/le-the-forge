"""Fail-visible visibility helpers for v4.1 refresh sequencing evidence."""

from __future__ import annotations

from .refresh_sequencing_visibility_models import (
    FAIL_VISIBLE_SEQUENCING_STATES,
    PROHIBITED_SEQUENCING_DOMAINS,
    SEQUENCING_STATE_BLOCKED,
    SEQUENCING_STATE_CIRCULAR,
    SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY,
    SEQUENCING_STATE_LINEAGE_DISCONTINUITY,
    SEQUENCING_STATE_PROHIBITED,
    SEQUENCING_STATE_PROVENANCE_DISCONTINUITY,
    SEQUENCING_STATE_REPLAY_DISCONTINUITY,
    SEQUENCING_STATE_ROLLBACK_DISCONTINUITY,
    SEQUENCING_STATE_SEQUENCING_DISCONTINUITY,
    SEQUENCING_STATE_STALE,
    SEQUENCING_STATE_UNSUPPORTED,
    SEQUENCING_STATES,
    RefreshOrderingNode,
    RefreshOrderingRelationship,
    RefreshSequencingVisibility,
    default_refresh_ordering_nodes,
    default_refresh_ordering_relationships,
    default_refresh_sequencing_visibility,
)


def count_refresh_ordering_node_states(nodes: tuple[RefreshOrderingNode, ...] | list[RefreshOrderingNode]) -> dict[str, int]:
    counts = {state: 0 for state in SEQUENCING_STATES}
    counts["invalid"] = 0
    for node in nodes:
        if node.state in counts:
            counts[node.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_refresh_ordering_relationship_states(
    relationships: tuple[RefreshOrderingRelationship, ...] | list[RefreshOrderingRelationship],
) -> dict[str, int]:
    counts = {state: 0 for state in SEQUENCING_STATES}
    counts["invalid"] = 0
    for relationship in relationships:
        if relationship.state in counts:
            counts[relationship.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_refresh_ordering_relationship_ids(
    relationships: tuple[RefreshOrderingRelationship, ...] | list[RefreshOrderingRelationship],
) -> tuple[str, ...]:
    return tuple(
        relationship.relationship_id
        for relationship in relationships
        if relationship.state in FAIL_VISIBLE_SEQUENCING_STATES and relationship.fail_visible
    )


def validate_refresh_sequencing_visibility(visibility: RefreshSequencingVisibility) -> dict[str, object]:
    node_counts = count_refresh_ordering_node_states(visibility.ordering_nodes)
    relationship_counts = count_refresh_ordering_relationship_states(visibility.ordering_relationships)
    unsupported_nodes = tuple(node.node_id for node in visibility.ordering_nodes if node.state == SEQUENCING_STATE_UNSUPPORTED)
    unsupported_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_UNSUPPORTED
    )
    blocked_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_BLOCKED
    )
    stale_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_STALE
    )
    prohibited_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_PROHIBITED
    )
    circular_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_CIRCULAR
    )
    sequencing_gap_relationships = tuple(
        item.relationship_id
        for item in visibility.ordering_relationships
        if item.state == SEQUENCING_STATE_SEQUENCING_DISCONTINUITY
    )
    dependency_gap_relationships = tuple(
        item.relationship_id
        for item in visibility.ordering_relationships
        if item.state == SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY
    )
    lineage_gap_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_LINEAGE_DISCONTINUITY
    )
    provenance_gap_relationships = tuple(
        item.relationship_id
        for item in visibility.ordering_relationships
        if item.state == SEQUENCING_STATE_PROVENANCE_DISCONTINUITY
    )
    replay_gap_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_REPLAY_DISCONTINUITY
    )
    rollback_gap_relationships = tuple(
        item.relationship_id for item in visibility.ordering_relationships if item.state == SEQUENCING_STATE_ROLLBACK_DISCONTINUITY
    )
    hidden_node_count = sum(1 for node in visibility.ordering_nodes if node.hidden)
    hidden_relationship_count = sum(1 for relationship in visibility.ordering_relationships if relationship.hidden)
    node_execution_count = sum(
        1
        for node in visibility.ordering_nodes
        if node.refresh_execution_enabled
        or node.orchestration_enabled
        or node.automatic_sequencing_enabled
        or node.automatic_dependency_resolution_enabled
        or node.remediation_enabled
        or node.runtime_mutation_enabled
        or node.silent_ordering_correction_enabled
    )
    relationship_execution_count = sum(
        1
        for relationship in visibility.ordering_relationships
        if relationship.refresh_execution_enabled
        or relationship.orchestration_enabled
        or relationship.automatic_sequencing_enabled
        or relationship.automatic_dependency_resolution_enabled
        or relationship.migration_execution_enabled
        or relationship.planner_integration_enabled
        or relationship.production_consumption_enabled
        or relationship.remediation_enabled
        or relationship.runtime_mutation_enabled
        or relationship.silent_ordering_correction_enabled
    )
    dependency_visibility = visibility.dependency_aware_visibility
    blocked = visibility.blocked_state_visibility
    unsupported = visibility.unsupported_state_visibility
    prohibited_domains_visible = set(PROHIBITED_SEQUENCING_DOMAINS).issubset(
        set(unsupported.prohibited_sequencing_domains)
    )
    dependency_references_visible = set(
        relationship.dependency_reference for relationship in visibility.ordering_relationships
    ).issubset(set(dependency_visibility.dependency_ordering_references))
    visibility_failures = [
        bool(set(unsupported_nodes) - set(unsupported.unsupported_node_ids)),
        bool(set(unsupported_relationships) - set(unsupported.unsupported_relationship_ids)),
        bool(set(blocked_relationships) - set(blocked.blocked_relationship_ids)),
        bool(set(stale_relationships) - set(unsupported.stale_relationship_ids)),
        bool(set(prohibited_relationships) - set(unsupported.prohibited_relationship_ids)),
        bool(set(circular_relationships) - set(blocked.circular_sequencing_visibility)),
        bool(set(sequencing_gap_relationships) - set(blocked.sequencing_discontinuity_visibility)),
        bool(set(dependency_gap_relationships) - set(blocked.dependency_ordering_discontinuity_visibility)),
        bool(set(lineage_gap_relationships) - set(blocked.lineage_discontinuity_visibility)),
        bool(set(provenance_gap_relationships) - set(blocked.provenance_discontinuity_visibility)),
        bool(set(replay_gap_relationships) - set(blocked.replay_discontinuity_visibility)),
        bool(set(rollback_gap_relationships) - set(blocked.rollback_discontinuity_visibility)),
        not prohibited_domains_visible,
        not dependency_references_visible,
    ]
    return {
        "node_state_counts": node_counts,
        "relationship_state_counts": relationship_counts,
        "fail_visible_relationship_count": len(fail_visible_refresh_ordering_relationship_ids(visibility.ordering_relationships)),
        "unsupported_node_visibility_count": len(unsupported.unsupported_node_ids),
        "unsupported_relationship_visibility_count": len(unsupported.unsupported_relationship_ids),
        "blocked_relationship_visibility_count": len(blocked.blocked_relationship_ids),
        "stale_relationship_visibility_count": len(unsupported.stale_relationship_ids),
        "prohibited_relationship_visibility_count": len(unsupported.prohibited_relationship_ids),
        "circular_sequencing_visibility_count": len(blocked.circular_sequencing_visibility),
        "sequencing_discontinuity_visibility_count": len(blocked.sequencing_discontinuity_visibility),
        "dependency_ordering_discontinuity_visibility_count": len(blocked.dependency_ordering_discontinuity_visibility),
        "lineage_discontinuity_visibility_count": len(blocked.lineage_discontinuity_visibility),
        "provenance_discontinuity_visibility_count": len(blocked.provenance_discontinuity_visibility),
        "replay_discontinuity_visibility_count": len(blocked.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility_count": len(blocked.rollback_discontinuity_visibility),
        "prohibited_sequencing_domain_visibility_count": len(unsupported.prohibited_sequencing_domains),
        "failure_visibility_count": len(unsupported.failure_visibility),
        "dependency_ordering_reference_visibility_count": len(dependency_visibility.dependency_ordering_references),
        "diagnostics_warning_visibility_count": (
            len(visibility.diagnostics.warning_visibility)
            + len(visibility.diagnostics.blocker_visibility)
            + len(visibility.diagnostics.unsupported_sequencing_visibility)
            + len(visibility.diagnostics.prohibited_sequencing_visibility)
            + len(visibility.diagnostics.circular_sequencing_visibility)
            + len(visibility.diagnostics.drift_visibility)
            + len(visibility.diagnostics.integrity_visibility)
        ),
        "governance_limitation_count": len(visibility.governance.explicit_limitations),
        "governance_prohibition_count": len(visibility.governance.explicit_prohibitions),
        "hidden_node_count": hidden_node_count,
        "hidden_relationship_count": hidden_relationship_count,
        "invalid_ordering_node_state_count": node_counts["invalid"],
        "invalid_ordering_relationship_state_count": relationship_counts["invalid"],
        "node_execution_semantics_count": node_execution_count,
        "relationship_execution_semantics_count": relationship_execution_count,
        "unsupported_nodes_visible": not bool(set(unsupported_nodes) - set(unsupported.unsupported_node_ids)),
        "unsupported_relationships_visible": not bool(
            set(unsupported_relationships) - set(unsupported.unsupported_relationship_ids)
        ),
        "blocked_relationships_visible": not bool(set(blocked_relationships) - set(blocked.blocked_relationship_ids)),
        "stale_relationships_visible": not bool(set(stale_relationships) - set(unsupported.stale_relationship_ids)),
        "prohibited_relationships_visible": not bool(
            set(prohibited_relationships) - set(unsupported.prohibited_relationship_ids)
        ),
        "circular_sequencing_visible": not bool(set(circular_relationships) - set(blocked.circular_sequencing_visibility)),
        "sequencing_discontinuity_visible": not bool(
            set(sequencing_gap_relationships) - set(blocked.sequencing_discontinuity_visibility)
        ),
        "dependency_ordering_discontinuity_visible": not bool(
            set(dependency_gap_relationships) - set(blocked.dependency_ordering_discontinuity_visibility)
        ),
        "lineage_discontinuity_visible": not bool(
            set(lineage_gap_relationships) - set(blocked.lineage_discontinuity_visibility)
        ),
        "provenance_discontinuity_visible": not bool(
            set(provenance_gap_relationships) - set(blocked.provenance_discontinuity_visibility)
        ),
        "replay_discontinuity_visible": not bool(set(replay_gap_relationships) - set(blocked.replay_discontinuity_visibility)),
        "rollback_discontinuity_visible": not bool(
            set(rollback_gap_relationships) - set(blocked.rollback_discontinuity_visibility)
        ),
        "prohibited_sequencing_domains_visible": prohibited_domains_visible,
        "dependency_references_visible": dependency_references_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *visibility.ordering_nodes,
                *visibility.ordering_relationships,
                visibility.dependency_aware_visibility,
                visibility.continuity_metadata,
                visibility.lineage_visibility,
                visibility.provenance_visibility,
                visibility.replay_visibility,
                visibility.rollback_visibility,
                visibility.drift_visibility,
                visibility.blocked_state_visibility,
                visibility.unsupported_state_visibility,
                visibility.diagnostics,
                visibility.governance,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_node_count == 0
            and hidden_relationship_count == 0
            and node_counts["invalid"] == 0
            and relationship_counts["invalid"] == 0
            and node_execution_count == 0
            and relationship_execution_count == 0
        ),
    }


def build_default_refresh_ordering_nodes() -> tuple[RefreshOrderingNode, ...]:
    return default_refresh_ordering_nodes()


def build_default_refresh_ordering_relationships() -> tuple[RefreshOrderingRelationship, ...]:
    return default_refresh_ordering_relationships()


def build_default_refresh_sequencing_visibility() -> RefreshSequencingVisibility:
    return default_refresh_sequencing_visibility()
