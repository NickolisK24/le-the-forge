"""Canonical class and mastery contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_base import CanonicalRecord


@dataclass(frozen=True)
class CanonicalClass(CanonicalRecord):
    mastery_ids: tuple[str, ...] = field(default_factory=tuple)
    passive_tree_ids: tuple[str, ...] = field(default_factory=tuple)
    skill_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "mastery_ids", tuple(self.mastery_ids))
        object.__setattr__(self, "passive_tree_ids", tuple(self.passive_tree_ids))
        object.__setattr__(self, "skill_ids", tuple(self.skill_ids))


@dataclass(frozen=True)
class CanonicalMastery(CanonicalRecord):
    class_id: str | None = None
    passive_tree_ids: tuple[str, ...] = field(default_factory=tuple)
    skill_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "passive_tree_ids", tuple(self.passive_tree_ids))
        object.__setattr__(self, "skill_ids", tuple(self.skill_ids))
