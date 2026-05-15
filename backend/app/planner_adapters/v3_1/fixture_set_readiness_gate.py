"""Deterministic fixture-set approval readiness gate.

The gate combines reviewed inputs, persisted fixture sets, and policy outcomes
to determine future approval-review readiness. It never authorizes runtime
routing or changes production planner ownership.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


FIXTURE_SET_READINESS_CLASSIFICATIONS = (
    "ready_for_approval_review",
    "blocked_missing_inputs",
    "blocked_policy_failure",
    "blocked_malformed_inputs",
    "blocked_duplicate_inputs",
    "blocked_insufficient_review",
)
STABLE_READINESS_GATE_TOKEN = "v3_1_phase_7_fixture_set_readiness_gate_token"


def build_fixture_set_readiness_gate(
    *,
    reviewed_fixture_inputs: dict[str, Any] | list[dict[str, Any]],
    persisted_fixture_sets: dict[str, Any],
    review_policy_evaluation: dict[str, Any],
    baseline_fixture_workflows: dict[str, Any] | None = None,
    run_id: str = "v3_1_phase_7_fixture_set_readiness_gate",
) -> dict[str, Any]:
    normalized_inputs = _normalized_inputs(reviewed_fixture_inputs)
    input_by_id = {str(row.get("normalized_fixture_id")): row for row in normalized_inputs}
    policy_by_set = {
        str(row.get("fixture_set_id")): row
        for row in review_policy_evaluation.get("evaluations", [])
    }
    workflow_by_fixture_id = {
        str(row.get("fixture_id")): row
        for row in (baseline_fixture_workflows or {}).get("fixtures", [])
    }
    records = [
        _readiness_record(
            fixture_set=fixture_set,
            input_by_id=input_by_id,
            policy=policy_by_set.get(str(fixture_set.get("fixture_set_id"))),
            workflow_by_fixture_id=workflow_by_fixture_id,
        )
        for fixture_set in sorted(persisted_fixture_sets.get("fixture_sets", []), key=lambda row: str(row.get("fixture_set_id") or ""))
    ]
    counts = Counter(row["readiness_classification"] for row in records)
    block_reasons = Counter(reason for row in records for reason in row["block_reason_codes"])
    envelope = {
        "schema_version": "v3_1.fixture_set_readiness_gate.1",
        "run": {
            "run_id": run_id,
            "fixture_set_count": len(records),
            "reviewed_input_count": len(normalized_inputs),
            "policy_evaluation_count": len(policy_by_set),
            "workflow_fixture_count": len(workflow_by_fixture_id),
        },
        "summary": {
            "total_fixture_sets_evaluated": len(records),
            "ready_count": counts["ready_for_approval_review"],
            "blocked_count": len(records) - counts["ready_for_approval_review"],
            "production_affected_count": sum(1 for row in records if row["production_output_affected"]),
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "readiness_classification_counts": {
            classification: counts[classification]
            for classification in FIXTURE_SET_READINESS_CLASSIFICATIONS
        },
        "block_reason_counts": dict(sorted(block_reasons.items())),
        "readiness_records": records,
        "input_consumption": {
            "reviewed_fixture_inputs_hash": _source_hash(reviewed_fixture_inputs),
            "persisted_fixture_sets_hash": persisted_fixture_sets.get("deterministic_hash"),
            "review_policy_evaluation_hash": review_policy_evaluation.get("deterministic_hash"),
            "baseline_fixture_workflows_hash": (baseline_fixture_workflows or {}).get("deterministic_hash"),
        },
        "safety_confirmations": {
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "legacy_planner_ownership_preserved": True,
            "runtime_state_mutated": False,
            "readiness_authorizes_production_routing": False,
        },
        "metadata": {
            "source": "v3_1_fixture_set_readiness_gate",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_READINESS_GATE_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _readiness_record(
    *,
    fixture_set: dict[str, Any],
    input_by_id: dict[str, dict[str, Any]],
    policy: dict[str, Any] | None,
    workflow_by_fixture_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    fixture_ids = [str(value) for value in fixture_set.get("associated_fixture_ids", [])]
    input_statuses = {
        fixture_id: (input_by_id.get(_normalize_id(fixture_id)) or {}).get("status", "missing_source")
        for fixture_id in fixture_ids
    }
    workflow_states = {
        fixture_id: (workflow_by_fixture_id.get(fixture_id) or {}).get("approval_state", "unknown")
        for fixture_id in fixture_ids
    }
    classification, reasons = _classify(fixture_set=fixture_set, policy=policy, input_statuses=input_statuses, workflow_states=workflow_states)
    return {
        "fixture_set_id": fixture_set.get("fixture_set_id"),
        "set_key": fixture_set.get("set_key"),
        "readiness_classification": classification,
        "associated_fixture_ids": fixture_ids,
        "input_statuses": dict(sorted(input_statuses.items())),
        "policy_outcome": (policy or {}).get("policy_outcome", "missing"),
        "workflow_states": dict(sorted(workflow_states.items())),
        "block_reason_codes": reasons,
        "non_production_authorization": {
            "readiness_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "trusted_default_routing": False,
        },
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _classify(
    *,
    fixture_set: dict[str, Any],
    policy: dict[str, Any] | None,
    input_statuses: dict[str, str],
    workflow_states: dict[str, str],
) -> tuple[str, list[str]]:
    statuses = Counter(input_statuses.values())
    if not input_statuses or statuses["missing_source"]:
        return "blocked_missing_inputs", ["missing_reviewed_fixture_input"]
    if statuses["malformed"]:
        return "blocked_malformed_inputs", ["malformed_reviewed_fixture_input"]
    if statuses["duplicate"]:
        return "blocked_duplicate_inputs", ["duplicate_reviewed_fixture_input"]
    policy_outcome = str((policy or {}).get("policy_outcome") or "missing")
    if policy_outcome != "passes_policy":
        return "blocked_policy_failure", [f"policy_{policy_outcome}"]
    if any(status != "reviewed" for status in input_statuses.values()):
        return "blocked_insufficient_review", ["input_not_reviewed"]
    if any(state in {"unsupported", "blocked", "insufficient_data", "unknown"} for state in workflow_states.values()):
        return "blocked_insufficient_review", ["workflow_not_review_ready"]
    if fixture_set.get("unsupported") or fixture_set.get("blocked"):
        return "blocked_policy_failure", ["fixture_set_not_governance_ready"]
    return "ready_for_approval_review", ["all_inputs_reviewed_policy_passed"]


def _normalized_inputs(reviewed_fixture_inputs: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(reviewed_fixture_inputs, dict):
        return list(reviewed_fixture_inputs.get("normalized_fixture_inputs") or [])
    return list(reviewed_fixture_inputs)


def _source_hash(value: Any) -> str | None:
    if isinstance(value, dict) and value.get("deterministic_hash"):
        return str(value["deterministic_hash"])
    return deterministic_hash({"source": _canonicalize(value)}) if value is not None else None


def _normalize_id(value: str) -> str:
    return "_".join(value.strip().lower().replace("\\", "/").replace(":", "_").split())


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _canonicalize(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return sorted(
            (_canonicalize(item) for item in value),
            key=lambda item: deterministic_hash({"item": item}),
        )
    return value
