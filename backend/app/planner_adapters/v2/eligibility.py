"""Eligibility gates for future v2 planner-facing consumption."""

from __future__ import annotations

from typing import Any

from .contracts import PlannerAdapterRecordEligibility

SUPPORTED_STABLE_STATUSES = frozenset({"trusted"})
SUPPORTED_TRUST_LEVELS = frozenset({"game_extracted", "generated_from_game_data"})
SCRIPTED_OR_UNSUPPORTED_BEHAVIORS = {
    "scripted_runtime_behavior": "scripted_behavior",
    "unsupported_special_behavior": "unsupported_behavior",
    "text_only_effect": "text_only_behavior",
    "unknown": "unknown_behavior",
}


def evaluate_modifier_record(record: dict[str, Any]) -> PlannerAdapterRecordEligibility:
    """Evaluate one normalized modifier row for planner-facing eligibility."""

    canonical_id = str(record.get("canonical_modifier_id") or "")
    support_status = str(record.get("support_status") or "unknown")
    trust_level = str(record.get("trust_level") or "unknown")
    value_scale_status = str(record.get("value_scale_status") or "unknown")
    operation = str(record.get("operation") or "unknown")
    stat_id = str(record.get("stat_id") or "stat:unknown")
    stable_calculable = bool(record.get("stable_calculable") is True)
    reasons: list[str] = []

    if not canonical_id:
        reasons.append("missing_canonical_id")
    if support_status not in SUPPORTED_STABLE_STATUSES:
        reasons.append("unstable_support_status")
    if trust_level not in SUPPORTED_TRUST_LEVELS:
        reasons.append("unstable_support_status")
    if not isinstance(record.get("provenance"), dict) or not record.get("provenance"):
        reasons.append("missing_provenance")

    source_record_status = str(record.get("source_record_status") or "")
    if source_record_status == "unsupported":
        reasons.append("unsupported_behavior")
    if source_record_status in {"text_only", "text_only_effect"}:
        reasons.append("text_only_behavior")
    if source_record_status == "experimental":
        reasons.append("unsupported_behavior")
    if source_record_status == "unknown":
        reasons.append("unknown_behavior")

    behavior = str(record.get("special_behavior_classification") or "")
    behavior_reason = SCRIPTED_OR_UNSUPPORTED_BEHAVIORS.get(behavior)
    if behavior_reason:
        reasons.append(behavior_reason)

    if value_scale_status == "unknown":
        reasons.append("unknown_value_scale")
    elif value_scale_status == "source_units":
        reasons.append("source_units_value_scale")
    elif value_scale_status != "planner_normalized":
        reasons.append("unknown_value_scale")

    if stat_id in {"", "stat:unknown"}:
        reasons.append("unresolved_stat_identity")
    if operation in {"", "unknown"}:
        reasons.append("unknown_operation")

    source_identity_status = str(record.get("source_identity_status") or "")
    if source_identity_status in {"ambiguous", "unresolved", "partially_unresolved"}:
        reasons.append("unresolved_skill_identity")

    if not stable_calculable:
        reasons.append("not_stable_calculable")

    unique_reasons = tuple(dict.fromkeys(reasons))
    return PlannerAdapterRecordEligibility(
        canonical_id=canonical_id,
        source_type=str(record.get("source_type") or "unknown"),
        source_id=str(record.get("source_id") or ""),
        eligible=not unique_reasons and stable_calculable,
        stable_calculable=stable_calculable,
        blocked_reasons=unique_reasons,
        support_status=support_status,
        trust_level=trust_level,
        value_scale_status=value_scale_status,
        operation=operation,
        stat_id=stat_id,
    )
