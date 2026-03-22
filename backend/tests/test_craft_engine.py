"""
Craft Engine Tests — validates crafting actions.

Run standalone (no Flask needed):
  python3 -m pytest backend/tests/test_craft_engine.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.engines.craft_engine import add_affix, upgrade_affix, remove_affix, seal_affix, unseal_affix, fracture_item


def _make_item(**kwargs):
    base = {
        "item_type": "helmet",
        "forging_potential": 40,
        "prefixes": [],
        "suffixes": [],
        "sealed_affix": None,
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# add_affix
# ---------------------------------------------------------------------------

class TestAddAffix:

    def test_adds_prefix_to_empty_item(self):
        item = _make_item()
        result = add_affix(item, "Spell Damage", 1)
        assert result is True
        assert len(item["prefixes"]) == 1
        assert item["prefixes"][0]["name"] == "Spell Damage"
        assert item["prefixes"][0]["tier"] == 1

    def test_deducts_fp_on_success(self):
        item = _make_item(forging_potential=40)
        fp_before = item["forging_potential"]
        add_affix(item, "Spell Damage", 1)
        assert item["forging_potential"] < fp_before

    def test_fails_when_not_enough_fp(self):
        item = _make_item(forging_potential=0)
        result = add_affix(item, "Spell Damage", 1)
        assert result["success"] is False
        assert result["reason"] == "Not enough FP"

    def test_fails_when_affix_not_found(self):
        item = _make_item()
        result = add_affix(item, "This Affix Does Not Exist", 1)
        assert result["success"] is False
        assert result["reason"] == "Affix not found"

    def test_fails_when_prefix_slots_full(self):
        item = _make_item(
            prefixes=[
                {"name": "Spell Damage", "tier": 1},
                {"name": "Fire Damage", "tier": 1},
            ]
        )
        result = add_affix(item, "Cold Damage", 1)
        assert result["success"] is False
        assert result["reason"] == "Slot limit reached"

    def test_fails_when_suffix_slots_full(self):
        item = _make_item(
            suffixes=[
                {"name": "Fire Resistance", "tier": 1},
                {"name": "Cold Resistance", "tier": 1},
            ]
        )
        result = add_affix(item, "Lightning Resistance", 1)
        assert result["success"] is False
        assert result["reason"] == "Slot limit reached"


# ---------------------------------------------------------------------------
# upgrade_affix
# ---------------------------------------------------------------------------

class TestUpgradeAffix:

    def test_upgrades_tier(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 1}])
        result = upgrade_affix(item, "Spell Damage")
        assert result is True
        assert item["prefixes"][0]["tier"] == 2

    def test_deducts_fp_on_upgrade(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 1}])
        fp_before = item["forging_potential"]
        upgrade_affix(item, "Spell Damage")
        assert item["forging_potential"] < fp_before

    def test_fails_when_not_enough_fp(self):
        item = _make_item(forging_potential=0, prefixes=[{"name": "Spell Damage", "tier": 1}])
        result = upgrade_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Not enough FP"

    def test_fails_when_affix_not_found(self):
        item = _make_item()
        result = upgrade_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Affix not found"

    def test_fails_at_max_tier(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 7}])
        result = upgrade_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Already at max tier"


# ---------------------------------------------------------------------------
# remove_affix
# ---------------------------------------------------------------------------

class TestRemoveAffix:

    def test_removes_prefix(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 2}])
        result = remove_affix(item, "Spell Damage")
        assert result is True
        assert len(item["prefixes"]) == 0

    def test_removes_suffix(self):
        item = _make_item(suffixes=[{"name": "Cast Speed", "tier": 1}])
        result = remove_affix(item, "Cast Speed")
        assert result is True
        assert len(item["suffixes"]) == 0

    def test_deducts_fp_on_remove(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 1}])
        fp_before = item["forging_potential"]
        remove_affix(item, "Spell Damage")
        assert item["forging_potential"] < fp_before

    def test_fails_when_not_enough_fp(self):
        item = _make_item(forging_potential=0, prefixes=[{"name": "Spell Damage", "tier": 1}])
        result = remove_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Not enough FP"

    def test_fails_when_affix_not_found(self):
        item = _make_item()
        result = remove_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Affix not found"


# ---------------------------------------------------------------------------
# seal_affix
# ---------------------------------------------------------------------------

class TestSealAffix:

    def test_seals_prefix(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 3}])
        result = seal_affix(item, "Spell Damage")
        assert result is True
        assert item["sealed_affix"]["name"] == "Spell Damage"
        assert len(item["prefixes"]) == 0

    def test_seals_suffix(self):
        item = _make_item(suffixes=[{"name": "Cast Speed", "tier": 2}])
        result = seal_affix(item, "Cast Speed")
        assert result is True
        assert item["sealed_affix"]["name"] == "Cast Speed"
        assert len(item["suffixes"]) == 0

    def test_deducts_fp_on_seal(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 1}])
        fp_before = item["forging_potential"]
        seal_affix(item, "Spell Damage")
        assert item["forging_potential"] < fp_before

    def test_fails_when_sealed_slot_occupied(self):
        item = _make_item(
            prefixes=[{"name": "Spell Damage", "tier": 1}],
            sealed_affix={"name": "Fire Damage", "tier": 2},
        )
        result = seal_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Already has sealed affix"

    def test_fails_when_not_enough_fp(self):
        item = _make_item(forging_potential=0, prefixes=[{"name": "Spell Damage", "tier": 1}])
        result = seal_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Not enough FP"

    def test_fails_when_affix_not_found(self):
        item = _make_item()
        result = seal_affix(item, "Spell Damage")
        assert result["success"] is False
        assert result["reason"] == "Affix not found"


# ---------------------------------------------------------------------------
# unseal_affix
# ---------------------------------------------------------------------------

class TestUnsealAffix:

    def test_returns_sealed_prefix_to_prefix_list(self):
        item = _make_item(sealed_affix={"name": "Spell Damage", "tier": 3})
        result = unseal_affix(item)
        assert result is True
        assert item["sealed_affix"] is None
        assert any(a["name"] == "Spell Damage" for a in item["prefixes"])

    def test_returns_sealed_suffix_to_suffix_list(self):
        item = _make_item(sealed_affix={"name": "Fire Resistance", "tier": 2})
        result = unseal_affix(item)
        assert result is True
        assert item["sealed_affix"] is None
        assert any(a["name"] == "Fire Resistance" for a in item["suffixes"])

    def test_deducts_fp_on_unseal(self):
        item = _make_item(sealed_affix={"name": "Spell Damage", "tier": 1})
        fp_before = item["forging_potential"]
        unseal_affix(item)
        assert item["forging_potential"] < fp_before

    def test_fails_when_no_sealed_affix(self):
        item = _make_item()
        result = unseal_affix(item)
        assert result["success"] is False
        assert result["reason"] == "No sealed affix"

    def test_fails_when_not_enough_fp(self):
        item = _make_item(forging_potential=0, sealed_affix={"name": "Spell Damage", "tier": 1})
        result = unseal_affix(item)
        assert result["success"] is False
        assert result["reason"] == "Not enough FP"

# ---------------------------------------------------------------------------
# fracture_item
# ---------------------------------------------------------------------------

class TestFractureItem:

    def test_marks_item_as_fractured(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 3}])
        result = fracture_item(item)
        assert result["success"] is True
        assert item["is_fractured"] is True

    def test_destroys_one_affix(self):
        item = _make_item(
            prefixes=[{"name": "Spell Damage", "tier": 3}],
            suffixes=[{"name": "Fire Resistance", "tier": 2}],
        )
        total_before = len(item["prefixes"]) + len(item["suffixes"])
        fracture_item(item)
        total_after = len(item["prefixes"]) + len(item["suffixes"])
        assert total_after == total_before - 1

    def test_returns_destroyed_affix_name(self):
        item = _make_item(prefixes=[{"name": "Spell Damage", "tier": 3}])
        result = fracture_item(item)
        assert result["destroyed_affix"] == "Spell Damage"

    def test_does_not_destroy_sealed_affix(self):
        sealed = {"name": "Spell Damage", "tier": 3, "sealed": True}
        item = _make_item(
            prefixes=[{"name": "Fire Damage", "tier": 1}, sealed],
        )
        fracture_item(item)
        assert any(a.get("sealed") for a in item["prefixes"])

    def test_fails_when_already_fractured(self):
        item = _make_item(
            prefixes=[{"name": "Spell Damage", "tier": 1}],
            is_fractured=True,
        )
        result = fracture_item(item)
        assert result["success"] is False
        assert result["reason"] == "Item is already fractured"

    def test_fails_when_no_affixes(self):
        item = _make_item()
        result = fracture_item(item)
        assert result["success"] is False
        assert result["reason"] == "No affixes to fracture"
