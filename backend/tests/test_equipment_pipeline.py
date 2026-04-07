"""
Integration tests for the equipment + passive → stat pipeline.

Tests the end-to-end flow:
  Item.apply_to_stat_pool()  →  EquipmentSet  →  BuildState.recompute()
  PassiveSystem.apply_to_stat_pool()  →  BuildState.recompute()

All tests use mock affixes with direct stat_key/value — no DB, no Flask
context required.  The stat_engine game_data_loader uses module-level
fallbacks so aggregate_stats works outside Flask.
"""

import pytest

from app.domain.item import Affix, Item
from app.domain.equipment_set import EquipmentSet, VALID_EQUIPMENT_SLOTS
from app.engines.stat_engine import StatPool, create_empty_stat_pool
from builds.passive_system import PassiveNode, PassiveSystem


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


# ---------------------------------------------------------------------------
# PassiveSystem → StatPool
# ---------------------------------------------------------------------------

def _make_passive_system(*nodes: PassiveNode, allocate_ids: list[int] | None = None) -> PassiveSystem:
    """Helper to create a PassiveSystem with registered and allocated nodes."""
    ps = PassiveSystem(list(nodes))
    for nid in (allocate_ids or []):
        ps.allocate(nid)
    return ps


class TestPassiveSystemStatPool:
    def test_minor_node_emits_flat_stat(self):
        """Minor node 0 → CORE_STAT_CYCLE[0] = ("max_health", 8)."""
        node = PassiveNode(node_id=0, name="Vitality I", node_type="minor")
        ps = _make_passive_system(node, allocate_ids=[0])
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat.get("max_health", 0) == 8.0

    def test_notable_node_emits_3x_stat(self):
        """Notable node 0 → ("max_health", 8 * 3 = 24)."""
        node = PassiveNode(node_id=0, name="Vitality II", node_type="notable")
        ps = _make_passive_system(node, allocate_ids=[0])
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat.get("max_health", 0) == 24.0

    def test_keystone_emits_known_bonus(self):
        """Keystone 'Juggernaut' → armour=200, max_health=100."""
        node = PassiveNode(node_id=99, name="Juggernaut", node_type="keystone")
        ps = _make_passive_system(node, allocate_ids=[99])
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat.get("armour", 0) == 200.0
        assert pool.flat.get("max_health", 0) == 100.0

    def test_pct_stat_routes_to_increased_bucket(self):
        """Minor node 1 → CORE_STAT_CYCLE[1] = ("spell_damage_pct", 1)."""
        node = PassiveNode(node_id=1, name="Arcane I", node_type="minor")
        ps = _make_passive_system(node, allocate_ids=[1])
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.increased.get("spell_damage_pct", 0) == 1.0

    def test_unallocated_node_not_emitted(self):
        """Only allocated nodes contribute stats."""
        node = PassiveNode(node_id=0, name="Vit", node_type="minor")
        ps = PassiveSystem([node])  # registered but NOT allocated
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat == {}

    def test_unregistered_allocated_node_skipped(self):
        """Allocated nodes without registry metadata are silently skipped."""
        ps = PassiveSystem()
        ps.allocate(42)  # allowed for unknown nodes
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat == {}

    def test_mastery_gate_emits_nothing(self):
        node = PassiveNode(node_id=50, name="Gate", node_type="mastery-gate")
        ps = _make_passive_system(node, allocate_ids=[50])
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat == {}
        assert pool.increased == {}

    def test_multiple_nodes_accumulate(self):
        """Two minor nodes with same stat_key should sum."""
        # node_id=0 and node_id=10 both → max_health (0 % 10 == 10 % 10 == 0)
        n0 = PassiveNode(node_id=0, name="Vit I", node_type="minor")
        n10 = PassiveNode(node_id=10, name="Vit II", node_type="minor")
        ps = _make_passive_system(n0, n10, allocate_ids=[0, 10])
        pool = create_empty_stat_pool()
        ps.apply_to_stat_pool(pool)
        assert pool.flat.get("max_health", 0) == 16.0  # 8 + 8


# ---------------------------------------------------------------------------
# BuildState.recompute() with PassiveSystem
# ---------------------------------------------------------------------------

class TestBuildStatePassiveIntegration:
    def test_passives_change_final_stats(self):
        """Allocating passives should produce different BuildStats than without."""
        from app.domain.build_state import BuildState

        # Baseline — no passives
        state_no_passives = BuildState(character_class="Sentinel")
        stats_base = state_no_passives.recompute()

        # With passives — 3 minor health nodes (ids 0, 10, 20 all → max_health)
        nodes = [
            PassiveNode(node_id=0, name="V1", node_type="minor"),
            PassiveNode(node_id=10, name="V2", node_type="minor"),
            PassiveNode(node_id=20, name="V3", node_type="minor"),
        ]
        ps = _make_passive_system(*nodes, allocate_ids=[0, 10, 20])
        state_with_passives = BuildState(
            character_class="Sentinel",
            passive_node_ids={0, 10, 20},
            passive_system=ps,
        )
        stats_passive = state_with_passives.recompute()

        # Passives should increase max_health
        assert stats_passive.max_health > stats_base.max_health

    def test_keystone_changes_stats(self):
        """Keystone 'Juggernaut' should add 200 armour + 100 health."""
        from app.domain.build_state import BuildState

        state_base = BuildState(character_class="Sentinel")
        base_stats = state_base.recompute()

        node = PassiveNode(node_id=99, name="Juggernaut", node_type="keystone")
        ps = _make_passive_system(node, allocate_ids=[99])
        state = BuildState(
            character_class="Sentinel",
            passive_node_ids={99},
            passive_system=ps,
        )
        stats = state.recompute()

        assert stats.armour > base_stats.armour
        assert stats.max_health > base_stats.max_health

    def test_passive_pool_snapshot_includes_passives(self):
        """Pool snapshot should contain passive contributions."""
        from app.domain.build_state import BuildState

        node = PassiveNode(node_id=0, name="Vit", node_type="minor")
        ps = _make_passive_system(node, allocate_ids=[0])
        state = BuildState(
            character_class="Sentinel",
            passive_node_ids={0},
            passive_system=ps,
        )
        state.recompute(capture_pool=True)
        snapshot = state.last_pool_snapshot
        assert snapshot is not None
        # node 0 → max_health flat
        assert snapshot["flat"].get("max_health", 0) >= 8.0

    def test_equipment_and_passives_combined(self):
        """Both equipment and passives should contribute to final stats."""
        from app.domain.build_state import BuildState

        helm = _make_item("head", "Helm", [_make_affix("h", "armour", 50.0)])
        gear = EquipmentSet()
        gear.equip_item(helm)

        # Juggernaut adds 200 armour
        node = PassiveNode(node_id=99, name="Juggernaut", node_type="keystone")
        ps = _make_passive_system(node, allocate_ids=[99])

        state = BuildState(
            character_class="Sentinel",
            equipment=gear,
            passive_node_ids={99},
            passive_system=ps,
        )
        stats = state.recompute()

        # Should have both gear armour (50) and keystone armour (200) plus base
        base_state = BuildState(character_class="Sentinel")
        base_armour = base_state.recompute().armour
        assert stats.armour >= base_armour + 50 + 200

    def test_serialization_preserves_passive_system(self):
        """Roundtrip should preserve passive system and node allocations."""
        from app.domain.build_state import BuildState

        nodes = [
            PassiveNode(node_id=0, name="V1", node_type="minor"),
            PassiveNode(node_id=1, name="A1", node_type="minor"),
        ]
        ps = _make_passive_system(*nodes, allocate_ids=[0, 1])
        state = BuildState(
            character_class="Mage",
            passive_node_ids={0, 1},
            passive_system=ps,
        )
        state.recompute()

        d = state.to_dict()
        state2 = BuildState.from_dict(d)
        assert state2.passive_system is not None
        assert set(state2.passive_system.get_allocated_ids()) == {0, 1}

        # Recompute from deserialized state should produce same health
        stats2 = state2.recompute()
        assert stats2.max_health == state.resolved_stats.max_health
