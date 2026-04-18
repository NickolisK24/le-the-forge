"""
Game Data Loader — thin public API over the GameDataPipeline.

All existing callers continue to work unchanged. The pipeline owns the actual
loading and caching; these functions are stable wrappers.

Prefer using the pipeline directly for new code:
    from flask import current_app
    pipeline = current_app.extensions["game_data"]
"""

from __future__ import annotations
from app.game_data.pipeline import GameDataPipeline

# ---------------------------------------------------------------------------
# Module-level fallback pipeline — used before app context is available,
# e.g. in tests or scripts that don't go through create_app().
# ---------------------------------------------------------------------------

_fallback: GameDataPipeline | None = None


def _pipeline() -> GameDataPipeline:
    """Return the app-context pipeline if available, else the fallback."""
    try:
        from flask import current_app
        p = current_app.extensions.get("game_data")
        if p is not None:
            return p
    except RuntimeError:
        pass
    global _fallback
    if _fallback is None:
        _fallback = GameDataPipeline()
        _fallback.load_all()
    return _fallback


def get_affix_tier_midpoints() -> dict:
    """Returns affix name → {T1: mid, T2: mid, …} mapping."""
    return _pipeline().affix_tier_midpoints


def get_affix_stat_keys() -> dict:
    """Returns affix display name → BuildStats field name mapping."""
    return _pipeline().affix_stat_keys


def get_affix_types() -> dict:
    """Returns affix display name → modifier type (flat/increased/more) mapping."""
    return {a.to_dict()["name"]: a.to_dict().get("type", "flat") for a in _pipeline().affixes}


def get_all_affixes() -> list[dict]:
    """Returns the full flat list of affix definitions as raw dicts (backward compat)."""
    return [a.to_dict() for a in _pipeline().affixes]


def get_affixes_by_category(category: str) -> list[dict]:
    """Returns affix definitions filtered by type (prefix/suffix)."""
    return [a.to_dict() for a in _pipeline().affixes if a.affix_type == category]


def get_affix_categories() -> dict:
    """Returns a summary of affix type counts."""
    from collections import Counter
    counts = Counter(a.affix_type for a in _pipeline().affixes)
    return dict(counts)


def get_affixes_by_slot(slot: str) -> list[dict]:
    """Returns all equipment affixes that can roll on the given slot slug (e.g. 'helm')."""
    return [a.to_dict() for a in _pipeline().affixes if slot in a.applicable_to]


def get_affixes_by_tag(tag: str) -> list[dict]:
    """Returns all affixes that carry the given tag (e.g. 'fire', 'minion')."""
    tag = tag.lower()
    # Tags are not a first-class field on AffixDefinition; fall through to serialized form.
    return [a for a in get_all_affixes() if tag in [t.lower() for t in a.get("tags", [])]]


def get_affix_by_id(affix_id: int) -> dict | None:
    """Returns a single affix by its numeric game id, or None."""
    for affix in _pipeline().affixes:
        if affix.affix_id == affix_id:
            return affix.to_dict()
    return None


# ---------------------------------------------------------------------------
# Class / skill data
# ---------------------------------------------------------------------------

def get_class_base_stats() -> dict:
    """Returns base stats dict keyed by class name."""
    return _pipeline().classes.get("base_stats", {})


def get_mastery_bonuses() -> dict:
    """Returns flat mastery bonus dicts keyed by mastery name."""
    return _pipeline().classes.get("mastery_bonuses", {})


def get_mastery_per_point() -> dict:
    """Returns per-passive-point bonuses for masteries that scale with points used."""
    return _pipeline().classes.get("mastery_per_point", {})


def get_keystone_bonuses() -> dict:
    """Returns keystone passive bonus dicts keyed by keystone name."""
    return _pipeline().classes.get("keystone_bonuses", {})


def get_attribute_scaling() -> dict:
    """Returns attribute → BuildStats field scaling ratios."""
    return _pipeline().classes.get("attribute_scaling", {})


def get_skill_stats() -> dict[str, object]:
    """Returns skill name → SkillStatDef mapping."""
    return _pipeline().skills


def get_skill_metadata(skill_name: str) -> dict | None:
    """Returns metadata dict for a skill (description, lore, class) or None."""
    return _pipeline().skills_metadata.get(skill_name)


def get_all_skills_metadata() -> dict:
    """Returns the full skill name → metadata dict."""
    return _pipeline().skills_metadata


def get_skill_base_damage(skill_name: str) -> dict | None:
    """
    Returns the 0G-1 base-damage payload for a skill, or None when the
    skill is unknown or its damage fields are not yet populated.

    Shape: {base_damage_min, base_damage_max, damage_scaling_stat, attack_type}
    Any field can be None independently of the others until 0G-2..0G-6
    finish populating values per class.
    """
    meta = _pipeline().skills_metadata.get(skill_name)
    if not meta:
        return None
    fields = ("base_damage_min", "base_damage_max",
              "damage_scaling_stat", "attack_type")
    if all(meta.get(f) is None for f in fields):
        return None
    return {f: meta.get(f) for f in fields}


# ---------------------------------------------------------------------------
# Enemy profiles
# ---------------------------------------------------------------------------

def get_enemy_profiles() -> list["EnemyProfile"]:
    """Returns all enemy profile definitions as typed EnemyProfile objects."""
    from app.domain.enemy import EnemyProfile  # noqa: F401 — re-export for callers
    return list(_pipeline().enemies)


def get_enemy_profile(enemy_id: str) -> "EnemyProfile | None":
    """Returns a single EnemyProfile by id, or None if not found."""
    return _pipeline().get_enemy(enemy_id)


# ---------------------------------------------------------------------------
# Unique items
# ---------------------------------------------------------------------------

def get_all_uniques() -> list:
    """Return all unique items as a list of dicts (with 'id' = slug key)."""
    raw = _pipeline().uniques
    return [{"id": slug, **item} for slug, item in raw.items() if slug != "_meta"]


def get_unique_by_id(slug: str) -> dict | None:
    """Return a single unique item by its slug, or None."""
    raw = _pipeline().uniques
    item = raw.get(slug)
    if item is None or slug == "_meta":
        return None
    return {"id": slug, **item}


# ---------------------------------------------------------------------------
# Static reference data
# ---------------------------------------------------------------------------

def get_rarities() -> list[dict]:
    return _pipeline().rarities


def get_damage_types() -> list[dict]:
    return _pipeline().damage_types


def get_implicit_stat(item_type: str) -> dict | None:
    return _pipeline().implicit_stats.get(item_type.lower())


def get_all_implicit_stats() -> dict:
    return _pipeline().implicit_stats


# ---------------------------------------------------------------------------
# Monolith blessings
# ---------------------------------------------------------------------------

def get_all_blessings() -> list[dict]:
    """Return all Monolith blessing definitions from data/progression/blessings.json."""
    return _pipeline().blessings


def get_blessing_by_id(blessing_id: str) -> dict | None:
    """Return a single blessing definition by its id, or None if not found."""
    return _pipeline().blessings_flat.get(blessing_id)


def get_all_blessings_flat() -> dict[str, dict]:
    """Return a {blessing_id: blessing_dict} index built once at startup for O(1) lookup."""
    return _pipeline().blessings_flat
