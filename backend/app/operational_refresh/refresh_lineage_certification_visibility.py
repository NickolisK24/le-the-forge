"""Fail-visible visibility helpers for v4.1 refresh lineage certification."""

from __future__ import annotations

from .refresh_lineage_certification_models import (
    FAIL_VISIBLE_LINEAGE_STATES,
    LINEAGE_STATE_BLOCKED,
    LINEAGE_STATE_CIRCULAR_ANCESTRY,
    LINEAGE_STATE_LINEAGE_DISCONTINUITY,
    LINEAGE_STATE_PROHIBITED,
    LINEAGE_STATE_PROVENANCE_DISCONTINUITY,
    LINEAGE_STATE_SCHEMA_DISCONTINUITY,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_UNSUPPORTED,
    LINEAGE_STATES,
    PROHIBITED_LINEAGE_DOMAINS,
    RefreshAncestryLink,
    RefreshAncestryNode,
    RefreshLineageCertification,
    default_ancestry_links,
    default_ancestry_nodes,
    default_refresh_lineage_certification,
)


def count_ancestry_node_states(nodes: tuple[RefreshAncestryNode, ...] | list[RefreshAncestryNode]) -> dict[str, int]:
    counts = {state: 0 for state in LINEAGE_STATES}
    counts["invalid"] = 0
    for node in nodes:
        if node.state in counts:
            counts[node.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_ancestry_link_states(links: tuple[RefreshAncestryLink, ...] | list[RefreshAncestryLink]) -> dict[str, int]:
    counts = {state: 0 for state in LINEAGE_STATES}
    counts["invalid"] = 0
    for link in links:
        if link.relationship_state in counts:
            counts[link.relationship_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_ancestry_link_ids(links: tuple[RefreshAncestryLink, ...] | list[RefreshAncestryLink]) -> tuple[str, ...]:
    return tuple(link.link_id for link in links if link.relationship_state in FAIL_VISIBLE_LINEAGE_STATES and link.fail_visible)


def validate_refresh_lineage_visibility(certification: RefreshLineageCertification) -> dict[str, object]:
    node_counts = count_ancestry_node_states(certification.ancestry_nodes)
    link_counts = count_ancestry_link_states(certification.ancestry_links)
    unsupported_nodes = tuple(node.node_id for node in certification.ancestry_nodes if node.state == LINEAGE_STATE_UNSUPPORTED)
    unsupported_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_UNSUPPORTED
    )
    blocked_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_BLOCKED
    )
    stale_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_STALE
    )
    prohibited_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_PROHIBITED
    )
    circular_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_CIRCULAR_ANCESTRY
    )
    lineage_gap_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_LINEAGE_DISCONTINUITY
    )
    provenance_gap_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_PROVENANCE_DISCONTINUITY
    )
    schema_gap_links = tuple(
        link.link_id for link in certification.ancestry_links if link.relationship_state == LINEAGE_STATE_SCHEMA_DISCONTINUITY
    )
    hidden_node_count = sum(1 for node in certification.ancestry_nodes if node.hidden)
    hidden_link_count = sum(1 for link in certification.ancestry_links if link.hidden)
    node_execution_count = sum(
        1
        for node in certification.ancestry_nodes
        if node.refresh_execution_enabled
        or node.migration_execution_enabled
        or node.automatic_lineage_repair_enabled
        or node.remediation_enabled
        or node.runtime_mutation_enabled
        or node.silent_correction_enabled
    )
    link_execution_count = sum(
        1
        for link in certification.ancestry_links
        if link.refresh_execution_enabled
        or link.orchestration_enabled
        or link.migration_execution_enabled
        or link.automatic_lineage_repair_enabled
        or link.automatic_continuity_correction_enabled
        or link.automatic_schema_migration_enabled
        or link.remediation_enabled
        or link.planner_integration_enabled
        or link.production_consumption_enabled
        or link.runtime_mutation_enabled
        or link.silent_correction_enabled
    )
    unsupported = certification.unsupported_state_visibility
    blocked = certification.blocked_state_visibility
    prohibited_domains_visible = set(PROHIBITED_LINEAGE_DOMAINS).issubset(set(unsupported.prohibited_lineage_domains))
    visibility_failures = [
        bool(set(unsupported_nodes) - set(unsupported.unsupported_lineage_nodes)),
        bool(set(unsupported_links) - set(unsupported.unsupported_lineage_links)),
        bool(set(stale_links) - set(unsupported.stale_lineage_links)),
        bool(set(prohibited_links) - set(unsupported.prohibited_lineage_links)),
        bool(set(blocked_links) - set(blocked.blocked_lineage_links)),
        bool(set(circular_links) - set(blocked.circular_ancestry_links)),
        bool(set(lineage_gap_links) - set(blocked.lineage_discontinuity_visibility)),
        bool(set(provenance_gap_links) - set(blocked.provenance_discontinuity_visibility)),
        bool(set(schema_gap_links) - set(blocked.schema_discontinuity_visibility)),
        not prohibited_domains_visible,
    ]
    return {
        "node_state_counts": node_counts,
        "link_state_counts": link_counts,
        "fail_visible_ancestry_link_count": len(fail_visible_ancestry_link_ids(certification.ancestry_links)),
        "unsupported_lineage_node_visibility_count": len(unsupported.unsupported_lineage_nodes),
        "unsupported_lineage_link_visibility_count": len(unsupported.unsupported_lineage_links),
        "blocked_lineage_link_visibility_count": len(blocked.blocked_lineage_links),
        "stale_lineage_link_visibility_count": len(unsupported.stale_lineage_links),
        "prohibited_lineage_link_visibility_count": len(unsupported.prohibited_lineage_links),
        "circular_ancestry_visibility_count": len(blocked.circular_ancestry_links),
        "ancestry_discontinuity_visibility_count": len(blocked.ancestry_discontinuity_visibility),
        "lineage_discontinuity_visibility_count": len(blocked.lineage_discontinuity_visibility),
        "provenance_discontinuity_visibility_count": len(blocked.provenance_discontinuity_visibility),
        "replay_discontinuity_visibility_count": len(blocked.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility_count": len(blocked.rollback_discontinuity_visibility),
        "schema_discontinuity_visibility_count": len(blocked.schema_discontinuity_visibility),
        "prohibited_lineage_domain_visibility_count": len(unsupported.prohibited_lineage_domains),
        "failure_visibility_count": len(unsupported.failure_visibility),
        "diagnostics_warning_visibility_count": (
            len(certification.diagnostics.warning_visibility)
            + len(certification.diagnostics.blocker_visibility)
            + len(certification.diagnostics.circular_ancestry_visibility)
            + len(certification.diagnostics.unsupported_lineage_visibility)
            + len(certification.diagnostics.prohibited_lineage_visibility)
            + len(certification.diagnostics.drift_visibility)
            + len(certification.diagnostics.integrity_visibility)
        ),
        "governance_limitation_count": len(certification.governance.explicit_limitations),
        "governance_prohibition_count": len(certification.governance.explicit_prohibitions),
        "hidden_node_count": hidden_node_count,
        "hidden_link_count": hidden_link_count,
        "invalid_ancestry_node_state_count": node_counts["invalid"],
        "invalid_ancestry_link_state_count": link_counts["invalid"],
        "node_execution_semantics_count": node_execution_count,
        "link_execution_semantics_count": link_execution_count,
        "unsupported_nodes_visible": not bool(set(unsupported_nodes) - set(unsupported.unsupported_lineage_nodes)),
        "unsupported_links_visible": not bool(set(unsupported_links) - set(unsupported.unsupported_lineage_links)),
        "blocked_links_visible": not bool(set(blocked_links) - set(blocked.blocked_lineage_links)),
        "stale_links_visible": not bool(set(stale_links) - set(unsupported.stale_lineage_links)),
        "prohibited_links_visible": not bool(set(prohibited_links) - set(unsupported.prohibited_lineage_links)),
        "circular_ancestry_visible": not bool(set(circular_links) - set(blocked.circular_ancestry_links)),
        "lineage_discontinuity_visible": not bool(set(lineage_gap_links) - set(blocked.lineage_discontinuity_visibility)),
        "provenance_discontinuity_visible": not bool(set(provenance_gap_links) - set(blocked.provenance_discontinuity_visibility)),
        "schema_discontinuity_visible": not bool(set(schema_gap_links) - set(blocked.schema_discontinuity_visibility)),
        "replay_discontinuity_visible": bool(blocked.replay_discontinuity_visibility),
        "rollback_discontinuity_visible": bool(blocked.rollback_discontinuity_visibility),
        "prohibited_lineage_domains_visible": prohibited_domains_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *certification.ancestry_nodes,
                *certification.ancestry_links,
                *certification.provenance_inheritance,
                certification.evolution_visibility,
                certification.continuity_metadata,
                certification.replay_lineage_visibility,
                certification.rollback_lineage_visibility,
                certification.schema_transition_continuity,
                certification.blocked_state_visibility,
                certification.unsupported_state_visibility,
                certification.drift_visibility,
                certification.diagnostics,
                certification.governance,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_node_count == 0
            and hidden_link_count == 0
            and node_counts["invalid"] == 0
            and link_counts["invalid"] == 0
            and node_execution_count == 0
            and link_execution_count == 0
        ),
    }


def build_default_ancestry_nodes() -> tuple[RefreshAncestryNode, ...]:
    return default_ancestry_nodes()


def build_default_ancestry_links() -> tuple[RefreshAncestryLink, ...]:
    return default_ancestry_links()


def build_default_refresh_lineage_certification() -> RefreshLineageCertification:
    return default_refresh_lineage_certification()
