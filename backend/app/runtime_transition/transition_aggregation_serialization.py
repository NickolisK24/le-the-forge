"""Deterministic serialization and hashing for v3.9 transition aggregation."""

from __future__ import annotations

from typing import Any

from .transition_foundation_hashing import deterministic_hash
from .transition_foundation_serialization import stable_serialize


def serialize_transition_aggregation_report(report: Any) -> str:
    from .transition_aggregation_models import export_transition_aggregation_report

    return stable_serialize(export_transition_aggregation_report(report))


def hash_transition_aggregation_summary(summary: Any) -> str:
    from .transition_aggregation_models import export_transition_aggregation_summary

    data = export_transition_aggregation_summary(summary)
    data.pop("deterministic_summary_hash", None)
    return deterministic_hash(data)


def hash_transition_aggregation_report(report: Any) -> str:
    from .transition_aggregation_models import export_transition_aggregation_report

    data = export_transition_aggregation_report(report)
    data.pop("deterministic_aggregation_hash", None)
    return deterministic_hash(data)


def validate_transition_aggregation_serialization_stability(report: Any) -> dict[str, Any]:
    first = serialize_transition_aggregation_report(report)
    second = serialize_transition_aggregation_report(report)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_9_transition_intelligence_aggregation",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_transition_aggregation_hash_stability(report: Any) -> dict[str, Any]:
    first = hash_transition_aggregation_report(report)
    second = hash_transition_aggregation_report(report)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_9_transition_intelligence_aggregation",
    }
