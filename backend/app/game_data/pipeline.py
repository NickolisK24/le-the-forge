"""
Game Data Pipeline — owns all JSON loading, validation, and caching.

Single point of entry for all canonical game data. The pipeline:
  - Loads JSON files from /data/ (never from within backend/app/)
  - Validates that required top-level keys are present
  - Produces typed domain objects where appropriate
  - Caches everything in-memory after first load
  - Exposes reload() for hot-reload without restarting the app
  - Tracks data_version from _version / _meta fields in source files

Usage (after initialization in create_app):
    from flask import current_app
    pipeline = current_app.extensions["game_data"]
    affixes = pipeline.affixes          # list[dict], validated and cached
    enemies = pipeline.enemies          # list[EnemyProfile], typed and cached
"""

import json
import os
from typing import Optional

from app.domain.enemy import EnemyProfile
from app.domain.item import AffixDefinition
from app.domain.skill import SkillStatDef
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

_PATHS = {
    "affixes":        os.path.join(_ROOT, "data", "items", "affixes.json"),
    "enemies":        os.path.join(_ROOT, "data", "entities", "enemy_profiles.json"),
    "skills":         os.path.join(_ROOT, "backend", "app", "game_data", "skills.json"),
    "classes":        os.path.join(_ROOT, "backend", "app", "game_data", "classes.json"),
    "skills_meta":    os.path.join(_ROOT, "data", "classes", "skills_metadata.json"),
    "uniques":        os.path.join(_ROOT, "data", "items", "uniques.json"),
    "rarities":       os.path.join(_ROOT, "data", "items", "rarities.json"),
    "damage_types":   os.path.join(_ROOT, "data", "combat", "damage_types.json"),
    "implicit_stats": os.path.join(_ROOT, "data", "items", "implicit_stats.json"),
    "base_items":     os.path.join(_ROOT, "data", "items", "base_items.json"),
    "crafting_rules": os.path.join(_ROOT, "data", "items", "crafting_rules.json"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(key: str) -> Optional[dict | list]:
    """Load a JSON file by pipeline key. Returns None if the file doesn't exist."""
    path = _PATHS[key]
    if not os.path.exists(path):
        log.warning("pipeline.missing_file", key=key, path=path)
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"pipeline: malformed JSON in {path!r}: {exc}"
        ) from exc


def _require_keys(data: dict, keys: list[str], source: str) -> None:
    """Assert that all required keys are present in a dict, raising at startup."""
    missing = [k for k in keys if k not in data]
    if missing:
        raise RuntimeError(
            f"pipeline: {source!r} is missing required keys: {missing}"
        )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class GameDataPipeline:
    """
    Owns all game data loading. Constructed once in create_app() and stored
    on app.extensions['game_data'].

    After construction, all data is available as properties. Call reload()
    to clear the cache and re-load from disk without restarting the app.
    """

    def __init__(self) -> None:
        self._cache: dict = {}
        self._version: str = "unknown"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Load and validate all game data. Called once at app startup."""
        log.info("pipeline.load_all.start")
        self._cache.clear()

        # Detect version before loading so it can be stamped on every domain object.
        self._version = self._detect_version()

        self._cache["affixes"]        = self._load_affixes(self._version)
        self._cache["enemies"]        = self._load_enemies(self._version)
        self._cache["skills"]         = self._load_skills(self._version)
        self._cache["classes"]        = self._load_classes()
        self._cache["skills_meta"]    = self._load_optional("skills_meta", {})
        self._cache["uniques"]        = self._load_optional("uniques", {})
        self._cache["rarities"]       = self._load_optional("rarities", {})
        self._cache["damage_types"]   = self._load_optional("damage_types", {})
        self._cache["implicit_stats"] = self._load_optional("implicit_stats", {})

        log.info("pipeline.load_all.done", version=self._version)

    def reload(self) -> None:
        """Clear the cache and reload all data from disk."""
        log.info("pipeline.reload")
        self.load_all()

    @property
    def data_version(self) -> str:
        return self._version

    # ------------------------------------------------------------------
    # Typed accessors
    # ------------------------------------------------------------------

    @property
    def affixes(self) -> list[AffixDefinition]:
        return self._cache.get("affixes", [])

    @property
    def affix_tier_midpoints(self) -> dict[str, dict[str, float]]:
        """Legacy accessor — computes from AffixDefinition objects for backward compat."""
        return {a.name: a.tier_midpoints() for a in self.affixes if a.name}

    @property
    def affix_stat_keys(self) -> dict[str, str]:
        """Legacy accessor — computes from AffixDefinition objects for backward compat."""
        return {a.name: a.stat_key for a in self.affixes if a.name}

    @property
    def enemies(self) -> list[EnemyProfile]:
        return self._cache.get("enemies", [])

    @property
    def skills(self) -> dict[str, SkillStatDef]:
        return self._cache.get("skills", {})

    @property
    def classes(self) -> dict:
        return self._cache.get("classes", {})

    @property
    def skills_metadata(self) -> dict:
        return self._cache.get("skills_meta", {})

    @property
    def uniques(self) -> dict:
        return self._cache.get("uniques", {})

    @property
    def rarities(self) -> dict:
        return self._cache.get("rarities", {})

    @property
    def damage_types(self) -> dict:
        return self._cache.get("damage_types", {})

    @property
    def implicit_stats(self) -> dict:
        return self._cache.get("implicit_stats", {})

    def get_enemy(self, enemy_id: str) -> Optional[EnemyProfile]:
        """Return a single EnemyProfile by id, or None."""
        for enemy in self.enemies:
            if enemy.id == enemy_id:
                return enemy
        return None

    # ------------------------------------------------------------------
    # Loaders (private)
    # ------------------------------------------------------------------

    def _load_affixes(self, data_version: str) -> list[AffixDefinition]:
        raw = _load_json("affixes")
        if raw is None:
            log.warning("pipeline.affixes.missing")
            return []
        raw_list: list[dict]
        if isinstance(raw, list):
            raw_list = raw
        else:
            _require_keys(raw, ["affixes"], "affixes.json")
            raw_list = raw["affixes"]
        return [AffixDefinition.from_dict(a, data_version=data_version) for a in raw_list]

    def _load_enemies(self, data_version: str) -> list[EnemyProfile]:
        raw = _load_json("enemies")
        if not raw:
            return []
        if not isinstance(raw, list):
            raise RuntimeError("pipeline: enemy_profiles.json must be a JSON array")
        return [EnemyProfile.from_dict(e, data_version=data_version) for e in raw]

    def _load_skills(self, data_version: str) -> dict[str, SkillStatDef]:
        raw = _load_json("skills")
        if raw is None:
            return {}
        _require_keys(raw, ["skills"], "skills.json")
        return {
            name: SkillStatDef.from_dict(data, data_version=data_version)
            for name, data in raw["skills"].items()
        }

    def _load_classes(self) -> dict:
        raw = _load_json("classes")
        if raw is None:
            return {}
        _require_keys(
            raw,
            ["base_stats", "mastery_bonuses", "attribute_scaling"],
            "classes.json",
        )
        return raw

    def _load_optional(self, key: str, default):
        raw = _load_json(key)
        return raw if raw is not None else default

    def _detect_version(self) -> str:
        raw = _load_json("affixes")
        if isinstance(raw, dict):
            return raw.get("_version", raw.get("_meta", {}).get("version", "unknown"))
        return "unknown"
