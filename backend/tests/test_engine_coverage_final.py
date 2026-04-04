"""
Final coverage push — maximum parametrization across all engines.
"""

from __future__ import annotations

import pytest

from app.engines.stat_resolution_pipeline import (
    quick_resolve, resolve_final_stats, apply_derived_stats, apply_conversions,
    STR_TO_HEALTH, DEX_TO_DODGE, VIT_TO_HEALTH, ATT_TO_MANA_REGEN,
)
from app.engines.combat_simulator import run_combat_simulation
from app.engines.craft_simulator import simulate_crafting_path
from app.engines.build_optimizer import optimize_build, pareto_front
from app.engines.build_serializer import (
    export_build, export_to_json, export_to_fbs,
    import_build, _checksum, _SCHEMA_VERSION,
)
from app.engines.validators import (
    validate_build, validate_item, validate_stat_ranges, validate_affix_combination,
    VALID_SLOTS,
)
from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_ehp


def _bs(**kw) -> BuildStats:
    s = BuildStats()
    for k, v in kw.items():
        setattr(s, k, v)
    return s


def _build(c="Mage", m="Sorcerer", pt=None, gear=None, skill="Fireball") -> dict:
    return {"character_class": c, "mastery": m, "passive_tree": pt or [],
            "gear": gear or [], "primary_skill": skill}


def _enemy(hp=10000, dmg=0) -> dict:
    return {"max_health": hp, "armor": 0,
            "resistances": {k: 0 for k in ["physical","fire","cold","lightning","void","necrotic"]},
            "crit_chance": 0.0, "crit_multiplier": 1.5,
            "damage_per_hit": dmg, "attack_speed": 0.5 if dmg > 0 else 0,
            "damage_range": [int(dmg*0.8)+1, int(dmg*1.2)+1] if dmg > 0 else [0, 0],
            "skill_pattern": ["basic"], "tags": []}


# ---------------------------------------------------------------------------
# A. DPS × attack speed matrix (15 combinations)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("base_damage", [10.0, 50.0, 100.0, 200.0, 500.0])
@pytest.mark.parametrize("attack_speed", [0.5, 1.0, 2.0])
def test_dps_damage_speed_matrix(base_damage, attack_speed):
    s = _bs(base_damage=base_damage, attack_speed=attack_speed,
            crit_chance=0.0, crit_multiplier=1.5)
    result = calculate_dps(s, "Fireball", 1)
    assert result.dps >= 0.0


# ---------------------------------------------------------------------------
# B. EHP × armour × health matrix (20 combinations)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("max_health", [100.0, 500.0, 1000.0, 5000.0])
@pytest.mark.parametrize("armour", [0.0, 100.0, 500.0, 1000.0, 5000.0])
def test_ehp_health_armour_matrix(max_health, armour):
    s = _bs(max_health=max_health, armour=armour)
    ehp = calculate_ehp(s)
    assert ehp > 0.0
    assert ehp >= max_health  # EHP always >= health


# ---------------------------------------------------------------------------
# C. Resolve stats for many gear configurations (12 combinations)
# ---------------------------------------------------------------------------

_SLOT_CONFIGS = [
    [],
    [{"slot_type": "helmet", "forging_potential": 10, "affixes": []}],
    [{"slot_type": "boots", "forging_potential": 15, "affixes": []}],
    [{"slot_type": "ring", "forging_potential": 5, "affixes": []}],
]

_CLASSES_SUBSET = [
    ("Mage", "Sorcerer"), ("Sentinel", "Paladin"),
    ("Rogue", "Bladedancer"),
]


@pytest.mark.parametrize("char_class,mastery", _CLASSES_SUBSET)
@pytest.mark.parametrize("gear", _SLOT_CONFIGS)
def test_resolve_with_gear_matrix(char_class, mastery, gear):
    b = _build(c=char_class, m=mastery, gear=gear)
    stats = quick_resolve(b)
    assert stats.max_health > 0.0
    assert stats.attack_speed >= 0.0


# ---------------------------------------------------------------------------
# D. Derived stats — all 5 attributes × 8 values (40 combinations)
# ---------------------------------------------------------------------------

_ATTR_VALUES = [0, 1, 5, 10, 25, 50, 100, 200]


@pytest.mark.parametrize("str_val", _ATTR_VALUES)
def test_str_health_derived(str_val):
    s = _bs(max_health=0.0, strength=float(str_val), vitality=0.0)
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(str_val * STR_TO_HEALTH)


@pytest.mark.parametrize("dex_val", _ATTR_VALUES)
def test_dex_dodge_derived(dex_val):
    s = _bs(dodge_rating=0.0, dexterity=float(dex_val))
    apply_derived_stats(s)
    assert s.dodge_rating == pytest.approx(dex_val * DEX_TO_DODGE)


@pytest.mark.parametrize("vit_val", _ATTR_VALUES)
def test_vit_health_derived(vit_val):
    s = _bs(max_health=0.0, vitality=float(vit_val), strength=0.0)
    apply_derived_stats(s)
    assert s.max_health == pytest.approx(vit_val * VIT_TO_HEALTH)


@pytest.mark.parametrize("att_val", _ATTR_VALUES)
def test_att_mana_derived(att_val):
    s = _bs(mana_regen=0.0, attunement=float(att_val))
    apply_derived_stats(s)
    assert s.mana_regen == pytest.approx(att_val * ATT_TO_MANA_REGEN)


# ---------------------------------------------------------------------------
# E. Combat simulation — seed × iterations matrix (25 combinations)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [1, 7, 42, 99, 100])
@pytest.mark.parametrize("iters", [10, 25, 50, 100, 200])
def test_combat_seed_iter_matrix(seed, iters):
    r = run_combat_simulation(_bs(base_damage=100.0, attack_speed=1.0,
                                   crit_chance=0.05, crit_multiplier=1.5,
                                   max_health=1000.0, armour=0.0),
                               _enemy(), iterations=iters, seed=seed)
    assert r.iterations == iters
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# F. Craft simulation — seed × FP matrix (20 combinations)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [1, 7, 42, 99])
@pytest.mark.parametrize("fp", [10, 20, 30, 50, 100])
def test_craft_seed_fp_matrix(seed, fp):
    item = {"forging_potential": fp, "prefixes": [], "suffixes": []}
    r = simulate_crafting_path(item, [{"action": "add_affix", "affix": "Added Health"}],
                                iterations=100, seed=seed)
    assert r.success_rate + r.fracture_rate == pytest.approx(1.0, abs=1e-9)
    assert r.average_fp_remaining >= 0.0


# ---------------------------------------------------------------------------
# G. Build optimizer — iterations × weights matrix (15 combinations)
# ---------------------------------------------------------------------------

_ITER_COUNTS = [1, 3, 5]
_GOAL_COMBOS = [
    {"dps_weight": 1.0, "ehp_weight": 0.0},
    {"dps_weight": 0.0, "ehp_weight": 1.0},
    {"dps_weight": 0.5, "ehp_weight": 0.5},
    {"dps_weight": 0.7, "ehp_weight": 0.3},
    {"dps_weight": 0.3, "ehp_weight": 0.7},
]


@pytest.mark.parametrize("iters", _ITER_COUNTS)
@pytest.mark.parametrize("goals", _GOAL_COMBOS)
def test_optimizer_iter_goals_matrix(iters, goals):
    r = optimize_build(_build(), goals=goals, iterations=iters)
    assert r.iterations == iters
    assert len(r.all_upgrades) == iters
    assert r.goals["dps_weight"] == pytest.approx(goals["dps_weight"])


# ---------------------------------------------------------------------------
# H. Build serializer — passive tree × metadata matrix (16 combinations)
# ---------------------------------------------------------------------------

_PASSIVE_TREES = [[], [1], [1, 2, 3], list(range(10))]
_METADATA_VARIANTS = [
    {},
    {"tag": "test"},
    {"build": "v1", "author": "user"},
    {"notes": "test build"},
]


@pytest.mark.parametrize("pt", _PASSIVE_TREES)
@pytest.mark.parametrize("meta", _METADATA_VARIANTS)
def test_serializer_pt_meta_matrix(pt, meta):
    b = _build(pt=pt)
    r = import_build(export_to_json(b, metadata=meta))
    assert r.success
    assert len(r.build["passive_tree"]) == len(set(pt))


# ---------------------------------------------------------------------------
# I. Validator — slot × sealed affix combinations (20 combos)
# ---------------------------------------------------------------------------

_TEST_SLOTS = sorted(VALID_SLOTS)[:10]  # first 10 slots
_SEALED_VALUES = [
    None,
    {"name": "Added Health", "tier": 1},
]


@pytest.mark.parametrize("slot", _TEST_SLOTS)
@pytest.mark.parametrize("sealed", _SEALED_VALUES)
def test_slot_sealed_matrix(slot, sealed):
    item = {"slot_type": slot, "forging_potential": 10,
            "affixes": [], "sealed_affix": sealed}
    r = validate_item(item)
    seal_errors = [e for e in r.errors if e.code == "SEAL_INVALID"]
    assert len(seal_errors) == 0


# ---------------------------------------------------------------------------
# J. Checksum stability across 25 unique data dicts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n,val", [(i, i * 100) for i in range(25)])
def test_checksum_stability(n, val):
    d = {"character_class": "Mage", "n": n, "val": val}
    chk1 = _checksum(d)
    chk2 = _checksum(d)
    assert chk1 == chk2
    assert len(chk1) == 16


# ---------------------------------------------------------------------------
# K. Validate stat ranges — all non-neg stats × boundary values (56 combos)
# ---------------------------------------------------------------------------

_NON_NEG = ["max_health", "armour", "dodge_rating", "ward",
             "base_damage", "attack_speed", "crit_multiplier"]
_BOUNDARY = [0.0, 0.001, 1.0, 100.0, 10000.0, 1000000.0, 1e9]


@pytest.mark.parametrize("stat", _NON_NEG)
@pytest.mark.parametrize("val", _BOUNDARY)
def test_boundary_values_nonneg(stat, val):
    r = validate_stat_ranges({stat: val})
    neg_errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(neg_errors) == 0


# ---------------------------------------------------------------------------
# L. Resolve → serializer → validator chain (15 combos)
# ---------------------------------------------------------------------------

_CHAIN_CLASSES = [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Paladin"),
    ("Rogue", "Bladedancer"),
    ("Primalist", "Druid"),
    ("Acolyte", "Lich"),
]
_CHAIN_SKILLS = ["Fireball", "Frostbolt", "Lightning Blast"]


@pytest.mark.parametrize("char_class,mastery", _CHAIN_CLASSES)
@pytest.mark.parametrize("skill", _CHAIN_SKILLS)
def test_full_chain_resolve_serialize_validate(char_class, mastery, skill):
    b = _build(c=char_class, m=mastery, skill=skill)
    # Validate
    vr = validate_build(b)
    assert vr.valid
    # Serialize
    fbs = export_to_fbs(b)
    r = import_build(fbs)
    assert r.success
    # Resolve
    stats = quick_resolve(b)
    assert stats.max_health > 0.0


# ---------------------------------------------------------------------------
# M. Pareto front size is always > 0 (15 combos)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CHAIN_CLASSES)
@pytest.mark.parametrize("skill", _CHAIN_SKILLS)
def test_pareto_nonempty_matrix(char_class, mastery, skill):
    b = _build(c=char_class, m=mastery, skill=skill)
    result = pareto_front(b, primary_skill=skill)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# N. Combat sim × character classes (10 combos)
# ---------------------------------------------------------------------------

_COMBAT_CLASSES = [
    ("Mage", "Sorcerer"), ("Mage", "Runemaster"),
    ("Sentinel", "Paladin"), ("Sentinel", "Forge Guard"),
    ("Rogue", "Bladedancer"), ("Rogue", "Marksman"),
    ("Primalist", "Druid"), ("Primalist", "Shaman"),
    ("Acolyte", "Lich"), ("Acolyte", "Necromancer"),
]


@pytest.mark.parametrize("char_class,mastery", _COMBAT_CLASSES)
def test_combat_sim_all_classes(char_class, mastery):
    b = _build(c=char_class, m=mastery)
    r = run_combat_simulation(b, _enemy(), iterations=30, seed=42)
    assert r.average_dps >= 0.0
    assert r.iterations == 30


# ---------------------------------------------------------------------------
# O. Version string in exports (5 tests)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CHAIN_CLASSES)
def test_export_version_constant(char_class, mastery):
    sb = export_build(_build(c=char_class, m=mastery))
    assert sb.version == _SCHEMA_VERSION
