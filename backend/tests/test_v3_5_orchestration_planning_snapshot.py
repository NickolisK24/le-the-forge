from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY,
    SNAPSHOT_BLOCKED_BY_LINEAGE_GAP,
    SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE,
    SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_READY_FOR_REPLAY_PLANNING,
    SNAPSHOT_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_UNSUPPORTED,
    VISIBILITY_PROHIBITED,
    VISIBILITY_UNSUPPORTED,
    default_orchestration_planning_snapshot_input,
    export_orchestration_planning_snapshot_result,
    generate_orchestration_planning_snapshot,
    hash_snapshot_result,
    serialize_orchestration_planning_snapshot_result,
)
from scripts.report_v3_5_orchestration_planning_snapshot import (
    build_v3_5_orchestration_planning_snapshot_report,
)


def _base_input():
    return default_orchestration_planning_snapshot_input()


def _result(source=None):
    return generate_orchestration_planning_snapshot(source or _base_input())


def _export(source=None):
    return export_orchestration_planning_snapshot_result(_result(source))


def _visibility_with(**changes):
    visibility = _base_input().visibility_result
    assert visibility is not None
    return replace(visibility, **changes)


def test_deterministic_snapshot_classification():
    first = _export()
    second = _export()

    assert first["snapshot_status"] == SNAPSHOT_READY_FOR_REPLAY_PLANNING
    assert first["deterministic_snapshot_hash"] == second["deterministic_snapshot_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    assert serialize_orchestration_planning_snapshot_result(_result()) == serialize_orchestration_planning_snapshot_result(_result())


def test_stable_deterministic_snapshot_hash_output():
    assert hash_snapshot_result(_result()) == hash_snapshot_result(_result())
    assert _export()["deterministic_snapshot_hash"] == _export()["deterministic_snapshot_hash"]


def test_priority_order_status_selection():
    source = replace(
        _base_input(),
        visibility_result=_visibility_with(
            aggregate_visibility_status=VISIBILITY_PROHIBITED,
            prohibited_state_summary=("runtime_execution",),
            unsupported_state_summary=("unsupported_snapshot_state",),
        ),
        readiness_result=None,
        replay_lineage_references=(),
        hash_stability_verified=False,
        manual_review_reasons=("manual_priority_check",),
    )
    result = _export(source)

    assert result["snapshot_status"] == SNAPSHOT_PROHIBITED
    assert result["prohibited_state_summary"] == ["runtime_execution"]
    assert result["unsupported_state_summary"] == ["unsupported_snapshot_state"]
    assert "replay_lineage_references" in result["lineage_summary"]


def test_readiness_state_preservation():
    result = _export()

    assert result["readiness_state_reference"]["reference_type"] == "readiness"
    assert result["readiness_state_reference"]["reference_status"] == "ready_for_future_orchestration_planning"
    assert result["readiness_state_reference"]["deterministic_hash"]


def test_dependency_state_preservation():
    result = _export()

    assert result["dependency_state_reference"]["reference_type"] == "dependency"
    assert result["dependency_state_reference"]["reference_status"] == "dependency_satisfied"
    assert result["dependency_state_reference"]["deterministic_hash"]


def test_coordination_state_preservation():
    result = _export()

    assert result["coordination_state_reference"]["reference_type"] == "coordination"
    assert result["coordination_state_reference"]["reference_status"] == "coordination_ready_for_planning"
    assert result["coordination_state_reference"]["deterministic_hash"]


def test_visibility_state_preservation():
    result = _export()

    assert result["visibility_aggregation_reference"]["reference_type"] == "visibility"
    assert result["visibility_aggregation_reference"]["reference_status"] == "visibility_ready_for_planning"
    assert result["visibility_aggregation_reference"]["deterministic_hash"]


def test_missing_visibility_state_blocked():
    result = _export(replace(_base_input(), visibility_result=None))

    assert result["snapshot_status"] == SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE
    assert result["visibility_aggregation_reference"] is None


def test_missing_readiness_state_blocked():
    result = _export(replace(_base_input(), readiness_result=None))

    assert result["snapshot_status"] == SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE
    assert result["readiness_state_reference"] is None


def test_missing_dependency_state_blocked():
    result = _export(replace(_base_input(), dependency_result=None))

    assert result["snapshot_status"] == SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE
    assert result["dependency_state_reference"] is None


def test_missing_coordination_state_blocked():
    result = _export(replace(_base_input(), coordination_result=None))

    assert result["snapshot_status"] == SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE
    assert result["coordination_state_reference"] is None


def test_blocker_preservation():
    result = _export(replace(_base_input(), hash_stability_verified=False))

    assert result["snapshot_status"] == SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY
    assert result["blocker_summary"] == ["snapshot_hash_stability_not_verified"]


def test_unsupported_and_prohibited_preservation():
    prohibited = _export(
        replace(
            _base_input(),
            visibility_result=_visibility_with(
                aggregate_visibility_status=VISIBILITY_PROHIBITED,
                prohibited_state_summary=("runtime_execution",),
            ),
        )
    )
    unsupported = _export(
        replace(
            _base_input(),
            visibility_result=_visibility_with(
                aggregate_visibility_status=VISIBILITY_UNSUPPORTED,
                unsupported_state_summary=("unsupported_snapshot_state",),
            ),
        )
    )

    assert prohibited["snapshot_status"] == SNAPSHOT_PROHIBITED
    assert prohibited["prohibited_state_summary"] == ["runtime_execution"]
    assert unsupported["snapshot_status"] == SNAPSHOT_UNSUPPORTED
    assert unsupported["unsupported_state_summary"] == ["unsupported_snapshot_state"]


def test_lineage_preservation():
    result = _export(
        replace(
            _base_input(),
            replay_lineage_references=(),
            rollback_lineage_references=(),
            visibility_result=_visibility_with(lineage_gap_summary=("visibility_lineage_gap",)),
        )
    )

    assert result["snapshot_status"] == SNAPSHOT_BLOCKED_BY_LINEAGE_GAP
    assert result["lineage_summary"] == [
        "replay_lineage_references",
        "rollback_lineage_references",
        "visibility_lineage_gap",
    ]


def test_manual_review_preservation():
    result = _export(replace(_base_input(), manual_review_reasons=("snapshot_manual_review_required",)))

    assert result["snapshot_status"] == SNAPSHOT_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_summary"] == ["snapshot_manual_review_required"]


def test_limitation_preservation():
    result = _export()

    assert "snapshot generation is declarative and planning-only" in result["limitation_summary"]
    assert "visibility aggregation is declarative and planning-only" in result["limitation_summary"]
    assert "snapshot generation does not capture runtime traces" in result["limitation_summary"]
    assert "snapshot generation does not read production state" in result["limitation_summary"]


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
    assert result["auto_approval_behavior_enabled"] is False
    assert result["runtime_trace_capture_enabled"] is False
    assert result["production_state_reads_enabled"] is False


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_orchestration_planning_snapshot_report()
    second = build_v3_5_orchestration_planning_snapshot_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_snapshot_status"] == SNAPSHOT_READY_FOR_REPLAY_PLANNING
    assert distribution[SNAPSHOT_READY_FOR_REPLAY_PLANNING] == 1
    assert distribution[SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE] == 1
    assert distribution[SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE] == 1
    assert distribution[SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE] == 1
    assert distribution[SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE] == 1
    assert distribution[SNAPSHOT_BLOCKED_BY_LINEAGE_GAP] == 1
    assert distribution[SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY] == 1
    assert distribution[SNAPSHOT_REQUIRES_MANUAL_REVIEW] == 1
    assert distribution[SNAPSHOT_UNSUPPORTED] == 1
    assert distribution[SNAPSHOT_PROHIBITED] == 2


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_orchestration_planning_snapshot_report()["explicit_non_execution_guarantees"]

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
    assert guarantees["auto_approval_behavior_enabled"] is False
    assert guarantees["runtime_trace_capture_enabled"] is False
    assert guarantees["production_state_reads_enabled"] is False
