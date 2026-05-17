"""Fail-visible visibility helpers for v4.1 schema evolution governance."""

from __future__ import annotations

from .schema_evolution_governance_models import (
    FAIL_VISIBLE_SCHEMA_STATES,
    PROHIBITED_SCHEMA_DOMAINS,
    SCHEMA_STATE_BLOCKED,
    SCHEMA_STATE_CIRCULAR_ANCESTRY,
    SCHEMA_STATE_LINEAGE_DISCONTINUITY,
    SCHEMA_STATE_PROHIBITED,
    SCHEMA_STATE_PROVENANCE_DISCONTINUITY,
    SCHEMA_STATE_REPLAY_DISCONTINUITY,
    SCHEMA_STATE_ROLLBACK_DISCONTINUITY,
    SCHEMA_STATE_STALE,
    SCHEMA_STATE_UNSUPPORTED,
    SCHEMA_STATE_VERSION_DISCONTINUITY,
    SCHEMA_STATES,
    SchemaEvolutionGovernance,
    SchemaVersionNode,
    SchemaVersionTransition,
    default_schema_evolution_governance,
    default_schema_version_nodes,
    default_schema_version_transitions,
)


def count_schema_node_states(nodes: tuple[SchemaVersionNode, ...] | list[SchemaVersionNode]) -> dict[str, int]:
    counts = {state: 0 for state in SCHEMA_STATES}
    counts["invalid"] = 0
    for node in nodes:
        if node.state in counts:
            counts[node.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_schema_transition_states(
    transitions: tuple[SchemaVersionTransition, ...] | list[SchemaVersionTransition],
) -> dict[str, int]:
    counts = {state: 0 for state in SCHEMA_STATES}
    counts["invalid"] = 0
    for transition in transitions:
        if transition.state in counts:
            counts[transition.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_schema_transition_ids(
    transitions: tuple[SchemaVersionTransition, ...] | list[SchemaVersionTransition],
) -> tuple[str, ...]:
    return tuple(
        transition.transition_id
        for transition in transitions
        if transition.state in FAIL_VISIBLE_SCHEMA_STATES and transition.fail_visible
    )


def validate_schema_evolution_visibility(governance: SchemaEvolutionGovernance) -> dict[str, object]:
    node_counts = count_schema_node_states(governance.version_nodes)
    transition_counts = count_schema_transition_states(governance.version_transitions)
    unsupported_nodes = tuple(node.node_id for node in governance.version_nodes if node.state == SCHEMA_STATE_UNSUPPORTED)
    unsupported_transitions = tuple(
        transition.transition_id for transition in governance.version_transitions if transition.state == SCHEMA_STATE_UNSUPPORTED
    )
    blocked_transitions = tuple(
        transition.transition_id for transition in governance.version_transitions if transition.state == SCHEMA_STATE_BLOCKED
    )
    stale_transitions = tuple(
        transition.transition_id for transition in governance.version_transitions if transition.state == SCHEMA_STATE_STALE
    )
    prohibited_transitions = tuple(
        transition.transition_id for transition in governance.version_transitions if transition.state == SCHEMA_STATE_PROHIBITED
    )
    circular_transitions = tuple(
        transition.transition_id
        for transition in governance.version_transitions
        if transition.state == SCHEMA_STATE_CIRCULAR_ANCESTRY
    )
    version_gap_transitions = tuple(
        transition.transition_id
        for transition in governance.version_transitions
        if transition.state == SCHEMA_STATE_VERSION_DISCONTINUITY
    )
    lineage_gap_transitions = tuple(
        transition.transition_id
        for transition in governance.version_transitions
        if transition.state == SCHEMA_STATE_LINEAGE_DISCONTINUITY
    )
    provenance_gap_transitions = tuple(
        transition.transition_id
        for transition in governance.version_transitions
        if transition.state == SCHEMA_STATE_PROVENANCE_DISCONTINUITY
    )
    replay_gap_transitions = tuple(
        transition.transition_id
        for transition in governance.version_transitions
        if transition.state == SCHEMA_STATE_REPLAY_DISCONTINUITY
    )
    rollback_gap_transitions = tuple(
        transition.transition_id
        for transition in governance.version_transitions
        if transition.state == SCHEMA_STATE_ROLLBACK_DISCONTINUITY
    )
    hidden_node_count = sum(1 for node in governance.version_nodes if node.hidden)
    hidden_transition_count = sum(1 for transition in governance.version_transitions if transition.hidden)
    node_execution_count = sum(
        1
        for node in governance.version_nodes
        if node.schema_migration_execution_enabled
        or node.automatic_schema_migration_enabled
        or node.automatic_schema_repair_enabled
        or node.automatic_compatibility_correction_enabled
        or node.refresh_execution_enabled
        or node.remediation_enabled
        or node.runtime_mutation_enabled
        or node.silent_compatibility_fallback_enabled
    )
    transition_execution_count = sum(
        1
        for transition in governance.version_transitions
        if transition.schema_migration_execution_enabled
        or transition.automatic_schema_migration_enabled
        or transition.automatic_schema_repair_enabled
        or transition.automatic_compatibility_correction_enabled
        or transition.refresh_execution_enabled
        or transition.orchestration_enabled
        or transition.planner_integration_enabled
        or transition.production_consumption_enabled
        or transition.remediation_enabled
        or transition.runtime_mutation_enabled
        or transition.silent_compatibility_fallback_enabled
    )
    unsupported = governance.unsupported_state_visibility
    blocked = governance.blocked_state_visibility
    compatibility = governance.compatibility_visibility
    prohibited_domains_visible = set(PROHIBITED_SCHEMA_DOMAINS).issubset(set(unsupported.prohibited_schema_domains))
    classifications_visible = set(
        transition.compatibility_classification for transition in governance.version_transitions
    ).issubset(set(compatibility.transition_classifications))
    visibility_failures = [
        bool(set(unsupported_nodes) - set(unsupported.unsupported_node_ids)),
        bool(set(unsupported_transitions) - set(unsupported.unsupported_transition_ids)),
        bool(set(blocked_transitions) - set(blocked.blocked_transition_ids)),
        bool(set(stale_transitions) - set(unsupported.stale_transition_ids)),
        bool(set(prohibited_transitions) - set(unsupported.prohibited_transition_ids)),
        bool(set(circular_transitions) - set(blocked.circular_schema_ancestry_visibility)),
        bool(set(version_gap_transitions) - set(blocked.schema_version_discontinuity_visibility)),
        bool(set(lineage_gap_transitions) - set(blocked.schema_lineage_discontinuity_visibility)),
        bool(set(provenance_gap_transitions) - set(blocked.schema_provenance_discontinuity_visibility)),
        bool(set(replay_gap_transitions) - set(blocked.schema_replay_discontinuity_visibility)),
        bool(set(rollback_gap_transitions) - set(blocked.schema_rollback_discontinuity_visibility)),
        not prohibited_domains_visible,
        not classifications_visible,
    ]
    return {
        "node_state_counts": node_counts,
        "transition_state_counts": transition_counts,
        "fail_visible_transition_count": len(fail_visible_schema_transition_ids(governance.version_transitions)),
        "unsupported_node_visibility_count": len(unsupported.unsupported_node_ids),
        "unsupported_transition_visibility_count": len(unsupported.unsupported_transition_ids),
        "blocked_transition_visibility_count": len(blocked.blocked_transition_ids),
        "stale_transition_visibility_count": len(unsupported.stale_transition_ids),
        "prohibited_transition_visibility_count": len(unsupported.prohibited_transition_ids),
        "circular_schema_ancestry_visibility_count": len(blocked.circular_schema_ancestry_visibility),
        "schema_version_discontinuity_visibility_count": len(blocked.schema_version_discontinuity_visibility),
        "schema_lineage_discontinuity_visibility_count": len(blocked.schema_lineage_discontinuity_visibility),
        "schema_provenance_discontinuity_visibility_count": len(blocked.schema_provenance_discontinuity_visibility),
        "schema_replay_discontinuity_visibility_count": len(blocked.schema_replay_discontinuity_visibility),
        "schema_rollback_discontinuity_visibility_count": len(blocked.schema_rollback_discontinuity_visibility),
        "prohibited_schema_domain_visibility_count": len(unsupported.prohibited_schema_domains),
        "failure_visibility_count": len(unsupported.failure_visibility),
        "compatibility_classification_visibility_count": len(compatibility.transition_classifications),
        "diagnostics_warning_visibility_count": (
            len(governance.diagnostics.warning_visibility)
            + len(governance.diagnostics.blocker_visibility)
            + len(governance.diagnostics.unsupported_schema_visibility)
            + len(governance.diagnostics.prohibited_schema_visibility)
            + len(governance.diagnostics.compatibility_visibility)
            + len(governance.diagnostics.drift_visibility)
            + len(governance.diagnostics.integrity_visibility)
        ),
        "governance_limitation_count": len(governance.governance.explicit_limitations),
        "governance_prohibition_count": len(governance.governance.explicit_prohibitions),
        "hidden_node_count": hidden_node_count,
        "hidden_transition_count": hidden_transition_count,
        "invalid_schema_node_state_count": node_counts["invalid"],
        "invalid_schema_transition_state_count": transition_counts["invalid"],
        "node_execution_semantics_count": node_execution_count,
        "transition_execution_semantics_count": transition_execution_count,
        "unsupported_nodes_visible": not bool(set(unsupported_nodes) - set(unsupported.unsupported_node_ids)),
        "unsupported_transitions_visible": not bool(
            set(unsupported_transitions) - set(unsupported.unsupported_transition_ids)
        ),
        "blocked_transitions_visible": not bool(set(blocked_transitions) - set(blocked.blocked_transition_ids)),
        "stale_transitions_visible": not bool(set(stale_transitions) - set(unsupported.stale_transition_ids)),
        "prohibited_transitions_visible": not bool(
            set(prohibited_transitions) - set(unsupported.prohibited_transition_ids)
        ),
        "circular_schema_ancestry_visible": not bool(
            set(circular_transitions) - set(blocked.circular_schema_ancestry_visibility)
        ),
        "schema_version_discontinuity_visible": not bool(
            set(version_gap_transitions) - set(blocked.schema_version_discontinuity_visibility)
        ),
        "schema_lineage_discontinuity_visible": not bool(
            set(lineage_gap_transitions) - set(blocked.schema_lineage_discontinuity_visibility)
        ),
        "schema_provenance_discontinuity_visible": not bool(
            set(provenance_gap_transitions) - set(blocked.schema_provenance_discontinuity_visibility)
        ),
        "schema_replay_discontinuity_visible": not bool(
            set(replay_gap_transitions) - set(blocked.schema_replay_discontinuity_visibility)
        ),
        "schema_rollback_discontinuity_visible": not bool(
            set(rollback_gap_transitions) - set(blocked.schema_rollback_discontinuity_visibility)
        ),
        "prohibited_schema_domains_visible": prohibited_domains_visible,
        "compatibility_classifications_visible": classifications_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *governance.version_nodes,
                *governance.version_transitions,
                governance.compatibility_visibility,
                governance.continuity_metadata,
                governance.lineage_visibility,
                governance.provenance_visibility,
                governance.replay_visibility,
                governance.rollback_visibility,
                governance.drift_visibility,
                governance.blocked_state_visibility,
                governance.unsupported_state_visibility,
                governance.diagnostics,
                governance.governance,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_node_count == 0
            and hidden_transition_count == 0
            and node_counts["invalid"] == 0
            and transition_counts["invalid"] == 0
            and node_execution_count == 0
            and transition_execution_count == 0
        ),
    }


def build_default_schema_version_nodes() -> tuple[SchemaVersionNode, ...]:
    return default_schema_version_nodes()


def build_default_schema_version_transitions() -> tuple[SchemaVersionTransition, ...]:
    return default_schema_version_transitions()


def build_default_schema_evolution_governance() -> SchemaEvolutionGovernance:
    return default_schema_evolution_governance()
