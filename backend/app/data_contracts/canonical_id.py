"""Canonical ID helpers."""

from __future__ import annotations

import re


CANONICAL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")


def validate_canonical_id(value: str, *, field_name: str = "canonical_id") -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    if value.strip() != value:
        raise ValueError(f"{field_name} must not contain leading or trailing whitespace")
    if not CANONICAL_ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must be stable lowercase text using letters, numbers, '.', '_', ':', or '-'"
        )
    return value
