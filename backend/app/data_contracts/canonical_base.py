"""Shared canonical record primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical_id import validate_canonical_id
from .source_provenance import SourceProvenance
from .trust_level import TrustLevel, coerce_trust_level
from .trust_status import SupportStatus, coerce_support_status


@dataclass(frozen=True)
class CanonicalRecord:
    canonical_id: str
    display_name: str
    support_status: SupportStatus
    trust_level: TrustLevel
    provenance: SourceProvenance
    source_id: str | None = None
    source_file: str | None = None
    patch_version: str | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    raw_reference: dict[str, Any] = field(default_factory=dict)
    normalized_fields: dict[str, Any] = field(default_factory=dict)
    consumer_safe_fields: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_canonical_id(self.canonical_id)
        if not self.display_name:
            raise ValueError("display_name is required")
        object.__setattr__(self, "support_status", coerce_support_status(self.support_status))
        object.__setattr__(self, "trust_level", coerce_trust_level(self.trust_level))
        if not isinstance(self.provenance, SourceProvenance):
            raise ValueError("provenance is required")
        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))
        object.__setattr__(self, "raw_reference", dict(self.raw_reference))
        object.__setattr__(self, "normalized_fields", dict(self.normalized_fields))
        object.__setattr__(self, "consumer_safe_fields", dict(self.consumer_safe_fields))

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_id": self.canonical_id,
            "display_name": self.display_name,
            "support_status": self.support_status.value,
            "trust_level": self.trust_level.value,
            "provenance": self.provenance.to_dict(),
            "source_id": self.source_id,
            "source_file": self.source_file,
            "patch_version": self.patch_version,
            "warnings": list(self.warnings),
            "raw_reference": dict(self.raw_reference),
            "normalized_fields": dict(self.normalized_fields),
            "consumer_safe_fields": dict(self.consumer_safe_fields),
        }
