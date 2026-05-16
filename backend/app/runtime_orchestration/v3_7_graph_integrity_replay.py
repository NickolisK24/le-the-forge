"""Non-executable replay evidence for v3.7 graph planning integrity."""

from __future__ import annotations

from typing import Any

from .v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from .v3_7_graph_integrity_models import (
    V37GraphIntegrityEnforcementResult,
    V37GraphIntegrityReplayEvidence,
    export_v3_7_graph_integrity_replay_evidence,
)


def build_v3_7_graph_integrity_replay_evidence(
    result: V37GraphIntegrityEnforcementResult | None = None,
) -> tuple[V37GraphIntegrityReplayEvidence, ...]:
    enforcement = result or enforce_v3_7_graph_planning_integrity()
    return enforcement.replay_evidence


def validate_v3_7_graph_integrity_replay_evidence(
    result: V37GraphIntegrityEnforcementResult | None = None,
) -> dict[str, Any]:
    enforcement = result or enforce_v3_7_graph_planning_integrity()
    replay = enforcement.replay_evidence
    return {
        "replay_evidence_count": len(replay),
        "rollback_reference_count": len(enforcement.rollback_continuity_references),
        "non_executable_replay_evidence": all(item.non_executable_replay_evidence for item in replay),
        "runtime_replay": any(item.runtime_replay for item in replay),
        "execution_authorization": any(item.execution_authorization for item in replay),
        "replay_continuity_preserved": all(
            item.evidence_source_references
            and item.integrity_finding_references
            and item.provenance_references
            and item.explainability_references
            and item.continuity_hashes
            for item in replay
        ),
        "rollback_continuity_preserved": bool(enforcement.rollback_continuity_references)
        and all(item.continuity_hashes for item in replay),
    }


def export_v3_7_graph_integrity_replay_evidence_records(
    evidence: tuple[V37GraphIntegrityReplayEvidence, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_integrity_replay_evidence(item)
        for item in sorted(evidence, key=lambda record: record.replay_evidence_id)
    ]
