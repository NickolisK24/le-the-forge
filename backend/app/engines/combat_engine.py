"""
Combat Engine — DPS calculation and Monte Carlo combat simulation.

Mirrors the logic in frontend/src/lib/simulation.ts:calculateSkillDPS().

Formulas (Last Epoch modifier stacking):
  IncreasedDmg = sum of all "increased" % bonuses (additive pool)
  MoreDmg      = product of all "more" multipliers (multiplicative pool)
  HitDamage    = BaseDamage * (1 + IncreasedDmg/100) * MoreDmg
  AverageHit   = (1 - CritChance) * HitDamage + CritChance * HitDamage * CritMultiplier
  DPS          = AverageHit * EffectiveAttackSpeed

Pure module — no DB, no HTTP.
"""

import random
from dataclasses import dataclass, asdict
from typing import Optional

from app.constants.combat import (
    BLEED_BASE_RATIO,
    BLEED_DURATION,
    IGNITE_DPS_RATIO,
    IGNITE_DURATION,
    POISON_DPS_RATIO,
    POISON_DURATION,
    CRIT_CHANCE_CAP,
)
from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)
from app.game_data.game_data_loader import get_enemy_profile


# ---------------------------------------------------------------------------
# Skill stat definitions — mirrors SKILL_STATS in frontend/src/lib/gameData.ts
# Only the fields used by the calculation are stored here.
# ---------------------------------------------------------------------------

@dataclass
class SkillStatDef:
    base_damage: float
    level_scaling: float    # damage multiplier per level above 1
    attack_speed: float     # base casts/attacks per second
    scaling_stats: list     # list of BuildStats field names for % damage bonus
    is_spell: bool = False
    is_melee: bool = False
    is_throwing: bool = False
    is_bow: bool = False


SKILL_STATS: dict = {
    # --- Acolyte ---
    "Rip Blood":              SkillStatDef(80,  0.12, 1.8, ["spell_damage_pct"], is_spell=True),
    "Bone Curse":             SkillStatDef(60,  0.10, 1.2, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Hungering Souls":        SkillStatDef(90,  0.13, 1.5, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Harvest":                SkillStatDef(100, 0.14, 1.0, ["spell_damage_pct"], is_spell=True, is_melee=True),
    "Reaper Form":            SkillStatDef(120, 0.15, 1.4, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Death Seal":             SkillStatDef(150, 0.14, 0.4, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Drain Life":             SkillStatDef(45,  0.09, 1.0, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Chthonic Fissure":       SkillStatDef(150, 0.14, 0.8, ["spell_damage_pct", "void_damage_pct"], is_spell=True),
    "Chaos Bolts":            SkillStatDef(100, 0.12, 1.8, ["spell_damage_pct", "fire_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Summon Skeleton":        SkillStatDef(60,  0.10, 1.0, ["minion_damage_pct"]),
    "Summon Bone Golem":      SkillStatDef(120, 0.12, 0.8, ["minion_damage_pct"]),
    "Wandering Spirits":      SkillStatDef(50,  0.09, 0.8, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Infernal Shade":         SkillStatDef(40,  0.08, 0.5, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Marrow Shards":          SkillStatDef(70,  0.11, 2.0, ["spell_damage_pct"], is_spell=True),
    "Transplant":             SkillStatDef(40,  0.08, 0.5, ["spell_damage_pct"], is_spell=True),
    "Mark for Death":         SkillStatDef(20,  0.06, 0.4, ["necrotic_damage_pct"], is_spell=True),
    "Spirit Plague":          SkillStatDef(30,  0.08, 0.5, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Summon Volatile Zombie": SkillStatDef(200, 0.15, 0.3, ["minion_damage_pct", "fire_damage_pct"]),
    "Summon Skeletal Mage":   SkillStatDef(80,  0.11, 1.0, ["minion_damage_pct", "necrotic_damage_pct"]),
    "Dread Shade":            SkillStatDef(35,  0.08, 0.5, ["minion_damage_pct", "necrotic_damage_pct"]),
    "Assemble Abomination":   SkillStatDef(180, 0.14, 0.5, ["minion_damage_pct"]),
    "Summon Wraith":          SkillStatDef(70,  0.10, 1.2, ["minion_damage_pct", "necrotic_damage_pct"]),
    "Aura of Decay":          SkillStatDef(25,  0.07, 0.5, ["poison_damage_pct"], is_spell=True),
    "Soul Feast":             SkillStatDef(80,  0.11, 1.2, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Profane Veil":           SkillStatDef(30,  0.07, 0.4, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    # --- Mage ---
    "Glacier":                SkillStatDef(120, 0.13, 0.9, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Fireball":               SkillStatDef(110, 0.12, 1.2, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Lightning Blast":        SkillStatDef(95,  0.11, 1.5, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Mana Strike":            SkillStatDef(80,  0.10, 2.0, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True, is_melee=True),
    "Teleport":               SkillStatDef(50,  0.09, 0.5, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Surge":                  SkillStatDef(90,  0.11, 1.6, ["lightning_damage_pct"], is_melee=True),
    "Frost Claw":             SkillStatDef(85,  0.11, 1.8, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Static Orb":             SkillStatDef(100, 0.12, 1.0, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Volcanic Orb":           SkillStatDef(130, 0.13, 0.8, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Disintegrate":           SkillStatDef(60,  0.09, 1.0, ["spell_damage_pct", "fire_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Shatter Strike":         SkillStatDef(130, 0.12, 1.3, ["spell_damage_pct", "cold_damage_pct"], is_melee=True),
    "Meteor":                 SkillStatDef(300, 0.16, 0.4, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Nova":                   SkillStatDef(180, 0.14, 0.7, ["spell_damage_pct", "cold_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Snap Freeze":            SkillStatDef(160, 0.14, 0.7, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Rune of Winter":         SkillStatDef(140, 0.13, 0.9, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Runic Invocation":       SkillStatDef(200, 0.15, 0.6, ["spell_damage_pct", "cold_damage_pct", "fire_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Runic Bolt":             SkillStatDef(90,  0.11, 1.6, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Flame Ward":             SkillStatDef(50,  0.08, 0.3, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Enchant Weapon":         SkillStatDef(80,  0.10, 1.0, ["fire_damage_pct"], is_spell=True),
    # --- Primalist ---
    "Summon Wolf":            SkillStatDef(75,  0.10, 1.5, ["minion_damage_pct", "physical_damage_pct"]),
    "Warcry":                 SkillStatDef(30,  0.06, 0.3, ["physical_damage_pct"]),
    "Entangling Roots":       SkillStatDef(40,  0.08, 0.5, ["spell_damage_pct"], is_spell=True),
    "Fury Leap":              SkillStatDef(90,  0.11, 0.5, ["physical_damage_pct"], is_melee=True),
    "Maelstrom":              SkillStatDef(55,  0.09, 0.8, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Avalanche":              SkillStatDef(180, 0.14, 0.5, ["spell_damage_pct", "physical_damage_pct", "cold_damage_pct"], is_spell=True),
    "Ice Thorns":             SkillStatDef(65,  0.10, 1.2, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Tornado":                SkillStatDef(65,  0.10, 0.6, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Serpent Strike":         SkillStatDef(70,  0.11, 2.2, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Gathering Storm":        SkillStatDef(45,  0.08, 0.5, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Werebear Form":          SkillStatDef(130, 0.13, 1.3, ["physical_damage_pct", "cold_damage_pct"], is_melee=True),
    "Spriggan Form":          SkillStatDef(80,  0.10, 1.0, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Swipe":                  SkillStatDef(110, 0.12, 1.4, ["physical_damage_pct"], is_melee=True),
    "Thorn Totem":            SkillStatDef(55,  0.09, 1.0, ["minion_damage_pct", "physical_damage_pct", "poison_damage_pct"]),
    "Summon Raptor":          SkillStatDef(90,  0.11, 1.8, ["minion_damage_pct", "physical_damage_pct"]),
    "Summon Bear":            SkillStatDef(150, 0.13, 0.9, ["minion_damage_pct"]),
    "Summon Sabertooth":      SkillStatDef(110, 0.12, 1.5, ["minion_damage_pct", "physical_damage_pct"]),
    "Earthquake":             SkillStatDef(250, 0.15, 0.4, ["spell_damage_pct", "physical_damage_pct"], is_spell=True),
    "Vessel of Chaos":        SkillStatDef(100, 0.12, 0.5, ["minion_damage_pct"]),
    # --- Sentinel ---
    "Lunge":                  SkillStatDef(80,  0.11, 0.8, ["physical_damage_pct"], is_melee=True),
    "Rive":                   SkillStatDef(100, 0.12, 1.8, ["physical_damage_pct"], is_melee=True),
    "Warpath":                SkillStatDef(85,  0.11, 1.5, ["physical_damage_pct"], is_melee=True),
    "Shield Rush":            SkillStatDef(70,  0.10, 0.7, ["physical_damage_pct"], is_melee=True),
    "Javelin":                SkillStatDef(130, 0.12, 1.4, ["physical_damage_pct", "lightning_damage_pct"], is_throwing=True),
    "Smite":                  SkillStatDef(120, 0.13, 1.2, ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], is_spell=True, is_melee=True),
    "Smelter's Wrath":        SkillStatDef(110, 0.12, 1.2, ["fire_damage_pct"], is_melee=True),
    "Manifest Armor":         SkillStatDef(80,  0.10, 0.8, ["minion_damage_pct"]),
    "Forge Strike":           SkillStatDef(140, 0.13, 1.0, ["fire_damage_pct", "physical_damage_pct"], is_melee=True),
    "Shield Throw":           SkillStatDef(110, 0.12, 1.5, ["physical_damage_pct"], is_throwing=True),
    "Volatile Reversal":      SkillStatDef(100, 0.12, 0.6, ["void_damage_pct"], is_spell=True),
    "Judgement":              SkillStatDef(200, 0.15, 0.6, ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], is_spell=True),
    "Anomaly":                SkillStatDef(160, 0.14, 0.5, ["spell_damage_pct", "void_damage_pct"], is_spell=True),
    "Devouring Orb":          SkillStatDef(100, 0.12, 1.0, ["spell_damage_pct", "void_damage_pct"], is_spell=True),
    "Erasing Strike":         SkillStatDef(180, 0.14, 0.9, ["void_damage_pct"], is_melee=True),
    "Void Cleave":            SkillStatDef(160, 0.13, 1.1, ["void_damage_pct"], is_melee=True),
    # --- Rogue ---
    "Shift":                  SkillStatDef(50,  0.08, 0.5, ["physical_damage_pct"], is_spell=True),
    "Flurry":                 SkillStatDef(65,  0.10, 3.0, ["physical_damage_pct"], is_melee=True),
    "Puncture":               SkillStatDef(80,  0.11, 2.0, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Acid Flask":             SkillStatDef(35,  0.07, 0.6, ["poison_damage_pct"], is_throwing=True),
    "Arrow Barrage":          SkillStatDef(70,  0.10, 2.5, ["physical_damage_pct"], is_bow=True),
    "Detonating Arrow":       SkillStatDef(130, 0.13, 1.2, ["fire_damage_pct", "physical_damage_pct"], is_bow=True),
    "Explosive Trap":         SkillStatDef(120, 0.12, 0.5, ["fire_damage_pct"]),
    "Shurikens":              SkillStatDef(55,  0.09, 3.5, ["physical_damage_pct"], is_throwing=True),
    "Shadow Cascade":         SkillStatDef(120, 0.13, 1.6, ["physical_damage_pct", "void_damage_pct"], is_melee=True),
    "Dancing Strikes":        SkillStatDef(90,  0.11, 2.5, ["physical_damage_pct"], is_melee=True),
    "Blade Flurry":           SkillStatDef(100, 0.12, 2.2, ["physical_damage_pct"], is_melee=True),
    "Synchronized Strike":    SkillStatDef(150, 0.13, 0.8, ["physical_damage_pct", "void_damage_pct"], is_melee=True),
    "Multishot":              SkillStatDef(85,  0.11, 1.8, ["physical_damage_pct"], is_bow=True),
    "Ballista":               SkillStatDef(70,  0.10, 2.0, ["minion_damage_pct", "physical_damage_pct"], is_bow=True),
    "Rain of Arrows":         SkillStatDef(45,  0.08, 0.8, ["physical_damage_pct"], is_bow=True),
    "Hail of Arrows":         SkillStatDef(60,  0.09, 1.0, ["physical_damage_pct", "cold_damage_pct"], is_bow=True),
    "Falcon Strikes":         SkillStatDef(90,  0.11, 2.0, ["minion_damage_pct", "physical_damage_pct"]),
    "Aerial Assault":         SkillStatDef(130, 0.13, 0.6, ["minion_damage_pct", "physical_damage_pct"]),
    "Dive Bomb":              SkillStatDef(200, 0.15, 0.4, ["minion_damage_pct", "physical_damage_pct"]),
    # --- Cross-class / missing skills ---
    "Scorpion Aspect":        SkillStatDef(95,  0.11, 1.6, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Ring of Shields":        SkillStatDef(60,  0.09, 0.4, ["physical_damage_pct"]),
    "Healing Hands":          SkillStatDef(40,  0.08, 0.8, ["spell_damage_pct"], is_spell=True),
    "Smoke Bomb":             SkillStatDef(45,  0.08, 0.5, ["physical_damage_pct", "poison_damage_pct"]),
}


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class DPSResult:
    hit_damage: int
    average_hit: int
    dps: int
    effective_attack_speed: float
    crit_contribution_pct: int
    # Flat added damage breakdown
    flat_damage_added: int = 0
    # Ailment DPS
    bleed_dps: int = 0
    ignite_dps: int = 0
    poison_dps: int = 0
    ailment_dps: int = 0
    total_dps: int = 0      # hit dps + ailment dps

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MonteCarloDPS:
    mean_dps: int
    min_dps: int
    max_dps: int
    std_dev: float
    percentile_25: int
    percentile_75: int
    n_simulations: int

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Skill lookup — registry-first, SKILL_STATS fallback
# ---------------------------------------------------------------------------

def _get_skill_def(skill_name: str) -> SkillStatDef | None:
    """
    Look up a SkillStatDef by name.

    Checks the app-context SkillRegistry first (populated at startup from
    skills.json). Falls back to the hardcoded SKILL_STATS dict so the engine
    continues to work in test contexts that don't go through create_app().
    """
    try:
        from flask import current_app
        registry = current_app.extensions.get("skill_registry")
        if registry is not None and skill_name in registry:
            return registry.get(skill_name)
    except RuntimeError:
        pass
    return SKILL_STATS.get(skill_name)


# Elemental stat keys — used to detect elemental skills for elemental_damage_pct
_ELEMENTAL_STATS = frozenset({"fire_damage_pct", "cold_damage_pct", "lightning_damage_pct"})


# ---------------------------------------------------------------------------
# Helpers — flat added damage and ailment calculation
# ---------------------------------------------------------------------------

def _sum_flat_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """Sum all flat added damage relevant to a skill's type."""
    total = 0.0
    if skill_def.is_spell:
        total += (stats.added_spell_damage + stats.added_spell_fire +
                  stats.added_spell_cold + stats.added_spell_lightning +
                  stats.added_spell_necrotic + stats.added_spell_void)
    if skill_def.is_melee:
        total += (stats.added_melee_physical + stats.added_melee_fire +
                  stats.added_melee_cold + stats.added_melee_lightning +
                  stats.added_melee_void + stats.added_melee_necrotic)
    if skill_def.is_throwing:
        total += (stats.added_throw_physical + stats.added_throw_fire +
                  stats.added_throw_cold)
    if skill_def.is_bow:
        total += stats.added_bow_physical + stats.added_bow_fire
    return total


def _sum_increased_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """Sum all % increased damage bonuses for a skill, including implicit type bonuses."""
    total = sum(getattr(stats, k, 0.0) for k in skill_def.scaling_stats)

    # Weapon-type % bonuses (additive with other increased damage)
    if skill_def.is_melee:
        total += stats.melee_damage_pct
    if skill_def.is_throwing:
        total += stats.throwing_damage_pct
    if skill_def.is_bow:
        total += stats.bow_damage_pct

    # Elemental damage bonus applies if skill scales with any elemental stat
    if _ELEMENTAL_STATS.intersection(skill_def.scaling_stats):
        total += stats.elemental_damage_pct

    return total


def _calc_ailment_dps(
    hit_damage: float,
    effective_as: float,
    stats: BuildStats,
) -> tuple[int, int, int]:
    """
    Calculate per-ailment DPS from proc chance, base hit, and DoT scaling.

    Returns (bleed_dps, ignite_dps, poison_dps).
    """
    bleed_dps = ignite_dps = poison_dps = 0

    # Bleed: physical DoT
    if stats.bleed_chance_pct > 0:
        chance = min(1.0, stats.bleed_chance_pct / 100)
        base_per_stack = hit_damage * BLEED_BASE_RATIO / BLEED_DURATION
        maintained = effective_as * chance * BLEED_DURATION
        increased = 1 + (stats.physical_damage_pct + stats.dot_damage_pct +
                         stats.bleed_damage_pct) / 100
        bleed_dps = round(base_per_stack * maintained * increased)

    # Ignite: fire DoT
    if stats.ignite_chance_pct > 0:
        chance = min(1.0, stats.ignite_chance_pct / 100)
        base_per_stack = hit_damage * IGNITE_DPS_RATIO
        maintained = effective_as * chance * IGNITE_DURATION
        increased = 1 + (stats.fire_damage_pct + stats.dot_damage_pct +
                         stats.ignite_damage_pct) / 100
        ignite_dps = round(base_per_stack * maintained * increased)

    # Poison: poison DoT
    if stats.poison_chance_pct > 0:
        chance = min(1.0, stats.poison_chance_pct / 100)
        base_per_stack = hit_damage * POISON_DPS_RATIO
        maintained = effective_as * chance * POISON_DURATION
        increased = 1 + (stats.poison_damage_pct + stats.dot_damage_pct +
                         stats.poison_dot_damage_pct) / 100
        poison_dps = round(base_per_stack * maintained * increased)

    return bleed_dps, ignite_dps, poison_dps


# ---------------------------------------------------------------------------
# DPS calculation
# ---------------------------------------------------------------------------

def calculate_dps(
    stats: BuildStats,
    skill_name: str,
    skill_level: int = 20,
    skill_modifiers: dict | None = None,
) -> DPSResult:
    """
    Calculate expected DPS for a skill at a given level using build stats.

    Includes flat added damage, weapon-type bonuses, ailment/DoT DPS, and
    optional skill_modifiers from the spec tree resolver:
        more_damage_pct     — extra "more" multiplier (multiplicative)
        added_hits_per_cast — additional projectiles / chains
        attack_speed_pct    — skill-specific attack speed bonus
        cast_speed_pct      — skill-specific cast speed bonus
        crit_chance_pct     — skill-specific crit chance bonus
        crit_multiplier_pct — skill-specific crit multiplier bonus
    """
    log.debug("calculate_dps", skill=skill_name, skill_level=skill_level)

    skill_def = _get_skill_def(skill_name)
    if not skill_def:
        log.warning("calculate_dps.unknown_skill", skill=skill_name)
        return DPSResult(0, 0, 0, 1.0, 0)

    sm = skill_modifiers or {}

    # Base damage scaled by level
    scaled_base = skill_def.base_damage * (1 + skill_def.level_scaling * (skill_level - 1))

    # Flat added damage from gear
    flat_added = _sum_flat_damage(stats, skill_def)
    effective_base = scaled_base + flat_added

    # Sum all "increased" % damage bonuses (additive pool)
    total_damage_pct = _sum_increased_damage(stats, skill_def)

    # "More" damage multiplier: product of base stats multiplier and spec-tree more%
    more_mult = stats.more_damage_multiplier * (1 + sm.get("more_damage_pct", 0.0) / 100)

    # HitDamage = EffectiveBase * (1 + IncreasedDamage%) * MoreDamage
    hit_damage = effective_base * (1 + total_damage_pct / 100) * more_mult

    # Crit chance and multiplier (base + spec tree bonuses)
    effective_crit_chance = min(CRIT_CHANCE_CAP, stats.crit_chance + sm.get("crit_chance_pct", 0.0) / 100)
    effective_crit_mult = stats.crit_multiplier + sm.get("crit_multiplier_pct", 0.0) / 100

    # AverageHit = non-crit portion + crit portion
    non_crit = (1 - effective_crit_chance) * hit_damage
    crit_hit = effective_crit_chance * hit_damage * effective_crit_mult
    average_hit = non_crit + crit_hit

    # Effective attack speed (base + build stats + spec tree bonuses)
    cast_speed_bonus = (stats.cast_speed + sm.get("cast_speed_pct", 0.0)) / 100 if skill_def.is_spell else 0.0
    attack_speed_bonus = (stats.attack_speed_pct + sm.get("attack_speed_pct", 0.0)) / 100 if not skill_def.is_spell else 0.0
    throw_speed_bonus = stats.throwing_attack_speed / 100 if skill_def.is_throwing else 0.0
    effective_as = skill_def.attack_speed * (1 + cast_speed_bonus + attack_speed_bonus + throw_speed_bonus)

    # Hits per cast: base 1 + spec tree extra projectiles/chains
    hits_per_cast = max(1, 1 + sm.get("added_hits_per_cast", 0))

    hit_dps = average_hit * effective_as * hits_per_cast
    crit_contrib = round((crit_hit * effective_as * hits_per_cast) / hit_dps * 100) if hit_dps > 0 else 0

    # Ailment DPS
    bleed_dps, ignite_dps, poison_dps = _calc_ailment_dps(hit_damage, effective_as, stats)
    ailment_total = bleed_dps + ignite_dps + poison_dps

    return DPSResult(
        hit_damage=round(hit_damage),
        average_hit=round(average_hit),
        dps=round(hit_dps),
        effective_attack_speed=round(effective_as * 100) / 100,
        crit_contribution_pct=crit_contrib,
        flat_damage_added=round(flat_added),
        bleed_dps=bleed_dps,
        ignite_dps=ignite_dps,
        poison_dps=poison_dps,
        ailment_dps=ailment_total,
        total_dps=round(hit_dps) + ailment_total,
    )


# ---------------------------------------------------------------------------
# Monte Carlo DPS simulation
# ---------------------------------------------------------------------------

def monte_carlo_dps(
    stats: BuildStats,
    skill_name: str,
    skill_level: int = 20,
    n: int = 10_000,
    seed: Optional[int] = None,
    skill_modifiers: dict | None = None,
) -> MonteCarloDPS:
    """
    Simulate n attacks and measure DPS variance from random crit outcomes.

    Each attack independently rolls whether it crits. This captures the
    variance in short burst windows even if mean DPS is the same.

    Pass ``seed`` for a fully reproducible run — useful for regression tests
    and deterministic comparison between build variants.
    """
    log.info(
        "monte_carlo_dps.start",
        skill=skill_name,
        skill_level=skill_level,
        n=n,
        seed=seed,
    )

    skill_def = _get_skill_def(skill_name)
    if not skill_def:
        log.warning("monte_carlo_dps.unknown_skill", skill=skill_name)
        return MonteCarloDPS(0, 0, 0, 0.0, 0, 0, n)

    rng = random.Random(seed)
    sm = skill_modifiers or {}

    scaled_base = skill_def.base_damage * (1 + skill_def.level_scaling * (skill_level - 1))
    flat_added = _sum_flat_damage(stats, skill_def)
    effective_base = scaled_base + flat_added

    total_pct = _sum_increased_damage(stats, skill_def)
    more_mult = stats.more_damage_multiplier * (1 + sm.get("more_damage_pct", 0.0) / 100)
    hit_damage = effective_base * (1 + total_pct / 100) * more_mult

    effective_crit_chance = min(CRIT_CHANCE_CAP, stats.crit_chance + sm.get("crit_chance_pct", 0.0) / 100)
    effective_crit_mult = stats.crit_multiplier + sm.get("crit_multiplier_pct", 0.0) / 100
    hits_per_cast = max(1, 1 + sm.get("added_hits_per_cast", 0))

    cast_speed_bonus = (stats.cast_speed + sm.get("cast_speed_pct", 0.0)) / 100 if skill_def.is_spell else 0.0
    attack_speed_bonus = (stats.attack_speed_pct + sm.get("attack_speed_pct", 0.0)) / 100 if not skill_def.is_spell else 0.0
    throw_speed_bonus = stats.throwing_attack_speed / 100 if skill_def.is_throwing else 0.0
    effective_as = skill_def.attack_speed * (1 + cast_speed_bonus + attack_speed_bonus + throw_speed_bonus)

    damages = []
    for _ in range(n):
        if rng.random() < effective_crit_chance:
            dmg = hit_damage * effective_crit_mult
        else:
            dmg = hit_damage
        damages.append(dmg * effective_as * hits_per_cast)

    damages.sort()
    mean = sum(damages) / n
    variance = sum((d - mean) ** 2 for d in damages) / n
    std = variance ** 0.5

    result = MonteCarloDPS(
        mean_dps=round(mean),
        min_dps=round(damages[0]),
        max_dps=round(damages[-1]),
        std_dev=round(std, 1),
        percentile_25=round(damages[n // 4]),
        percentile_75=round(damages[3 * n // 4]),
        n_simulations=n,
    )
    log.info("monte_carlo_dps.end", skill=skill_name, mean_dps=result.mean_dps, seed=seed)
    return result


# ---------------------------------------------------------------------------
# Enemy-aware DPS calculation
# ---------------------------------------------------------------------------

@dataclass
class EnemyAwareDPS:
    skill_name: str
    enemy_id: str
    raw_dps: int              # DPS vs Training Dummy (0 res, 0 armor)
    effective_dps: int        # DPS after enemy resistances and armor
    armor_reduction_pct: float
    avg_res_reduction_pct: float
    penetration_applied: dict

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_dps_vs_enemy(
    stats: BuildStats,
    skill_name: str,
    skill_level: int,
    enemy_id: str = "training_dummy",
) -> EnemyAwareDPS:
    """
    Calculates effective DPS against a specific enemy profile from enemy_profiles.json.

    Applies:
    - Enemy armor reduction formula: Mitigation = Armor / (Armor + 300)
    - Enemy resistances minus character penetration for matching damage types
    - Resistance cap at 75%

    Returns raw DPS (vs dummy) and effective DPS (vs enemy).
    """
    base_result = calculate_dps(stats, skill_name, skill_level)
    raw_dps = base_result.total_dps

    enemy = get_enemy_profile(enemy_id)
    if not enemy:
        return EnemyAwareDPS(
            skill_name=skill_name,
            enemy_id=enemy_id,
            raw_dps=raw_dps,
            effective_dps=raw_dps,
            armor_reduction_pct=0.0,
            avg_res_reduction_pct=0.0,
            penetration_applied={},
        )

    # Armor reduction
    armor = enemy["armor"]
    armor_mitigation = armor / (armor + 1000)

    # Penetration dict — maps BuildStats field → damage type id
    PENETRATION_MAP = {
        "physical_penetration": "physical",
        "fire_penetration": "fire",
        "cold_penetration": "cold",
        "lightning_penetration": "lightning",
        "void_penetration": "void",
        "necrotic_penetration": "necrotic",
    }

    # Resolve skill's primary damage type(s) from scaling_stats
    skill_def = _get_skill_def(skill_name)
    if not skill_def:
        return EnemyAwareDPS(skill_name, enemy_id, 0, 0, 0.0, 0.0, {})

    # Determine which damage types this skill deals
    skill_damage_types: set[str] = set()
    if "physical_damage_pct" in skill_def.scaling_stats or skill_def.is_melee:
        skill_damage_types.add("physical")
    for stat in skill_def.scaling_stats:
        for pen_stat, dmg_type in PENETRATION_MAP.items():
            if dmg_type + "_damage_pct" == stat:
                skill_damage_types.add(dmg_type)

    # Calculate effective resistance for each damage type the skill deals
    pen_applied: dict[str, float] = {}
    res_reductions: list[float] = []

    for dmg_type in (skill_damage_types or {"physical"}):
        enemy_res = enemy["resistances"].get(dmg_type, 0)
        pen_stat = dmg_type + "_penetration"
        pen = getattr(stats, pen_stat, 0.0)
        effective_res = max(0, min(75, enemy_res - pen))
        if pen > 0:
            pen_applied[dmg_type] = pen
        res_reductions.append(effective_res)

    avg_res = sum(res_reductions) / len(res_reductions) if res_reductions else 0.0

    # Apply both reductions multiplicatively
    effective_multiplier = (1 - armor_mitigation) * (1 - avg_res / 100)
    effective_dps = round(raw_dps * effective_multiplier)

    return EnemyAwareDPS(
        skill_name=skill_name,
        enemy_id=enemy_id,
        raw_dps=raw_dps,
        effective_dps=effective_dps,
        armor_reduction_pct=round(armor_mitigation * 100, 1),
        avg_res_reduction_pct=round(avg_res, 1),
        penetration_applied=pen_applied,
    )
