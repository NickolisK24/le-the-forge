"""J9 — Tests for data_mapper.py"""

import pytest
from data.mappers.data_mapper import DataMapper


class TestMappingCorrectness:
    def test_skill_from_raw(self):
        raw = {"base_damage": 120.0, "attack_speed": 1.2, "tags": ["spell", "fire"]}
        skill = DataMapper.skill_from_raw("fireball", raw)
        assert skill.skill_id == "fireball"
        assert skill.base_damage == 120.0
        assert "spell" in skill.tags

    def test_enemy_from_raw(self):
        raw = {"id": "wolf", "health": 250, "armor": 15, "resistances": {"physical": 10}}
        enemy = DataMapper.enemy_from_raw(raw)
        assert enemy.enemy_id == "wolf"
        assert enemy.max_health == 250
        assert enemy.resistance("physical") == 10

    def test_affix_from_raw_multi_tier(self):
        raw = {
            "id": "fire_res",
            "stat_key": "fire_resistance",
            "tiers": [{"tier": 1, "min": 10, "max": 20}, {"tier": 2, "min": 21, "max": 35}],
        }
        models = DataMapper.affix_from_raw(raw)
        assert len(models) == 2
        assert models[0].affix_id == "fire_res_t1"
        assert models[1].affix_id == "fire_res_t2"

    def test_passive_from_raw_list_stats(self):
        raw = {"id": "strength_node", "stats": ["strength +5", "health +20"], "connections": ["root"]}
        node = DataMapper.passive_from_raw(raw)
        assert node.node_id == "strength_node"
        assert len(node.stat_modifiers) == 2


class TestReferenceResolution:
    def test_skills_from_bundle(self):
        bundle = {
            "skills": {
                "fireball": {"base_damage": 100, "cooldown": 1.5, "mana_cost": 20},
                "ice_bolt":  {"base_damage": 80,  "cooldown": 1.0, "mana_cost": 15},
            }
        }
        skills = DataMapper.skills_from_bundle(bundle)
        assert len(skills) == 2
        ids = {s.skill_id for s in skills}
        assert "fireball" in ids

    def test_enemies_from_real_data(self):
        from data.loaders.raw_data_loader import RawDataLoader
        loader = RawDataLoader()
        bundle = loader.load("entities/enemy_profiles.json")
        enemies = DataMapper.enemies_from_bundle(bundle)
        assert len(enemies) > 0
        assert all(e.max_health > 0 for e in enemies)
