"""
E4 — Tests for GearSystem.
"""

import pytest
from builds.gear_system import GearItem, GearAffix, VALID_SLOTS


class TestGearAffix:
    def test_creates_correctly(self):
        a = GearAffix("Spell Damage", 3)
        assert a.name == "Spell Damage"
        assert a.tier == 3

    def test_to_dict(self):
        a = GearAffix("Fire Damage", 2)
        assert a.to_dict() == {"name": "Fire Damage", "tier": 2}


class TestGearItem:
    def test_valid_slot_accepted(self):
        for slot in VALID_SLOTS:
            item = GearItem(slot=slot)
            assert item.slot == slot

    def test_invalid_slot_raises(self):
        with pytest.raises(ValueError, match="Invalid slot"):
            GearItem(slot="invalid_slot")

    def test_invalid_rarity_raises(self):
        with pytest.raises(ValueError, match="Invalid rarity"):
            GearItem(slot="weapon", rarity="legendary")

    def test_add_affix(self):
        item = GearItem(slot="weapon")
        item.add_affix(GearAffix("Spell Damage", 3))
        assert len(item.affixes) == 1

    def test_to_affix_dicts(self):
        item = GearItem(slot="head", affixes=[
            GearAffix("Health", 2),
            GearAffix("Fire Damage", 1),
        ])
        dicts = item.to_affix_dicts()
        assert dicts == [
            {"name": "Health",      "tier": 2},
            {"name": "Fire Damage", "tier": 1},
        ]

    def test_empty_gear_safe(self):
        item = GearItem(slot="body")
        assert item.to_affix_dicts() == []
        assert item.to_dict()["affixes"] == []

    def test_slot_conflicts_prevented_via_build(self):
        from builds.build_definition import BuildDefinition
        b = BuildDefinition(character_class="Mage", mastery="Sorcerer")
        b.add_gear(GearItem(slot="weapon", affixes=[GearAffix("Increased Spell Damage", 1)]))
        b.add_gear(GearItem(slot="weapon", affixes=[GearAffix("Increased Cold Damage", 2)]))
        # Only the second weapon should remain
        assert len(b.gear) == 1
        assert b.gear[0].affixes[0].name == "Increased Cold Damage"

    def test_from_dict_roundtrip(self):
        item = GearItem(slot="ring_1", affixes=[GearAffix("Lightning Damage", 3)], rarity="rare")
        item2 = GearItem.from_dict(item.to_dict())
        assert item2.slot == "ring_1"
        assert item2.rarity == "rare"
        assert item2.affixes[0].name == "Lightning Damage"
        assert item2.affixes[0].tier == 3
