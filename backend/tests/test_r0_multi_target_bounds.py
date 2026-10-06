"""
R0 regression: bounded multi-target simulation (API-2).

The audit reproduced an anonymous request (3600 s, 0.01 s tick, 10 targets)
using ~1.66 GB RSS; a larger one was SIGKILLed. Oversized requests must be
rejected before any simulation state is built, and the response is bounded.
"""

from unittest.mock import patch

import pytest

from app.routes import multi_target as mt

URL = "/api/simulate/multi-target"


def _targets(n, hp=10_000):
    return [{"target_id": f"t{i}", "max_health": hp, "position_index": i} for i in range(n)]


def _post(client, **overrides):
    body = {"base_damage": 1000, "tick_size": 0.1, "max_duration": 60, "targets": _targets(2)}
    body.update(overrides)
    return client.post(URL, json=body)


@pytest.fixture
def engine_spy():
    """Fails loudly if the engine runs for a request that should be rejected."""
    with patch("app.services.multi_target_encounter.MultiTargetEncounterEngine.run") as run:
        yield run


def test_audit_reproduction_payload_rejected_before_simulation(client, engine_spy):
    resp = _post(client, max_duration=3600, tick_size=0.01, targets=_targets(10, hp=1e12))
    assert resp.status_code == 422
    engine_spy.assert_not_called()


@pytest.mark.parametrize("overrides", [
    {"max_duration": mt.MAX_DURATION_SECONDS + 0.001},
    {"tick_size": mt.MIN_TICK_SECONDS / 2},
    {"tick_size": 0},
    {"tick_size": mt.MAX_TICK_SECONDS + 1},
    {"targets": _targets(mt.MAX_TARGETS + 1)},
    {"targets": [{"target_id": "t", "max_health": 0}]},
    {"targets": [{"target_id": "t", "max_health": mt.MAX_HEALTH * 10}]},
    {"base_damage": mt.MAX_BASE_DAMAGE * 10},
    {"base_damage": 0},
    {"max_duration": 300, "tick_size": 0.01, "targets": _targets(5)},  # 150k steps
])
def test_oversized_requests_rejected(client, engine_spy, overrides):
    assert _post(client, **overrides).status_code == 422
    engine_spy.assert_not_called()


def test_template_respects_step_budget(client, engine_spy):
    # mob_swarm has 10 targets: 300 s / 0.01 s x 10 = 300k steps
    resp = client.post(URL, json={"base_damage": 1, "tick_size": 0.01, "max_duration": 300,
                                  "template": "mob_swarm"})
    assert resp.status_code == 422
    engine_spy.assert_not_called()


def test_step_budget_boundary_is_inclusive():
    # 300 s / 0.01 s x 4 targets = 120,000 steps exactly
    assert mt.simulation_steps(300, 0.01, 4) == mt.MAX_SIMULATION_STEPS


def test_boundary_request_accepted(client):
    resp = _post(client, max_duration=300, tick_size=0.01, targets=_targets(4, hp=1e12), base_damage=1)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["damage_events_total"] > mt.MAX_RETURNED_EVENTS
    assert data["damage_events_truncated"] is True
    assert len(data["damage_events"]) == mt.MAX_RETURNED_EVENTS


def test_default_ui_request_still_works(client):
    resp = _post(client)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["cleared"] is True
    assert data["damage_events_truncated"] is False
    assert len(data["damage_events"]) == data["damage_events_total"]


@pytest.mark.parametrize("template", ["single_boss", "elite_pack", "mob_swarm"])
def test_templates_with_default_settings_still_work(client, template):
    resp = client.post(URL, json={"base_damage": 5000, "template": template})
    assert resp.status_code == 200
