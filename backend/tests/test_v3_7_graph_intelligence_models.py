from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from app.runtime_orchestration.v3_7_graph_intelligence_models import (
    V37_INTELLIGENCE_FINDING_CLASSIFICATIONS,
    export_v3_7_graph_intelligence_counts,
    hash_v3_7_graph_planning_intelligence_aggregation,
    serialize_v3_7_graph_planning_intelligence_aggregation,
    validate_v3_7_graph_intelligence_hash_stability,
    validate_v3_7_graph_intelligence_serialization_stability,
)
from scripts.report_v3_7_graph_planning_intelligence_aggregation import (
    build_v3_7_graph_planning_intelligence_aggregation_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_intelligence_finding_classifications_are_explicit():
    assert V37_INTELLIGENCE_FINDING_CLASSIFICATIONS == (
        "governance_visible",
        "compatibility_visible",
        "evaluation_visible",
        "session_visible",
        "scenario_visible",
        "blocked_visible",
        "unsupported_visible",
        "prohibited_visible",
        "unknown_visible",
        "experimental_visible",
        "continuity_warning_visible",
        "provenance_continuity_visible",
        "explainability_continuity_visible",
        "replay_continuity_visible",
        "rollback_continuity_visible",
    )


def test_intelligence_aggregation_is_immutable_and_non_executable():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()

    with pytest.raises(FrozenInstanceError):
        aggregation.routing_enabled = True

    assert aggregation.aggregation_is_non_executable is True
    assert aggregation.planning_evidence_summarization_only is True
    assert aggregation.aggregated_insights_are_not_recommendations is True
    assert aggregation.aggregated_insights_do_not_authorize_execution is True
    assert aggregation.aggregation_does_not_select_graph_paths is True
    assert aggregation.routing_enabled is False
    assert aggregation.scheduling_enabled is False
    assert aggregation.dispatch_enabled is False
    assert aggregation.graph_traversal_execution_enabled is False
    assert aggregation.recommendation_enabled is False


def test_intelligence_serialization_and_hash_are_deterministic():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    reordered = replace(
        aggregation,
        metadata=tuple(reversed(aggregation.metadata)),
        evidence_sources=tuple(reversed(aggregation.evidence_sources)),
        findings=tuple(reversed(aggregation.findings)),
        insights=tuple(reversed(aggregation.insights)),
        replay_evidence=tuple(reversed(aggregation.replay_evidence)),
        rollback_continuity_references=tuple(reversed(aggregation.rollback_continuity_references)),
    )

    assert serialize_v3_7_graph_planning_intelligence_aggregation(aggregation) == serialize_v3_7_graph_planning_intelligence_aggregation(reordered)
    assert hash_v3_7_graph_planning_intelligence_aggregation(aggregation) == hash_v3_7_graph_planning_intelligence_aggregation(reordered)
    assert validate_v3_7_graph_intelligence_serialization_stability(aggregation)["stable"] is True
    assert validate_v3_7_graph_intelligence_hash_stability(aggregation)["stable"] is True
    assert json.loads(serialize_v3_7_graph_planning_intelligence_aggregation(aggregation))["dispatch_enabled"] is False


def test_intelligence_counts_and_report_are_deterministic():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    first = build_v3_7_graph_planning_intelligence_aggregation_report(REPO_ROOT)
    second = build_v3_7_graph_planning_intelligence_aggregation_report(REPO_ROOT)

    assert export_v3_7_graph_intelligence_counts(aggregation) == {
        "aggregation_count": 1,
        "evidence_source_count": 6,
        "finding_count": 15,
        "insight_count": 8,
        "replay_evidence_count": 1,
        "rollback_continuity_reference_count": 1,
    }
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["aggregation_is_non_executable"] is True
    assert first["aggregated_insights_are_not_recommendations"] is True
    assert first["aggregation_does_not_select_graph_paths"] is True
