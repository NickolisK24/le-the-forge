"""Canonical modifier contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical_base import CanonicalRecord
from .canonical_id import validate_canonical_id


@dataclass(frozen=True)
class CanonicalModifierReference:
    modifier_id: str
    property: str | None = None
    property_path: str | None = None
    source_record_id: str | None = None

    def __post_init__(self) -> None:
        validate_canonical_id(self.modifier_id, field_name="modifier_id")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "modifier_id": self.modifier_id,
            "property": self.property,
            "property_path": self.property_path,
            "source_record_id": self.source_record_id,
        }


@dataclass(frozen=True)
class CanonicalModifier(CanonicalRecord):
    source_type: str = "unknown"
    source_record_id: str | None = None
    stat_id: str | None = None
    operation: str = "unknown"
    value_min: float | None = None
    value_max: float | None = None
    scaling: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    conditions: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "tags", tuple(str(tag) for tag in self.tags))
        object.__setattr__(self, "conditions", dict(self.conditions))
