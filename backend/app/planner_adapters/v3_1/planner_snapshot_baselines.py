"""Deterministic planner-adjacent snapshot baseline infrastructure.

Snapshots are migration-readiness artifacts derived from dual-run comparison
metadata. They do not call planner/runtime code and cannot change production
ownership.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .dual_run_comparison import V31DualRunComparison, build_sample_dual_run_inputs
from .trusted_shadow_consumption import deterministic_hash


BASELINE_READINESS_CLASSIFICATIONS = (
    "baseline_candidate",
    "comparison_ready",
    "unsupported",
    "blocked",
    "insufficient_data",
    "legacy_only",
    "shadow_only",
)
STABLE_GENERATION_TOKEN = "v3_1_phase_3_planner_snapshot_baseline_token"


class V31PlannerSnapshotBaselines:
    """Build deterministic baseline candidate snapshots from dual-run output."""

    def build(
        self,
        *,
        dual_run_comparison: dict[str, Any],
        snapshot_category: str = "planner_adjacent_summary",
        run_id: str = "v3_1_phase_3_planner_snapshot_baselines",
    ) -> dict[str, Any]:
        comparison_rows = list(dual_run_comparison.get("comparison_results") or [])
        snapshots = [
            _snapshot_from_comparison(
                row=row,
                snapshot_category=snapshot_category,
                dual_run_gate=dual_run_comparison.get("trusted_shadow_gate") or {},
            )
            for row in sorted(comparison_rows, key=lambda item: str(item.get("stable_key") or item.get("comparison_id") or ""))
        ]
        counts = Counter(snapshot["baseline_readiness"] for snapshot in snapshots)
        production_affected_count = sum(1 for snapshot in snapshots if snapshot["production_output_affected"])
        envelope = {
            "schema_version": "v3_1.planner_snapshot_baselines.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "run": {
                "run_id": run_id,
                "snapshot_category": snapshot_category,
                "source_dual_run_schema": dual_run_comparison.get("schema_version"),
                "source_dual_run_hash": dual_run_comparison.get("deterministic_hash"),
                "snapshot_count": len(snapshots),
            },
            "summary": {
                "total_snapshots": len(snapshots),
                "baseline_candidate_count": counts["baseline_candidate"],
                "comparison_ready_count": counts["comparison_ready"],
                "unsupported_count": counts["unsupported"],
                "blocked_count": counts["blocked"],
                "insufficient_data_count": counts["insufficient_data"],
                "legacy_only_count": counts["legacy_only"],
                "shadow_only_count": counts["shadow_only"],
                "production_affected_count": production_affected_count,
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "deterministic": True,
            },
            "baseline_readiness_counts": {
                category: counts[category]
                for category in BASELINE_READINESS_CLASSIFICATIONS
            },
            "snapshots": snapshots,
            "safety_confirmations": {
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "legacy_planner_ownership_preserved": True,
                "planner_output_replaced": False,
                "runtime_state_mutated": False,
                "unsupported_states_hidden": False,
                "blocked_states_hidden": False,
                "automatic_drift_acceptance": False,
            },
            "metadata": {
                "source": "v3_1_planner_snapshot_baselines",
                "observational_only": True,
                "production_consumer": False,
                "production_behavior_changed": False,
                "planner_remap_performed": False,
                "production_default_routing_authorized": False,
                "stable_generation_token": STABLE_GENERATION_TOKEN,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_sample_planner_snapshot_baseline_inputs() -> dict[str, Any]:
    legacy, trusted_shadow = build_sample_dual_run_inputs()
    return V31DualRunComparison().compare(
        legacy_summaries=legacy,
        trusted_shadow_metadata=trusted_shadow,
        run_id="v3_1_phase_3_dual_run_snapshot_sample",
    )


def _snapshot_from_comparison(
    *,
    row: dict[str, Any],
    snapshot_category: str,
    dual_run_gate: dict[str, Any],
) -> dict[str, Any]:
    comparison_id = str(row.get("stable_key") or row.get("comparison_id"))
    baseline_readiness, reason_codes = _baseline_readiness(row)
    unsupported = baseline_readiness == "unsupported"
    blocked = baseline_readiness == "blocked"
    eligible = baseline_readiness in {"baseline_candidate", "comparison_ready"}
    snapshot_seed = {
        "comparison_id": comparison_id,
        "snapshot_category": snapshot_category,
        "generation_token": STABLE_GENERATION_TOKEN,
    }
    return {
        "snapshot_id": f"v3_1_snapshot_{deterministic_hash(snapshot_seed)[:16]}",
        "stable_key": comparison_id,
        "snapshot_category": snapshot_category,
        "planner_source_ownership": {
            "owner": "legacy",
            "legacy_controlled": True,
            "trusted_default_routing": False,
        },
        "trusted_shadow_participation": {
            "gate_enabled": bool((row.get("trusted_shadow_gate") or dual_run_gate).get("enabled", False)),
            "gate_mode": str((row.get("trusted_shadow_gate") or dual_run_gate).get("mode", "unknown")),
            "shadow_only": bool((row.get("trusted_shadow_gate") or dual_run_gate).get("shadow_only", True)),
            "trusted_shadow_status": row.get("trusted_shadow_status"),
        },
        "dual_run_comparison_state": {
            "comparison_id": row.get("comparison_id"),
            "legacy_status": row.get("legacy_status"),
            "trusted_shadow_status": row.get("trusted_shadow_status"),
            "drift_classification": row.get("drift_classification"),
            "reason_codes": list(row.get("reason_codes") or []),
            "legacy_hash": row.get("legacy_hash"),
            "trusted_hash": row.get("trusted_hash"),
        },
        "generation": {
            "strategy": "stable_token_and_sorted_json_hash",
            "token": STABLE_GENERATION_TOKEN,
            "timestamp_strategy": "report_level_deterministic_token",
        },
        "unsupported": unsupported,
        "blocked": blocked,
        "unsupported_or_blocked_reason": row.get("unsupported_or_blocked_reason"),
        "production_output_affected": False,
        "comparison_eligible": eligible,
        "baseline_candidate": baseline_readiness == "baseline_candidate",
        "baseline_readiness": baseline_readiness,
        "reason_codes": reason_codes,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
        },
    }


def _baseline_readiness(row: dict[str, Any]) -> tuple[str, list[str]]:
    drift = str(row.get("drift_classification"))
    if drift == "equivalent":
        return "baseline_candidate", ["dual_run_equivalent"]
    if drift == "divergent":
        return "comparison_ready", ["dual_run_divergent_requires_review"]
    if drift == "unsupported":
        return "unsupported", ["unsupported_state_visible"]
    if drift == "blocked":
        return "blocked", ["blocked_state_visible"]
    if drift in {"unavailable", "not_evaluated"}:
        return "insufficient_data", [f"dual_run_{drift}"]
    if drift == "legacy_only":
        return "legacy_only", ["trusted_shadow_missing"]
    if drift == "trusted_only":
        return "shadow_only", ["legacy_summary_missing"]
    return "insufficient_data", ["unknown_dual_run_classification"]


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
