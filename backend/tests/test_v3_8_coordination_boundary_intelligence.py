from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest


APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_boundary_intelligence import (  # noqa: E402
    audit_v3_8_coordination_boundary_intelligence,
)
from runtime_coordination.coordination_boundary_models import (  # noqa: E402
    BOUNDARY_CLASSIFICATION_EXPERIMENTAL,
    BOUNDARY_CLASSIFICATION_NON_EXECUTABLE,
    BOUNDARY_CLASSIFICATION_PLANNING_ONLY,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SUPPORTED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_VISIBILITY_FAIL_VISIBLE,
    V3_8_BOUNDARY_AUDIT_STABLE,
    boundary_finding_id,
    hash_v3_8_boundary_audit,
    serialize_v3_8_boundary_audit,
    validate_v3_8_boundary_hash_stability,
    validate_v3_8_boundary_serialization_stability,
)
from scripts.report_v3_8_coordination_boundary_intelligence import (  # noqa: E402
    build_v3_8_coordination_boundary_intelligence_report,
)


def test_v3_8_boundary_audit_is_immutable_and_non_executable():
    audit = audit_v3_8_coordination_boundary_intelligence()

    with pytest.raises(FrozenInstanceError):
        audit.orchestration_execution_enabled = True

    assert audit.audit_status == V3_8_BOUNDARY_AUDIT_STABLE
    assert audit.non_executable is True
    assert audit.coordination_execution_enabled is False
    assert audit.orchestration_execution_enabled is False
    assert audit.routing_enabled is False
    assert audit.scheduling_enabled is False
    assert audit.dispatch_enabled is False
    assert audit.traversal_execution_enabled is False
    assert audit.optimization_enabled is False
    assert audit.recommendation_enabled is False
    assert audit.execution_authorization_enabled is False
    assert audit.callable_coordination_flow_enabled is False
    assert audit.persistent_runtime_mutation_enabled is False
    assert audit.hidden_transition_enabled is False
    assert audit.silent_fallback_enabled is False
    assert audit.validation_totals["execution_boundary_violation_count"] == 0


def test_v3_8_boundary_serialization_hashing_and_output_are_stable():
    first = audit_v3_8_coordination_boundary_intelligence()
    second = audit_v3_8_coordination_boundary_intelligence()

    assert first == second
    assert serialize_v3_8_boundary_audit(first) == serialize_v3_8_boundary_audit(second)
    assert hash_v3_8_boundary_audit(first) == hash_v3_8_boundary_audit(second)
    assert validate_v3_8_boundary_serialization_stability(first)["stable"] is True
    assert validate_v3_8_boundary_hash_stability(first)["stable"] is True
    assert json.loads(serialize_v3_8_boundary_audit(first))["non_executable"] is True


def test_v3_8_boundary_finding_ids_are_deterministic():
    audit = audit_v3_8_coordination_boundary_intelligence()

    finding_ids = tuple(finding.finding_id for finding in audit.findings)
    assert len(finding_ids) == len(set(finding_ids))
    for finding in audit.findings:
        assert finding.finding_id == boundary_finding_id(
            finding.boundary_classification,
            finding.boundary_id,
        )
        assert finding.source_coordination_reference == audit.source_foundation_id
        assert finding.provenance_reference
        assert finding.replay_safe_evidence
        assert finding.rollback_safe_evidence
        assert finding.non_execution_confirmation is True


def test_v3_8_boundary_counts_cover_required_classifications():
    audit = audit_v3_8_coordination_boundary_intelligence()

    assert audit.validation_totals["boundary_count"] == 15
    assert audit.validation_totals["finding_count"] == 15
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_SUPPORTED] == 3
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_UNSUPPORTED] == 3
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_PROHIBITED] == 4
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_UNKNOWN] == 2
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_EXPERIMENTAL] == 1
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_PLANNING_ONLY] == 1
    assert audit.classification_counts[BOUNDARY_CLASSIFICATION_NON_EXECUTABLE] == 1


def test_v3_8_boundary_unsupported_prohibited_and_unknown_states_are_fail_visible():
    audit = audit_v3_8_coordination_boundary_intelligence()

    unsupported = [
        record for record in audit.boundary_records if record.classification == BOUNDARY_CLASSIFICATION_UNSUPPORTED
    ]
    prohibited = [
        record for record in audit.boundary_records if record.classification == BOUNDARY_CLASSIFICATION_PROHIBITED
    ]
    unknown = [
        record for record in audit.boundary_records if record.classification == BOUNDARY_CLASSIFICATION_UNKNOWN
    ]

    assert all(record.visibility_status == BOUNDARY_VISIBILITY_FAIL_VISIBLE for record in unsupported)
    assert all(record.visibility_status == BOUNDARY_VISIBILITY_FAIL_VISIBLE for record in prohibited)
    assert all(record.visibility_status == BOUNDARY_VISIBILITY_FAIL_VISIBLE for record in unknown)
    assert all(record.fail_visible and not record.hidden for record in unsupported + prohibited + unknown)
    assert audit.validation_totals["fail_visible_unsupported_count"] == 3
    assert audit.validation_totals["fail_visible_prohibited_count"] == 4
    assert audit.validation_totals["fail_visible_unknown_count"] == 2


def test_v3_8_boundary_supported_states_do_not_hide_risk():
    audit = audit_v3_8_coordination_boundary_intelligence()

    supported = [
        record for record in audit.boundary_records if record.classification == BOUNDARY_CLASSIFICATION_SUPPORTED
    ]

    assert supported
    assert all(record.supported_risk_hidden is False for record in supported)
    assert all(record.fail_visible and not record.hidden for record in supported)
    assert audit.validation_totals["supported_hidden_risk_count"] == 0
    assert audit.validation_totals["hidden_finding_count"] == 0


def test_v3_8_boundary_replay_rollback_and_provenance_are_preserved():
    audit = audit_v3_8_coordination_boundary_intelligence()

    assert audit.validation_totals["replay_safe_evidence_count"] == audit.validation_totals["finding_count"]
    assert audit.validation_totals["rollback_safe_evidence_count"] == audit.validation_totals["finding_count"]
    assert audit.validation_totals["provenance_continuity_count"] == audit.validation_totals["finding_count"]
    assert all(record.evidence.replay_safe for record in audit.boundary_records)
    assert all(record.evidence.rollback_safe for record in audit.boundary_records)
    assert all(record.evidence.provenance_preserved for record in audit.boundary_records)
    assert all(finding.replay_safe_evidence for finding in audit.findings)
    assert all(finding.rollback_safe_evidence for finding in audit.findings)


def test_v3_8_boundary_report_contains_required_totals_and_guarantees():
    report = build_v3_8_coordination_boundary_intelligence_report()

    assert report["summary"]["audit_status"] == V3_8_BOUNDARY_AUDIT_STABLE
    assert report["summary"]["boundary_count"] == 15
    assert report["summary"]["finding_count"] == 15
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["unsupported_fail_visible"] is True
    assert report["summary"]["prohibited_fail_visible"] is True
    assert report["summary"]["unknown_fail_visible"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["boundary_totals"]["supported_boundary_count"] == 3
    assert report["boundary_totals"]["unsupported_boundary_count"] == 3
    assert report["boundary_totals"]["prohibited_boundary_count"] == 4
    assert report["boundary_totals"]["unknown_boundary_count"] == 2
    assert report["boundary_totals"]["experimental_boundary_count"] == 1
    assert report["boundary_totals"]["planning_only_boundary_count"] == 1
    assert report["boundary_totals"]["non_executable_boundary_count"] == 1
    assert report["boundary_totals"]["execution_boundary_violation_count"] == 0

