"""H14 — Conditional API Endpoint tests."""
import json
import pytest


def _post(client, payload):
    return client.post(
        "/api/simulate/conditional",
        data=json.dumps(payload),
        content_type="application/json",
    )


class TestRequestValidation:
    def test_missing_base_damage_returns_422(self, client):
        r = _post(client, {"modifiers": []})
        assert r.status_code == 422

    def test_negative_base_damage_returns_422(self, client):
        r = _post(client, {"base_damage": -10.0})
        assert r.status_code == 422

    def test_empty_modifiers_ok(self, client):
        r = _post(client, {"base_damage": 1000.0, "modifiers": []})
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["base_damage"] == 1000.0
        assert data["adjusted_damage"] == 1000.0


class TestResponseCorrectness:
    def _payload(self, target_pct=0.3, modifier_value=50.0):
        return {
            "base_damage": 1000.0,
            "state": {
                "target_health_pct": target_pct,
                "player_health_pct": 1.0,
                "elapsed_time": 5.0,
                "active_buffs": [],
                "active_status_effects": {},
            },
            "modifiers": [
                {
                    "modifier_id":   "low_hp_amp",
                    "stat_target":   "spell_damage_pct",
                    "value":         modifier_value,
                    "modifier_type": "additive",
                    "condition": {
                        "condition_id":        "low_hp_amp_c",
                        "condition_type":      "target_health_pct",
                        "threshold_value":     0.5,
                        "comparison_operator": "lt",
                    },
                }
            ],
        }

    def test_active_modifier_boosts_damage(self, client):
        r = _post(client, self._payload(target_pct=0.3, modifier_value=50.0))
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["adjusted_damage"] == pytest.approx(1500.0)
        assert data["damage_multiplier"] == pytest.approx(1.5)
        assert "low_hp_amp" in data["active_modifier_ids"]

    def test_inactive_modifier_no_change(self, client):
        r = _post(client, self._payload(target_pct=0.8, modifier_value=50.0))
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["adjusted_damage"] == pytest.approx(1000.0)
        assert data["active_modifier_ids"] == []

    def test_buff_condition(self, client):
        payload = {
            "base_damage": 500.0,
            "state": {
                "target_health_pct": 1.0,
                "active_buffs": ["power_surge"],
                "elapsed_time": 0.0,
            },
            "modifiers": [{
                "modifier_id":   "surge_amp",
                "stat_target":   "spell_damage_pct",
                "value":         100.0,
                "modifier_type": "additive",
                "condition": {
                    "condition_id":        "power_surge",
                    "condition_type":      "buff_active",
                    "threshold_value":     None,
                    "comparison_operator": "lt",
                },
            }],
        }
        r = _post(client, payload)
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["adjusted_damage"] == pytest.approx(1000.0)
