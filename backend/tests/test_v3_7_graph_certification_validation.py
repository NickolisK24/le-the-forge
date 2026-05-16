from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_certification_evidence import (
    build_v3_7_graph_planning_continuity_certification,
)
from app.runtime_orchestration.v3_7_graph_certification_models import (
    V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED,
)
from app.runtime_orchestration.v3_7_graph_certification_validation import (
    V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED,
    V37_GRAPH_CERTIFICATION_VALIDATION_STABLE,
    V37_CERTIFICATION_VALIDATION_BLOCKED_BY_DUPLICATE_CERTIFICATION,
    V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY,
    V37_CERTIFICATION_VALIDATION_BLOCKED_BY_HIDDEN_STATE,
    V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INCOMPLETE_SCOPE,
    validate_v3_7_graph_certification,
)


def test_default_certification_validation_is_stable_and_fail_visible():
    result = validate_v3_7_graph_certification()

    assert result.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_STABLE
    assert result.valid is True
    assert result.error_count == 0
    assert result.visibility_finding_count == 11
    assert result.provenance_continuity_preserved is True
    assert result.explainability_continuity_preserved is True
    assert result.replay_continuity_preserved is True
    assert result.rollback_continuity_preserved is True
    assert result.certification_non_executable is True
    assert result.certified_continuity_does_not_authorize_execution is True
    assert result.certification_does_not_mark_runtime_execution_readiness is True


def test_validation_detects_duplicate_certification_identity():
    certification = build_v3_7_graph_planning_continuity_certification()
    result = validate_v3_7_graph_certification((certification, certification))

    assert result.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED
    assert result.duplicate_certification_identity_count == 1
    assert any(finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_DUPLICATE_CERTIFICATION for finding in result.findings)


def test_validation_detects_incomplete_scope():
    certification = build_v3_7_graph_planning_continuity_certification()
    filtered_scope = replace(
        certification.scope,
        references=tuple(reference for reference in certification.scope.references if reference.reference_type != "integrity"),
    )
    result = validate_v3_7_graph_certification((replace(certification, scope=filtered_scope),))

    assert result.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED
    assert result.incomplete_scope_count >= 1
    assert any(finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_INCOMPLETE_SCOPE for finding in result.findings)


def test_validation_detects_hidden_risk_states():
    certification = build_v3_7_graph_planning_continuity_certification()
    hidden_findings = tuple(
        replace(finding, hidden=True, active_violation=True, blocks_certification=True)
        if finding.finding_classification == V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED
        else finding
        for finding in certification.findings
    )
    result = validate_v3_7_graph_certification((replace(certification, findings=hidden_findings),))

    assert result.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED
    assert result.hidden_prohibited_finding_count == 1
    assert result.hidden_unsupported_finding_count == 1
    assert result.hidden_unknown_finding_count == 1
    assert any(finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_HIDDEN_STATE for finding in result.findings)


def test_validation_detects_execution_boundary_failure():
    certification = build_v3_7_graph_planning_continuity_certification()
    result = validate_v3_7_graph_certification((replace(certification, execution_readiness_approval_enabled=True),))

    assert result.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_BLOCKED
    assert result.execution_boundary_certification_failure_count == 1
    assert any(finding.status == V37_CERTIFICATION_VALIDATION_BLOCKED_BY_EXECUTION_BOUNDARY for finding in result.findings)
