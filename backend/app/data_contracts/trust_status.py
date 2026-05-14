"""Canonical v2 support status values."""

from __future__ import annotations

from enum import StrEnum


class SupportStatus(StrEnum):
    TRUSTED = "trusted"
    PARTIAL = "partial"
    TEXT_ONLY = "text_only"
    UNSUPPORTED = "unsupported"
    EXPERIMENTAL = "experimental"
    UNKNOWN = "unknown"


STABLE_CALCULABLE_STATUSES = frozenset({SupportStatus.TRUSTED})
DISPLAY_ONLY_STATUSES = frozenset(
    {
        SupportStatus.TEXT_ONLY,
        SupportStatus.UNSUPPORTED,
        SupportStatus.UNKNOWN,
        SupportStatus.EXPERIMENTAL,
    }
)


def coerce_support_status(value: str | SupportStatus) -> SupportStatus:
    if isinstance(value, SupportStatus):
        return value
    try:
        return SupportStatus(str(value))
    except ValueError as exc:
        allowed = ", ".join(status.value for status in SupportStatus)
        raise ValueError(f"Invalid support status {value!r}. Expected one of: {allowed}") from exc
