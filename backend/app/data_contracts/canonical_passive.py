"""Canonical passive tree contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_base import CanonicalRecord
from .canonical_modifier import CanonicalModifierReference


@dataclass(frozen=True)
class CanonicalPassiveNode(CanonicalRecord):
    tree_id: str | None = None
    max_points: int | None = None
    required_points: int | None = None
    position: dict[str, float] = field(default_factory=dict)
    modifier_references: tuple[CanonicalModifierReference, ...] = field(default_factory=tuple)
    text_effects: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "position", dict(self.position))
        object.__setattr__(self, "modifier_references", tuple(self.modifier_references))
        object.__setattr__(self, "text_effects", tuple(self.text_effects))


@dataclass(frozen=True)
class CanonicalPassiveTree(CanonicalRecord):
    owner_class_id: str | None = None
    owner_mastery_id: str | None = None
    node_ids: tuple[str, ...] = field(default_factory=tuple)
    edges: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "node_ids", tuple(self.node_ids))
        object.__setattr__(self, "edges", tuple(tuple(edge) for edge in self.edges))
