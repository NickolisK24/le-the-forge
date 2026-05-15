"""Admission-aware policy evaluation bridge for v3.1 governance.

This bridge lets downstream governance account for fixture source admission
status without approving fixture sets or authorizing production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


ADMISSION_AWARE_POLICY_STATUSES = (
    "policy_satisfied_for_review",
    "blocked_source_not_admitted",
    "blocked_policy_failure",
    "blocked_missing_admission_record",
    "blocked_missing_fixture_input",
    "blocked_invalid_review_state",
)
STABLE_ADMISSION_AWARE_POLICY_TOKEN = "v3_1_phase_12_admission_aware_policy_evaluation_token"


def build_admission_aware_policy_evaluation(
    *,
    fixture_source_admission_policy: dict[str, Any],
    reviewed_fixture_inputs: dict[str, Any],
    review_policy_evaluation: dict[str, Any],
    run_id: str = "v3_1_phase_12_admission_aware_policy_evaluation",
) -> dict[str, Any]:
    """Build deterministic admission-aware policy records."""

    admission_by_source = {
        str(row.get("source_id") or ""): deepcopy(row)
        for row in fixture_source_admission_policy.get("source_admission_records", [])
    }
    fixture_inputs = _fixture_inputs_by_id(reviewed_fixture_inputs.get("normalized_fixture_inputs", []))
    records = [
        _record_for_policy_evaluation(evaluation, fixture_inputs, admission_by_source)
        for evaluation in sorted(review_policy_evaluation.get("evaluations", []), key=lambda row: str(row.get("fixture_set_id") or row.get("fixture_id") or ""))
    ]
    counts = Counter(row["admission_aware_policy_status"] for row in records)
    blocker_reasons = Counter(reason for row in records for reason in row["remaining_blockers"])
    source_admission_impacts = Counter(row["source_admission_impact"] for row in records)
    envelope = {
        "schema_version": "v3_1.admission_aware_policy_evaluation.1",
        "run": {
            "run_id": run_id,
            "record_count": len(records),
            "fixture_source_admission_hash": fixture_source_admission_policy.get("deterministic_hash"),
            "reviewed_fixture_inputs_hash": reviewed_fixture_inputs.get("deterministic_hash"),
            "review_policy_evaluation_hash": review_policy_evaluation.get("deterministic_hash"),
        },
        "summary": {
            "records_evaluated": len(records),
            "satisfied_for_review_count": counts["policy_satisfied_for_review"],
            "blocked_count": len(records) - counts["policy_satisfied_for_review"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "admission_aware_status_counts": {
            status: counts[status]
            for status in ADMISSION_AWARE_POLICY_STATUSES
        },
        "blocker_reason_counts": dict(sorted(blocker_reasons.items())),
        "source_admission_impact_summary": dict(sorted(source_admission_impacts.items())),
        "remaining_blocker_summary": [
            {"reason": reason, "count": count}
            for reason, count in sorted(blocker_reasons.items(), key=lambda item: (-item[1], item[0]))
        ],
        "admission_aware_policy_records": records,
        "safety_confirmations": {
            "satisfied_for_review_is_production_approval": False,
            "admission_aware_policy_authorizes_production_routing": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
            "remaining_blockers_hidden": False,
        },
        "metadata": {
            "source": "v3_1_admission_aware_policy_evaluation",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_ADMISSION_AWARE_POLICY_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _record_for_policy_evaluation(
    evaluation: dict[str, Any],
    fixture_inputs: dict[str, dict[str, Any]],
    admission_by_source: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    fixture_id = evaluation.get("fixture_id")
    fixture_set_id = evaluation.get("fixture_set_id")
    key = str(fixture_set_id or fixture_id or "")
    fixture_input = fixture_inputs.get(key)
    if not fixture_input:
        return _policy_record(
            evaluation=evaluation,
            fixture_input=None,
            admission=None,
            status="blocked_missing_fixture_input",
            blockers=["missing_reviewed_fixture_input"],
            impact="missing_fixture_input",
        )

    source_id = str(fixture_input.get("source_id") or "")
    admission = admission_by_source.get(source_id)
    if not admission:
        return _policy_record(
            evaluation=evaluation,
            fixture_input=fixture_input,
            admission=None,
            status="blocked_missing_admission_record",
            blockers=["missing_source_admission_record"],
            impact="missing_admission_record",
        )

    if fixture_input.get("status") in {"malformed", "duplicate", "missing_source"}:
        return _policy_record(
            evaluation=evaluation,
            fixture_input=fixture_input,
            admission=admission,
            status="blocked_invalid_review_state",
            blockers=[f"invalid_review_state_{fixture_input.get('status')}"],
            impact="invalid_review_state",
        )

    admission_status = admission.get("admission_status")
    if admission_status != "admitted_for_review":
        return _policy_record(
            evaluation=evaluation,
            fixture_input=fixture_input,
            admission=admission,
            status="blocked_source_not_admitted",
            blockers=list(admission.get("block_reasons") or [f"source_admission_{admission_status}"]),
            impact="source_not_admitted",
        )

    original_policy = evaluation.get("policy_outcome")
    reason_codes = list(evaluation.get("deterministic_reason_codes") or [])
    if original_policy == "passes_policy":
        return _policy_record(
            evaluation=evaluation,
            fixture_input=fixture_input,
            admission=admission,
            status="policy_satisfied_for_review",
            blockers=[],
            impact="already_policy_satisfied",
        )
    if _is_source_unsupported_failure(original_policy, reason_codes):
        return _policy_record(
            evaluation=evaluation,
            fixture_input=fixture_input,
            admission=admission,
            status="policy_satisfied_for_review",
            blockers=[],
            impact="unsupported_source_reclassified_by_admission",
        )
    return _policy_record(
        evaluation=evaluation,
        fixture_input=fixture_input,
        admission=admission,
        status="blocked_policy_failure",
        blockers=reason_codes or [f"policy_outcome_{original_policy or 'missing'}"],
        impact="non_source_policy_failure_preserved",
    )


def _policy_record(
    *,
    evaluation: dict[str, Any],
    fixture_input: dict[str, Any] | None,
    admission: dict[str, Any] | None,
    status: str,
    blockers: list[str],
    impact: str,
) -> dict[str, Any]:
    fixture_id = evaluation.get("fixture_id")
    fixture_set_id = evaluation.get("fixture_set_id")
    source_id = fixture_input.get("source_id") if fixture_input else None
    seed = {
        "fixture_id": fixture_id,
        "fixture_set_id": fixture_set_id,
        "source_id": source_id,
        "status": status,
        "token": STABLE_ADMISSION_AWARE_POLICY_TOKEN,
    }
    return {
        "admission_aware_policy_id": f"v3_1_admission_policy_{deterministic_hash(seed)[:16]}",
        "fixture_id": fixture_id,
        "fixture_set_id": fixture_set_id,
        "source_id": source_id,
        "original_policy_status": evaluation.get("policy_outcome"),
        "original_reason_codes": list(evaluation.get("deterministic_reason_codes") or []),
        "fixture_input_status": fixture_input.get("status") if fixture_input else None,
        "admission_status": admission.get("admission_status") if admission else None,
        "admission_aware_policy_status": status,
        "remaining_blockers": sorted(set(blockers)),
        "source_admission_impact": impact,
        "non_production_authorization": {
            "satisfied_for_review_is_production_approval": False,
            "policy_authorizes_production_routing": False,
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


def _fixture_inputs_by_id(inputs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in sorted(inputs, key=lambda item: str(item.get("normalized_fixture_id") or "")):
        normalized_id = str(row.get("normalized_fixture_id") or "")
        source_fixture_id = str(row.get("source_fixture_id") or "")
        if normalized_id:
            result[normalized_id] = deepcopy(row)
        if source_fixture_id:
            result[source_fixture_id] = deepcopy(row)
    return result


def _is_source_unsupported_failure(policy_status: Any, reason_codes: list[str]) -> bool:
    if policy_status != "unsupported":
        return False
    return bool(reason_codes) and all("unsupported_fixture" in reason for reason in reason_codes)
