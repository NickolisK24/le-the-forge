"""Deterministic fixture source admission policy.

Admission means a fixture source is eligible for governance review. It does not
approve fixture sets, serialize production-authoritative manifests, or authorize
production routing.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any

from .reviewed_fixture_inputs import SUPPORTED_SOURCE_TYPES
from .trusted_shadow_consumption import deterministic_hash


FIXTURE_SOURCE_ADMISSION_STATUSES = (
    "admitted_for_review",
    "blocked_unknown_source",
    "blocked_missing_metadata",
    "blocked_missing_review_evidence",
    "blocked_unstable_identity",
    "blocked_unsupported_schema",
)
STABLE_FIXTURE_SOURCE_ADMISSION_TOKEN = "v3_1_phase_11_fixture_source_admission_policy_token"


def evaluate_fixture_source_admission_policy(
    *,
    reviewed_fixture_inputs: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_1_phase_11_fixture_source_admission_policy",
) -> dict[str, Any]:
    """Evaluate reviewed fixture input sources for governance-review admission."""

    records = _source_records(reviewed_fixture_inputs)
    evaluations = [_evaluate_source(source) for source in records]
    evaluations = sorted(evaluations, key=lambda row: (row["source_id"], row["source_type"], row["admission_id"]))
    counts = Counter(row["admission_status"] for row in evaluations)
    block_reasons = Counter(reason for row in evaluations if row["admission_status"] != "admitted_for_review" for reason in row["block_reasons"])
    source_hash = reviewed_fixture_inputs.get("deterministic_hash") if isinstance(reviewed_fixture_inputs, dict) else None
    source_schema = reviewed_fixture_inputs.get("schema_version") if isinstance(reviewed_fixture_inputs, dict) else None
    envelope = {
        "schema_version": "v3_1.fixture_source_admission_policy.1",
        "run": {
            "run_id": run_id,
            "source_count": len(evaluations),
            "reviewed_fixture_inputs_hash": source_hash,
            "reviewed_fixture_inputs_schema": source_schema,
        },
        "summary": {
            "total_sources_evaluated": len(evaluations),
            "admitted_for_review_count": counts["admitted_for_review"],
            "blocked_count": len(evaluations) - counts["admitted_for_review"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "admission_status_counts": {
            status: counts[status]
            for status in FIXTURE_SOURCE_ADMISSION_STATUSES
        },
        "block_reason_counts": dict(sorted(block_reasons.items())),
        "source_admission_records": evaluations,
        "source_evidence_summaries": [
            {
                "source_id": row["source_id"],
                "source_type": row["source_type"],
                "admission_status": row["admission_status"],
                "evidence_summary": deepcopy(row["evidence_summary"]),
            }
            for row in evaluations
        ],
        "recommended_next_governance_action": _recommended_action(evaluations),
        "safety_confirmations": {
            "admitted_sources_are_production_approved": False,
            "admission_policy_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_fixture_source_admission_policy",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_FIXTURE_SOURCE_ADMISSION_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _source_records(reviewed_fixture_inputs: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    inputs = reviewed_fixture_inputs.get("normalized_fixture_inputs", []) if isinstance(reviewed_fixture_inputs, dict) else reviewed_fixture_inputs
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in inputs:
        key = (
            str(record.get("source_id") or ""),
            str(record.get("source_type") or ""),
            str(record.get("source_path") or ""),
        )
        grouped[key].append(deepcopy(record))
    return [
        {
            "source_id": source_id,
            "source_type": source_type,
            "source_path": source_path,
            "records": sorted(records, key=lambda row: str(row.get("normalized_fixture_id") or "")),
        }
        for (source_id, source_type, source_path), records in sorted(grouped.items())
    ]


def _evaluate_source(source: dict[str, Any]) -> dict[str, Any]:
    status, block_reasons = _admission_status(source)
    evidence = _evidence_summary(source)
    source_id = source["source_id"]
    source_type = source["source_type"]
    seed = {
        "source_id": source_id,
        "source_type": source_type,
        "source_path": source["source_path"],
        "token": STABLE_FIXTURE_SOURCE_ADMISSION_TOKEN,
    }
    return {
        "admission_id": f"v3_1_source_admission_{deterministic_hash(seed)[:16]}",
        "source_id": source_id,
        "source_type": source_type,
        "source_path": source["source_path"],
        "admission_status": status,
        "evidence_summary": evidence,
        "block_reasons": block_reasons,
        "non_production_authorization": {
            "source_is_production_approved": False,
            "source_authorizes_production_routing": False,
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


def _admission_status(source: dict[str, Any]) -> tuple[str, list[str]]:
    source_id = source["source_id"].strip()
    source_type = source["source_type"].strip()
    source_path = source["source_path"].strip()
    records = source["records"]
    if not source_id or source_id == "unknown":
        return "blocked_unknown_source", ["unknown_source_id"]
    if not source_path:
        return "blocked_missing_metadata", ["missing_source_path"]
    if not source_type:
        return "blocked_missing_metadata", ["missing_source_type"]
    if source_type not in SUPPORTED_SOURCE_TYPES:
        return "blocked_unsupported_schema", [f"unsupported_source_type_{source_type}"]
    if any(not row.get("normalized_fixture_id") or not row.get("source_fixture_id") for row in records):
        return "blocked_unstable_identity", ["fixture_source_identity_unstable"]
    if not any(row.get("payload_digest") or row.get("reason_codes") for row in records):
        return "blocked_missing_review_evidence", ["missing_review_evidence"]
    return "admitted_for_review", ["source_identity_schema_and_evidence_present"]


def _evidence_summary(source: dict[str, Any]) -> dict[str, Any]:
    records = source["records"]
    status_counts = Counter(str(row.get("status") or "unknown") for row in records)
    return {
        "record_count": len(records),
        "reviewed_record_count": status_counts["reviewed"],
        "unsupported_record_count": status_counts["unsupported"],
        "malformed_record_count": status_counts["malformed"],
        "duplicate_record_count": status_counts["duplicate"],
        "missing_source_record_count": status_counts["missing_source"],
        "payload_digest_count": sum(1 for row in records if row.get("payload_digest")),
        "reason_code_count": sum(len(row.get("reason_codes") or []) for row in records),
        "normalized_fixture_ids": sorted(str(row.get("normalized_fixture_id") or "") for row in records),
    }


def _recommended_action(evaluations: list[dict[str, Any]]) -> str:
    blocked = [row for row in evaluations if row["admission_status"] != "admitted_for_review"]
    if not evaluations:
        return "provide reviewed fixture input sources before source admission can be evaluated"
    if blocked:
        return "resolve blocked source admission reasons before relying on source admission for governance review"
    return "use admitted sources as governance-review inputs only; do not authorize production routing"
