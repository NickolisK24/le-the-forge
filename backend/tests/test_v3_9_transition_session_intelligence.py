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

from runtime_transition.transition_session_engine import (  # noqa: E402
    build_v3_9_transition_session,
    default_transition_session_inputs,
)
from runtime_transition.transition_session_models import (  # noqa: E402
    SESSION_CLASSIFICATION_BLOCKED,
    SESSION_CLASSIFICATION_COMPLETE,
    SESSION_CLASSIFICATION_INCOMPLETE,
    SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
    SESSION_CLASSIFICATION_PROHIBITED,
    SESSION_CLASSIFICATION_UNKNOWN,
    SESSION_CLASSIFICATION_UNSUPPORTED,
    SESSION_FINDING_CATEGORIES,
    SESSION_FINDING_COMPLETENESS,
    SESSION_FINDING_CONTINUITY,
    SESSION_FINDING_EVALUATION,
    SESSION_FINDING_EXPLAINABILITY,
    SESSION_FINDING_GOVERNANCE,
    SESSION_FINDING_INTEGRITY,
    SESSION_FINDING_MISSING_EVIDENCE,
    SESSION_FINDING_PROHIBITED,
    SESSION_FINDING_PROVENANCE,
    SESSION_FINDING_UNCERTAINTY,
    SESSION_FINDING_UNSUPPORTED,
    TransitionSessionInput,
)
from runtime_transition.transition_session_reporting import (  # noqa: E402
    build_v3_9_transition_session_intelligence_report,
)
from runtime_transition.transition_session_serialization import (  # noqa: E402
    hash_transition_session_report,
    serialize_transition_session_report,
    validate_transition_session_hash_stability,
    validate_transition_session_serialization_stability,
)
from runtime_transition.transition_session_validation import (  # noqa: E402
    validate_transition_session_report,
)


def _default_input(input_id: str) -> TransitionSessionInput:
    inputs = {source.input_id: source for source in default_transition_session_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = build_v3_9_transition_session((_default_input(input_id),))
    assert len(report.visibilities) == 1
    return report.visibilities[0].classification


def test_v3_9_transition_session_report_is_immutable_and_non_executable():
    report = build_v3_9_transition_session()

    with pytest.raises(FrozenInstanceError):
        report.orchestration_execution_enabled = True

    assert report.non_executable is True
    assert report.orchestration_execution_enabled is False
    assert report.transition_execution_enabled is False
    assert report.graph_traversal_enabled is False
    assert report.routing_enabled is False
    assert report.scheduling_enabled is False
    assert report.dispatch_enabled is False
    assert report.runtime_orchestration_engine_enabled is False
    assert report.runtime_mutation_enabled is False
    assert report.authorization_enabled is False
    assert report.approval_enabled is False
    assert report.optimization_enabled is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False
    assert report.autonomous_behavior_enabled is False
    assert report.callable_orchestration_flow_enabled is False
    assert report.transition_handler_enabled is False
    assert report.runtime_state_machine_enabled is False
    assert report.production_behavior_enabled is False
    assert report.hidden_fallback_enabled is False
    assert report.silent_correction_enabled is False


def test_v3_9_transition_session_classifies_complete_session():
    report = build_v3_9_transition_session((_default_input("complete_transition_session"),))
    visibility = report.visibilities[0]

    assert visibility.classification == SESSION_CLASSIFICATION_COMPLETE
    assert visibility.visibility_status == "visible"
    assert visibility.hidden is False
    assert visibility.reason == "transition session is complete for deterministic evidence recording only"
    assert {finding.finding_category for finding in report.findings} == {
        SESSION_FINDING_COMPLETENESS,
        SESSION_FINDING_EVALUATION,
        SESSION_FINDING_CONTINUITY,
        SESSION_FINDING_PROVENANCE,
        SESSION_FINDING_EXPLAINABILITY,
    }


def test_v3_9_transition_session_classifies_required_non_complete_states():
    assert (
        _single_classification("partially_complete_transition_session")
        == SESSION_CLASSIFICATION_PARTIALLY_COMPLETE
    )
    assert _single_classification("incomplete_transition_session") == SESSION_CLASSIFICATION_INCOMPLETE
    assert _single_classification("blocked_transition_session") == SESSION_CLASSIFICATION_BLOCKED
    assert _single_classification("unsupported_transition_session") == SESSION_CLASSIFICATION_UNSUPPORTED
    assert _single_classification("prohibited_transition_session") == SESSION_CLASSIFICATION_PROHIBITED
    assert _single_classification("unknown_transition_session") == SESSION_CLASSIFICATION_UNKNOWN


def test_v3_9_transition_session_findings_are_fail_visible_and_complete():
    report = build_v3_9_transition_session()

    assert report.findings
    for finding in report.findings:
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.reason
        assert finding.evidence_reference
        assert finding.provenance_reference
        assert finding.continuity_reference
        assert finding.explainability_message
        assert finding.non_execution_confirmation is True

    non_complete = [
        visibility
        for visibility in report.visibilities
        if visibility.classification != SESSION_CLASSIFICATION_COMPLETE
    ]
    assert len(non_complete) == 6
    assert all(visibility.visibility_status == "fail_visible" for visibility in non_complete)
    assert all(visibility.hidden is False for visibility in non_complete)
    assert all(visibility.session_state_visible is True for visibility in non_complete)


def test_v3_9_transition_session_finding_categories_are_visible():
    report = build_v3_9_transition_session()
    categories = {finding.finding_category for finding in report.findings}

    assert categories == set(SESSION_FINDING_CATEGORIES)
    assert SESSION_FINDING_EVALUATION in categories
    assert SESSION_FINDING_CONTINUITY in categories
    assert SESSION_FINDING_PROVENANCE in categories
    assert SESSION_FINDING_EXPLAINABILITY in categories
    assert SESSION_FINDING_GOVERNANCE in categories
    assert SESSION_FINDING_INTEGRITY in categories
    assert SESSION_FINDING_UNSUPPORTED in categories
    assert SESSION_FINDING_PROHIBITED in categories
    assert SESSION_FINDING_MISSING_EVIDENCE in categories
    assert SESSION_FINDING_UNCERTAINTY in categories
    assert SESSION_FINDING_COMPLETENESS in categories
    assert report.summary.governance_finding_count >= 1
    assert report.summary.uncertainty_finding_count >= 1
    assert report.summary.missing_evidence_finding_count >= 1
    assert report.summary.hidden_session_finding_count == 0


def test_v3_9_transition_session_entry_and_finding_ordering_are_deterministic():
    inputs = default_transition_session_inputs()
    first = build_v3_9_transition_session(tuple(reversed(inputs)))
    second = build_v3_9_transition_session(inputs)

    assert first == second
    assert tuple(visibility.input_id for visibility in first.visibilities) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(entry.deterministic_order for entry in first.entries) == tuple(
        sorted(entry.deterministic_order for entry in first.entries)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert tuple(finding.finding_id for finding in first.findings) == tuple(
        finding.finding_id for finding in second.findings
    )
    assert len({entry.entry_id for entry in first.entries}) == len(first.entries)
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)


def test_v3_9_transition_session_serialization_hashing_and_equality_are_stable():
    first = build_v3_9_transition_session()
    second = build_v3_9_transition_session()

    assert first == second
    assert serialize_transition_session_report(first) == serialize_transition_session_report(second)
    assert hash_transition_session_report(first) == hash_transition_session_report(second)
    assert validate_transition_session_serialization_stability(first)["stable"] is True
    assert validate_transition_session_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_session_report(first))["non_executable"] is True


def test_v3_9_transition_session_continuity_and_provenance_are_preserved():
    report = build_v3_9_transition_session()
    validation = validate_transition_session_report(report)

    assert validation["replay_safe_session_finding_count"] == validation["session_finding_count"]
    assert validation["rollback_safe_session_finding_count"] == validation["session_finding_count"]
    assert validation["provenance_safe_session_finding_count"] == validation["session_finding_count"]
    assert validation["explainability_safe_session_finding_count"] == validation["session_finding_count"]
    assert validation["replay_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["rollback_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["provenance_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["explainability_continuity_preserved_count"] == validation["continuity_record_count"]
    assert all(entry.replay_safe for entry in report.entries)
    assert all(entry.rollback_safe for entry in report.entries)
    assert all(entry.provenance_preserved for entry in report.entries)
    assert all(entry.explainability_safe for entry in report.entries)
    assert all(finding.replay_safe for finding in report.findings)
    assert all(finding.rollback_safe for finding in report.findings)
    assert all(finding.provenance_preserved for finding in report.findings)
    assert all(finding.explainability_safe for finding in report.findings)


def test_v3_9_transition_session_detects_execution_boundary_violation_requests():
    report = build_v3_9_transition_session((_default_input("prohibited_transition_session"),))
    validation = validate_transition_session_report(report)

    assert report.visibilities[0].classification == SESSION_CLASSIFICATION_PROHIBITED
    assert validation["execution_boundary_violation_count"] == 3
    assert validation["report_execution_capability_violation_count"] == 0
    assert validation["non_execution_confirmation"] is True
    assert sum(1 for finding in report.findings if finding.execution_boundary_violation_detected) == 3


def test_v3_9_transition_session_validation_detects_hidden_findings():
    report = build_v3_9_transition_session((_default_input("unknown_transition_session"),))
    hidden_finding = replace(report.findings[0], hidden=True, fail_visible=False)
    hidden_report = replace(report, findings=(hidden_finding, *report.findings[1:]))
    validation = validate_transition_session_report(hidden_report)

    assert validation["valid"] is False
    assert validation["hidden_session_finding_count"] == 1
    assert validation["finding_not_fail_visible_count"] == 1


def test_v3_9_transition_session_report_contains_required_counts_and_guarantees():
    report = build_v3_9_transition_session_intelligence_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["complete_count"] == 1
    assert report["summary"]["partially_complete_count"] == 1
    assert report["summary"]["incomplete_count"] == 1
    assert report["summary"]["blocked_count"] == 1
    assert report["summary"]["unsupported_count"] == 1
    assert report["summary"]["prohibited_count"] == 1
    assert report["summary"]["unknown_count"] == 1
    assert report["summary"]["session_finding_count"] >= 11
    assert report["summary"]["evaluation_entry_count"] >= 7
    assert report["summary"]["governance_finding_count"] >= 1
    assert report["summary"]["uncertainty_finding_count"] >= 1
    assert report["summary"]["missing_evidence_finding_count"] >= 1
    assert report["summary"]["hidden_session_finding_count"] == 0
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
    assert report["non_execution_guarantees"]["graph_traversal_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
