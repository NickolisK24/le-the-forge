from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from app.runtime_orchestration.v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
)
from app.runtime_orchestration.v3_7_graph_integrity_validation import (
    V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED,
    V37_GRAPH_INTEGRITY_VALIDATION_STABLE,
    V37_INTEGRITY_VALIDATION_BLOCKED_BY_DUPLICATE_ENFORCEMENT,
    V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY,
    V37_INTEGRITY_VALIDATION_BLOCKED_BY_HIDDEN_STATE,
    V37_INTEGRITY_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE_SOURCE,
    validate_v3_7_graph_integrity,
)


def test_default_integrity_validation_is_stable_and_fail_visible():
    result = validate_v3_7_graph_integrity()

    assert result.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count >= 4
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.integrity_enforcement_non_executable is True
    assert result.valid_integrity_does_not_authorize_execution is True
    assert result.execution_boundary_violations_blocked is True


def test_validation_detects_duplicate_enforcement_identity():
    enforcement = enforce_v3_7_graph_planning_integrity()
    result = validate_v3_7_graph_integrity((enforcement, enforcement))

    assert result.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED
    assert result.duplicate_enforcement_identity_count == 1
    assert any(finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_DUPLICATE_ENFORCEMENT for finding in result.findings)


def test_validation_detects_missing_scenario_source():
    enforcement = enforce_v3_7_graph_planning_integrity()
    filtered_types = tuple(source_type for source_type in enforcement.evidence_source_types if source_type != "scenario")
    result = validate_v3_7_graph_integrity((replace(enforcement, evidence_source_types=filtered_types),))

    assert result.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED
    assert any(finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_INVALID_EVIDENCE_SOURCE for finding in result.findings)


def test_validation_detects_hidden_risk_states():
    enforcement = enforce_v3_7_graph_planning_integrity()
    hidden_findings = tuple(
        replace(finding, hidden=True)
        if finding.finding_classification
        in (
            V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
            V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
            V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
        )
        else finding
        for finding in enforcement.findings
    )
    result = validate_v3_7_graph_integrity((replace(enforcement, findings=hidden_findings),))

    assert result.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED
    assert any(finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_HIDDEN_STATE for finding in result.findings)
    assert result.hidden_prohibited_finding_count == 1
    assert result.hidden_unsupported_finding_count == 1
    assert result.hidden_unknown_finding_count == 1


def test_validation_detects_execution_boundary_violation():
    enforcement = enforce_v3_7_graph_planning_integrity()
    result = validate_v3_7_graph_integrity((replace(enforcement, routing_enabled=True),))

    assert result.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_BLOCKED
    assert result.execution_boundary_violation_count == 1
    assert any(finding.status == V37_INTEGRITY_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY for finding in result.findings)
