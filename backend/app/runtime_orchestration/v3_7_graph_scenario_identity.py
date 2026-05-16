"""Deterministic identity helpers for v3.7 graph planning scenarios."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session
from .v3_7_graph_scenario_models import (
    V3_7_GRAPH_SCENARIO_PHASE_ID,
    V37GraphScenarioIdentity,
)


DEFAULT_V37_GRAPH_SCENARIO_ID = "v3_7_graph_planning_scenario_default"


def build_v3_7_graph_scenario_identity(
    planning_session_id: str | None = None,
    graph_id: str | None = None,
) -> V37GraphScenarioIdentity:
    session = build_v3_7_graph_planning_session()
    source_session_id = planning_session_id or session.identity.session_id
    source_graph_id = graph_id or session.identity.graph_id
    key_payload = {
        "graph_id": source_graph_id,
        "phase_id": V3_7_GRAPH_SCENARIO_PHASE_ID,
        "planning_session_id": source_session_id,
        "scenario_id": DEFAULT_V37_GRAPH_SCENARIO_ID,
        "scenario_version": "v3.7",
    }
    return V37GraphScenarioIdentity(
        scenario_id=DEFAULT_V37_GRAPH_SCENARIO_ID,
        planning_session_id=source_session_id,
        graph_id=source_graph_id,
        scenario_version="v3.7",
        phase_id=V3_7_GRAPH_SCENARIO_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_scenario_identity_key(identity: V37GraphScenarioIdentity) -> str:
    return deterministic_hash(
        {
            "graph_id": identity.graph_id,
            "phase_id": identity.phase_id,
            "planning_session_id": identity.planning_session_id,
            "scenario_id": identity.scenario_id,
            "scenario_version": identity.scenario_version,
        }
    )


def graph_scenario_identities_are_unique(
    identities: tuple[V37GraphScenarioIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))
