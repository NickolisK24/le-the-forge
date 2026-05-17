from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.bundle_governance_serialization import (  # noqa: E402
    serialize_trusted_bundle_governance_report,
)
from operational_lifecycle.lifecycle_drift_serialization import serialize_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_serialization import serialize_patch_lifecycle_foundation  # noqa: E402
from operational_lifecycle.production_consumption_governance import (  # noqa: E402
    evaluate_blocked_state_gate,
    evaluate_bundle_governance_gate,
    evaluate_controlled_production_consumption_governance,
    evaluate_drift_evidence_gate,
    evaluate_integrity_warning_gate,
    evaluate_lifecycle_evidence_gate,
    evaluate_lineage_continuity_gate,
    evaluate_operational_validation_gate,
    evaluate_production_consumption_prohibition_gate,
    evaluate_production_consumption_readiness_gate,
    evaluate_prohibited_state_gate,
    evaluate_provenance_continuity_gate,
    evaluate_replay_continuity_gate,
    evaluate_rollback_continuity_gate,
    evaluate_unknown_state_gate,
    evaluate_unsupported_state_gate,
)
from operational_lifecycle.production_consumption_hashing import (  # noqa: E402
    hash_production_consumption_governance_report,
)
from operational_lifecycle.production_consumption_models import (  # noqa: E402
    PRODUCTION_CONSUMPTION_GATE_BLOCKED_STATE,
    PRODUCTION_CONSUMPTION_GATE_BUNDLE_GOVERNANCE,
    PRODUCTION_CONSUMPTION_GATE_DRIFT_EVIDENCE,
    PRODUCTION_CONSUMPTION_GATE_INTEGRITY_WARNING,
    PRODUCTION_CONSUMPTION_GATE_LIFECYCLE_EVIDENCE,
    PRODUCTION_CONSUMPTION_GATE_LINEAGE_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_OPERATIONAL_VALIDATION,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS,
    PRODUCTION_CONSUMPTION_GATE_PROHIBITED_STATE,
    PRODUCTION_CONSUMPTION_GATE_PROVENANCE_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_REPLAY_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_ROLLBACK_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
    PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED,
    PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED,
    PRODUCTION_CONSUMPTION_GATE_TYPES,
    PRODUCTION_CONSUMPTION_GATE_UNKNOWN_STATE,
    PRODUCTION_CONSUMPTION_GATE_UNSUPPORTED_STATE,
    PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING,
    PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL,
    PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED,
    PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN,
    PRODUCTION_CONSUMPTION_SEVERITY_WARNING,
    V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_STABLE,
)
from operational_lifecycle.production_consumption_serialization import (  # noqa: E402
    export_production_consumption_governance_report,
    serialize_production_consumption_governance_report,
)
from operational_lifecycle.production_consumption_visibility import (  # noqa: E402
    count_production_consumption_gate_states,
    count_production_consumption_gate_types,
    count_production_consumption_severities,
    validate_production_consumption_visibility,
)
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    serialize_operational_validation_report,
)
from scripts.report_v4_0_controlled_production_consumption_governance import (  # noqa: E402
    build_representative_controlled_production_consumption_inputs,
    build_v4_0_controlled_production_consumption_governance_report,
)


def _representative_report():
    lifecycle_foundation, drift_report, governance_report, validation_report = (
        build_representative_controlled_production_consumption_inputs()
    )
    return evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    )


def test_v4_0_production_consumption_gate_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [gate.deterministic_key for gate in first.gates]
    second_keys = [gate.deterministic_key for gate in second.gates]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.gate_count == 15
    assert first.gate_count == len(first.gates)


def test_v4_0_production_consumption_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_production_consumption_governance_report(first) == serialize_production_consumption_governance_report(second)
    assert hash_production_consumption_governance_report(first) == hash_production_consumption_governance_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_production_consumption_governance_report(first)
    exported = json.loads(serialize_production_consumption_governance_report(first))
    assert exported["gate_count"] == 15
    assert exported["production_consumption_authorized"] is False
    assert exported["production_consumption_enabled"] is False
    assert exported["planner_behavior_changed"] is False
    assert all(gate["lifecycle_reference"] for gate in exported["gates"])
    assert all(gate["drift_reference"] for gate in exported["gates"])
    assert all(gate["governance_reference"] for gate in exported["gates"])
    assert all(gate["validation_reference"] for gate in exported["gates"])
    assert all(gate["provenance_reference"] for gate in exported["gates"])
    assert all(gate["lineage_reference"] for gate in exported["gates"])


def test_v4_0_production_consumption_report_contains_all_required_gate_types():
    report = _representative_report()
    gate_type_counts = count_production_consumption_gate_types(report.gates)

    assert set(PRODUCTION_CONSUMPTION_GATE_TYPES) <= set(gate_type_counts)
    for gate_type in PRODUCTION_CONSUMPTION_GATE_TYPES:
        assert gate_type_counts[gate_type] == 1
    assert gate_type_counts["invalid"] == 0


def test_v4_0_production_consumption_gate_functions_are_descriptive_only():
    lifecycle_foundation, drift_report, governance_report, validation_report = (
        build_representative_controlled_production_consumption_inputs()
    )
    gates = (
        evaluate_lifecycle_evidence_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_drift_evidence_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_bundle_governance_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_operational_validation_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_provenance_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_lineage_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_replay_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_rollback_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_unsupported_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_prohibited_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_blocked_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_unknown_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_integrity_warning_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
        evaluate_production_consumption_prohibition_gate(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
        ),
        evaluate_production_consumption_readiness_gate(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
        ),
    )

    assert all(gate.descriptive_only for gate in gates)
    assert all(not gate.approval_enabled for gate in gates)
    assert all(not gate.authorization_enabled for gate in gates)
    assert all(not gate.production_consumption_authorized for gate in gates)
    assert all(not gate.production_consumption_enabled for gate in gates)
    assert all(not gate.production_bundle_consumption_enabled for gate in gates)
    assert all(not gate.planner_integration_enabled for gate in gates)
    assert all(not gate.planner_behavior_changed for gate in gates)
    assert all(not gate.remediation_enabled for gate in gates)
    assert all(not gate.execution_enabled for gate in gates)
    assert all(not gate.orchestration_execution_enabled for gate in gates)


def test_v4_0_production_consumption_exposes_evidence_and_continuity_gates():
    report = _representative_report()
    gates = {gate.gate_type: gate for gate in report.gates}

    assert gates[PRODUCTION_CONSUMPTION_GATE_LIFECYCLE_EVIDENCE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
    assert gates[PRODUCTION_CONSUMPTION_GATE_DRIFT_EVIDENCE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
    assert gates[PRODUCTION_CONSUMPTION_GATE_BUNDLE_GOVERNANCE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
    assert gates[PRODUCTION_CONSUMPTION_GATE_OPERATIONAL_VALIDATION].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED
    assert gates[PRODUCTION_CONSUMPTION_GATE_PROVENANCE_CONTINUITY].severity == PRODUCTION_CONSUMPTION_SEVERITY_WARNING
    assert gates[PRODUCTION_CONSUMPTION_GATE_LINEAGE_CONTINUITY].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED
    assert gates[PRODUCTION_CONSUMPTION_GATE_REPLAY_CONTINUITY].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
    assert gates[PRODUCTION_CONSUMPTION_GATE_ROLLBACK_CONTINUITY].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED


def test_v4_0_production_consumption_exposes_fail_visible_gate_states():
    report = _representative_report()
    visibility = validate_production_consumption_visibility(report)
    gate_state_counts = count_production_consumption_gate_states(report.gates)
    severity_counts = count_production_consumption_severities(report.gates)
    gates = {gate.gate_type: gate for gate in report.gates}

    assert visibility["valid"] is True
    assert report.satisfied_gate_count == 6
    assert report.blocked_gate_count == 4
    assert report.unsupported_gate_count == 1
    assert report.prohibited_gate_count == 2
    assert report.unknown_gate_count == 1
    assert report.warning_count == 7
    assert report.critical_count == 1
    assert gate_state_counts[PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED] == 1
    assert gate_state_counts[PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED] == 2
    assert gate_state_counts[PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED] == 4
    assert gate_state_counts[PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN] == 1
    assert severity_counts[PRODUCTION_CONSUMPTION_SEVERITY_WARNING] == 7
    assert severity_counts[PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING] == 4
    assert severity_counts[PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED] == 2
    assert severity_counts[PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN] == 1
    assert severity_counts[PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL] == 1
    assert gates[PRODUCTION_CONSUMPTION_GATE_UNSUPPORTED_STATE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED
    assert gates[PRODUCTION_CONSUMPTION_GATE_PROHIBITED_STATE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED
    assert gates[PRODUCTION_CONSUMPTION_GATE_BLOCKED_STATE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED
    assert gates[PRODUCTION_CONSUMPTION_GATE_UNKNOWN_STATE].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN
    assert visibility["capability_enabled_count"] == 0


def test_v4_0_production_consumption_prohibition_and_planner_flags_are_preserved():
    report = _representative_report()
    gates = [
        gate
        for gate in report.gates
        if gate.gate_type == PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION
    ]
    readiness = [
        gate
        for gate in report.gates
        if gate.gate_type == PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS
    ]

    assert report.production_consumption_authorized is False
    assert report.production_consumption_enabled is False
    assert report.production_bundle_consumption_enabled is False
    assert report.planner_integration_enabled is False
    assert report.planner_behavior_changed is False
    assert len(gates) == 1
    assert gates[0].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED
    assert gates[0].severity == PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED
    assert len(readiness) == 1
    assert readiness[0].gate_state == PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED
    assert "planner behavior is unchanged" in readiness[0].explanation


def test_v4_0_production_consumption_governance_does_not_mutate_inputs():
    lifecycle_foundation, drift_report, governance_report, validation_report = (
        build_representative_controlled_production_consumption_inputs()
    )
    lifecycle_before = serialize_patch_lifecycle_foundation(lifecycle_foundation)
    drift_before = serialize_lifecycle_drift_report(drift_report)
    governance_before = serialize_trusted_bundle_governance_report(governance_report)
    validation_before = serialize_operational_validation_report(validation_report)

    evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    )
    evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    )

    assert serialize_patch_lifecycle_foundation(lifecycle_foundation) == lifecycle_before
    assert serialize_lifecycle_drift_report(drift_report) == drift_before
    assert serialize_trusted_bundle_governance_report(governance_report) == governance_before
    assert serialize_operational_validation_report(validation_report) == validation_before


def test_v4_0_production_consumption_hash_changes_when_validation_hash_changes():
    lifecycle_foundation, drift_report, governance_report, validation_report = (
        build_representative_controlled_production_consumption_inputs()
    )
    baseline = evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    )
    changed_validation = replace(validation_report, deterministic_report_hash="changed_validation_hash")
    changed = evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        changed_validation,
    )

    assert baseline.deterministic_report_hash != changed.deterministic_report_hash
    assert baseline.validation_report_hash != changed.validation_report_hash


def test_v4_0_production_consumption_generated_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_controlled_production_consumption_governance_report()
    production_report = report["production_consumption_governance_report"]

    assert report["foundation_status"] == V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_STABLE
    assert report["governance_mode"] == "descriptive_only"
    assert report["gate_count"] == 15
    assert report["satisfied_gate_count"] == 6
    assert report["blocked_gate_count"] == 4
    assert report["unsupported_gate_count"] == 1
    assert report["prohibited_gate_count"] == 2
    assert report["unknown_gate_count"] == 1
    assert report["warning_count"] == 7
    assert report["critical_count"] == 1
    assert report["production_consumption_authorization_status"] is False
    assert report["production_consumption_enabled_status"] is False
    assert report["planner_behavior_changed"] is False
    assert report["deterministic_production_consumption_report_hash"] == production_report["deterministic_report_hash"]
    assert set(report["implemented_production_consumption_gate_types"]) == set(PRODUCTION_CONSUMPTION_GATE_TYPES)
    assert report["non_execution_guarantees"]["approval_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
    assert report["non_execution_guarantees"]["execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["planner_behavior_unchanged"] is True
    assert report["non_execution_guarantees"]["production_consumption_authorized"] is False
    assert report["non_execution_guarantees"]["production_consumption_enabled"] is False
    assert report["summary"]["capability_enabled_count"] == 0
    assert "v4.0 Phase 5 does not change planner behavior." in report["explicit_limitations"]


def test_v4_0_production_consumption_export_preserves_order_and_flags():
    report = _representative_report()
    exported = export_production_consumption_governance_report(report)

    assert exported["production_consumption_authorized"] is False
    assert exported["production_consumption_enabled"] is False
    assert exported["planner_integration_enabled"] is False
    assert exported["planner_behavior_changed"] is False
    assert [gate["deterministic_key"] for gate in exported["gates"]] == sorted(
        gate["deterministic_key"] for gate in exported["gates"]
    )
    assert any(
        gate["gate_type"] == PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION
        for gate in exported["gates"]
    )
