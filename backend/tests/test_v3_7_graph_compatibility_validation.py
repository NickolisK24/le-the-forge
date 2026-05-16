from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_compatibility_models import (
    V37_INCOMPATIBLE,
    V37_PROHIBITED_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
    V37_UNSUPPORTED_COMPATIBILITY,
)
from app.runtime_orchestration.v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map
from app.runtime_orchestration.v3_7_graph_compatibility_validation import (
    V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_EDGE_RELATIONSHIP,
    V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_NODE_RELATIONSHIP,
    V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA,
    V37_COMPATIBILITY_BLOCKED_BY_PROHIBITED_STATE,
    V37_COMPATIBILITY_BLOCKED_BY_UNKNOWN_STATE,
    V37_COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_STATE,
    V37_COMPATIBILITY_COMPATIBLE_VISIBLE,
    V37_COMPATIBILITY_PROHIBITED_VISIBLE,
    V37_COMPATIBILITY_UNKNOWN_VISIBLE,
    V37_COMPATIBILITY_UNSUPPORTED_VISIBLE,
    V37_COMPATIBILITY_VALIDATION_BLOCKED,
    V37_COMPATIBILITY_VALIDATION_STABLE,
    validate_v3_7_graph_compatibility,
)


def _statuses(result):
    return {finding.status for finding in result.findings}


def test_default_compatibility_validation_is_stable_with_visible_findings():
    result = validate_v3_7_graph_compatibility(build_v3_7_graph_compatibility_map())

    assert result.validation_status == V37_COMPATIBILITY_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 5
    assert result.prohibited_state_count == 0
    assert result.unsupported_state_count == 0
    assert result.unknown_state_count == 0
    assert result.governance_aware_outcome_count == 3
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.serialization_stable is True
    assert result.hash_stable is True
    assert result.non_execution_guarantee_preserved is True
    assert V37_COMPATIBILITY_COMPATIBLE_VISIBLE in _statuses(result)
    assert V37_COMPATIBILITY_PROHIBITED_VISIBLE in _statuses(result)
    assert V37_COMPATIBILITY_UNSUPPORTED_VISIBLE in _statuses(result)
    assert V37_COMPATIBILITY_UNKNOWN_VISIBLE in _statuses(result)


def test_fail_visible_prohibited_unsupported_unknown_and_incompatible_results():
    compatibility_map = build_v3_7_graph_compatibility_map()
    prohibited_edge = replace(
        compatibility_map.edge_results[0],
        compatibility_classification=V37_PROHIBITED_COMPATIBILITY,
    )
    unsupported_edge = replace(
        compatibility_map.edge_results[1],
        compatibility_classification=V37_UNSUPPORTED_COMPATIBILITY,
    )
    unknown_node = replace(
        compatibility_map.node_results[0],
        compatibility_classification=V37_UNKNOWN_COMPATIBILITY,
    )
    incompatible_node = replace(
        compatibility_map.node_results[1],
        compatibility_classification=V37_INCOMPATIBLE,
    )
    result = validate_v3_7_graph_compatibility(
        replace(
            compatibility_map,
            node_results=(unknown_node, incompatible_node),
            edge_results=(prohibited_edge, unsupported_edge),
        )
    )

    assert result.validation_status == V37_COMPATIBILITY_VALIDATION_BLOCKED
    assert result.prohibited_state_count == 1
    assert result.unsupported_state_count == 1
    assert result.unknown_state_count == 1
    assert result.incompatible_node_relationship_count == 1
    assert V37_COMPATIBILITY_BLOCKED_BY_PROHIBITED_STATE in _statuses(result)
    assert V37_COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_STATE in _statuses(result)
    assert V37_COMPATIBILITY_BLOCKED_BY_UNKNOWN_STATE in _statuses(result)
    assert V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_NODE_RELATIONSHIP in _statuses(result)


def test_missing_metadata_and_incompatible_edge_are_fail_visible():
    compatibility_map = build_v3_7_graph_compatibility_map()
    broken_edge = replace(
        compatibility_map.edge_results[0],
        rule_id="",
        domain_compatibility_classification="",
        compatibility_classification=V37_INCOMPATIBLE,
    )
    result = validate_v3_7_graph_compatibility(
        replace(compatibility_map, edge_results=(broken_edge,) + compatibility_map.edge_results[1:])
    )

    assert result.validation_status == V37_COMPATIBILITY_VALIDATION_BLOCKED
    assert result.missing_metadata_count == 1
    assert result.incompatible_edge_relationship_count == 1
    assert V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA in _statuses(result)
    assert V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_EDGE_RELATIONSHIP in _statuses(result)


def test_execution_capability_flags_are_rejected():
    compatibility_map = build_v3_7_graph_compatibility_map()
    traversal_edge = replace(
        compatibility_map.edge_results[0],
        edge_compatibility_implies_traversal=True,
        traversal_enabled=True,
    )
    ordered_node = replace(
        compatibility_map.node_results[0],
        node_relationship_implies_runtime_ordering=True,
    )
    result = validate_v3_7_graph_compatibility(
        replace(
            compatibility_map,
            node_results=(ordered_node,) + compatibility_map.node_results[1:],
            edge_results=(traversal_edge,) + compatibility_map.edge_results[1:],
            graph_execution_enabled=True,
            routing_enabled=True,
            scheduling_enabled=True,
            dispatch_enabled=True,
        )
    )

    assert result.validation_status == V37_COMPATIBILITY_VALIDATION_BLOCKED
    assert result.non_execution_guarantee_preserved is False
    assert V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY in _statuses(result)
