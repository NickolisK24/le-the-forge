"""Tests for affix_engine.py"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.engines.affix_engine import (
    affix_data,
    get_affixes_by_type,
    get_prefixes,
    get_suffixes,
    get_affix_pool,
    get_affix_by_name,
    get_affix_by_id,
    get_affix_tier_data,
    get_max_tier,
    is_affix_valid_for_item,
    validate_affix_slots,
    can_add_affix,
    count_affix_types,
)


class TestAffixLoading(unittest.TestCase):
    def test_data_loaded(self):
        self.assertIsInstance(affix_data, list)
        self.assertGreater(len(affix_data), 0)

    def test_affix_schema(self):
        for affix in affix_data:
            self.assertIn("id", affix)
            self.assertIn("name", affix)
            self.assertIn("type", affix)
            self.assertIn("applicable_to", affix)
            self.assertIn("tiers", affix)

    def test_only_known_types(self):
        # Affix types: prefix, suffix, and idol (idol-slot affixes)
        types = {a["type"] for a in affix_data}
        self.assertTrue(types <= {"prefix", "suffix", "idol"})


class TestAffixFiltering(unittest.TestCase):
    def test_get_affixes_by_type_returns_list(self):
        result = get_affixes_by_type("wand", "prefix")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_all_results_match_type(self):
        for affix in get_affixes_by_type("helmet", "prefix"):
            self.assertEqual(affix["type"], "prefix")

    def test_all_results_valid_for_item(self):
        for affix in get_affixes_by_type("boots", "suffix"):
            self.assertIn("boots", affix["applicable_to"])

    def test_unknown_item_type_returns_empty(self):
        result = get_affixes_by_type("magic_carpet", "prefix")
        self.assertEqual(result, [])

    def test_get_prefixes_helper(self):
        result = get_prefixes("wand")
        self.assertTrue(all(a["type"] == "prefix" for a in result))

    def test_get_suffixes_helper(self):
        result = get_suffixes("boots")
        self.assertTrue(all(a["type"] == "suffix" for a in result))

    def test_get_affix_pool(self):
        pool = get_affix_pool("helmet")
        self.assertIn("prefixes", pool)
        self.assertIn("suffixes", pool)
        self.assertIsInstance(pool["prefixes"], list)
        self.assertIsInstance(pool["suffixes"], list)


class TestAffixLookup(unittest.TestCase):
    def test_get_affix_by_name_found(self):
        first = affix_data[0]
        result = get_affix_by_name(first["name"])
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], first["id"])

    def test_get_affix_by_name_missing(self):
        self.assertIsNone(get_affix_by_name("NonExistentAffix_XYZ"))

    def test_get_affix_by_id_found(self):
        first = affix_data[0]
        result = get_affix_by_id(first["id"])
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], first["name"])

    def test_get_affix_by_id_missing(self):
        self.assertIsNone(get_affix_by_id("does_not_exist"))


class TestTierAccess(unittest.TestCase):
    def _get_affix_def(self):
        return get_affix_by_name(affix_data[0]["name"])

    def test_get_affix_tier_data_valid(self):
        affix_def = self._get_affix_def()
        tier_data = get_affix_tier_data(affix_def, 1)
        self.assertIsNotNone(tier_data)
        self.assertIsInstance(tier_data.min, float)
        self.assertIsInstance(tier_data.max, float)

    def test_get_affix_tier_data_out_of_range(self):
        affix_def = self._get_affix_def()
        self.assertIsNone(get_affix_tier_data(affix_def, 999))

    def test_get_max_tier(self):
        affix_def = self._get_affix_def()
        max_t = get_max_tier(affix_def)
        self.assertGreater(max_t, 0)
        self.assertEqual(max_t, max(t.tier for t in affix_def.tiers))


class TestSlotValidation(unittest.TestCase):
    def test_valid_item(self):
        item = {"prefixes": [{"name": "a"}, {"name": "b"}], "suffixes": [{"name": "c"}]}
        self.assertTrue(validate_affix_slots(item))

    def test_full_item(self):
        item = {
            "prefixes": [{"name": "a"}, {"name": "b"}],
            "suffixes": [{"name": "c"}, {"name": "d"}],
        }
        self.assertTrue(validate_affix_slots(item))

    def test_prefix_overflow(self):
        item = {"prefixes": [{"name": "a"}, {"name": "b"}, {"name": "c"}], "suffixes": []}
        self.assertFalse(validate_affix_slots(item))

    def test_suffix_overflow(self):
        item = {"prefixes": [], "suffixes": [{"name": "a"}, {"name": "b"}, {"name": "c"}]}
        self.assertFalse(validate_affix_slots(item))

    def test_empty_item(self):
        item = {"prefixes": [], "suffixes": []}
        self.assertTrue(validate_affix_slots(item))

    def test_can_add_prefix_when_space(self):
        item = {"prefixes": [{"name": "a"}], "suffixes": []}
        self.assertTrue(can_add_affix(item, "prefix"))

    def test_cannot_add_prefix_when_full(self):
        item = {"prefixes": [{"name": "a"}, {"name": "b"}], "suffixes": []}
        self.assertFalse(can_add_affix(item, "prefix"))

    def test_can_add_suffix(self):
        item = {"prefixes": [], "suffixes": []}
        self.assertTrue(can_add_affix(item, "suffix"))


class TestAffixCompatibility(unittest.TestCase):
    def test_valid_item_type(self):
        affix = affix_data[0]
        item_type = affix["applicable_to"][0]
        self.assertTrue(is_affix_valid_for_item(item_type, affix))

    def test_invalid_item_type(self):
        affix = affix_data[0]
        self.assertFalse(is_affix_valid_for_item("magic_carpet", affix))


class TestAffixCounting(unittest.TestCase):
    def test_count_affixes(self):
        item = {
            "prefixes": [{"name": "a"}, {"name": "b"}],
            "suffixes": [{"name": "c"}],
            "sealed": None,
        }
        counts = count_affix_types(item)
        self.assertEqual(counts["prefixes"], 2)
        self.assertEqual(counts["suffixes"], 1)
        self.assertEqual(counts["sealed"], 0)

    def test_count_with_sealed(self):
        item = {
            "prefixes": [{"name": "a"}],
            "suffixes": [],
            "sealed": {"name": "b"},
        }
        counts = count_affix_types(item)
        self.assertEqual(counts["sealed"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
