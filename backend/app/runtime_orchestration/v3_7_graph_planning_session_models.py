"""Deterministic v3.7 graph planning session models.

Planning sessions are immutable evidence containers for graph reasoning. They
do not execute graphs, route work, schedule work, dispatch work, mutate runtime
state, or store runtime orchestration behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance


V3_7_GRAPH_PLANNING_SESSION_PHASE_ID = "v3_7_graph_planning_sessions"
V37_SESSION_STATUS_INITIALIZED = "initialized"
V37_SESSION_STATUS_EVALUATED = "evaluated"
V37_SESSION_STATUS_BLOCKED = "blocked"
V37_SESSION_STATUS_UNSUPPORTED = "unsupported"
V37_SESSION_STATUS_PROHIBITED = "prohibited"
V37_SESSION_STATUS_UNKNOWN = "unknown"
V37_SESSION_STATUS_AUDIT_FAILED = "audit_failed"
V37_SESSION_STATUS_CLOSED = "closed"
V37_GRAPH_PLANNING_SESSION_STATUSES: tuple[str, ...] = (
    V37_SESSION_STATUS_INITIALIZED,
    V37_SESSION_STATUS_EVALUATED,
    V37_SESSION_STATUS_BLOCKED,
    V37_SESSION_STATUS_UNSUPPORTED,
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_AUDIT_FAILED,
    V37_SESSION_STATUS_CLOSED,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphPlanningSessionIdentity:
    session_id: str
    graph_id: str
    session_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphPlanningSessionMetadata:
    metadata_key: str
    metadata_value: str


@dataclass(frozen=True)
class V37GraphPlanningSessionSnapshot:
    snapshot_id: str
    session_id: str
    graph_id: str
    graph_hash: str
    graph_serialization_hash: str
    governance_evidence_references: tuple[str, ...]
    compatibility_evidence_references: tuple[str, ...]
    evaluation_evidence_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    replay_continuity_references: tuple[str, ...]
    rollback_continuity_references: tuple[str, ...]
    provenance: V37GraphProvenance
    snapshot_is_executable: bool = False
    execution_state: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "governance_evidence_references",
            "compatibility_evidence_references",
            "evaluation_evidence_references",
            "provenance_references",
            "explainability_references",
            "replay_continuity_references",
            "rollback_continuity_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphPlanningSessionEvaluationEvidence:
    evidence_id: str
    session_id: str
    snapshot_id: str
    evaluation_trace_references: tuple[str, ...]
    evaluation_finding_references: tuple[str, ...]
    evaluation_hash: str
    evaluation_validation_hash: str
    continuity_audit_hash: str
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_trace_references",
            "evaluation_finding_references",
            "provenance_references",
            "explainability_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphPlanningSessionReplayEvidence:
    replay_evidence_id: str
    session_id: str
    snapshot_id: str
    evaluation_trace_references: tuple[str, ...]
    replay_packet_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    rollback_evidence_references: tuple[str, ...]
    non_executable_replay_evidence: bool = True
    runtime_replay: bool = False
    orchestration_runtime_packet: bool = False
    execution_authorization: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_trace_references",
            "replay_packet_references",
            "provenance_references",
            "explainability_references",
            "continuity_hashes",
            "rollback_evidence_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphPlanningSessionRollbackEvidence:
    rollback_evidence_id: str
    session_id: str
    snapshot_id: str
    rollback_reference_ids: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    provenance_references: tuple[str, ...]
    rollback_safe: bool = True
    runtime_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("rollback_reference_ids", "continuity_hashes", "provenance_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphPlanningSessionAuditTrailEntry:
    audit_entry_id: str
    audit_order: int
    audit_type: str
    session_status: str
    subject_type: str
    subject_id: str
    message: str
    evidence_references: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37GraphPlanningSession:
    identity: V37GraphPlanningSessionIdentity
    status: str
    metadata: tuple[V37GraphPlanningSessionMetadata, ...]
    snapshots: tuple[V37GraphPlanningSessionSnapshot, ...]
    evaluation_evidence: tuple[V37GraphPlanningSessionEvaluationEvidence, ...]
    replay_evidence: tuple[V37GraphPlanningSessionReplayEvidence, ...]
    rollback_evidence: tuple[V37GraphPlanningSessionRollbackEvidence, ...]
    audit_trail: tuple[V37GraphPlanningSessionAuditTrailEntry, ...]
    provenance: V37GraphProvenance
    explainability_reference_ids: tuple[str, ...]
    continuity_hash_references: tuple[str, ...]
    planning_sessions_are_non_executable: bool = True
    evidence_container_only: bool = True
    session_replay_evidence_is_not_runtime_replay: bool = True
    snapshots_do_not_imply_execution_state: bool = True
    audit_trails_do_not_imply_runtime_history: bool = True
    session_statuses_do_not_authorize_orchestration: bool = True
    graph_planning_sessions_do_not_enable_routing_scheduling_dispatch: bool = True
    graph_execution_enabled: bool = False
    session_execution_enabled: bool = False
    runtime_orchestration_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    graph_traversal_execution_enabled: bool = False
    path_selection_enabled: bool = False
    graph_optimization_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    background_orchestration_processing_enabled: bool = False
    execution_capable_session_state_enabled: bool = False
    session_driven_orchestration_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "snapshots",
            "evaluation_evidence",
            "replay_evidence",
            "rollback_evidence",
            "audit_trail",
            "explainability_reference_ids",
            "continuity_hash_references",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_graph_planning_session_identity(
    identity: V37GraphPlanningSessionIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_planning_session_metadata(
    metadata: V37GraphPlanningSessionMetadata,
) -> dict[str, Any]:
    return asdict(metadata)


def export_v3_7_graph_planning_session_snapshot(
    snapshot: V37GraphPlanningSessionSnapshot,
) -> dict[str, Any]:
    data = asdict(snapshot)
    for field_name in (
        "governance_evidence_references",
        "compatibility_evidence_references",
        "evaluation_evidence_references",
        "provenance_references",
        "explainability_references",
        "replay_continuity_references",
        "rollback_continuity_references",
    ):
        data[field_name] = sorted(data[field_name])
    data["provenance"] = _export_provenance(snapshot.provenance)
    return data


def export_v3_7_graph_planning_session_evaluation_evidence(
    evidence: V37GraphPlanningSessionEvaluationEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evaluation_trace_references",
        "evaluation_finding_references",
        "provenance_references",
        "explainability_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_planning_session_replay_evidence(
    evidence: V37GraphPlanningSessionReplayEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evaluation_trace_references",
        "replay_packet_references",
        "provenance_references",
        "explainability_references",
        "continuity_hashes",
        "rollback_evidence_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_planning_session_rollback_evidence(
    evidence: V37GraphPlanningSessionRollbackEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in ("rollback_reference_ids", "continuity_hashes", "provenance_references"):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_planning_session_audit_trail_entry(
    entry: V37GraphPlanningSessionAuditTrailEntry,
) -> dict[str, Any]:
    data = asdict(entry)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_planning_session(session: V37GraphPlanningSession) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_planning_session_identity(session.identity),
        "status": session.status,
        "metadata": [
            export_v3_7_graph_planning_session_metadata(metadata)
            for metadata in sorted(session.metadata, key=lambda item: item.metadata_key)
        ],
        "snapshots": [
            export_v3_7_graph_planning_session_snapshot(snapshot)
            for snapshot in sorted(session.snapshots, key=lambda item: item.snapshot_id)
        ],
        "evaluation_evidence": [
            export_v3_7_graph_planning_session_evaluation_evidence(evidence)
            for evidence in sorted(session.evaluation_evidence, key=lambda item: item.evidence_id)
        ],
        "replay_evidence": [
            export_v3_7_graph_planning_session_replay_evidence(evidence)
            for evidence in sorted(session.replay_evidence, key=lambda item: item.replay_evidence_id)
        ],
        "rollback_evidence": [
            export_v3_7_graph_planning_session_rollback_evidence(evidence)
            for evidence in sorted(session.rollback_evidence, key=lambda item: item.rollback_evidence_id)
        ],
        "audit_trail": [
            export_v3_7_graph_planning_session_audit_trail_entry(entry)
            for entry in sorted(session.audit_trail, key=lambda item: (item.audit_order, item.audit_entry_id))
        ],
        "provenance": _export_provenance(session.provenance),
        "explainability_reference_ids": sorted(session.explainability_reference_ids),
        "continuity_hash_references": sorted(session.continuity_hash_references),
        "planning_sessions_are_non_executable": session.planning_sessions_are_non_executable,
        "evidence_container_only": session.evidence_container_only,
        "session_replay_evidence_is_not_runtime_replay": session.session_replay_evidence_is_not_runtime_replay,
        "snapshots_do_not_imply_execution_state": session.snapshots_do_not_imply_execution_state,
        "audit_trails_do_not_imply_runtime_history": session.audit_trails_do_not_imply_runtime_history,
        "session_statuses_do_not_authorize_orchestration": session.session_statuses_do_not_authorize_orchestration,
        "graph_planning_sessions_do_not_enable_routing_scheduling_dispatch": (
            session.graph_planning_sessions_do_not_enable_routing_scheduling_dispatch
        ),
        "graph_execution_enabled": session.graph_execution_enabled,
        "session_execution_enabled": session.session_execution_enabled,
        "runtime_orchestration_enabled": session.runtime_orchestration_enabled,
        "routing_enabled": session.routing_enabled,
        "scheduling_enabled": session.scheduling_enabled,
        "dispatch_enabled": session.dispatch_enabled,
        "graph_traversal_execution_enabled": session.graph_traversal_execution_enabled,
        "path_selection_enabled": session.path_selection_enabled,
        "graph_optimization_enabled": session.graph_optimization_enabled,
        "recommendation_enabled": session.recommendation_enabled,
        "autonomous_orchestration_enabled": session.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": session.runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": session.persistent_runtime_writes_enabled,
        "background_orchestration_processing_enabled": session.background_orchestration_processing_enabled,
        "execution_capable_session_state_enabled": session.execution_capable_session_state_enabled,
        "session_driven_orchestration_behavior_enabled": session.session_driven_orchestration_behavior_enabled,
    }


def export_v3_7_graph_planning_session_counts(session: V37GraphPlanningSession) -> dict[str, int]:
    return {
        "planning_session_count": 1,
        "snapshot_count": len(session.snapshots),
        "evaluation_evidence_count": len(session.evaluation_evidence),
        "replay_evidence_count": len(session.replay_evidence),
        "rollback_evidence_count": len(session.rollback_evidence),
        "audit_trail_count": len(session.audit_trail),
    }


def serialize_v3_7_graph_planning_session(session: V37GraphPlanningSession) -> str:
    return stable_serialize(export_v3_7_graph_planning_session(session))


def hash_v3_7_graph_planning_session(session: V37GraphPlanningSession) -> str:
    return deterministic_hash(export_v3_7_graph_planning_session(session))


def validate_v3_7_graph_planning_session_serialization_stability(
    session: V37GraphPlanningSession,
) -> dict[str, Any]:
    first = serialize_v3_7_graph_planning_session(session)
    second = serialize_v3_7_graph_planning_session(session)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_graph_planning_session",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_graph_planning_session_hash_stability(
    session: V37GraphPlanningSession,
) -> dict[str, Any]:
    first = hash_v3_7_graph_planning_session(session)
    second = hash_v3_7_graph_planning_session(session)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_planning_session",
    }


def _export_provenance(provenance: V37GraphProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in (
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "governance_references",
        "compatibility_references",
        "explainability_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data
