"""
J9 — Data Mapping Layer

Converts raw JSON dicts (as loaded by RawDataLoader) into Phase J domain
model objects (SkillModel, ItemModel, AffixModel, PassiveTreeModel, EnemyModel).

The mapper normalises field names and resolves the differences between the
various source JSON formats and the canonical model definitions.
"""

from __future__ import annotations

from typing import Any

from data.models.skill_model import SkillModel
from data.models.item_model import ItemModel
from data.models.affix_model import AffixModel
from data.models.passive_tree_model import PassiveTreeModel
from data.models.enemy_model import EnemyModel

__all__ = ["DataMapper"]


class DataMapper:
    """
    Stateless collection of class-methods that map raw dicts → models.

    Each method accepts a raw dict (validated or unvalidated) and returns
    a typed model object.  Mapping failures raise :exc:`ValueError` with
    a descriptive message.
    """

    # ------------------------------------------------------------------
    # Skills  (source: app/game_data/skills.json  { "skills": { name: {...} } })
    # ------------------------------------------------------------------

    @classmethod
    def skill_from_raw(cls, skill_id: str, raw: dict[str, Any]) -> SkillModel:
        """
        Map a raw skills.json entry to a :class:`SkillModel`.

        The source dict uses ``base_damage``, ``attack_speed``, and
        optionally ``tags``.  Cooldown and mana_cost default to 0 when
        absent (many skills in the source data omit them).
        """
        try:
            return SkillModel(
                skill_id=skill_id,
                base_damage=float(raw.get("base_damage", 0)),
                cooldown=float(raw.get("cooldown", 0)),
                mana_cost=float(raw.get("mana_cost", 0)),
                tags=tuple(raw.get("tags", [])),
                attack_speed=float(raw.get("attack_speed", 1.0)),
                level_scaling=float(raw.get("level_scaling", 0.0)),
                scaling_stats=tuple(raw.get("scaling_stats", [])),
                is_spell=bool(raw.get("is_spell", False)),
                is_melee=bool(raw.get("is_melee", False)),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Cannot map skill {skill_id!r}: {exc}"
            ) from exc

    @classmethod
    def skills_from_bundle(cls, bundle: dict[str, Any]) -> list[SkillModel]:
        """
        Map an entire skills.json bundle (``{ "skills": { name: {...} } }``).

        Accepts both a bare dict and a dict wrapped under ``"skills"`` key.
        """
        raw_skills: dict = bundle.get("skills", bundle)
        return [
            cls.skill_from_raw(skill_id, raw)
            for skill_id, raw in raw_skills.items()
            if isinstance(raw, dict)
        ]

    # ------------------------------------------------------------------
    # Items  (source: data/items/base_items.json)
    # ------------------------------------------------------------------

    @classmethod
    def item_from_raw(cls, raw: dict[str, Any]) -> ItemModel:
        """Map a base_items.json entry to an :class:`ItemModel`."""
        item_id = raw.get("id") or raw.get("item_id") or raw.get("name", "")
        slot_type = raw.get("slot") or raw.get("slot_type", "")
        try:
            return ItemModel(
                item_id=str(item_id),
                slot_type=str(slot_type),
                implicit_stats=dict(raw.get("implicit_stats", {})),
                explicit_affixes=tuple(raw.get("explicit_affixes", [])),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Cannot map item {item_id!r}: {exc}") from exc

    @classmethod
    def items_from_bundle(
        cls, bundle: dict[str, Any] | list
    ) -> list[ItemModel]:
        """
        Map a base_items.json bundle.

        Accepts:
        - A list of item dicts
        - A dict of ``{ slot: [item, ...] }`` (the real format)
        """
        if isinstance(bundle, list):
            return [cls.item_from_raw(r) for r in bundle if isinstance(r, dict)]

        items: list[ItemModel] = []
        for slot, entries in bundle.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                # Inject the slot from the key if not already present
                enriched = {"slot_type": slot, **entry}
                items.append(cls.item_from_raw(enriched))
        return items

    # ------------------------------------------------------------------
    # Affixes  (source: data/items/affixes.json)
    # ------------------------------------------------------------------

    @classmethod
    def affix_from_raw(cls, raw: dict[str, Any]) -> list[AffixModel]:
        """
        Map a single affixes.json entry to one :class:`AffixModel` per tier.

        Each tier produces a model with id ``<affix_id>_t<tier>``.
        """
        base_id = raw.get("id") or raw.get("affix_id") or raw.get("name", "unknown")
        stat_type = raw.get("stat_key") or raw.get("name", str(base_id))
        tiers = raw.get("tiers", [])

        if not tiers:
            # Single-tier flat affix
            return [
                AffixModel(
                    affix_id=str(base_id),
                    stat_type=str(stat_type),
                    min_value=float(raw.get("min_value", raw.get("min", 0))),
                    max_value=float(raw.get("max_value", raw.get("max", 0))),
                )
            ]

        models: list[AffixModel] = []
        for t in tiers:
            tier_num = t.get("tier", 1)
            models.append(
                AffixModel(
                    affix_id=f"{base_id}_t{tier_num}",
                    stat_type=str(stat_type),
                    min_value=float(t.get("min", 0)),
                    max_value=float(t.get("max", 0)),
                )
            )
        return models

    @classmethod
    def affixes_from_bundle(cls, bundle: list) -> list[AffixModel]:
        """Map an entire affixes.json array."""
        result: list[AffixModel] = []
        for raw in bundle:
            if not isinstance(raw, dict):
                continue
            try:
                result.extend(cls.affix_from_raw(raw))
            except ValueError:
                continue  # skip malformed entries
        return result

    # ------------------------------------------------------------------
    # Passive Tree  (source: data/classes/passives.json)
    # ------------------------------------------------------------------

    @classmethod
    def passive_from_raw(cls, raw: dict[str, Any]) -> PassiveTreeModel:
        """Map a passives.json entry to a :class:`PassiveTreeModel`."""
        node_id = raw.get("id") or raw.get("node_id", "")
        # stats field is a list of stat strings in the real data
        raw_stats = raw.get("stats", raw.get("stat_modifiers", {}))
        if isinstance(raw_stats, list):
            # Convert list of stat strings to a simple dict with value=1
            stat_mods: dict = {s: 1.0 for s in raw_stats if isinstance(s, str)}
        else:
            stat_mods = dict(raw_stats)

        deps = raw.get("connections", raw.get("dependencies", []))
        try:
            return PassiveTreeModel(
                node_id=str(node_id),
                stat_modifiers=stat_mods,
                dependencies=tuple(str(d) for d in deps),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Cannot map passive {node_id!r}: {exc}") from exc

    @classmethod
    def passives_from_bundle(cls, bundle: dict | list) -> list[PassiveTreeModel]:
        """Map a passives.json bundle (list or dict-wrapped list)."""
        raw_list = bundle.get("passives", bundle) if isinstance(bundle, dict) else bundle
        return [
            cls.passive_from_raw(r)
            for r in raw_list
            if isinstance(r, dict)
        ]

    # ------------------------------------------------------------------
    # Enemies  (source: data/entities/enemy_profiles.json)
    # ------------------------------------------------------------------

    @classmethod
    def enemy_from_raw(cls, raw: dict[str, Any]) -> EnemyModel:
        """Map an enemy_profiles.json entry to an :class:`EnemyModel`."""
        enemy_id = raw.get("id") or raw.get("enemy_id", "")
        try:
            return EnemyModel(
                enemy_id=str(enemy_id),
                max_health=float(raw.get("health", raw.get("max_health", 1))),
                resistances=dict(raw.get("resistances", {})),
                armor=float(raw.get("armor", 0)),
                name=str(raw.get("name", "")),
                category=str(raw.get("category", "")),
                crit_chance=float(raw.get("crit_chance", 0.0)),
                crit_multiplier=float(raw.get("crit_multiplier", 1.5)),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Cannot map enemy {enemy_id!r}: {exc}") from exc

    @classmethod
    def enemies_from_bundle(cls, bundle: list | dict) -> list[EnemyModel]:
        """Map an enemy_profiles.json bundle."""
        raw_list = bundle if isinstance(bundle, list) else bundle.get("enemies", [])
        return [
            cls.enemy_from_raw(r)
            for r in raw_list
            if isinstance(r, dict)
        ]
