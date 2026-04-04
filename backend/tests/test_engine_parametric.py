"""
Parametric engine tests — heavy combinations for all 6 upgrade engines.
"""

from __future__ import annotations

import pytest

from app.engines.stat_resolution_pipeline import quick_resolve, resolve_final_stats, apply_derived_stats
from app.engines.combat_simulator import run_combat_simulation
from app.engines.craft_simulator import simulate_crafting_path
from app.engines.build_optimizer import optimize_build, pareto_front
from app.engines.build_serializer import export_build, import_build, export_to_json, export_to_fbs
from app.engines.validators import validate_build, validate_item, validate_stat_ranges
from app.engines.stat_engine import BuildStats


def _bs(**kw) -> BuildStats:
    s = BuildStats()
    for k, v in kw.items():
        setattr(s, k, v)
    return s


def _build(c="Mage", m="Sorcerer") -> dict:
    return {"character_class": c, "mastery": m, "passive_tree": [], "gear": []}


def _enemy(dmg=0, armor=0) -> dict:
    return {
        "max_health": 10000, "armor": armor,
        "resistances": {k: 0 for k in ["physical","fire","cold","lightning","void","necrotic"]},
        "crit_chance": 0.0, "crit_multiplier": 1.5,
        "damage_per_hit": dmg, "attack_speed": 0.5 if dmg > 0 else 0,
        "damage_range": [int(dmg*0.8), int(dmg*1.2)] if dmg > 0 else [0,0],
        "skill_pattern": ["basic"], "tags": [],
    }


# ---------------------------------------------------------------------------
# A. Stat engine — attribute combinations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("str_v,dex_v,vit_v,int_v,att_v", [
    (0, 0, 0, 0, 0),
    (10, 0, 0, 0, 0),
    (0, 10, 0, 0, 0),
    (0, 0, 10, 0, 0),
    (0, 0, 0, 10, 0),
    (0, 0, 0, 0, 10),
    (10, 10, 10, 10, 10),
    (50, 30, 20, 15, 25),
    (100, 100, 100, 100, 100),
    (0, 0, 100, 0, 0),
    (100, 0, 0, 0, 0),
])
def test_attribute_combinations(str_v, dex_v, vit_v, int_v, att_v):
    s = _bs(max_health=0.0, dodge_rating=0.0, ward_retention_pct=0.0,
            mana_regen=0.0, strength=float(str_v), dexterity=float(dex_v),
            vitality=float(vit_v), intelligence=float(int_v), attunement=float(att_v))
    apply_derived_stats(s)
    assert s.max_health >= 0.0
    assert s.dodge_rating >= 0.0


# ---------------------------------------------------------------------------
# B. Combat simulator — stat × enemy matrix
# ---------------------------------------------------------------------------

_STAT_CONFIGS = [
    {"base_damage": 50.0, "attack_speed": 0.5, "crit_chance": 0.0},
    {"base_damage": 100.0, "attack_speed": 1.0, "crit_chance": 0.05},
    {"base_damage": 200.0, "attack_speed": 1.5, "crit_chance": 0.1},
    {"base_damage": 500.0, "attack_speed": 2.0, "crit_chance": 0.25},
]

_ENEMY_CONFIGS = [
    {"dmg": 0, "armor": 0},
    {"dmg": 50, "armor": 100},
    {"dmg": 200, "armor": 300},
]


@pytest.mark.parametrize("stat_cfg", _STAT_CONFIGS)
@pytest.mark.parametrize("enemy_cfg", _ENEMY_CONFIGS)
def test_stat_enemy_matrix(stat_cfg, enemy_cfg):
    stats = _bs(max_health=2000.0, armour=0.0, **stat_cfg)
    enemy = _enemy(**enemy_cfg)
    r = run_combat_simulation(stats, enemy, iterations=50, seed=42)
    assert r.average_dps >= 0.0
    assert 0.0 <= r.death_rate <= 1.0


# ---------------------------------------------------------------------------
# C. Craft simulator — FP × seed matrix
# ---------------------------------------------------------------------------

_FP_VALUES = [10, 15, 20, 30, 50]
_SEEDS = [1, 7, 42, 99, 123]


@pytest.mark.parametrize("fp", _FP_VALUES)
@pytest.mark.parametrize("seed", _SEEDS)
def test_fp_seed_matrix(fp, seed):
    r = simulate_crafting_path(
        {"forging_potential": fp, "prefixes": [], "suffixes": []},
        [{"action": "add_affix", "affix": "Added Health"}],
        iterations=100, seed=seed,
    )
    assert r.success_rate + r.fracture_rate == pytest.approx(1.0, abs=1e-9)
    assert r.average_fp_remaining >= 0.0


# ---------------------------------------------------------------------------
# D. Build optimizer — class × weight matrix
# ---------------------------------------------------------------------------

_OPT_CLASSES = [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Paladin"),
    ("Rogue", "Bladedancer"),
    ("Primalist", "Druid"),
    ("Acolyte", "Lich"),
]

_WEIGHT_PAIRS = [
    (1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (0.7, 0.3), (0.3, 0.7),
]


@pytest.mark.parametrize("char_class,mastery", _OPT_CLASSES)
@pytest.mark.parametrize("dw,ew", _WEIGHT_PAIRS)
def test_class_weight_matrix(char_class, mastery, dw, ew):
    b = _build(char_class, mastery)
    r = optimize_build(b, goals={"dps_weight": dw, "ehp_weight": ew}, iterations=3)
    assert r.score is not None
    assert r.best_upgrade["rank"] == 1


# ---------------------------------------------------------------------------
# E. Build serializer — class × skill matrix
# ---------------------------------------------------------------------------

_SKILLS = ["Fireball", "Frostbolt", "Hammer Throw", "Bone Curse", "Maelstrom"]
_SER_CLASSES = [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Paladin"),
    ("Rogue", "Bladedancer"),
]


@pytest.mark.parametrize("char_class,mastery", _SER_CLASSES)
@pytest.mark.parametrize("skill", _SKILLS)
def test_class_skill_export_import(char_class, mastery, skill):
    b = {"character_class": char_class, "mastery": mastery,
         "passive_tree": [], "gear": [], "primary_skill": skill}
    r = import_build(export_to_fbs(b))
    assert r.success
    assert r.build["primary_skill"] == skill


@pytest.mark.parametrize("char_class,mastery", _SER_CLASSES)
@pytest.mark.parametrize("skill", _SKILLS)
def test_class_skill_json_round_trip(char_class, mastery, skill):
    b = {"character_class": char_class, "mastery": mastery,
         "passive_tree": [], "gear": [], "primary_skill": skill}
    r = import_build(export_to_json(b))
    assert r.success
    assert r.build["character_class"] == char_class


# ---------------------------------------------------------------------------
# F. Validator — stat × value matrix
# ---------------------------------------------------------------------------

_NON_NEG_STATS = ["max_health", "armour", "dodge_rating", "attack_speed", "base_damage"]
_POS_VALUES = [0.0, 0.5, 1.0, 10.0, 100.0]
_NEG_VALUES = [-0.001, -1.0, -100.0]


@pytest.mark.parametrize("stat", _NON_NEG_STATS)
@pytest.mark.parametrize("val", _POS_VALUES)
def test_non_neg_stat_valid_values(stat, val):
    r = validate_stat_ranges({stat: val})
    neg_errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(neg_errors) == 0


@pytest.mark.parametrize("stat", _NON_NEG_STATS)
@pytest.mark.parametrize("val", _NEG_VALUES)
def test_non_neg_stat_invalid_values(stat, val):
    r = validate_stat_ranges({stat: val})
    neg_errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
    assert len(neg_errors) > 0


# ---------------------------------------------------------------------------
# G. Resolve → DPS monotonicity matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("low,high", [
    (50.0, 100.0), (100.0, 200.0), (200.0, 500.0),
    (10.0, 1000.0), (1.0, 100.0),
])
def test_more_damage_more_dps(low, high):
    from app.engines.combat_engine import calculate_dps
    s_low = _bs(base_damage=low, attack_speed=1.0, crit_chance=0.0, crit_multiplier=1.5)
    s_high = _bs(base_damage=high, attack_speed=1.0, crit_chance=0.0, crit_multiplier=1.5)
    dps_low = calculate_dps(s_low, "Fireball", 1).dps
    dps_high = calculate_dps(s_high, "Fireball", 1).dps
    assert dps_high >= dps_low


# ---------------------------------------------------------------------------
# H. EHP monotonicity matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hp_low,hp_high", [
    (500.0, 1000.0), (1000.0, 5000.0), (100.0, 100000.0),
])
def test_more_health_more_ehp(hp_low, hp_high):
    from app.engines.defense_engine import calculate_ehp
    s_low = _bs(max_health=hp_low, armour=0.0)
    s_high = _bs(max_health=hp_high, armour=0.0)
    assert calculate_ehp(s_high) > calculate_ehp(s_low)


@pytest.mark.parametrize("arm_low,arm_high", [
    (0.0, 500.0), (500.0, 2000.0), (0.0, 10000.0),
])
def test_more_armour_more_ehp(arm_low, arm_high):
    from app.engines.defense_engine import calculate_ehp
    s_low = _bs(max_health=1000.0, armour=arm_low)
    s_high = _bs(max_health=1000.0, armour=arm_high)
    assert calculate_ehp(s_high) >= calculate_ehp(s_low)


# ---------------------------------------------------------------------------
# I. Resolution determinism matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", [
    ("Mage", "Sorcerer"), ("Mage", "Runemaster"),
    ("Sentinel", "Paladin"), ("Sentinel", "Forge Guard"),
    ("Rogue", "Bladedancer"), ("Rogue", "Marksman"),
    ("Primalist", "Druid"), ("Primalist", "Shaman"),
    ("Acolyte", "Lich"), ("Acolyte", "Necromancer"),
])
@pytest.mark.parametrize("n_passive", [0, 5, 10])
def test_resolve_determinism_matrix(char_class, mastery, n_passive):
    b = _build(char_class, mastery)
    b["passive_tree"] = list(range(n_passive))
    r1 = quick_resolve(b)
    r2 = quick_resolve(b)
    assert r1.max_health == r2.max_health


# ---------------------------------------------------------------------------
# J. Validators — slot × fp matrix
# ---------------------------------------------------------------------------

_SLOTS = ["helmet", "body", "gloves", "boots", "belt", "ring", "amulet"]
_FP_LEVELS = [0, 5, 10, 20]


@pytest.mark.parametrize("slot", _SLOTS)
@pytest.mark.parametrize("fp", _FP_LEVELS)
def test_valid_slot_fp_matrix(slot, fp):
    r = validate_item({"slot_type": slot, "forging_potential": fp, "affixes": []})
    slot_errors = [e for e in r.errors if e.code in ("SLOT_INVALID", "SLOT_MISSING")]
    fp_errors = [e for e in r.errors if e.code == "FP_NEGATIVE"]
    assert len(slot_errors) == 0
    assert len(fp_errors) == 0


# ---------------------------------------------------------------------------
# K. Pareto front across classes × skills
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _OPT_CLASSES)
@pytest.mark.parametrize("skill", ["Fireball", "Frostbolt"])
def test_pareto_class_skill_matrix(char_class, mastery, skill):
    b = {**_build(char_class, mastery), "primary_skill": skill}
    result = pareto_front(b, primary_skill=skill)
    assert isinstance(result, list)
    assert len(result) > 0
