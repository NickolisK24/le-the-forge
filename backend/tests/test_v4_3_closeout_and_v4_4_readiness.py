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

from orchestration_governance.v4_3_closeout_readiness_audit import (  # noqa: E402
    build_v4_3_closeout_and_v4_4_readiness_report,
    build_v4_3_closeout_readiness,
    enabled_v4_3_closeout_capability_flags,
    hash_v4_3_closeout_readiness,
    serialize_v4_3_closeout_readiness,
    v4_3_closeout_readiness_equal,
    validate_v4_3_closeout_non_operational,
    validate_v4_3_closeout_readiness,
    validate_v4_3_final_counters,
    validate_v4_3_operational_boundaries,
    validate_v4_3_phase_evidence_coverage,
    validate_v4_3_state_visibility,
)
from orchestration_governance.v4_3_closeout_readiness_models import (  # noqa: E402
    V4_3_CLOSEOUT_CLASSIFICATION_BLOCKED,
    V4_3_CLOSEOUT_CLASSIFICATION_COMPLETE,
    V4_3_CLOSEOUT_READINESS_SCHEMA_VERSION,
    V4_3_CLOSEOUT_READINESS_STATUS_STABLE,
    V4_3_EXPECTED_PHASE_IDS,
    V4_3_FINAL_COUNTER_NAMES,
    V4_4_READINESS_CLASSIFICATION_READY,
    V43CloseoutReadinessCertification,
)


def test_v4_3_closeout_models_are_immutable_and_non_operational():
    closeout = build_v4_3_closeout_readiness()

    with pytest.raises(FrozenInstanceError):
        closeout.orchestration_execution_enabled = True

    assert closeout.identity.schema_version == V4_3_CLOSEOUT_READINESS_SCHEMA_VERSION
    assert closeout.non_executable is True
    assert closeout.non_authorizing is True
    assert closeout.non_approving is True
    assert closeout.non_decisioning is True
    assert closeout.descriptive_only is True
    assert enabled_v4_3_closeout_capability_flags(closeout) == {}
    assert closeout.closeout_classification.final_closeout_classification == (
        V4_3_CLOSEOUT_CLASSIFICATION_COMPLETE
    )
    assert closeout.v4_4_readiness_classification.v4_4_readiness_classification == (
        V4_4_READINESS_CLASSIFICATION_READY
    )


def test_v4_3_closeout_phase_1_through_9_coverage_is_complete():
    closeout = build_v4_3_closeout_readiness()
    coverage = validate_v4_3_phase_evidence_coverage(closeout)

    assert coverage["valid"] is True
    assert tuple(coverage["phase_order"]) == V4_3_EXPECTED_PHASE_IDS
    assert coverage["missing_phase_ids"] == []
    assert coverage["missing_or_invalid_evidence_phase_ids"] == []
    assert len(closeout.phase_evidence) == 9
    assert all(reference.report_present for reference in closeout.phase_evidence)
    assert all(reference.report_json_valid for reference in closeout.phase_evidence)
    assert all(reference.migration_doc_present for reference in closeout.phase_evidence)
    assert all(reference.focused_test_present for reference in closeout.phase_evidence)
    assert all(reference.internal_report_hash for reference in closeout.phase_evidence)


def test_v4_3_closeout_serialization_hashing_and_equality_are_stable():
    first = build_v4_3_closeout_readiness()
    second = build_v4_3_closeout_readiness()

    assert first == second
    assert v4_3_closeout_readiness_equal(first, second)
    assert serialize_v4_3_closeout_readiness(first) == serialize_v4_3_closeout_readiness(second)
    assert hash_v4_3_closeout_readiness(first) == hash_v4_3_closeout_readiness(second)


def test_v4_3_closeout_ordering_survives_reordered_collections():
    closeout = build_v4_3_closeout_readiness()
    reordered = V43CloseoutReadinessCertification(
        identity=closeout.identity,
        phase_evidence=tuple(reversed(closeout.phase_evidence)),
        report_inventory=closeout.report_inventory,
        migration_doc_inventory=closeout.migration_doc_inventory,
        focused_test_inventory=closeout.focused_test_inventory,
        state_visibility_summaries=tuple(reversed(closeout.state_visibility_summaries)),
        final_counter_guarantees=tuple(reversed(closeout.final_counter_guarantees)),
        operational_boundary_guarantees=tuple(reversed(closeout.operational_boundary_guarantees)),
        closeout_classification=closeout.closeout_classification,
        v4_4_readiness_classification=closeout.v4_4_readiness_classification,
        deterministic_guarantees=tuple(reversed(closeout.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(closeout.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(closeout.explicit_prohibitions)),
    )

    assert serialize_v4_3_closeout_readiness(closeout) == serialize_v4_3_closeout_readiness(reordered)
    assert hash_v4_3_closeout_readiness(closeout) == hash_v4_3_closeout_readiness(reordered)


def test_v4_3_closeout_state_visibility_is_preserved():
    closeout = build_v4_3_closeout_readiness()
    state_visibility = validate_v4_3_state_visibility(closeout)

    assert state_visibility["valid"] is True
    assert state_visibility["prohibited_state_count"] == 31
    assert state_visibility["unsupported_state_count"] == 6
    assert state_visibility["blocked_state_count"] == 6
    assert state_visibility["stale_state_count"] == 6
    assert state_visibility["conflicting_state_count"] == 6
    assert state_visibility["fail_visible"] is True
    assert state_visibility["descriptive_only"] is True


def test_v4_3_closeout_final_counters_remain_zero():
    closeout = build_v4_3_closeout_readiness()
    counters = validate_v4_3_final_counters(closeout)

    assert counters["valid"] is True
    assert tuple(sorted(counters["counters"])) == tuple(sorted(V4_3_FINAL_COUNTER_NAMES))
    assert all(value == 0 for value in counters["counters"].values())


def test_v4_3_closeout_operational_boundaries_remain_absent():
    closeout = build_v4_3_closeout_readiness()
    boundaries = validate_v4_3_operational_boundaries(closeout)

    assert boundaries["valid"] is True
    assert boundaries["no_orchestration_runtime_exists"] is True
    assert boundaries["no_orchestration_execution_exists"] is True
    assert boundaries["no_orchestration_activation_exists"] is True
    assert boundaries["no_orchestration_authorization_exists"] is True
    assert boundaries["no_orchestration_approval_exists"] is True
    assert boundaries["no_orchestration_dispatch_exists"] is True
    assert boundaries["no_planner_integration_exists"] is True
    assert boundaries["no_production_consumption_exists"] is True
    assert boundaries["no_runtime_mutation_exists"] is True
    assert boundaries["no_operational_mutation_exists"] is True
    assert boundaries["no_hidden_orchestration_pathways_exist"] is True


def test_v4_3_closeout_non_operational_validation_detects_contamination():
    closeout = build_v4_3_closeout_readiness()
    contaminated_boundary = replace(closeout.operational_boundary_guarantees[0], exists=True)
    contaminated = replace(
        closeout,
        operational_boundary_guarantees=(
            contaminated_boundary,
        )
        + closeout.operational_boundary_guarantees[1:],
        orchestration_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        orchestration_decision_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
    )
    validation = validate_v4_3_closeout_non_operational(contaminated)
    boundaries = validate_v4_3_operational_boundaries(contaminated)

    assert validate_v4_3_closeout_non_operational(closeout)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] > 0
    assert validation["orchestration_execution_disabled"] is False
    assert validation["orchestration_authorization_disabled"] is False
    assert validation["orchestration_approval_disabled"] is False
    assert validation["orchestration_decision_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert boundaries["valid"] is False
    assert "orchestration_runtime" in boundaries["enabled_boundary_names"]


def test_v4_3_closeout_missing_phase_evidence_blocks_closeout_visibility():
    missing_report_name = "v4_3_orchestration_manifest_foundations_report.json"
    closeout = build_v4_3_closeout_readiness(
        report_presence_overrides={missing_report_name: False},
    )
    validation = validate_v4_3_closeout_readiness(closeout)

    assert validation["valid"] is False
    assert validation["final_closeout_classification"] == V4_3_CLOSEOUT_CLASSIFICATION_BLOCKED
    assert missing_report_name in validation["diagnostics"]["report_inventory"]["missing_report_names"]
    assert validation["diagnostics"]["missing_evidence_visible"] is True


def test_v4_3_closeout_report_generation_and_hash_are_stable():
    first = build_v4_3_closeout_and_v4_4_readiness_report()
    second = build_v4_3_closeout_and_v4_4_readiness_report()

    assert first == second
    assert first["foundation_status"] == V4_3_CLOSEOUT_READINESS_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["non_execution_guarantees_validated"] is True
    assert first["summary"]["non_authorization_guarantees_validated"] is True
    assert first["summary"]["non_approval_guarantees_validated"] is True
    assert first["summary"]["non_decision_guarantees_validated"] is True
    assert first["summary"]["enabled_coordination_execution_count"] == 0
    assert first["summary"]["enabled_transition_execution_count"] == 0
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["enabled_orchestration_decision_count"] == 0
    assert first["summary"]["enabled_orchestration_recommendation_count"] == 0
    assert first["summary"]["enabled_orchestration_authorization_count"] == 0
    assert first["summary"]["enabled_orchestration_approval_count"] == 0
    assert first["summary"]["final_closeout_classification"] == V4_3_CLOSEOUT_CLASSIFICATION_COMPLETE
    assert first["summary"]["v4_4_readiness_classification"] == V4_4_READINESS_CLASSIFICATION_READY


def test_v4_3_closeout_report_json_matches_phase_9_readiness_evidence():
    report = build_v4_3_closeout_and_v4_4_readiness_report()
    phase_9_report_path = (
        BACKEND_ROOT.parent
        / "docs"
        / "generated"
        / "v4_3_orchestration_readiness_certification_report.json"
    )
    phase_9_report = json.loads(phase_9_report_path.read_text(encoding="utf-8"))

    for counter_name in V4_3_FINAL_COUNTER_NAMES:
        assert report["summary"][counter_name] == phase_9_report["summary"][counter_name] == 0
    assert report["readiness_findings"]["readiness_validation"]["valid"] is True
    assert phase_9_report["summary"]["readiness_certification_verified"] is True
    assert phase_9_report["summary"]["planner_integration_disabled"] is True
    assert phase_9_report["summary"]["production_consumption_disabled"] is True
