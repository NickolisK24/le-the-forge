from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT,
    AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP,
    AUDIT_CHAIN_INTEGRITY_COMPROMISED,
    AUDIT_CHAIN_PROHIBITED,
    AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW,
    AUDIT_CHAIN_STABLE,
    AUDIT_CHAIN_UNSUPPORTED,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_UNSUPPORTED,
    build_orchestration_audit_chain,
    default_orchestration_audit_chain_input,
    export_orchestration_audit_chain_result,
    hash_audit_chain_result,
    serialize_orchestration_audit_chain_result,
)
from scripts.report_v3_5_orchestration_audit_chain import build_v3_5_orchestration_audit_chain_report


def _base_input():
    return default_orchestration_audit_chain_input()


def _result(source=None):
    return build_orchestration_audit_chain(source or _base_input())


def _export(source=None):
    return export_orchestration_audit_chain_result(_result(source))


def test_deterministic_audit_classification():
    first = _export()
    second = _export()

    assert first["audit_chain_status"] == AUDIT_CHAIN_STABLE
    assert first["deterministic_audit_chain_hash"] == second["deterministic_audit_chain_hash"]
    assert first["planning_only"] is True


def test_stable_serialization():
    assert serialize_orchestration_audit_chain_result(_result()) == serialize_orchestration_audit_chain_result(_result())


def test_stable_deterministic_audit_chain_hash_output():
    assert hash_audit_chain_result(_result()) == hash_audit_chain_result(_result())


def test_priority_order_status_selection():
    base = _base_input()
    source, target = base.snapshot_sequence
    assert source is not None and target is not None
    prohibited_target = replace(target, snapshot_status=SNAPSHOT_PROHIBITED)
    result = _export(
        replace(
            base,
            snapshot_sequence=(source, prohibited_target),
            diff_analysis_sequence=(),
            chain_lineage_references=(),
            replay_continuity_references=(),
            prohibited_reasons=("runtime_execution",),
            deterministic_serialization_verified=False,
            manual_review_reasons=("manual_priority_check",),
        )
    )

    assert result["audit_chain_status"] == AUDIT_CHAIN_PROHIBITED
    assert "runtime_execution" in result["integrity_summary"] or result["lineage_gap_summary"]


def test_snapshot_continuity_preservation():
    result = _export()

    assert result["chain_snapshot_sequence"] == ["snapshot-v3-5-phase-6", "snapshot-v3-5-phase-6"]
    assert result["snapshot_gap_summary"] == []


def test_diff_analysis_continuity_preservation():
    result = _export()

    assert result["chain_diff_analysis_sequence"] == ["snapshot-diff-v3-5-phase-7"]
    assert result["diff_analysis_gap_summary"] == []


def test_lineage_continuity_preservation_and_gap_visibility():
    result = _export(replace(_base_input(), chain_lineage_references=()))

    assert result["audit_chain_status"] == AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP
    assert result["lineage_continuity"]["gaps"] == ["lineage_continuity_references"]
    assert result["lineage_gap_summary"] == ["lineage_continuity_references"]


def test_replay_continuity_preservation_and_gap_visibility():
    result = _export(replace(_base_input(), replay_continuity_references=()))

    assert result["audit_chain_status"] == AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP
    assert result["replay_continuity"]["gaps"] == ["replay_continuity_references"]
    assert result["replay_gap_summary"] == ["replay_continuity_references"]


def test_missing_snapshot_detection():
    base = _base_input()
    source = base.snapshot_sequence[0]
    result = _export(replace(base, snapshot_sequence=(source, None)))

    assert result["audit_chain_status"] == AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT
    assert result["snapshot_gap_summary"] == ["snapshot_sequence[1]"]


def test_missing_diff_analysis_detection():
    result = _export(replace(_base_input(), diff_analysis_sequence=()))

    assert result["audit_chain_status"] == AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS
    assert result["diff_analysis_gap_summary"] == ["diff_analysis_sequence"]


def test_integrity_validation_visibility():
    base = _base_input()
    diff = base.diff_analysis_sequence[0]
    assert diff is not None
    result = _export(replace(base, diff_analysis_sequence=(replace(diff, source_snapshot_hash="mismatched-source-snapshot-hash"),)))

    assert result["audit_chain_status"] == AUDIT_CHAIN_INTEGRITY_COMPROMISED
    assert "diff_source_snapshot_hash_mismatch" in result["integrity_summary"]


def test_unsupported_and_prohibited_visibility():
    base = _base_input()
    source, target = base.snapshot_sequence
    assert source is not None and target is not None
    prohibited = _export(replace(base, snapshot_sequence=(source, replace(target, snapshot_status=SNAPSHOT_PROHIBITED))))
    unsupported = _export(replace(base, snapshot_sequence=(source, replace(target, snapshot_status=SNAPSHOT_UNSUPPORTED))))

    assert prohibited["audit_chain_status"] == AUDIT_CHAIN_PROHIBITED
    assert unsupported["audit_chain_status"] == AUDIT_CHAIN_UNSUPPORTED


def test_blocker_compatibility_environment_continuity_preservation():
    result = _export()

    assert result["blocker_continuity"]["references"] == ["blocker-continuity-v3-5-phase-8"]
    assert result["compatibility_continuity"]["references"] == ["compatibility-continuity-v3-5-phase-8"]
    assert result["environment_continuity"]["references"] == ["environment-continuity-v3-5-phase-8"]


def test_manual_review_preservation():
    result = _export(replace(_base_input(), manual_review_reasons=("manual_audit_chain_review",)))

    assert result["audit_chain_status"] == AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_summary"] == ["manual_audit_chain_review"]


def test_limitation_preservation():
    result = _export()

    assert "audit-chain construction is declarative and planning-only" in result["limitation_summary"]
    assert "audit-chain construction does not persist audit state" in result["limitation_summary"]
    assert "audit-chain construction does not capture runtime lineage or traces" in result["limitation_summary"]


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
    first = build_v3_5_orchestration_audit_chain_report()
    second = build_v3_5_orchestration_audit_chain_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_audit_chain_status"] == AUDIT_CHAIN_STABLE
    assert distribution[AUDIT_CHAIN_STABLE] == 1
    assert distribution[AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP] == 2
    assert distribution[AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP] == 1
    assert distribution[AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT] == 1
    assert distribution[AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS] == 1
    assert distribution[AUDIT_CHAIN_INTEGRITY_COMPROMISED] == 2
    assert distribution[AUDIT_CHAIN_PROHIBITED] == 2
    assert distribution[AUDIT_CHAIN_UNSUPPORTED] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_orchestration_audit_chain_report()["explicit_non_execution_guarantees"]

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
