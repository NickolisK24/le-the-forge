"""
Affix Registry — pre-indexed AffixDefinition lookups for O(1) access.

Seeded from data/items/affixes.json via the GameDataPipeline (which
normalizes raw JSON → AffixDefinition) at app startup. The registry
receives pre-normalized domain objects; it does not do normalization itself.

Usage:
    from flask import current_app
    registry = current_app.extensions["affix_registry"]
    affix  = registry.get_by_name("Spell Damage")       # O(1), raises if missing
    affixes = registry.for_slot("helm", "prefix")        # O(1) list
"""

from __future__ import annotations
from app.domain.item import AffixDefinition
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
    Receives a pre-normalized list[AffixDefinition] from the pipeline.
    Constructed once in create_app() and stored on app.extensions.
    """

    def __init__(self, affixes: list[AffixDefinition]) -> None:
        """
        Args:
            affixes: flat list of AffixDefinition domain objects, already
                     normalized by the pipeline. No further normalization here.
        Raises:
            ValueError: if affixes is empty or contains mixed data versions.
        """
        if not affixes:
            raise ValueError("AffixRegistry requires at least one definition")

        version = affixes[0].data_version
        for d in affixes:
            if d.data_version != version:
                raise ValueError(
                    f"Mixed data versions in AffixRegistry: "
                    f"expected {version!r}, got {d.data_version!r} on affix {d.name!r}"
                )
        self.data_version = version

        self._by_name: dict[str, AffixDefinition] = {}
        self._by_id: dict[int, AffixDefinition] = {}
        self._by_slot_type: dict[tuple[str, str], list[AffixDefinition]] = {}

        for affix in affixes:
            if affix.name:
                self._by_name[affix.name] = affix
            if affix.affix_id is not None:
                self._by_id[affix.affix_id] = affix
            for slot in affix.applicable_to:
                key = (slot, affix.affix_type)
                if key not in self._by_slot_type:
                    self._by_slot_type[key] = []
                self._by_slot_type[key].append(affix)

        log.info(
            "affix_registry.initialized",
            data_version=self.data_version,
            by_name=len(self._by_name),
            by_id=len(self._by_id),
            slot_type_buckets=len(self._by_slot_type),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_by_name(self, name: str) -> AffixDefinition:
        """Return an AffixDefinition by display name, or raise AffixNotFoundError."""
        affix = self._by_name.get(name)
        if affix is None:
            raise AffixNotFoundError(name)
        return affix

    def get_by_id(self, affix_id: int) -> AffixDefinition:
        """Return an AffixDefinition by numeric id, or raise AffixNotFoundError."""
        affix = self._by_id.get(affix_id)
        if affix is None:
            raise AffixNotFoundError(str(affix_id))
        return affix

    def for_slot(self, slot: str, affix_type: str) -> list[AffixDefinition]:
        """Return all affixes valid for the given slot and type (prefix/suffix). O(1)."""
        return self._by_slot_type.get((slot, affix_type), [])

    def all(self) -> list[AffixDefinition]:
        """Return all affixes as a flat list (by-name values, deduplicated)."""
        return list(self._by_name.values())

    def names(self) -> list[str]:
        """Return all affix names, sorted."""
        return sorted(self._by_name.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)
