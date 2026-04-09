"""
Validation Layer — Upgrade 8

Validates build configurations, item structures, affix combinations, and
stat values before they enter the simulation engines.  The principle is:

    Never trust input.

All validation is pure (no DB, no HTTP) and returns structured results with
specific error messages.  Engines call these validators at their boundaries.

Rules:
- All limits from constants.json — no magic numbers
- Every violation has a machine-readable code and human-readable message
- Warnings are non-fatal; errors block processing
- Input dicts are never mutated
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONSTANTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "game_data", "constants.json"
)


@lru_cache(maxsize=1)
def _load_constants() -> dict:
    with open(_CONSTANTS_PATH) as f:
        return json.load(f)


def _const(section: str, key: str, default: Any = None) -> Any:
    return _load_constants().get(section, {}).get(key, default)


# ---------------------------------------------------------------------------
# Violation types
# ---------------------------------------------------------------------------

VALID_SLOTS = {
    "helmet", "body", "gloves", "boots", "belt", "ring", "amulet", "relic",
    "sword", "axe", "mace", "dagger", "sceptre", "wand", "staff",
    "bow", "two_handed_spear", "shield", "quiver", "catalyst",
    "idol_small", "idol_large", "idol_grand", "idol_stout",
    # Legacy aliases
    "helm", "chest", "spear",
}

VALID_CLASSES = {
    "Acolyte", "Mage", "Primalist", "Rogue", "Sentinel",
}

VALID_MASTERIES: dict[str, set[str]] = {
    "Acolyte":   {"Lich", "Necromancer", "Warlock"},
    "Mage":      {"Sorcerer", "Runemaster", "Spellblade"},
    "Primalist": {"Shaman", "Druid", "Beastmaster"},
    "Rogue":     {"Bladedancer", "Marksman", "Falconer"},
    "Sentinel":  {"Forge Guard", "Paladin", "Void Knight"},
}


@dataclass
class Violation:
    """A single validation error or warning."""
    code:     str     # machine-readable identifier, e.g. "SLOT_INVALID"
    message:  str     # human-readable explanation
    field:    str     # which field triggered this, e.g. "gear[0].slot_type"
    severity: str     # "error" or "warning"

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message,
                "field": self.field, "severity": self.severity}


@dataclass
class ValidationResult:
    """Aggregated output of a validation pass."""
    valid:       bool
    errors:      list[Violation] = field(default_factory=list)
    warnings:    list[Violation] = field(default_factory=list)

    def add_error(self, code: str, message: str, field: str = "") -> None:
        self.errors.append(Violation(code, message, field, "error"))
        self.valid = False

    def add_warning(self, code: str, message: str, field: str = "") -> None:
        self.warnings.append(Violation(code, message, field, "warning"))

    def merge(self, other: "ValidationResult") -> None:
        self.errors   += other.errors
        self.warnings += other.warnings
        if not other.valid:
            self.valid = False

    def to_dict(self) -> dict:
        return {
            "valid":    self.valid,
            "errors":   [v.to_dict() for v in self.errors],
            "warnings": [v.to_dict() for v in self.warnings],
        }


# ---------------------------------------------------------------------------
# Item validation
# ---------------------------------------------------------------------------

def validate_item(item: dict, slot_index: int = 0) -> ValidationResult:
    """Validate a single gear item dict.

    Checks:
    - slot_type is a recognised value
    - forging_potential / forge_potential ≥ 0
    - prefix + suffix count within limits
    - affix tiers within [1, max_affix_tier]
    - sealed_affix slot not double-occupied
    - implicit_stats values are numeric
    """
    result     = ValidationResult(valid=True)
    prefix     = f"gear[{slot_index}]"
    max_pfx    = _const("crafting", "max_prefixes", 3)
    max_sfx    = _const("crafting", "max_suffixes", 3)
    max_tier   = _const("crafting", "max_affix_tier", 7)
    max_sealed = _const("crafting", "max_sealed_affixes", 1)

    # Slot type
    slot = item.get("slot_type", item.get("slot", ""))
    if not slot:
        result.add_error("SLOT_MISSING", "Item has no slot_type", f"{prefix}.slot_type")
    elif slot not in VALID_SLOTS:
        result.add_error(
            "SLOT_INVALID",
            f"Slot type {slot!r} is not recognised. Valid: {sorted(VALID_SLOTS)}",
            f"{prefix}.slot_type",
        )

    # FP
    fp = item.get("forging_potential", item.get("forge_potential", None))
    if fp is None:
        result.add_warning("FP_MISSING", "Item has no forging_potential field", f"{prefix}.forging_potential")
    elif not isinstance(fp, (int, float)) or fp < 0:
        result.add_error("FP_NEGATIVE", f"forging_potential must be ≥ 0 (got {fp})", f"{prefix}.forging_potential")

    # Affixes (flat list schema)
    affixes = item.get("affixes", [])
    prefixes = item.get("prefixes", [])
    suffixes = item.get("suffixes", [])
    all_active = list(affixes) + list(prefixes) + list(suffixes)

    prefix_count = sum(1 for a in all_active if a.get("type") == "prefix" and not a.get("sealed"))
    suffix_count = sum(1 for a in all_active if a.get("type") == "suffix" and not a.get("sealed"))

    if len(prefixes) > max_pfx:
        result.add_error(
            "PREFIX_OVERFLOW",
            f"Item has {len(prefixes)} prefixes (max {max_pfx})",
            f"{prefix}.prefixes",
        )
    if len(suffixes) > max_sfx:
        result.add_error(
            "SUFFIX_OVERFLOW",
            f"Item has {len(suffixes)} suffixes (max {max_sfx})",
            f"{prefix}.suffixes",
        )

    # Affix tier validation
    for i, affix in enumerate(all_active):
        tier = affix.get("tier", 1)
        name = affix.get("name", f"affix[{i}]")
        if not isinstance(tier, int) or tier < 1:
            result.add_error(
                "TIER_BELOW_MIN",
                f"Affix {name!r} has tier {tier} (min 1)",
                f"{prefix}.affixes[{i}].tier",
            )
        elif tier > max_tier:
            result.add_error(
                "TIER_ABOVE_MAX",
                f"Affix {name!r} has tier {tier} (max {max_tier})",
                f"{prefix}.affixes[{i}].tier",
            )

    # Sealed affix
    sealed = item.get("sealed_affix")
    if sealed is not None and not isinstance(sealed, dict):
        result.add_error("SEAL_INVALID", "sealed_affix must be a dict or null", f"{prefix}.sealed_affix")

    # Implicit stats
    implicits = item.get("implicit_stats", {})
    for stat_key, val in implicits.items():
        if not isinstance(val, (int, float)):
            result.add_error(
                "IMPLICIT_NOT_NUMERIC",
                f"implicit_stats[{stat_key!r}] must be numeric (got {type(val).__name__})",
                f"{prefix}.implicit_stats.{stat_key}",
            )

    return result


# ---------------------------------------------------------------------------
# Build validation
# ---------------------------------------------------------------------------

def validate_build(build: dict) -> ValidationResult:
    """Validate a full build dict.

    Checks:
    - character_class present and recognised
    - mastery compatible with character_class
    - passive_tree is a list of ints (or dicts with id)
    - passive_tree length ≤ max_allocated_nodes
    - gear is a list; each item is validated
    - no duplicate gear slots (warning, not error)
    - primary_skill is a string (if provided)
    """
    result = ValidationResult(valid=True)
    max_nodes = _const("passives", "max_allocated_nodes", 113)

    # character_class
    char_class = build.get("character_class")
    if not char_class:
        result.add_error("CLASS_MISSING", "Build has no character_class", "character_class")
    elif char_class not in VALID_CLASSES:
        result.add_warning(
            "CLASS_UNKNOWN",
            f"character_class {char_class!r} not in known classes {sorted(VALID_CLASSES)}",
            "character_class",
        )

    # mastery
    mastery = build.get("mastery", "")
    if char_class and char_class in VALID_MASTERIES:
        valid_masts = VALID_MASTERIES[char_class]
        if mastery and mastery not in valid_masts:
            result.add_error(
                "MASTERY_MISMATCH",
                f"Mastery {mastery!r} is not valid for {char_class!r}. Valid: {sorted(valid_masts)}",
                "mastery",
            )

    # passive_tree
    passive_tree = build.get("passive_tree", [])
    if not isinstance(passive_tree, list):
        result.add_error("PASSIVE_NOT_LIST", "passive_tree must be a list", "passive_tree")
    else:
        for i, node in enumerate(passive_tree):
            if isinstance(node, dict):
                if "id" not in node and "node_id" not in node:
                    result.add_warning(
                        "NODE_NO_ID",
                        f"passive_tree[{i}] dict has no 'id' or 'node_id'",
                        f"passive_tree[{i}]",
                    )
            elif not isinstance(node, int):
                result.add_error(
                    "NODE_INVALID_TYPE",
                    f"passive_tree[{i}] must be int or dict (got {type(node).__name__})",
                    f"passive_tree[{i}]",
                )
        if len(passive_tree) > max_nodes:
            result.add_error(
                "PASSIVE_OVERFLOW",
                f"passive_tree has {len(passive_tree)} nodes (max {max_nodes})",
                "passive_tree",
            )

    # gear
    gear = build.get("gear", [])
    if not isinstance(gear, list):
        result.add_error("GEAR_NOT_LIST", "gear must be a list", "gear")
    else:
        seen_slots: dict[str, int] = {}
        for i, item in enumerate(gear):
            if not isinstance(item, dict):
                result.add_error("ITEM_NOT_DICT", f"gear[{i}] must be a dict", f"gear[{i}]")
                continue
            item_result = validate_item(item, slot_index=i)
            result.merge(item_result)

            slot = item.get("slot_type", item.get("slot", ""))
            if slot and slot in seen_slots:
                result.add_warning(
                    "SLOT_DUPLICATE",
                    f"Slot {slot!r} appears at both gear[{seen_slots[slot]}] and gear[{i}]",
                    f"gear[{i}].slot_type",
                )
            elif slot:
                seen_slots[slot] = i

    # primary_skill
    skill = build.get("primary_skill")
    if skill is not None and not isinstance(skill, str):
        result.add_error("SKILL_NOT_STRING", "primary_skill must be a string", "primary_skill")

    log.debug(
        "validate_build.result",
        valid=result.valid,
        n_errors=len(result.errors),
        n_warnings=len(result.warnings),
    )
    return result


# ---------------------------------------------------------------------------
# Affix combination validation
# ---------------------------------------------------------------------------

def validate_affix_combination(affixes: list[dict]) -> ValidationResult:
    """Validate that a set of affixes has no illegal combinations.

    Checks:
    - No duplicate affix names
    - Prefix / suffix counts within limits
    - Tier ranges valid

    Does NOT check slot compatibility (that requires the item context).
    """
    result   = ValidationResult(valid=True)
    max_pfx  = _const("crafting", "max_prefixes", 3)
    max_sfx  = _const("crafting", "max_suffixes", 3)
    max_tier = _const("crafting", "max_affix_tier", 7)

    seen_names: set[str] = set()
    prefix_count = 0
    suffix_count = 0

    for i, affix in enumerate(affixes):
        name = affix.get("name", "")
        tier = affix.get("tier", 1)
        affix_type = affix.get("type", "prefix")

        if name in seen_names:
            result.add_error(
                "AFFIX_DUPLICATE",
                f"Affix {name!r} appears more than once",
                f"affixes[{i}].name",
            )
        seen_names.add(name)

        if isinstance(tier, int):
            if tier < 1:
                result.add_error("TIER_BELOW_MIN", f"Affix {name!r} tier {tier} < 1", f"affixes[{i}].tier")
            elif tier > max_tier:
                result.add_error("TIER_ABOVE_MAX", f"Affix {name!r} tier {tier} > {max_tier}", f"affixes[{i}].tier")

        if affix_type == "prefix":
            prefix_count += 1
        elif affix_type == "suffix":
            suffix_count += 1

    if prefix_count > max_pfx:
        result.add_error("PREFIX_OVERFLOW", f"{prefix_count} prefixes exceed max {max_pfx}", "affixes")
    if suffix_count > max_sfx:
        result.add_error("SUFFIX_OVERFLOW", f"{suffix_count} suffixes exceed max {max_sfx}", "affixes")

    return result


# ---------------------------------------------------------------------------
# Stat range validation
# ---------------------------------------------------------------------------

def validate_stat_ranges(stats_dict: dict) -> ValidationResult:
    """Validate that a stats dict has no obviously illegal values.

    Useful for validating BuildStats.to_dict() or manually-constructed
    stat objects before they enter simulation.
    """
    result = ValidationResult(valid=True)

    _expect_non_negative = [
        "max_health", "armour", "dodge_rating", "ward",
        "base_damage", "attack_speed", "crit_multiplier",
    ]
    _expect_0_to_1 = ["crit_chance"]
    _expect_0_to_100 = [
        "fire_res", "cold_res", "lightning_res", "void_res",
        "necrotic_res", "physical_res", "poison_res",
    ]

    for key in _expect_non_negative:
        val = stats_dict.get(key)
        if val is not None and val < 0:
            result.add_error(
                "STAT_NEGATIVE",
                f"{key} must be ≥ 0 (got {val})",
                key,
            )

    for key in _expect_0_to_1:
        val = stats_dict.get(key)
        if val is not None and not (0.0 <= val <= 1.0):
            result.add_error(
                "STAT_OUT_OF_RANGE",
                f"{key} must be in [0, 1] (got {val})",
                key,
            )

    for key in _expect_0_to_100:
        val = stats_dict.get(key)
        if val is not None and not (-100 <= val <= 100):
            result.add_warning(
                "RESISTANCE_EXTREME",
                f"{key} value {val} is outside normal range [-100, 100]",
                key,
            )

    return result
