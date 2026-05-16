"""Non-executable replay evidence for v3.7 graph planning scenarios."""

from __future__ import annotations

from typing import Any

from .v3_7_graph_scenario_models import (
    V37GraphPlanningScenario,
    V37GraphScenarioReplayEvidence,
    export_v3_7_graph_scenario_replay_evidence,
)
from .v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


def build_v3_7_graph_scenario_replay_evidence(
    scenario: V37GraphPlanningScenario | None = None,
) -> tuple[V37GraphScenarioReplayEvidence, ...]:
    planning_scenario = scenario or build_v3_7_graph_planning_scenario()
    return planning_scenario.replay_evidence


def validate_v3_7_graph_scenario_replay_evidence(
    scenario: V37GraphPlanningScenario | None = None,
) -> dict[str, Any]:
    planning_scenario = scenario or build_v3_7_graph_planning_scenario()
    replay = planning_scenario.replay_evidence
    return {
        "replay_evidence_count": len(replay),
        "rollback_reference_count": sum(len(item.rollback_references) for item in replay),
        "non_executable_replay_evidence": all(item.non_executable_replay_evidence for item in replay),
        "runtime_replay_state": any(item.runtime_replay_state for item in replay),
        "execution_authorization": any(item.execution_authorization for item in replay),
        "replay_continuity_preserved": all(
            item.variation_references
            and item.graph_snapshot_references
            and item.evaluation_references
            and item.provenance_references
            and item.explainability_references
            and item.continuity_hashes
            for item in replay
        ),
        "rollback_continuity_preserved": all(item.rollback_references and item.continuity_hashes for item in replay),
    }


def export_v3_7_graph_scenario_replay_evidence_records(
    evidence: tuple[V37GraphScenarioReplayEvidence, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_scenario_replay_evidence(item)
        for item in sorted(evidence, key=lambda record: record.replay_evidence_id)
    ]
