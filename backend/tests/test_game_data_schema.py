"""J1 — Tests for game_data_schema.py"""

import pytest
from marshmallow import ValidationError

from data.schemas.game_data_schema import (
    SkillSchema,
    ItemSchema,
    AffixSchema,
    PassiveNodeSchema,
    EnemySchema,
)


class TestSkillSchema:
    def test_valid_skill(self):
        data = {"skill_id": "fireball", "base_damage": 100.0, "cooldown": 1.5, "mana_cost": 20.0}
        result = SkillSchema().load(data)
        assert result["skill_id"] == "fireball"
        assert result["tags"] == []

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError) as exc:
            SkillSchema().load({"skill_id": "x", "cooldown": 1.0, "mana_cost": 5.0})
        assert "base_damage" in exc.value.messages

    def test_negative_base_damage_rejected(self):
        with pytest.raises(ValidationError):
            SkillSchema().load({"skill_id": "x", "base_damage": -1, "cooldown": 0, "mana_cost": 0})


class TestItemSchema:
    def test_valid_item(self):
        data = {"item_id": "iron_helm", "slot_type": "helm"}
        result = ItemSchema().load(data)
        assert result["item_id"] == "iron_helm"
        assert result["implicit_stats"] == {}

    def test_missing_slot_type_raises(self):
        with pytest.raises(ValidationError) as exc:
            ItemSchema().load({"item_id": "x"})
        assert "slot_type" in exc.value.messages


class TestAffixSchema:
    def test_valid_affix(self):
        data = {"affix_id": "fire_res", "stat_type": "fire_resistance", "min_value": 10.0, "max_value": 20.0}
        result = AffixSchema().load(data)
        assert result["affix_id"] == "fire_res"

    def test_min_greater_than_max_raises(self):
        with pytest.raises(ValidationError):
            AffixSchema().load({"affix_id": "x", "stat_type": "s", "min_value": 50.0, "max_value": 10.0})

    def test_missing_affix_id_raises(self):
        with pytest.raises(ValidationError) as exc:
            AffixSchema().load({"stat_type": "s", "min_value": 1.0, "max_value": 5.0})
        assert "affix_id" in exc.value.messages


class TestPassiveNodeSchema:
    def test_valid_node(self):
        data = {"node_id": "n1", "stat_modifiers": {"strength": 5.0}, "dependencies": ["n0"]}
        result = PassiveNodeSchema().load(data)
        assert result["node_id"] == "n1"

    def test_missing_node_id_raises(self):
        with pytest.raises(ValidationError) as exc:
            PassiveNodeSchema().load({"stat_modifiers": {}})
        assert "node_id" in exc.value.messages


class TestEnemySchema:
    def test_valid_enemy(self):
        data = {"enemy_id": "goblin", "max_health": 500.0, "armor": 20.0}
        result = EnemySchema().load(data)
        assert result["resistances"] == {}

    def test_zero_max_health_rejected(self):
        with pytest.raises(ValidationError):
            EnemySchema().load({"enemy_id": "x", "max_health": 0, "armor": 0})

    def test_missing_enemy_id_raises(self):
        with pytest.raises(ValidationError) as exc:
            EnemySchema().load({"max_health": 100, "armor": 0})
        assert "enemy_id" in exc.value.messages
