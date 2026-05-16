"""Runtime drift detection contracts for v3.2 governance.

This layer validates explicit drift baselines against current runtime evidence
on top of the v3.2 runtime governance chain. It is governance-only and does not
enable runtime manifest consumption or production routing.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash
from app.planner_adapters.v3_2.experimental_runtime_entrypoint_contracts import (
    EXPERIMENTAL_RUNTIME_ELIGIBLE,
    PRODUCTION_RUNTIME_PROHIBITED,
)
from app.planner_adapters.v3_2.runtime_determinism_validation_contracts import RUNTIME_DETERMINISM_SATISFIED
from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import RUNTIME_DIFF_AUDIT_SATISFIED
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_replayability_contracts import RUNTIME_REPLAYABILITY_SATISFIED
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED
from app.planner_adapters.v3_2.runtime_traceability_contracts import RUNTIME_TRACEABILITY_SATISFIED


RUNTIME_DRIFT_DETECTION_SATISFIED = "runtime_drift_detection_satisfied"
RUNTIME_DRIFT_DETECTION_BLOCKED = "runtime_drift_detection_blocked"
RUNTIME_DRIFT_BASELINE_MISSING = "runtime_drift_baseline_missing"
CURRENT_RUNTIME_EVIDENCE_MISSING = "current_runtime_evidence_missing"
RUNTIME_DRIFT_NOT_DETECTED = "runtime_drift_not_detected"
RUNTIME_DRIFT_DETECTED = "runtime_drift_detected"
RUNTIME_EXPECTED_DRIFT_DETECTED = "runtime_expected_drift_detected"
RUNTIME_UNEXPECTED_DRIFT_DETECTED = "runtime_unexpected_drift_detected"
RUNTIME_UNREVIEWED_DRIFT_DETECTED = "runtime_unreviewed_drift_detected"
RUNTIME_DRIFT_SEVERITY_NONE = "runtime_drift_severity_none"
RUNTIME_DRIFT_SEVERITY_LOW = "runtime_drift_severity_low"
RUNTIME_DRIFT_SEVERITY_MODERATE = "runtime_drift_severity_moderate"
RUNTIME_DRIFT_SEVERITY_HIGH = "runtime_drift_severity_high"
RUNTIME_DRIFT_SEVERITY_CRITICAL = "runtime_drift_severity_critical"
RUNTIME_DRIFT_REPLAYABILITY_COMPATIBILITY_MISSING = "runtime_drift_replayability_compatibility_missing"
RUNTIME_DRIFT_TRACEABILITY_COMPATIBILITY_MISSING = "runtime_drift_traceability_compatibility_missing"
RUNTIME_DRIFT_DETERMINISM_COMPATIBILITY_MISSING = "runtime_drift_determinism_compatibility_missing"
RUNTIME_DRIFT_DIFF_AUDIT_COMPATIBILITY_MISSING = "runtime_drift_diff_audit_compatibility_missing"
RUNTIME_DRIFT_ROLLBACK_COMPATIBILITY_MISSING = "runtime_drift_rollback_compatibility_missing"
RUNTIME_DRIFT_SESSION_COMPATIBILITY_MISSING = "runtime_drift_session_compatibility_missing"
RUNTIME_DRIFT_ISOLATION_COMPATIBILITY_MISSING = "runtime_drift_isolation_compatibility_missing"
RUNTIME_DRIFT_ENTRYPOINT_COMPATIBILITY_MISSING = "runtime_drift_entrypoint_compatibility_missing"

RUNTIME_DRIFT_DETECTION_STATUSES = (
    RUNTIME_DRIFT_DETECTION_SATISFIED,
    RUNTIME_DRIFT_DETECTION_BLOCKED,
    RUNTIME_DRIFT_BASELINE_MISSING,
    CURRENT_RUNTIME_EVIDENCE_MISSING,
    RUNTIME_DRIFT_NOT_DETECTED,
    RUNTIME_DRIFT_DETECTED,
    RUNTIME_EXPECTED_DRIFT_DETECTED,
    RUNTIME_UNEXPECTED_DRIFT_DETECTED,
    RUNTIME_UNREVIEWED_DRIFT_DETECTED,
    RUNTIME_DRIFT_REPLAYABILITY_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_TRACEABILITY_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_DETERMINISM_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_DIFF_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_DRIFT_ENTRYPOINT_COMPATIBILITY_MISSING,
)
RUNTIME_DRIFT_SEVERITY_STATUSES = (
    RUNTIME_DRIFT_SEVERITY_NONE,
    RUNTIME_DRIFT_SEVERITY_LOW,
    RUNTIME_DRIFT_SEVERITY_MODERATE,
    RUNTIME_DRIFT_SEVERITY_HIGH,
    RUNTIME_DRIFT_SEVERITY_CRITICAL,
)
STABLE_RUNTIME_DRIFT_DETECTION_TOKEN = "v3_2_phase_9_runtime_drift_detection_contracts_token"


def build_runtime_drift_detection_contract(
    runtime_drift_detection_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_diff_audit_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_determinism_validation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_traceability_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_replayability_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_9_runtime_drift_detection_contracts",
) -> dict[str, Any]:
    requests = _records(runtime_drift_detection_requests, "runtime_drift_detection_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    determinism_records = _records(runtime_determinism_validation_contracts, "runtime_determinism_validation_contracts")
    traceability_records = _records(runtime_traceability_contracts, "runtime_traceability_contracts")
    replayability_records = _records(runtime_replayability_contracts, "runtime_replayability_contracts")
    maps = {
        "entrypoint": _by_key(entrypoints),
        "isolation": _by_key(isolations),
        "session": _by_key(sessions),
        "safety": _by_key(safety_records),
        "diff": _by_key(diff_records),
        "determinism": _by_key(determinism_records),
        "traceability": _by_key(traceability_records),
        "replayability": _by_key(replayability_records),
    }
    contracts = [
        evaluate_runtime_drift_detection_contract(
            request,
            entrypoint_contract=maps["entrypoint"].get(_trace_key(request)),
            isolation_contract=maps["isolation"].get(_trace_key(request)),
            session_boundary_contract=maps["session"].get(_trace_key(request)),
            safety_rollback_contract=maps["safety"].get(_trace_key(request)),
            diff_audit_contract=maps["diff"].get(_trace_key(request)),
            determinism_validation_contract=maps["determinism"].get(_trace_key(request)),
            traceability_contract=maps["traceability"].get(_trace_key(request)),
            replayability_contract=maps["replayability"].get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [evaluate_runtime_drift_detection_contract({}, entrypoint_contract=None, isolation_contract=None, session_boundary_contract=None, safety_rollback_contract=None, diff_audit_contract=None, determinism_validation_contract=None, traceability_contract=None, replayability_contract=None)]
    return summarize_runtime_drift_detection_contract(
        contracts,
        run_id=run_id,
        runtime_drift_detection_requests_hash=_source_hash(runtime_drift_detection_requests),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
        session_count=len(sessions),
        safety_rollback_count=len(safety_records),
        diff_audit_count=len(diff_records),
        determinism_count=len(determinism_records),
        traceability_count=len(traceability_records),
        replayability_count=len(replayability_records),
    )


def evaluate_runtime_drift_detection_contract(
    runtime_drift_detection_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
    safety_rollback_contract: dict[str, Any] | None,
    diff_audit_contract: dict[str, Any] | None,
    determinism_validation_contract: dict[str, Any] | None,
    traceability_contract: dict[str, Any] | None,
    replayability_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    request = deepcopy(runtime_drift_detection_request)
    blockers = _drift_blockers(request, entrypoint_contract, isolation_contract, session_boundary_contract, safety_rollback_contract, diff_audit_contract, determinism_validation_contract, traceability_contract, replayability_contract)
    severity_blockers = _severity_blockers(request)
    drift_status = classify_runtime_drift_state(request, blockers=blockers + severity_blockers)
    severity_status = classify_runtime_drift_severity_state(request, blockers=severity_blockers)
    manifest_id = request.get("manifest_id") or (replayability_contract or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (replayability_contract or {}).get("fixture_set_id")
    seed = {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "drift": drift_status, "severity": severity_status, "token": STABLE_RUNTIME_DRIFT_DETECTION_TOKEN}
    return {
        "runtime_drift_detection_contract_id": f"v3_2_runtime_drift_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_drift_baseline_evidence_state": request.get("runtime_drift_baseline_evidence_state"),
        "current_runtime_evidence_state": request.get("current_runtime_evidence_state"),
        "drift_comparison_state": request.get("drift_comparison_state"),
        "drift_classification_state": request.get("drift_classification_state"),
        "drift_severity_state": request.get("drift_severity_state"),
        "expected_drift_state": request.get("expected_drift_state"),
        "unexpected_drift_state": request.get("unexpected_drift_state"),
        "unreviewed_drift_state": request.get("unreviewed_drift_state"),
        "entrypoint_contract_status": (entrypoint_contract or {}).get("runtime_entrypoint_status"),
        "isolation_contract_status": (isolation_contract or {}).get("runtime_isolation_status"),
        "session_boundary_contract_status": (session_boundary_contract or {}).get("runtime_session_boundary_status"),
        "safety_contract_status": (safety_rollback_contract or {}).get("runtime_safety_status"),
        "rollback_contract_status": (safety_rollback_contract or {}).get("runtime_rollback_status"),
        "diff_audit_contract_status": (diff_audit_contract or {}).get("runtime_diff_audit_status"),
        "determinism_contract_status": (determinism_validation_contract or {}).get("runtime_determinism_status"),
        "traceability_contract_status": (traceability_contract or {}).get("runtime_traceability_status"),
        "replayability_contract_status": (replayability_contract or {}).get("runtime_replayability_status"),
        "runtime_drift_detection_status": drift_status,
        "runtime_drift_severity_status": severity_status,
        "drift_blocker_state": "blocked" if blockers else "unblocked_for_contract_only",
        "drift_severity_blocker_state": "blocked" if severity_blockers else "unblocked_for_contract_only",
        "drift_blockers": blockers,
        "drift_severity_blockers": severity_blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "runtime_drift_detection_authorizes_runtime_consumption": False,
        "runtime_drift_detection_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {"governance_only": True, "runtime_drift_detection_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_consumer": False, "planner_remap_performed": False, "silent_drift_failures_allowed": False, "implicit_drift_approval_allowed": False, "fallback_drift_detection_allowed": False},
    }


def classify_runtime_drift_state(runtime_drift_detection_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _drift_blockers(runtime_drift_detection_request or {}, None, None, None, None, None, None, None, None))
    for blocker, status in _STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    classification = (runtime_drift_detection_request or {}).get("drift_classification_state")
    if classification == RUNTIME_DRIFT_NOT_DETECTED:
        return RUNTIME_DRIFT_NOT_DETECTED
    if classification == RUNTIME_EXPECTED_DRIFT_DETECTED:
        return RUNTIME_EXPECTED_DRIFT_DETECTED
    if classification == RUNTIME_DRIFT_DETECTED:
        return RUNTIME_DRIFT_DETECTED
    if blocker_set:
        return RUNTIME_DRIFT_DETECTION_BLOCKED
    return RUNTIME_DRIFT_DETECTION_SATISFIED


def classify_runtime_drift_severity_state(runtime_drift_detection_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _severity_blockers(runtime_drift_detection_request or {}))
    if "runtime_drift_severity_critical" in blocker_set:
        return RUNTIME_DRIFT_SEVERITY_CRITICAL
    if "runtime_drift_severity_high" in blocker_set:
        return RUNTIME_DRIFT_SEVERITY_HIGH
    if "runtime_drift_severity_moderate" in blocker_set:
        return RUNTIME_DRIFT_SEVERITY_MODERATE
    if "runtime_drift_severity_low" in blocker_set:
        return RUNTIME_DRIFT_SEVERITY_LOW
    return RUNTIME_DRIFT_SEVERITY_NONE


def summarize_runtime_drift_detection_contract(
    runtime_drift_detection_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_9_runtime_drift_detection_contracts",
    runtime_drift_detection_requests_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
    safety_rollback_count: int | None = None,
    diff_audit_count: int | None = None,
    determinism_count: int | None = None,
    traceability_count: int | None = None,
    replayability_count: int | None = None,
) -> dict[str, Any]:
    contracts = [deepcopy(record) for record in sorted(runtime_drift_detection_contracts, key=_record_sort_key)]
    drift_counts = Counter(record["runtime_drift_detection_status"] for record in contracts)
    severity_counts = Counter(record["runtime_drift_severity_status"] for record in contracts)
    blocker_counts = Counter(blocker for record in contracts for blocker in record["drift_blockers"])
    severity_blocker_counts = Counter(blocker for record in contracts for blocker in record["drift_severity_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_drift_detection_contracts.1",
        "run": {"run_id": run_id, "runtime_drift_detection_request_count": len(contracts) if request_count is None else request_count, "entrypoint_contract_count": entrypoint_count, "runtime_isolation_contract_count": isolation_count, "runtime_session_boundary_contract_count": session_count, "runtime_safety_rollback_contract_count": safety_rollback_count, "runtime_diff_audit_contract_count": diff_audit_count, "runtime_determinism_validation_contract_count": determinism_count, "runtime_traceability_contract_count": traceability_count, "runtime_replayability_contract_count": replayability_count, "runtime_drift_detection_requests_hash": runtime_drift_detection_requests_hash},
        "summary": {"records_evaluated": len(contracts), "runtime_drift_detection_satisfied_count": drift_counts[RUNTIME_DRIFT_DETECTION_SATISFIED] + drift_counts[RUNTIME_DRIFT_NOT_DETECTED], "runtime_drift_detection_blocked_count": len(contracts) - drift_counts[RUNTIME_DRIFT_DETECTION_SATISFIED] - drift_counts[RUNTIME_DRIFT_NOT_DETECTED], "runtime_drift_not_detected_count": drift_counts[RUNTIME_DRIFT_NOT_DETECTED], "runtime_expected_drift_detected_count": drift_counts[RUNTIME_EXPECTED_DRIFT_DETECTED], "runtime_unexpected_drift_detected_count": drift_counts[RUNTIME_UNEXPECTED_DRIFT_DETECTED], "runtime_unreviewed_drift_detected_count": drift_counts[RUNTIME_UNREVIEWED_DRIFT_DETECTED], "runtime_drift_severity_critical_count": severity_counts[RUNTIME_DRIFT_SEVERITY_CRITICAL], "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_routing_authorized": False, "production_default_routing_authorized": False, "production_output_affected": False, "production_behavior_changed": False, "deterministic": True},
        "runtime_drift_detection_status_counts": {status: drift_counts[status] for status in RUNTIME_DRIFT_DETECTION_STATUSES},
        "runtime_drift_severity_status_counts": {status: severity_counts[status] for status in RUNTIME_DRIFT_SEVERITY_STATUSES},
        "drift_baseline_evidence_distribution": _distribution(contracts, "runtime_drift_baseline_evidence_state"),
        "current_runtime_evidence_distribution": _distribution(contracts, "current_runtime_evidence_state"),
        "drift_comparison_distribution": _distribution(contracts, "drift_comparison_state"),
        "drift_classification_distribution": _distribution(contracts, "drift_classification_state"),
        "drift_severity_distribution": _distribution(contracts, "drift_severity_state"),
        "expected_drift_distribution": _distribution(contracts, "expected_drift_state"),
        "unexpected_drift_distribution": _distribution(contracts, "unexpected_drift_state"),
        "unreviewed_drift_distribution": _distribution(contracts, "unreviewed_drift_state"),
        "replayability_compatibility_distribution": _distribution(contracts, "replayability_contract_status"),
        "traceability_compatibility_distribution": _distribution(contracts, "traceability_contract_status"),
        "determinism_compatibility_distribution": _distribution(contracts, "determinism_contract_status"),
        "diff_audit_compatibility_distribution": _distribution(contracts, "diff_audit_contract_status"),
        "rollback_compatibility_distribution": _distribution(contracts, "rollback_contract_status"),
        "session_compatibility_distribution": _distribution(contracts, "session_boundary_contract_status"),
        "isolation_compatibility_distribution": _distribution(contracts, "isolation_contract_status"),
        "entrypoint_compatibility_distribution": _distribution(contracts, "entrypoint_contract_status"),
        "drift_blocker_distribution": dict(sorted(blocker_counts.items())),
        "drift_severity_blocker_distribution": dict(sorted(severity_blocker_counts.items())),
        "runtime_disabled_path_verification": {"runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_runtime_prohibited": True, "production_routing_authorized": False, "silent_drift_failures_allowed": False, "implicit_drift_approval_allowed": False, "fallback_drift_detection_allowed": False},
        "runtime_drift_detection_contracts": contracts,
        "safety_confirmations": {"runtime_drift_detection_enables_runtime_manifest_consumption": False, "runtime_drift_detection_authorizes_production_routing": False, "runtime_drift_detection_allows_silent_failures": False, "production_runtime_routing_prohibited": True, "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "legacy_planner_ownership_preserved": True, "production_output_affected": False, "production_behavior_changed": False, "production_planner_routing_changed": False},
        "metadata": {"source": "v3_2_runtime_drift_detection_contracts", "governance_only": True, "runtime_drift_detection_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_consumer": False, "production_behavior_changed": False, "planner_remap_performed": False, "stable_generation_token": STABLE_RUNTIME_DRIFT_DETECTION_TOKEN, "deterministic_serializer": "json_sort_keys_sha256"},
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


_STATUS_PRIORITY = (
    ("runtime_drift_entrypoint_compatibility_missing", RUNTIME_DRIFT_ENTRYPOINT_COMPATIBILITY_MISSING),
    ("runtime_drift_isolation_compatibility_missing", RUNTIME_DRIFT_ISOLATION_COMPATIBILITY_MISSING),
    ("runtime_drift_session_compatibility_missing", RUNTIME_DRIFT_SESSION_COMPATIBILITY_MISSING),
    ("runtime_drift_rollback_compatibility_missing", RUNTIME_DRIFT_ROLLBACK_COMPATIBILITY_MISSING),
    ("runtime_drift_diff_audit_compatibility_missing", RUNTIME_DRIFT_DIFF_AUDIT_COMPATIBILITY_MISSING),
    ("runtime_drift_determinism_compatibility_missing", RUNTIME_DRIFT_DETERMINISM_COMPATIBILITY_MISSING),
    ("runtime_drift_traceability_compatibility_missing", RUNTIME_DRIFT_TRACEABILITY_COMPATIBILITY_MISSING),
    ("runtime_drift_replayability_compatibility_missing", RUNTIME_DRIFT_REPLAYABILITY_COMPATIBILITY_MISSING),
    ("runtime_drift_baseline_missing", RUNTIME_DRIFT_BASELINE_MISSING),
    ("current_runtime_evidence_missing", CURRENT_RUNTIME_EVIDENCE_MISSING),
    ("runtime_unexpected_drift_detected", RUNTIME_UNEXPECTED_DRIFT_DETECTED),
    ("runtime_unreviewed_drift_detected", RUNTIME_UNREVIEWED_DRIFT_DETECTED),
)


def _drift_blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None, isolation: dict[str, Any] | None, session: dict[str, Any] | None, safety: dict[str, Any] | None, diff: dict[str, Any] | None, determinism: dict[str, Any] | None, traceability: dict[str, Any] | None, replayability: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if entrypoint is None or entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
        blockers.append("runtime_drift_entrypoint_compatibility_missing")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("runtime_drift_isolation_compatibility_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("runtime_drift_session_compatibility_missing")
    if safety is None or safety.get("runtime_safety_status") != RUNTIME_SAFETY_SATISFIED or safety.get("runtime_rollback_status") != RUNTIME_ROLLBACK_READY:
        blockers.append("runtime_drift_rollback_compatibility_missing")
    if diff is None or diff.get("runtime_diff_audit_status") != RUNTIME_DIFF_AUDIT_SATISFIED:
        blockers.append("runtime_drift_diff_audit_compatibility_missing")
    if determinism is None or determinism.get("runtime_determinism_status") != RUNTIME_DETERMINISM_SATISFIED:
        blockers.append("runtime_drift_determinism_compatibility_missing")
    if traceability is None or traceability.get("runtime_traceability_status") != RUNTIME_TRACEABILITY_SATISFIED:
        blockers.append("runtime_drift_traceability_compatibility_missing")
    if replayability is None or replayability.get("runtime_replayability_status") != RUNTIME_REPLAYABILITY_SATISFIED:
        blockers.append("runtime_drift_replayability_compatibility_missing")
    if request.get("runtime_drift_baseline_evidence_state") != "runtime_drift_baseline_present":
        blockers.append("runtime_drift_baseline_missing")
    if request.get("current_runtime_evidence_state") != "current_runtime_evidence_present":
        blockers.append("current_runtime_evidence_missing")
    if request.get("unexpected_drift_state") == RUNTIME_UNEXPECTED_DRIFT_DETECTED or request.get("drift_classification_state") == RUNTIME_UNEXPECTED_DRIFT_DETECTED:
        blockers.append("runtime_unexpected_drift_detected")
    if request.get("unreviewed_drift_state") == RUNTIME_UNREVIEWED_DRIFT_DETECTED or request.get("drift_classification_state") == RUNTIME_UNREVIEWED_DRIFT_DETECTED:
        blockers.append("runtime_unreviewed_drift_detected")
    return sorted(set(blockers), key=blockers.index)


def _severity_blockers(request: dict[str, Any]) -> list[str]:
    severity = request.get("drift_severity_state")
    if severity in {RUNTIME_DRIFT_SEVERITY_LOW, RUNTIME_DRIFT_SEVERITY_MODERATE, RUNTIME_DRIFT_SEVERITY_HIGH, RUNTIME_DRIFT_SEVERITY_CRITICAL}:
        return [severity]
    return []


def _records(value: dict[str, Any] | list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get(key, [])]


def _by_key(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {_trace_key(record): record for record in records if _trace_key(record)}


def _trace_key(record: dict[str, Any] | None) -> tuple[str, str] | None:
    if not record:
        return None
    manifest_id = record.get("manifest_id")
    fixture_set_id = record.get("fixture_set_id")
    if not manifest_id or not fixture_set_id:
        return None
    return (str(manifest_id), str(fixture_set_id))


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    return (str(record.get("fixture_set_id") or ""), str(record.get("manifest_id") or ""))


def _distribution(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(record.get(key) or "missing" for record in records).items()))


def _source_hash(value: dict[str, Any] | list[dict[str, Any]]) -> str | None:
    if isinstance(value, dict):
        return value.get("deterministic_hash")
    return None
