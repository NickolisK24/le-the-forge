"""Deterministic hashing helpers for runtime replay orchestration contracts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


def hash_replay_orchestration_manifest(manifest: dict[str, Any]) -> str:
    stable = deepcopy(manifest)
    stable.pop("deterministic_hash", None)
    return deterministic_hash(stable)


def validate_replay_orchestration_replay_stability(manifest: dict[str, Any]) -> dict[str, Any]:
    first = hash_replay_orchestration_manifest(manifest)
    second = hash_replay_orchestration_manifest(deepcopy(manifest))
    return {
        "replay_stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "serializer": "json_sort_keys_sha256",
    }


def serialize_replay_orchestration_manifest(manifest: dict[str, Any]) -> str:
    return stable_serialize(manifest)
