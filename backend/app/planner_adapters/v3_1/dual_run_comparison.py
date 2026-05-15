"""Deterministic v3.1 legacy/trusted-shadow dual-run comparison.

The comparison layer accepts already-built legacy summaries and Phase 1 trusted
shadow metadata. It does not call production planner/runtime code and cannot
replace production output.
"""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .trusted_shadow_consumption import V31TrustedProductionShadowConsumption, deterministic_hash


DRIFT_CLASSIFICATIONS = (
    "equivalent",
    "legacy_only",
    "trusted_only",
    "divergent",
    "unavailable",
    "unsupported",
    "blocked",
    "not_evaluated",
)


class V31DualRunComparison:
    """Compare legacy production summaries against trusted shadow metadata."""

    def compare(
        self,
        *,
        legacy_summaries: list[dict[str, Any]],
        trusted_shadow_metadata: dict[str, Any],
        run_id: str = "v3_1_phase_2_dual_run_comparison",
    ) -> dict[str, Any]:
        legacy_by_key = {
            _comparison_key(row): deepcopy(row)
            for row in legacy_summaries
        }
        trusted_by_key = _trusted_rows_by_key(trusted_shadow_metadata)
        keys = sorted(set(legacy_by_key) | set(trusted_by_key))
        gate = trusted_shadow_metadata.get("gate") or {}

        results = [
            _comparison_result(
                comparison_id=key,
                legacy=legacy_by_key.get(key),
                trusted=trusted_by_key.get(key),
                trusted_gate=gate,
            )
            for key in keys
        ]
        counts = Counter(row["drift_classification"] for row in results)
        production_affected_count = sum(1 for row in results if row["production_output_affected"])
        envelope = {
            "schema_version": "v3_1.dual_run_comparison.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "run": {
                "run_id": run_id,
                "legacy_summary_count": len(legacy_summaries),
                "trusted_summary_count": len(trusted_by_key),
                "comparison_count": len(results),
            },
            "summary": {
                "total_comparisons": len(results),
                "equivalent_count": counts["equivalent"],
                "divergent_count": counts["divergent"],
                "unsupported_count": counts["unsupported"],
                "blocked_count": counts["blocked"],
                "legacy_only_count": counts["legacy_only"],
                "trusted_only_count": counts["trusted_only"],
                "unavailable_count": counts["unavailable"],
                "not_evaluated_count": counts["not_evaluated"],
                "production_affected_count": production_affected_count,
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "deterministic": True,
            },
            "drift_classification_counts": {
                category: counts[category]
                for category in DRIFT_CLASSIFICATIONS
            },
            "comparison_results": results,
            "trusted_shadow_gate": {
                "enabled": bool(gate.get("enabled", False)),
                "mode": str(gate.get("mode", "unknown")),
                "shadow_only": bool(gate.get("shadow_only", True)),
                "production_truth_source": gate.get("production_truth_source", "legacy"),
                "production_output_affected": bool(gate.get("production_output_affected", False)),
            },
            "safety_confirmations": {
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "legacy_output_replaced": False,
                "runtime_state_mutated": False,
                "silent_missing_trusted_accepted": False,
                "silent_missing_legacy_accepted": False,
                "unsupported_states_hidden": False,
            },
            "metadata": {
                "source": "v3_1_dual_run_comparison",
                "observational_only": True,
                "production_consumer": False,
                "production_behavior_changed": False,
                "planner_remap_performed": False,
                "production_default_routing_authorized": False,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_sample_dual_run_inputs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trusted_shadow = V31TrustedProductionShadowConsumption().inspect(
        enabled=True,
        trusted_repository_probes=[
            _sample_probe("affix", "v2_affix_bundle", 1098),
            _sample_probe("item_base", "v2_item_base_bundle", 542),
            _sample_probe("passive_skill", "v2_passive_tree_bundle", 5),
        ],
        legacy_output={"route": "legacy", "sample_total": 3},
        run_id="v3_1_phase_2_trusted_shadow_sample",
    )
    legacy = [
        _legacy_summary("affix", "available", 1098, "legacy_affix_catalog"),
        _legacy_summary("item_base", "available", 540, "legacy_item_catalog"),
        _legacy_summary("passive_skill", "unsupported", None, "legacy_passive_skill_runtime"),
        _legacy_summary("idol", "available", 81, "legacy_idol_catalog"),
    ]
    trusted_shadow["trusted_repository_rows"].append(
        {
            "domain": "monolith_echo",
            "repository_name": "unsupported_shadow_repository",
            "routing_status": "blocked_unsupported_domain",
            "trusted_repository_available": False,
            "trusted_entity_count": 0,
            "legacy_path_still_active": True,
            "trusted_path_shadowed_only": True,
            "production_output_affected": False,
            "blocked_reasons": ["unsupported_trusted_shadow_domain"],
            "fallback_behavior": "legacy_remains_active_reported",
            "metadata": {},
        }
    )
    return legacy, trusted_shadow


def _sample_probe(domain: str, repository_name: str, count: int):
    from .trusted_shadow_consumption import TrustedRepositoryProbe

    return TrustedRepositoryProbe(
        domain=domain,
        repository_name=repository_name,
        count_loader=lambda: count,
        metadata_loader=lambda: {"entity_count": count, "schema_version": "sample", "source_path": f"sample:{repository_name}"},
    )


def _legacy_summary(comparison_id: str, status: str, comparable_value: Any, source: str) -> dict[str, Any]:
    return {
        "comparison_id": comparison_id,
        "legacy_status": status,
        "comparable_value": comparable_value,
        "source": source,
        "production_output": True,
    }


def _trusted_rows_by_key(trusted_shadow_metadata: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in trusted_shadow_metadata.get("trusted_repository_rows") or []:
        key = str(row.get("comparison_id") or row.get("domain") or row.get("repository_name") or "")
        if not key:
            continue
        rows[key] = {
            "comparison_id": key,
            "trusted_shadow_status": _trusted_status(row),
            "comparable_value": row.get("trusted_entity_count"),
            "routing_status": row.get("routing_status"),
            "repository_name": row.get("repository_name"),
            "blocked_reasons": list(row.get("blocked_reasons") or []),
            "production_output_affected": bool(row.get("production_output_affected", False)),
            "raw_shadow_row": deepcopy(row),
        }
    return rows


def _trusted_status(row: dict[str, Any]) -> str:
    routing_status = str(row.get("routing_status", ""))
    if routing_status == "trusted_repository_shadowed":
        return "available"
    if routing_status == "trusted_repository_unavailable":
        return "unavailable"
    if routing_status == "blocked_unsupported_domain":
        return "unsupported"
    if routing_status.startswith("blocked"):
        return "blocked"
    return "not_evaluated"


def _comparison_result(
    *,
    comparison_id: str,
    legacy: dict[str, Any] | None,
    trusted: dict[str, Any] | None,
    trusted_gate: dict[str, Any],
) -> dict[str, Any]:
    legacy_status = str((legacy or {}).get("legacy_status") or (legacy or {}).get("status") or "missing")
    trusted_status = str((trusted or {}).get("trusted_shadow_status") or "missing")
    classification, reason_codes = _classify(
        legacy=legacy,
        trusted=trusted,
        legacy_status=legacy_status,
        trusted_status=trusted_status,
        trusted_gate=trusted_gate,
    )
    return {
        "comparison_id": comparison_id,
        "stable_key": comparison_id,
        "legacy_status": legacy_status,
        "trusted_shadow_status": trusted_status,
        "drift_classification": classification,
        "production_output_affected": False,
        "trusted_shadow_gate": {
            "enabled": bool(trusted_gate.get("enabled", False)),
            "mode": str(trusted_gate.get("mode", "unknown")),
            "shadow_only": bool(trusted_gate.get("shadow_only", True)),
        },
        "unsupported_or_blocked_reason": _unsupported_or_blocked_reason(legacy=legacy, trusted=trusted, reason_codes=reason_codes),
        "reason_codes": reason_codes,
        "legacy_hash": _value_hash((legacy or {}).get("comparable_value")) if legacy is not None else None,
        "trusted_hash": _value_hash((trusted or {}).get("comparable_value")) if trusted is not None else None,
        "deterministic_notes": [
            "comparison rows sorted by stable key",
            "comparable values hashed through sorted JSON serialization",
            "production output is not mutated or replaced",
        ],
    }


def _classify(
    *,
    legacy: dict[str, Any] | None,
    trusted: dict[str, Any] | None,
    legacy_status: str,
    trusted_status: str,
    trusted_gate: dict[str, Any],
) -> tuple[str, list[str]]:
    if not bool(trusted_gate.get("enabled", False)):
        return "not_evaluated", ["trusted_shadow_gate_disabled"]
    if legacy is None and trusted is None:
        return "not_evaluated", ["legacy_and_trusted_missing"]
    if legacy_status == "unsupported" or trusted_status == "unsupported":
        return "unsupported", ["unsupported_state_visible"]
    if legacy_status == "blocked" or trusted_status == "blocked":
        return "blocked", ["blocked_state_visible"]
    if legacy_status == "unavailable" or trusted_status == "unavailable":
        return "unavailable", ["unavailable_state_visible"]
    if legacy_status == "not_evaluated" or trusted_status == "not_evaluated":
        return "not_evaluated", ["not_evaluated_state_visible"]
    if legacy is None and trusted is not None:
        return "trusted_only", ["legacy_summary_missing"]
    if trusted is None and legacy is not None:
        return "legacy_only", ["trusted_shadow_summary_missing"]
    legacy_hash = _value_hash(legacy.get("comparable_value"))
    trusted_hash = _value_hash(trusted.get("comparable_value"))
    if legacy_hash == trusted_hash:
        return "equivalent", ["comparable_value_hash_match"]
    return "divergent", ["comparable_value_hash_mismatch"]


def _unsupported_or_blocked_reason(
    *,
    legacy: dict[str, Any] | None,
    trusted: dict[str, Any] | None,
    reason_codes: list[str],
) -> str | None:
    trusted_reasons = list((trusted or {}).get("blocked_reasons") or [])
    legacy_reason = (legacy or {}).get("blocked_reason") or (legacy or {}).get("unsupported_reason")
    reasons = [str(legacy_reason)] if legacy_reason else []
    reasons.extend(str(reason) for reason in trusted_reasons)
    if reasons:
        return ";".join(sorted(set(reasons)))
    if any("missing" in reason or "visible" in reason for reason in reason_codes):
        return ";".join(reason_codes)
    return None


def _comparison_key(row: dict[str, Any]) -> str:
    return str(row.get("comparison_id") or row.get("stable_key") or row.get("domain") or "")


def _value_hash(value: Any) -> str:
    return deterministic_hash({"value": value})


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
