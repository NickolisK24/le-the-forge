"""Canonical item, base item, and implicit contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_base import CanonicalRecord
from .canonical_modifier import CanonicalModifierReference


@dataclass(frozen=True)
class CanonicalImplicit(CanonicalRecord):
    modifier_references: tuple[CanonicalModifierReference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "modifier_references", tuple(self.modifier_references))


@dataclass(frozen=True)
class CanonicalItemBase(CanonicalRecord):
    item_type: str | None = None
    slot: str | None = None
    subtype: str | None = None
    level_requirement: int | None = None
    class_restrictions: tuple[str, ...] = field(default_factory=tuple)
    implicit_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "class_restrictions", tuple(self.class_restrictions))
        object.__setattr__(self, "implicit_ids", tuple(self.implicit_ids))
