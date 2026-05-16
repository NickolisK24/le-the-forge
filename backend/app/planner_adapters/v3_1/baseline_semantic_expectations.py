"""Baseline semantic expectation enrichment for v3.1 governance.

Expectation records are derived from planner-adjacent baseline snapshots. They
preserve unavailable fields explicitly and never authorize production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


BASELINE_SEMANTIC_EXPECTATION_STATUSES = (
    "semantic_expectations_available",
    "semantic_expectations_partial",
    "blocked_missing_baseline_snapshot",
    "blocked_unstable_baseline_identity",
    "blocked_missing_required_trace",
)
STABLE_BASELINE_SEMANTIC_EXPECTATION_TOKEN = "v3_1_phase_21_baseline_semantic_expectations_token"


def build_baseline_semantic_expectations(
    *,
    planner_snapshot_baselines: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_21_baseline_semantic_expectations",
) -> dict[str, Any]:
    """Build deterministic semantic expectation records from baseline snapshots."""

    snapshots = _baseline_snapshots(planner_snapshot_baselines)
    expectation_records = [
        _expectation_record(snapshot)
        for snapshot in sorted(snapshots, key=_snapshot_sort_key)
    ]
    if not expectation_records:
        expectation_records = [_missing_baseline_record()]

    counts = Counter(record["semantic_expectation_status"] for record in expectation_records)
    unavailable_fields = Counter(field for record in expectation_records for field in record["unavailable_semantic_fields"])
    blocker_reasons = Counter(reason for record in expectation_records for reason in record["blockers"])
    baseline_hash = planner_snapshot_baselines.get("deterministic_hash") if isinstance(planner_snapshot_baselines, dict) else None
    envelope = {
        "schema_version": "v3_1.baseline_semantic_expectations.1",
        "run": {
            "run_id": run_id,
            "baseline_snapshot_count": len(snapshots),
            "planner_snapshot_baselines_hash": baseline_hash,
        },
        "summary": {
            "baseline_records_evaluated": len(expectation_records),
            "expectations_available_count": counts["semantic_expectations_available"],
            "partial_count": counts["semantic_expectations_partial"],
            "blocked_count": (
                counts["blocked_missing_baseline_snapshot"]
                + counts["blocked_unstable_baseline_identity"]
                + counts["blocked_missing_required_trace"]
            ),
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "semantic_expectation_status_counts": {
            status: counts[status]
            for status in BASELINE_SEMANTIC_EXPECTATION_STATUSES
        },
        "unavailable_semantic_field_counts": dict(sorted(unavailable_fields.items())),
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "baseline_semantic_expectation_records": expectation_records,
        "safety_confirmations": {
            "semantic_expectations_authorize_production_routing": False,
            "semantic_expectations_are_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_baseline_semantic_expectations",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_BASELINE_SEMANTIC_EXPECTATION_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _baseline_snapshots(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("snapshots", [])]


def _expectation_record(snapshot: dict[str, Any]) -> dict[str, Any]:
    expected_identity_fields = _identity_fields(snapshot)
    expected_manifest_trace_fields = _manifest_trace_fields(snapshot)
    expected_fixture_trace_fields = _fixture_trace_fields(snapshot)
    unavailable_fields = _unavailable_fields(
        expected_identity_fields=expected_identity_fields,
        expected_manifest_trace_fields=expected_manifest_trace_fields,
        expected_fixture_trace_fields=expected_fixture_trace_fields,
    )
    blockers = _blockers(
        snapshot=snapshot,
        expected_identity_fields=expected_identity_fields,
        expected_manifest_trace_fields=expected_manifest_trace_fields,
        expected_fixture_trace_fields=expected_fixture_trace_fields,
    )
    status = _status(blockers=blockers, unavailable_fields=unavailable_fields)
    semantic_expectations = {
        **expected_identity_fields,
        **expected_manifest_trace_fields,
        **expected_fixture_trace_fields,
    }
    seed = {
        "baseline_id": snapshot.get("snapshot_id"),
        "stable_key": snapshot.get("stable_key"),
        "status": status,
        "token": STABLE_BASELINE_SEMANTIC_EXPECTATION_TOKEN,
    }
    return {
        "baseline_semantic_expectation_id": f"v3_1_baseline_semantic_expectation_{deterministic_hash(seed)[:16]}",
        "baseline_id": snapshot.get("snapshot_id"),
        "fixture_set_id": expected_fixture_trace_fields.get("fixture_set_id"),
        "expected_identity_fields": expected_identity_fields,
        "expected_manifest_trace_fields": expected_manifest_trace_fields,
        "expected_fixture_trace_fields": expected_fixture_trace_fields,
        "semantic_expectations": semantic_expectations,
        "unavailable_semantic_fields": unavailable_fields,
        "semantic_expectation_status": status,
        "blockers": blockers,
        "semantic_expectations_authorize_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_baseline_record() -> dict[str, Any]:
    seed = {"missing_baseline": True, "token": STABLE_BASELINE_SEMANTIC_EXPECTATION_TOKEN}
    return {
        "baseline_semantic_expectation_id": f"v3_1_baseline_semantic_expectation_{deterministic_hash(seed)[:16]}",
        "baseline_id": None,
        "fixture_set_id": None,
        "expected_identity_fields": {},
        "expected_manifest_trace_fields": {},
        "expected_fixture_trace_fields": {},
        "semantic_expectations": {},
        "unavailable_semantic_fields": [],
        "semantic_expectation_status": "blocked_missing_baseline_snapshot",
        "blockers": ["blocked_missing_baseline_snapshot"],
        "semantic_expectations_authorize_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _identity_fields(snapshot: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key in ("snapshot_id", "stable_key", "snapshot_category", "baseline_readiness"):
        if snapshot.get(key) not in (None, ""):
            fields[key] = snapshot[key]
    comparison = snapshot.get("dual_run_comparison_state") or {}
    for key in ("comparison_id", "legacy_status", "trusted_shadow_status", "drift_classification", "legacy_hash", "trusted_hash"):
        if comparison.get(key) not in (None, ""):
            fields[key] = comparison[key]
    return fields


def _manifest_trace_fields(snapshot: dict[str, Any]) -> dict[str, Any]:
    return _first_present_mapping(
        snapshot,
        ("expected_manifest_trace_fields", "manifest_trace_fields"),
        ("manifest_id", "expected_manifest_id"),
    )


def _fixture_trace_fields(snapshot: dict[str, Any]) -> dict[str, Any]:
    return _first_present_mapping(
        snapshot,
        ("expected_fixture_trace_fields", "fixture_trace_fields"),
        ("fixture_set_id", "expected_fixture_set_id"),
    )


def _first_present_mapping(snapshot: dict[str, Any], mapping_keys: tuple[str, ...], scalar_keys: tuple[str, ...]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key in mapping_keys:
        value = snapshot.get(key)
        if isinstance(value, dict):
            fields.update({item_key: item_value for item_key, item_value in value.items() if item_value not in (None, "")})
    for key in scalar_keys:
        if snapshot.get(key) not in (None, ""):
            normalized_key = key.removeprefix("expected_")
            fields[normalized_key] = snapshot[key]
    semantics = snapshot.get("semantic_expectations")
    if isinstance(semantics, dict):
        for key in scalar_keys:
            normalized_key = key.removeprefix("expected_")
            if semantics.get(normalized_key) not in (None, ""):
                fields[normalized_key] = semantics[normalized_key]
    return fields


def _unavailable_fields(
    *,
    expected_identity_fields: dict[str, Any],
    expected_manifest_trace_fields: dict[str, Any],
    expected_fixture_trace_fields: dict[str, Any],
) -> list[str]:
    unavailable: list[str] = []
    if not expected_identity_fields.get("snapshot_id"):
        unavailable.append("snapshot_id")
    if not expected_identity_fields.get("stable_key"):
        unavailable.append("stable_key")
    if not expected_manifest_trace_fields:
        unavailable.append("manifest_trace_fields")
    if not expected_fixture_trace_fields:
        unavailable.append("fixture_trace_fields")
    return unavailable


def _blockers(
    *,
    snapshot: dict[str, Any],
    expected_identity_fields: dict[str, Any],
    expected_manifest_trace_fields: dict[str, Any],
    expected_fixture_trace_fields: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not snapshot:
        blockers.append("blocked_missing_baseline_snapshot")
    if not expected_identity_fields.get("snapshot_id") or not expected_identity_fields.get("stable_key"):
        blockers.append("blocked_unstable_baseline_identity")
    if snapshot.get("semantic_trace_required") is True and (not expected_manifest_trace_fields or not expected_fixture_trace_fields):
        blockers.append("blocked_missing_required_trace")
    return blockers


def _status(*, blockers: list[str], unavailable_fields: list[str]) -> str:
    if blockers:
        return blockers[0]
    if unavailable_fields:
        return "semantic_expectations_partial"
    return "semantic_expectations_available"


def _snapshot_sort_key(snapshot: dict[str, Any]) -> tuple[str, str]:
    return (
        str(snapshot.get("stable_key") or ""),
        str(snapshot.get("snapshot_id") or ""),
    )
