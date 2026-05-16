from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_scenario_identity import (
    DEFAULT_V37_GRAPH_SCENARIO_ID,
    build_v3_7_graph_scenario_identity,
    graph_scenario_identities_are_unique,
    graph_scenario_identity_key,
)


def test_scenario_identity_is_stable_and_deterministic():
    identity = build_v3_7_graph_scenario_identity()

    assert identity.scenario_id == DEFAULT_V37_GRAPH_SCENARIO_ID
    assert identity.phase_id == "v3_7_graph_planning_scenarios"
    assert identity.scenario_version == "v3.7"
    assert identity.stable_identity_key == graph_scenario_identity_key(identity)


def test_scenario_identity_reflects_session_and_graph_scope():
    first = build_v3_7_graph_scenario_identity("session-a", "graph-a")
    second = build_v3_7_graph_scenario_identity("session-b", "graph-a")

    assert first.stable_identity_key != second.stable_identity_key
    assert graph_scenario_identities_are_unique((first, second)) is True
    assert graph_scenario_identities_are_unique((first, replace(first))) is False
