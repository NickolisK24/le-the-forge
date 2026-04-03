"""J5 — Tests for item_model.py"""

import pytest
from data.models.item_model import ItemModel


class TestItemCreation:
    def test_basic_creation(self):
        item = ItemModel(item_id="iron_helm", slot_type="helm")
        assert item.item_id == "iron_helm"
        assert item.slot_type == "helm"
        assert item.implicit_stats == {}

    def test_implicit_stats_stored(self):
        item = ItemModel("sword_1", "sword", implicit_stats={"crit_chance": 5.0})
        assert item.implicit_stats["crit_chance"] == 5.0

    def test_explicit_affixes_tuple(self):
        item = ItemModel("x", "helm", explicit_affixes=["fire_res", "cold_res"])
        assert isinstance(item.explicit_affixes, tuple)
        assert "fire_res" in item.explicit_affixes


class TestSlotValidation:
    def test_empty_item_id_raises(self):
        with pytest.raises(ValueError, match="item_id"):
            ItemModel(item_id="", slot_type="helm")

    def test_empty_slot_type_raises(self):
        with pytest.raises(ValueError, match="slot_type"):
            ItemModel(item_id="x", slot_type="")

    def test_is_weapon_sword(self):
        item = ItemModel("big_sword", "sword")
        assert item.is_weapon() is True

    def test_is_weapon_helm_false(self):
        item = ItemModel("helm_1", "helm")
        assert item.is_weapon() is False

    def test_to_dict(self):
        item = ItemModel("i1", "chest", implicit_stats={"armor": 100})
        d = item.to_dict()
        assert d["item_id"] == "i1"
        assert d["slot_type"] == "chest"
