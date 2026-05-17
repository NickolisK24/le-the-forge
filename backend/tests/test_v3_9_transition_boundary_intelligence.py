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

from runtime_transition.transition_boundary_classifier import (  # noqa: E402
    classify_v3_9_transition_boundaries,
    default_transition_boundary_inputs,
)
from runtime_transition.transition_boundary_models import (  # noqa: E402
    BOUNDARY_CLASSIFICATION_BLOCKED,
    BOUNDARY_CLASSIFICATION_INCOMPLETE,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SAFE,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_VISIBILITY_FAIL_VISIBLE,
    TransitionBoundaryInput,
    transition_boundary_finding_id,
)
from runtime_transition.transition_boundary_report import (  # noqa: E402
    build_v3_9_transition_boundary_intelligence_report,
)
from runtime_transition.transition_boundary_serialization import (  # noqa: E402
    hash_transition_boundary_report,
    serialize_transition_boundary_report,
    validate_transition_boundary_hash_stability,
    validate_transition_boundary_serialization_stability,
)
from runtime_transition.transition_boundary_validation import (  # noqa: E402
    validate_transition_boundary_report,
)


def _default_input(input_id: str) -> TransitionBoundaryInput:
    inputs = {source.input_id: source for source in default_transition_boundary_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = classify_v3_9_transition_boundaries((_default_input(input_id),))
    assert len(report.findings) == 1
    return report.findings[0].classification


def test_v3_9_transition_boundary_report_is_immutable_and_non_executable():
    report = classify_v3_9_transition_boundaries()

    with pytest.raises(FrozenInstanceError):
        report.orchestration_execution_enabled = True

    assert report.non_executable is True
    assert report.transition_execution_enabled is False
    assert report.orchestration_execution_enabled is False
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
    assert report.state_machine_enabled is False
    assert report.production_behavior_enabled is False
    assert report.hidden_fallback_enabled is False
    assert report.silent_correction_enabled is False


def test_v3_9_transition_boundary_classifies_safe_transition():
    report = classify_v3_9_transition_boundaries((_default_input("safe_transition_boundary"),))
    finding = report.findings[0]

    assert finding.classification == BOUNDARY_CLASSIFICATION_SAFE
    assert finding.non_safe_state is False
    assert finding.hidden is False
    assert finding.reason == "transition boundary is safe for deterministic evidence modeling only"
    assert finding.deterministic_evidence_reference
    assert finding.provenance_reference
    assert finding.continuity_reference
    assert finding.explainability_message


def test_v3_9_transition_boundary_classifies_required_non_safe_states():
    assert _single_classification("unsupported_transition_boundary") == BOUNDARY_CLASSIFICATION_UNSUPPORTED
    assert _single_classification("prohibited_transition_boundary") == BOUNDARY_CLASSIFICATION_PROHIBITED
    assert _single_classification("unknown_transition_boundary") == BOUNDARY_CLASSIFICATION_UNKNOWN
    assert _single_classification("incomplete_transition_boundary") == BOUNDARY_CLASSIFICATION_INCOMPLETE
    assert _single_classification("blocked_transition_boundary") == BOUNDARY_CLASSIFICATION_BLOCKED


def test_v3_9_transition_boundary_non_safe_findings_are_fail_visible_and_complete():
    report = classify_v3_9_transition_boundaries()
    non_safe_findings = [
        finding for finding in report.findings if finding.classification != BOUNDARY_CLASSIFICATION_SAFE
    ]

    assert len(non_safe_findings) == 5
    for finding in non_safe_findings:
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.non_safe_state is True
        assert finding.reason
        assert finding.deterministic_evidence_reference
        assert finding.provenance_reference
        assert finding.continuity_reference
        assert finding.explainability_message
        classification = next(
            item for item in report.classifications if item.deterministic_evidence_reference == finding.deterministic_evidence_reference
        )
        assert classification.visibility_status == BOUNDARY_VISIBILITY_FAIL_VISIBLE
        assert classification.fail_visible is True
        assert classification.hidden is False


def test_v3_9_transition_boundary_finding_order_and_ids_are_deterministic():
    inputs = default_transition_boundary_inputs()
    first = classify_v3_9_transition_boundaries(tuple(reversed(inputs)))
    second = classify_v3_9_transition_boundaries(inputs)

    assert first == second
    assert tuple(finding.input_id for finding in first.findings) == tuple(
        sorted(source.input_id for source in inputs)
    )
    for finding in first.findings:
        assert finding.finding_id == transition_boundary_finding_id(
            finding.classification,
            finding.input_id,
        )
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)


def test_v3_9_transition_boundary_serialization_hashing_and_equality_are_stable():
    first = classify_v3_9_transition_boundaries()
    second = classify_v3_9_transition_boundaries()

    assert first == second
    assert serialize_transition_boundary_report(first) == serialize_transition_boundary_report(second)
    assert hash_transition_boundary_report(first) == hash_transition_boundary_report(second)
    assert validate_transition_boundary_serialization_stability(first)["stable"] is True
    assert validate_transition_boundary_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_boundary_report(first))["non_executable"] is True


def test_v3_9_transition_boundary_replay_rollback_and_provenance_are_preserved():
    report = classify_v3_9_transition_boundaries()
    validation = validate_transition_boundary_report(report)

    assert validation["replay_safe_boundary_evidence_count"] == validation["finding_count"]
    assert validation["rollback_safe_boundary_evidence_count"] == validation["finding_count"]
    assert validation["provenance_safe_boundary_evidence_count"] == validation["finding_count"]
    assert validation["explainability_safe_boundary_evidence_count"] == validation["finding_count"]
    assert all(finding.replay_safe for finding in report.findings)
    assert all(finding.rollback_safe for finding in report.findings)
    assert all(finding.provenance_preserved for finding in report.findings)
    assert all(finding.explainability_safe for finding in report.findings)


def test_v3_9_transition_boundary_detects_execution_boundary_violation_requests():
    report = classify_v3_9_transition_boundaries((_default_input("prohibited_transition_boundary"),))
    finding = report.findings[0]
    validation = validate_transition_boundary_report(report)

    assert finding.classification == BOUNDARY_CLASSIFICATION_PROHIBITED
    assert finding.execution_boundary_violation_detected is True
    assert validation["execution_boundary_violation_count"] == 3
    assert validation["report_execution_capability_violation_count"] == 0
    assert validation["non_execution_confirmation"] is True


def test_v3_9_transition_boundary_validation_detects_hidden_non_safe_states():
    report = classify_v3_9_transition_boundaries((_default_input("unsupported_transition_boundary"),))
    hidden_finding = replace(report.findings[0], hidden=True, fail_visible=False)
    hidden_report = replace(
        report,
        findings=(hidden_finding,),
        classifications=(
            replace(report.classifications[0], hidden=True, fail_visible=False),
        ),
    )
    validation = validate_transition_boundary_report(hidden_report)

    assert validation["valid"] is False
    assert validation["hidden_non_safe_state_count"] == 1
    assert validation["non_safe_not_fail_visible_count"] == 1


def test_v3_9_transition_boundary_report_contains_required_counts_and_guarantees():
    report = build_v3_9_transition_boundary_intelligence_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["safe_transition_count"] == 1
    assert report["summary"]["unsupported_behavior_detection_count"] == 1
    assert report["summary"]["prohibited_behavior_detection_count"] == 1
    assert report["summary"]["unknown_behavior_detection_count"] == 1
    assert report["summary"]["incomplete_behavior_detection_count"] == 1
    assert report["summary"]["blocked_behavior_detection_count"] == 1
    assert report["summary"]["hidden_non_safe_state_count"] == 0
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
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
