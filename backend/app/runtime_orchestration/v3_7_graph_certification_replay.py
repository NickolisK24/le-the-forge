"""Non-executable replay evidence for v3.7 continuity certification."""

from __future__ import annotations

from typing import Any

from .v3_7_graph_certification_evidence import build_v3_7_graph_planning_continuity_certification
from .v3_7_graph_certification_models import (
    V37GraphCertificationReplayEvidence,
    V37GraphPlanningContinuityCertification,
    export_v3_7_graph_certification_replay_evidence,
)


def build_v3_7_graph_certification_replay_evidence(
    certification: V37GraphPlanningContinuityCertification | None = None,
) -> tuple[V37GraphCertificationReplayEvidence, ...]:
    result = certification or build_v3_7_graph_planning_continuity_certification()
    return result.replay_evidence


def validate_v3_7_graph_certification_replay_evidence(
    certification: V37GraphPlanningContinuityCertification | None = None,
) -> dict[str, Any]:
    result = certification or build_v3_7_graph_planning_continuity_certification()
    replay = result.replay_evidence
    return {
        "replay_evidence_count": len(replay),
        "rollback_reference_count": len(result.rollback_continuity_references),
        "non_executable_replay_evidence": all(item.non_executable_replay_evidence for item in replay),
        "runtime_replay": any(item.runtime_replay for item in replay),
        "execution_authorization": any(item.execution_authorization for item in replay),
        "runtime_readiness_certification": any(item.runtime_readiness_certification for item in replay),
        "replay_continuity_preserved": all(
            item.certification_outcome
            and item.finding_references
            and item.evidence_source_references
            and item.provenance_references
            and item.explainability_references
            and item.continuity_hashes
            for item in replay
        ),
        "rollback_continuity_preserved": bool(result.rollback_continuity_references)
        and all(item.continuity_hashes for item in replay),
    }


def export_v3_7_graph_certification_replay_evidence_records(
    evidence: tuple[V37GraphCertificationReplayEvidence, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_certification_replay_evidence(item)
        for item in sorted(evidence, key=lambda record: record.replay_evidence_id)
    ]
