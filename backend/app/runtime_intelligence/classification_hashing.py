"""Deterministic hashing helpers for runtime intelligence contracts."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


def stable_serialize(payload: Any) -> str:
    """Serialize payloads deterministically for replay-stable manifests."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def deterministic_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_classification_manifest(manifest: dict[str, Any]) -> str:
    stable = deepcopy(manifest)
    stable.pop("deterministic_hash", None)
    return deterministic_hash(stable)


def validate_replay_stability(manifest: dict[str, Any]) -> dict[str, Any]:
    first = hash_classification_manifest(manifest)
    second = hash_classification_manifest(deepcopy(manifest))
    return {
        "replay_stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "serializer": "json_sort_keys_sha256",
    }
