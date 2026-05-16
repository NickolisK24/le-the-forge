"""Non-executable replay evidence for v3.7 planning intelligence aggregation."""

from __future__ import annotations

from typing import Any

from .v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from .v3_7_graph_intelligence_models import (
    V37GraphIntelligenceReplayEvidence,
    V37GraphPlanningIntelligenceAggregation,
    export_v3_7_graph_intelligence_replay_evidence,
)


def build_v3_7_graph_intelligence_replay_evidence(
    aggregation: V37GraphPlanningIntelligenceAggregation | None = None,
) -> tuple[V37GraphIntelligenceReplayEvidence, ...]:
    planning_intelligence = aggregation or build_v3_7_graph_planning_intelligence_aggregation()
    return planning_intelligence.replay_evidence


def validate_v3_7_graph_intelligence_replay_evidence(
    aggregation: V37GraphPlanningIntelligenceAggregation | None = None,
) -> dict[str, Any]:
    planning_intelligence = aggregation or build_v3_7_graph_planning_intelligence_aggregation()
    replay = planning_intelligence.replay_evidence
    return {
        "replay_evidence_count": len(replay),
        "rollback_reference_count": len(planning_intelligence.rollback_continuity_references),
        "non_executable_replay_evidence": all(item.non_executable_replay_evidence for item in replay),
        "runtime_replay": any(item.runtime_replay for item in replay),
        "execution_authorization": any(item.execution_authorization for item in replay),
        "replay_continuity_preserved": all(
            item.evidence_source_references
            and item.graph_evidence_references
            and item.governance_evidence_references
            and item.compatibility_evidence_references
            and item.evaluation_evidence_references
            and item.session_evidence_references
            and item.scenario_evidence_references
            and item.provenance_references
            and item.explainability_references
            and item.continuity_hashes
            for item in replay
        ),
        "rollback_continuity_preserved": bool(planning_intelligence.rollback_continuity_references)
        and all(item.continuity_hashes for item in replay),
    }


def export_v3_7_graph_intelligence_replay_evidence_records(
    evidence: tuple[V37GraphIntelligenceReplayEvidence, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_intelligence_replay_evidence(item)
        for item in sorted(evidence, key=lambda record: record.replay_evidence_id)
    ]
