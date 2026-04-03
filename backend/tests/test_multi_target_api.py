"""I14 — Multi-Target API tests."""
import json
import pytest


def _post(client, payload):
    return client.post(
        "/api/simulate/multi-target",
        data=json.dumps(payload),
        content_type="application/json",
    )


_BOSS = {"base_damage": 50000.0, "template": "single_boss", "max_duration": 30.0}
_PACK = {"base_damage": 50000.0, "template": "elite_pack",  "max_duration": 30.0}


class TestRequestValidation:
    def test_missing_base_damage_returns_422(self, client):
        r = _post(client, {"template": "single_boss"})
        assert r.status_code == 422

    def test_zero_base_damage_rejected(self, client):
        r = _post(client, {"base_damage": 0.0, "template": "single_boss"})
        assert r.status_code == 422

    def test_no_template_no_targets_rejected(self, client):
        r = _post(client, {"base_damage": 100.0})
        assert r.status_code == 422

    def test_unknown_template_rejected(self, client):
        r = _post(client, {"base_damage": 100.0, "template": "dragon_boss"})
        assert r.status_code == 422


class TestMultiTargetResponseCorrectness:
    def test_single_boss_clears(self, client):
        r = _post(client, _BOSS)
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["cleared"] is True
        assert data["total_kills"] == 1
        assert data["time_to_clear"] is not None

    def test_elite_pack_clears(self, client):
        r = _post(client, _PACK)
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["total_kills"] == 3

    def test_custom_targets(self, client):
        payload = {
            "base_damage": 10000.0,
            "targets": [
                {"target_id": "enemy_a", "max_health": 500.0},
                {"target_id": "enemy_b", "max_health": 800.0},
            ],
            "distribution": "full_aoe",
            "max_duration": 10.0,
        }
        r = _post(client, payload)
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["total_kills"] == 2

    def test_response_has_metrics(self, client):
        r = _post(client, _BOSS)
        data = r.get_json()["data"]
        assert "metrics" in data
        assert "damage_per_target" in data["metrics"]
