"""Controlled consumption promotion readiness gate for v3.1 governance.

Promotion readiness is limited to future experimental runtime consideration.
It does not enable production routing, runtime manifest consumption, or
production-authoritative manifests.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


CONTROLLED_CONSUMPTION_PROMOTION_READINESS_STATUSES = (
    "ready_for_limited_experimental_runtime_consideration",
    "blocked_missing_controlled_consumption",
    "blocked_invalid_output_validation",
    "blocked_missing_structural_parity",
    "blocked_missing_semantic_parity",
    "blocked_invalid_manifest_eligibility",
    "blocked_invalid_authorization_state",
    "blocked_runtime_consumption_enabled",
)
STABLE_PROMOTION_READINESS_TOKEN = "v3_1_phase_24_controlled_consumption_promotion_readiness_token"


def build_controlled_consumption_promotion_readiness(
    *,
    controlled_test_consumption: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_parity_snapshot: dict[str, Any] | list[dict[str, Any]],
    trace_backfilled_semantic_parity: dict[str, Any] | list[dict[str, Any]],
    manifest_consumption_eligibility: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_24_controlled_consumption_promotion_readiness",
) -> dict[str, Any]:
    """Build deterministic promotion readiness records from the evidence chain."""

    consumption_records = _consumption_records(controlled_test_consumption)
    validation_records = _validation_records(controlled_consumption_output_validation)
    parity_records = _parity_records(controlled_consumption_parity_snapshot)
    semantic_records = _semantic_records(trace_backfilled_semantic_parity)
    eligibility_records = _eligibility_records(manifest_consumption_eligibility)
    runtime_enabled = any(
        (
            _runtime_enabled(controlled_test_consumption),
            _runtime_enabled(controlled_consumption_output_validation),
            _runtime_enabled(controlled_consumption_parity_snapshot),
            _runtime_enabled(trace_backfilled_semantic_parity),
            _runtime_enabled(manifest_consumption_eligibility),
        )
    )
    validation_by_key = {_trace_key(record): record for record in validation_records if _trace_key(record)}
    parity_by_key = {_trace_key(record): record for record in parity_records if _trace_key(record)}
    semantic_by_key = {_trace_key(record): record for record in semantic_records if _trace_key(record)}
    eligibility_by_key = {_trace_key(record): record for record in eligibility_records if _trace_key(record)}
    readiness_records = [
        _readiness_record(
            consumption=record,
            validation=validation_by_key.get(_trace_key(record)),
            structural_parity=parity_by_key.get(_trace_key(record)),
            semantic_parity=semantic_by_key.get(_trace_key(record)),
            eligibility=eligibility_by_key.get(_trace_key(record)),
            runtime_enabled=runtime_enabled,
        )
        for record in sorted(consumption_records, key=_record_sort_key)
    ]
    if not readiness_records:
        readiness_records = [_missing_consumption_record(runtime_enabled=runtime_enabled)]

    counts = Counter(record["promotion_readiness_status"] for record in readiness_records)
    blocker_reasons = Counter(reason for record in readiness_records for reason in record["blockers"])
    envelope = {
        "schema_version": "v3_1.controlled_consumption_promotion_readiness.1",
        "run": {
            "run_id": run_id,
            "controlled_consumption_record_count": len(consumption_records),
            "validation_record_count": len(validation_records),
            "structural_parity_record_count": len(parity_records),
            "semantic_parity_record_count": len(semantic_records),
            "eligibility_record_count": len(eligibility_records),
            "controlled_test_consumption_hash": _source_hash(controlled_test_consumption),
            "controlled_consumption_output_validation_hash": _source_hash(controlled_consumption_output_validation),
            "controlled_consumption_parity_snapshot_hash": _source_hash(controlled_consumption_parity_snapshot),
            "trace_backfilled_semantic_parity_hash": _source_hash(trace_backfilled_semantic_parity),
            "manifest_consumption_eligibility_hash": _source_hash(manifest_consumption_eligibility),
        },
        "summary": {
            "records_evaluated": len(readiness_records),
            "ready_count": counts["ready_for_limited_experimental_runtime_consideration"],
            "blocked_count": len(readiness_records) - counts["ready_for_limited_experimental_runtime_consideration"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "deterministic": True,
        },
        "promotion_readiness_status_counts": {
            status: counts[status]
            for status in CONTROLLED_CONSUMPTION_PROMOTION_READINESS_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "evidence_chain_summary": {
            "controlled_consumption_records": len(consumption_records),
            "validated_output_records": len(validation_records),
            "structural_parity_records": len(parity_records),
            "semantic_parity_records": len(semantic_records),
            "manifest_eligibility_records": len(eligibility_records),
            "runtime_consumption_enabled": runtime_enabled,
            "production_routing_authorized": False,
        },
        "promotion_readiness_records": readiness_records,
        "safety_confirmations": {
            "promotion_readiness_authorizes_production_routing": False,
            "promotion_readiness_is_production_approval": False,
            "promotion_readiness_enables_runtime_consumption": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_controlled_consumption_promotion_readiness",
            "observational_only": True,
            "controlled_test_only": True,
            "future_limited_experimental_consideration_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_PROMOTION_READINESS_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _consumption_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("controlled_consumption_records", [])]


def _validation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("validation_records", [])]


def _parity_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("parity_records", [])]


def _semantic_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("trace_backfilled_semantic_parity_records", [])]


def _eligibility_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("eligibility_records", [])]


def _readiness_record(
    *,
    consumption: dict[str, Any],
    validation: dict[str, Any] | None,
    structural_parity: dict[str, Any] | None,
    semantic_parity: dict[str, Any] | None,
    eligibility: dict[str, Any] | None,
    runtime_enabled: bool,
) -> dict[str, Any]:
    blockers = _blockers(
        consumption=consumption,
        validation=validation,
        structural_parity=structural_parity,
        semantic_parity=semantic_parity,
        eligibility=eligibility,
        runtime_enabled=runtime_enabled,
    )
    status = blockers[0] if blockers else "ready_for_limited_experimental_runtime_consideration"
    seed = {
        "manifest_id": consumption.get("manifest_id"),
        "fixture_set_id": consumption.get("fixture_set_id"),
        "status": status,
        "token": STABLE_PROMOTION_READINESS_TOKEN,
    }
    return {
        "promotion_readiness_id": f"v3_1_promotion_readiness_{deterministic_hash(seed)[:16]}",
        "manifest_id": consumption.get("manifest_id"),
        "fixture_set_id": consumption.get("fixture_set_id"),
        "controlled_consumption_status": consumption.get("controlled_consumption_status"),
        "validation_status": (validation or {}).get("validation_status"),
        "structural_parity_status": (structural_parity or {}).get("parity_status"),
        "semantic_parity_status": (semantic_parity or {}).get("final_semantic_parity_status"),
        "eligibility_status": (eligibility or {}).get("eligibility_status"),
        "promotion_readiness_status": status,
        "blockers": blockers,
        "promotion_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "future_limited_experimental_consideration_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_consumption_record(*, runtime_enabled: bool) -> dict[str, Any]:
    seed = {"missing_consumption": True, "runtime_enabled": runtime_enabled, "token": STABLE_PROMOTION_READINESS_TOKEN}
    blockers = ["blocked_missing_controlled_consumption"]
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    return {
        "promotion_readiness_id": f"v3_1_promotion_readiness_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "controlled_consumption_status": None,
        "validation_status": None,
        "structural_parity_status": None,
        "semantic_parity_status": None,
        "eligibility_status": None,
        "promotion_readiness_status": "blocked_missing_controlled_consumption",
        "blockers": blockers,
        "promotion_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "controlled_test_only": True,
            "future_limited_experimental_consideration_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _blockers(
    *,
    consumption: dict[str, Any],
    validation: dict[str, Any] | None,
    structural_parity: dict[str, Any] | None,
    semantic_parity: dict[str, Any] | None,
    eligibility: dict[str, Any] | None,
    runtime_enabled: bool,
) -> list[str]:
    blockers: list[str] = []
    if consumption.get("controlled_consumption_status") != "consumed_in_controlled_test":
        blockers.append("blocked_missing_controlled_consumption")
    if validation is None or validation.get("validation_status") != "valid_controlled_test_output":
        blockers.append("blocked_invalid_output_validation")
    if structural_parity is None or structural_parity.get("parity_status") != "parity_confirmed":
        blockers.append("blocked_missing_structural_parity")
    if semantic_parity is None or semantic_parity.get("final_semantic_parity_status") != "semantic_parity_confirmed":
        blockers.append("blocked_missing_semantic_parity")
    if eligibility is None or eligibility.get("eligibility_status") != "eligible_for_controlled_test_consumption":
        blockers.append("blocked_invalid_manifest_eligibility")
    if _authorization_invalid(consumption=consumption, validation=validation, eligibility=eligibility):
        blockers.append("blocked_invalid_authorization_state")
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    return sorted(set(blockers), key=blockers.index)


def _authorization_invalid(
    *,
    consumption: dict[str, Any],
    validation: dict[str, Any] | None,
    eligibility: dict[str, Any] | None,
) -> bool:
    states = [
        consumption.get("authorization_state"),
        (validation or {}).get("traceability_summary", {}).get("authorization_state"),
        (eligibility or {}).get("authorization_state"),
    ]
    return any(state != NON_PRODUCTION_AUTHORIZATION_STATE for state in states if state is not None) or not states[0]


def _runtime_enabled(value: dict[str, Any] | list[dict[str, Any]]) -> bool:
    if not isinstance(value, dict):
        return False
    summary = value.get("summary") or {}
    safety = value.get("safety_confirmations") or {}
    return bool(
        summary.get("runtime_manifest_consumption_enabled")
        or summary.get("runtime_production_consumption_enabled")
        or summary.get("manifest_runtime_consumption_enabled")
        or safety.get("runtime_manifest_consumption_enabled")
        or safety.get("runtime_production_consumption_enabled")
    )


def _trace_key(record: dict[str, Any] | None) -> tuple[str, str] | None:
    if not record:
        return None
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if not manifest_id or not fixture_set_id:
        return None
    return (str(manifest_id), str(fixture_set_id))


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    return (
        str(record.get("fixture_set_id") or ""),
        str(record.get("manifest_id") or ""),
    )


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
