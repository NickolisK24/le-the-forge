"""Non-executable replay evidence for v3.7 graph planning sessions."""

from __future__ import annotations

from typing import Any

from .v3_7_graph_planning_session_models import (
    V37GraphPlanningSession,
    V37GraphPlanningSessionReplayEvidence,
    export_v3_7_graph_planning_session_replay_evidence,
)
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


def build_v3_7_graph_planning_session_replay_evidence(
    session: V37GraphPlanningSession | None = None,
) -> tuple[V37GraphPlanningSessionReplayEvidence, ...]:
    planning_session = session or build_v3_7_graph_planning_session()
    return planning_session.replay_evidence


def validate_v3_7_graph_planning_session_replay_evidence(
    session: V37GraphPlanningSession | None = None,
) -> dict[str, Any]:
    planning_session = session or build_v3_7_graph_planning_session()
    replay = planning_session.replay_evidence
    rollback = planning_session.rollback_evidence
    return {
        "replay_evidence_count": len(replay),
        "rollback_evidence_count": len(rollback),
        "non_executable_replay_evidence": all(item.non_executable_replay_evidence for item in replay),
        "runtime_replay": any(item.runtime_replay for item in replay),
        "orchestration_runtime_packet": any(item.orchestration_runtime_packet for item in replay),
        "execution_authorization": any(item.execution_authorization for item in replay),
        "replay_continuity_preserved": all(item.replay_packet_references and item.continuity_hashes for item in replay),
        "rollback_continuity_preserved": all(item.rollback_reference_ids and item.continuity_hashes for item in rollback),
    }


def export_v3_7_graph_planning_session_replay_evidence_records(
    evidence: tuple[V37GraphPlanningSessionReplayEvidence, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_planning_session_replay_evidence(item)
        for item in sorted(evidence, key=lambda record: record.replay_evidence_id)
    ]
