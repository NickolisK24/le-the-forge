from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_certification_evidence import (
    build_v3_7_graph_planning_continuity_certification,
)
from app.runtime_orchestration.v3_7_graph_certification_models import (
    V37_CERTIFICATION_FINDING_CLASSIFICATIONS,
    V37_CERTIFICATION_OUTCOMES,
    export_v3_7_graph_certification_counts,
    hash_v3_7_graph_planning_continuity_certification,
    serialize_v3_7_graph_planning_continuity_certification,
    validate_v3_7_graph_certification_hash_stability,
    validate_v3_7_graph_certification_serialization_stability,
)
from scripts.report_v3_7_graph_planning_continuity_certification import (
    build_v3_7_graph_planning_continuity_certification_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_certification_outcomes_and_findings_are_explicit():
    assert V37_CERTIFICATION_OUTCOMES == (
        "certified",
        "uncertified",
        "blocked",
        "warning",
        "audit_failed",
    )
    assert V37_CERTIFICATION_FINDING_CLASSIFICATIONS == (
        "certification_passed",
        "certification_failed",
        "certification_blocked",
        "certification_warning",
        "scope_complete",
        "scope_incomplete",
        "continuity_certified",
        "continuity_uncertified",
        "provenance_certified",
        "provenance_uncertified",
        "explainability_certified",
        "explainability_uncertified",
        "replay_certified",
        "replay_uncertified",
        "rollback_certified",
        "rollback_uncertified",
        "integrity_certified",
        "integrity_uncertified",
        "execution_boundary_certified",
        "execution_boundary_uncertified",
        "hidden_risk_state_detected",
    )


def test_certification_is_immutable_and_non_executable():
    certification = build_v3_7_graph_planning_continuity_certification()

    with pytest.raises(FrozenInstanceError):
        certification.routing_enabled = True

    assert certification.certification_is_non_executable is True
    assert certification.certification_validates_planning_continuity_only is True
    assert certification.certified_continuity_does_not_authorize_execution is True
    assert certification.certification_does_not_mark_runtime_execution_readiness is True
    assert certification.graph_execution_enabled is False
    assert certification.routing_enabled is False
    assert certification.scheduling_enabled is False
    assert certification.dispatch_enabled is False
    assert certification.traversal_logic_enabled is False
    assert certification.execution_readiness_approval_enabled is False


def test_certification_serialization_and_hash_are_deterministic():
    certification = build_v3_7_graph_planning_continuity_certification()
    reordered = replace(
        certification,
        metadata=tuple(reversed(certification.metadata)),
        findings=tuple(reversed(certification.findings)),
        replay_evidence=tuple(reversed(certification.replay_evidence)),
        rollback_continuity_references=tuple(reversed(certification.rollback_continuity_references)),
    )

    assert serialize_v3_7_graph_planning_continuity_certification(certification) == serialize_v3_7_graph_planning_continuity_certification(reordered)
    assert hash_v3_7_graph_planning_continuity_certification(certification) == hash_v3_7_graph_planning_continuity_certification(reordered)
    assert validate_v3_7_graph_certification_serialization_stability(certification)["stable"] is True
    assert validate_v3_7_graph_certification_hash_stability(certification)["stable"] is True
    assert json.loads(serialize_v3_7_graph_planning_continuity_certification(certification))["certification_does_not_mark_runtime_execution_readiness"] is True


def test_certification_counts_and_report_are_deterministic():
    certification = build_v3_7_graph_planning_continuity_certification()
    first = build_v3_7_graph_planning_continuity_certification_report(REPO_ROOT)
    second = build_v3_7_graph_planning_continuity_certification_report(REPO_ROOT)

    assert export_v3_7_graph_certification_counts(certification) == {
        "certification_count": 1,
        "scope_count": 1,
        "scope_reference_count": 8,
        "certification_evidence_count": 1,
        "finding_count": 21,
        "blocked_finding_count": 0,
        "replay_evidence_count": 1,
        "rollback_continuity_reference_count": 1,
    }
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["certification_is_non_executable"] is True
    assert first["certified_continuity_does_not_authorize_execution"] is True
    assert first["certification_does_not_mark_runtime_execution_readiness"] is True
