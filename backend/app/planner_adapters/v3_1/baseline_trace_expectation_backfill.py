"""Baseline trace expectation backfill for v3.1 governance.

Trace expectation backfill uses deterministic governance artifacts to enrich
baseline semantic expectation records with manifest and fixture trace fields.
It does not invent semantics and cannot authorize production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


BASELINE_TRACE_EXPECTATION_BACKFILL_STATUSES = (
    "trace_expectations_backfilled",
    "trace_expectations_partial",
    "blocked_missing_baseline_expectation",
    "blocked_missing_trace_source",
    "blocked_trace_conflict",
    "blocked_invalid_authorization_state",
)
STABLE_BASELINE_TRACE_BACKFILL_TOKEN = "v3_1_phase_22_baseline_trace_expectation_backfill_token"


def build_baseline_trace_expectation_backfill(
    *,
    baseline_semantic_expectations: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_parity_snapshot: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    admission_aware_manifest_serialization: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_22_baseline_trace_expectation_backfill",
) -> dict[str, Any]:
    """Backfill deterministic trace expectations into baseline expectation records."""

    expectations = _expectation_records(baseline_semantic_expectations)
    parity_records = _parity_records(controlled_consumption_parity_snapshot)
    validation_records = _validation_records(controlled_consumption_output_validation)
    serialized_manifests = _serialized_manifests(admission_aware_manifest_serialization)
    trace_sources = _trace_sources(
        parity_records=parity_records,
        validation_records=validation_records,
        serialized_manifests=serialized_manifests,
    )
    backfill_records = [
        _backfill_record(expectation=record, trace_source=trace_sources.get(str(record.get("baseline_id") or "")))
        for record in sorted(expectations, key=_expectation_sort_key)
    ]
    if not backfill_records:
        backfill_records = [_missing_expectation_record()]

    counts = Counter(record["trace_backfill_status"] for record in backfill_records)
    remaining_unavailable = Counter(field for record in backfill_records for field in record["remaining_unavailable_fields"])
    blocker_reasons = Counter(reason for record in backfill_records for reason in record["blockers"])
    trace_conflicts = Counter(conflict for record in backfill_records for conflict in record["trace_conflicts"])
    expectation_hash = baseline_semantic_expectations.get("deterministic_hash") if isinstance(baseline_semantic_expectations, dict) else None
    parity_hash = controlled_consumption_parity_snapshot.get("deterministic_hash") if isinstance(controlled_consumption_parity_snapshot, dict) else None
    validation_hash = controlled_consumption_output_validation.get("deterministic_hash") if isinstance(controlled_consumption_output_validation, dict) else None
    manifest_hash = admission_aware_manifest_serialization.get("deterministic_hash") if isinstance(admission_aware_manifest_serialization, dict) else None
    envelope = {
        "schema_version": "v3_1.baseline_trace_expectation_backfill.1",
        "run": {
            "run_id": run_id,
            "baseline_expectation_record_count": len(expectations),
            "trace_source_count": len(trace_sources),
            "baseline_semantic_expectations_hash": expectation_hash,
            "controlled_consumption_parity_snapshot_hash": parity_hash,
            "controlled_consumption_output_validation_hash": validation_hash,
            "admission_aware_manifest_serialization_hash": manifest_hash,
        },
        "summary": {
            "baseline_expectation_records_evaluated": len(backfill_records),
            "backfilled_count": counts["trace_expectations_backfilled"],
            "partial_count": counts["trace_expectations_partial"],
            "blocked_count": (
                counts["blocked_missing_baseline_expectation"]
                + counts["blocked_missing_trace_source"]
                + counts["blocked_trace_conflict"]
                + counts["blocked_invalid_authorization_state"]
            ),
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "trace_backfill_status_counts": {
            status: counts[status]
            for status in BASELINE_TRACE_EXPECTATION_BACKFILL_STATUSES
        },
        "remaining_unavailable_field_counts": dict(sorted(remaining_unavailable.items())),
        "trace_conflict_counts": dict(sorted(trace_conflicts.items())),
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "baseline_trace_backfill_records": backfill_records,
        "safety_confirmations": {
            "backfilled_expectations_authorize_production_routing": False,
            "backfilled_expectations_are_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_baseline_trace_expectation_backfill",
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_BASELINE_TRACE_BACKFILL_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _expectation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("baseline_semantic_expectation_records", [])]


def _parity_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("parity_records", [])]


def _validation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("validation_records", [])]


def _serialized_manifests(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("serialized_manifests", [])]


def _trace_sources(
    *,
    parity_records: list[dict[str, Any]],
    validation_records: list[dict[str, Any]],
    serialized_manifests: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    validations_by_key = {_trace_key(record): record for record in validation_records if _trace_key(record)}
    manifests_by_key = {_trace_key(record): record for record in serialized_manifests if _trace_key(record)}
    sources: dict[str, dict[str, Any]] = {}
    for parity in sorted(parity_records, key=_parity_sort_key):
        if parity.get("parity_status") != "parity_confirmed" or not parity.get("baseline_id"):
            continue
        source = _source_from_parity(
            parity=parity,
            validation=validations_by_key.get(_trace_key(parity)),
            manifest=manifests_by_key.get(_trace_key(parity)),
        )
        sources[str(parity["baseline_id"])] = source
    return sources


def _source_from_parity(
    *,
    parity: dict[str, Any],
    validation: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    manifest_id = parity.get("manifest_id")
    fixture_set_id = parity.get("fixture_set_id")
    conflicts: list[str] = []
    authorization_states = []
    if validation is not None:
        validation_auth = (validation.get("traceability_summary") or {}).get("authorization_state")
        authorization_states.append(validation_auth)
        if validation.get("manifest_id") != manifest_id:
            conflicts.append("validation_manifest_id")
        if validation.get("fixture_set_id") != fixture_set_id:
            conflicts.append("validation_fixture_set_id")
    if manifest is not None:
        manifest_auth = (manifest.get("authorization_status") or {}).get("authorization_state")
        authorization_states.append(manifest_auth)
        if manifest.get("manifest_id") != manifest_id:
            conflicts.append("serialized_manifest_id")
        if manifest.get("fixture_set_id") != fixture_set_id:
            conflicts.append("serialized_fixture_set_id")
    return {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "validation_present": validation is not None,
        "serialized_manifest_present": manifest is not None,
        "authorization_states": authorization_states,
        "authorization_valid": bool(authorization_states) and all(state == NON_PRODUCTION_AUTHORIZATION_STATE for state in authorization_states),
        "conflicts": conflicts,
    }


def _backfill_record(*, expectation: dict[str, Any], trace_source: dict[str, Any] | None) -> dict[str, Any]:
    manifest_fields = deepcopy(expectation.get("expected_manifest_trace_fields") or {})
    fixture_fields = deepcopy(expectation.get("expected_fixture_trace_fields") or {})
    conflicts = _trace_conflicts(expectation=expectation, trace_source=trace_source)
    if trace_source and not conflicts and trace_source.get("authorization_valid"):
        manifest_fields.setdefault("manifest_id", trace_source.get("manifest_id"))
        fixture_fields.setdefault("fixture_set_id", trace_source.get("fixture_set_id"))
    remaining_unavailable = _remaining_unavailable(
        original_unavailable=list(expectation.get("unavailable_semantic_fields") or []),
        manifest_fields=manifest_fields,
        fixture_fields=fixture_fields,
    )
    blockers = _blockers(expectation=expectation, trace_source=trace_source, conflicts=conflicts)
    status = _status(blockers=blockers, remaining_unavailable=remaining_unavailable, trace_source=trace_source)
    seed = {
        "baseline_id": expectation.get("baseline_id"),
        "manifest_id": manifest_fields.get("manifest_id"),
        "fixture_set_id": fixture_fields.get("fixture_set_id"),
        "status": status,
        "token": STABLE_BASELINE_TRACE_BACKFILL_TOKEN,
    }
    return {
        "baseline_trace_backfill_id": f"v3_1_baseline_trace_backfill_{deterministic_hash(seed)[:16]}",
        "baseline_id": expectation.get("baseline_id"),
        "fixture_set_id": fixture_fields.get("fixture_set_id"),
        "manifest_id": manifest_fields.get("manifest_id"),
        "original_semantic_expectation_status": expectation.get("semantic_expectation_status"),
        "backfilled_manifest_trace_fields": manifest_fields,
        "backfilled_fixture_trace_fields": fixture_fields,
        "remaining_unavailable_fields": remaining_unavailable,
        "trace_backfill_status": status,
        "trace_conflicts": conflicts,
        "blockers": blockers,
        "backfilled_expectations_authorize_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_expectation_record() -> dict[str, Any]:
    seed = {"missing_baseline_expectation": True, "token": STABLE_BASELINE_TRACE_BACKFILL_TOKEN}
    return {
        "baseline_trace_backfill_id": f"v3_1_baseline_trace_backfill_{deterministic_hash(seed)[:16]}",
        "baseline_id": None,
        "fixture_set_id": None,
        "manifest_id": None,
        "original_semantic_expectation_status": None,
        "backfilled_manifest_trace_fields": {},
        "backfilled_fixture_trace_fields": {},
        "remaining_unavailable_fields": [],
        "trace_backfill_status": "blocked_missing_baseline_expectation",
        "trace_conflicts": [],
        "blockers": ["blocked_missing_baseline_expectation"],
        "backfilled_expectations_authorize_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _trace_conflicts(*, expectation: dict[str, Any], trace_source: dict[str, Any] | None) -> list[str]:
    if not trace_source:
        return []
    conflicts = list(trace_source.get("conflicts") or [])
    expected_manifest = (expectation.get("expected_manifest_trace_fields") or {}).get("manifest_id")
    expected_fixture = (expectation.get("expected_fixture_trace_fields") or {}).get("fixture_set_id")
    if expected_manifest and expected_manifest != trace_source.get("manifest_id"):
        conflicts.append("baseline_manifest_id")
    if expected_fixture and expected_fixture != trace_source.get("fixture_set_id"):
        conflicts.append("baseline_fixture_set_id")
    return sorted(set(conflicts))


def _remaining_unavailable(*, original_unavailable: list[str], manifest_fields: dict[str, Any], fixture_fields: dict[str, Any]) -> list[str]:
    remaining: list[str] = []
    for field in original_unavailable:
        if field == "manifest_trace_fields" and manifest_fields.get("manifest_id"):
            continue
        if field == "fixture_trace_fields" and fixture_fields.get("fixture_set_id"):
            continue
        remaining.append(field)
    return remaining


def _blockers(*, expectation: dict[str, Any], trace_source: dict[str, Any] | None, conflicts: list[str]) -> list[str]:
    blockers: list[str] = []
    if not expectation.get("baseline_id"):
        blockers.append("blocked_missing_baseline_expectation")
    if conflicts:
        blockers.append("blocked_trace_conflict")
    if trace_source and not trace_source.get("authorization_valid"):
        blockers.append("blocked_invalid_authorization_state")
    return blockers


def _status(*, blockers: list[str], remaining_unavailable: list[str], trace_source: dict[str, Any] | None) -> str:
    if blockers:
        return blockers[0]
    if not trace_source:
        return "trace_expectations_partial"
    if remaining_unavailable:
        return "trace_expectations_partial"
    return "trace_expectations_backfilled"


def _trace_key(record: dict[str, Any] | None) -> tuple[str, str] | None:
    if not record:
        return None
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if not manifest_id or not fixture_set_id:
        return None
    return (str(manifest_id), str(fixture_set_id))


def _expectation_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    return (
        str(record.get("baseline_id") or ""),
        str(record.get("baseline_semantic_expectation_id") or ""),
    )


def _parity_sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(record.get("baseline_id") or ""),
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
    )
