"""Deterministic baseline fixture approval workflow infrastructure.

Fixture workflows are governance records over planner snapshot baselines. They
do not approve production routing and do not replace legacy planner ownership.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .planner_snapshot_baselines import (
    V31PlannerSnapshotBaselines,
    build_sample_planner_snapshot_baseline_inputs,
)
from .trusted_shadow_consumption import deterministic_hash


FIXTURE_WORKFLOW_STATES = (
    "pending_review",
    "approved_candidate",
    "approved_baseline",
    "rejected",
    "unsupported",
    "blocked",
    "insufficient_data",
    "archived",
)
STABLE_WORKFLOW_GENERATION_TOKEN = "v3_1_phase_4_baseline_fixture_workflow_token"


class V31BaselineFixtureWorkflows:
    """Build deterministic approval workflow records from snapshot baselines."""

    def build(
        self,
        *,
        planner_snapshot_baselines: dict[str, Any],
        approval_overrides: dict[str, dict[str, Any]] | None = None,
        run_id: str = "v3_1_phase_4_baseline_fixture_workflows",
    ) -> dict[str, Any]:
        overrides = approval_overrides or {}
        snapshots = list(planner_snapshot_baselines.get("snapshots") or [])
        fixtures = [
            _fixture_from_snapshot(snapshot=snapshot, approval_override=_override_for(snapshot, overrides))
            for snapshot in sorted(snapshots, key=lambda item: str(item.get("snapshot_id") or item.get("stable_key") or ""))
        ]
        counts = Counter(fixture["approval_state"] for fixture in fixtures)
        production_affected_count = sum(1 for fixture in fixtures if fixture["production_output_affected"])
        envelope = {
            "schema_version": "v3_1.baseline_fixture_workflows.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "run": {
                "run_id": run_id,
                "source_snapshot_schema": planner_snapshot_baselines.get("schema_version"),
                "source_snapshot_hash": planner_snapshot_baselines.get("deterministic_hash"),
                "fixture_count": len(fixtures),
                "approval_override_count": len(overrides),
            },
            "summary": {
                "total_fixtures": len(fixtures),
                "pending_review_count": counts["pending_review"],
                "approved_candidate_count": counts["approved_candidate"],
                "approved_baseline_count": counts["approved_baseline"],
                "rejected_count": counts["rejected"],
                "unsupported_count": counts["unsupported"],
                "blocked_count": counts["blocked"],
                "insufficient_data_count": counts["insufficient_data"],
                "archived_count": counts["archived"],
                "production_affected_count": production_affected_count,
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "deterministic": True,
            },
            "approval_state_counts": {
                state: counts[state]
                for state in FIXTURE_WORKFLOW_STATES
            },
            "fixtures": fixtures,
            "safety_confirmations": {
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "legacy_planner_ownership_preserved": True,
                "planner_output_replaced": False,
                "runtime_state_mutated": False,
                "approval_status_authorizes_production_routing": False,
                "automatic_drift_acceptance": False,
                "unsupported_states_hidden": False,
                "blocked_states_hidden": False,
            },
            "metadata": {
                "source": "v3_1_baseline_fixture_workflows",
                "observational_only": True,
                "production_consumer": False,
                "production_behavior_changed": False,
                "planner_remap_performed": False,
                "production_default_routing_authorized": False,
                "stable_workflow_generation_token": STABLE_WORKFLOW_GENERATION_TOKEN,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_sample_baseline_fixture_workflow_inputs() -> dict[str, Any]:
    dual_run = build_sample_planner_snapshot_baseline_inputs()
    return V31PlannerSnapshotBaselines().build(
        dual_run_comparison=dual_run,
        run_id="v3_1_phase_4_snapshot_workflow_sample",
    )


def _fixture_from_snapshot(*, snapshot: dict[str, Any], approval_override: dict[str, Any] | None) -> dict[str, Any]:
    state, reason_codes = _approval_state(snapshot=snapshot, approval_override=approval_override)
    snapshot_id = str(snapshot.get("snapshot_id"))
    fixture_seed = {
        "snapshot_id": snapshot_id,
        "generation_token": STABLE_WORKFLOW_GENERATION_TOKEN,
    }
    unsupported = state == "unsupported" or bool(snapshot.get("unsupported", False))
    blocked = state == "blocked" or bool(snapshot.get("blocked", False))
    review_notes = list((approval_override or {}).get("review_notes") or [])
    return {
        "fixture_id": f"v3_1_fixture_{deterministic_hash(fixture_seed)[:16]}",
        "associated_snapshot_id": snapshot_id,
        "snapshot_stable_key": snapshot.get("stable_key"),
        "approval_state": state,
        "baseline_classification": snapshot.get("baseline_readiness"),
        "comparison_readiness": {
            "comparison_eligible": bool(snapshot.get("comparison_eligible", False)),
            "baseline_candidate": bool(snapshot.get("baseline_candidate", False)),
            "dual_run_drift_classification": (snapshot.get("dual_run_comparison_state") or {}).get("drift_classification"),
        },
        "unsupported": unsupported,
        "blocked": blocked,
        "unsupported_or_blocked_reason": snapshot.get("unsupported_or_blocked_reason"),
        "review_notes": review_notes,
        "reason_codes": reason_codes,
        "production_ownership_state": {
            "owner": "legacy",
            "legacy_controlled": True,
            "trusted_default_routing": False,
            "approval_authorizes_production_routing": False,
        },
        "production_output_affected": False,
        "generation": {
            "strategy": "stable_token_and_sorted_json_hash",
            "token": STABLE_WORKFLOW_GENERATION_TOKEN,
            "timestamp_strategy": "report_level_deterministic_token",
        },
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
        },
    }


def _approval_state(*, snapshot: dict[str, Any], approval_override: dict[str, Any] | None) -> tuple[str, list[str]]:
    baseline_readiness = str(snapshot.get("baseline_readiness"))
    if baseline_readiness == "unsupported":
        return "unsupported", ["unsupported_state_visible"]
    if baseline_readiness == "blocked":
        return "blocked", ["blocked_state_visible"]
    if baseline_readiness == "insufficient_data":
        return "insufficient_data", ["insufficient_data_visible"]
    if approval_override:
        requested = str(approval_override.get("approval_state", ""))
        if requested in FIXTURE_WORKFLOW_STATES and requested not in {"unsupported", "blocked", "insufficient_data"}:
            return requested, [f"explicit_{requested}"]
        return "pending_review", ["invalid_or_unsafe_approval_override"]
    if baseline_readiness in {"baseline_candidate", "comparison_ready"}:
        return "pending_review", [f"{baseline_readiness}_requires_review"]
    if baseline_readiness == "legacy_only":
        return "insufficient_data", ["legacy_only_missing_trusted_shadow"]
    if baseline_readiness == "shadow_only":
        return "insufficient_data", ["shadow_only_missing_legacy_summary"]
    return "insufficient_data", ["unknown_baseline_readiness"]


def _override_for(snapshot: dict[str, Any], overrides: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    snapshot_id = str(snapshot.get("snapshot_id"))
    stable_key = str(snapshot.get("stable_key"))
    if snapshot_id in overrides:
        return overrides[snapshot_id]
    if stable_key in overrides:
        return overrides[stable_key]
    return None


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
