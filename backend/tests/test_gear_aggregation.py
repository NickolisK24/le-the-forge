"""
Tests for gear_aggregator (Step 89).

Validates stat aggregation from equipped gear items.
"""

import pytest

from app.domain.item import Affix, Item
from build.gear_aggregator import aggregate_gear


def _item(slot: str, **stat_values) -> Item:
    """Build a test Item with one Affix per stat_key=value pair."""
    affixes = [
        Affix(name=k, stat_key=k, value=v)
        for k, v in stat_values.items()
    ]
    return Item(slot=slot, item_name=f"Test {slot}", rarity="Magic", affixes=affixes)


class TestAggregateGear:
    def test_empty_list_returns_empty_dict(self):
        assert aggregate_gear([]) == {}

    def test_single_item_no_affixes(self):
        item = Item(slot="head", item_name="Helm", rarity="Normal", affixes=[])
        assert aggregate_gear([item]) == {}

    def test_single_item_single_affix(self):
        item = _item("amulet", fire_damage_pct=12.0)
        result = aggregate_gear([item])
        assert result == {"fire_damage_pct": 12.0}

    def test_single_item_multiple_affixes(self):
        item = _item("ring", fire_damage_pct=10.0, crit_chance_pct=5.0)
        result = aggregate_gear([item])
        assert result["fire_damage_pct"] == pytest.approx(10.0)
        assert result["crit_chance_pct"] == pytest.approx(5.0)

    def test_multiple_items_different_stats_merged(self):
        items = [
            _item("amulet", fire_damage_pct=12.0),
            _item("ring",   cold_damage_pct=8.0),
        ]
        result = aggregate_gear(items)
        assert result == {"fire_damage_pct": 12.0, "cold_damage_pct": 8.0}

    def test_duplicate_stat_key_stacks_additively(self):
        items = [
            _item("amulet", fire_damage_pct=12.0),
            _item("ring",   fire_damage_pct=8.0),
        ]
        result = aggregate_gear(items)
        assert result["fire_damage_pct"] == pytest.approx(20.0)

    def test_multiple_items_mixed_overlap(self):
        items = [
            _item("amulet", fire_damage_pct=10.0, spell_damage_pct=5.0),
            _item("ring",   fire_damage_pct=8.0,  crit_chance_pct=3.0),
            _item("gloves", spell_damage_pct=7.0),
        ]
        result = aggregate_gear(items)
        assert result["fire_damage_pct"]  == pytest.approx(18.0)
        assert result["spell_damage_pct"] == pytest.approx(12.0)
        assert result["crit_chance_pct"]  == pytest.approx(3.0)

    def test_negative_affix_value_accepted(self):
        items = [
            _item("boots", movement_speed_pct=10.0),
            _item("chest", movement_speed_pct=-5.0),   # downside affix
        ]
        result = aggregate_gear(items)
        assert result["movement_speed_pct"] == pytest.approx(5.0)

    def test_sealed_affix_included(self):
        affix = Affix(name="Sealed Fire", stat_key="fire_damage_pct", value=15.0, sealed=True)
        item  = Item(slot="ring", item_name="Sealed Ring", rarity="Exalted", affixes=[affix])
        result = aggregate_gear([item])
        assert result["fire_damage_pct"] == pytest.approx(15.0)

    def test_zero_value_affix_included(self):
        item = _item("helm", armor_flat=0.0)
        result = aggregate_gear([item])
        assert "armor_flat" in result
        assert result["armor_flat"] == pytest.approx(0.0)

    def test_many_items_correct_total(self):
        items = [_item(f"slot{i}", fire_damage_pct=2.0) for i in range(50)]
        result = aggregate_gear(items)
        assert result["fire_damage_pct"] == pytest.approx(100.0)

    def test_original_items_not_mutated(self):
        affix = Affix(name="Fire", stat_key="fire_damage_pct", value=10.0)
        item  = Item(slot="ring", item_name="Ring", rarity="Magic", affixes=[affix])
        aggregate_gear([item])
        assert item.affixes[0].value == pytest.approx(10.0)
