"""Canonical v2 trust level values."""

from __future__ import annotations

from enum import StrEnum


class TrustLevel(StrEnum):
    GAME_EXTRACTED = "game_extracted"
    GENERATED_FROM_GAME_DATA = "generated_from_game_data"
    MANUAL_BRIDGE = "manual_bridge"
    INFERRED = "inferred"
    PLACEHOLDER = "placeholder"
    DEPRECATED = "deprecated"


STABLE_TRUST_LEVELS = frozenset(
    {
        TrustLevel.GAME_EXTRACTED,
        TrustLevel.GENERATED_FROM_GAME_DATA,
    }
)


def coerce_trust_level(value: str | TrustLevel) -> TrustLevel:
    if isinstance(value, TrustLevel):
        return value
    try:
        return TrustLevel(str(value))
    except ValueError as exc:
        allowed = ", ".join(level.value for level in TrustLevel)
        raise ValueError(f"Invalid trust level {value!r}. Expected one of: {allowed}") from exc
