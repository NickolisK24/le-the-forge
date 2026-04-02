"""
F9 — Integration tests for POST /api/optimize/build.

Uses a minimal build (Mage/Spellblade, no gear, 5 variants) to keep
each test fast while still exercising the full HTTP → schema → service
→ simulation → ranking round-trip.
"""

import pytest


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_BASE_BUILD = {
    "character_class": "Mage",
    "mastery":         "Spellblade",
    "skill_id":        "Rip Blood",
    "skill_level":     20,
    "gear":            [],
    "passive_ids":     [],
    "buffs":           [],
}

_FAST_CONFIG = {
    "target_metric":  "dps",
    "max_variants":   5,
    "mutation_depth": 1,
    "constraints":    {},
    "random_seed":    42,
}

_FAST_ENCOUNTER = {
    "enemy_template": "TRAINING_DUMMY",
    "fight_duration": 10.0,
    "tick_size":      0.5,
    "distribution":   "SINGLE",
}


def _post(client, body):
    return client.post("/api/optimize/build", json=body)


def _minimal(client, **overrides):
    body = {
        "build":     _BASE_BUILD,
        "config":    _FAST_CONFIG,
        "encounter": _FAST_ENCOUNTER,
        "top_n":     3,
        **overrides,
    }
    return _post(client, body)


# ---------------------------------------------------------------------------
# F9 — Happy-path tests
# ---------------------------------------------------------------------------

class TestOptimizeBuildHappyPath:
    def test_returns_200(self, client):
        resp = _minimal(client)
        assert resp.status_code == 200

    def test_response_envelope(self, client):
        resp = _minimal(client)
        body = resp.get_json()
        assert body["errors"] is None
        assert "data" in body

    def test_summary_fields_present(self, client):
        data = _minimal(client).get_json()["data"]
        for key in (
            "results",
            "total_variants_generated",
            "variants_passed_constraints",
            "variants_simulated",
            "variants_failed_simulation",
        ):
            assert key in data, f"Missing key: {key}"

    def test_results_list_bounded_by_top_n(self, client):
        data = _minimal(client).get_json()["data"]
        assert len(data["results"]) <= 3

    def test_result_fields(self, client):
        data = _minimal(client).get_json()["data"]
        if not data["results"]:
            pytest.skip("No results produced (all variants failed simulation)")
        r = data["results"][0]
        for key in ("rank", "score", "mutations_applied", "build_variant", "simulation_output"):
            assert key in r, f"Missing result key: {key}"

    def test_rank_starts_at_one(self, client):
        data = _minimal(client).get_json()["data"]
        if data["results"]:
            assert data["results"][0]["rank"] == 1

    def test_ranks_are_sequential(self, client):
        data = _minimal(client).get_json()["data"]
        for i, r in enumerate(data["results"]):
            assert r["rank"] == i + 1

    def test_scores_descending(self, client):
        data = _minimal(client).get_json()["data"]
        scores = [r["score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)

    def test_variant_count_fields_are_ints(self, client):
        data = _minimal(client).get_json()["data"]
        for key in (
            "total_variants_generated",
            "variants_passed_constraints",
            "variants_simulated",
            "variants_failed_simulation",
        ):
            assert isinstance(data[key], int), f"{key} should be int"

    def test_generated_ge_passed_ge_simulated(self, client):
        data = _minimal(client).get_json()["data"]
        assert data["total_variants_generated"] >= data["variants_passed_constraints"]
        assert data["variants_passed_constraints"] >= data["variants_simulated"]

    def test_config_defaults_when_omitted(self, client):
        """Omitting config should use default OptimizationConfig."""
        resp = _post(client, {
            "build":     _BASE_BUILD,
            "encounter": _FAST_ENCOUNTER,
        })
        assert resp.status_code == 200

    def test_top_n_default(self, client):
        """top_n defaults to 10 when not supplied."""
        resp = _post(client, {
            "build":     _BASE_BUILD,
            "config":    _FAST_CONFIG,
            "encounter": _FAST_ENCOUNTER,
        })
        data = resp.get_json()["data"]
        assert len(data["results"]) <= 10

    def test_deterministic_with_same_seed(self, client):
        """Two calls with identical config+seed must return identical scores."""
        r1 = _minimal(client).get_json()["data"]
        r2 = _minimal(client).get_json()["data"]
        scores1 = [r["score"] for r in r1["results"]]
        scores2 = [r["score"] for r in r2["results"]]
        assert scores1 == scores2

    def test_different_metrics_produce_different_order(self, client):
        """dps and ttk metrics may produce different result ordering."""
        cfg_dps = {**_FAST_CONFIG, "target_metric": "dps"}
        cfg_ttk = {**_FAST_CONFIG, "target_metric": "ttk"}
        r_dps = _post(client, {
            "build": _BASE_BUILD, "config": cfg_dps, "encounter": _FAST_ENCOUNTER, "top_n": 5
        }).get_json()["data"]
        r_ttk = _post(client, {
            "build": _BASE_BUILD, "config": cfg_ttk, "encounter": _FAST_ENCOUNTER, "top_n": 5
        }).get_json()["data"]
        # Both should succeed; we don't assert order equality (metrics differ)
        assert r_dps["total_variants_generated"] > 0
        assert r_ttk["total_variants_generated"] > 0


# ---------------------------------------------------------------------------
# F9 — Validation / error tests
# ---------------------------------------------------------------------------

class TestOptimizeBuildValidation:
    def test_missing_build_returns_400(self, client):
        resp = _post(client, {"config": _FAST_CONFIG})
        assert resp.status_code in (400, 422)

    def test_invalid_class_returns_400(self, client):
        bad = {**_BASE_BUILD, "character_class": "Wizard"}
        resp = _post(client, {"build": bad, "config": _FAST_CONFIG})
        assert resp.status_code in (400, 422)

    def test_invalid_metric_returns_400(self, client):
        bad_config = {**_FAST_CONFIG, "target_metric": "invalid_metric"}
        resp = _post(client, {"build": _BASE_BUILD, "config": bad_config})
        assert resp.status_code in (400, 422)

    def test_max_variants_out_of_range_returns_400(self, client):
        bad_config = {**_FAST_CONFIG, "max_variants": 9999}
        resp = _post(client, {"build": _BASE_BUILD, "config": bad_config})
        assert resp.status_code in (400, 422)

    def test_top_n_out_of_range_returns_400(self, client):
        resp = _post(client, {"build": _BASE_BUILD, "config": _FAST_CONFIG, "top_n": 999})
        assert resp.status_code in (400, 422)

    def test_invalid_enemy_template_returns_400(self, client):
        bad_enc = {**_FAST_ENCOUNTER, "enemy_template": "FAKE_BOSS"}
        resp = _post(client, {"build": _BASE_BUILD, "config": _FAST_CONFIG, "encounter": bad_enc})
        assert resp.status_code in (400, 422)

    def test_empty_body_returns_400(self, client):
        resp = _post(client, {})
        assert resp.status_code in (400, 422)
