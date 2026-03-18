"""
Game Data Loader — loads and caches game constants from JSON files.

Engines import from here when they want authoritative data from the JSON
files rather than their inline constants.  The JSON files are the canonical
reference for future patch updates.

Usage:
    from app.game_data.game_data_loader import (
        get_class_base_stats,
        get_mastery_bonuses,
        get_keystone_bonuses,
        get_attribute_scaling,
        get_affix_tier_midpoints,
        get_affix_stat_keys,
        get_all_affixes,
        get_affixes_by_category,
        get_skill_stats,
    )
"""

import json
import math
import os
from functools import lru_cache

_DATA_DIR = os.path.dirname(__file__)


def _load(filename: str) -> dict:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _classes() -> dict:
    return _load("classes.json")


@lru_cache(maxsize=1)
def _affixes_raw() -> dict:
    return _load("affixes.json")


@lru_cache(maxsize=1)
def _skills() -> dict:
    return _load("skills.json")


# ------------------------------------------------------------------
# Derived affix lookups — built once from the v3.0 affixes.json
# ------------------------------------------------------------------

@lru_cache(maxsize=1)
def _build_affix_lookups() -> tuple[dict, dict, dict]:
    """Build tier-midpoints, stat-keys, and type dicts from affix list.

    Returns:
        (midpoints, stat_keys, affix_types)
        midpoints: {name: {"T1": val, "T2": val, ...}}
        stat_keys: {name: "stat_field_name"}
        affix_types: {name: "flat" | "increased" | "more"}
    """
    raw = _affixes_raw()
    affix_list = raw.get("affixes", [])

    midpoints: dict[str, dict[str, float]] = {}
    stat_keys: dict[str, str] = {}
    affix_types: dict[str, str] = {}

    for affix in affix_list:
        name = affix["name"]
        # v3.0 uses "stat", v2.0 used "stat_key" — support both
        stat_keys[name] = affix.get("stat", affix.get("stat_key", ""))
        affix_types[name] = affix.get("type", "flat")
        tiers = affix.get("tiers", [])
        mp: dict[str, float] = {}
        if isinstance(tiers, list):
            # v3.0 format: [{"tier": 1, "value": 10, "min": 5, "max": 15}, ...]
            for entry in tiers:
                tier_num = entry["tier"]
                mp[f"T{tier_num}"] = entry.get("value", math.floor((entry.get("min", 0) + entry.get("max", 0)) / 2))
        else:
            # v2.0 fallback: {"1": [lo, hi], ...}
            for tier_key, bounds in tiers.items():
                lo, hi = bounds
                mp[f"T{tier_key}"] = math.floor((lo + hi) / 2)
        midpoints[name] = mp

    return midpoints, stat_keys, affix_types


def get_affix_tier_midpoints() -> dict:
    """Returns affix name → {T1: mid, T2: mid, …} mapping (all categories)."""
    return _build_affix_lookups()[0]


def get_affix_stat_keys() -> dict:
    """Returns affix display name → BuildStats field name mapping."""
    return _build_affix_lookups()[1]


def get_affix_types() -> dict:
    """Returns affix display name → modifier type (flat/increased/more) mapping."""
    return _build_affix_lookups()[2]


def get_all_affixes() -> list[dict]:
    """Returns the full list of affix definitions from the canonical JSON."""
    return _affixes_raw().get("affixes", [])


def get_affixes_by_category(category: str) -> list[dict]:
    """Returns affix definitions filtered by category."""
    return [a for a in get_all_affixes() if a.get("category") == category]


def get_affix_categories() -> dict:
    """Returns the category descriptions dict."""
    return _affixes_raw().get("_categories", {})


# ------------------------------------------------------------------
# Class / skill data
# ------------------------------------------------------------------

def get_class_base_stats() -> dict:
    """Returns base stats dict keyed by class name."""
    return _classes()["base_stats"]


def get_mastery_bonuses() -> dict:
    """Returns flat mastery bonus dicts keyed by mastery name."""
    return _classes()["mastery_bonuses"]


def get_mastery_per_point() -> dict:
    """Returns per-passive-point bonuses for masteries that scale with points used."""
    return _classes()["mastery_per_point"]


def get_keystone_bonuses() -> dict:
    """Returns keystone passive bonus dicts keyed by keystone name."""
    return _classes()["keystone_bonuses"]


def get_attribute_scaling() -> dict:
    """Returns attribute → BuildStats field scaling ratios."""
    return _classes()["attribute_scaling"]


def get_skill_stats() -> dict:
    """Returns skill name → stat definition dict."""
    return _skills()["skills"]
