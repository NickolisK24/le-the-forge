"""
Skill Classifier — determines whether a skill is a damage dealer, utility, or minion skill.

Used by the build analyzer to auto-detect the primary damage skill from a build's
skill loadout. Utility skills (movement, buffs, auras) and minion skills (summons)
are excluded from primary damage skill detection.

Pure module — no DB, no HTTP, no Flask context.
"""

from __future__ import annotations

from typing import Literal, Optional


# ---------------------------------------------------------------------------
# Classification constants
# ---------------------------------------------------------------------------

SkillClassification = Literal["damage", "utility", "minion"]

# Tags from skills_with_trees.json that indicate a utility skill
_UTILITY_TAGS: frozenset[str] = frozenset({
    "Buff", "Transform",
})

# Tags that indicate a minion skill
_MINION_TAGS: frozenset[str] = frozenset({
    "Minion",
})

# Explicit utility skill names (movement, buffs, auras, transforms)
_UTILITY_SKILL_NAMES: frozenset[str] = frozenset({
    # Movement / traversal
    "Shift", "Lunge", "Teleport", "Evade", "Dive", "Fury Leap",
    "Shield Rush", "Transplant", "Volatile Reversal", "Flame Rush",
    "Rampage", "Reap",
    # Buffs / auras
    "Focus", "Dark Quiver", "Fire Shield", "Holy Aura", "Roar",
    "Symbols of Hope", "Thorn Shield", "Eterra's Blessing",
    "Warcry", "Rebuke", "Smoke Bomb", "Flame Ward",
    # Transforms
    "Human Form", "Swarmblade Form", "Werebear Form", "Spriggan Form",
    "Reaper Form",
    # Utility
    "Mark for Death", "Mark For Death", "Ring of Shields", "Ring Of Shields",
    "Arcane Ascendance", "Decoy", "Detonate Decoy", "Create Shadow",
    "Banner Rush", "Ice Ward", "Frost Wall", "Glyph of Dominion",
    "Falconry", "Firebrand", "Static", "Rune Bolt",
    "Black Hole", "Ice Barrage", "Flame Reave",
})

# Explicit minion skill names
_MINION_SKILL_NAMES: frozenset[str] = frozenset({
    "Summon Bear", "Summon Bone Golem", "Summon Raptor", "Summon Sabertooth",
    "Summon Skeletal Mage", "Summon Skeleton", "Summon Volatile Zombie",
    "Summon Wolf", "Summon Wraith", "Summon Scorpion", "Summon Spriggan",
    "Summon Cryomancer", "Summon Death Knight", "Summon Forged Weapon",
    "Summon Frenzy Totem", "Summon Healing Totem", "Summon Hive",
    "Summon Pyromancer", "Summon Skeleton Rogue", "Summon Squirrel",
    "Summon Storm Crows", "Summon Storm Totem", "Summon Thorn Totem",
    "Summon Vine", "Summon Vines",
    "Assemble Abomination", "Manifest Armor",
    "Thorn Totem", "Ballista",
    "Falcon Strikes", "Aerial Assault", "Dive Bomb",
})


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_skill(skill_name: str) -> SkillClassification:
    """Classify a skill as damage, utility, or minion.

    Classification priority:
      1. Explicit minion name list → "minion"
      2. Explicit utility name list → "utility"
      3. Default → "damage"
    """
    if skill_name in _MINION_SKILL_NAMES:
        return "minion"
    if skill_name in _UTILITY_SKILL_NAMES:
        return "utility"
    return "damage"


def classify_skills(skill_names: list[str]) -> dict[str, SkillClassification]:
    """Classify multiple skills at once. Returns {skill_name: classification}."""
    return {name: classify_skill(name) for name in skill_names}


# ---------------------------------------------------------------------------
# Primary skill detection
# ---------------------------------------------------------------------------

def detect_primary_skill(skills: list[dict]) -> Optional[str]:
    """Detect the primary damage skill from a build's skill loadout.

    Args:
        skills: List of skill dicts with keys:
            - skill_name (str)
            - slot (int, 0-4)
            - allocated_nodes (int) — total skill tree points invested

    Returns:
        The skill_name of the detected primary skill, or None if no skills.

    Logic:
        1. Filter out UTILITY and MINION skills
        2. From remaining DAMAGE skills, return the one with highest allocated_nodes
        3. Tiebreak: prefer lower slot number
        4. If no damage skills exist, fall back to slot 0 (first) skill
        5. If no skills at all, return None
    """
    if not skills:
        return None

    # Classify and filter
    damage_skills = [
        s for s in skills
        if classify_skill(s.get("skill_name", "")) == "damage"
    ]

    if damage_skills:
        # Sort by allocated_nodes descending, then slot ascending for tiebreak
        damage_skills.sort(
            key=lambda s: (-s.get("allocated_nodes", 0), s.get("slot", 99))
        )
        return damage_skills[0]["skill_name"]

    # Fallback: no damage skills, use first slot
    sorted_by_slot = sorted(skills, key=lambda s: s.get("slot", 99))
    return sorted_by_slot[0].get("skill_name")
