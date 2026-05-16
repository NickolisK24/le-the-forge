"""Controlled consumption semantic parity audit for v3.1 governance.

Semantic parity extends structural parity by comparing controlled-test output
against optional planner baseline semantic expectations. Missing semantic
metadata is reported explicitly and never authorizes production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


CONTROLLED_CONSUMPTION_SEMANTIC_PARITY_STATUSES = (
    "semantic_parity_confirmed",
    "semantic_parity_partial",
    "blocked_missing_structural_parity",
    "blocked_missing_controlled_output",
    "blocked_missing_baseline_semantics",
    "blocked_semantic_mismatch",
    "blocked_invalid_authorization_state",
)
STABLE_CONTROLLED_SEMANTIC_PARITY_TOKEN = "v3_1_phase_20_controlled_consumption_semantic_parity_token"


def build_controlled_consumption_semantic_parity(
    *,
    controlled_consumption_parity_snapshot: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    planner_snapshot_baselines: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_20_controlled_consumption_semantic_parity",
) -> dict[str, Any]:
    """Build deterministic semantic parity audit records."""

    parity_records = _parity_records(controlled_consumption_parity_snapshot)
    validation_records = _validation_records(controlled_consumption_output_validation)
    baseline_snapshots = _baseline_snapshots(planner_snapshot_baselines)
    validation_by_key = {_validation_key(record): record for record in validation_records}
    baseline_by_id = {
        str(snapshot.get("snapshot_id")): snapshot
        for snapshot in baseline_snapshots
        if snapshot.get("snapshot_id")
    }
    semantic_records = [
        _semantic_record(
            parity_record=record,
            validation_record=validation_by_key.get(_parity_key(record)),
            baseline_snapshot=baseline_by_id.get(str(record.get("baseline_id"))),
        )
        for record in sorted(parity_records, key=_parity_sort_key)
    ]
    if not semantic_records:
        semantic_records = [_missing_structural_parity_record()]

    counts = Counter(record["semantic_parity_status"] for record in semantic_records)
    blocker_reasons = Counter(reason for record in semantic_records for reason in record["blockers"])
    unavailable_fields = Counter(field for record in semantic_records for field in record["unavailable_fields"])
    mismatched_fields = Counter(field for record in semantic_records for field in record["mismatched_fields"])
    parity_hash = controlled_consumption_parity_snapshot.get("deterministic_hash") if isinstance(controlled_consumption_parity_snapshot, dict) else None
    validation_hash = controlled_consumption_output_validation.get("deterministic_hash") if isinstance(controlled_consumption_output_validation, dict) else None
    baseline_hash = planner_snapshot_baselines.get("deterministic_hash") if isinstance(planner_snapshot_baselines, dict) else None
    envelope = {
        "schema_version": "v3_1.controlled_consumption_semantic_parity.1",
        "run": {
            "run_id": run_id,
            "structural_parity_record_count": len(parity_records),
            "validated_output_record_count": len(validation_records),
            "planner_snapshot_count": len(baseline_snapshots),
            "controlled_consumption_parity_snapshot_hash": parity_hash,
            "controlled_consumption_output_validation_hash": validation_hash,
            "planner_snapshot_baselines_hash": baseline_hash,
        },
        "summary": {
            "records_evaluated": len(semantic_records),
            "semantic_parity_confirmed_count": counts["semantic_parity_confirmed"],
            "semantic_parity_partial_count": counts["semantic_parity_partial"],
            "blocked_count": len(semantic_records) - counts["semantic_parity_confirmed"] - counts["semantic_parity_partial"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "semantic_parity_status_counts": {
            status: counts[status]
            for status in CONTROLLED_CONSUMPTION_SEMANTIC_PARITY_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "unavailable_semantic_field_counts": dict(sorted(unavailable_fields.items())),
        "mismatched_semantic_field_counts": dict(sorted(mismatched_fields.items())),
        "semantic_parity_records": semantic_records,
        "safety_confirmations": {
            "semantic_parity_authorizes_production_routing": False,
            "semantic_parity_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_controlled_consumption_semantic_parity",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_CONTROLLED_SEMANTIC_PARITY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _parity_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("parity_records", [])]


def _validation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("validation_records", [])]


def _baseline_snapshots(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("snapshots", [])]


def _semantic_record(
    *,
    parity_record: dict[str, Any],
    validation_record: dict[str, Any] | None,
    baseline_snapshot: dict[str, Any] | None,
) -> dict[str, Any]:
    compared_fields, unavailable_fields, mismatched_fields = _semantic_field_audit(
        validation_record=validation_record,
        baseline_snapshot=baseline_snapshot,
    )
    blockers = _blockers(
        parity_record=parity_record,
        validation_record=validation_record,
        baseline_snapshot=baseline_snapshot,
        unavailable_fields=unavailable_fields,
        mismatched_fields=mismatched_fields,
    )
    status = _status(
        blockers=blockers,
        compared_fields=compared_fields,
        unavailable_fields=unavailable_fields,
    )
    seed = {
        "parity_record_id": parity_record.get("parity_record_id"),
        "manifest_id": parity_record.get("manifest_id"),
        "fixture_set_id": parity_record.get("fixture_set_id"),
        "baseline_id": parity_record.get("baseline_id"),
        "status": status,
        "token": STABLE_CONTROLLED_SEMANTIC_PARITY_TOKEN,
    }
    return {
        "semantic_parity_record_id": f"v3_1_controlled_semantic_parity_{deterministic_hash(seed)[:16]}",
        "manifest_id": parity_record.get("manifest_id"),
        "fixture_set_id": parity_record.get("fixture_set_id"),
        "baseline_id": parity_record.get("baseline_id"),
        "structural_parity_status": parity_record.get("parity_status"),
        "semantic_parity_status": status,
        "compared_fields": compared_fields,
        "unavailable_fields": unavailable_fields,
        "mismatched_fields": mismatched_fields,
        "blockers": blockers,
        "semantic_parity_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_structural_parity_record() -> dict[str, Any]:
    seed = {"missing_structural_parity": True, "token": STABLE_CONTROLLED_SEMANTIC_PARITY_TOKEN}
    return {
        "semantic_parity_record_id": f"v3_1_controlled_semantic_parity_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "baseline_id": None,
        "structural_parity_status": None,
        "semantic_parity_status": "blocked_missing_structural_parity",
        "compared_fields": [],
        "unavailable_fields": [],
        "mismatched_fields": [],
        "blockers": ["blocked_missing_structural_parity"],
        "semantic_parity_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _semantic_field_audit(
    *,
    validation_record: dict[str, Any] | None,
    baseline_snapshot: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    baseline_semantics = _baseline_semantics(baseline_snapshot)
    controlled_semantics = _controlled_semantics(validation_record)
    if not baseline_semantics:
        return [], ["baseline_semantics"], []
    compared_fields: list[dict[str, Any]] = []
    unavailable_fields: list[str] = []
    mismatched_fields: list[str] = []
    for field in sorted(baseline_semantics):
        expected = baseline_semantics[field]
        if field not in controlled_semantics:
            unavailable_fields.append(field)
            continue
        actual = controlled_semantics[field]
        matches = actual == expected
        compared_fields.append({"field": field, "expected": expected, "actual": actual, "matches": matches})
        if not matches:
            mismatched_fields.append(field)
    return compared_fields, unavailable_fields, mismatched_fields


def _blockers(
    *,
    parity_record: dict[str, Any],
    validation_record: dict[str, Any] | None,
    baseline_snapshot: dict[str, Any] | None,
    unavailable_fields: list[str],
    mismatched_fields: list[str],
) -> list[str]:
    blockers: list[str] = []
    if parity_record.get("parity_status") != "parity_confirmed":
        blockers.append("blocked_missing_structural_parity")
    if validation_record is None:
        blockers.append("blocked_missing_controlled_output")
    if _authorization_state(validation_record) != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("blocked_invalid_authorization_state")
    if not _baseline_semantics(baseline_snapshot) and (baseline_snapshot or {}).get("semantic_required") is True:
        blockers.append("blocked_missing_baseline_semantics")
    if mismatched_fields:
        blockers.append("blocked_semantic_mismatch")
    return sorted(set(blockers), key=blockers.index)


def _status(*, blockers: list[str], compared_fields: list[dict[str, Any]], unavailable_fields: list[str]) -> str:
    if blockers:
        return blockers[0]
    if unavailable_fields or not compared_fields:
        return "semantic_parity_partial"
    return "semantic_parity_confirmed"


def _baseline_semantics(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    if not snapshot:
        return {}
    for key in ("semantic_expectations", "expected_semantics", "baseline_semantics"):
        value = snapshot.get(key)
        if isinstance(value, dict):
            return deepcopy(value)
    return {}


def _controlled_semantics(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {}
    for key in ("controlled_semantics", "semantic_output", "output_semantics", "controlled_output_semantics"):
        value = record.get(key)
        if isinstance(value, dict):
            return deepcopy(value)
    return {}


def _authorization_state(record: dict[str, Any] | None) -> str | None:
    if not record:
        return None
    return (record.get("traceability_summary") or {}).get("authorization_state")


def _parity_key(record: dict[str, Any]) -> tuple[str, str]:
    return (str(record.get("manifest_id") or ""), str(record.get("fixture_set_id") or ""))


def _validation_key(record: dict[str, Any]) -> tuple[str, str]:
    return (str(record.get("manifest_id") or ""), str(record.get("fixture_set_id") or ""))


def _parity_sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
        str(record.get("parity_record_id") or ""),
    )
