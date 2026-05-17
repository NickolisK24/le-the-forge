"""Deterministic hashing for v4.1 closeout readiness."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_1_closeout_readiness_models import (
    V41CloseoutIdentity,
    V41CloseoutIntegrityBoundary,
    V41CloseoutReadiness,
    V41ReadinessCertification,
    V41WarningAggregation,
)
from .v4_1_closeout_readiness_serialization import export_v4_1_closeout_readiness, stable_serialize


def deterministic_v4_1_closeout_hash(value: Any) -> str:
    if isinstance(value, V41CloseoutReadiness):
        value = export_v4_1_closeout_readiness(value)
    return hashlib.sha256(stable_serialize(value).encode("utf-8")).hexdigest()


def hash_v4_1_closeout_identity(identity: V41CloseoutIdentity) -> str:
    return deterministic_v4_1_closeout_hash(identity)


def hash_v4_1_closeout_readiness(payload: V41CloseoutReadiness) -> str:
    return deterministic_v4_1_closeout_hash(payload)


def hash_v4_1_readiness_certification(readiness: V41ReadinessCertification) -> str:
    return deterministic_v4_1_closeout_hash(readiness)


def hash_v4_1_warning_aggregation(aggregation: V41WarningAggregation) -> str:
    return deterministic_v4_1_closeout_hash(aggregation)


def hash_v4_1_closeout_integrity(boundary: V41CloseoutIntegrityBoundary) -> str:
    return deterministic_v4_1_closeout_hash(boundary)
