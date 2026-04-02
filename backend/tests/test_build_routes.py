"""
E8 — Tests for POST /api/simulate/encounter-build.
E11 — Integration: Build → Stats → Simulation.
E12 — Regression: lock known-good stat and simulation outputs.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LICH_BUILD = {
    "character_class": "Acolyte",
    "mastery":         "Lich",
    "skill_id":        "Rip Blood",
    "skill_level":     20,
    "gear":            [],
    "passive_ids":     [],
    "buffs":           [],
}

_SORCERER_BUILD = {
    "character_class": "Mage",
    "mastery":         "Sorcerer",
    "skill_id":        "Glacial Bolt",
    "skill_level":     20,
    "gear":            [],
    "passive_ids":     [],
    "buffs":           [],
}

_ENCOUNTER = {
    "enemy_template": "STANDARD_BOSS",
    "fight_duration": 60.0,
    "tick_size":      0.1,
    "distribution":   "SINGLE",
    "crit_chance":    0.0,
    "crit_multiplier": 2.0,
}


def _post(client, build=None, encounter=None):
    body = {"build": build or _LICH_BUILD}
    if encounter is not None:
        body["encounter"] = encounter
    return client.post("/api/simulate/encounter-build", json=body)


# ---------------------------------------------------------------------------
# E8 — API endpoint
# ---------------------------------------------------------------------------

class TestEncounterBuildEndpoint:
    def test_basic_success(self, client):
        resp = _post(client)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["total_damage"] > 0

    def test_all_response_fields_present(self, client):
        resp = _post(client)
        data = resp.get_json()["data"]
        for key in ("total_damage", "dps", "elapsed_time", "ticks_simulated",
                    "all_enemies_dead", "enemies_killed", "total_casts",
                    "downtime_ticks", "active_phase_id", "damage_per_tick"):
            assert key in data, f"Missing field: {key}"

    def test_missing_build_rejected(self, client):
        resp = client.post("/api/simulate/encounter-build", json={})
        assert resp.status_code == 422

    def test_invalid_class_rejected(self, client):
        bad = {**_LICH_BUILD, "character_class": "Dragon"}
        resp = _post(client, build=bad)
        assert resp.status_code == 422

    def test_invalid_mastery_rejected(self, client):
        bad = {**_LICH_BUILD, "mastery": "Wizard"}
        resp = _post(client, build=bad)
        assert resp.status_code == 422

    def test_encounter_overrides_accepted(self, client):
        resp = _post(client, encounter=_ENCOUNTER)
        assert resp.status_code == 200

    def test_invalid_encounter_template_rejected(self, client):
        enc = {**_ENCOUNTER, "enemy_template": "FAKE_BOSS"}
        resp = _post(client, encounter=enc)
        assert resp.status_code == 422

    def test_build_with_gear(self, client):
        build = {
            **_LICH_BUILD,
            "gear": [{"slot": "weapon",
                       "affixes": [{"name": "Increased Spell Damage", "tier": 4}],
                       "rarity": "rare"}],
        }
        resp = _post(client, build=build)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["total_damage"] > 0

    def test_build_with_buffs(self, client):
        build = {
            **_LICH_BUILD,
            "buffs": [{"buff_id": "power", "modifiers": {"base_damage": 200.0},
                        "duration": None}],
        }
        resp = _post(client, build=build)
        assert resp.status_code == 200

    def test_movement_boss_has_downtime(self, client):
        enc = {**_ENCOUNTER, "enemy_template": "MOVEMENT_BOSS",
               "fight_duration": 90.0, "crit_chance": 0.0}
        resp = _post(client, build={**_LICH_BUILD, "buffs": [
            {"buff_id": "weak", "modifiers": {"base_damage": -70.0}, "duration": None}
        ]}, encounter=enc)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["downtime_ticks"] > 0

    def test_save_and_load_build_json(self, client):
        """Serialised build token can be decoded and submitted."""
        from builds.build_definition import BuildDefinition
        from builds.serializers       import export_json, import_json
        b  = BuildDefinition.from_dict(_LICH_BUILD)
        raw = export_json(b)
        b2  = import_json(raw)
        resp = _post(client, build=b2.to_dict())
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# E11 — Integration: Build → Stats → Simulation chain
# ---------------------------------------------------------------------------

class TestBuildToSimulationIntegration:
    def test_gear_boosts_damage_in_simulation(self, client):
        bare_resp = _post(client, build=_LICH_BUILD,
                          encounter={**_ENCOUNTER, "crit_chance": 0.0})
        gear_build = {
            **_LICH_BUILD,
            "gear": [{"slot": "weapon",
                       "affixes": [{"name": "Increased Spell Damage", "tier": 4}] * 3,
                       "rarity": "exalted"}],
        }
        gear_resp  = _post(client, build=gear_build,
                           encounter={**_ENCOUNTER, "crit_chance": 0.0})
        bare = bare_resp.get_json()["data"]["total_damage"]
        gear = gear_resp.get_json()["data"]["total_damage"]
        assert gear > bare, "Gear should increase total damage"

    def test_buff_boosts_damage_in_simulation(self, client):
        bare_resp = _post(client, build=_LICH_BUILD,
                          encounter={**_ENCOUNTER, "crit_chance": 0.0})
        buff_build = {
            **_LICH_BUILD,
            "buffs": [{"buff_id": "power", "modifiers": {"base_damage": 200.0},
                        "duration": None}],
        }
        buff_resp  = _post(client, build=buff_build,
                           encounter={**_ENCOUNTER, "crit_chance": 0.0})
        assert buff_resp.get_json()["data"]["total_damage"] > \
               bare_resp.get_json()["data"]["total_damage"]

    def test_deterministic_builds_produce_same_output(self, client):
        enc = {**_ENCOUNTER, "crit_chance": 0.0}
        r1 = _post(client, build=_LICH_BUILD, encounter=enc).get_json()["data"]
        r2 = _post(client, build=_LICH_BUILD, encounter=enc).get_json()["data"]
        assert r1["total_damage"]    == r2["total_damage"]
        assert r1["ticks_simulated"] == r2["ticks_simulated"]

    def test_different_classes_produce_different_damage(self, client):
        enc = {**_ENCOUNTER, "crit_chance": 0.0}
        r_lich = _post(client, build=_LICH_BUILD,     encounter=enc).get_json()["data"]
        r_sorc = _post(client, build=_SORCERER_BUILD, encounter=enc).get_json()["data"]
        assert r_lich["total_damage"] != r_sorc["total_damage"]

    def test_outputs_deterministic_across_requests(self, client):
        enc = {**_ENCOUNTER, "enemy_template": "TRAINING_DUMMY",
               "fight_duration": 30.0, "crit_chance": 0.0}
        results = [_post(client, build=_LICH_BUILD, encounter=enc).get_json()["data"]
                   for _ in range(3)]
        dmg = results[0]["total_damage"]
        assert all(r["total_damage"] == dmg for r in results)


# ---------------------------------------------------------------------------
# E12 — Regression: lock expected stat and simulation outputs
# ---------------------------------------------------------------------------

class TestBuildRegressionStats:
    def test_acolyte_lich_base_damage(self, client):
        """Acolyte base_damage == 80, no modifiers."""
        from builds.build_definition  import BuildDefinition
        from builds.build_stats_engine import BuildStatsEngine
        b     = BuildDefinition.from_dict(_LICH_BUILD)
        stats = BuildStatsEngine().compile(b)
        assert stats.base_damage == 80.0

    def test_acolyte_lich_crit_chance(self, client):
        from builds.build_definition  import BuildDefinition
        from builds.build_stats_engine import BuildStatsEngine
        b     = BuildDefinition.from_dict(_LICH_BUILD)
        stats = BuildStatsEngine().compile(b)
        assert abs(stats.crit_chance - 0.05) < 0.01

    def test_acolyte_lich_crit_multiplier(self, client):
        from builds.build_definition  import BuildDefinition
        from builds.build_stats_engine import BuildStatsEngine
        b     = BuildDefinition.from_dict(_LICH_BUILD)
        stats = BuildStatsEngine().compile(b)
        assert abs(stats.crit_multiplier - 1.5) < 0.05

    def test_training_dummy_deterministic_damage(self, client):
        """Lich (effective_damage=88, crit_mult=1.5) vs training dummy.
        rng_crit=None → always crits → 88 × 1.5 × 600 = 79,200.
        """
        enc = {
            "enemy_template": "TRAINING_DUMMY",
            "fight_duration": 60.0,
            "tick_size":      0.1,
            "distribution":   "SINGLE",
        }
        resp = _post(client, build=_LICH_BUILD, encounter=enc)
        data = resp.get_json()["data"]
        assert abs(data["total_damage"] - 79_200.0) < 1000.0
        assert data["total_casts"] == 600
