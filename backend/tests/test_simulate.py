"""
Tests for the /api/simulate endpoints — verifying the backend acts as
the single source of truth for all simulation math.
"""

import pytest


# ---------------------------------------------------------------------------
# POST /api/simulate/stats
# ---------------------------------------------------------------------------

class TestSimulateStats:
    def test_basic_stat_aggregation(self, client):
        """Aggregate stats for a Lich with no passives or gear."""
        resp = client.post("/api/simulate/stats", json={
            "character_class": "Acolyte",
            "mastery": "Lich",
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        # Acolyte base health = 380, Lich gets no flat mastery bonus for health
        assert data["max_health"] > 0
        assert data["base_damage"] == 80.0  # Acolyte base
        assert data["attack_speed"] > 0

    def test_with_gear_affixes(self, client):
        """Gear affixes should increase stats."""
        resp = client.post("/api/simulate/stats", json={
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "gear_affixes": [
                {"name": "Spell Damage", "tier": 3},
                {"name": "Health", "tier": 2},
            ],
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        # Sorcerer gets spell_damage_pct bonus + gear affix
        assert data["spell_damage_pct"] > 0
        assert data["max_health"] > 340  # Mage base health

    def test_invalid_class(self, client):
        resp = client.post("/api/simulate/stats", json={
            "character_class": "InvalidClass",
            "mastery": "Lich",
        })
        assert resp.status_code == 422

    def test_mismatched_mastery(self, client):
        resp = client.post("/api/simulate/stats", json={
            "character_class": "Mage",
            "mastery": "Lich",  # Lich is Acolyte, not Mage
        })
        assert resp.status_code == 422

    def test_empty_body(self, client):
        resp = client.post("/api/simulate/stats", json={})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/simulate/combat
# ---------------------------------------------------------------------------

class TestSimulateCombat:
    def test_basic_dps(self, client):
        """DPS calculation with minimal stats and a known skill."""
        resp = client.post("/api/simulate/combat", json={
            "stats": {
                "base_damage": 100,
                "attack_speed": 1.0,
                "crit_chance": 0.05,
                "crit_multiplier": 1.5,
                "spell_damage_pct": 50,
                "cast_speed": 10,
            },
            "skill_name": "Fireball",
            "skill_level": 20,
            "n_simulations": 500,
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["dps"]["dps"] > 0
        assert data["dps"]["hit_damage"] > 0
        assert data["monte_carlo"]["mean_dps"] > 0
        assert data["monte_carlo"]["n_simulations"] == 500

    def test_unknown_skill(self, client):
        """Unknown skills should return 0 DPS, not an error."""
        resp = client.post("/api/simulate/combat", json={
            "stats": {"base_damage": 100},
            "skill_name": "NonexistentSkill",
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["dps"]["dps"] == 0

    def test_missing_skill_name(self, client):
        resp = client.post("/api/simulate/combat", json={
            "stats": {"base_damage": 100},
        })
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/simulate/defense
# ---------------------------------------------------------------------------

class TestSimulateDefense:
    def test_basic_defense(self, client):
        resp = client.post("/api/simulate/defense", json={
            "stats": {
                "max_health": 2000,
                "armour": 1000,
                "fire_res": 75,
                "cold_res": 75,
                "lightning_res": 75,
                "void_res": 50,
                "necrotic_res": 30,
                "dodge_rating": 200,
                "ward": 300,
                "ward_retention_pct": 10,
                "ward_regen": 20,
            },
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["effective_hp"] > 2000  # Should be amplified by resists/armour
        assert data["armor_reduction_pct"] == 50  # 1000/(1000+1000)
        assert data["survivability_score"] > 0
        assert data["dodge_chance_pct"] > 0
        assert isinstance(data["weaknesses"], list)
        assert isinstance(data["strengths"], list)

    def test_ward_sustainability(self, client):
        """Ward regen and decay should be reported."""
        resp = client.post("/api/simulate/defense", json={
            "stats": {
                "max_health": 1000,
                "ward": 500,
                "ward_retention_pct": 15,
                "ward_regen": 30,
            },
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["ward_decay_per_second"] >= 0
        assert data["ward_regen_per_second"] == 30.0

    def test_empty_stats(self, client):
        """Default stats should still return a valid result."""
        resp = client.post("/api/simulate/defense", json={"stats": {}})
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["survivability_score"] >= 0


# ---------------------------------------------------------------------------
# POST /api/simulate/optimize
# ---------------------------------------------------------------------------

class TestSimulateOptimize:
    def test_returns_upgrades(self, client):
        resp = client.post("/api/simulate/optimize", json={
            "stats": {
                "base_damage": 100,
                "attack_speed": 1.0,
                "crit_chance": 0.05,
                "crit_multiplier": 1.5,
                "spell_damage_pct": 30,
                "max_health": 2000,
                "armour": 500,
            },
            "skill_name": "Fireball",
            "top_n": 3,
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 3
        assert "stat" in data[0]
        assert "dps_gain_pct" in data[0]
        assert "ehp_gain_pct" in data[0]

    def test_top_n_defaults_to_5(self, client):
        resp = client.post("/api/simulate/optimize", json={
            "stats": {"base_damage": 100},
            "skill_name": "Fireball",
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 5


# ---------------------------------------------------------------------------
# POST /api/simulate/build
# ---------------------------------------------------------------------------

class TestSimulateBuild:
    def test_full_pipeline(self, client):
        """Full pipeline should return stats, dps, defense, and upgrades."""
        resp = client.post("/api/simulate/build", json={
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "skill_name": "Fireball",
            "skill_level": 20,
            "allocated_node_ids": [],
            "gear_affixes": [
                {"name": "Spell Damage", "tier": 4},
            ],
            "n_simulations": 500,
        })
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "stats" in data
        assert "dps" in data
        assert "monte_carlo" in data
        assert "defense" in data
        assert "stat_upgrades" in data
        assert data["primary_skill"] == "Fireball"
        assert data["dps"]["dps"] > 0

    def test_missing_required_fields(self, client):
        resp = client.post("/api/simulate/build", json={
            "character_class": "Mage",
            "mastery": "Sorcerer",
            # missing skill_name
        })
        assert resp.status_code == 422

    def test_mismatched_class_mastery(self, client):
        resp = client.post("/api/simulate/build", json={
            "character_class": "Rogue",
            "mastery": "Sorcerer",
            "skill_name": "Fireball",
        })
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Exception handling
# ---------------------------------------------------------------------------

class TestExceptionHandling:
    def test_forge_error_handler(self, client, db):
        """ItemFracturedError should be caught by global handler and return 400."""
        from app.models import CraftSession
        import secrets

        session = CraftSession(
            slug=secrets.token_urlsafe(8),
            item_type="Helmet",
            instability=50,
            forge_potential=20,
            affixes=[{"name": "Spell Damage", "tier": 2, "sealed": False}],
            is_fractured=True,
        )
        db.session.add(session)
        db.session.commit()

        resp = client.post(f"/api/craft/{session.slug}/action", json={
            "action": "upgrade_affix",
            "affix_name": "Spell Damage",
        })
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("fractured" in e["message"].lower() for e in errors)

    def test_insufficient_fp_error(self, client, db):
        """InsufficientForgePotentialError should return 400."""
        from app.models import CraftSession
        import secrets

        session = CraftSession(
            slug=secrets.token_urlsafe(8),
            item_type="Helmet",
            instability=0,
            forge_potential=0,  # No FP left
            affixes=[{"name": "Spell Damage", "tier": 2, "sealed": False}],
        )
        db.session.add(session)
        db.session.commit()

        resp = client.post(f"/api/craft/{session.slug}/action", json={
            "action": "upgrade_affix",
            "affix_name": "Spell Damage",
        })
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("forge potential" in e["message"].lower() for e in errors)
