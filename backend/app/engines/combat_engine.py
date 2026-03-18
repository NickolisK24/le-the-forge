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

from app.engines.stat_engine import BuildStats


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
    "Javelin":                SkillStatDef(130, 0.12, 1.4, ["physical_damage_pct", "lightning_damage_pct"]),
    "Smite":                  SkillStatDef(120, 0.13, 1.2, ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], is_spell=True, is_melee=True),
    "Smelter's Wrath":        SkillStatDef(110, 0.12, 1.2, ["fire_damage_pct"], is_melee=True),
    "Manifest Armor":         SkillStatDef(80,  0.10, 0.8, ["minion_damage_pct"]),
    "Forge Strike":           SkillStatDef(140, 0.13, 1.0, ["fire_damage_pct", "physical_damage_pct"], is_melee=True),
    "Shield Throw":           SkillStatDef(110, 0.12, 1.5, ["physical_damage_pct"]),
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
    "Acid Flask":             SkillStatDef(35,  0.07, 0.6, ["poison_damage_pct"]),
    "Arrow Barrage":          SkillStatDef(70,  0.10, 2.5, ["physical_damage_pct"]),
    "Detonating Arrow":       SkillStatDef(130, 0.13, 1.2, ["fire_damage_pct", "physical_damage_pct"]),
    "Explosive Trap":         SkillStatDef(120, 0.12, 0.5, ["fire_damage_pct"]),
    "Shurikens":              SkillStatDef(55,  0.09, 3.5, ["physical_damage_pct"]),
    "Shadow Cascade":         SkillStatDef(120, 0.13, 1.6, ["physical_damage_pct", "void_damage_pct"], is_melee=True),
    "Dancing Strikes":        SkillStatDef(90,  0.11, 2.5, ["physical_damage_pct"], is_melee=True),
    "Blade Flurry":           SkillStatDef(100, 0.12, 2.2, ["physical_damage_pct"], is_melee=True),
    "Synchronized Strike":    SkillStatDef(150, 0.13, 0.8, ["physical_damage_pct", "void_damage_pct"], is_melee=True),
    "Multishot":              SkillStatDef(85,  0.11, 1.8, ["physical_damage_pct"]),
    "Ballista":               SkillStatDef(70,  0.10, 2.0, ["minion_damage_pct", "physical_damage_pct"]),
    "Rain of Arrows":         SkillStatDef(45,  0.08, 0.8, ["physical_damage_pct"]),
    "Hail of Arrows":         SkillStatDef(60,  0.09, 1.0, ["physical_damage_pct", "cold_damage_pct"]),
    "Falcon Strikes":         SkillStatDef(90,  0.11, 2.0, ["minion_damage_pct", "physical_damage_pct"]),
    "Aerial Assault":         SkillStatDef(130, 0.13, 0.6, ["minion_damage_pct", "physical_damage_pct"]),
    "Dive Bomb":              SkillStatDef(200, 0.15, 0.4, ["minion_damage_pct", "physical_damage_pct"]),
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
# DPS calculation
# ---------------------------------------------------------------------------

def calculate_dps(
    stats: BuildStats,
    skill_name: str,
    skill_level: int = 20,
) -> DPSResult:
    """
    Calculate expected DPS for a skill at a given level using build stats.

    Mirrors calculateSkillDPS() in frontend/src/lib/simulation.ts.
    """
    skill_def = SKILL_STATS.get(skill_name)
    if not skill_def:
        return DPSResult(0, 0, 0, 1.0, 0)

    # Base damage scaled by level
    scaled_base = skill_def.base_damage * (1 + skill_def.level_scaling * (skill_level - 1))

    # Sum all "increased" % damage bonuses relevant to this skill (additive pool)
    total_damage_pct = 0.0
    for stat_key in skill_def.scaling_stats:
        total_damage_pct += getattr(stats, stat_key, 0.0)

    # HitDamage = BaseDamage * (1 + IncreasedDamage%) * MoreDamage
    # "more" multipliers stack multiplicatively on top of the increased pool
    hit_damage = scaled_base * (1 + total_damage_pct / 100) * stats.more_damage_multiplier

    # AverageHit = non-crit portion + crit portion
    non_crit = (1 - stats.crit_chance) * hit_damage
    crit_hit = stats.crit_chance * hit_damage * stats.crit_multiplier
    average_hit = non_crit + crit_hit

    # Effective attack speed
    cast_speed_bonus = stats.cast_speed / 100 if skill_def.is_spell else 0.0
    attack_speed_bonus = stats.attack_speed_pct / 100 if not skill_def.is_spell else 0.0
    effective_as = skill_def.attack_speed * (1 + cast_speed_bonus + attack_speed_bonus)

    dps = average_hit * effective_as
    crit_contrib = round((crit_hit * effective_as) / dps * 100) if dps > 0 else 0

    return DPSResult(
        hit_damage=round(hit_damage),
        average_hit=round(average_hit),
        dps=round(dps),
        effective_attack_speed=round(effective_as * 100) / 100,
        crit_contribution_pct=crit_contrib,
    )


# ---------------------------------------------------------------------------
# Monte Carlo DPS simulation
# ---------------------------------------------------------------------------

def monte_carlo_dps(
    stats: BuildStats,
    skill_name: str,
    skill_level: int = 20,
    n: int = 10_000,
) -> MonteCarloDPS:
    """
    Simulate n attacks and measure DPS variance from random crit outcomes.

    Each attack independently rolls whether it crits. This captures the
    variance in short burst windows even if mean DPS is the same.
    """
    skill_def = SKILL_STATS.get(skill_name)
    if not skill_def:
        return MonteCarloDPS(0, 0, 0, 0.0, 0, 0, n)

    scaled_base = skill_def.base_damage * (1 + skill_def.level_scaling * (skill_level - 1))
    total_pct = sum(getattr(stats, k, 0.0) for k in skill_def.scaling_stats)
    hit_damage = scaled_base * (1 + total_pct / 100) * stats.more_damage_multiplier

    cast_speed_bonus = stats.cast_speed / 100 if skill_def.is_spell else 0.0
    attack_speed_bonus = stats.attack_speed_pct / 100 if not skill_def.is_spell else 0.0
    effective_as = skill_def.attack_speed * (1 + cast_speed_bonus + attack_speed_bonus)

    damages = []
    for _ in range(n):
        if random.random() < stats.crit_chance:
            dmg = hit_damage * stats.crit_multiplier
        else:
            dmg = hit_damage
        damages.append(dmg * effective_as)

    damages.sort()
    mean = sum(damages) / n
    variance = sum((d - mean) ** 2 for d in damages) / n
    std = variance ** 0.5

    return MonteCarloDPS(
        mean_dps=round(mean),
        min_dps=round(damages[0]),
        max_dps=round(damages[-1]),
        std_dev=round(std, 1),
        percentile_25=round(damages[n // 4]),
        percentile_75=round(damages[3 * n // 4]),
        n_simulations=n,
    )
