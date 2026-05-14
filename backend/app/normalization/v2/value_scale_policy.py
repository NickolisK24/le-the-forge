"""Audit-only value scale policy helpers for v2 modifier families."""

from __future__ import annotations

from collections import Counter
from typing import Any

SAFE_EVIDENCE_TYPES = frozenset(
    {
        "explicit_source_contract",
        "golden_planner_baseline",
        "round_trip_export_validation",
    }
)

SAFE_CONFIDENCE_LEVELS = frozenset({"high"})

PERCENT_LIKE_OPERATIONS = frozenset({"increased", "more", "reduced", "less", "chance", "conversion"})
STRUCTURED_NUMERIC_OPERATIONS = frozenset({"flat", "duration", "cooldown", "cost"})


def stat_family(stat_id: str) -> str:
    """Reduce a canonical stat ID to an audit family without inferring semantics."""

    value = str(stat_id or "stat:unknown")
    if not value.startswith("stat:"):
        return "unknown"
    parts = [part for part in value.removeprefix("stat:").split("_") if part]
    if not parts:
        return "unknown"
    if parts[0] in {"added", "increased", "more", "reduced", "less", "chance", "duration", "cooldown", "cost"} and len(parts) > 1:
        return "_".join(parts[:2])
    return parts[0]


def family_key(record: dict[str, Any]) -> str:
    return "|".join(
        [
            str(record.get("source_type") or "unknown"),
            str(record.get("operation") or "unknown"),
            stat_family(str(record.get("stat_id") or "stat:unknown")),
        ]
    )


def classify_family(records: list[dict[str, Any]], evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify a value-scale family without applying normalization."""

    evidence = evidence or {}
    scales = Counter(str(record.get("value_scale_status") or "unknown") for record in records)
    operations = Counter(str(record.get("operation") or "unknown") for record in records)
    stat_ids = Counter(str(record.get("stat_id") or "stat:unknown") for record in records)
    reasons: list[str] = []
    if scales.get("unknown"):
        reasons.append("unknown_value_scale")
    if operations.get("unknown"):
        reasons.append("unknown_operation")
    if stat_ids.get("stat:unknown"):
        reasons.append("unknown_stat_id")
    if any(record.get("source_identity_status") in {"ambiguous", "unresolved", "partially_unresolved"} for record in records):
        reasons.append("source_identity_gap")
    if any(record.get("special_behavior_classification") in {"text_only_effect", "scripted_runtime_behavior", "unsupported_special_behavior", "unknown"} for record in records):
        reasons.append("special_behavior_not_calculable")

    evidence_type = str(evidence.get("evidence_type") or "none")
    confidence = str(evidence.get("confidence") or "none")
    has_safe_evidence = evidence_type in SAFE_EVIDENCE_TYPES and confidence in SAFE_CONFIDENCE_LEVELS
    scale_factor = evidence.get("scale_factor")
    if has_safe_evidence and scale_factor is not None and not reasons:
        return {
            "policy_status": "candidate_safe_with_explicit_evidence",
            "planner_normalization_safe": True,
            "proposed_scale_factor": scale_factor,
            "evidence_type": evidence_type,
            "confidence": confidence,
            "blocked_reasons": [],
        }
    if scales == {"source_units": len(records)} and not reasons:
        operation = next(iter(operations))
        if operation in PERCENT_LIKE_OPERATIONS:
            status = "candidate_percent_family_requires_source_validation"
        elif operation in STRUCTURED_NUMERIC_OPERATIONS:
            status = "candidate_numeric_family_requires_source_validation"
        else:
            status = "candidate_requires_source_validation"
        return {
            "policy_status": status,
            "planner_normalization_safe": False,
            "proposed_scale_factor": None,
            "evidence_type": evidence_type,
            "confidence": confidence,
            "blocked_reasons": ["missing_explicit_scale_evidence"],
        }
    return {
        "policy_status": "blocked_or_unsafe",
        "planner_normalization_safe": False,
        "proposed_scale_factor": None,
        "evidence_type": evidence_type,
        "confidence": confidence,
        "blocked_reasons": sorted(set(reasons or ["mixed_or_incomplete_evidence"])),
    }
