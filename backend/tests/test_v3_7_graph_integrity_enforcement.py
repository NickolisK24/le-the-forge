from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_integrity_enforcement import (
    enforce_v3_7_graph_planning_integrity,
    graph_integrity_enforcement_identities_are_unique,
    graph_integrity_enforcement_identity_key,
)
from app.runtime_orchestration.v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION,
    V37_INTEGRITY_OUTCOME_BLOCKED,
    V37_INTEGRITY_OUTCOME_VALID,
)
from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import (
    build_v3_7_graph_planning_intelligence_aggregation,
)


def test_default_integrity_enforcement_is_valid_and_cross_system():
    result = enforce_v3_7_graph_planning_integrity()

    assert result.enforcement_outcome == V37_INTEGRITY_OUTCOME_VALID
    assert result.identity.stable_identity_key == graph_integrity_enforcement_identity_key(result.identity)
    assert graph_integrity_enforcement_identities_are_unique((result.identity,)) is True
    assert {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
        "aggregation",
    }.issubset(set(result.evidence_source_types))
    assert result.integrity_enforcement_is_non_executable is True


def test_integrity_enforcement_blocks_execution_boundary_violations():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    result = enforce_v3_7_graph_planning_integrity(replace(aggregation, routing_enabled=True))
    execution_boundary = next(
        finding
        for finding in result.findings
        if finding.finding_classification == V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION
    )

    assert result.enforcement_outcome == V37_INTEGRITY_OUTCOME_BLOCKED
    assert execution_boundary.active_violation is True
    assert execution_boundary.blocks_validation is True


def test_integrity_enforcement_does_not_create_execution_controls():
    result = enforce_v3_7_graph_planning_integrity()

    assert result.orchestration_authorization_enabled is False
    assert result.path_selection_enabled is False
    assert result.scenario_selection_enabled is False
    assert result.execution_gates_enabled is False
    assert result.callable_orchestration_flows_enabled is False
