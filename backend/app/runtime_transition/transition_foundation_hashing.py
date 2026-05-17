"""Deterministic hashing helpers for v3.9 transition foundations.

Hashing here is evidence hashing only. It does not approve, select, schedule,
dispatch, route, traverse, mutate, or execute transition behavior.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .transition_foundation_serialization import stable_serialize


def deterministic_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_transition_payload(payload: Any) -> str:
    return deterministic_hash(payload)


def hash_v3_9_transition_identity(identity: Any) -> str:
    return deterministic_hash(identity)


def hash_v3_9_transition_reference(reference: Any) -> str:
    return deterministic_hash(reference)


def hash_v3_9_transition_state_reference(reference: Any) -> str:
    return deterministic_hash(reference)


def hash_v3_9_transition_provenance_reference(reference: Any) -> str:
    return deterministic_hash(reference)


def hash_v3_9_transition_continuity_reference(reference: Any) -> str:
    return deterministic_hash(reference)


def hash_v3_9_transition_foundation(foundation: Any) -> str:
    from .transition_foundation_models import export_v3_9_transition_foundation

    return deterministic_hash(export_v3_9_transition_foundation(foundation))
