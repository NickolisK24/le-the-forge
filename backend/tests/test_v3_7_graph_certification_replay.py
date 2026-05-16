from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_certification_evidence import (
    build_v3_7_graph_planning_continuity_certification,
)
from app.runtime_orchestration.v3_7_graph_certification_replay import (
    build_v3_7_graph_certification_replay_evidence,
    export_v3_7_graph_certification_replay_evidence_records,
    validate_v3_7_graph_certification_replay_evidence,
)


def test_certification_replay_evidence_is_non_executable_and_stable():
    certification = build_v3_7_graph_planning_continuity_certification()
    replay = build_v3_7_graph_certification_replay_evidence(certification)
    validation = validate_v3_7_graph_certification_replay_evidence(certification)

    assert len(replay) == 1
    assert validation["replay_evidence_count"] == 1
    assert validation["non_executable_replay_evidence"] is True
    assert validation["runtime_replay"] is False
    assert validation["execution_authorization"] is False
    assert validation["runtime_readiness_certification"] is False
    assert validation["replay_continuity_preserved"] is True
    assert validation["rollback_continuity_preserved"] is True


def test_certification_replay_detects_runtime_readiness_flag():
    certification = build_v3_7_graph_planning_continuity_certification()
    broken_replay = replace(certification.replay_evidence[0], runtime_readiness_certification=True)
    validation = validate_v3_7_graph_certification_replay_evidence(replace(certification, replay_evidence=(broken_replay,)))

    assert validation["runtime_readiness_certification"] is True
    assert validation["non_executable_replay_evidence"] is True


def test_certification_replay_records_are_sorted():
    certification = build_v3_7_graph_planning_continuity_certification()
    records = export_v3_7_graph_certification_replay_evidence_records(certification.replay_evidence)

    assert [record["replay_evidence_id"] for record in records] == sorted(record["replay_evidence_id"] for record in records)
