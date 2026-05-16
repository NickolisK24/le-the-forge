"""Deterministic graph planning session snapshots and session construction."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_evaluation_models import hash_v3_7_graph_evaluation_chain
from .v3_7_graph_evaluation_replay import build_v3_7_graph_evaluation_replay_packets
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain
from .v3_7_graph_evaluation_validation import validate_v3_7_graph_evaluation
from .v3_7_graph_hashing import hash_v3_7_graph
from .v3_7_graph_models import V37GraphMetadataEntry, default_v3_7_graph_provenance, default_v3_7_orchestration_planning_graph
from .v3_7_graph_planning_session_identity import build_v3_7_graph_planning_session_identity
from .v3_7_graph_planning_session_models import (
    V37_SESSION_STATUS_BLOCKED,
    V37_SESSION_STATUS_EVALUATED,
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_UNSUPPORTED,
    V37GraphPlanningSession,
    V37GraphPlanningSessionAuditTrailEntry,
    V37GraphPlanningSessionEvaluationEvidence,
    V37GraphPlanningSessionMetadata,
    V37GraphPlanningSessionReplayEvidence,
    V37GraphPlanningSessionRollbackEvidence,
    V37GraphPlanningSessionSnapshot,
)
from .v3_7_graph_serialization import serialize_v3_7_graph


def build_v3_7_graph_planning_session() -> V37GraphPlanningSession:
    graph = default_v3_7_orchestration_planning_graph()
    evaluation_chain = build_v3_7_graph_evaluation_chain()
    validation = validate_v3_7_graph_evaluation(evaluation_chain)
    replay_packets = build_v3_7_graph_evaluation_replay_packets(evaluation_chain)
    identity = build_v3_7_graph_planning_session_identity(graph.identity.graph_id)
    snapshots = build_v3_7_graph_planning_session_snapshots(identity.session_id)
    snapshot = snapshots[0]
    evaluation_evidence = (
        V37GraphPlanningSessionEvaluationEvidence(
            evidence_id="v3_7_graph_planning_session_evaluation_evidence",
            session_id=identity.session_id,
            snapshot_id=snapshot.snapshot_id,
            evaluation_trace_references=tuple(trace.trace_id for trace in evaluation_chain.traces),
            evaluation_finding_references=tuple(finding.finding_id for finding in evaluation_chain.findings),
            evaluation_hash=hash_v3_7_graph_evaluation_chain(evaluation_chain),
            evaluation_validation_hash=validation.deterministic_validation_hash,
            continuity_audit_hash=validation.deterministic_evaluation_hash,
            provenance_references=(evaluation_chain.provenance.provenance_id,),
            explainability_references=("v3_7_graph_evaluation_explainability",),
        ),
    )
    rollback_evidence = (
        V37GraphPlanningSessionRollbackEvidence(
            rollback_evidence_id="v3_7_graph_planning_session_rollback_evidence",
            session_id=identity.session_id,
            snapshot_id=snapshot.snapshot_id,
            rollback_reference_ids=tuple(
                sorted({reference for packet in replay_packets for reference in packet.rollback_lineage_references})
            ),
            continuity_hashes=(validation.deterministic_evaluation_hash,),
            provenance_references=(evaluation_chain.provenance.provenance_id,),
        ),
    )
    replay_evidence = (
        V37GraphPlanningSessionReplayEvidence(
            replay_evidence_id="v3_7_graph_planning_session_replay_evidence",
            session_id=identity.session_id,
            snapshot_id=snapshot.snapshot_id,
            evaluation_trace_references=tuple(trace.trace_id for trace in evaluation_chain.traces),
            replay_packet_references=tuple(packet.replay_packet_id for packet in replay_packets),
            provenance_references=tuple(
                sorted({reference for packet in replay_packets for reference in packet.provenance_lineage_references})
            ),
            explainability_references=("v3_7_graph_evaluation_explainability",),
            continuity_hashes=tuple(packet.deterministic_replay_hash for packet in replay_packets),
            rollback_evidence_references=tuple(item.rollback_evidence_id for item in rollback_evidence),
        ),
    )
    audit_trail = build_v3_7_graph_planning_session_audit_trail(identity.session_id)
    return V37GraphPlanningSession(
        identity=identity,
        status=V37_SESSION_STATUS_EVALUATED,
        metadata=(
            V37GraphPlanningSessionMetadata("session_semantics", "deterministic_evidence_container_only"),
            V37GraphPlanningSessionMetadata("runtime_capability", "none"),
            V37GraphPlanningSessionMetadata("status_authorization", "statuses_do_not_authorize_orchestration"),
        ),
        snapshots=snapshots,
        evaluation_evidence=evaluation_evidence,
        replay_evidence=replay_evidence,
        rollback_evidence=rollback_evidence,
        audit_trail=audit_trail,
        provenance=default_v3_7_graph_provenance(identity.session_id, "graph_planning_session"),
        explainability_reference_ids=("v3_7_graph_planning_session_explainability",),
        continuity_hash_references=(
            hash_v3_7_graph(graph),
            validation.deterministic_evaluation_hash,
            replay_packets[0].deterministic_replay_hash,
        ),
    )


def build_v3_7_graph_planning_session_snapshots(
    session_id: str | None = None,
) -> tuple[V37GraphPlanningSessionSnapshot, ...]:
    graph = default_v3_7_orchestration_planning_graph()
    evaluation_chain = build_v3_7_graph_evaluation_chain()
    graph_serialized = serialize_v3_7_graph(graph)
    graph_hash = hash_v3_7_graph(graph)
    return (
        V37GraphPlanningSessionSnapshot(
            snapshot_id="v3_7_graph_planning_session_snapshot_default",
            session_id=session_id or "v3_7_graph_planning_session_default",
            graph_id=graph.identity.graph_id,
            graph_hash=graph_hash,
            graph_serialization_hash=deterministic_hash(graph_serialized),
            governance_evidence_references=("v3_7_graph_governance_boundary_intelligence",),
            compatibility_evidence_references=("v3_7_graph_compatibility_reasoning",),
            evaluation_evidence_references=tuple(trace.trace_id for trace in evaluation_chain.traces),
            provenance_references=(graph.provenance.provenance_id, evaluation_chain.provenance.provenance_id),
            explainability_references=("v3_7_graph_explainability", "v3_7_graph_evaluation_explainability"),
            replay_continuity_references=("v3_7_graph_evaluation_replay_continuity",),
            rollback_continuity_references=("v3_7_graph_evaluation_rollback_continuity",),
            provenance=default_v3_7_graph_provenance(
                "v3_7_graph_planning_session_snapshot_default",
                "graph_planning_session_snapshot",
            ),
        ),
    )


def build_v3_7_graph_planning_session_audit_trail(
    session_id: str,
) -> tuple[V37GraphPlanningSessionAuditTrailEntry, ...]:
    entries = (
        _entry(1, "session_status", V37_SESSION_STATUS_EVALUATED, session_id, "planning session evaluated structural graph evidence"),
        _entry(2, "blocked_visibility", V37_SESSION_STATUS_BLOCKED, session_id, "blocked states remain fail-visible when present"),
        _entry(3, "unsupported_visibility", V37_SESSION_STATUS_UNSUPPORTED, session_id, "unsupported states remain fail-visible"),
        _entry(4, "prohibited_visibility", V37_SESSION_STATUS_PROHIBITED, session_id, "prohibited states remain fail-visible"),
        _entry(5, "unknown_visibility", V37_SESSION_STATUS_UNKNOWN, session_id, "unknown states remain fail-visible"),
        _entry(6, "non_execution_boundary", V37_SESSION_STATUS_EVALUATED, session_id, "planning session contains evidence only"),
    )
    return entries


def _entry(
    order: int,
    audit_type: str,
    status: str,
    session_id: str,
    message: str,
) -> V37GraphPlanningSessionAuditTrailEntry:
    return V37GraphPlanningSessionAuditTrailEntry(
        audit_entry_id=f"v3_7_graph_planning_session_audit_{order:04d}_{audit_type}",
        audit_order=order,
        audit_type=audit_type,
        session_status=status,
        subject_type="graph_planning_session",
        subject_id=session_id,
        message=message,
        evidence_references=(session_id, audit_type),
        fail_visible=True,
        hidden=False,
    )
