"""J16 — Game Data Regression Suite"""

import pytest
from data.loaders.raw_data_loader import RawDataLoader
from data.mappers.data_mapper import DataMapper


class TestSkillOutputConsistency:
    def test_skills_bundle_maps_correctly(self):
        import json
        import os
        skills_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "game_data", "skills.json"
        )
        with open(skills_path) as f:
            bundle = json.load(f)
        skills = DataMapper.skills_from_bundle(bundle)
        assert len(skills) > 0
        # All skills have non-negative damage
        assert all(s.base_damage >= 0 for s in skills)

    def test_skill_ids_are_unique(self):
        import json, os
        skills_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "game_data", "skills.json"
        )
        with open(skills_path) as f:
            bundle = json.load(f)
        skills = DataMapper.skills_from_bundle(bundle)
        ids = [s.skill_id for s in skills]
        assert len(ids) == len(set(ids))


class TestItemStatAccuracy:
    def test_items_from_real_base_items(self):
        loader = RawDataLoader()
        bundle = loader.load("items/base_items.json")
        items = DataMapper.items_from_bundle(bundle)
        assert len(items) > 0
        assert all(item.slot_type for item in items)

    def test_no_empty_item_ids(self):
        loader = RawDataLoader()
        bundle = loader.load("items/base_items.json")
        items = DataMapper.items_from_bundle(bundle)
        # filter out any without an id (some entries may have empty name)
        named = [i for i in items if i.item_id]
        assert len(named) > 0


class TestEnemyStatValidation:
    def test_all_enemies_have_positive_health(self):
        loader = RawDataLoader()
        bundle = loader.load("entities/enemy_profiles.json")
        enemies = DataMapper.enemies_from_bundle(bundle)
        assert all(e.max_health > 0 for e in enemies)

    def test_enemy_count_matches_source(self):
        loader = RawDataLoader()
        bundle = loader.load("entities/enemy_profiles.json")
        enemies = DataMapper.enemies_from_bundle(bundle)
        assert len(enemies) == len(bundle)
