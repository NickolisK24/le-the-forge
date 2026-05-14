"""Source provenance contracts for canonical v2 records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceProvenance:
    source_path: str
    source_type: str
    extraction_method: str
    patch_version: str | None = None
    source_id: str | None = None
    schema_version: str = "v2"
    notes: tuple[str, ...] = field(default_factory=tuple)
    raw_reference: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_path:
            raise ValueError("source_path is required")
        if not self.source_type:
            raise ValueError("source_type is required")
        if not self.extraction_method:
            raise ValueError("extraction_method is required")
        object.__setattr__(self, "notes", tuple(str(note) for note in self.notes))
        object.__setattr__(self, "raw_reference", dict(self.raw_reference))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "source_type": self.source_type,
            "extraction_method": self.extraction_method,
            "patch_version": self.patch_version,
            "source_id": self.source_id,
            "schema_version": self.schema_version,
            "notes": list(self.notes),
            "raw_reference": dict(self.raw_reference),
        }
