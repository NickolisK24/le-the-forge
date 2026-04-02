"""
D10 — Integration tests for POST /api/simulate/encounter.

Validates the full round-trip: HTTP request → schema → service → engine → response.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# crit_chance=0 → deterministic (no crits, known damage values)
_VALID = {
    "base_damage":     500.0,
    "enemy_template":  "STANDARD_BOSS",
    "fight_duration":  60.0,
    "tick_size":       0.1,
    "distribution":    "SINGLE",
    "crit_chance":     0.0,
    "crit_multiplier": 2.0,
}

# MOVEMENT_BOSS config: weak base_damage so boss survives past the downtime windows
_MOVEMENT = {
    "base_damage":    50.0,
    "enemy_template": "MOVEMENT_BOSS",
    "fight_duration": 90.0,
    "tick_size":      0.1,
    "distribution":   "SINGLE",
    "crit_chance":    0.0,
    "crit_multiplier": 2.0,
}


def _post(client, body):
    return client.post("/api/simulate/encounter", json=body)


# ---------------------------------------------------------------------------
# D10 — Integration
# ---------------------------------------------------------------------------

class TestEncounterEndpointIntegration:
    def test_end_to_end_simulation(self, client):
        """Full round-trip returns valid data."""
        resp = _post(client, _VALID)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["total_damage"] > 0
        assert data["elapsed_time"] > 0
        assert data["ticks_simulated"] > 0

    def test_all_response_fields_present(self, client):
        resp = _post(client, _VALID)
        data = resp.get_json()["data"]
        expected_keys = {
            "total_damage", "dps", "elapsed_time", "ticks_simulated",
            "all_enemies_dead", "enemies_killed", "total_casts",
            "downtime_ticks", "active_phase_id", "damage_per_tick",
        }
        assert expected_keys.issubset(data.keys())

    def test_damage_per_tick_is_list(self, client):
        resp = _post(client, _VALID)
        data = resp.get_json()["data"]
        assert isinstance(data["damage_per_tick"], list)
        assert len(data["damage_per_tick"]) == data["ticks_simulated"]

    def test_dps_computed(self, client):
        resp = _post(client, _VALID)
        data = resp.get_json()["data"]
        expected_dps = data["total_damage"] / data["elapsed_time"]
        assert abs(data["dps"] - expected_dps) < 1.0

    def test_training_dummy_does_not_die(self, client):
        body = {**_VALID, "enemy_template": "TRAINING_DUMMY", "base_damage": 100.0}
        resp = _post(client, body)
        data = resp.get_json()["data"]
        assert data["all_enemies_dead"] is False
        assert data["enemies_killed"] == 0

    def test_standard_boss_killed(self, client):
        resp = _post(client, _VALID)
        data = resp.get_json()["data"]
        assert data["all_enemies_dead"] is True
        assert data["enemies_killed"] == 1

    def test_movement_boss_has_downtime(self, client):
        resp = _post(client, _MOVEMENT)
        data = resp.get_json()["data"]
        assert data["downtime_ticks"] > 0

    def test_cleave_distribution_accepted(self, client):
        body = {**_VALID, "enemy_template": "ADD_FIGHT", "distribution": "CLEAVE"}
        resp = _post(client, body)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["total_damage"] > 0


# ---------------------------------------------------------------------------
# D10 — Schema validation
# ---------------------------------------------------------------------------

class TestEncounterSchemaValidation:
    def test_missing_base_damage_rejected(self, client):
        body = {k: v for k, v in _VALID.items() if k != "base_damage"}
        resp = _post(client, body)
        assert resp.status_code == 422

    def test_negative_base_damage_rejected(self, client):
        resp = _post(client, {**_VALID, "base_damage": -10.0})
        assert resp.status_code == 422

    def test_zero_base_damage_rejected(self, client):
        resp = _post(client, {**_VALID, "base_damage": 0.0})
        assert resp.status_code == 422

    def test_invalid_template_rejected(self, client):
        resp = _post(client, {**_VALID, "enemy_template": "DRAGON_BOSS"})
        assert resp.status_code == 422

    def test_invalid_distribution_rejected(self, client):
        resp = _post(client, {**_VALID, "distribution": "BOUNCE"})
        assert resp.status_code == 422

    def test_crit_chance_above_one_rejected(self, client):
        resp = _post(client, {**_VALID, "crit_chance": 1.5})
        assert resp.status_code == 422

    def test_empty_body_missing_base_damage(self, client):
        resp = _post(client, {})
        assert resp.status_code == 422

    def test_only_base_damage_uses_defaults(self, client):
        resp = _post(client, {"base_damage": 100.0})
        assert resp.status_code == 200

    def test_all_templates_accepted(self, client):
        for tpl in ["TRAINING_DUMMY", "STANDARD_BOSS", "SHIELDED_BOSS", "ADD_FIGHT", "MOVEMENT_BOSS"]:
            resp = _post(client, {**_VALID, "enemy_template": tpl})
            assert resp.status_code == 200, f"Template {tpl} failed"

    def test_all_distributions_accepted(self, client):
        for dist in ["SINGLE", "CLEAVE", "SPLIT", "CHAIN"]:
            resp = _post(client, {**_VALID, "distribution": dist})
            assert resp.status_code == 200, f"Distribution {dist} failed"


# ---------------------------------------------------------------------------
# D11 — Regression: lock known-good values (crit_chance=0 for determinism)
# ---------------------------------------------------------------------------

class TestEncounterApiRegression:
    def test_standard_boss_total_damage(self, client):
        resp = _post(client, _VALID)
        data = resp.get_json()["data"]
        assert abs(data["total_damage"] - 50_000.0) < 500.0

    def test_standard_boss_ticks(self, client):
        """STANDARD_BOSS with base_damage=500, crit=0 dies in ~138 ticks."""
        resp = _post(client, _VALID)
        data = resp.get_json()["data"]
        assert 50 <= data["ticks_simulated"] <= 200

    def test_training_dummy_total_damage(self, client):
        body = {**_VALID, "base_damage": 100.0, "enemy_template": "TRAINING_DUMMY",
                "fight_duration": 60.0}
        resp = _post(client, body)
        data = resp.get_json()["data"]
        assert abs(data["total_damage"] - 60_000.0) < 600.0

    def test_training_dummy_casts(self, client):
        body = {**_VALID, "base_damage": 100.0, "enemy_template": "TRAINING_DUMMY",
                "fight_duration": 60.0}
        resp = _post(client, body)
        data = resp.get_json()["data"]
        assert data["total_casts"] == 600

    def test_movement_boss_downtime_ticks(self, client):
        resp = _post(client, _MOVEMENT)
        data = resp.get_json()["data"]
        assert data["downtime_ticks"] == 60

    def test_determinism_same_request_same_output(self, client):
        # crit_chance=0 → fully deterministic
        r1 = _post(client, _VALID).get_json()["data"]
        r2 = _post(client, _VALID).get_json()["data"]
        assert r1["total_damage"] == r2["total_damage"]
        assert r1["ticks_simulated"] == r2["ticks_simulated"]


# ---------------------------------------------------------------------------
# D12 — Performance
# ---------------------------------------------------------------------------

class TestEncounterApiPerformance:
    def test_single_simulation_under_200ms(self, client):
        import time
        start = time.perf_counter()
        resp = _post(client, _VALID)
        elapsed = time.perf_counter() - start
        assert resp.status_code == 200
        assert elapsed < 0.2, f"Single simulation took {elapsed:.3f}s (budget: 0.2s)"

    def test_50_simulations_under_5s(self, client):
        import time
        start = time.perf_counter()
        for _ in range(50):
            resp = _post(client, _VALID)
            assert resp.status_code == 200
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"50 simulations took {elapsed:.2f}s (budget: 5s)"
