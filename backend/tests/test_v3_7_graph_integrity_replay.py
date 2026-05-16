from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from app.runtime_orchestration.v3_7_graph_integrity_replay import (
    build_v3_7_graph_integrity_replay_evidence,
    export_v3_7_graph_integrity_replay_evidence_records,
    validate_v3_7_graph_integrity_replay_evidence,
)


def test_integrity_replay_evidence_is_non_executable_and_stable():
    enforcement = enforce_v3_7_graph_planning_integrity()
    replay = build_v3_7_graph_integrity_replay_evidence(enforcement)
    validation = validate_v3_7_graph_integrity_replay_evidence(enforcement)

    assert len(replay) == 1
    assert validation["replay_evidence_count"] == 1
    assert validation["non_executable_replay_evidence"] is True
    assert validation["runtime_replay"] is False
    assert validation["execution_authorization"] is False
    assert validation["replay_continuity_preserved"] is True
    assert validation["rollback_continuity_preserved"] is True


def test_integrity_replay_detects_runtime_replay_flag():
    enforcement = enforce_v3_7_graph_planning_integrity()
    broken_replay = replace(enforcement.replay_evidence[0], runtime_replay=True)
    validation = validate_v3_7_graph_integrity_replay_evidence(replace(enforcement, replay_evidence=(broken_replay,)))

    assert validation["runtime_replay"] is True
    assert validation["non_executable_replay_evidence"] is True


def test_integrity_replay_records_are_sorted():
    enforcement = enforce_v3_7_graph_planning_integrity()
    records = export_v3_7_graph_integrity_replay_evidence_records(enforcement.replay_evidence)

    assert [record["replay_evidence_id"] for record in records] == sorted(record["replay_evidence_id"] for record in records)
