from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_intelligence_models import (
    V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
)
from app.runtime_orchestration.v3_7_graph_intelligence_validation import (
    V37_GRAPH_INTELLIGENCE_VALIDATION_BLOCKED,
    V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE,
    V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_EXECUTION_AUTHORIZATION,
    V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_HIDDEN_STATE,
    V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SCENARIO_EVIDENCE,
    validate_v3_7_graph_intelligence,
)
from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation


def test_default_intelligence_validation_is_stable_and_fail_visible():
    result = validate_v3_7_graph_intelligence()

    assert result.validation_status == V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 3
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.non_execution_guarantee_preserved is True
    assert result.no_execution_recommendation_preserved is True
    assert result.no_runtime_path_selection_preserved is True


def test_validation_detects_missing_scenario_source():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    filtered_sources = tuple(source for source in aggregation.evidence_sources if source.source_type != "scenario")
    result = validate_v3_7_graph_intelligence((replace(aggregation, evidence_sources=filtered_sources),))

    assert result.validation_status == V37_GRAPH_INTELLIGENCE_VALIDATION_BLOCKED
    assert any(finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_INVALID_SCENARIO_EVIDENCE for finding in result.findings)


def test_validation_detects_hidden_unsupported_prohibited_and_unknown_findings():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    hidden_findings = tuple(
        replace(finding, hidden=True)
        if finding.finding_classification in (
            V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
            V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
            V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
        )
        else finding
        for finding in aggregation.findings
    )
    result = validate_v3_7_graph_intelligence((replace(aggregation, findings=hidden_findings),))

    assert result.validation_status == V37_GRAPH_INTELLIGENCE_VALIDATION_BLOCKED
    assert any(finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_HIDDEN_STATE for finding in result.findings)
    assert result.hidden_prohibited_finding_count == 1
    assert result.hidden_unsupported_finding_count == 1
    assert result.hidden_unknown_finding_count == 1


def test_validation_detects_execution_recommendation_and_path_selection():
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    broken_insight = replace(aggregation.insights[0], recommends_execution=True, selects_runtime_path=True)
    result = validate_v3_7_graph_intelligence((replace(aggregation, insights=(broken_insight,) + aggregation.insights[1:]),))

    assert result.validation_status == V37_GRAPH_INTELLIGENCE_VALIDATION_BLOCKED
    assert any(finding.status == V37_INTELLIGENCE_VALIDATION_BLOCKED_BY_EXECUTION_AUTHORIZATION for finding in result.findings)
