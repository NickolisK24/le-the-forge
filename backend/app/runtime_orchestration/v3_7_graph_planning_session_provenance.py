"""Provenance continuity for v3.7 graph planning sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance
from .v3_7_graph_planning_session_models import V37GraphPlanningSession
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED = "v3_7_graph_planning_session_provenance_preserved"
V37_GRAPH_PLANNING_SESSION_PROVENANCE_BLOCKED = "v3_7_graph_planning_session_provenance_blocked"


@dataclass(frozen=True)
class V37GraphPlanningSessionProvenanceResult:
    provenance_status: str
    session_creation_provenance_preserved: bool
    graph_snapshot_provenance_preserved: bool
    evaluation_provenance_preserved: bool
    replay_provenance_preserved: bool
    rollback_provenance_preserved: bool
    audit_provenance_preserved: bool
    explainability_provenance_preserved: bool
    continuity_provenance_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_planning_session_provenance(
    session: V37GraphPlanningSession | None = None,
) -> V37GraphPlanningSessionProvenanceResult:
    planning_session = session or build_v3_7_graph_planning_session()
    missing: list[str] = []
    session_ok = _provenance_complete(planning_session.provenance)
    if not session_ok:
        missing.append(planning_session.identity.session_id)
    snapshot_ok = _all_complete(
        ((snapshot.snapshot_id, snapshot.provenance) for snapshot in planning_session.snapshots),
        missing,
    )
    evaluation_ok = all(evidence.provenance_references for evidence in planning_session.evaluation_evidence)
    if not evaluation_ok:
        missing.append("session_evaluation_evidence")
    replay_ok = all(evidence.provenance_references for evidence in planning_session.replay_evidence)
    if not replay_ok:
        missing.append("session_replay_evidence")
    rollback_ok = all(evidence.provenance_references and evidence.rollback_reference_ids for evidence in planning_session.rollback_evidence)
    if not rollback_ok:
        missing.append("session_rollback_evidence")
    audit_ok = all(entry.evidence_references for entry in planning_session.audit_trail)
    if not audit_ok:
        missing.append("session_audit_trail")
    explainability_ok = bool(planning_session.explainability_reference_ids) and all(
        snapshot.explainability_references for snapshot in planning_session.snapshots
    )
    if not explainability_ok:
        missing.append("session_explainability")
    continuity_ok = bool(planning_session.continuity_hash_references) and all(
        snapshot.replay_continuity_references and snapshot.rollback_continuity_references
        for snapshot in planning_session.snapshots
    )
    if not continuity_ok:
        missing.append("session_continuity")
    replay_continuity_ok = all(evidence.replay_packet_references for evidence in planning_session.replay_evidence)
    rollback_continuity_ok = all(evidence.rollback_reference_ids for evidence in planning_session.rollback_evidence)
    preserved = all(
        (
            session_ok,
            snapshot_ok,
            evaluation_ok,
            replay_ok,
            rollback_ok,
            audit_ok,
            explainability_ok,
            continuity_ok,
            replay_continuity_ok,
            rollback_continuity_ok,
        )
    )
    records = collect_v3_7_graph_planning_session_provenance(planning_session)
    result = V37GraphPlanningSessionProvenanceResult(
        provenance_status=(
            V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED
            if preserved
            else V37_GRAPH_PLANNING_SESSION_PROVENANCE_BLOCKED
        ),
        session_creation_provenance_preserved=session_ok,
        graph_snapshot_provenance_preserved=snapshot_ok,
        evaluation_provenance_preserved=evaluation_ok,
        replay_provenance_preserved=replay_ok,
        rollback_provenance_preserved=rollback_ok,
        audit_provenance_preserved=audit_ok,
        explainability_provenance_preserved=bool(explainability_ok),
        continuity_provenance_preserved=continuity_ok,
        replay_continuity_preserved=replay_continuity_ok,
        rollback_continuity_preserved=rollback_continuity_ok,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(
        result,
        deterministic_provenance_hash=hash_v3_7_graph_planning_session_provenance_result(result),
    )


def collect_v3_7_graph_planning_session_provenance(
    session: V37GraphPlanningSession,
) -> tuple[V37GraphProvenance, ...]:
    records = [session.provenance]
    records.extend(snapshot.provenance for snapshot in session.snapshots)
    return tuple(sorted(records, key=lambda item: item.provenance_id))


def export_v3_7_graph_planning_session_provenance_result(
    result: V37GraphPlanningSessionProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_planning_session_provenance_result(
    result: V37GraphPlanningSessionProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_planning_session_provenance_result(result))


def hash_v3_7_graph_planning_session_provenance_result(
    result: V37GraphPlanningSessionProvenanceResult,
) -> str:
    data = export_v3_7_graph_planning_session_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def _all_complete(records: object, missing: list[str]) -> bool:
    complete = True
    for subject_id, provenance in records:
        if not _provenance_complete(provenance):
            missing.append(subject_id)
            complete = False
    return complete


def _provenance_complete(provenance: V37GraphProvenance) -> bool:
    return all(
        (
            provenance.provenance_id,
            provenance.source_phase_id,
            provenance.source_artifact_id,
            provenance.source_kind,
            provenance.lineage_references,
            provenance.replay_lineage_references,
            provenance.rollback_lineage_references,
            provenance.governance_references,
            provenance.compatibility_references,
            provenance.explainability_references,
        )
    )
