"""
Engine integration tests — exercising multiple engines together.

These tests verify that stat resolution → combat/craft/optimize pipelines
produce consistent and valid outputs end-to-end.
"""

from __future__ import annotations

import pytest

from app.engines.stat_resolution_pipeline import quick_resolve, resolve_final_stats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_ehp
from app.engines.combat_simulator import run_combat_simulation
from app.engines.craft_simulator import simulate_crafting_path
from app.engines.build_optimizer import optimize_build, pareto_front
from app.engines.build_serializer import export_build, import_build, export_to_fbs, export_to_json
from app.engines.validators import validate_build, validate_item
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build(char_class="Mage", mastery="Sorcerer", gear=None,
           passive_tree=None, primary_skill="Fireball") -> dict:
    return {
        "character_class": char_class,
        "mastery": mastery,
        "passive_tree": passive_tree or [],
        "gear": gear or [],
        "primary_skill": primary_skill,
    }


def _dummy_enemy():
    return {
        "max_health": 10000, "armor": 0,
        "resistances": {"physical": 0, "fire": 0, "cold": 0,
                        "lightning": 0, "void": 0, "necrotic": 0},
        "crit_chance": 0.0, "crit_multiplier": 1.5,
        "damage_per_hit": 0, "attack_speed": 0,
        "damage_range": [0, 0], "skill_pattern": ["basic"], "tags": [],
    }


def _craft_item(fp=30):
    return {"forging_potential": fp, "prefixes": [], "suffixes": []}


_CLASSES = [
    ("Mage", "Sorcerer"), ("Mage", "Runemaster"),
    ("Sentinel", "Paladin"), ("Sentinel", "Forge Guard"),
    ("Rogue", "Bladedancer"), ("Rogue", "Marksman"),
    ("Primalist", "Druid"), ("Primalist", "Shaman"),
    ("Acolyte", "Lich"), ("Acolyte", "Necromancer"),
]


# ---------------------------------------------------------------------------
# A. Resolve → DPS (all classes)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolve_to_dps(char_class, mastery):
    stats = quick_resolve(_build(char_class=char_class, mastery=mastery))
    result = calculate_dps(stats, "Fireball", 1)
    assert result.dps >= 0.0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolve_to_ehp(char_class, mastery):
    stats = quick_resolve(_build(char_class=char_class, mastery=mastery))
    ehp = calculate_ehp(stats)
    assert ehp > 0.0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolve_to_combat_sim(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = run_combat_simulation(b, _dummy_enemy(), iterations=30, seed=42)
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# B. Validate → export → import (all classes)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_validate_then_export_json(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    vr = validate_build(b)
    assert vr.valid
    js = export_to_json(b)
    r = import_build(js)
    assert r.success
    assert r.build["character_class"] == char_class


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_validate_then_export_fbs(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    fbs = export_to_fbs(b)
    r = import_build(fbs)
    assert r.success
    assert r.build["character_class"] == char_class


# ---------------------------------------------------------------------------
# C. Optimize → validate result
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_optimize_result_valid(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    result = optimize_build(b, iterations=5)
    assert isinstance(result.best_upgrade, dict)
    assert "stat" in result.best_upgrade


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_pareto_front_valid(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    result = pareto_front(b)
    assert isinstance(result, list)
    for item in result:
        assert "stat" in item
        assert "dps_gain_pct" in item
        assert "ehp_gain_pct" in item


# ---------------------------------------------------------------------------
# D. Craft simulation → result validity (all classes with same item)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_craft_simulation_class_independent(char_class, mastery):
    # Craft simulation doesn't need character class, but verify it integrates
    item = _craft_item(fp=30)
    r = simulate_crafting_path(
        item, [{"action": "add_affix", "affix": "Added Health"}],
        iterations=50, seed=42
    )
    assert 0.0 <= r.success_rate <= 1.0


# ---------------------------------------------------------------------------
# E. Stat pipeline → stat validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolved_stats_pass_range_validation(char_class, mastery):
    from app.engines.validators import validate_stat_ranges
    stats = quick_resolve(_build(char_class=char_class, mastery=mastery))
    from dataclasses import asdict
    d = asdict(stats)
    result = validate_stat_ranges(d)
    # No stat_negative errors (all non-negative stats should be >= 0)
    stat_neg_errors = [e for e in result.errors if e.code == "STAT_NEGATIVE"]
    assert len(stat_neg_errors) == 0


# ---------------------------------------------------------------------------
# F. Full pipeline: resolve → optimize → export → import
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_full_pipeline(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    # 1. Validate
    vr = validate_build(b)
    assert vr.valid
    # 2. Optimize
    opt = optimize_build(b, iterations=3)
    assert opt.score is not None
    # 3. Export
    fbs = export_to_fbs(b)
    # 4. Import
    r = import_build(fbs)
    assert r.success


# ---------------------------------------------------------------------------
# G. Gear with affixes — pipeline
# ---------------------------------------------------------------------------

_GEAR_CONFIGS = [
    [],
    [{"slot_type": "helmet", "forging_potential": 10,
      "affixes": [{"name": "Added Health", "tier": 1}]}],
    [{"slot_type": "boots", "forging_potential": 15,
      "affixes": [{"name": "Increased Spell Damage", "tier": 2}]}],
    [{"slot_type": "helmet", "forging_potential": 10, "affixes": []},
     {"slot_type": "boots", "forging_potential": 12, "affixes": []}],
]


@pytest.mark.parametrize("gear", _GEAR_CONFIGS)
def test_gear_config_resolves(gear):
    b = _build(gear=gear)
    stats = quick_resolve(b)
    assert stats.max_health > 0


@pytest.mark.parametrize("gear", _GEAR_CONFIGS)
def test_gear_config_exports(gear):
    b = _build(gear=gear)
    js = export_to_json(b)
    r = import_build(js)
    assert r.success


@pytest.mark.parametrize("gear", _GEAR_CONFIGS)
def test_gear_config_validates(gear):
    b = _build(gear=gear)
    r = validate_build(b)
    # No class/mastery/passive errors (gear may have FP warnings)
    class_errors = [e for e in r.errors if "CLASS" in e.code or "PASSIVE" in e.code]
    assert len(class_errors) == 0


# ---------------------------------------------------------------------------
# H. Passive tree sizes — pipeline
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_nodes", [0, 1, 5, 10, 20, 50])
def test_passive_tree_sizes_resolve(n_nodes):
    b = _build(passive_tree=list(range(n_nodes)))
    stats = quick_resolve(b)
    assert stats.max_health > 0


@pytest.mark.parametrize("n_nodes", [0, 5, 20, 50])
def test_passive_tree_sizes_validate(n_nodes):
    b = _build(passive_tree=list(range(n_nodes)))
    r = validate_build(b)
    overflow = [e for e in r.errors if e.code == "PASSIVE_OVERFLOW"]
    if n_nodes <= 113:
        assert len(overflow) == 0


@pytest.mark.parametrize("n_nodes", [0, 5, 20])
def test_passive_tree_sizes_export(n_nodes):
    b = _build(passive_tree=list(range(n_nodes)))
    sb = export_build(b)
    assert len(sb.passive_tree) == n_nodes


# ---------------------------------------------------------------------------
# I. Serialization idempotency
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_double_export_import_idempotent(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    # First round trip
    r1 = import_build(export_to_json(b))
    assert r1.success
    # Second round trip from imported build
    r2 = import_build(export_to_json(r1.build))
    assert r2.success
    assert r2.build["character_class"] == char_class


# ---------------------------------------------------------------------------
# J. Combat simulator with resolved stats
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolved_stats_in_combat_sim(char_class, mastery):
    stats = quick_resolve(_build(char_class=char_class, mastery=mastery))
    r = run_combat_simulation(stats, _dummy_enemy(), iterations=30, seed=42)
    assert r.average_dps >= 0.0
    assert 0.0 <= r.death_rate <= 1.0


# ---------------------------------------------------------------------------
# K. Optimizer with resolved stats
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_resolved_stats_in_optimizer(char_class, mastery):
    stats = quick_resolve(_build(char_class=char_class, mastery=mastery))
    r = optimize_build(stats, iterations=3)
    assert isinstance(r.best_upgrade, dict)
    assert r.score is not None


# ---------------------------------------------------------------------------
# L. Build serializer round-trip preserves all key fields
# ---------------------------------------------------------------------------

_SKILLS = ["Fireball", "Frostbolt", "Lightning Blast", "Hammer Throw", "Maelstrom"]

@pytest.mark.parametrize("skill", _SKILLS)
@pytest.mark.parametrize("char_class,mastery", _CLASSES[:5])
def test_skill_class_round_trip(skill, char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery, primary_skill=skill)
    r = import_build(export_to_fbs(b))
    assert r.success
    assert r.build["character_class"] == char_class
    assert r.build["primary_skill"] == skill
