"""Limited experimental runtime dry-run adapter for v3.1 governance.

The adapter exercises the guarded manifest evidence chain in dry-run mode only.
It is pure, non-mutating, and does not enable runtime manifest consumption or
production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


LIMITED_EXPERIMENTAL_RUNTIME_DRY_RUN_STATUSES = (
    "dry_run_ready",
    "blocked_missing_guard_contract",
    "blocked_invalid_guard_status",
    "blocked_missing_promotion_readiness",
    "blocked_invalid_authorization_state",
    "blocked_runtime_consumption_enabled",
    "blocked_production_routing_authorized",
    "blocked_missing_manifest",
    "blocked_missing_validated_evidence",
)
STABLE_LIMITED_RUNTIME_DRY_RUN_TOKEN = "v3_1_phase_26_limited_experimental_runtime_dry_run_token"


def build_limited_experimental_runtime_dry_run(
    *,
    limited_experimental_runtime_guards: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_promotion_readiness: dict[str, Any] | list[dict[str, Any]],
    admission_aware_manifest_serialization: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_parity_snapshot: dict[str, Any] | list[dict[str, Any]],
    trace_backfilled_semantic_parity: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_26_limited_experimental_runtime_dry_run",
) -> dict[str, Any]:
    """Build deterministic dry-run records from guarded non-production evidence."""

    guard_records = _guard_records(limited_experimental_runtime_guards)
    readiness_records = _readiness_records(controlled_consumption_promotion_readiness)
    manifests = _serialized_manifests(admission_aware_manifest_serialization)
    validations = _validation_records(controlled_consumption_output_validation)
    structural_parity = _structural_parity_records(controlled_consumption_parity_snapshot)
    semantic_parity = _semantic_parity_records(trace_backfilled_semantic_parity)
    runtime_enabled = _runtime_enabled(
        limited_experimental_runtime_guards,
        controlled_consumption_promotion_readiness,
        admission_aware_manifest_serialization,
        controlled_consumption_output_validation,
        controlled_consumption_parity_snapshot,
        trace_backfilled_semantic_parity,
    )
    production_routing_authorized = _production_routing_authorized(
        limited_experimental_runtime_guards,
        controlled_consumption_promotion_readiness,
        admission_aware_manifest_serialization,
        controlled_consumption_output_validation,
        controlled_consumption_parity_snapshot,
        trace_backfilled_semantic_parity,
    )
    readiness_by_key = {_trace_key(record): record for record in readiness_records if _trace_key(record)}
    manifests_by_key = {_trace_key(record): record for record in manifests if _trace_key(record)}
    validations_by_key = {_trace_key(record): record for record in validations if _trace_key(record)}
    structural_by_key = {_trace_key(record): record for record in structural_parity if _trace_key(record)}
    semantic_by_key = {_trace_key(record): record for record in semantic_parity if _trace_key(record)}
    dry_run_records = [
        _dry_run_record(
            guard=record,
            readiness=readiness_by_key.get(_trace_key(record)),
            manifest=manifests_by_key.get(_trace_key(record)),
            validation=validations_by_key.get(_trace_key(record)),
            structural_parity=structural_by_key.get(_trace_key(record)),
            semantic_parity=semantic_by_key.get(_trace_key(record)),
            runtime_enabled=runtime_enabled,
            production_routing_authorized=production_routing_authorized,
        )
        for record in sorted(guard_records, key=_record_sort_key)
    ]
    if not dry_run_records:
        dry_run_records = [_missing_guard_record(runtime_enabled=runtime_enabled, production_routing_authorized=production_routing_authorized)]

    counts = Counter(record["dry_run_status"] for record in dry_run_records)
    blocker_reasons = Counter(reason for record in dry_run_records for reason in record["blockers"])
    envelope = {
        "schema_version": "v3_1.limited_experimental_runtime_dry_run.1",
        "run": {
            "run_id": run_id,
            "guard_record_count": len(guard_records),
            "promotion_readiness_record_count": len(readiness_records),
            "serialized_manifest_count": len(manifests),
            "validation_record_count": len(validations),
            "structural_parity_record_count": len(structural_parity),
            "semantic_parity_record_count": len(semantic_parity),
            "limited_experimental_runtime_guards_hash": _source_hash(limited_experimental_runtime_guards),
            "controlled_consumption_promotion_readiness_hash": _source_hash(controlled_consumption_promotion_readiness),
            "admission_aware_manifest_serialization_hash": _source_hash(admission_aware_manifest_serialization),
            "controlled_consumption_output_validation_hash": _source_hash(controlled_consumption_output_validation),
            "controlled_consumption_parity_snapshot_hash": _source_hash(controlled_consumption_parity_snapshot),
            "trace_backfilled_semantic_parity_hash": _source_hash(trace_backfilled_semantic_parity),
        },
        "summary": {
            "records_evaluated": len(dry_run_records),
            "dry_run_ready_count": counts["dry_run_ready"],
            "blocked_count": len(dry_run_records) - counts["dry_run_ready"],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "dry_run_status_counts": {
            status: counts[status]
            for status in LIMITED_EXPERIMENTAL_RUNTIME_DRY_RUN_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "evidence_summary": {
            "guard_records": len(guard_records),
            "promotion_readiness_records": len(readiness_records),
            "serialized_manifests": len(manifests),
            "validation_records": len(validations),
            "structural_parity_records": len(structural_parity),
            "semantic_parity_records": len(semantic_parity),
            "runtime_manifest_consumption_enabled": runtime_enabled,
            "production_routing_authorized": production_routing_authorized,
            "dry_run_mutates_runtime_state": False,
        },
        "limited_experimental_runtime_dry_run_records": dry_run_records,
        "safety_confirmations": {
            "dry_run_enables_runtime_routing": False,
            "dry_run_authorizes_production_routing": False,
            "dry_run_is_production_approval": False,
            "dry_run_mutates_runtime_state": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_limited_experimental_runtime_dry_run",
            "observational_only": True,
            "dry_run_only": True,
            "non_mutating": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_LIMITED_RUNTIME_DRY_RUN_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _guard_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("limited_experimental_runtime_guard_records", [])]


def _readiness_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("promotion_readiness_records", [])]


def _serialized_manifests(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("serialized_manifests", [])]


def _validation_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("validation_records", [])]


def _structural_parity_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("parity_records", [])]


def _semantic_parity_records(value: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(row) for row in value]
    return [deepcopy(row) for row in value.get("trace_backfilled_semantic_parity_records", [])]


def _dry_run_record(
    *,
    guard: dict[str, Any],
    readiness: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    structural_parity: dict[str, Any] | None,
    semantic_parity: dict[str, Any] | None,
    runtime_enabled: bool,
    production_routing_authorized: bool,
) -> dict[str, Any]:
    blockers = _blockers(
        guard=guard,
        readiness=readiness,
        manifest=manifest,
        validation=validation,
        structural_parity=structural_parity,
        semantic_parity=semantic_parity,
        runtime_enabled=runtime_enabled,
        production_routing_authorized=production_routing_authorized,
    )
    status = blockers[0] if blockers else "dry_run_ready"
    authorization_state = _authorization_state(guard=guard, manifest=manifest)
    seed = {
        "manifest_id": guard.get("manifest_id"),
        "fixture_set_id": guard.get("fixture_set_id"),
        "status": status,
        "token": STABLE_LIMITED_RUNTIME_DRY_RUN_TOKEN,
    }
    return {
        "limited_runtime_dry_run_id": f"v3_1_limited_runtime_dry_run_{deterministic_hash(seed)[:16]}",
        "manifest_id": guard.get("manifest_id"),
        "fixture_set_id": guard.get("fixture_set_id"),
        "guard_status": guard.get("guard_contract_status"),
        "promotion_readiness_status": (readiness or {}).get("promotion_readiness_status"),
        "authorization_state": authorization_state,
        "dry_run_status": status,
        "blockers": blockers,
        "evidence_summary": {
            "manifest_present": manifest is not None,
            "validation_status": (validation or {}).get("validation_status"),
            "structural_parity_status": (structural_parity or {}).get("parity_status"),
            "semantic_parity_status": (semantic_parity or {}).get("final_semantic_parity_status"),
            "runtime_consumption_enabled": runtime_enabled,
            "production_routing_authorized": production_routing_authorized,
            "dry_run_mutates_runtime_state": False,
        },
        "dry_run_enables_runtime_routing": False,
        "dry_run_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "dry_run_only": True,
            "non_mutating": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _missing_guard_record(*, runtime_enabled: bool, production_routing_authorized: bool) -> dict[str, Any]:
    seed = {"missing_guard": True, "runtime_enabled": runtime_enabled, "production_routing_authorized": production_routing_authorized, "token": STABLE_LIMITED_RUNTIME_DRY_RUN_TOKEN}
    blockers = ["blocked_missing_guard_contract"]
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    if production_routing_authorized:
        blockers.append("blocked_production_routing_authorized")
    return {
        "limited_runtime_dry_run_id": f"v3_1_limited_runtime_dry_run_{deterministic_hash(seed)[:16]}",
        "manifest_id": None,
        "fixture_set_id": None,
        "guard_status": None,
        "promotion_readiness_status": None,
        "authorization_state": None,
        "dry_run_status": "blocked_missing_guard_contract",
        "blockers": blockers,
        "evidence_summary": {
            "manifest_present": False,
            "validation_status": None,
            "structural_parity_status": None,
            "semantic_parity_status": None,
            "runtime_consumption_enabled": runtime_enabled,
            "production_routing_authorized": production_routing_authorized,
            "dry_run_mutates_runtime_state": False,
        },
        "dry_run_enables_runtime_routing": False,
        "dry_run_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "dry_run_only": True,
            "non_mutating": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _blockers(
    *,
    guard: dict[str, Any],
    readiness: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    structural_parity: dict[str, Any] | None,
    semantic_parity: dict[str, Any] | None,
    runtime_enabled: bool,
    production_routing_authorized: bool,
) -> list[str]:
    blockers: list[str] = []
    if not guard:
        blockers.append("blocked_missing_guard_contract")
    if guard.get("guard_contract_status") != "guard_contract_ready":
        blockers.append("blocked_invalid_guard_status")
    if readiness is None or readiness.get("promotion_readiness_status") != "ready_for_limited_experimental_runtime_consideration":
        blockers.append("blocked_missing_promotion_readiness")
    if _authorization_state(guard=guard, manifest=manifest) != NON_PRODUCTION_AUTHORIZATION_STATE:
        blockers.append("blocked_invalid_authorization_state")
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    if production_routing_authorized:
        blockers.append("blocked_production_routing_authorized")
    if not _manifest_is_non_production_authoritative(manifest):
        blockers.append("blocked_missing_manifest")
    if (
        validation is None
        or validation.get("validation_status") != "valid_controlled_test_output"
        or structural_parity is None
        or structural_parity.get("parity_status") != "parity_confirmed"
        or semantic_parity is None
        or semantic_parity.get("final_semantic_parity_status") != "semantic_parity_confirmed"
    ):
        blockers.append("blocked_missing_validated_evidence")
    return sorted(set(blockers), key=blockers.index)


def _authorization_state(*, guard: dict[str, Any], manifest: dict[str, Any] | None) -> str | None:
    return guard.get("authorization_state") or ((manifest or {}).get("authorization_status") or {}).get("authorization_state")


def _manifest_is_non_production_authoritative(manifest: dict[str, Any] | None) -> bool:
    if not manifest:
        return False
    authorization = manifest.get("authorization_status") or {}
    return (
        manifest.get("non_production_authoritative") is True
        and authorization.get("authorization_state") == NON_PRODUCTION_AUTHORIZATION_STATE
        and authorization.get("manifest_authorizes_production_routing") is False
        and authorization.get("manifest_is_production_authoritative") is False
        and authorization.get("manifest_is_production_approved") is False
    )


def _runtime_enabled(*values: Any) -> bool:
    for value in values:
        if not isinstance(value, dict):
            continue
        summary = value.get("summary") or {}
        safety = value.get("safety_confirmations") or {}
        if (
            value.get("runtime_manifest_consumption_enabled")
            or value.get("runtime_production_consumption_enabled")
            or summary.get("runtime_manifest_consumption_enabled")
            or summary.get("runtime_production_consumption_enabled")
            or summary.get("manifest_runtime_consumption_enabled")
            or safety.get("runtime_manifest_consumption_enabled")
            or safety.get("runtime_production_consumption_enabled")
        ):
            return True
    return False


def _production_routing_authorized(*values: Any) -> bool:
    for value in values:
        if not isinstance(value, dict):
            continue
        summary = value.get("summary") or {}
        safety = value.get("safety_confirmations") or {}
        if (
            value.get("production_default_routing_authorized")
            or value.get("production_routing_authorized")
            or summary.get("production_default_routing_authorized")
            or summary.get("production_routing_authorized")
            or safety.get("production_planner_routing_changed")
        ):
            return True
    return False


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
