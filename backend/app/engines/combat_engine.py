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
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, asdict, field
from typing import Optional

from app.domain.skill import SkillStatDef
from app.domain.enemy import EnemyProfile
from app.domain.calculators.damage_type_router import damage_types_for_stats
from app.domain.calculators.skill_calculator import sum_flat_damage, scale_skill_damage, hits_per_cast
from app.domain.calculators.enemy_mitigation_calculator import (
    armor_mitigation,
    effective_resistance,
)
from app.domain.calculators.final_damage_calculator import DamageContext, calculate_final_damage
from app.domain.calculators.conversion_calculator import DamageConversion, apply_conversions
from app.domain.calculators.crit_calculator import (
    effective_crit_chance,
    effective_crit_multiplier,
    calculate_average_hit,
    crit_contribution_pct,
)
from app.domain.calculators.speed_calculator import effective_attack_speed
from app.domain.calculators.ailment_calculator import calc_ailment_dps
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats
from app.constants.combat import HIT_DAMAGE_VARIANCE

# Shorthand for hardcoded fallback entries in SKILL_STATS.
# data_version is required on SkillStatDef; "hardcoded" marks these as static
# definitions rather than values loaded from a versioned data file.
def _S(bd: float, ls: float, asp: float, ss: list, **kw) -> SkillStatDef:
    if "damage_types" not in kw:
        kw["damage_types"] = tuple(damage_types_for_stats(tuple(ss)))
    return SkillStatDef(bd, ls, asp, tuple(ss), data_version="hardcoded", **kw)
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)
from app.game_data.game_data_loader import get_enemy_profile


SKILL_STATS: dict = {
    # --- Acolyte ---
    "Rip Blood":              _S(80,  0.12, 1.8, ["spell_damage_pct"], is_spell=True),
    "Bone Curse":             _S(60,  0.10, 1.2, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Hungering Souls":        _S(90,  0.13, 1.5, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Harvest":                _S(100, 0.14, 1.0, ["spell_damage_pct"], is_spell=True, is_melee=True),
    "Reaper Form":            _S(120, 0.15, 1.4, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Death Seal":             _S(150, 0.14, 0.4, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Drain Life":             _S(45,  0.09, 1.0, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Chthonic Fissure":       _S(150, 0.14, 0.8, ["spell_damage_pct", "void_damage_pct"], is_spell=True),
    "Chaos Bolts":            _S(100, 0.12, 1.8, ["spell_damage_pct", "fire_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Summon Skeleton":        _S(60,  0.10, 1.0, ["minion_damage_pct"]),
    "Summon Bone Golem":      _S(120, 0.12, 0.8, ["minion_damage_pct"]),
    "Wandering Spirits":      _S(50,  0.09, 0.8, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Infernal Shade":         _S(40,  0.08, 0.5, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Marrow Shards":          _S(70,  0.11, 2.0, ["spell_damage_pct"], is_spell=True),
    "Transplant":             _S(40,  0.08, 0.5, ["spell_damage_pct"], is_spell=True),
    "Mark for Death":         _S(20,  0.06, 0.4, ["necrotic_damage_pct"], is_spell=True),
    "Spirit Plague":          _S(30,  0.08, 0.5, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Summon Volatile Zombie": _S(200, 0.15, 0.3, ["minion_damage_pct", "fire_damage_pct"]),
    "Summon Skeletal Mage":   _S(80,  0.11, 1.0, ["minion_damage_pct", "necrotic_damage_pct"]),
    "Dread Shade":            _S(35,  0.08, 0.5, ["minion_damage_pct", "necrotic_damage_pct"]),
    "Assemble Abomination":   _S(180, 0.14, 0.5, ["minion_damage_pct"]),
    "Summon Wraith":          _S(70,  0.10, 1.2, ["minion_damage_pct", "necrotic_damage_pct"]),
    "Aura of Decay":          _S(25,  0.07, 0.5, ["poison_damage_pct"], is_spell=True),
    "Soul Feast":             _S(80,  0.11, 1.2, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    "Profane Veil":           _S(30,  0.07, 0.4, ["spell_damage_pct", "necrotic_damage_pct"], is_spell=True),
    # --- Mage ---
    "Glacier":                _S(120, 0.13, 0.9, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Fireball":               _S(110, 0.12, 1.2, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Lightning Blast":        _S(95,  0.11, 1.5, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Mana Strike":            _S(80,  0.10, 2.0, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True, is_melee=True),
    "Teleport":               _S(50,  0.09, 0.5, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Surge":                  _S(90,  0.11, 1.6, ["lightning_damage_pct"], is_melee=True),
    "Frost Claw":             _S(85,  0.11, 1.8, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Static Orb":             _S(100, 0.12, 1.0, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Volcanic Orb":           _S(130, 0.13, 0.8, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Disintegrate":           _S(60,  0.09, 1.0, ["spell_damage_pct", "fire_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Shatter Strike":         _S(130, 0.12, 1.3, ["spell_damage_pct", "cold_damage_pct"], is_melee=True),
    # VERIFIED: 1.4.3 spec §6 — Meteor base damage 240 per hit, added damage effectiveness 1200%
    "Meteor":                 _S(240, 0.16, 0.4, ["spell_damage_pct", "fire_damage_pct"], is_spell=True, added_damage_effectiveness=12.0),
    "Nova":                   _S(180, 0.14, 0.7, ["spell_damage_pct", "cold_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Snap Freeze":            _S(160, 0.14, 0.7, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Rune of Winter":         _S(140, 0.13, 0.9, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Runic Invocation":       _S(200, 0.15, 0.6, ["spell_damage_pct", "cold_damage_pct", "fire_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Runic Bolt":             _S(90,  0.11, 1.6, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Flame Ward":             _S(50,  0.08, 0.3, ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Enchant Weapon":         _S(80,  0.10, 1.0, ["fire_damage_pct"], is_spell=True),
    # --- Primalist ---
    "Summon Wolf":            _S(75,  0.10, 1.5, ["minion_damage_pct", "physical_damage_pct"]),
    "Warcry":                 _S(30,  0.06, 0.3, ["physical_damage_pct"]),
    "Entangling Roots":       _S(40,  0.08, 0.5, ["spell_damage_pct"], is_spell=True),
    "Fury Leap":              _S(90,  0.11, 0.5, ["physical_damage_pct"], is_melee=True),
    "Maelstrom":              _S(55,  0.09, 0.8, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Avalanche":              _S(180, 0.14, 0.5, ["spell_damage_pct", "physical_damage_pct", "cold_damage_pct"], is_spell=True),
    "Ice Thorns":             _S(65,  0.10, 1.2, ["spell_damage_pct", "cold_damage_pct"], is_spell=True),
    "Tornado":                _S(65,  0.10, 0.6, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Serpent Strike":         _S(70,  0.11, 2.2, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Gathering Storm":        _S(45,  0.08, 0.5, ["spell_damage_pct", "lightning_damage_pct"], is_spell=True),
    "Werebear Form":          _S(130, 0.13, 1.3, ["physical_damage_pct", "cold_damage_pct"], is_melee=True),
    "Spriggan Form":          _S(80,  0.10, 1.0, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Swipe":                  _S(110, 0.12, 1.4, ["physical_damage_pct"], is_melee=True),
    "Thorn Totem":            _S(55,  0.09, 1.0, ["minion_damage_pct", "physical_damage_pct", "poison_damage_pct"]),
    "Summon Raptor":          _S(90,  0.11, 1.8, ["minion_damage_pct", "physical_damage_pct"]),
    "Summon Bear":            _S(150, 0.13, 0.9, ["minion_damage_pct"]),
    "Summon Sabertooth":      _S(110, 0.12, 1.5, ["minion_damage_pct", "physical_damage_pct"]),
    "Earthquake":             _S(250, 0.15, 0.4, ["spell_damage_pct", "physical_damage_pct"], is_spell=True),
    "Vessel of Chaos":        _S(100, 0.12, 0.5, ["minion_damage_pct"]),
    # --- Sentinel ---
    "Lunge":                  _S(80,  0.11, 0.8, ["physical_damage_pct"], is_melee=True),
    "Rive":                   _S(100, 0.12, 1.8, ["physical_damage_pct"], is_melee=True),
    "Warpath":                _S(85,  0.11, 1.5, ["physical_damage_pct"], is_melee=True),
    "Shield Rush":            _S(70,  0.10, 0.7, ["physical_damage_pct"], is_melee=True),
    "Javelin":                _S(130, 0.12, 1.4, ["physical_damage_pct", "lightning_damage_pct"], is_throwing=True),
    "Smite":                  _S(120, 0.13, 1.2, ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], is_spell=True, is_melee=True),
    "Smelter's Wrath":        _S(110, 0.12, 1.2, ["fire_damage_pct"], is_melee=True),
    "Manifest Armor":         _S(80,  0.10, 0.8, ["minion_damage_pct"]),
    "Forge Strike":           _S(140, 0.13, 1.0, ["fire_damage_pct", "physical_damage_pct"], is_melee=True),
    "Shield Throw":           _S(110, 0.12, 1.5, ["physical_damage_pct"], is_throwing=True),
    "Volatile Reversal":      _S(100, 0.12, 0.6, ["void_damage_pct"], is_spell=True),
    "Judgement":              _S(200, 0.15, 0.6, ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], is_spell=True),
    "Anomaly":                _S(160, 0.14, 0.5, ["spell_damage_pct", "void_damage_pct"], is_spell=True),
    "Devouring Orb":          _S(100, 0.12, 1.0, ["spell_damage_pct", "void_damage_pct"], is_spell=True),
    "Erasing Strike":         _S(180, 0.14, 0.9, ["void_damage_pct"], is_melee=True),
    "Void Cleave":            _S(160, 0.13, 1.1, ["void_damage_pct"], is_melee=True),
    # --- Rogue ---
    "Shift":                  _S(50,  0.08, 0.5, ["physical_damage_pct"], is_spell=True),
    "Flurry":                 _S(65,  0.10, 3.0, ["physical_damage_pct"], is_melee=True),
    "Puncture":               _S(80,  0.11, 2.0, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Acid Flask":             _S(35,  0.07, 0.6, ["poison_damage_pct"], is_throwing=True),
    "Arrow Barrage":          _S(70,  0.10, 2.5, ["physical_damage_pct"], is_bow=True),
    "Detonating Arrow":       _S(130, 0.13, 1.2, ["fire_damage_pct", "physical_damage_pct"], is_bow=True),
    "Explosive Trap":         _S(120, 0.12, 0.5, ["fire_damage_pct"]),
    "Shurikens":              _S(55,  0.09, 3.5, ["physical_damage_pct"], is_throwing=True),
    "Umbral Blades":          _S(80,  0.08, 1.33, ["physical_damage_pct"], is_throwing=True, hit_count=5, mana_cost=12),
    "Shadow Cascade":         _S(120, 0.13, 1.6, ["physical_damage_pct", "void_damage_pct"], is_melee=True),
    "Shadow Rend":            _S(120, 0.13, 0.8, ["physical_damage_pct"], is_melee=True, added_damage_effectiveness=5.0),
    "Dancing Strikes":        _S(90,  0.11, 2.5, ["physical_damage_pct"], is_melee=True),
    "Blade Flurry":           _S(100, 0.12, 2.2, ["physical_damage_pct"], is_melee=True),
    "Synchronized Strike":    _S(150, 0.13, 0.8, ["physical_damage_pct", "void_damage_pct"], is_melee=True),
    "Multishot":              _S(85,  0.11, 1.8, ["physical_damage_pct"], is_bow=True),
    "Ballista":               _S(70,  0.10, 2.0, ["minion_damage_pct", "physical_damage_pct"], is_bow=True),
    "Rain of Arrows":         _S(45,  0.08, 0.8, ["physical_damage_pct"], is_bow=True),
    "Hail of Arrows":         _S(60,  0.09, 1.0, ["physical_damage_pct", "cold_damage_pct"], is_bow=True),
    "Falcon Strikes":         _S(90,  0.11, 2.0, ["minion_damage_pct", "physical_damage_pct"]),
    "Aerial Assault":         _S(130, 0.13, 0.6, ["minion_damage_pct", "physical_damage_pct"]),
    "Dive Bomb":              _S(200, 0.15, 0.4, ["minion_damage_pct", "physical_damage_pct"]),
    # --- Cross-class / missing skills ---
    "Scorpion Aspect":        _S(95,  0.11, 1.6, ["physical_damage_pct", "poison_damage_pct"], is_melee=True),
    "Ring of Shields":        _S(60,  0.09, 0.4, ["physical_damage_pct"]),
    "Healing Hands":          _S(40,  0.08, 0.8, ["spell_damage_pct"], is_spell=True),
    "Smoke Bomb":             _S(45,  0.08, 0.5, ["physical_damage_pct", "poison_damage_pct"]),

    # --- Added skills (game data coverage completion) ---
    "Abyssal Echoes":         _S(120, 0.12, 1.43, ["void_damage_pct"], is_spell=True, mana_cost=35),
    "Arcane Ascendance":      _S(0,   0.00, 1.33, []),
    "Armblade Slash":         _S(80, 0.10, 1.33, ["physical_damage_pct"], is_melee=True),
    "Aura Of Decay":          _S(20,  0.06, 1.33, ["poison_damage_pct"]),
    "Banner Rush":            _S(0,   0.00, 1.0,  []),
    "Black Hole":             _S(160, 0.14, 0.8,  ["spell_damage_pct", "cold_damage_pct"], is_spell=True, mana_cost=35, added_damage_effectiveness=8.0),
    "Bladestorm":             _S(80,  0.10, 3.0,  ["physical_damage_pct"], is_throwing=True, added_damage_effectiveness=1.5),
    "Cinder Strike":          _S(75, 0.10, 1.28, ["fire_damage_pct"], is_melee=True),
    "Create Shadow":          _S(0,   0.00, 1.33, []),
    "Dark Quiver":            _S(0,   0.00, 1.33, []),
    "Decoy":                  _S(40, 0.07, 1.43, ["fire_damage_pct"], is_throwing=True),
    "Detonate Decoy":         _S(0,   0.00, 1.33, []),
    "Dive":                   _S(0,   0.00, 2.5,  ["physical_damage_pct"], is_melee=True),
    "Eterra's Blessing":      _S(0, 0.00, 1.33, ["spell_damage_pct"], is_spell=True),
    "Evade":                  _S(0,   0.00, 2.0,  []),
    "Familiar Rage":          _S(0,   0.00, 1.0,  ["spell_damage_pct"], is_spell=True),
    "Falconry":               _S(0,   0.00, 1.33, []),
    "Fire Shield":            _S(0,   0.00, 1.33, []),
    "Firebrand":              _S(75,  0.10, 1.5,  ["fire_damage_pct"], is_melee=True),
    "Flame Reave":            _S(100, 0.12, 1.4,  ["fire_damage_pct"], is_melee=True, mana_cost=26),
    "Flame Rush":             _S(60,  0.09, 0.5,  ["spell_damage_pct", "fire_damage_pct"], is_spell=True, mana_cost=22),
    "Flay":                   _S(110, 0.12, 1.0,  ["physical_damage_pct"], is_melee=True),
    "Focus":                  _S(0,   0.00, 1.33, []),
    "Frigid Tempest":         _S(70, 0.10, 2.0,  ["cold_damage_pct"], is_spell=True),
    "Frost Wall":             _S(40,  0.08, 0.7,  ["spell_damage_pct", "cold_damage_pct"], is_spell=True, mana_cost=35),
    "Ghostflame":             _S(25, 0.07, 5.0,  ["fire_damage_pct"], is_spell=True),
    "Glyph of Dominion":      _S(50,  0.09, 0.8,  ["spell_damage_pct", "lightning_damage_pct"], is_spell=True, mana_cost=30),
    "Hammer Throw":           _S(65, 0.09, 1.33, ["physical_damage_pct"], is_throwing=True),
    "Heartseeker":            _S(75, 0.10, 1.33, ["physical_damage_pct"], is_bow=True),
    "Holy Aura":              _S(0, 0.00, 1.33, ["spell_damage_pct"], is_spell=True),
    "Human Form":             _S(0, 0.00, 3.33, ["spell_damage_pct"], is_spell=True),
    "Ice Barrage":            _S(85,  0.11, 1.8,  ["spell_damage_pct", "cold_damage_pct"], is_spell=True, mana_cost=50),
    "Ice Ward":               _S(0,   0.00, 1.33, []),
    "Lethal Mirage":          _S(160, 0.14, 0.67, ["physical_damage_pct"], is_melee=True),
    "Mark For Death":         _S(0,   0.00, 1.33, []),
    "Maul":                   _S(45, 0.07, 4.0,  ["physical_damage_pct"], is_melee=True),
    "Multistrike":            _S(85, 0.10, 1.33, ["physical_damage_pct"], is_melee=True),
    "Net":                    _S(40, 0.07, 1.11, ["physical_damage_pct"], is_throwing=True),
    "Rampage":                _S(0,   0.00, 1.0,  ["physical_damage_pct"], is_melee=True),
    "Reap":                   _S(0,   0.00, 5.0,  ["necrotic_damage_pct"], is_melee=True),
    "Rebuke":                 _S(20, 0.07, 5.0,  ["spell_damage_pct"], is_spell=True),
    "Ring Of Shields":        _S(60,  0.09, 0.4,  ["physical_damage_pct"]),
    "Riposte":                _S(80, 0.10, 1.33, ["physical_damage_pct"], is_melee=True),
    "Roar":                   _S(0, 0.00, 1.33, ["spell_damage_pct"], is_spell=True),
    "Rune Bolt":              _S(0,   0.00, 1.33, []),
    "Runebolt":               _S(90,  0.11, 1.6,  ["spell_damage_pct", "fire_damage_pct"], is_spell=True),
    "Sacrifice":              _S(120, 0.12, 1.33, ["spell_damage_pct"], is_spell=True),
    "Shield Bash":            _S(95, 0.10, 1.33, ["physical_damage_pct"], is_melee=True),
    "Shocking Impact":        _S(150, 0.13, 0.5,  ["lightning_damage_pct"], is_spell=True),
    "Spirit Thorns":          _S(65, 0.09, 1.33, ["spell_damage_pct"], is_spell=True),
    "Static":                 _S(70,  0.10, 1.4,  ["spell_damage_pct", "lightning_damage_pct"], is_spell=True, mana_cost=15),
    "Summon Cryomancer":      _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Death Knight":    _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Forged Weapon":   _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Frenzy Totem":    _S(0,   0.00, 1.67, ["minion_damage_pct"]),
    "Summon Healing Totem":   _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Hive":            _S(0,   0.00, 1.67, ["minion_damage_pct"]),
    "Summon Pyromancer":      _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Scorpion":        _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Skeleton Rogue":  _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Spriggan":        _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Squirrel":        _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Storm Crows":     _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Storm Totem":     _S(0,   0.00, 1.67, ["minion_damage_pct"]),
    "Summon Thorn Totem":     _S(0,   0.00, 1.67, ["minion_damage_pct"]),
    "Summon Vine":            _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Summon Vines":           _S(0,   0.00, 1.33, ["minion_damage_pct"]),
    "Swarm Strike":           _S(85, 0.10, 1.25, ["physical_damage_pct"], is_melee=True),
    "Swarmblade Form":        _S(0,   0.00, 1.25, []),
    "Symbols of Hope":        _S(0, 0.00, 1.33, ["spell_damage_pct"], is_spell=True),
    "Tempest Strike":         _S(100, 0.12, 1.67, ["cold_damage_pct"], is_melee=True),
    "Thorn Shield":           _S(0, 0.00, 1.33, ["spell_damage_pct"], is_spell=True),
    "Upheaval":               _S(110, 0.12, 1.25, ["physical_damage_pct"], is_melee=True),
    "Vengeance":              _S(85, 0.10, 1.33, ["physical_damage_pct"], is_melee=True),
    "Wave of Death":          _S(80, 0.10, 1.33, ["necrotic_damage_pct"], is_spell=True),
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
    # Per-type damage amounts (post-increased, pre-crit) — string keys for JSON
    damage_by_type: dict = field(default_factory=dict)

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


# ---------------------------------------------------------------------------
# DPS calculation
# ---------------------------------------------------------------------------

def calculate_dps(
    stats: BuildStats,
    skill_name: str,
    skill_level: int = 20,
    skill_modifiers: SkillModifiers | None = None,
    conversions: list[DamageConversion] | None = None,
    *,
    debug: bool = False,
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

    sm = skill_modifiers or SkillModifiers()

    flat_added = sum_flat_damage(stats, skill_def)
    scaled = scale_skill_damage(skill_def.base_damage, skill_def.level_scaling, skill_level, skill_def.damage_types)
    scaled = apply_conversions(scaled, conversions or [])
    # sum(scaled.values()) == total for any non-empty damage_types (split then re-sum).
    # Fall back to inline formula only when damage_types is empty (pending data migration).
    scaled_total = sum(scaled.values()) if scaled else skill_def.base_damage * (1 + skill_def.level_scaling * (skill_level - 1))
    # VERIFIED: 1.4.3 spec §2.1 — flat added × effectiveness before summing
    effective_base = scaled_total + flat_added * skill_def.added_damage_effectiveness

    # Post-conversion damage types drive the increased-damage pool so that
    # e.g. a physical→cold converted skill scales with cold_damage_pct /
    # elemental_damage_pct rather than the static physical_damage_pct.
    post_conversion_types = set(scaled.keys())
    damage = calculate_final_damage(
        DamageContext.from_build(
            effective_base, stats, skill_def, sm.more_damage_pct,
            scaled=scaled,
            post_conversion_types=post_conversion_types,
        ),
        debug=debug,
    )
    hit_damage = damage.total

    eff_crit_chance = effective_crit_chance(stats.crit_chance, flat_bonus_pct=sm.crit_chance_pct, increased_pct=0.0)
    eff_crit_mult = effective_crit_multiplier(stats.crit_multiplier, sm.crit_multiplier_pct)
    average_hit = calculate_average_hit(hit_damage, eff_crit_chance, eff_crit_mult)

    effective_as = effective_attack_speed(skill_def, stats, sm)
    hpc = hits_per_cast(sm.added_hits_per_cast)

    hit_dps = average_hit * effective_as * hpc
    crit_contrib = crit_contribution_pct(hit_damage, eff_crit_chance, eff_crit_mult, average_hit)

    bleed_dps, ignite_dps, poison_dps = calc_ailment_dps(hit_damage, effective_as, stats)
    ailment_total = bleed_dps + ignite_dps + poison_dps

    # Convert DamageType-keyed dict to string-keyed for JSON serialization
    damage_by_type_str = {dt.value: v for dt, v in damage.damage_by_type.items()}

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
        damage_by_type=damage_by_type_str,
    )


# ---------------------------------------------------------------------------
# Monte Carlo DPS simulation
# ---------------------------------------------------------------------------

def _simulate_chunk(
    hit_damage: float,
    eff_crit_chance: float,
    eff_crit_mult: float,
    effective_as: float,
    hpc: float,
    n: int,
    seed: Optional[int],
) -> list:
    """
    Run n independent hit rolls and return per-hit DPS values.

    Module-level so it is picklable by ProcessPoolExecutor workers.
    Each call creates its own Random instance from seed, giving full
    isolation between chunks when running in parallel.

    Each hit rolls two independent random values:
      1. Hit damage variance: uniform in [1 - HIT_DAMAGE_VARIANCE, 1 + HIT_DAMAGE_VARIANCE]
         (VERIFIED: 1.4.3 spec §2.1 — ±25% on hit damage)
      2. Crit outcome: crit if rand() < eff_crit_chance
    """
    rng = random.Random(seed)
    # Pre-compute values used every iteration outside the loop.
    scale    = effective_as * hpc
    variance_low  = 1.0 - HIT_DAMAGE_VARIANCE  # 0.75
    variance_span = 2.0 * HIT_DAMAGE_VARIANCE  # 0.50
    # Cache bound method to skip attribute lookup on every call.
    rand = rng.random
    # Pre-allocate exact size — avoids the ~log2(n) capacity doublings that
    # [] + append triggers as the list grows.
    results = [0.0] * n
    for i in range(n):
        # Uniform ±HIT_DAMAGE_VARIANCE roll on the base hit damage
        roll = variance_low + variance_span * rand()
        base = hit_damage * roll
        if rand() < eff_crit_chance:
            base *= eff_crit_mult
        results[i] = base * scale
    return results


def monte_carlo_dps(
    stats: BuildStats,
    skill_name: str,
    skill_level: int = 20,
    n: int = 10_000,
    seed: Optional[int] = None,
    skill_modifiers: SkillModifiers | None = None,
    conversions: list[DamageConversion] | None = None,
    *,
    workers: int = 1,
    debug: bool = False,
) -> MonteCarloDPS:
    """
    Simulate n attacks and measure DPS variance from random crit outcomes.

    Each attack independently rolls whether it crits. This captures the
    variance in short burst windows even if mean DPS is the same.

    Pass ``seed`` for a fully reproducible run — useful for regression tests
    and deterministic comparison between build variants.

    workers (default 1): number of parallel processes. When > 1, n is split
    evenly across workers via ProcessPoolExecutor. Each worker receives a
    deterministic sub-seed derived from seed (seed+i) so that seeded runs
    are fully reproducible. Pass workers=None to auto-select based on CPU count.
    """
    if workers < 1:
        raise ValueError(f"monte_carlo_dps: workers must be >= 1, got {workers}")

    log.info(
        "monte_carlo_dps.start",
        skill=skill_name,
        skill_level=skill_level,
        n=n,
        seed=seed,
        workers=workers,
    )

    skill_def = _get_skill_def(skill_name)
    if not skill_def:
        log.warning("monte_carlo_dps.unknown_skill", skill=skill_name)
        return MonteCarloDPS(0, 0, 0, 0.0, 0, 0, n)

    sm = skill_modifiers or SkillModifiers()

    flat_added = sum_flat_damage(stats, skill_def)
    scaled = scale_skill_damage(skill_def.base_damage, skill_def.level_scaling, skill_level, skill_def.damage_types)
    scaled = apply_conversions(scaled, conversions or [])
    scaled_total = sum(scaled.values()) if scaled else skill_def.base_damage * (1 + skill_def.level_scaling * (skill_level - 1))
    # VERIFIED: 1.4.3 spec §2.1 — flat added × effectiveness before summing
    effective_base = scaled_total + flat_added * skill_def.added_damage_effectiveness

    # Post-conversion types drive the increased-damage pool (see calculate_dps).
    post_conversion_types = set(scaled.keys())
    damage = calculate_final_damage(
        DamageContext.from_build(
            effective_base, stats, skill_def, sm.more_damage_pct,
            scaled=scaled,
            post_conversion_types=post_conversion_types,
        ),
        debug=debug,
    )
    hit_damage = damage.total

    eff_crit_chance = effective_crit_chance(stats.crit_chance, flat_bonus_pct=sm.crit_chance_pct, increased_pct=0.0)
    eff_crit_mult = effective_crit_multiplier(stats.crit_multiplier, sm.crit_multiplier_pct)
    hpc = hits_per_cast(sm.added_hits_per_cast)
    effective_as = effective_attack_speed(skill_def, stats, sm)

    # VERIFIED: DoT DPS is deterministic — added after variance rolls
    bleed_dps, ignite_dps, poison_dps = calc_ailment_dps(hit_damage, effective_as, stats)
    ailment_total = bleed_dps + ignite_dps + poison_dps

    # Build per-worker (chunk_size, sub_seed) pairs.
    # Remainder hits go to the first (n % workers) workers.
    chunk_size = n // workers
    remainder  = n % workers
    chunk_args = [
        (
            hit_damage,
            eff_crit_chance,
            eff_crit_mult,
            effective_as,
            hpc,
            chunk_size + (1 if i < remainder else 0),
            (seed + i) if seed is not None else None,
        )
        for i in range(workers)
    ]

    if workers == 1:
        damages = _simulate_chunk(*chunk_args[0])
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_simulate_chunk, *args) for args in chunk_args]
            # Pre-allocate the full output buffer once; fill each chunk's
            # slice in place to avoid repeated copies from extend().
            damages = [0.0] * n
            offset = 0
            for f in futures:
                chunk = f.result()
                end = offset + len(chunk)
                damages[offset:end] = chunk
                offset = end

    # VERIFIED: DoT DPS is deterministic — added after variance rolls
    if ailment_total:
        damages = [d + ailment_total for d in damages]

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
    area_level: int = 100,
) -> EnemyAwareDPS:
    """
    Calculates effective DPS against a specific enemy profile from enemy_profiles.json.

    Applies:
    - Enemy armor reduction formula: Mitigation = Armor / (Armor + 10 × area_level)
      (VERIFIED: 1.4.3 spec §3.1 — armor formula is area-level-based)
    - Enemy resistances minus character penetration for matching damage types
    - Resistance cap at 75%
    - Ailment DoT DPS bypasses armor entirely (VERIFIED: 1.4.3 spec §4.4 — DoTs are
      mitigated only by resistances, not armor).

    Returns raw DPS (vs dummy) and effective DPS (vs enemy).
    """
    base_result = calculate_dps(stats, skill_name, skill_level)
    hit_dps = base_result.dps
    ailment_dps = base_result.ailment_dps
    raw_dps = base_result.total_dps

    enemy: EnemyProfile | None = get_enemy_profile(enemy_id)
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

    skill_def = _get_skill_def(skill_name)
    if not skill_def:
        return EnemyAwareDPS(skill_name, enemy_id, 0, 0, 0.0, 0.0, {})

    if not skill_def.damage_types:
        log.warning("calculate_dps_vs_enemy.no_damage_types", skill=skill_name)
    skill_damage_types = {dt.value for dt in skill_def.damage_types} or {"physical"}

    # Build penetration map: damage_type_str → pen value from BuildStats
    pen_map: dict[str, float] = {
        dt: pen
        for dt in skill_damage_types
        if (pen := getattr(stats, f"{dt}_penetration", 0.0)) > 0
    }

    # Calculate steady-state armor shred
    from app.domain.armor_shred import armor_shred_amount
    shred = armor_shred_amount(
        stats.armour_shred_chance,
        base_result.effective_attack_speed,
        skill_def.hit_count,
    )
    effective_armor = max(0, enemy.armor - shred)

    # Armor only applies to hits; use the non-physical path when no physical
    # damage is present in the skill's damage types.
    has_physical = "physical" in skill_damage_types
    armor_factor = 1.0 - armor_mitigation(effective_armor, area_level, physical=has_physical)

    # Proportion-weighted resistance when a per-type damage breakdown is
    # available (populated by calculate_dps via DamageResult.damage_by_type).
    # Falls back to equal-weight average when breakdown is absent.
    if base_result.damage_by_type:
        from app.domain.calculators.damage_type_router import DamageType as _DT
        total = sum(base_result.damage_by_type.values()) or 1.0
        res_factor = sum(
            (amount / total) * (
                1.0 - effective_resistance(enemy, dt, pen_map.get(dt, 0.0)) / 100.0
            )
            for dt, amount in base_result.damage_by_type.items()
        )
        avg_res = (1.0 - res_factor) * 100.0
    else:
        res_values = [
            effective_resistance(enemy, dt, pen_map.get(dt, 0.0))
            for dt in skill_damage_types
        ]
        avg_res = sum(res_values) / len(res_values) if res_values else 0.0
        res_factor = 1.0 - avg_res / 100.0

    # VERIFIED: 1.4.3 spec §4.4 — DoTs bypass armor; only resistances apply.
    hit_multiplier = armor_factor * res_factor
    ailment_multiplier = res_factor
    effective_dps = round(hit_dps * hit_multiplier + ailment_dps * ailment_multiplier)

    return EnemyAwareDPS(
        skill_name=skill_name,
        enemy_id=enemy_id,
        raw_dps=raw_dps,
        effective_dps=effective_dps,
        armor_reduction_pct=round(armor_mitigation(effective_armor, area_level, physical=has_physical) * 100, 1),
        avg_res_reduction_pct=round(avg_res, 1),
        penetration_applied=pen_map,
    )
