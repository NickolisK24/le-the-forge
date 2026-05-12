"""Canonical idol contract."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical_item import CanonicalItemBase


@dataclass(frozen=True)
class CanonicalIdol(CanonicalItemBase):
    idol_size: str | None = None
    idol_shape: str | None = None
    allowed_affix_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "allowed_affix_ids", tuple(self.allowed_affix_ids))
