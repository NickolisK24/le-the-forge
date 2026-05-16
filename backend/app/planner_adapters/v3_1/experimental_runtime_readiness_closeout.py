"""Experimental runtime readiness closeout audit for v3.1 governance.

The closeout summarizes the controlled-consumption evidence chain for future
limited experimental runtime consideration. It is reporting-only and does not
enable runtime manifest consumption or production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


EXPERIMENTAL_RUNTIME_READINESS_CLOSEOUT_STATUSES = (
    "ready_for_future_limited_experimental_runtime_phase",
    "blocked_missing_manifest_eligibility",
    "blocked_missing_controlled_consumption",
    "blocked_missing_output_validation",
    "blocked_missing_structural_parity",
    "blocked_missing_semantic_parity",
    "blocked_missing_promotion_readiness",
    "blocked_missing_runtime_guard",
    "blocked_missing_dry_run",
    "blocked_missing_dry_run_stability",
    "blocked_runtime_consumption_enabled",
    "blocked_production_routing_authorized",
)
STABLE_EXPERIMENTAL_RUNTIME_READINESS_CLOSEOUT_TOKEN = "v3_1_phase_28_experimental_runtime_readiness_closeout_token"


def build_experimental_runtime_readiness_closeout(
    *,
    manifest_consumption_eligibility: dict[str, Any] | list[dict[str, Any]],
    controlled_test_consumption: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_output_validation: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_parity_snapshot: dict[str, Any] | list[dict[str, Any]],
    trace_backfilled_semantic_parity: dict[str, Any] | list[dict[str, Any]],
    controlled_consumption_promotion_readiness: dict[str, Any] | list[dict[str, Any]],
    limited_experimental_runtime_guards: dict[str, Any] | list[dict[str, Any]],
    limited_experimental_runtime_dry_run: dict[str, Any] | list[dict[str, Any]],
    dry_run_result_stability: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_28_experimental_runtime_readiness_closeout",
) -> dict[str, Any]:
    """Build deterministic closeout readiness records from governance evidence."""

    eligibility = _records(manifest_consumption_eligibility, "eligibility_records")
    consumption = _records(controlled_test_consumption, "controlled_consumption_records")
    validation = _records(controlled_consumption_output_validation, "validation_records")
    structural = _records(controlled_consumption_parity_snapshot, "parity_records")
    semantic = _records(trace_backfilled_semantic_parity, "trace_backfilled_semantic_parity_records")
    promotion = _records(controlled_consumption_promotion_readiness, "promotion_readiness_records")
    guards = _records(limited_experimental_runtime_guards, "limited_experimental_runtime_guard_records")
    dry_runs = _records(limited_experimental_runtime_dry_run, "limited_experimental_runtime_dry_run_records")
    stability = _records(dry_run_result_stability, "dry_run_result_stability_records")
    runtime_enabled = _runtime_enabled(
        manifest_consumption_eligibility,
        controlled_test_consumption,
        controlled_consumption_output_validation,
        controlled_consumption_parity_snapshot,
        trace_backfilled_semantic_parity,
        controlled_consumption_promotion_readiness,
        limited_experimental_runtime_guards,
        limited_experimental_runtime_dry_run,
        dry_run_result_stability,
    )
    production_routing_authorized = _production_routing_authorized(
        manifest_consumption_eligibility,
        controlled_test_consumption,
        controlled_consumption_output_validation,
        controlled_consumption_parity_snapshot,
        trace_backfilled_semantic_parity,
        controlled_consumption_promotion_readiness,
        limited_experimental_runtime_guards,
        limited_experimental_runtime_dry_run,
        dry_run_result_stability,
    )
    layer_maps = {
        "eligibility": _by_key(eligibility),
        "consumption": _by_key(consumption),
        "validation": _by_key(validation),
        "structural": _by_key(structural),
        "semantic": _by_key(semantic),
        "promotion": _by_key(promotion),
        "guard": _by_key(guards),
        "dry_run": _by_key(dry_runs),
        "stability": _by_key(stability),
    }
    keys = sorted(
        {
            key
            for mapping in layer_maps.values()
            for key in mapping
        },
        key=lambda item: (item[1], item[0]),
    )
    if not keys:
        keys = [(None, None)]
    closeout_records = [
        _closeout_record(
            key=key,
            layers=layer_maps,
            runtime_enabled=runtime_enabled,
            production_routing_authorized=production_routing_authorized,
        )
        for key in keys
    ]
    counts = Counter(record["closeout_readiness_status"] for record in closeout_records)
    blockers = Counter(reason for record in closeout_records for reason in record["blockers"])
    envelope = {
        "schema_version": "v3_1.experimental_runtime_readiness_closeout.1",
        "run": {
            "run_id": run_id,
            "manifest_eligibility_hash": _source_hash(manifest_consumption_eligibility),
            "controlled_test_consumption_hash": _source_hash(controlled_test_consumption),
            "controlled_consumption_output_validation_hash": _source_hash(controlled_consumption_output_validation),
            "controlled_consumption_parity_snapshot_hash": _source_hash(controlled_consumption_parity_snapshot),
            "trace_backfilled_semantic_parity_hash": _source_hash(trace_backfilled_semantic_parity),
            "controlled_consumption_promotion_readiness_hash": _source_hash(controlled_consumption_promotion_readiness),
            "limited_experimental_runtime_guards_hash": _source_hash(limited_experimental_runtime_guards),
            "limited_experimental_runtime_dry_run_hash": _source_hash(limited_experimental_runtime_dry_run),
            "dry_run_result_stability_hash": _source_hash(dry_run_result_stability),
        },
        "summary": {
            "records_evaluated": len(closeout_records),
            "ready_count": counts["ready_for_future_limited_experimental_runtime_phase"],
            "blocked_count": len(closeout_records) - counts["ready_for_future_limited_experimental_runtime_phase"],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "closeout_status_counts": {
            status: counts[status]
            for status in EXPERIMENTAL_RUNTIME_READINESS_CLOSEOUT_STATUSES
        },
        "unresolved_blocker_counts": dict(sorted(blockers.items())),
        "evidence_chain_summary": {
            "manifest_eligibility_records": len(eligibility),
            "controlled_consumption_records": len(consumption),
            "output_validation_records": len(validation),
            "structural_parity_records": len(structural),
            "semantic_parity_records": len(semantic),
            "promotion_readiness_records": len(promotion),
            "runtime_guard_records": len(guards),
            "dry_run_records": len(dry_runs),
            "dry_run_stability_records": len(stability),
            "runtime_manifest_consumption_enabled": runtime_enabled,
            "production_routing_authorized": production_routing_authorized,
        },
        "closeout_records": closeout_records,
        "safety_confirmations": {
            "closeout_authorizes_runtime_manifest_consumption": False,
            "closeout_authorizes_production_routing": False,
            "closeout_is_production_approval": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_experimental_runtime_readiness_closeout",
            "observational_only": True,
            "audit_reporting_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_EXPERIMENTAL_RUNTIME_READINESS_CLOSEOUT_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _closeout_record(
    *,
    key: tuple[str | None, str | None],
    layers: dict[str, dict[tuple[str | None, str | None], dict[str, Any]]],
    runtime_enabled: bool,
    production_routing_authorized: bool,
) -> dict[str, Any]:
    manifest_id, fixture_set_id = key
    evidence = {
        "manifest_eligibility": (layers["eligibility"].get(key) or {}).get("eligibility_status"),
        "controlled_consumption": (layers["consumption"].get(key) or {}).get("controlled_consumption_status"),
        "output_validation": (layers["validation"].get(key) or {}).get("validation_status"),
        "structural_parity": (layers["structural"].get(key) or {}).get("parity_status"),
        "semantic_parity": (layers["semantic"].get(key) or {}).get("final_semantic_parity_status"),
        "promotion_readiness": (layers["promotion"].get(key) or {}).get("promotion_readiness_status"),
        "runtime_guard": (layers["guard"].get(key) or {}).get("guard_contract_status"),
        "runtime_dry_run": (layers["dry_run"].get(key) or {}).get("dry_run_status"),
        "dry_run_stability": (layers["stability"].get(key) or {}).get("stability_status"),
    }
    blockers = _blockers(evidence, runtime_enabled=runtime_enabled, production_routing_authorized=production_routing_authorized)
    status = blockers[0] if blockers else "ready_for_future_limited_experimental_runtime_phase"
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "status": status,
        "token": STABLE_EXPERIMENTAL_RUNTIME_READINESS_CLOSEOUT_TOKEN,
    }
    return {
        "experimental_runtime_readiness_closeout_id": f"v3_1_experimental_runtime_closeout_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "evidence_chain_statuses": evidence,
        "closeout_readiness_status": status,
        "blockers": blockers,
        "closeout_readiness_authorizes_runtime_routing": False,
        "closeout_readiness_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "audit_reporting_only": True,
            "runtime_behavior_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
            "closeout_readiness_does_not_authorize_runtime_or_production_routing": True,
        },
    }


def _blockers(evidence: dict[str, Any], *, runtime_enabled: bool, production_routing_authorized: bool) -> list[str]:
    blockers: list[str] = []
    if evidence["manifest_eligibility"] != "eligible_for_controlled_test_consumption":
        blockers.append("blocked_missing_manifest_eligibility")
    if evidence["controlled_consumption"] != "consumed_in_controlled_test":
        blockers.append("blocked_missing_controlled_consumption")
    if evidence["output_validation"] != "valid_controlled_test_output":
        blockers.append("blocked_missing_output_validation")
    if evidence["structural_parity"] != "parity_confirmed":
        blockers.append("blocked_missing_structural_parity")
    if evidence["semantic_parity"] != "semantic_parity_confirmed":
        blockers.append("blocked_missing_semantic_parity")
    if evidence["promotion_readiness"] != "ready_for_limited_experimental_runtime_consideration":
        blockers.append("blocked_missing_promotion_readiness")
    if evidence["runtime_guard"] != "guard_contract_ready":
        blockers.append("blocked_missing_runtime_guard")
    if evidence["runtime_dry_run"] != "dry_run_ready":
        blockers.append("blocked_missing_dry_run")
    if evidence["dry_run_stability"] != "dry_run_stable":
        blockers.append("blocked_missing_dry_run_stability")
    if runtime_enabled:
        blockers.append("blocked_runtime_consumption_enabled")
    if production_routing_authorized:
        blockers.append("blocked_production_routing_authorized")
    return blockers


def _records(value: dict[str, Any] | list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get(key, [])]


def _by_key(records: list[dict[str, Any]]) -> dict[tuple[str | None, str | None], dict[str, Any]]:
    return {
        _trace_key(record): record
        for record in records
        if _trace_key(record) != (None, None)
    }


def _trace_key(record: dict[str, Any]) -> tuple[str | None, str | None]:
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    return (str(manifest_id) if manifest_id is not None else None, str(fixture_set_id) if fixture_set_id is not None else None)


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


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
