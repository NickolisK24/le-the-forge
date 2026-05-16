from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP,
    COORDINATION_BLOCKED_BY_DEPENDENCY,
    DEPENDENCY_MISSING,
    INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY,
    INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE,
    INTEGRITY_AUDIT_INTEGRITY_COMPROMISED,
    INTEGRITY_AUDIT_PROHIBITED,
    INTEGRITY_AUDIT_REQUIRES_MANUAL_REVIEW,
    INTEGRITY_AUDIT_STABLE,
    SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    VISIBILITY_BLOCKED_BY_READINESS,
    audit_orchestration_planning_integrity,
    default_orchestration_integrity_audit_input,
    export_orchestration_integrity_audit_result,
    hash_integrity_audit_result,
    serialize_orchestration_integrity_audit_result,
)
from scripts.report_v3_5_orchestration_integrity_audit import build_v3_5_orchestration_integrity_audit_report


def _base_input():
    return default_orchestration_integrity_audit_input()


def _result(source=None):
    return audit_orchestration_planning_integrity(source or _base_input())


def _export(source=None):
    return export_orchestration_integrity_audit_result(_result(source))


def test_deterministic_integrity_classification():
    first = _export()
    second = _export()

    assert first["integrity_audit_status"] == INTEGRITY_AUDIT_STABLE
    assert first["deterministic_integrity_hash"] == second["deterministic_integrity_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    assert serialize_orchestration_integrity_audit_result(_result()) == serialize_orchestration_integrity_audit_result(_result())


def test_stable_deterministic_integrity_hash_output():
    assert hash_integrity_audit_result(_result()) == hash_integrity_audit_result(_result())


def test_priority_order_status_selection():
    base = _base_input()
    result = _export(
        replace(
            base,
            governance_integrity_references=(),
            replay_integrity_references=(),
            expected_integrity_hash="mismatched-integrity-hash",
            prohibited_reasons=("runtime_execution",),
            deterministic_serialization_verified=False,
            manual_review_reasons=("manual_priority_check",),
        )
    )

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_PROHIBITED
    assert "runtime_execution" in result["unsupported_prohibited_summary"]


def test_governance_integrity_preservation():
    result = _export()

    assert result["governance_integrity"]["references"] == ["governance-consumption-v3-5-phase-1"]
    assert result["readiness_integrity"]["references"] == ["ready_for_future_orchestration_planning"]


def test_governance_failure_visibility():
    result = _export(replace(_base_input(), governance_integrity_references=()))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE
    assert result["governance_integrity"]["failures"] == ["governance_integrity_references"]


def test_dependency_integrity_preservation_and_failure_visibility():
    base = _base_input()
    dependency = base.dependency_result
    assert dependency is not None
    result = _export(replace(base, dependency_result=replace(dependency, dependency_status=DEPENDENCY_MISSING)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE
    assert result["dependency_integrity"]["failures"] == ["dependency_integrity_failure:dependency_missing"]


def test_coordination_integrity_preservation_and_failure_visibility():
    base = _base_input()
    coordination = base.coordination_result
    assert coordination is not None
    result = _export(replace(base, coordination_result=replace(coordination, coordination_status=COORDINATION_BLOCKED_BY_DEPENDENCY)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE
    assert result["coordination_integrity"]["failures"] == ["coordination_integrity_failure:coordination_blocked_by_dependency"]


def test_visibility_integrity_preservation_and_failure_visibility():
    base = _base_input()
    visibility = base.visibility_result
    assert visibility is not None
    result = _export(replace(base, visibility_result=replace(visibility, aggregate_visibility_status=VISIBILITY_BLOCKED_BY_READINESS)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE
    assert result["visibility_integrity"]["failures"] == ["visibility_integrity_failure:visibility_blocked_by_readiness"]


def test_snapshot_integrity_preservation_and_failure_visibility():
    base = _base_input()
    snapshot = base.snapshot_result
    assert snapshot is not None
    result = _export(replace(base, snapshot_result=replace(snapshot, snapshot_status=SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE
    assert result["snapshot_integrity"]["failures"] == ["snapshot_integrity_failure:snapshot_blocked_by_visibility_state"]


def test_diff_drift_integrity_preservation_and_failure_visibility():
    base = _base_input()
    diff = base.diff_result
    assert diff is not None
    result = _export(replace(base, diff_result=replace(diff, diff_status=SNAPSHOT_DIFF_DRIFT_DETECTED)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE
    assert result["diff_drift_integrity"]["failures"] == ["diff_drift_integrity_failure:snapshot_diff_drift_detected"]


def test_audit_chain_integrity_preservation_and_failure_visibility():
    base = _base_input()
    audit_chain = base.audit_chain_result
    assert audit_chain is not None
    result = _export(replace(base, audit_chain_result=replace(audit_chain, audit_chain_status=AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE
    assert result["audit_chain_integrity"]["failures"] == ["audit_chain_integrity_failure:audit_chain_blocked_by_lineage_gap"]


def test_replay_rollback_lineage_integrity_preservation():
    result = _export()

    assert result["replay_integrity"]["references"] == ["replay-integrity-v3-5-phase-9"]
    assert result["rollback_integrity"]["references"] == ["rollback-integrity-v3-5-phase-9"]
    assert result["lineage_integrity"]["references"] == ["lineage-integrity-v3-5-phase-9"]


def test_replay_continuity_failure_is_integrity_compromised():
    result = _export(replace(_base_input(), replay_integrity_references=()))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_INTEGRITY_COMPROMISED
    assert result["replay_integrity"]["failures"] == ["replay_integrity_references"]


def test_serialization_and_hash_stability_preservation():
    serialization = _export(replace(_base_input(), deterministic_serialization_verified=False))
    hash_mismatch = _export(replace(_base_input(), expected_integrity_hash="mismatched-integrity-hash"))

    assert serialization["integrity_audit_status"] == INTEGRITY_AUDIT_INTEGRITY_COMPROMISED
    assert serialization["deterministic_serialization_integrity"]["failures"] == ["deterministic_serialization_not_verified"]
    assert hash_mismatch["integrity_audit_status"] == INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY
    assert hash_mismatch["deterministic_hash_stability"]["failures"] == ["integrity_hash_mismatch"]


def test_manual_review_and_limitation_preservation():
    result = _export(replace(_base_input(), manual_review_reasons=("manual_integrity_review",)))

    assert result["integrity_audit_status"] == INTEGRITY_AUDIT_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_summary"] == ["manual_integrity_review"]
    assert "integrity auditing is declarative and planning-only" in result["limitation_summary"]
    assert "integrity auditing does not persist audit state" in result["limitation_summary"]


def test_failure_classification_visibility():
    result = _export(replace(_base_input(), governance_integrity_references=(), replay_integrity_references=()))

    assert "governance_integrity_references" in result["failure_classification_summary"]
    assert "replay_integrity_references" in result["failure_classification_summary"]
    assert result["blocker_summary"] == result["failure_classification_summary"]


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["audit_log_writing_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["graph_traversal_behavior_enabled"] is False
    assert result["scheduling_behavior_enabled"] is False
    assert result["orchestration_dispatch_enabled"] is False
    assert result["runtime_trace_capture_enabled"] is False
    assert result["production_state_reads_enabled"] is False
    assert result["live_replay_enabled"] is False
    assert result["persistent_audit_storage_enabled"] is False


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_orchestration_integrity_audit_report()
    second = build_v3_5_orchestration_integrity_audit_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_integrity_audit_status"] == INTEGRITY_AUDIT_STABLE
    assert distribution[INTEGRITY_AUDIT_STABLE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE] == 1
    assert distribution[INTEGRITY_AUDIT_INTEGRITY_COMPROMISED] == 1
    assert distribution[INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY] == 1
    assert distribution[INTEGRITY_AUDIT_PROHIBITED] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_orchestration_integrity_audit_report()["explicit_non_execution_guarantees"]

    assert guarantees["runtime_execution_enabled"] is False
    assert guarantees["orchestration_execution_enabled"] is False
    assert guarantees["routing_behavior_enabled"] is False
    assert guarantees["mutation_behavior_enabled"] is False
    assert guarantees["audit_log_writing_enabled"] is False
    assert guarantees["production_consumption_enabled"] is False
    assert guarantees["graph_execution_enabled"] is False
    assert guarantees["graph_traversal_behavior_enabled"] is False
    assert guarantees["scheduling_behavior_enabled"] is False
    assert guarantees["orchestration_dispatch_enabled"] is False
    assert guarantees["runtime_trace_capture_enabled"] is False
    assert guarantees["production_state_reads_enabled"] is False
    assert guarantees["live_replay_enabled"] is False
    assert guarantees["persistent_audit_storage_enabled"] is False
