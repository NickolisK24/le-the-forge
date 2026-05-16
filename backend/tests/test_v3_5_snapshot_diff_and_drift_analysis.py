from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH,
    SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE,
    SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY,
    SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    SNAPSHOT_DIFF_PROHIBITED,
    SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED,
    SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_DIFF_STABLE,
    SNAPSHOT_DIFF_UNSUPPORTED,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_UNSUPPORTED,
    analyze_orchestration_snapshot_diff,
    default_orchestration_snapshot_diff_input,
    export_orchestration_snapshot_diff_result,
    hash_snapshot_diff_result,
    serialize_orchestration_snapshot_diff_result,
)
from scripts.report_v3_5_snapshot_diff_and_drift_analysis import (
    build_v3_5_snapshot_diff_and_drift_analysis_report,
)


def _base_input():
    return default_orchestration_snapshot_diff_input()


def _result(source=None):
    return analyze_orchestration_snapshot_diff(source or _base_input())


def _export(source=None):
    return export_orchestration_snapshot_diff_result(_result(source))


def _target_with(**changes):
    return replace(_base_input().target_snapshot, **changes)


def test_deterministic_diff_classification():
    first = _export()
    second = _export()

    assert first["diff_status"] == SNAPSHOT_DIFF_STABLE
    assert first["deterministic_diff_hash"] == second["deterministic_diff_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    assert serialize_orchestration_snapshot_diff_result(_result()) == serialize_orchestration_snapshot_diff_result(_result())


def test_stable_deterministic_diff_hash_output():
    assert hash_snapshot_diff_result(_result()) == hash_snapshot_diff_result(_result())


def test_priority_order_status_selection():
    target = _target_with(
        snapshot_status=SNAPSHOT_PROHIBITED,
        prohibited_state_summary=("runtime_execution",),
        unsupported_state_summary=("unsupported_diff_state",),
        replay_lineage_references=("changed-replay-lineage",),
        deterministic_snapshot_hash="priority-target-hash",
    )
    result = _export(
        replace(
            _base_input(),
            target_snapshot=target,
            expected_target_snapshot_hash="unexpected-target-hash",
            replay_stability_verified=False,
            deterministic_serialization_verified=False,
            manual_review_reasons=("manual_priority_check",),
        )
    )

    assert result["diff_status"] == SNAPSHOT_DIFF_PROHIBITED
    assert result["replay_safety_diffs"]
    assert result["lineage_diffs"]
    assert result["manual_review_diffs"] == ["manual_priority_check"]


def test_changed_without_drift():
    target = _target_with(deterministic_snapshot_hash="changed-without-drift-hash")
    result = _export(
        replace(
            _base_input(),
            target_snapshot=target,
            expected_target_snapshot_hash=target.deterministic_snapshot_hash,
        )
    )

    assert result["diff_status"] == SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT
    assert result["drift_classifications"] == []
    assert result["replay_safety_diffs"] == ["snapshot_hash_changed"]


def test_lineage_diff_preservation():
    target = _target_with(replay_lineage_references=("changed-replay-lineage",))
    result = _export(replace(_base_input(), target_snapshot=target, expected_target_snapshot_hash=target.deterministic_snapshot_hash))

    assert result["diff_status"] == SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE
    assert result["lineage_diffs"][0]["diff_type"] == "replay_lineage"
    assert "lineage_drift" in result["drift_classifications"]


def test_replay_instability_preservation():
    result = _export(replace(_base_input(), replay_stability_verified=False))

    assert result["diff_status"] == SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY
    assert result["replay_safety_diffs"] == ["replay_stability_not_verified"]
    assert "replay_drift" in result["drift_classifications"]


def test_hash_mismatch_preservation():
    result = _export(replace(_base_input(), expected_target_snapshot_hash="unexpected-target-snapshot-hash"))

    assert result["diff_status"] == SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH
    assert result["replay_safety_diffs"] == ["target_snapshot_hash_mismatch"]
    assert "hash_drift" in result["drift_classifications"]


def test_unsupported_and_prohibited_diff_preservation():
    prohibited = _export(
        replace(
            _base_input(),
            target_snapshot=_target_with(snapshot_status=SNAPSHOT_PROHIBITED, prohibited_state_summary=("runtime_execution",)),
        )
    )
    unsupported = _export(
        replace(
            _base_input(),
            target_snapshot=_target_with(snapshot_status=SNAPSHOT_UNSUPPORTED, unsupported_state_summary=("unsupported_diff_state",)),
        )
    )

    assert prohibited["diff_status"] == SNAPSHOT_DIFF_PROHIBITED
    assert prohibited["unsupported_prohibited_diffs"][0]["diff_type"] == "prohibited_states"
    assert unsupported["diff_status"] == SNAPSHOT_DIFF_UNSUPPORTED
    assert unsupported["unsupported_prohibited_diffs"][0]["diff_type"] == "unsupported_states"


def test_readiness_dependency_coordination_visibility_diff_preservation():
    base = _base_input()
    target = replace(
        base.target_snapshot,
        readiness_state_reference=replace(base.target_snapshot.readiness_state_reference, reference_status="blocked_by_governance_dependency"),
        dependency_state_reference=replace(base.target_snapshot.dependency_state_reference, reference_status="dependency_blocked"),
        coordination_state_reference=replace(base.target_snapshot.coordination_state_reference, reference_status="coordination_blocked_by_dependency"),
        visibility_aggregation_reference=replace(base.target_snapshot.visibility_aggregation_reference, reference_status="visibility_blocked_by_readiness"),
    )
    result = _export(replace(base, target_snapshot=target, expected_target_snapshot_hash=target.deterministic_snapshot_hash))

    assert result["diff_status"] == SNAPSHOT_DIFF_DRIFT_DETECTED
    assert result["readiness_diffs"]
    assert result["dependency_diffs"]
    assert result["coordination_diffs"]
    assert result["visibility_diffs"]
    assert "governance_drift" in result["drift_classifications"]


def test_blocker_diff_preservation():
    target = _target_with(blocker_summary=("new_blocker",))
    result = _export(replace(_base_input(), target_snapshot=target, expected_target_snapshot_hash=target.deterministic_snapshot_hash))

    assert result["diff_status"] == SNAPSHOT_DIFF_DRIFT_DETECTED
    assert result["blocker_diffs"][0]["added_values"] == ["new_blocker"]
    assert "blocker_drift" in result["drift_classifications"]


def test_replay_safety_compromise_visibility():
    result = _export(replace(_base_input(), deterministic_serialization_verified=False))

    assert result["diff_status"] == SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED
    assert result["replay_safety_diffs"] == ["deterministic_serialization_not_verified"]
    assert "replay_drift" in result["drift_classifications"]


def test_compatibility_environment_and_limitation_diff_preservation():
    target = _target_with(
        compatibility_references=("changed-compatibility-reference",),
        environment_references=("changed-environment-reference",),
        limitation_summary=("changed limitation",),
    )
    result = _export(replace(_base_input(), target_snapshot=target, expected_target_snapshot_hash=target.deterministic_snapshot_hash))

    assert result["diff_status"] == SNAPSHOT_DIFF_DRIFT_DETECTED
    assert result["compatibility_diffs"]
    assert result["environment_diffs"]
    assert result["limitation_diffs"]
    assert "compatibility_drift" in result["drift_classifications"]
    assert "environment_drift" in result["drift_classifications"]
    assert "limitation_drift" in result["drift_classifications"]


def test_manual_review_preservation():
    result = _export(replace(_base_input(), manual_review_reasons=("manual_drift_review",)))

    assert result["diff_status"] == SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_diffs"] == ["manual_drift_review"]


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


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_snapshot_diff_and_drift_analysis_report()
    second = build_v3_5_snapshot_diff_and_drift_analysis_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_diff_status"] == SNAPSHOT_DIFF_STABLE
    assert distribution[SNAPSHOT_DIFF_STABLE] == 1
    assert distribution[SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT] == 1
    assert distribution[SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE] == 1
    assert distribution[SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY] == 1
    assert distribution[SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH] == 1
    assert distribution[SNAPSHOT_DIFF_PROHIBITED] == 2
    assert distribution[SNAPSHOT_DIFF_UNSUPPORTED] == 1
    assert distribution[SNAPSHOT_DIFF_DRIFT_DETECTED] == 2
    assert distribution[SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_snapshot_diff_and_drift_analysis_report()["explicit_non_execution_guarantees"]

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
