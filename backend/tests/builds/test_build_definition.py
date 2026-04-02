"""
E1 — Tests for BuildDefinition object.
"""

import pytest
from builds.build_definition import BuildDefinition, BuildMetadata
from builds.gear_system      import GearItem, GearAffix
from builds.buff_system      import Buff
from builds.passive_system   import PassiveNode


def _make_build(**kwargs) -> BuildDefinition:
    defaults = dict(character_class="Acolyte", mastery="Lich")
    return BuildDefinition(**{**defaults, **kwargs})


class TestBuildDefinitionCreation:
    def test_create_minimal(self):
        b = _make_build()
        assert b.character_class == "Acolyte"
        assert b.mastery == "Lich"
        assert b.skill_id == "Rip Blood"
        assert b.skill_level == 20
        assert b.gear == []
        assert b.passive_ids == []
        assert b.buffs == []

    def test_default_metadata(self):
        b = _make_build()
        assert b.metadata.name == "Untitled Build"
        assert b.metadata.version == "1.0"

    def test_custom_skill(self):
        b = _make_build(skill_id="Hungering Souls", skill_level=15)
        assert b.skill_id == "Hungering Souls"
        assert b.skill_level == 15


class TestGearHelpers:
    def test_add_gear(self):
        b = _make_build()
        item = GearItem(slot="weapon", affixes=[GearAffix("Spell Damage", 3)])
        b.add_gear(item)
        assert len(b.gear) == 1
        assert b.get_gear("weapon") is item

    def test_add_gear_replaces_same_slot(self):
        b = _make_build()
        b.add_gear(GearItem(slot="weapon", affixes=[GearAffix("Spell Damage", 1)]))
        b.add_gear(GearItem(slot="weapon", affixes=[GearAffix("Fire Damage", 2)]))
        assert len(b.gear) == 1
        assert b.get_gear("weapon").affixes[0].name == "Fire Damage"

    def test_remove_gear(self):
        b = _make_build()
        item = GearItem(slot="head")
        b.add_gear(item)
        removed = b.remove_gear("head")
        assert removed is item
        assert len(b.gear) == 0

    def test_remove_gear_missing_slot_returns_none(self):
        b = _make_build()
        assert b.remove_gear("weapon") is None

    def test_multiple_gear_slots(self):
        b = _make_build()
        b.add_gear(GearItem(slot="weapon"))
        b.add_gear(GearItem(slot="head"))
        b.add_gear(GearItem(slot="ring_1"))
        assert len(b.gear) == 3

    def test_all_gear_affixes_flattened(self):
        b = _make_build()
        b.add_gear(GearItem(slot="weapon", affixes=[GearAffix("Spell Damage", 3), GearAffix("Fire Damage", 2)]))
        b.add_gear(GearItem(slot="head",   affixes=[GearAffix("Health", 1)]))
        affixes = b.all_gear_affixes()
        assert len(affixes) == 3
        assert {"name": "Spell Damage", "tier": 3} in affixes
        assert {"name": "Health", "tier": 1} in affixes


class TestPassiveHelpers:
    def test_add_passive(self):
        b = _make_build()
        b.add_passive(101)
        b.add_passive(202)
        assert 101 in b.passive_ids
        assert 202 in b.passive_ids

    def test_add_passive_no_duplicates(self):
        b = _make_build()
        b.add_passive(101)
        b.add_passive(101)
        assert b.passive_ids.count(101) == 1

    def test_remove_passive(self):
        b = _make_build()
        b.add_passive(101)
        b.remove_passive(101)
        assert 101 not in b.passive_ids

    def test_remove_passive_not_in_list_is_safe(self):
        b = _make_build()
        b.remove_passive(999)  # should not raise


class TestBuffHelpers:
    def test_add_buff(self):
        b = _make_build()
        buff = Buff("frenzy", {"spell_damage_pct": 30.0})
        b.add_buff(buff)
        assert len(b.buffs) == 1

    def test_add_buff_replaces_same_id(self):
        b = _make_build()
        b.add_buff(Buff("frenzy", {"spell_damage_pct": 10.0}))
        b.add_buff(Buff("frenzy", {"spell_damage_pct": 30.0}))
        assert len(b.buffs) == 1
        assert b.buffs[0].modifiers["spell_damage_pct"] == 30.0

    def test_remove_buff(self):
        b = _make_build()
        b.add_buff(Buff("frenzy", {}))
        b.remove_buff("frenzy")
        assert b.buffs == []

    def test_remove_buff_missing_is_safe(self):
        b = _make_build()
        b.remove_buff("nonexistent")  # should not raise


class TestSerializationSafety:
    def test_to_dict_contains_required_keys(self):
        b = _make_build()
        d = b.to_dict()
        for key in ("character_class", "mastery", "skill_id", "skill_level",
                    "gear", "passive_ids", "buffs", "metadata"):
            assert key in d

    def test_from_dict_roundtrip(self):
        b = _make_build(
            skill_id="Bone Curse",
            gear=[GearItem("weapon", [GearAffix("Spell Damage", 3)])],
            passive_ids=[1, 5, 10],
        )
        b.add_buff(Buff("power", {"base_damage": 50.0}))
        d = b.to_dict()
        b2 = BuildDefinition.from_dict(d)
        assert b2.character_class == b.character_class
        assert b2.skill_id == b.skill_id
        assert len(b2.gear) == 1
        assert b2.gear[0].affixes[0].name == "Spell Damage"
        assert b2.passive_ids == [1, 5, 10]
        assert b2.buffs[0].buff_id == "power"
