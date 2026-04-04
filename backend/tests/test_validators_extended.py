"""
Extended validator tests — heavy parametrization for coverage breadth.
"""

from __future__ import annotations

import pytest

from app.engines.validators import (
    validate_build, validate_item, validate_affix_combination,
    validate_stat_ranges, VALID_SLOTS, VALID_CLASSES, VALID_MASTERIES,
)


def _item(**kw) -> dict:
    b = {"slot_type": "helmet", "forging_potential": 10, "affixes": []}
    b.update(kw)
    return b


def _build(**kw) -> dict:
    b = {"character_class": "Mage", "mastery": "Sorcerer",
         "passive_tree": [], "gear": [], "primary_skill": "Fireball"}
    b.update(kw)
    return b


def _affix(name="Added Health", tier=1, affix_type="prefix") -> dict:
    return {"name": name, "tier": tier, "type": affix_type}


# ---------------------------------------------------------------------------
# A. All valid slots × forging_potential values
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", sorted(VALID_SLOTS))
@pytest.mark.parametrize("fp", [0, 1, 5, 10, 20, 50, 100])
def test_slot_with_fp(slot, fp):
    r = validate_item({"slot_type": slot, "forging_potential": fp, "affixes": []})
    slot_errors = [e for e in r.errors if e.code == "SLOT_INVALID"]
    fp_errors = [e for e in r.errors if e.code == "FP_NEGATIVE"]
    assert len(slot_errors) == 0
    assert len(fp_errors) == 0


# ---------------------------------------------------------------------------
# B. All valid slots — single tier 1 affix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", sorted(VALID_SLOTS))
def test_valid_slot_one_affix(slot):
    item = {"slot_type": slot, "forging_potential": 10,
            "affixes": [_affix("Added Health", tier=1)]}
    r = validate_item(item)
    slot_errors = [e for e in r.errors if e.code == "SLOT_INVALID"]
    assert len(slot_errors) == 0


# ---------------------------------------------------------------------------
# C. All valid tiers for each slot
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", sorted(VALID_SLOTS))
@pytest.mark.parametrize("tier", [1, 2, 3, 4, 5, 6, 7])
def test_valid_tier_in_each_slot(slot, tier):
    item = {"slot_type": slot, "forging_potential": 10,
            "affixes": [_affix("Added Health", tier=tier)]}
    r = validate_item(item)
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    assert len(tier_errors) == 0


# ---------------------------------------------------------------------------
# D. Invalid tiers per slot
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slot", sorted(VALID_SLOTS))
@pytest.mark.parametrize("bad_tier", [0, -1, 8, 9, 10])
def test_invalid_tier_in_each_slot(slot, bad_tier):
    item = {"slot_type": slot, "forging_potential": 10,
            "affixes": [_affix("Added Health", tier=bad_tier)]}
    r = validate_item(item)
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    assert len(tier_errors) > 0


# ---------------------------------------------------------------------------
# E. All valid class–mastery combos
# ---------------------------------------------------------------------------

_CLASS_MASTERY_PAIRS = [
    (cls, mastery)
    for cls, masteries in VALID_MASTERIES.items()
    for mastery in masteries
    if mastery  # skip empty strings
]


@pytest.mark.parametrize("char_class,mastery", _CLASS_MASTERY_PAIRS)
def test_valid_class_mastery_no_error(char_class, mastery):
    r = validate_build(_build(character_class=char_class, mastery=mastery))
    mismatch_errors = [e for e in r.errors if e.code == "MASTERY_MISMATCH"]
    assert len(mismatch_errors) == 0


@pytest.mark.parametrize("char_class,mastery", _CLASS_MASTERY_PAIRS)
def test_valid_class_mastery_build_valid(char_class, mastery):
    r = validate_build(_build(character_class=char_class, mastery=mastery))
    assert r.valid


# ---------------------------------------------------------------------------
# F. Invalid mastery for each class (cross-class masteries)
# ---------------------------------------------------------------------------

_WRONG_MASTERIES = [
    ("Mage", "Paladin"),
    ("Mage", "Bladedancer"),
    ("Mage", "Lich"),
    ("Sentinel", "Sorcerer"),
    ("Sentinel", "Bladedancer"),
    ("Sentinel", "Lich"),
    ("Rogue", "Paladin"),
    ("Rogue", "Sorcerer"),
    ("Rogue", "Lich"),
    ("Primalist", "Sorcerer"),
    ("Primalist", "Paladin"),
    ("Primalist", "Bladedancer"),
    ("Acolyte", "Sorcerer"),
    ("Acolyte", "Paladin"),
    ("Acolyte", "Bladedancer"),
]


@pytest.mark.parametrize("char_class,bad_mastery", _WRONG_MASTERIES)
def test_wrong_mastery_is_error(char_class, bad_mastery):
    r = validate_build(_build(character_class=char_class, mastery=bad_mastery))
    assert any(e.code == "MASTERY_MISMATCH" for e in r.errors)


# ---------------------------------------------------------------------------
# G. Implicit stats — numeric types accepted
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val", [0, 1, -1, 0.5, 100.0, -100.0, 1e6])
def test_numeric_implicit_stat_accepted(val):
    item = _item(implicit_stats={"health_bonus": val})
    r = validate_item(item)
    impl_errors = [e for e in r.errors if e.code == "IMPLICIT_NOT_NUMERIC"]
    assert len(impl_errors) == 0


@pytest.mark.parametrize("bad_val", ["50", None, [], {}])
def test_non_numeric_implicit_stat_rejected(bad_val):
    item = _item(implicit_stats={"health_bonus": bad_val})
    r = validate_item(item)
    impl_errors = [e for e in r.errors if e.code == "IMPLICIT_NOT_NUMERIC"]
    assert len(impl_errors) > 0


# ---------------------------------------------------------------------------
# H. validate_stat_ranges — non-negative stats parametrized
# ---------------------------------------------------------------------------

_NON_NEGATIVE_STATS = [
    "max_health", "armour", "dodge_rating", "ward",
    "base_damage", "attack_speed", "crit_multiplier",
]


@pytest.mark.parametrize("stat", _NON_NEGATIVE_STATS)
@pytest.mark.parametrize("val", [0.0, 0.001, 1.0, 100.0, 10000.0])
def test_non_negative_stat_positive_values(stat, val):
    r = validate_stat_ranges({stat: val})
    neg_errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(neg_errors) == 0


@pytest.mark.parametrize("stat", _NON_NEGATIVE_STATS)
@pytest.mark.parametrize("val", [-0.001, -1.0, -100.0])
def test_non_negative_stat_negative_values(stat, val):
    r = validate_stat_ranges({stat: val})
    neg_errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(neg_errors) > 0


# ---------------------------------------------------------------------------
# I. validate_stat_ranges — resistance parametrized
# ---------------------------------------------------------------------------

_RES_STATS = ["fire_res", "cold_res", "lightning_res", "void_res",
              "necrotic_res", "physical_res", "poison_res"]


@pytest.mark.parametrize("res", _RES_STATS)
@pytest.mark.parametrize("val", [-100.0, -50.0, 0.0, 25.0, 50.0, 75.0, 100.0])
def test_resistance_normal_range(res, val):
    r = validate_stat_ranges({res: val})
    extreme_warns = [w for w in r.warnings if w.code == "RESISTANCE_EXTREME" and w.field == res]
    assert len(extreme_warns) == 0


@pytest.mark.parametrize("res", _RES_STATS)
@pytest.mark.parametrize("val", [-200.0, -150.0, 150.0, 200.0, 500.0])
def test_resistance_extreme_range(res, val):
    r = validate_stat_ranges({res: val})
    extreme_warns = [w for w in r.warnings if w.code == "RESISTANCE_EXTREME" and w.field == res]
    assert len(extreme_warns) > 0


# ---------------------------------------------------------------------------
# J. validate_affix_combination — tier range
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tier", [1, 2, 3, 4, 5, 6, 7])
def test_affix_combo_valid_tier(tier):
    r = validate_affix_combination([_affix("Added Health", tier=tier)])
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    assert len(tier_errors) == 0


@pytest.mark.parametrize("tier", [0, -1, 8, 9, 100])
def test_affix_combo_invalid_tier(tier):
    r = validate_affix_combination([_affix("Added Health", tier=tier)])
    tier_errors = [e for e in r.errors if "TIER" in e.code]
    assert len(tier_errors) > 0


# ---------------------------------------------------------------------------
# K. validate_build — passive tree sizes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_nodes", [0, 1, 5, 10, 50, 100, 113])
def test_passive_tree_size_at_or_below_limit(n_nodes):
    r = validate_build(_build(passive_tree=list(range(n_nodes))))
    overflow_errors = [e for e in r.errors if e.code == "PASSIVE_OVERFLOW"]
    assert len(overflow_errors) == 0


@pytest.mark.parametrize("n_nodes", [114, 150, 200, 300])
def test_passive_tree_size_above_limit(n_nodes):
    r = validate_build(_build(passive_tree=list(range(n_nodes))))
    assert any(e.code == "PASSIVE_OVERFLOW" for e in r.errors)


# ---------------------------------------------------------------------------
# L. validate_build — FP missing warning propagation through gear
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_items", [1, 2, 3])
def test_gear_items_without_fp_each_warn(n_items):
    gear = [{"slot_type": f"helmet" if i == 0 else ("boots" if i == 1 else "gloves"),
             "affixes": []} for i in range(n_items)]
    r = validate_build(_build(gear=gear))
    fp_warns = [w for w in r.warnings if w.code == "FP_MISSING"]
    assert len(fp_warns) == n_items


# ---------------------------------------------------------------------------
# M. validate_item — slot_index parameter
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("idx", [0, 1, 2, 5, 10, 15])
def test_slot_index_in_field_path_valid(idx):
    r = validate_item(_item(), slot_index=idx)
    assert isinstance(r.valid, bool)


@pytest.mark.parametrize("idx", [0, 1, 3, 5])
def test_slot_index_in_fp_field_path(idx):
    r = validate_item({"slot_type": "helmet", "affixes": []}, slot_index=idx)
    fp_warns = [w for w in r.warnings if w.code == "FP_MISSING"]
    for w in fp_warns:
        assert f"gear[{idx}]" in w.field


# ---------------------------------------------------------------------------
# N. validate_affix_combination — prefix/suffix mix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_prefixes,n_suffixes", [
    (0, 1), (0, 2), (0, 3),
    (1, 0), (2, 0), (3, 0),
    (1, 1), (1, 2), (2, 1),
    (2, 2), (3, 3),
    (1, 3), (3, 1),
])
def test_valid_prefix_suffix_mix(n_prefixes, n_suffixes):
    affixes = (
        [_affix(f"P{i}") for i in range(n_prefixes)] +
        [_affix(f"S{i}", affix_type="suffix") for i in range(n_suffixes)]
    )
    r = validate_affix_combination(affixes)
    overflow = any(e.code in ("PREFIX_OVERFLOW", "SUFFIX_OVERFLOW") for e in r.errors)
    assert not overflow


@pytest.mark.parametrize("n_prefixes,n_suffixes", [
    (4, 0), (5, 0), (4, 3),
    (0, 4), (0, 5), (3, 4),
    (4, 4),
])
def test_overflow_prefix_suffix(n_prefixes, n_suffixes):
    affixes = (
        [_affix(f"P{i}") for i in range(n_prefixes)] +
        [_affix(f"S{i}", affix_type="suffix") for i in range(n_suffixes)]
    )
    r = validate_affix_combination(affixes)
    overflow = any(e.code in ("PREFIX_OVERFLOW", "SUFFIX_OVERFLOW") for e in r.errors)
    assert overflow


# ---------------------------------------------------------------------------
# O. validate_build — primary_skill types
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill", ["Fireball", "Frostbolt", "", "Some Skill Name 123"])
def test_valid_primary_skill_strings(skill):
    r = validate_build(_build(primary_skill=skill))
    skill_errors = [e for e in r.errors if e.code == "SKILL_NOT_STRING"]
    assert len(skill_errors) == 0


@pytest.mark.parametrize("bad_skill", [123, 3.14, [], {}, True])
def test_invalid_primary_skill_types(bad_skill):
    r = validate_build(_build(primary_skill=bad_skill))
    skill_errors = [e for e in r.errors if e.code == "SKILL_NOT_STRING"]
    assert len(skill_errors) > 0
