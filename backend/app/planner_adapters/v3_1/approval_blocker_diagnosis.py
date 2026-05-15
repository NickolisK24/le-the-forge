"""Deterministic approval blocker diagnosis across v3.1 governance layers.

This module explains why fixture sets have not reached approval-manifest
serialization. It is observational only and never authorizes production routing.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .trusted_shadow_consumption import deterministic_hash


APPROVAL_BLOCKER_CLASSIFICATIONS = (
    "missing_reviewed_inputs",
    "insufficient_fixture_set_coverage",
    "policy_not_satisfied",
    "readiness_gate_blocked",
    "no_candidate_ready_records",
    "no_serialized_manifests",
    "malformed_or_duplicate_inputs",
    "unsupported_fixture_source",
    "unknown_blocker",
)
APPROVAL_BLOCKER_SEVERITIES = ("info", "warning", "blocking")
STABLE_APPROVAL_BLOCKER_DIAGNOSIS_TOKEN = "v3_1_phase_10_approval_blocker_diagnosis_token"


def build_approval_blocker_diagnosis(
    *,
    reviewed_fixture_inputs: dict[str, Any] | None = None,
    persisted_fixture_sets: dict[str, Any] | None = None,
    review_policy_evaluation: dict[str, Any] | None = None,
    fixture_set_readiness_gate: dict[str, Any] | None = None,
    approval_manifest_candidates: dict[str, Any] | None = None,
    approval_manifest_serialization: dict[str, Any] | None = None,
    run_id: str = "v3_1_phase_10_approval_blocker_diagnosis",
) -> dict[str, Any]:
    """Build deterministic blocker diagnosis records from v3.1 governance outputs."""

    records: list[dict[str, Any]] = []
    records.extend(_reviewed_input_blockers(reviewed_fixture_inputs or {}))
    records.extend(_fixture_set_blockers(persisted_fixture_sets or {}))
    records.extend(_policy_blockers(review_policy_evaluation or {}))
    records.extend(_readiness_blockers(fixture_set_readiness_gate or {}))
    records.extend(_candidate_blockers(approval_manifest_candidates or {}))
    records.extend(_serialization_blockers(approval_manifest_serialization or {}))

    if not records:
        records.append(
            _blocker_record(
                classification="unknown_blocker",
                severity="info",
                layer="diagnosis",
                fixture_set_id=None,
                reason="no explicit governance blocker was detected",
                recommended_action="review upstream governance artifacts for missing diagnostic coverage",
            )
        )

    records = sorted(records, key=lambda row: (row["severity_rank"], row["affected_layer"], row["blocker_type"], row["blocker_id"]))
    severity_counts = Counter(row["severity"] for row in records)
    layer_counts = Counter(row["affected_layer"] for row in records)
    type_counts = Counter(row["blocker_type"] for row in records)
    blocking_reason_counts = Counter(row["reason"] for row in records if row["severity"] == "blocking")

    envelope = {
        "schema_version": "v3_1.approval_blocker_diagnosis.1",
        "run": {
            "run_id": run_id,
            "reviewed_fixture_input_hash": (reviewed_fixture_inputs or {}).get("deterministic_hash"),
            "persisted_fixture_set_hash": (persisted_fixture_sets or {}).get("deterministic_hash"),
            "review_policy_evaluation_hash": (review_policy_evaluation or {}).get("deterministic_hash"),
            "readiness_gate_hash": (fixture_set_readiness_gate or {}).get("deterministic_hash"),
            "approval_manifest_candidate_hash": (approval_manifest_candidates or {}).get("deterministic_hash"),
            "approval_manifest_serialization_hash": (approval_manifest_serialization or {}).get("deterministic_hash"),
        },
        "summary": {
            "total_blockers": len(records),
            "info_count": severity_counts["info"],
            "warning_count": severity_counts["warning"],
            "blocking_count": severity_counts["blocking"],
            "production_affected_count": 0,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "trusted_data_default_truth": False,
            "deterministic": True,
        },
        "blocker_type_counts": {
            blocker_type: type_counts[blocker_type]
            for blocker_type in APPROVAL_BLOCKER_CLASSIFICATIONS
        },
        "severity_counts": {
            severity: severity_counts[severity]
            for severity in APPROVAL_BLOCKER_SEVERITIES
        },
        "layer_counts": dict(sorted(layer_counts.items())),
        "top_blocking_reasons": [
            {"reason": reason, "count": count}
            for reason, count in sorted(blocking_reason_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "recommended_next_action_summary": _recommended_next_action_summary(records),
        "blocker_records": [_public_record(row) for row in records],
        "safety_confirmations": {
            "diagnosis_authorizes_production_routing": False,
            "diagnosis_promotes_fixture_sets": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "runtime_state_mutated": False,
            "trusted_data_default_truth": False,
        },
        "metadata": {
            "source": "v3_1_approval_blocker_diagnosis",
            "observational_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "production_default_routing_authorized": False,
            "stable_generation_token": STABLE_APPROVAL_BLOCKER_DIAGNOSIS_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _reviewed_input_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    if not report:
        return []
    records: list[dict[str, Any]] = []
    summary = report.get("summary") or report
    if summary.get("missing_source_count", 0) > 0:
        records.append(
            _blocker_record(
                classification="missing_reviewed_inputs",
                severity="blocking",
                layer="reviewed_fixture_inputs",
                fixture_set_id=None,
                reason="reviewed fixture input source is missing",
                recommended_action="restore or generate the missing reviewed fixture input source before approval review",
            )
        )
    if summary.get("malformed_count", 0) > 0 or summary.get("duplicate_count", 0) > 0:
        records.append(
            _blocker_record(
                classification="malformed_or_duplicate_inputs",
                severity="blocking",
                layer="reviewed_fixture_inputs",
                fixture_set_id=None,
                reason="reviewed fixture inputs contain malformed or duplicate records",
                recommended_action="repair malformed fixture identifiers and deduplicate reviewed fixture inputs",
            )
        )
    normalized = _nested(report, "reviewed_fixture_inputs", "normalized_fixture_inputs", default=[])
    for row in normalized:
        if row.get("status") == "unsupported":
            records.append(
                _blocker_record(
                    classification="unsupported_fixture_source",
                    severity="warning",
                    layer="reviewed_fixture_inputs",
                    fixture_set_id=row.get("normalized_fixture_id"),
                    reason="reviewed fixture input source is unsupported",
                    recommended_action="replace unsupported fixture source data with supported reviewed fixture inputs",
                )
            )
    return records


def _fixture_set_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    if not report:
        return []
    records: list[dict[str, Any]] = []
    summary = report.get("summary") or {}
    fixture_sets = _nested(report, "persisted_fixture_sets", "fixture_sets", default=[])
    if summary.get("total_fixture_sets", len(fixture_sets)) == 0:
        records.append(
            _blocker_record(
                classification="insufficient_fixture_set_coverage",
                severity="blocking",
                layer="persisted_fixture_sets",
                fixture_set_id=None,
                reason="no persisted fixture sets are available for approval diagnosis",
                recommended_action="create persisted fixture sets from reviewed fixture workflows before policy evaluation",
            )
        )
    for row in fixture_sets:
        state = str(row.get("lifecycle_state") or "")
        if state in {"draft", "insufficient_data", "partially_approved"} or row.get("missing_fixture_ids"):
            records.append(
                _blocker_record(
                    classification="insufficient_fixture_set_coverage",
                    severity="blocking",
                    layer="persisted_fixture_sets",
                    fixture_set_id=row.get("fixture_set_id"),
                    reason=f"fixture set coverage is insufficient ({state or 'unknown'})",
                    recommended_action="complete fixture-set membership and lifecycle evidence before approval review",
                )
            )
        if state == "unsupported" or row.get("unsupported"):
            records.append(
                _blocker_record(
                    classification="unsupported_fixture_source",
                    severity="blocking",
                    layer="persisted_fixture_sets",
                    fixture_set_id=row.get("fixture_set_id"),
                    reason="persisted fixture set contains unsupported fixture source state",
                    recommended_action="resolve unsupported fixture sources before policy review can pass",
                )
            )
    return records


def _policy_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    if not report:
        return []
    records: list[dict[str, Any]] = []
    evaluations = _nested(report, "review_policy_evaluation", "evaluations", default=[])
    for row in evaluations:
        outcome = row.get("policy_outcome")
        if outcome != "passes_policy":
            records.append(
                _blocker_record(
                    classification="policy_not_satisfied",
                    severity="blocking",
                    layer="review_policy_evaluation",
                    fixture_set_id=row.get("fixture_set_id"),
                    reason=f"review policy outcome is {outcome or 'missing'}",
                    recommended_action="resolve policy blockers until the fixture set reaches passes_policy",
                )
            )
    return records


def _readiness_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    if not report:
        return []
    records: list[dict[str, Any]] = []
    readiness_records = _nested(report, "fixture_set_readiness_gate", "readiness_records", default=[])
    for row in readiness_records:
        classification = row.get("readiness_classification")
        if classification != "ready_for_approval_review":
            reasons = ", ".join(row.get("block_reason_codes") or [classification or "missing_readiness_classification"])
            records.append(
                _blocker_record(
                    classification="readiness_gate_blocked",
                    severity="blocking",
                    layer="fixture_set_readiness_gate",
                    fixture_set_id=row.get("fixture_set_id"),
                    reason=f"readiness gate blocked approval review: {reasons}",
                    recommended_action="clear readiness gate block reasons before manifest candidate generation",
                )
            )
    return records


def _candidate_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary") or {}
    candidates = _nested(report, "approval_manifest_candidates", "manifest_candidates", default=[])
    ready_count = summary.get("candidate_ready_count")
    if ready_count is None:
        ready_count = sum(1 for row in candidates if row.get("candidate_status") == "candidate_ready")
    if ready_count:
        return []
    return [
        _blocker_record(
            classification="no_candidate_ready_records",
            severity="blocking",
            layer="approval_manifest_candidates",
            fixture_set_id=None,
            reason="no manifest candidate records reached candidate_ready",
            recommended_action="resolve upstream readiness and policy blockers before manifest candidate review",
        )
    ]


def _serialization_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary") or {}
    manifests = _nested(report, "approval_manifest_serialization", "serialized_manifests", default=[])
    manifest_count = summary.get("serialized_manifest_count")
    if manifest_count is None:
        manifest_count = len(manifests)
    if manifest_count:
        return []
    return [
        _blocker_record(
            classification="no_serialized_manifests",
            severity="blocking",
            layer="approval_manifest_serialization",
            fixture_set_id=None,
            reason="no serialized approval manifests were produced",
            recommended_action="produce candidate_ready records before serialization can emit non-authoritative manifests",
        )
    ]


def _blocker_record(
    *,
    classification: str,
    severity: str,
    layer: str,
    fixture_set_id: Any,
    reason: str,
    recommended_action: str,
) -> dict[str, Any]:
    seed = {
        "classification": classification,
        "severity": severity,
        "layer": layer,
        "fixture_set_id": fixture_set_id,
        "reason": reason,
        "token": STABLE_APPROVAL_BLOCKER_DIAGNOSIS_TOKEN,
    }
    return {
        "blocker_id": f"v3_1_blocker_{deterministic_hash(seed)[:16]}",
        "blocker_type": classification if classification in APPROVAL_BLOCKER_CLASSIFICATIONS else "unknown_blocker",
        "severity": severity if severity in APPROVAL_BLOCKER_SEVERITIES else "warning",
        "severity_rank": {"blocking": 0, "warning": 1, "info": 2}.get(severity, 2),
        "affected_layer": layer,
        "affected_fixture_set_id": fixture_set_id,
        "reason": reason,
        "recommended_next_governance_action": recommended_action,
        "diagnosis_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "observational_only": True,
            "production_consumer": False,
            "planner_remap_performed": False,
        },
    }


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "severity_rank"}


def _recommended_next_action_summary(records: list[dict[str, Any]]) -> list[str]:
    actions = {
        row["recommended_next_governance_action"]
        for row in records
        if row["severity"] == "blocking"
    }
    return sorted(actions)


def _nested(value: dict[str, Any], *keys: str, default: Any) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            if isinstance(value, dict) and keys and keys[-1] in value:
                return value[keys[-1]]
            return default
        current = current[key]
    return current
