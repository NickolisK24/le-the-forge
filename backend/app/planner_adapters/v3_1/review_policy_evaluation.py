"""Deterministic review policy evaluation infrastructure."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .persisted_fixture_sets import V31PersistedFixtureSets, build_sample_persisted_fixture_set_inputs
from .trusted_shadow_consumption import deterministic_hash


REVIEW_POLICY_OUTCOMES = (
    "passes_policy",
    "requires_review",
    "blocked",
    "unsupported",
    "insufficient_data",
    "not_evaluated",
)
STABLE_POLICY_GENERATION_TOKEN = "v3_1_phase_5_review_policy_evaluation_token"


class V31ReviewPolicyEvaluation:
    """Evaluate persisted fixture sets against explicit review policy metadata."""

    def evaluate(
        self,
        *,
        persisted_fixture_sets: dict[str, Any],
        policy: dict[str, Any] | None = None,
        run_id: str = "v3_1_phase_5_review_policy_evaluation",
    ) -> dict[str, Any]:
        policy_record = _normalize_policy(policy)
        evaluations = [
            _evaluate_fixture_set(fixture_set=row, policy=policy_record)
            for row in sorted(persisted_fixture_sets.get("fixture_sets") or [], key=lambda item: str(item.get("fixture_set_id") or ""))
        ]
        counts = Counter(row["policy_outcome"] for row in evaluations)
        production_affected_count = sum(1 for row in evaluations if row["production_output_affected"])
        envelope = {
            "schema_version": "v3_1.review_policy_evaluation.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "run": {
                "run_id": run_id,
                "source_fixture_set_schema": persisted_fixture_sets.get("schema_version"),
                "source_fixture_set_hash": persisted_fixture_sets.get("deterministic_hash"),
                "evaluation_count": len(evaluations),
            },
            "policy": policy_record,
            "summary": {
                "total_evaluations": len(evaluations),
                "policy_pass_count": counts["passes_policy"],
                "requires_review_count": counts["requires_review"],
                "blocked_count": counts["blocked"],
                "unsupported_count": counts["unsupported"],
                "insufficient_data_count": counts["insufficient_data"],
                "not_evaluated_count": counts["not_evaluated"],
                "production_affected_count": production_affected_count,
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "deterministic": True,
            },
            "policy_outcome_counts": {
                outcome: counts[outcome]
                for outcome in REVIEW_POLICY_OUTCOMES
            },
            "evaluations": evaluations,
            "safety_confirmations": {
                "production_output_affected": False,
                "production_behavior_changed": False,
                "trusted_data_default_truth": False,
                "legacy_planner_ownership_preserved": True,
                "runtime_state_mutated": False,
                "policy_authorizes_production_routing": False,
                "hidden_heuristics_used": False,
                "unsupported_states_hidden": False,
                "blocked_states_hidden": False,
            },
            "metadata": {
                "source": "v3_1_review_policy_evaluation",
                "observational_only": True,
                "production_consumer": False,
                "production_behavior_changed": False,
                "planner_remap_performed": False,
                "production_default_routing_authorized": False,
                "stable_policy_generation_token": STABLE_POLICY_GENERATION_TOKEN,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_sample_review_policy_inputs() -> dict[str, Any]:
    workflows = build_sample_persisted_fixture_set_inputs()
    return V31PersistedFixtureSets().build(
        baseline_fixture_workflows=workflows,
        run_id="v3_1_phase_5_review_policy_fixture_set_sample",
    )


def _normalize_policy(policy: dict[str, Any] | None) -> dict[str, Any]:
    policy = policy or {}
    return {
        "policy_id": str(policy.get("policy_id") or "v3_1_default_review_policy"),
        "policy_version": str(policy.get("policy_version") or "1"),
        "requires_no_blocked": bool(policy.get("requires_no_blocked", True)),
        "requires_no_unsupported": bool(policy.get("requires_no_unsupported", True)),
        "requires_no_insufficient_data": bool(policy.get("requires_no_insufficient_data", True)),
        "requires_approved_candidate_state": bool(policy.get("requires_approved_candidate_state", True)),
        "production_routing_authorized": False,
        "generation_token": STABLE_POLICY_GENERATION_TOKEN,
    }


def _evaluate_fixture_set(*, fixture_set: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    outcome, reason_codes = _policy_outcome(fixture_set=fixture_set, policy=policy)
    return {
        "fixture_set_id": fixture_set.get("fixture_set_id"),
        "set_key": fixture_set.get("set_key"),
        "lifecycle_state": fixture_set.get("lifecycle_state"),
        "policy_outcome": outcome,
        "review_readiness_classification": outcome,
        "unsupported": bool(fixture_set.get("unsupported", False)),
        "blocked": bool(fixture_set.get("blocked", False)),
        "deterministic_reason_codes": reason_codes,
        "production_ownership_metadata": {
            "owner": "legacy",
            "legacy_controlled": True,
            "trusted_default_routing": False,
            "policy_authorizes_production_routing": False,
        },
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
        },
    }


def _policy_outcome(*, fixture_set: dict[str, Any], policy: dict[str, Any]) -> tuple[str, list[str]]:
    state = str(fixture_set.get("lifecycle_state"))
    if state == "blocked" or (policy["requires_no_blocked"] and fixture_set.get("blocked")):
        return "blocked", ["blocked_fixture_set_visible"]
    if state == "unsupported" or (policy["requires_no_unsupported"] and fixture_set.get("unsupported")):
        return "unsupported", ["unsupported_fixture_set_visible"]
    if state == "insufficient_data" or (policy["requires_no_insufficient_data"] and state == "insufficient_data"):
        return "insufficient_data", ["insufficient_data_visible"]
    if state == "approved_candidate" and policy["requires_approved_candidate_state"]:
        return "passes_policy", ["approved_candidate_fixture_set"]
    if state in {"review_ready", "partially_approved", "draft", "archived"}:
        return "requires_review", [f"{state}_requires_review"]
    return "not_evaluated", ["unrecognized_fixture_set_lifecycle"]


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
