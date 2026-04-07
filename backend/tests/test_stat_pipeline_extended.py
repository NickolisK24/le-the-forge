"""
Extended stat resolution pipeline tests — heavy parametrization.
"""

from __future__ import annotations

import pytest

from app.engines.stat_resolution_pipeline import (
    resolve_final_stats, quick_resolve,
    apply_derived_stats, apply_conversions,
    STR_TO_HEALTH, DEX_TO_DODGE, INT_TO_WARD_RETENTION,
    VIT_TO_HEALTH, ATT_TO_MANA_REGEN,
)
from app.engines.stat_engine import BuildStats


def _stats(**kw) -> BuildStats:
    s = BuildStats()
    for k, v in kw.items():
        setattr(s, k, v)
    return s


def _build(char_class="Mage", mastery="Sorcerer",
           passive_tree=None, gear=None, **kw) -> dict:
    b = {"character_class": char_class, "mastery": mastery,
         "passive_tree": passive_tree or [], "gear": gear or []}
    b.update(kw)
    return b


# ---------------------------------------------------------------------------
# A. All classes produce valid stats
# ---------------------------------------------------------------------------

_CLASSES = [
    ("Mage", "Sorcerer"), ("Mage", "Runemaster"), ("Mage", "Spellblade"),
    ("Sentinel", "Forge Guard"), ("Sentinel", "Paladin"), ("Sentinel", "Void Knight"),
    ("Rogue", "Bladedancer"), ("Rogue", "Marksman"), ("Rogue", "Falconer"),
    ("Primalist", "Shaman"), ("Primalist", "Druid"), ("Primalist", "Beastmaster"),
    ("Acolyte", "Lich"), ("Acolyte", "Necromancer"), ("Acolyte", "Warlock"),
]


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_produce_valid_result(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert isinstance(r.stats, BuildStats)
    assert r.stats.max_health > 0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_crit_chance_valid(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert 0.0 <= r.stats.crit_chance <= 1.0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_attack_speed_nonneg(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert r.stats.attack_speed >= 0.0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_quick_resolve(char_class, mastery):
    s = quick_resolve(_build(char_class=char_class, mastery=mastery))
    assert isinstance(s, BuildStats)


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_deterministic(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r1 = resolve_final_stats(b)
    r2 = resolve_final_stats(b)
    assert r1.stats.max_health == r2.stats.max_health


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resistances_capped_75(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    for attr in ("fire_res", "cold_res", "lightning_res", "void_res", "necrotic_res"):
        assert getattr(r.stats, attr) <= 75.0


# ---------------------------------------------------------------------------
# B. Derived stats — exact scaling for all attribute combinations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("str_val", [0, 1, 5, 10, 25, 50, 100, 200])
def test_str_health_exact_scaling(str_val):
    s = _stats(max_health=0.0, strength=float(str_val), vitality=0.0)
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(str_val * STR_TO_HEALTH)


@pytest.mark.parametrize("dex_val", [0, 1, 5, 10, 25, 50, 100, 200])
def test_dex_dodge_exact_scaling(dex_val):
    s = _stats(dodge_rating=0.0, dexterity=float(dex_val))
    apply_derived_stats(s)
    assert s.dodge_rating == pytest.approx(dex_val * DEX_TO_DODGE)


@pytest.mark.parametrize("int_val", [0, 1, 5, 10, 25, 50, 100])
def test_int_ward_exact_scaling(int_val):
    s = _stats(ward_retention_pct=0.0, intelligence=float(int_val))
    apply_derived_stats(s)
    assert s.ward_retention_pct == pytest.approx(int_val * INT_TO_WARD_RETENTION)


@pytest.mark.parametrize("vit_val", [0, 1, 5, 10, 25, 50, 100])
def test_vit_health_exact_scaling(vit_val):
    s = _stats(max_health=0.0, vitality=float(vit_val), strength=0.0)
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(vit_val * VIT_TO_HEALTH)


@pytest.mark.parametrize("att_val", [0, 1, 5, 10, 25, 50, 100])
def test_att_mana_exact_scaling(att_val):
    s = _stats(mana_regen=0.0, attunement=float(att_val))
    apply_derived_stats(s)
    assert s.mana_regen == pytest.approx(att_val * ATT_TO_MANA_REGEN)


# ---------------------------------------------------------------------------
# C. All damage type conversions
# ---------------------------------------------------------------------------

_DAMAGE_TYPES = ["physical", "fire", "cold", "lightning"]
_CONVERSION_PAIRS = [
    (a, b) for a in _DAMAGE_TYPES for b in _DAMAGE_TYPES if a != b
]


@pytest.mark.parametrize("from_type,to_type", _CONVERSION_PAIRS)
def test_conversion_transfers_correct_amount(from_type, to_type):
    from_attr = f"{from_type}_damage_pct"
    to_attr = f"{to_type}_damage_pct"
    s = BuildStats()
    setattr(s, from_attr, 100.0)
    setattr(s, to_attr, 0.0)
    apply_conversions(s, [{"from": from_type, "to": to_type, "pct": 25}])
    assert getattr(s, to_attr) == pytest.approx(25.0)


@pytest.mark.parametrize("from_type,to_type", _CONVERSION_PAIRS)
def test_conversion_source_unchanged(from_type, to_type):
    from_attr = f"{from_type}_damage_pct"
    to_attr = f"{to_type}_damage_pct"
    s = BuildStats()
    setattr(s, from_attr, 100.0)
    setattr(s, to_attr, 0.0)
    apply_conversions(s, [{"from": from_type, "to": to_type, "pct": 50}])
    assert getattr(s, from_attr) == pytest.approx(100.0)


@pytest.mark.parametrize("pct", [0, 10, 20, 25, 33, 50, 75, 100])
def test_physical_to_fire_pct_exact(pct):
    s = _stats(physical_damage_pct=100.0, fire_damage_pct=0.0)
    apply_conversions(s, [{"from": "physical", "to": "fire", "pct": pct}])
    assert s.fire_damage_pct == pytest.approx(float(pct))


# ---------------------------------------------------------------------------
# D. Snapshots captured for all 6 layers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("layer_key", [
    "1_base_stats", "2_flat_additions", "3_increased_pct",
    "4_more_multipliers", "5_conversions", "6_derived_stats"
])
def test_snapshot_contains_layer(layer_key):
    r = resolve_final_stats(_build(), capture_snapshots=True)
    assert layer_key in r.layer_snapshots


@pytest.mark.parametrize("char_class,mastery", _CLASSES[:5])
def test_snapshot_6_derived_has_max_health(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery),
                            capture_snapshots=True)
    snap = r.layer_snapshots.get("6_derived_stats", {})
    assert "max_health" in snap


# ---------------------------------------------------------------------------
# E. Resolution order — all 6 layers labeled correctly
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolution_order_7_layers(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert len(r.resolution_order) == 7


@pytest.mark.parametrize("i,expected_prefix", [
    (0, "1"), (1, "2"), (2, "3"), (3, "4"), (4, "5"), (5, "6")
])
def test_resolution_order_prefix(i, expected_prefix):
    r = resolve_final_stats(_build())
    assert r.resolution_order[i].startswith(expected_prefix)


# ---------------------------------------------------------------------------
# F. Gear with affixes — pipeline integration
# ---------------------------------------------------------------------------

_AFFIX_ITEMS = [
    [{"name": "Added Health", "tier": 1, "type": "prefix"}],
    [{"name": "Added Health", "tier": 3}],
    [{"name": "Increased Spell Damage", "tier": 1}],
    [],
]


@pytest.mark.parametrize("affixes", _AFFIX_ITEMS)
def test_gear_affixes_resolve(affixes):
    gear = [{"slot_type": "helmet", "forging_potential": 10, "affixes": affixes}]
    r = resolve_final_stats(_build(gear=gear))
    assert r.stats.max_health > 0


@pytest.mark.parametrize("n_gear", [0, 1, 2, 3, 5])
def test_n_empty_gear_items(n_gear):
    slots = ["helmet", "boots", "gloves", "ring", "body"]
    gear = [{"slot_type": slots[i % len(slots)], "forging_potential": 10,
             "affixes": []} for i in range(n_gear)]
    r = resolve_final_stats(_build(gear=gear))
    assert r.stats.max_health > 0


# ---------------------------------------------------------------------------
# G. Passive tree as lists of various lengths
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [0, 1, 5, 10, 20, 50, 100])
def test_passive_tree_lengths(n):
    b = _build(passive_tree=list(range(n)))
    r = resolve_final_stats(b)
    assert r.stats.max_health > 0


# ---------------------------------------------------------------------------
# H. to_dict completeness per class
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_to_dict_has_stats(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    d = r.to_dict()
    assert "stats" in d
    assert "max_health" in d["stats"]


# ---------------------------------------------------------------------------
# I. Multiple derived stat combos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("str_v,dex_v,vit_v,expected_health_bonus", [
    (10, 0, 0, 10 * STR_TO_HEALTH),
    (0, 0, 10, 10 * VIT_TO_HEALTH),
    (10, 0, 10, 10 * STR_TO_HEALTH + 10 * VIT_TO_HEALTH),
    (5, 5, 5, 5 * STR_TO_HEALTH + 5 * VIT_TO_HEALTH),
])
def test_combined_str_vit_health(str_v, dex_v, vit_v, expected_health_bonus):
    s = _stats(max_health=0.0, strength=float(str_v),
               dexterity=float(dex_v), vitality=float(vit_v))
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(expected_health_bonus)


# ---------------------------------------------------------------------------
# J. No negative health from default build
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_health_always_positive(char_class, mastery):
    r = resolve_final_stats(_build(char_class=char_class, mastery=mastery))
    assert r.stats.max_health > 0


# ---------------------------------------------------------------------------
# K. Conversions with no damage stat have no effect
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("from_type", ["physical", "fire", "cold", "lightning"])
def test_zero_source_conversion_no_effect(from_type):
    from_attr = f"{from_type}_damage_pct"
    to_attr = "fire_damage_pct" if from_type != "fire" else "cold_damage_pct"
    to_type = "fire" if from_type != "fire" else "cold"
    s = BuildStats()
    setattr(s, from_attr, 0.0)
    setattr(s, to_attr, 0.0)
    apply_conversions(s, [{"from": from_type, "to": to_type, "pct": 100}])
    assert getattr(s, to_attr) == pytest.approx(0.0)
