"""Deterministic identity helpers for v3.7 graph planning sessions."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain
from .v3_7_graph_planning_session_models import (
    V3_7_GRAPH_PLANNING_SESSION_PHASE_ID,
    V37GraphPlanningSessionIdentity,
)


DEFAULT_V37_GRAPH_PLANNING_SESSION_ID = "v3_7_graph_planning_session_default"


def build_v3_7_graph_planning_session_identity(graph_id: str | None = None) -> V37GraphPlanningSessionIdentity:
    source_graph_id = graph_id or build_v3_7_graph_evaluation_chain().graph_id
    key_payload = {
        "graph_id": source_graph_id,
        "phase_id": V3_7_GRAPH_PLANNING_SESSION_PHASE_ID,
        "session_id": DEFAULT_V37_GRAPH_PLANNING_SESSION_ID,
        "session_version": "v3.7",
    }
    return V37GraphPlanningSessionIdentity(
        session_id=DEFAULT_V37_GRAPH_PLANNING_SESSION_ID,
        graph_id=source_graph_id,
        session_version="v3.7",
        phase_id=V3_7_GRAPH_PLANNING_SESSION_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_planning_session_identity_key(identity: V37GraphPlanningSessionIdentity) -> str:
    return deterministic_hash(
        {
            "graph_id": identity.graph_id,
            "phase_id": identity.phase_id,
            "session_id": identity.session_id,
            "session_version": identity.session_version,
        }
    )


def graph_planning_session_identities_are_unique(
    identities: tuple[V37GraphPlanningSessionIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))
