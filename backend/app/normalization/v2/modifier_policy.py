"""Conservative policy helpers for v2 modifier normalization."""

from __future__ import annotations

import re
from typing import Any

from app.data_contracts.trust_level import TrustLevel
from app.data_contracts.trust_status import SupportStatus

MODIFIER_OPERATIONS = frozenset(
    {
        "flat",
        "increased",
        "more",
        "reduced",
        "less",
        "conversion",
        "chance",
        "duration",
        "cooldown",
        "cost",
        "unknown",
    }
)

VALUE_SCALE_STATUSES = frozenset({"planner_normalized", "source_units", "unknown", "not_applicable"})

_KNOWN_OPERATION_MAP = {
    "ADDED": "flat",
    "ADD": "flat",
    "FLAT": "flat",
    "INCREASED": "increased",
    "INCREASE": "increased",
    "MORE": "more",
    "REDUCED": "reduced",
    "REDUCE": "reduced",
    "LESS": "less",
    "CONVERSION": "conversion",
    "CONVERTED": "conversion",
    "CHANCE": "chance",
    "DURATION": "duration",
    "COOLDOWN": "cooldown",
    "COST": "cost",
}

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def normalize_stat_id(raw_stat: Any) -> str:
    """Create a stable canonical stat ID from a structural source stat label."""

    text = str(raw_stat or "").strip()
    if not text:
        return "stat:unknown"
    slug = _SLUG_RE.sub("_", text.lower()).strip("_")
    return f"stat:{slug or 'unknown'}"


def classify_operation(*, modifier_type: Any = None, property_path: Any = None, stat_label: Any = None) -> str:
    """Classify an operation using structural fields only."""

    candidates = [modifier_type, property_path, stat_label]
    for candidate in candidates:
        text = str(candidate or "").strip()
        if not text:
            continue
        head = text.split(".", 1)[0].upper()
        if head in _KNOWN_OPERATION_MAP:
            return _KNOWN_OPERATION_MAP[head]
        upper = text.upper()
        for raw, operation in _KNOWN_OPERATION_MAP.items():
            if raw in upper:
                return operation
    return "unknown"


def classify_value_scale(row: dict[str, Any], *, fallback: str = "unknown") -> str:
    value_scale = row.get("value_scale") or row.get("valueScale") or row.get("scale_status")
    if value_scale in VALUE_SCALE_STATUSES:
        return str(value_scale)
    if value_scale == "source_units":
        return "source_units"
    if row.get("normalized_value_min") is not None or row.get("normalized_value_max") is not None:
        return "planner_normalized"
    if row.get("value_min") is not None or row.get("value_max") is not None:
        return "source_units"
    if row.get("min_value") is not None or row.get("max_value") is not None:
        return "source_units"
    return fallback if fallback in VALUE_SCALE_STATUSES else "unknown"


def is_allowed_support_status(value: str) -> bool:
    return value == SupportStatus.TRUSTED.value


def is_allowed_trust_level(value: str) -> bool:
    return value in {TrustLevel.GAME_EXTRACTED.value, TrustLevel.GENERATED_FROM_GAME_DATA.value}


def is_stable_modifier_eligible(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return stable-planner eligibility and deterministic blocked reasons."""

    reasons: list[str] = []
    if not is_allowed_support_status(str(record.get("support_status", "unknown"))):
        reasons.append("support_status_not_trusted")
    if not is_allowed_trust_level(str(record.get("trust_level", "unknown"))):
        reasons.append("trust_level_not_stable")
    if record.get("stat_id") in {None, "", "stat:unknown"}:
        reasons.append("stat_id_unknown")
    if record.get("operation") not in MODIFIER_OPERATIONS or record.get("operation") == "unknown":
        reasons.append("operation_unknown")
    if record.get("value_scale_status") != "planner_normalized":
        reasons.append("value_scale_not_planner_normalized")
    if record.get("source_identity_status") in {"ambiguous", "unresolved", "partially_unresolved"}:
        reasons.append("source_identity_not_resolved")
    if record.get("source_record_status") in {"text_only", "unsupported", "experimental", "unknown"}:
        reasons.append("source_record_not_calculable")
    if record.get("special_behavior_classification") in {
        "text_only_effect",
        "scripted_runtime_behavior",
        "unsupported_special_behavior",
        "unknown",
    }:
        reasons.append("special_behavior_not_calculable")
    if not isinstance(record.get("provenance"), dict) or not record.get("provenance"):
        reasons.append("missing_provenance")
    return not reasons, reasons
