"""Deterministic diff audit for serialized approval manifests."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .approval_manifest_serialization import NON_PRODUCTION_AUTHORIZATION_STATE
from .trusted_shadow_consumption import deterministic_hash


APPROVAL_MANIFEST_DIFF_CLASSIFICATIONS = (
    "unchanged",
    "added",
    "removed",
    "changed_hash",
    "changed_metadata",
    "changed_authorization_state",
)
STABLE_APPROVAL_MANIFEST_DIFF_AUDIT_TOKEN = "v3_1_phase_9_approval_manifest_diff_audit_token"


def audit_approval_manifest_diffs(
    *,
    before: dict[str, Any] | list[dict[str, Any]],
    after: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_9_approval_manifest_diff_audit",
) -> dict[str, Any]:
    """Compare two manifest snapshots and return deterministic diff metadata."""

    before_by_id = _records_by_manifest_id(before)
    after_by_id = _records_by_manifest_id(after)
    manifest_ids = sorted(set(before_by_id) | set(after_by_id))
    records = [
        _diff_record(manifest_id, before_by_id.get(manifest_id), after_by_id.get(manifest_id))
        for manifest_id in manifest_ids
    ]
    counts = Counter(row["diff_classification"] for row in records)
    blocked_high_risk_count = sum(1 for row in records if row["blocked"] and row["high_risk"])
    envelope = {
        "schema_version": "v3_1.approval_manifest_diff_audit.1",
        "run": {
            "run_id": run_id,
            "before_manifest_count": len(before_by_id),
            "after_manifest_count": len(after_by_id),
        },
        "diff_summary": {
            "total_diffs_evaluated": len(records),
            "unchanged_count": counts["unchanged"],
            "added_count": counts["added"],
            "removed_count": counts["removed"],
            "changed_hash_count": counts["changed_hash"],
            "changed_metadata_count": counts["changed_metadata"],
            "changed_authorization_state_count": counts["changed_authorization_state"],
            "blocked_high_risk_count": blocked_high_risk_count,
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "classification_counts": {
            status: counts[status]
            for status in APPROVAL_MANIFEST_DIFF_CLASSIFICATIONS
        },
        "diff_records": records,
        "safety_confirmations": {
            "production_output_affected": False,
            "production_behavior_changed": False,
            "trusted_data_default_truth": False,
            "legacy_planner_ownership_preserved": True,
            "runtime_state_mutated": False,
            "authorization_state_changes_are_blocked_high_risk": True,
        },
        "metadata": {
            "source": "v3_1_approval_manifest_diff_audit",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_APPROVAL_MANIFEST_DIFF_AUDIT_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _records_by_manifest_id(value: dict[str, Any] | list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    records = value.get("serialized_manifests", []) if isinstance(value, dict) else value
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        manifest_id = record.get("manifest_id")
        if manifest_id:
            result[str(manifest_id)] = deepcopy(record)
    return result


def _diff_record(manifest_id: str, before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, Any]:
    if before is None:
        return _base_record(manifest_id, "added", before, after, ["manifest_added"])
    if after is None:
        return _base_record(manifest_id, "removed", before, after, ["manifest_removed"])
    if _authorization_state(before) != _authorization_state(after):
        return _base_record(
            manifest_id,
            "changed_authorization_state",
            before,
            after,
            ["authorization_state_changed_blocked_high_risk"],
            high_risk=True,
            blocked=True,
        )
    if before.get("generated_hash") != after.get("generated_hash"):
        return _base_record(manifest_id, "changed_hash", before, after, ["manifest_generated_hash_changed"])
    if _payload_hash(before) != _payload_hash(after):
        return _base_record(manifest_id, "changed_metadata", before, after, ["manifest_metadata_changed"])
    return _base_record(manifest_id, "unchanged", before, after, ["manifest_unchanged"])


def _base_record(
    manifest_id: str,
    classification: str,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    reason_codes: list[str],
    *,
    high_risk: bool = False,
    blocked: bool = False,
) -> dict[str, Any]:
    return {
        "manifest_id": manifest_id,
        "diff_classification": classification,
        "before_hash": before.get("generated_hash") if before else None,
        "after_hash": after.get("generated_hash") if after else None,
        "before_authorization_state": _authorization_state(before) if before else None,
        "after_authorization_state": _authorization_state(after) if after else None,
        "high_risk": high_risk,
        "blocked": blocked,
        "reason_codes": reason_codes,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "authorization_state_change_blocked": classification == "changed_authorization_state",
        },
    }


def _authorization_state(record: dict[str, Any] | None) -> str | None:
    if not record:
        return None
    return (record.get("authorization_status") or {}).get("authorization_state", NON_PRODUCTION_AUTHORIZATION_STATE)


def _payload_hash(record: dict[str, Any]) -> str:
    payload = deepcopy(record)
    payload.pop("generated_hash", None)
    return deterministic_hash({"manifest_payload": payload})
