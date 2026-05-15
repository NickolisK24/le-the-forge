"""Deterministic approval manifest candidate generation.

Manifest candidates are governance artifacts derived from fixture-set readiness
records. They never approve production routing or replace legacy planner
ownership.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


APPROVAL_MANIFEST_CANDIDATE_STATUSES = (
    "candidate_ready",
    "excluded_not_ready",
    "excluded_missing_readiness",
    "excluded_invalid_policy_state",
)
STABLE_APPROVAL_MANIFEST_TOKEN = "v3_1_phase_8_approval_manifest_candidates_token"


def build_approval_manifest_candidates(
    *,
    readiness_gate: dict[str, Any],
    run_id: str = "v3_1_phase_8_approval_manifest_candidates",
) -> dict[str, Any]:
    records = [
        _candidate_record(record)
        for record in sorted(readiness_gate.get("readiness_records", []), key=lambda row: str(row.get("fixture_set_id") or ""))
    ]
    counts = Counter(row["candidate_status"] for row in records)
    exclusion_reasons = Counter(reason for row in records if row["candidate_status"] != "candidate_ready" for reason in row["reason_codes"])
    envelope = {
        "schema_version": "v3_1.approval_manifest_candidates.1",
        "run": {
            "run_id": run_id,
            "readiness_record_count": len(records),
            "source_readiness_hash": readiness_gate.get("deterministic_hash"),
        },
        "summary": {
            "total_readiness_records_evaluated": len(records),
            "candidate_ready_count": counts["candidate_ready"],
            "excluded_count": len(records) - counts["candidate_ready"],
            "production_affected_count": sum(1 for row in records if row["production_output_affected"]),
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "candidate_status_counts": {
            status: counts[status]
            for status in APPROVAL_MANIFEST_CANDIDATE_STATUSES
        },
        "exclusion_reason_counts": dict(sorted(exclusion_reasons.items())),
        "manifest_candidates": records,
        "candidate_ready_manifest": [record for record in records if record["candidate_status"] == "candidate_ready"],
        "input_consumption": {
            "readiness_gate_hash": readiness_gate.get("deterministic_hash"),
            "readiness_gate_schema": readiness_gate.get("schema_version"),
        },
        "safety_confirmations": {
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "legacy_planner_ownership_preserved": True,
            "runtime_state_mutated": False,
            "approval_manifest_authorizes_production_routing": False,
            "manifest_candidates_are_production_approved": False,
        },
        "metadata": {
            "source": "v3_1_approval_manifest_candidates",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_APPROVAL_MANIFEST_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _candidate_record(readiness_record: dict[str, Any]) -> dict[str, Any]:
    status, reason_codes = _candidate_status(readiness_record)
    fixture_set_id = str(readiness_record.get("fixture_set_id") or "")
    seed = {
        "fixture_set_id": fixture_set_id,
        "generation_token": STABLE_APPROVAL_MANIFEST_TOKEN,
    }
    return {
        "manifest_candidate_id": f"v3_1_manifest_candidate_{deterministic_hash(seed)[:16]}",
        "fixture_set_id": readiness_record.get("fixture_set_id"),
        "candidate_status": status,
        "source_summary": {
            "set_key": readiness_record.get("set_key"),
            "associated_fixture_ids": list(readiness_record.get("associated_fixture_ids") or []),
            "input_statuses": deepcopy(readiness_record.get("input_statuses") or {}),
        },
        "policy_summary": {
            "policy_outcome": readiness_record.get("policy_outcome"),
            "valid_policy_state": readiness_record.get("policy_outcome") == "passes_policy",
        },
        "readiness_summary": {
            "readiness_classification": readiness_record.get("readiness_classification"),
            "block_reason_codes": list(readiness_record.get("block_reason_codes") or []),
        },
        "authorization_status": {
            "candidate_is_production_approved": False,
            "candidate_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "trusted_default_routing": False,
        },
        "reason_codes": reason_codes,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _candidate_status(readiness_record: dict[str, Any]) -> tuple[str, list[str]]:
    readiness = readiness_record.get("readiness_classification")
    policy = readiness_record.get("policy_outcome")
    if not readiness:
        return "excluded_missing_readiness", ["missing_readiness_classification"]
    if readiness == "ready_for_approval_review" and policy != "passes_policy":
        return "excluded_invalid_policy_state", [f"invalid_policy_state_{policy or 'missing'}"]
    if readiness != "ready_for_approval_review":
        return "excluded_not_ready", list(readiness_record.get("block_reason_codes") or [f"readiness_{readiness}"])
    return "candidate_ready", ["ready_for_approval_review_policy_passed"]
