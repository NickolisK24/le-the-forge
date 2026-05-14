"""Canonical skill and skill tree contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_base import CanonicalRecord
from .canonical_modifier import CanonicalModifierReference


@dataclass(frozen=True)
class CanonicalSkill(CanonicalRecord):
    owner_class_ids: tuple[str, ...] = field(default_factory=tuple)
    owner_mastery_ids: tuple[str, ...] = field(default_factory=tuple)
    skill_tree_id: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    damage_types: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "owner_class_ids", tuple(self.owner_class_ids))
        object.__setattr__(self, "owner_mastery_ids", tuple(self.owner_mastery_ids))
        object.__setattr__(self, "tags", tuple(self.tags))
        object.__setattr__(self, "damage_types", tuple(self.damage_types))


@dataclass(frozen=True)
class CanonicalSkillTreeNode(CanonicalRecord):
    skill_tree_id: str | None = None
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
class CanonicalSkillTree(CanonicalRecord):
    skill_id: str | None = None
    node_ids: tuple[str, ...] = field(default_factory=tuple)
    edges: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "node_ids", tuple(self.node_ids))
        object.__setattr__(self, "edges", tuple(tuple(edge) for edge in self.edges))
