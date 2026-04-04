"""
Matrix validator tests — maximum parametrization for coverage.
"""

from __future__ import annotations

import pytest

from app.engines.validators import (
    validate_build, validate_item, validate_affix_combination,
    validate_stat_ranges, VALID_SLOTS, VALID_CLASSES, VALID_MASTERIES,
)


# All slots sorted
_ALL_SLOTS = sorted(VALID_SLOTS)
# Tiers 1-7 valid, 0 and 8+ invalid
_VALID_TIERS = [1, 2, 3, 4, 5, 6, 7]
_INVALID_TIERS = [0, -1, -5, 8, 9, 10, 50, 100]
# FP values
_VALID_FP = [0, 1, 5, 10, 15, 20, 30, 50, 75, 100]
_INVALID_FP = [-1, -5, -10, -100]
# Stat values
_POS_VALS = [0.0, 0.001, 0.5, 1.0, 5.0, 10.0, 100.0, 1000.0]
_NEG_VALS = [-0.001, -0.5, -1.0, -10.0, -100.0]


# ---------------------------------------------------------------------------
# A. Every valid slot with every valid tier
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", _ALL_SLOTS)
@pytest.mark.parametrize("tier", _VALID_TIERS)
def test_slot_tier_valid(slot, tier):
    item = {"slot_type": slot, "forging_potential": 10,
            "affixes": [{"name": "Added Health", "tier": tier}]}
    r = validate_item(item)
    slot_errors = [e for e in r.errors if e.code == "SLOT_INVALID"]
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    assert len(slot_errors) == 0
    assert len(tier_errors) == 0


# ---------------------------------------------------------------------------
# B. Every valid slot with every valid FP
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", _ALL_SLOTS)
@pytest.mark.parametrize("fp", _VALID_FP)
def test_slot_fp_valid(slot, fp):
    item = {"slot_type": slot, "forging_potential": fp, "affixes": []}
    r = validate_item(item)
    slot_errors = [e for e in r.errors if e.code in ("SLOT_INVALID", "SLOT_MISSING")]
    fp_errors = [e for e in r.errors if e.code == "FP_NEGATIVE"]
    assert len(slot_errors) == 0
    assert len(fp_errors) == 0


# ---------------------------------------------------------------------------
# C. Every valid slot with invalid tier
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", _ALL_SLOTS[:10])  # subset for efficiency
@pytest.mark.parametrize("tier", _INVALID_TIERS)
def test_slot_invalid_tier(slot, tier):
    item = {"slot_type": slot, "forging_potential": 10,
            "affixes": [{"name": "Added Health", "tier": tier}]}
    r = validate_item(item)
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    assert len(tier_errors) > 0


# ---------------------------------------------------------------------------
# D. Every valid slot with invalid FP
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", _ALL_SLOTS[:10])  # subset for efficiency
@pytest.mark.parametrize("fp", _INVALID_FP)
def test_slot_invalid_fp(slot, fp):
    item = {"slot_type": slot, "forging_potential": fp, "affixes": []}
    r = validate_item(item)
    fp_errors = [e for e in r.errors if e.code == "FP_NEGATIVE"]
    assert len(fp_errors) > 0


# ---------------------------------------------------------------------------
# E. validate_stat_ranges — non-negative stats × positive values
# ---------------------------------------------------------------------------

_NON_NEG_KEYS = ["max_health", "armour", "dodge_rating", "ward",
                  "base_damage", "attack_speed", "crit_multiplier"]


@pytest.mark.parametrize("stat", _NON_NEG_KEYS)
@pytest.mark.parametrize("val", _POS_VALS)
def test_stat_positive_values(stat, val):
    r = validate_stat_ranges({stat: val})
    errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(errors) == 0


@pytest.mark.parametrize("stat", _NON_NEG_KEYS)
@pytest.mark.parametrize("val", _NEG_VALS)
def test_stat_negative_values(stat, val):
    r = validate_stat_ranges({stat: val})
    errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(errors) > 0


# ---------------------------------------------------------------------------
# F. validate_stat_ranges — crit_chance
# ---------------------------------------------------------------------------

_CRIT_VALID = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0]
_CRIT_INVALID = [-0.01, -0.5, -1.0, 1.001, 1.1, 1.5, 2.0, 10.0]


@pytest.mark.parametrize("val", _CRIT_VALID)
def test_crit_chance_valid(val):
    r = validate_stat_ranges({"crit_chance": val})
    errors = [e for e in r.errors if e.code == "STAT_OUT_OF_RANGE" and e.field == "crit_chance"]
    assert len(errors) == 0


@pytest.mark.parametrize("val", _CRIT_INVALID)
def test_crit_chance_invalid(val):
    r = validate_stat_ranges({"crit_chance": val})
    errors = [e for e in r.errors if e.code == "STAT_OUT_OF_RANGE" and e.field == "crit_chance"]
    assert len(errors) > 0


# ---------------------------------------------------------------------------
# G. validate_stat_ranges — resistances
# ---------------------------------------------------------------------------

_RES_KEYS = ["fire_res", "cold_res", "lightning_res", "void_res",
              "necrotic_res", "physical_res", "poison_res"]
_RES_NORMAL = [-100.0, -75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0, 100.0]
_RES_EXTREME = [-200.0, -150.0, 101.0, 150.0, 200.0, 500.0]


@pytest.mark.parametrize("res", _RES_KEYS)
@pytest.mark.parametrize("val", _RES_NORMAL)
def test_resistance_normal_no_warning(res, val):
    r = validate_stat_ranges({res: val})
    extreme = [w for w in r.warnings if w.code == "RESISTANCE_EXTREME" and w.field == res]
    assert len(extreme) == 0


@pytest.mark.parametrize("res", _RES_KEYS)
@pytest.mark.parametrize("val", _RES_EXTREME)
def test_resistance_extreme_warning(res, val):
    r = validate_stat_ranges({res: val})
    extreme = [w for w in r.warnings if w.code == "RESISTANCE_EXTREME" and w.field == res]
    assert len(extreme) > 0


# ---------------------------------------------------------------------------
# H. validate_affix_combination — duplicate detection
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_dups", [2, 3, 4])
@pytest.mark.parametrize("affix_name", ["Added Health", "Increased Spell Damage", "Armor"])
def test_duplicate_affixes_detected(n_dups, affix_name):
    affixes = [{"name": affix_name, "tier": 1, "type": "prefix"}] * n_dups
    r = validate_affix_combination(affixes)
    dup_errors = [e for e in r.errors if e.code == "AFFIX_DUPLICATE"]
    assert len(dup_errors) >= n_dups - 1


# ---------------------------------------------------------------------------
# I. validate_build — node type validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("node_val", [1, 2, 5, 10, 100, 1000])
def test_valid_int_nodes(node_val):
    r = validate_build({"character_class": "Mage", "mastery": "Sorcerer",
                        "passive_tree": [node_val], "gear": []})
    node_errors = [e for e in r.errors if e.code == "NODE_INVALID_TYPE"]
    assert len(node_errors) == 0


@pytest.mark.parametrize("bad_node", [3.14, "node_1", None, []])
def test_invalid_node_types(bad_node):
    r = validate_build({"character_class": "Mage", "mastery": "Sorcerer",
                        "passive_tree": [bad_node], "gear": []})
    node_errors = [e for e in r.errors if e.code == "NODE_INVALID_TYPE"]
    assert len(node_errors) > 0


# ---------------------------------------------------------------------------
# J. validate_item — implicit stats matrix
# ---------------------------------------------------------------------------

_IMPLICIT_STATS = [
    {"health": 50.0},
    {"health": 100.0, "mana": 20.0},
    {"armor": 200.0, "health": 150.0, "resist_fire": 10.0},
    {},
]


@pytest.mark.parametrize("implicits", _IMPLICIT_STATS)
def test_valid_implicit_stats(implicits):
    item = {"slot_type": "helmet", "forging_potential": 10,
            "implicit_stats": implicits, "affixes": []}
    r = validate_item(item)
    impl_errors = [e for e in r.errors if e.code == "IMPLICIT_NOT_NUMERIC"]
    assert len(impl_errors) == 0


_BAD_IMPLICITS = [
    {"health": "50"},
    {"health": None},
    {"health": [1, 2]},
    {"health": {}},
]


@pytest.mark.parametrize("implicits", _BAD_IMPLICITS)
def test_invalid_implicit_stats(implicits):
    item = {"slot_type": "helmet", "forging_potential": 10,
            "implicit_stats": implicits, "affixes": []}
    r = validate_item(item)
    impl_errors = [e for e in r.errors if e.code == "IMPLICIT_NOT_NUMERIC"]
    assert len(impl_errors) > 0


# ---------------------------------------------------------------------------
# K. validate_build — gear slot uniqueness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", ["helmet", "body", "gloves", "boots", "belt"])
def test_duplicate_slot_warning(slot):
    gear = [{"slot_type": slot, "forging_potential": 10, "affixes": []},
            {"slot_type": slot, "forging_potential": 10, "affixes": []}]
    r = validate_build({"character_class": "Mage", "mastery": "Sorcerer",
                        "passive_tree": [], "gear": gear})
    dup_warns = [w for w in r.warnings if w.code == "SLOT_DUPLICATE"]
    assert len(dup_warns) > 0


@pytest.mark.parametrize("slot1,slot2", [
    ("helmet", "boots"), ("boots", "gloves"), ("ring", "amulet"),
    ("helmet", "body"), ("gloves", "belt"),
])
def test_different_slots_no_duplicate_warning(slot1, slot2):
    gear = [{"slot_type": slot1, "forging_potential": 10, "affixes": []},
            {"slot_type": slot2, "forging_potential": 10, "affixes": []}]
    r = validate_build({"character_class": "Mage", "mastery": "Sorcerer",
                        "passive_tree": [], "gear": gear})
    dup_warns = [w for w in r.warnings if w.code == "SLOT_DUPLICATE"]
    assert len(dup_warns) == 0


# ---------------------------------------------------------------------------
# L. validate_affix_combination — tier edge cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier1,tier2,both_valid", [
    (1, 7, True), (3, 5, True), (1, 1, True), (7, 7, True),
    (0, 1, False), (1, 8, False), (0, 8, False),
])
def test_two_affix_tier_combo(tier1, tier2, both_valid):
    affixes = [
        {"name": "AffixA", "tier": tier1, "type": "prefix"},
        {"name": "AffixB", "tier": tier2, "type": "suffix"},
    ]
    r = validate_affix_combination(affixes)
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    if both_valid:
        assert len(tier_errors) == 0
    else:
        assert len(tier_errors) > 0
