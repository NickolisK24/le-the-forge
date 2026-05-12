"""Canonical unique item contract."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_item import CanonicalItemBase
from .canonical_modifier import CanonicalModifierReference


@dataclass(frozen=True)
class CanonicalUnique(CanonicalItemBase):
    base_item_id: str | None = None
    unique_effect_text: tuple[str, ...] = field(default_factory=tuple)
    modifier_references: tuple[CanonicalModifierReference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "unique_effect_text", tuple(self.unique_effect_text))
        object.__setattr__(self, "modifier_references", tuple(self.modifier_references))
