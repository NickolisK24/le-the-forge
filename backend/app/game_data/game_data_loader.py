"""
Game Data Loader — loads and caches game constants from JSON files.

Engines import from here when they want authoritative data from the JSON
files rather than their inline constants. The two sources are kept in sync;
the JSON files are the canonical reference for future patch updates.

Usage:
    from app.game_data.game_data_loader import (
        get_class_base_stats,
        get_mastery_bonuses,
        get_keystone_bonuses,
        get_attribute_scaling,
        get_affix_tier_midpoints,
        get_affix_stat_keys,
        get_skill_stats,
    )
"""

import json
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
def _affixes() -> dict:
    return _load("affixes.json")


@lru_cache(maxsize=1)
def _skills() -> dict:
    return _load("skills.json")


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


def get_affix_tier_midpoints() -> dict:
    """Returns affix name → tier → midpoint value mapping."""
    return _affixes()["tier_midpoints"]


def get_affix_stat_keys() -> dict:
    """Returns affix display name → BuildStats field name mapping."""
    return _affixes()["stat_keys"]


def get_skill_stats() -> dict:
    """Returns skill name → stat definition dict."""
    return _skills()["skills"]
