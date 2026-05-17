from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_transition.transition_compatibility_engine import (  # noqa: E402
    default_transition_compatibility_inputs,
    evaluate_v3_9_transition_compatibility,
)
from runtime_transition.transition_compatibility_models import (  # noqa: E402
    COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PROHIBITED,
    COMPATIBILITY_CLASSIFICATION_UNKNOWN,
    COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
    COMPATIBILITY_CONFLICT_BOUNDARY,
    COMPATIBILITY_CONFLICT_CONTINUITY,
    COMPATIBILITY_CONFLICT_EXPLAINABILITY,
    COMPATIBILITY_CONFLICT_MISSING_EVIDENCE,
    COMPATIBILITY_CONFLICT_PROHIBITED_STATE,
    COMPATIBILITY_CONFLICT_PROVENANCE,
    COMPATIBILITY_CONFLICT_TRANSITION_STATE,
    COMPATIBILITY_CONFLICT_TYPES,
    COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE,
    TransitionCompatibilityInput,
    transition_compatibility_finding_id,
)
from runtime_transition.transition_compatibility_reporting import (  # noqa: E402
    build_v3_9_transition_compatibility_intelligence_report,
)
from runtime_transition.transition_compatibility_serialization import (  # noqa: E402
    hash_transition_compatibility_report,
    serialize_transition_compatibility_report,
    validate_transition_compatibility_hash_stability,
    validate_transition_compatibility_serialization_stability,
)
from runtime_transition.transition_compatibility_validation import (  # noqa: E402
    validate_transition_compatibility_report,
)


def _default_input(input_id: str) -> TransitionCompatibilityInput:
    inputs = {source.input_id: source for source in default_transition_compatibility_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = evaluate_v3_9_transition_compatibility((_default_input(input_id),))
    assert len(report.findings) == 1
    return report.findings[0].classification


def test_v3_9_transition_compatibility_report_is_immutable_and_non_executable():
    report = evaluate_v3_9_transition_compatibility()

    with pytest.raises(FrozenInstanceError):
        report.orchestration_execution_enabled = True

    assert report.non_executable is True
    assert report.transition_execution_enabled is False
    assert report.orchestration_execution_enabled is False
    assert report.orchestration_traversal_enabled is False
    assert report.routing_enabled is False
    assert report.scheduling_enabled is False
    assert report.dispatch_enabled is False
    assert report.orchestration_engine_enabled is False
    assert report.runtime_mutation_enabled is False
    assert report.autonomous_behavior_enabled is False
    assert report.optimization_enabled is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False
    assert report.approval_enabled is False
    assert report.authorization_enabled is False
    assert report.callable_orchestration_flow_enabled is False
    assert report.transition_handler_enabled is False
    assert report.orchestration_evaluator_enabled is False
    assert report.runtime_state_machine_enabled is False
    assert report.production_execution_pathway_enabled is False
    assert report.hidden_fallback_enabled is False
    assert report.silent_correction_enabled is False


def test_v3_9_transition_compatibility_classifies_compatible_transition():
    report = evaluate_v3_9_transition_compatibility(
        (_default_input("compatible_transition_compatibility"),)
    )
    finding = report.findings[0]

    assert finding.classification == COMPATIBILITY_CLASSIFICATION_COMPATIBLE
    assert finding.compatible_state is True
    assert finding.hidden is False
    assert finding.conflicts == ()
    assert finding.reason == "transition states are compatible for deterministic evidence reasoning only"
    assert finding.evidence.evidence_id
    assert finding.evidence.provenance_reference_ids
    assert finding.evidence.continuity_reference_ids


def test_v3_9_transition_compatibility_classifies_required_non_compatible_states():
    assert (
        _single_classification("incompatible_transition_compatibility")
        == COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE
    )
    assert (
        _single_classification("partially_compatible_transition_compatibility")
        == COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE
    )
    assert (
        _single_classification("unsupported_transition_compatibility")
        == COMPATIBILITY_CLASSIFICATION_UNSUPPORTED
    )
    assert (
        _single_classification("prohibited_transition_compatibility")
        == COMPATIBILITY_CLASSIFICATION_PROHIBITED
    )
    assert _single_classification("unknown_transition_compatibility") == COMPATIBILITY_CLASSIFICATION_UNKNOWN
    assert _single_classification("incomplete_transition_compatibility") == COMPATIBILITY_CLASSIFICATION_INCOMPLETE


def test_v3_9_transition_compatibility_non_compatible_findings_are_fail_visible():
    report = evaluate_v3_9_transition_compatibility()
    non_compatible = [
        finding
        for finding in report.findings
        if finding.classification != COMPATIBILITY_CLASSIFICATION_COMPATIBLE
    ]

    assert len(non_compatible) == 6
    for finding in non_compatible:
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.compatible_state is False
        assert finding.reason
        assert finding.evidence.evidence_id
        assert finding.evidence.provenance_reference_ids
        assert finding.evidence.continuity_reference_ids
        assert finding.conflicts
        assert all(conflict.fail_visible for conflict in finding.conflicts)
        assert all(conflict.hidden is False for conflict in finding.conflicts)


def test_v3_9_transition_compatibility_conflict_categories_are_visible():
    report = evaluate_v3_9_transition_compatibility()
    conflict_types = {conflict.conflict_type for conflict in report.conflicts}

    assert conflict_types == set(COMPATIBILITY_CONFLICT_TYPES)
    assert report.summary.provenance_conflict_count == 1
    assert report.summary.continuity_conflict_count == 1
    assert report.summary.boundary_conflict_count >= 2
    assert any(conflict.conflict_type == COMPATIBILITY_CONFLICT_TRANSITION_STATE for conflict in report.conflicts)
    assert any(conflict.conflict_type == COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE for conflict in report.conflicts)
    assert any(conflict.conflict_type == COMPATIBILITY_CONFLICT_PROHIBITED_STATE for conflict in report.conflicts)
    assert any(conflict.conflict_type == COMPATIBILITY_CONFLICT_EXPLAINABILITY for conflict in report.conflicts)
    assert any(conflict.conflict_type == COMPATIBILITY_CONFLICT_MISSING_EVIDENCE for conflict in report.conflicts)
    assert all(conflict.visibility_status == "fail_visible" for conflict in report.conflicts)


def test_v3_9_transition_compatibility_ordering_ids_and_equality_are_deterministic():
    inputs = default_transition_compatibility_inputs()
    first = evaluate_v3_9_transition_compatibility(tuple(reversed(inputs)))
    second = evaluate_v3_9_transition_compatibility(inputs)

    assert first == second
    assert tuple(finding.input_id for finding in first.findings) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(conflict.conflict_id for conflict in first.conflicts) == tuple(
        conflict.conflict_id for conflict in second.conflicts
    )
    assert tuple(conflict.deterministic_order for conflict in first.conflicts) == tuple(
        sorted(conflict.deterministic_order for conflict in first.conflicts)
    )
    for finding in first.findings:
        assert finding.finding_id == transition_compatibility_finding_id(
            finding.classification,
            finding.input_id,
        )
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)
    assert len({conflict.conflict_id for conflict in first.conflicts}) == len(first.conflicts)


def test_v3_9_transition_compatibility_serialization_hashing_and_equality_are_stable():
    first = evaluate_v3_9_transition_compatibility()
    second = evaluate_v3_9_transition_compatibility()

    assert first == second
    assert serialize_transition_compatibility_report(first) == serialize_transition_compatibility_report(second)
    assert hash_transition_compatibility_report(first) == hash_transition_compatibility_report(second)
    assert validate_transition_compatibility_serialization_stability(first)["stable"] is True
    assert validate_transition_compatibility_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_compatibility_report(first))["non_executable"] is True


def test_v3_9_transition_compatibility_replay_rollback_and_provenance_are_preserved():
    report = evaluate_v3_9_transition_compatibility()
    validation = validate_transition_compatibility_report(report)

    assert validation["replay_safe_compatibility_evidence_count"] == validation["finding_count"]
    assert validation["rollback_safe_compatibility_evidence_count"] == validation["finding_count"]
    assert validation["provenance_safe_compatibility_evidence_count"] == validation["finding_count"]
    assert validation["explainability_safe_compatibility_evidence_count"] == validation["finding_count"]
    assert all(finding.replay_safe for finding in report.findings)
    assert all(finding.rollback_safe for finding in report.findings)
    assert all(finding.provenance_preserved for finding in report.findings)
    assert all(finding.explainability_safe for finding in report.findings)


def test_v3_9_transition_compatibility_detects_execution_boundary_violation_requests():
    report = evaluate_v3_9_transition_compatibility(
        (_default_input("prohibited_transition_compatibility"),)
    )
    finding = report.findings[0]
    validation = validate_transition_compatibility_report(report)

    assert finding.classification == COMPATIBILITY_CLASSIFICATION_PROHIBITED
    assert finding.execution_boundary_violation_detected is True
    assert validation["execution_boundary_violation_count"] == 3
    assert validation["report_execution_capability_violation_count"] == 0
    assert validation["non_execution_confirmation"] is True


def test_v3_9_transition_compatibility_validation_detects_hidden_conflicts():
    report = evaluate_v3_9_transition_compatibility(
        (_default_input("incompatible_transition_compatibility"),)
    )
    hidden_conflict = replace(report.conflicts[0], hidden=True)
    hidden_report = replace(report, conflicts=(hidden_conflict, *report.conflicts[1:]))
    validation = validate_transition_compatibility_report(hidden_report)

    assert validation["valid"] is False
    assert validation["hidden_conflict_count"] == 1


def test_v3_9_transition_compatibility_report_contains_required_counts_and_guarantees():
    report = build_v3_9_transition_compatibility_intelligence_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["compatible_count"] == 1
    assert report["summary"]["incompatible_count"] == 1
    assert report["summary"]["partially_compatible_count"] == 1
    assert report["summary"]["unsupported_count"] == 1
    assert report["summary"]["prohibited_count"] == 1
    assert report["summary"]["unknown_count"] == 1
    assert report["summary"]["incomplete_count"] == 1
    assert report["summary"]["compatibility_conflict_count"] >= 8
    assert report["summary"]["provenance_conflict_count"] == 1
    assert report["summary"]["continuity_conflict_count"] == 1
    assert report["summary"]["boundary_conflict_count"] >= 2
    assert report["summary"]["hidden_conflict_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 3
    assert report["summary"]["report_execution_capability_violation_count"] == 0
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["explainability_verified"] is True
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["summary"]["source_artifact_continuity_preserved"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_traversal_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
