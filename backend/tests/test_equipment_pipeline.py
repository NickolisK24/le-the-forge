"""
Integration tests for the equipment → stat pipeline.

Tests the end-to-end flow:
  Item.apply_to_stat_pool()  →  EquipmentSet  →  BuildState.recompute()

All tests use mock affixes with direct stat_key/value — no DB, no Flask
context required.  The stat_engine game_data_loader uses module-level
fallbacks so aggregate_stats works outside Flask.
"""

import pytest

from app.domain.item import Affix, Item
from app.domain.equipment_set import EquipmentSet, VALID_EQUIPMENT_SLOTS
from app.engines.stat_engine import StatPool, create_empty_stat_pool


# ---------------------------------------------------------------------------
# Fixtures — reusable mock items
# ---------------------------------------------------------------------------

def _make_affix(name: str, stat_key: str, value: float, tier: int = 3) -> Affix:
    return Affix(name=name, stat_key=stat_key, value=value, tier=tier)


def _make_item(slot: str, name: str, affixes: list[Affix], implicits: dict | None = None) -> Item:
    return Item(
        slot=slot,
        item_name=name,
        rarity="Rare",
        affixes=affixes,
        implicit_stats=implicits or {},
    )


# ---------------------------------------------------------------------------
# Item → StatPool
# ---------------------------------------------------------------------------

class TestItemApplyToStatPool:
    def test_flat_affix_goes_to_flat_bucket(self):
        item = _make_item("head", "Iron Helm", [
            _make_affix("health", "max_health", 40.0),
        ])
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        assert pool.flat["max_health"] == 40.0

    def test_pct_affix_goes_to_increased_bucket(self):
        item = _make_item("body", "Robe", [
            _make_affix("spell_dmg", "spell_damage_pct", 25.0),
        ])
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        assert pool.increased["spell_damage_pct"] == 25.0

    def test_more_affix_goes_to_more_bucket(self):
        item = _make_item("weapon", "Staff", [
            _make_affix("more_dmg", "more_damage_multiplier", 15.0),
        ])
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        # more bucket compounds: 1.0 * (1 + 15/100) = 1.15
        assert abs(pool.more["more_damage_multiplier"] - 1.15) < 1e-9

    def test_multiple_affixes_accumulate(self):
        item = _make_item("body", "Plate", [
            _make_affix("health", "max_health", 40.0),
            _make_affix("armor", "armour", 100.0),
            _make_affix("fire", "fire_res", 20.0),
        ])
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        assert pool.flat["max_health"] == 40.0
        assert pool.flat["armour"] == 100.0
        assert pool.flat["fire_res"] == 20.0

    def test_implicit_stats_emitted(self):
        item = _make_item("weapon", "Sword", [], implicits={"base_damage": 15.0})
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        assert pool.flat["base_damage"] == 15.0

    def test_zero_value_affix_skipped(self):
        item = _make_item("head", "Helm", [
            _make_affix("empty", "max_health", 0.0),
        ])
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        assert "max_health" not in pool.flat

    def test_sealed_affix_still_applied(self):
        affix = Affix(name="sealed_fire", stat_key="fire_res", value=15.0, tier=5, sealed=True)
        item = _make_item("hands", "Gloves", [affix])
        pool = create_empty_stat_pool()
        item.apply_to_stat_pool(pool)
        assert pool.flat["fire_res"] == 15.0

    def test_from_dict_preserves_implicit_stats(self):
        d = {
            "slot": "weapon",
            "item_name": "Sword",
            "rarity": "Rare",
            "affixes": [],
            "implicit_stats": {"base_damage": 10.0},
        }
        item = Item.from_dict(d)
        assert item.implicit_stats == {"base_damage": 10.0}


# ---------------------------------------------------------------------------
# EquipmentSet → StatPool
# ---------------------------------------------------------------------------

class TestEquipmentSetStatPool:
    def test_multi_item_aggregation(self):
        helm = _make_item("head", "Iron Helm", [
            _make_affix("health", "max_health", 40.0),
        ])
        body = _make_item("body", "Plate", [
            _make_affix("armor", "armour", 100.0),
        ])
        gear = EquipmentSet()
        gear.equip_item(helm)
        gear.equip_item(body)

        pool = create_empty_stat_pool()
        gear.apply_to_stat_pool(pool)
        assert pool.flat["max_health"] == 40.0
        assert pool.flat["armour"] == 100.0

    def test_equip_replaces_existing(self):
        helm1 = _make_item("head", "Old Helm", [_make_affix("h", "max_health", 20.0)])
        helm2 = _make_item("head", "New Helm", [_make_affix("h", "max_health", 60.0)])
        gear = EquipmentSet()
        old = gear.equip_item(helm1)
        assert old is None
        old = gear.equip_item(helm2)
        assert old is not None
        assert old.item_name == "Old Helm"

        pool = create_empty_stat_pool()
        gear.apply_to_stat_pool(pool)
        assert pool.flat["max_health"] == 60.0  # only new helm

    def test_unequip_removes_item(self):
        helm = _make_item("head", "Helm", [_make_affix("h", "max_health", 40.0)])
        gear = EquipmentSet()
        gear.equip_item(helm)
        removed = gear.unequip("head")
        assert removed is not None
        assert len(gear) == 0

    def test_invalid_slot_raises(self):
        item = Item(slot="invalid_slot", item_name="Bad", rarity="Normal")
        gear = EquipmentSet()
        with pytest.raises(ValueError, match="not a valid equipment slot"):
            gear.equip_item(item)

    def test_empty_slot_raises(self):
        item = Item(slot="", item_name="Bad", rarity="Normal")
        gear = EquipmentSet()
        with pytest.raises(ValueError, match="no slot defined"):
            gear.equip_item(item)

    def test_from_item_list(self):
        items = [
            _make_item("head", "Helm", [_make_affix("h", "max_health", 30.0)]),
            _make_item("body", "Plate", [_make_affix("a", "armour", 50.0)]),
        ]
        gear = EquipmentSet.from_item_list(items)
        assert len(gear) == 2
        assert gear.get_item("head") is not None

    def test_list_items_deterministic(self):
        gear = EquipmentSet()
        gear.equip_item(_make_item("body", "B", []))
        gear.equip_item(_make_item("head", "H", []))
        items = gear.list_items()
        assert [i.slot for i in items] == ["body", "head"]

    def test_serialization_roundtrip(self):
        gear = EquipmentSet()
        gear.equip_item(_make_item("head", "Helm", [
            _make_affix("h", "max_health", 40.0),
        ], implicits={"armour": 10.0}))
        d = gear.to_dict()
        gear2 = EquipmentSet.from_dict(d)
        assert len(gear2) == 1
        assert gear2.get_item("head").item_name == "Helm"
        assert gear2.get_item("head").implicit_stats["armour"] == 10.0


# ---------------------------------------------------------------------------
# BuildState.recompute()
# ---------------------------------------------------------------------------

class TestBuildStateRecompute:
    def test_basic_recompute(self):
        from app.domain.build_state import BuildState

        helm = _make_item("head", "Iron Helm", [
            _make_affix("health", "max_health", 40.0),
        ])
        gear = EquipmentSet()
        gear.equip_item(helm)

        state = BuildState(
            character_class="Sentinel",
            mastery="",
            equipment=gear,
        )
        stats = state.recompute()
        assert stats is not None
        # Sentinel base health + affix + attribute scaling
        assert stats.max_health > 40.0
        assert state.resolved_stats is stats

    def test_recompute_with_buffs(self):
        from app.domain.build_state import BuildState
        from builds.buff_system import Buff

        gear = EquipmentSet()
        gear.equip_item(_make_item("head", "Helm", [
            _make_affix("h", "max_health", 20.0),
        ]))
        state = BuildState(
            character_class="Mage",
            mastery="Sorcerer",
            equipment=gear,
        )
        state.add_buff(Buff(buff_id="ward_buff", modifiers={"ward": 50.0}))
        stats = state.recompute()
        assert stats.ward >= 50.0

    def test_mutation_invalidates_cache(self):
        from app.domain.build_state import BuildState

        state = BuildState(character_class="Sentinel")
        state.recompute()
        assert state.resolved_stats is not None

        state.equip_item(_make_item("head", "Helm", []))
        assert state.resolved_stats is None  # invalidated

    def test_pool_snapshot_captured(self):
        from app.domain.build_state import BuildState

        gear = EquipmentSet()
        gear.equip_item(_make_item("head", "Helm", [
            _make_affix("h", "max_health", 30.0),
        ]))
        state = BuildState(character_class="Sentinel", equipment=gear)
        state.recompute(capture_pool=True)
        assert state.last_pool_snapshot is not None
        assert "flat" in state.last_pool_snapshot

    def test_serialization_roundtrip(self):
        from app.domain.build_state import BuildState

        gear = EquipmentSet()
        gear.equip_item(_make_item("head", "Helm", [
            _make_affix("h", "max_health", 30.0),
        ]))
        state = BuildState(
            character_class="Mage",
            mastery="Sorcerer",
            equipment=gear,
            passive_node_ids={1, 5},
        )
        state.recompute()
        d = state.to_dict()
        state2 = BuildState.from_dict(d)
        assert state2.character_class == "Mage"
        assert state2.mastery == "Sorcerer"
        assert len(state2.equipment) == 1
        assert state2.passive_node_ids == {1, 5}
