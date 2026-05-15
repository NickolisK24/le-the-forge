"""Deterministic persisted fixture-set infrastructure.

Persisted fixture sets are migration-governance groupings over baseline fixture
workflow records. They do not authorize runtime routing or production planner
replacement.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .baseline_fixture_workflows import (
    V31BaselineFixtureWorkflows,
    build_sample_baseline_fixture_workflow_inputs,
)
from .trusted_shadow_consumption import deterministic_hash


FIXTURE_SET_LIFECYCLE_STATES = (
    "draft",
    "review_ready",
    "partially_approved",
    "approved_candidate",
    "archived",
    "blocked",
    "unsupported",
    "insufficient_data",
)
STABLE_FIXTURE_SET_GENERATION_TOKEN = "v3_1_phase_5_persisted_fixture_set_token"


class V31PersistedFixtureSets:
    """Build deterministic persisted fixture-set records from workflow fixtures."""

    def build(
        self,
        *,
        baseline_fixture_workflows: dict[str, Any],
        set_definitions: list[dict[str, Any]] | None = None,
        run_id: str = "v3_1_phase_5_persisted_fixture_sets",
    ) -> dict[str, Any]:
        fixtures = list(baseline_fixture_workflows.get("fixtures") or [])
        fixture_by_id = {str(fixture.get("fixture_id")): fixture for fixture in fixtures}
        definitions = set_definitions or [_default_definition(fixtures)]
        fixture_sets = [
            _fixture_set_from_definition(definition=definition, fixture_by_id=fixture_by_id)
            for definition in sorted(definitions, key=lambda row: str(row.get("set_key") or ""))
        ]
        counts = Counter(row["lifecycle_state"] for row in fixture_sets)
        policy_counts = Counter(row["policy_evaluation_status"] for row in fixture_sets)
        production_affected_count = sum(1 for row in fixture_sets if row["production_output_affected"])
        envelope = {
            "schema_version": "v3_1.persisted_fixture_sets.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "run": {
                "run_id": run_id,
                "source_fixture_workflow_schema": baseline_fixture_workflows.get("schema_version"),
                "source_fixture_workflow_hash": baseline_fixture_workflows.get("deterministic_hash"),
                "fixture_set_count": len(fixture_sets),
            },
            "summary": {
                "total_fixture_sets": len(fixture_sets),
                "draft_count": counts["draft"],
                "review_ready_count": counts["review_ready"],
                "partially_approved_count": counts["partially_approved"],
                "approved_candidate_count": counts["approved_candidate"],
                "archived_count": counts["archived"],
                "blocked_count": counts["blocked"],
                "unsupported_count": counts["unsupported"],
                "insufficient_data_count": counts["insufficient_data"],
                "policy_pass_count": policy_counts["passes_policy"],
                "requires_review_count": policy_counts["requires_review"],
                "production_affected_count": production_affected_count,
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "deterministic": True,
            },
            "lifecycle_state_counts": {
                state: counts[state]
                for state in FIXTURE_SET_LIFECYCLE_STATES
            },
            "policy_evaluation_status_counts": dict(sorted(policy_counts.items())),
            "fixture_sets": fixture_sets,
            "safety_confirmations": {
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "legacy_planner_ownership_preserved": True,
                "runtime_state_mutated": False,
                "fixture_set_authorizes_production_routing": False,
                "unsupported_states_hidden": False,
                "blocked_states_hidden": False,
            },
            "metadata": {
                "source": "v3_1_persisted_fixture_sets",
                "observational_only": True,
                "production_consumer": False,
                "production_behavior_changed": False,
                "planner_remap_performed": False,
                "production_default_routing_authorized": False,
                "stable_fixture_set_generation_token": STABLE_FIXTURE_SET_GENERATION_TOKEN,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_sample_persisted_fixture_set_inputs() -> dict[str, Any]:
    snapshots = build_sample_baseline_fixture_workflow_inputs()
    return V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines=snapshots,
        run_id="v3_1_phase_5_fixture_set_workflow_sample",
    )


def _default_definition(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "set_key": "sample_migration_readiness_set",
        "fixture_ids": sorted(str(fixture.get("fixture_id")) for fixture in fixtures),
    }


def _fixture_set_from_definition(*, definition: dict[str, Any], fixture_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    set_key = str(definition.get("set_key") or "fixture_set")
    requested_ids = sorted(str(value) for value in definition.get("fixture_ids") or [])
    fixtures = [fixture_by_id[fixture_id] for fixture_id in requested_ids if fixture_id in fixture_by_id]
    missing_ids = [fixture_id for fixture_id in requested_ids if fixture_id not in fixture_by_id]
    state, reason_codes = _lifecycle_state(definition=definition, fixtures=fixtures, missing_ids=missing_ids)
    fixture_set_seed = {
        "set_key": set_key,
        "fixture_ids": requested_ids,
        "generation_token": STABLE_FIXTURE_SET_GENERATION_TOKEN,
    }
    unsupported = state == "unsupported" or any(fixture.get("unsupported") for fixture in fixtures)
    blocked = state == "blocked" or any(fixture.get("blocked") for fixture in fixtures)
    return {
        "fixture_set_id": f"v3_1_fixture_set_{deterministic_hash(fixture_set_seed)[:16]}",
        "set_key": set_key,
        "associated_fixture_ids": requested_ids,
        "resolved_fixture_ids": sorted(str(fixture.get("fixture_id")) for fixture in fixtures),
        "missing_fixture_ids": missing_ids,
        "lifecycle_state": state,
        "policy_evaluation_status": _policy_status_for_lifecycle(state),
        "unsupported": unsupported,
        "blocked": blocked,
        "deterministic_reason_codes": reason_codes,
        "fixture_state_counts": dict(sorted(Counter(str(fixture.get("approval_state")) for fixture in fixtures).items())),
        "production_ownership_metadata": {
            "owner": "legacy",
            "legacy_controlled": True,
            "trusted_default_routing": False,
            "fixture_set_authorizes_production_routing": False,
        },
        "production_output_affected": False,
        "generation": {
            "strategy": "stable_token_fixture_membership_hash",
            "token": STABLE_FIXTURE_SET_GENERATION_TOKEN,
            "timestamp_strategy": "report_level_deterministic_token",
        },
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
        },
    }


def _lifecycle_state(*, definition: dict[str, Any], fixtures: list[dict[str, Any]], missing_ids: list[str]) -> tuple[str, list[str]]:
    requested = str(definition.get("lifecycle_state") or "")
    if requested in FIXTURE_SET_LIFECYCLE_STATES:
        return requested, [f"explicit_{requested}"]
    if missing_ids or not fixtures:
        return "insufficient_data", ["missing_or_empty_fixture_membership"]
    states = Counter(str(fixture.get("approval_state")) for fixture in fixtures)
    if states["blocked"]:
        return "blocked", ["blocked_fixture_present"]
    if states["unsupported"]:
        return "unsupported", ["unsupported_fixture_present"]
    if states["insufficient_data"]:
        return "insufficient_data", ["insufficient_data_fixture_present"]
    if states["archived"] == len(fixtures):
        return "archived", ["all_fixtures_archived"]
    approved = states["approved_candidate"] + states["approved_baseline"]
    if approved == len(fixtures):
        return "approved_candidate", ["all_fixtures_approved_for_candidate_review"]
    if approved:
        return "partially_approved", ["mixed_approval_states"]
    if states["pending_review"] == len(fixtures):
        return "review_ready", ["all_fixtures_pending_review"]
    return "draft", ["fixture_set_requires_review_setup"]


def _policy_status_for_lifecycle(lifecycle_state: str) -> str:
    if lifecycle_state == "approved_candidate":
        return "passes_policy"
    if lifecycle_state in {"review_ready", "partially_approved", "draft", "archived"}:
        return "requires_review"
    if lifecycle_state in {"blocked", "unsupported", "insufficient_data"}:
        return lifecycle_state
    return "not_evaluated"


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
