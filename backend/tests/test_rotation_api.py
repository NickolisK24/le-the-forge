"""G12 — POST /api/simulate/rotation integration tests"""
import pytest


_SKILLS = [
    {"skill_id": "fireball", "base_damage": 200.0, "cooldown": 1.0},
    {"skill_id": "frostbolt", "base_damage": 150.0, "cooldown": 1.5},
]

_ROTATION = {
    "rotation_id": "test",
    "steps": [
        {"skill_id": "fireball", "priority": 0},
        {"skill_id": "frostbolt", "priority": 1},
    ],
    "loop": True,
}

_ENC = {
    "enemy_template": "TRAINING_DUMMY",
    "fight_duration": 5.0,
    "tick_size": 0.5,
    "distribution": "SINGLE",
}


def _post(client, body):
    return client.post("/api/simulate/rotation", json=body)


def _body(**overrides):
    base = {
        "rotation": _ROTATION,
        "skills":   _SKILLS,
        "duration": 5.0,
        "gcd":      0.0,
        "encounter": _ENC,
    }
    base.update(overrides)
    return base


class TestRequestValidation:
    def test_missing_rotation_returns_error(self, client):
        resp = _post(client, {"skills": _SKILLS})
        assert resp.status_code in (400, 422)

    def test_missing_skills_returns_error(self, client):
        resp = _post(client, {"rotation": _ROTATION})
        assert resp.status_code in (400, 422)

    def test_empty_steps_returns_error(self, client):
        bad_rot = {**_ROTATION, "steps": []}
        resp = _post(client, _body(rotation=bad_rot))
        assert resp.status_code in (400, 422)

    def test_invalid_template_returns_error(self, client):
        bad_enc = {**_ENC, "enemy_template": "FAKE_BOSS"}
        resp = _post(client, _body(encounter=bad_enc))
        assert resp.status_code in (400, 422)

    def test_duration_out_of_range_returns_error(self, client):
        resp = _post(client, _body(duration=0.5))
        assert resp.status_code in (400, 422)

    def test_gcd_out_of_range_returns_error(self, client):
        resp = _post(client, _body(gcd=99.0))
        assert resp.status_code in (400, 422)


class TestResponseValidation:
    def test_returns_200(self, client):
        resp = _post(client, _body())
        assert resp.status_code == 200

    def test_envelope_shape(self, client):
        body = _post(client, _body()).get_json()
        assert body["errors"] is None
        assert "data" in body

    def test_top_level_fields(self, client):
        data = _post(client, _body()).get_json()["data"]
        for key in ("total_damage", "dps", "total_casts", "rotation_metrics", "cast_results"):
            assert key in data, f"Missing key: {key}"

    def test_rotation_metrics_fields(self, client):
        data = _post(client, _body()).get_json()["data"]
        m = data["rotation_metrics"]
        for key in ("total_damage", "total_casts", "dps", "uptime_fraction",
                    "idle_time", "efficiency", "cast_counts", "damage_by_skill",
                    "avg_cast_interval"):
            assert key in m

    def test_cast_results_is_list(self, client):
        data = _post(client, _body()).get_json()["data"]
        assert isinstance(data["cast_results"], list)

    def test_total_casts_positive(self, client):
        data = _post(client, _body()).get_json()["data"]
        assert data["total_casts"] > 0

    def test_total_damage_positive(self, client):
        data = _post(client, _body()).get_json()["data"]
        assert data["total_damage"] > 0

    def test_cast_results_have_correct_keys(self, client):
        data = _post(client, _body()).get_json()["data"]
        if data["cast_results"]:
            c = data["cast_results"][0]
            for key in ("skill_id", "cast_at", "resolves_at", "damage"):
                assert key in c

    def test_no_encounter_defaults_ok(self, client):
        """Omitting encounter should use defaults."""
        body = {"rotation": _ROTATION, "skills": _SKILLS, "duration": 5.0}
        resp = _post(client, body)
        assert resp.status_code == 200

    def test_gcd_slows_cast_rate(self, client):
        """With GCD=1s, fewer casts fit than with GCD=0."""
        no_gcd = _post(client, _body(gcd=0.0)).get_json()["data"]
        with_gcd = _post(client, _body(gcd=1.0)).get_json()["data"]
        assert no_gcd["total_casts"] >= with_gcd["total_casts"]
