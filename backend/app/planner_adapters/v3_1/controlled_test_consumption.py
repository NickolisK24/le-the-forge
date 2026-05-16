"""Controlled test consumption adapter for v3.1 manifests.

This module is runtime-isolated governance infrastructure. It can consume
eligible non-production manifests only when explicitly invoked in controlled
test mode, and it never connects to production planner routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


CONTROLLED_TEST_CONSUMPTION_STATUSES = (
    "consumed_in_controlled_test",
    "blocked_not_eligible",
    "blocked_invalid_authorization_state",
    "blocked_missing_manifest",
    "blocked_missing_eligibility_record",
    "blocked_runtime_consumption_disabled",
)
STABLE_CONTROLLED_TEST_CONSUMPTION_TOKEN = "v3_1_phase_17_controlled_test_consumption_token"


def build_controlled_test_consumption(
    *,
    manifest_consumption_eligibility: dict[str, Any],
    admission_aware_manifest_serialization: dict[str, Any],
    controlled_test_mode: bool = False,
    run_id: str = "v3_1_phase_17_controlled_test_consumption",
) -> dict[str, Any]:
    """Build controlled test consumption records from eligible manifests only."""

    eligibility_by_manifest = {
        str(row.get("manifest_id") or ""): deepcopy(row)
        for row in manifest_consumption_eligibility.get("eligibility_records", [])
        if row.get("manifest_id")
    }
    manifests_by_id = {
        str(row.get("manifest_id") or ""): deepcopy(row)
        for row in admission_aware_manifest_serialization.get("serialized_manifests", [])
        if row.get("manifest_id")
    }
    manifest_ids = sorted(set(eligibility_by_manifest) | set(manifests_by_id))
    if not manifest_ids:
        manifest_ids = [""]
    records = [
        _consumption_record(
            manifest_id=manifest_id,
            eligibility=eligibility_by_manifest.get(manifest_id),
            manifest=manifests_by_id.get(manifest_id),
            controlled_test_mode=controlled_test_mode,
        )
        for manifest_id in manifest_ids
    ]
    counts = Counter(row["controlled_consumption_status"] for row in records)
    blocker_reasons = Counter(reason for row in records for reason in row["blockers"])
    envelope = {
        "schema_version": "v3_1.controlled_test_consumption.1",
        "run": {
            "run_id": run_id,
            "controlled_test_mode": controlled_test_mode,
            "eligibility_record_count": len(eligibility_by_manifest),
            "manifest_record_count": len(manifests_by_id),
            "manifest_consumption_eligibility_hash": manifest_consumption_eligibility.get("deterministic_hash"),
            "admission_aware_manifest_serialization_hash": admission_aware_manifest_serialization.get("deterministic_hash"),
        },
        "summary": {
            "manifests_evaluated": len(records),
            "controlled_test_consumed_count": counts["consumed_in_controlled_test"],
            "blocked_count": len(records) - counts["consumed_in_controlled_test"],
            "runtime_production_consumption_enabled": False,
            "runtime_manifest_consumption_enabled": False,
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "controlled_consumption_status_counts": {
            status: counts[status]
            for status in CONTROLLED_TEST_CONSUMPTION_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "controlled_consumption_records": records,
        "safety_confirmations": {
            "controlled_consumption_authorizes_production_routing": False,
            "controlled_consumption_is_production_consumption": False,
            "runtime_production_consumption_enabled": False,
            "runtime_manifest_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_controlled_test_consumption",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_CONTROLLED_TEST_CONSUMPTION_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _consumption_record(
    *,
    manifest_id: str,
    eligibility: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    controlled_test_mode: bool,
) -> dict[str, Any]:
    status, blockers = _status(
        eligibility=eligibility,
        manifest=manifest,
        controlled_test_mode=controlled_test_mode,
    )
    fixture_set_id = (manifest or eligibility or {}).get("fixture_set_id")
    authorization_state = ((manifest or {}).get("authorization_status") or {}).get(
        "authorization_state",
        (eligibility or {}).get("authorization_state"),
    )
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "controlled_test_mode": controlled_test_mode,
        "token": STABLE_CONTROLLED_TEST_CONSUMPTION_TOKEN,
    }
    return {
        "controlled_consumption_id": f"v3_1_controlled_consumption_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id or None,
        "fixture_set_id": fixture_set_id,
        "eligibility_status": (eligibility or {}).get("eligibility_status"),
        "authorization_state": authorization_state,
        "controlled_consumption_status": status,
        "blockers": blockers,
        "controlled_test_mode": controlled_test_mode,
        "not_production_consumption": True,
        "controlled_consumption_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _status(
    *,
    eligibility: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    controlled_test_mode: bool,
) -> tuple[str, list[str]]:
    if not controlled_test_mode:
        return "blocked_runtime_consumption_disabled", ["controlled_test_mode_not_enabled"]
    if eligibility is None:
        return "blocked_missing_eligibility_record", ["missing_manifest_eligibility_record"]
    if manifest is None:
        return "blocked_missing_manifest", ["missing_serialized_manifest"]
    if eligibility.get("eligibility_status") != "eligible_for_controlled_test_consumption":
        return "blocked_not_eligible", list(eligibility.get("blockers") or [f"eligibility_{eligibility.get('eligibility_status')}"])
    if not _is_non_production_authoritative(manifest):
        return "blocked_invalid_authorization_state", ["manifest_not_non_production_authoritative"]
    return "consumed_in_controlled_test", []


def _is_non_production_authoritative(manifest: dict[str, Any]) -> bool:
    authorization = manifest.get("authorization_status") or {}
    return (
        manifest.get("non_production_authoritative") is True
        and authorization.get("authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
        and authorization.get("manifest_authorizes_production_routing") is False
        and authorization.get("manifest_is_production_approved") is False
        and authorization.get("manifest_is_production_authoritative") is False
    )
