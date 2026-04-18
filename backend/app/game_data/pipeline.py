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

# skills.json and classes.json live alongside pipeline.py in the game_data
# package directory. Using __file__-relative paths works both on the host
# (backend/app/game_data/) and inside Docker (where the backend is mounted
# at /app, making _ROOT resolve to / rather than the project root).
_HERE = os.path.dirname(os.path.abspath(__file__))

_PATHS = {
    "affixes":        os.path.join(_ROOT, "data", "items", "affixes.json"),
    "enemies":        os.path.join(_ROOT, "data", "entities", "enemy_profiles.json"),
    "skills":         os.path.join(_HERE, "skills.json"),
    "classes":        os.path.join(_HERE, "classes.json"),
    "skills_meta":    os.path.join(_ROOT, "data", "classes", "skills_metadata.json"),
    "uniques":        os.path.join(_ROOT, "data", "items", "uniques.json"),
    "rarities":       os.path.join(_ROOT, "data", "items", "rarities.json"),
    "damage_types":   os.path.join(_ROOT, "data", "combat", "damage_types.json"),
    "implicit_stats": os.path.join(_ROOT, "data", "items", "implicit_stats.json"),
    "base_items":     os.path.join(_ROOT, "data", "items", "base_items.json"),
    "crafting_rules": os.path.join(_ROOT, "data", "items", "crafting_rules.json"),
    "blessings":      os.path.join(_ROOT, "data", "progression", "blessings.json"),
    "weaver_tree":    os.path.join(_ROOT, "data", "progression", "weaver_tree.json"),
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
        self._cache["skills_meta"]    = self._load_skills_metadata()
        self._cache["uniques"]        = self._load_optional("uniques", {})
        self._cache["rarities"]       = self._load_optional("rarities", [])
        self._cache["damage_types"]   = self._load_optional("damage_types", [])
        self._cache["implicit_stats"] = self._load_optional("implicit_stats", {})
        self._cache["blessings"]      = self._load_optional("blessings", [])
        # blessings.json is a list of 10 timelines, each with a nested
        # ``blessings`` array of individual blessing definitions.  Flatten
        # that inner list into a {blessing_id: definition} index so
        # get_blessing_by_id() resolves the actual blessings, not the
        # outer timeline wrappers.
        _flat: dict[str, dict] = {}
        for timeline in self._cache["blessings"]:
            if not isinstance(timeline, dict):
                continue
            for b in timeline.get("blessings", []) or []:
                if isinstance(b, dict) and "id" in b:
                    _flat[b["id"]] = b
        self._cache["blessings_flat"] = _flat

        self._cache["weaver_tree"] = self._load_weaver_tree()

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
    def rarities(self) -> list[dict]:
        return self._cache.get("rarities", [])

    @property
    def damage_types(self) -> list[dict]:
        return self._cache.get("damage_types", [])

    @property
    def implicit_stats(self) -> dict:
        return self._cache.get("implicit_stats", {})

    @property
    def blessings(self) -> list[dict]:
        return self._cache.get("blessings", [])

    @property
    def blessings_flat(self) -> dict[str, dict]:
        return self._cache.get("blessings_flat", {})

    @property
    def weaver_tree_nodes(self) -> list[dict]:
        """Return the list of Weaver Tree nodes (empty until populated in 0L-*)."""
        return self._cache.get("weaver_tree", [])

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

    def _load_skills_metadata(self) -> dict:
        """
        Load skills_metadata.json, drop meta-keys (``_schema``, ``_meta``),
        and validate the Phase-0 0G-1 damage fields whenever they are
        populated. Missing values are allowed (user fills them in 0G-2..0G-6);
        malformed values raise at startup so bad data cannot reach the engine.
        """
        raw = _load_json("skills_meta")
        if raw is None:
            return {}
        if not isinstance(raw, dict):
            raise RuntimeError(
                "pipeline: skills_metadata.json must be a JSON object"
            )

        skills = {k: v for k, v in raw.items() if not k.startswith("_")}
        populated = 0
        missing_any = 0
        for name, entry in skills.items():
            if not isinstance(entry, dict):
                raise RuntimeError(
                    f"pipeline: skills_metadata.json[{name!r}] must be an object"
                )
            self._validate_skill_damage_fields(name, entry)
            if all(
                entry.get(f) is not None
                for f in ("base_damage_min", "base_damage_max",
                          "damage_scaling_stat", "attack_type")
            ):
                populated += 1
            elif any(
                f not in entry
                for f in ("base_damage_min", "base_damage_max",
                          "damage_scaling_stat", "attack_type")
            ):
                missing_any += 1

        log.info(
            "pipeline.skills_metadata.loaded",
            total=len(skills),
            populated_0g=populated,
            unpopulated_0g=len(skills) - populated,
            entries_missing_any_0g_field=missing_any,
        )
        return skills

    def _load_weaver_tree(self) -> list[dict]:
        """
        Load data/progression/weaver_tree.json, strip the self-describing
        ``_schema`` wrapper, and return the flat node list. Validates every
        populated node so bad data cannot reach the engine.

        The file ships as a scaffold with ``nodes: []`` — node content gets
        captured from the in-game Weaver Tree in a follow-up task. The loader
        therefore treats an empty list as valid and logs the count at startup.
        """
        raw = _load_json("weaver_tree")
        if raw is None:
            return []
        if not isinstance(raw, dict):
            raise RuntimeError(
                "pipeline: weaver_tree.json must be a JSON object with a 'nodes' array"
            )
        nodes = raw.get("nodes", [])
        if not isinstance(nodes, list):
            raise RuntimeError(
                "pipeline: weaver_tree.json['nodes'] must be a list"
            )

        seen_ids: set[str] = set()
        for node in nodes:
            self._validate_weaver_node(node, seen_ids)
            seen_ids.add(node["id"])

        log.info(
            "pipeline.weaver_tree.loaded",
            nodes=len(nodes),
        )
        return nodes

    _REQUIRED_WEAVER_NODE_FIELDS = (
        "id", "name", "max_points", "connections", "stats",
    )

    def _validate_weaver_node(self, node: object, seen_ids: set[str]) -> None:
        """
        Per-node validation. Missing required keys, wrong types, or duplicate
        IDs raise at startup; the engine never sees malformed tree data.
        """
        if not isinstance(node, dict):
            raise RuntimeError(
                "pipeline: weaver_tree.json['nodes'] entry is not an object"
            )
        missing = [f for f in self._REQUIRED_WEAVER_NODE_FIELDS if f not in node]
        if missing:
            raise RuntimeError(
                f"pipeline: weaver_tree node missing required fields: {missing}"
            )
        node_id = node["id"]
        if not isinstance(node_id, str) or not node_id:
            raise RuntimeError(
                "pipeline: weaver_tree node.id must be a non-empty string"
            )
        if node_id in seen_ids:
            raise RuntimeError(
                f"pipeline: weaver_tree duplicate node id: {node_id!r}"
            )
        if not isinstance(node["name"], str):
            raise RuntimeError(
                f"pipeline: weaver_tree node[{node_id!r}].name must be a string"
            )
        if not isinstance(node["max_points"], int) or node["max_points"] < 1:
            raise RuntimeError(
                f"pipeline: weaver_tree node[{node_id!r}].max_points must be >= 1"
            )
        if not isinstance(node["connections"], list):
            raise RuntimeError(
                f"pipeline: weaver_tree node[{node_id!r}].connections must be a list"
            )
        for conn in node["connections"]:
            if not isinstance(conn, str) or not conn:
                raise RuntimeError(
                    f"pipeline: weaver_tree node[{node_id!r}] has invalid connection "
                    f"entry {conn!r}"
                )
        if not isinstance(node["stats"], list):
            raise RuntimeError(
                f"pipeline: weaver_tree node[{node_id!r}].stats must be a list"
            )
        for stat in node["stats"]:
            if not isinstance(stat, dict) or "key" not in stat or "value" not in stat:
                raise RuntimeError(
                    f"pipeline: weaver_tree node[{node_id!r}].stats entry must be "
                    "{'key': str, 'value': str|number}"
                )

    _ALLOWED_ATTACK_TYPES = {
        "melee", "ranged", "throwing", "spell",
        "channeled", "dot", "minion", "aura", "utility",
    }
    _ALLOWED_SCALING_STATS = {
        "strength", "intelligence", "dexterity",
        "vitality", "attunement", "none",
    }

    def _validate_skill_damage_fields(self, name: str, entry: dict) -> None:
        """
        Per-entry check for the 0G-1 fields. Null values are fine.
        Any populated value must match its declared type / enum.
        """
        dmin = entry.get("base_damage_min")
        dmax = entry.get("base_damage_max")
        if dmin is not None and not isinstance(dmin, (int, float)):
            raise RuntimeError(
                f"skills_metadata[{name!r}].base_damage_min must be numeric or null"
            )
        if dmax is not None and not isinstance(dmax, (int, float)):
            raise RuntimeError(
                f"skills_metadata[{name!r}].base_damage_max must be numeric or null"
            )
        if dmin is not None and dmax is not None and dmin > dmax:
            raise RuntimeError(
                f"skills_metadata[{name!r}]: base_damage_min > base_damage_max"
            )

        scaling = entry.get("damage_scaling_stat")
        if scaling is not None and scaling not in self._ALLOWED_SCALING_STATS:
            raise RuntimeError(
                f"skills_metadata[{name!r}].damage_scaling_stat={scaling!r} "
                f"not in {sorted(self._ALLOWED_SCALING_STATS)}"
            )

        atype = entry.get("attack_type")
        if atype is not None and atype not in self._ALLOWED_ATTACK_TYPES:
            raise RuntimeError(
                f"skills_metadata[{name!r}].attack_type={atype!r} "
                f"not in {sorted(self._ALLOWED_ATTACK_TYPES)}"
            )

    def _detect_version(self) -> str:
        raw = _load_json("affixes")
        if isinstance(raw, dict):
            return raw.get("_version", raw.get("_meta", {}).get("version", "unknown"))
        return "unknown"
