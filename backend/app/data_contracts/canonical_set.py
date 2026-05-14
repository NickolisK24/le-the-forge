"""Canonical set item contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_item import CanonicalItemBase
from .canonical_modifier import CanonicalModifierReference


@dataclass(frozen=True)
class CanonicalSetItem(CanonicalItemBase):
    set_id: str | None = None
    base_item_id: str | None = None
    modifier_references: tuple[CanonicalModifierReference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "modifier_references", tuple(self.modifier_references))


@dataclass(frozen=True)
class CanonicalSet(CanonicalItemBase):
    item_ids: tuple[str, ...] = field(default_factory=tuple)
    bonus_modifier_references: tuple[CanonicalModifierReference, ...] = field(default_factory=tuple)
    bonus_text: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "item_ids", tuple(self.item_ids))
        object.__setattr__(self, "bonus_modifier_references", tuple(self.bonus_modifier_references))
        object.__setattr__(self, "bonus_text", tuple(self.bonus_text))
