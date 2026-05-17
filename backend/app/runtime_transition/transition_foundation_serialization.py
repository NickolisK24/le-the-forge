"""Deterministic JSON serialization helpers for v3.9 transition foundations.

These helpers serialize immutable evidence records only. They do not execute,
route, schedule, dispatch, traverse, mutate, optimize, recommend, rank, score,
select, authorize, or create callable orchestration behavior.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_for_transition_serialization(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_for_transition_serialization(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_for_transition_serialization(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, (tuple, list)):
        return [canonicalize_for_transition_serialization(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_for_transition_serialization(payload),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def serialize_v3_9_transition_foundation(foundation: Any) -> str:
    from .transition_foundation_models import export_v3_9_transition_foundation

    return stable_serialize(export_v3_9_transition_foundation(foundation))
