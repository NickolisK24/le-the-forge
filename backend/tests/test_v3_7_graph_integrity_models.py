from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from app.runtime_orchestration.v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from app.runtime_orchestration.v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_CLASSIFICATIONS,
    V37_INTEGRITY_OUTCOMES,
    export_v3_7_graph_integrity_counts,
    hash_v3_7_graph_integrity_enforcement_result,
    serialize_v3_7_graph_integrity_enforcement_result,
    validate_v3_7_graph_integrity_hash_stability,
    validate_v3_7_graph_integrity_serialization_stability,
)
from scripts.report_v3_7_graph_planning_integrity_enforcement import (
    build_v3_7_graph_planning_integrity_enforcement_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_integrity_outcomes_and_findings_are_explicit():
    assert V37_INTEGRITY_OUTCOMES == (
        "valid",
        "invalid",
        "blocked",
        "warning",
        "audit_failed",
    )
    assert V37_INTEGRITY_FINDING_CLASSIFICATIONS == (
        "integrity_valid",
        "integrity_invalid",
        "integrity_blocked",
        "integrity_warning",
        "continuity_violation",
        "provenance_violation",
        "explainability_violation",
        "replay_violation",
        "rollback_violation",
        "execution_boundary_violation",
        "hidden_prohibited_state",
        "hidden_unsupported_state",
        "hidden_unknown_state",
    )


def test_integrity_enforcement_is_immutable_and_non_executable():
    result = enforce_v3_7_graph_planning_integrity()

    with pytest.raises(FrozenInstanceError):
        result.routing_enabled = True

    assert result.integrity_enforcement_is_non_executable is True
    assert result.integrity_enforcement_validates_planning_evidence_only is True
    assert result.valid_integrity_does_not_authorize_execution is True
    assert result.blocked_integrity_does_not_perform_runtime_blocking is True
    assert result.graph_execution_enabled is False
    assert result.routing_enabled is False
    assert result.scheduling_enabled is False
    assert result.dispatch_enabled is False
    assert result.traversal_logic_enabled is False
    assert result.runtime_control_system_enabled is False


def test_integrity_serialization_and_hash_are_deterministic():
    result = enforce_v3_7_graph_planning_integrity()
    reordered = replace(
        result,
        metadata=tuple(reversed(result.metadata)),
        evidence_source_references=tuple(reversed(result.evidence_source_references)),
        evidence_source_types=tuple(reversed(result.evidence_source_types)),
        findings=tuple(reversed(result.findings)),
        replay_evidence=tuple(reversed(result.replay_evidence)),
        rollback_continuity_references=tuple(reversed(result.rollback_continuity_references)),
    )

    assert serialize_v3_7_graph_integrity_enforcement_result(result) == serialize_v3_7_graph_integrity_enforcement_result(reordered)
    assert hash_v3_7_graph_integrity_enforcement_result(result) == hash_v3_7_graph_integrity_enforcement_result(reordered)
    assert validate_v3_7_graph_integrity_serialization_stability(result)["stable"] is True
    assert validate_v3_7_graph_integrity_hash_stability(result)["stable"] is True
    assert json.loads(serialize_v3_7_graph_integrity_enforcement_result(result))["dispatch_enabled"] is False


def test_integrity_counts_and_report_are_deterministic():
    result = enforce_v3_7_graph_planning_integrity()
    first = build_v3_7_graph_planning_integrity_enforcement_report(REPO_ROOT)
    second = build_v3_7_graph_planning_integrity_enforcement_report(REPO_ROOT)

    assert export_v3_7_graph_integrity_counts(result) == {
        "integrity_policy_count": 1,
        "enforcement_result_count": 1,
        "evidence_source_count": 7,
        "integrity_finding_count": 13,
        "blocked_finding_count": 0,
        "warning_finding_count": 1,
        "replay_evidence_count": 1,
        "rollback_continuity_reference_count": 1,
    }
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["integrity_enforcement_is_non_executable"] is True
    assert first["valid_integrity_does_not_authorize_execution"] is True
    assert first["routing_enabled"] is False
