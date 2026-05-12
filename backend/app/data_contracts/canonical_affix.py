"""Canonical affix contract."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_base import CanonicalRecord
from .canonical_modifier import CanonicalModifierReference


@dataclass(frozen=True)
class CanonicalAffix(CanonicalRecord):
    affix_type: str | None = None
    tier_count: int | None = None
    item_applicability: tuple[str, ...] = field(default_factory=tuple)
    class_restrictions: tuple[str, ...] = field(default_factory=tuple)
    modifier_references: tuple[CanonicalModifierReference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "item_applicability", tuple(self.item_applicability))
        object.__setattr__(self, "class_restrictions", tuple(self.class_restrictions))
        object.__setattr__(self, "modifier_references", tuple(self.modifier_references))
