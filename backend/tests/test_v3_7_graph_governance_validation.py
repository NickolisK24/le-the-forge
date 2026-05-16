from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_governance_domains import DOMAIN_GRAPH_EXECUTION
from app.runtime_orchestration.v3_7_graph_governance_models import (
    V37_EDGE_PROHIBITED_STRUCTURAL,
    V37_EDGE_UNSUPPORTED_STRUCTURAL,
)
from app.runtime_orchestration.v3_7_graph_governance_rules import build_v3_7_graph_governance_map
from app.runtime_orchestration.v3_7_graph_governance_validation import (
    V37_GOVERNANCE_BLOCKED_BY_EXECUTION_CAPABILITY,
    V37_GOVERNANCE_BLOCKED_BY_MISSING_METADATA,
    V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_CROSS_DOMAIN_STRUCTURE,
    V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_EDGE_RELATIONSHIP,
    V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_DOMAIN_CONNECTION,
    V37_GOVERNANCE_PROHIBITED_RELATIONSHIP_VISIBLE,
    V37_GOVERNANCE_UNSUPPORTED_RELATIONSHIP_VISIBLE,
    V37_GOVERNANCE_VALIDATION_BLOCKED,
    V37_GOVERNANCE_VALIDATION_STABLE,
    validate_v3_7_graph_governance,
)


def _statuses(result):
    return {finding.status for finding in result.findings}


def test_default_governance_validation_is_stable_with_visible_relationships():
    result = validate_v3_7_graph_governance(build_v3_7_graph_governance_map())

    assert result.validation_status == V37_GOVERNANCE_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 4
    assert result.prohibited_relationship_visible_count == 2
    assert result.unsupported_relationship_visible_count == 2
    assert result.governance_continuity_preserved is True
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.serialization_stable is True
    assert result.hash_stable is True
    assert result.non_execution_guarantee_preserved is True
    assert V37_GOVERNANCE_PROHIBITED_RELATIONSHIP_VISIBLE in _statuses(result)
    assert V37_GOVERNANCE_UNSUPPORTED_RELATIONSHIP_VISIBLE in _statuses(result)


def test_fail_visible_prohibited_and_unsupported_edge_states():
    governance_map = build_v3_7_graph_governance_map()
    prohibited_edge = replace(
        governance_map.edge_classifications[0],
        governance_classification=V37_EDGE_PROHIBITED_STRUCTURAL,
        prohibited_relationship_ids=("rule_graph_execution_relationship_prohibited",),
    )
    unsupported_edge = replace(
        governance_map.edge_classifications[1],
        governance_classification=V37_EDGE_UNSUPPORTED_STRUCTURAL,
        unsupported_relationship_ids=("rule_runtime_dispatch_relationship_unsupported",),
    )
    result = validate_v3_7_graph_governance(
        replace(governance_map, edge_classifications=(prohibited_edge, unsupported_edge))
    )

    assert result.validation_status == V37_GOVERNANCE_VALIDATION_BLOCKED
    assert result.prohibited_edge_relationship_count == 1
    assert result.unsupported_edge_relationship_count == 1
    assert V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_EDGE_RELATIONSHIP in _statuses(result)
    assert V37_GOVERNANCE_BLOCKED_BY_UNSUPPORTED_DOMAIN_CONNECTION in _statuses(result)


def test_missing_governance_metadata_is_fail_visible():
    governance_map = build_v3_7_graph_governance_map()
    missing_metadata_node = replace(governance_map.node_classifications[0], governance_domain_ids=())
    result = validate_v3_7_graph_governance(
        replace(governance_map, node_classifications=(missing_metadata_node,) + governance_map.node_classifications[1:])
    )

    assert result.validation_status == V37_GOVERNANCE_VALIDATION_BLOCKED
    assert result.missing_metadata_count == 1
    assert V37_GOVERNANCE_BLOCKED_BY_MISSING_METADATA in _statuses(result)


def test_execution_capability_flags_are_rejected():
    governance_map = build_v3_7_graph_governance_map()
    executable_edge = replace(
        governance_map.edge_classifications[0],
        edge_implies_execution_flow=True,
        traversal_execution_enabled=True,
    )
    result = validate_v3_7_graph_governance(
        replace(
            governance_map,
            edge_classifications=(executable_edge,) + governance_map.edge_classifications[1:],
            graph_execution_enabled=True,
            routing_enabled=True,
            scheduling_enabled=True,
            dispatch_enabled=True,
        )
    )

    assert result.validation_status == V37_GOVERNANCE_VALIDATION_BLOCKED
    assert result.non_execution_guarantee_preserved is False
    assert V37_GOVERNANCE_BLOCKED_BY_EXECUTION_CAPABILITY in _statuses(result)


def test_prohibited_cross_domain_structure_is_fail_visible():
    governance_map = build_v3_7_graph_governance_map()
    prohibited_domain_edge = replace(
        governance_map.edge_classifications[0],
        governance_domain_ids=(DOMAIN_GRAPH_EXECUTION,),
    )
    result = validate_v3_7_graph_governance(
        replace(
            governance_map,
            edge_classifications=(prohibited_domain_edge,) + governance_map.edge_classifications[1:],
        )
    )

    assert result.validation_status == V37_GOVERNANCE_VALIDATION_BLOCKED
    assert V37_GOVERNANCE_BLOCKED_BY_PROHIBITED_CROSS_DOMAIN_STRUCTURE in _statuses(result)
