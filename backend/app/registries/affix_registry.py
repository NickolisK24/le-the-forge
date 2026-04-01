"""
Affix Registry — pre-indexed affix lookups for O(1) access.

Replaces the O(n) linear scans in affix_engine.py. Seeded from
data/items/affixes.json via the GameDataPipeline at app startup.

Usage:
    from flask import current_app
    registry = current_app.extensions["affix_registry"]
    affix  = registry.get_by_name("Spell Damage")       # O(1), raises if missing
    affixes = registry.for_slot("helm", "prefix")        # O(1) list
"""

from __future__ import annotations
from app.utils.exceptions import ForgeError
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


class AffixNotFoundError(ForgeError):
    status_code = 404

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Unknown affix: {identifier!r}")


class AffixRegistry:
    """
    Three-way indexed map of all affixes loaded from affixes.json.

    Lookup by name, by numeric id, or by (slot, type) pair — all O(1).
    Constructed once in create_app() and stored on app.extensions.
    """

    def __init__(self, affix_list: list[dict]) -> None:
        """
        Args:
            affix_list: flat list of affix dicts from the pipeline.
        """
        self._by_name: dict[str, dict] = {}
        self._by_id: dict[int, dict] = {}
        self._by_slot_type: dict[tuple[str, str], list[dict]] = {}

        for affix in affix_list:
            name = affix.get("name", "")
            affix_id = affix.get("affix_id") or affix.get("id")
            affix_type = affix.get("type", "")

            if name:
                self._by_name[name] = affix
            if affix_id is not None:
                try:
                    self._by_id[int(affix_id)] = affix
                except (TypeError, ValueError):
                    pass

            for slot in affix.get("applicable_to", []):
                key = (slot, affix_type)
                if key not in self._by_slot_type:
                    self._by_slot_type[key] = []
                self._by_slot_type[key].append(affix)

        log.info(
            "affix_registry.initialized",
            by_name=len(self._by_name),
            by_id=len(self._by_id),
            slot_type_buckets=len(self._by_slot_type),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_by_name(self, name: str) -> dict:
        """Return an affix dict by display name, or raise AffixNotFoundError."""
        affix = self._by_name.get(name)
        if affix is None:
            raise AffixNotFoundError(name)
        return affix

    def get_by_id(self, affix_id: int) -> dict:
        """Return an affix dict by numeric id, or raise AffixNotFoundError."""
        affix = self._by_id.get(affix_id)
        if affix is None:
            raise AffixNotFoundError(str(affix_id))
        return affix

    def for_slot(self, slot: str, affix_type: str) -> list[dict]:
        """Return all affixes valid for the given slot and type (prefix/suffix). O(1)."""
        return self._by_slot_type.get((slot, affix_type), [])

    def all(self) -> list[dict]:
        """Return all affixes as a flat list (by-name values, deduplicated)."""
        return list(self._by_name.values())

    def names(self) -> list[str]:
        """Return all affix names, sorted."""
        return sorted(self._by_name.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)
