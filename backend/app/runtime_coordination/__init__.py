"""Deterministic runtime coordination foundation models.

The runtime coordination package models non-executable orchestration-planning
coordination evidence. It does not route, schedule, dispatch, traverse, mutate,
optimize, recommend, authorize, or execute orchestration behavior.
"""

from .coordination_foundation_models import (
    V3_8_COORDINATION_FOUNDATION_PHASE_ID,
    V3_8_COORDINATION_FOUNDATION_STATUS_BLOCKED,
    V3_8_COORDINATION_FOUNDATION_STATUS_STABLE,
    V3_8_COORDINATION_SCHEMA_VERSION,
    V38CoordinationFoundation,
    default_v3_8_coordination_foundation,
    export_v3_8_coordination_foundation,
    hash_v3_8_coordination_foundation,
    serialize_v3_8_coordination_foundation,
    validate_v3_8_coordination_foundation_guarantees,
    validate_v3_8_coordination_hash_stability,
    validate_v3_8_coordination_serialization_stability,
)

__all__ = [
    "V3_8_COORDINATION_FOUNDATION_PHASE_ID",
    "V3_8_COORDINATION_FOUNDATION_STATUS_BLOCKED",
    "V3_8_COORDINATION_FOUNDATION_STATUS_STABLE",
    "V3_8_COORDINATION_SCHEMA_VERSION",
    "V38CoordinationFoundation",
    "default_v3_8_coordination_foundation",
    "export_v3_8_coordination_foundation",
    "hash_v3_8_coordination_foundation",
    "serialize_v3_8_coordination_foundation",
    "validate_v3_8_coordination_foundation_guarantees",
    "validate_v3_8_coordination_hash_stability",
    "validate_v3_8_coordination_serialization_stability",
]
