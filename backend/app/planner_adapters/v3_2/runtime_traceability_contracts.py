"""Runtime traceability contracts for v3.2 governance.

This layer validates deterministic trace identity and end-to-end governance
lineage across the v3.2 runtime contract chain. It is governance-only and does
not enable runtime manifest consumption or production routing.
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
from app.planner_adapters.v3_2.runtime_determinism_validation_contracts import (
    RUNTIME_DETERMINISM_SATISFIED,
    RUNTIME_REPLAY_CONSISTENCY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import RUNTIME_DIFF_AUDIT_SATISFIED
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED


RUNTIME_TRACEABILITY_SATISFIED = "runtime_traceability_satisfied"
RUNTIME_TRACEABILITY_BLOCKED = "runtime_traceability_blocked"
RUNTIME_TRACE_IDENTITY_MISSING = "runtime_trace_identity_missing"
RUNTIME_SOURCE_LINEAGE_MISSING = "runtime_source_lineage_missing"
RUNTIME_MANIFEST_LINEAGE_MISSING = "runtime_manifest_lineage_missing"
RUNTIME_FIXTURE_LINEAGE_MISSING = "runtime_fixture_lineage_missing"
RUNTIME_ENTRYPOINT_LINEAGE_MISSING = "runtime_entrypoint_lineage_missing"
RUNTIME_ISOLATION_LINEAGE_MISSING = "runtime_isolation_lineage_missing"
RUNTIME_SESSION_LINEAGE_MISSING = "runtime_session_lineage_missing"
RUNTIME_SAFETY_ROLLBACK_LINEAGE_MISSING = "runtime_safety_rollback_lineage_missing"
RUNTIME_DIFF_AUDIT_LINEAGE_MISSING = "runtime_diff_audit_lineage_missing"
RUNTIME_DETERMINISM_LINEAGE_MISSING = "runtime_determinism_lineage_missing"
RUNTIME_FINAL_CLASSIFICATION_LINEAGE_MISSING = "runtime_final_classification_lineage_missing"
RUNTIME_EVIDENCE_UNEXPLAINABLE = "runtime_evidence_unexplainable"
RUNTIME_LINEAGE_BROKEN = "runtime_lineage_broken"

RUNTIME_TRACEABILITY_STATUSES = (
    RUNTIME_TRACEABILITY_SATISFIED,
    RUNTIME_TRACEABILITY_BLOCKED,
    RUNTIME_TRACE_IDENTITY_MISSING,
    RUNTIME_SOURCE_LINEAGE_MISSING,
    RUNTIME_MANIFEST_LINEAGE_MISSING,
    RUNTIME_FIXTURE_LINEAGE_MISSING,
    RUNTIME_ENTRYPOINT_LINEAGE_MISSING,
    RUNTIME_ISOLATION_LINEAGE_MISSING,
    RUNTIME_SESSION_LINEAGE_MISSING,
    RUNTIME_SAFETY_ROLLBACK_LINEAGE_MISSING,
    RUNTIME_DIFF_AUDIT_LINEAGE_MISSING,
    RUNTIME_DETERMINISM_LINEAGE_MISSING,
    RUNTIME_FINAL_CLASSIFICATION_LINEAGE_MISSING,
    RUNTIME_EVIDENCE_UNEXPLAINABLE,
    RUNTIME_LINEAGE_BROKEN,
)
RUNTIME_LINEAGE_STATUSES = (
    RUNTIME_TRACEABILITY_SATISFIED,
    RUNTIME_LINEAGE_BROKEN,
    RUNTIME_SOURCE_LINEAGE_MISSING,
    RUNTIME_MANIFEST_LINEAGE_MISSING,
    RUNTIME_FIXTURE_LINEAGE_MISSING,
    RUNTIME_ENTRYPOINT_LINEAGE_MISSING,
    RUNTIME_ISOLATION_LINEAGE_MISSING,
    RUNTIME_SESSION_LINEAGE_MISSING,
    RUNTIME_SAFETY_ROLLBACK_LINEAGE_MISSING,
    RUNTIME_DIFF_AUDIT_LINEAGE_MISSING,
    RUNTIME_DETERMINISM_LINEAGE_MISSING,
    RUNTIME_FINAL_CLASSIFICATION_LINEAGE_MISSING,
)
STABLE_RUNTIME_TRACEABILITY_TOKEN = "v3_2_phase_7_runtime_traceability_contracts_token"


def build_runtime_traceability_contract(
    runtime_traceability_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_diff_audit_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_determinism_validation_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_7_runtime_traceability_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime traceability contracts."""

    requests = _records(runtime_traceability_requests, "runtime_traceability_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    determinism_records = _records(runtime_determinism_validation_contracts, "runtime_determinism_validation_contracts")
    entrypoint_by_key = {_trace_key(record): record for record in entrypoints if _trace_key(record)}
    isolation_by_key = {_trace_key(record): record for record in isolations if _trace_key(record)}
    session_by_key = {_trace_key(record): record for record in sessions if _trace_key(record)}
    safety_by_key = {_trace_key(record): record for record in safety_records if _trace_key(record)}
    diff_by_key = {_trace_key(record): record for record in diff_records if _trace_key(record)}
    determinism_by_key = {_trace_key(record): record for record in determinism_records if _trace_key(record)}
    contracts = [
        evaluate_runtime_traceability_contract(
            request,
            entrypoint_contract=entrypoint_by_key.get(_trace_key(request)),
            isolation_contract=isolation_by_key.get(_trace_key(request)),
            session_boundary_contract=session_by_key.get(_trace_key(request)),
            safety_rollback_contract=safety_by_key.get(_trace_key(request)),
            diff_audit_contract=diff_by_key.get(_trace_key(request)),
            determinism_validation_contract=determinism_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [
            evaluate_runtime_traceability_contract(
                {},
                entrypoint_contract=None,
                isolation_contract=None,
                session_boundary_contract=None,
                safety_rollback_contract=None,
                diff_audit_contract=None,
                determinism_validation_contract=None,
            )
        ]
    return summarize_runtime_traceability_contract(
        contracts,
        run_id=run_id,
        runtime_traceability_requests_hash=_source_hash(runtime_traceability_requests),
        experimental_runtime_entrypoint_contracts_hash=_source_hash(experimental_runtime_entrypoint_contracts),
        runtime_isolation_contracts_hash=_source_hash(runtime_isolation_contracts),
        runtime_session_boundary_contracts_hash=_source_hash(runtime_session_boundary_contracts),
        runtime_safety_rollback_contracts_hash=_source_hash(runtime_safety_rollback_contracts),
        runtime_diff_audit_contracts_hash=_source_hash(runtime_diff_audit_contracts),
        runtime_determinism_validation_contracts_hash=_source_hash(runtime_determinism_validation_contracts),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
        session_count=len(sessions),
        safety_rollback_count=len(safety_records),
        diff_audit_count=len(diff_records),
        determinism_count=len(determinism_records),
    )


def evaluate_runtime_traceability_contract(
    runtime_traceability_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
    safety_rollback_contract: dict[str, Any] | None,
    diff_audit_contract: dict[str, Any] | None,
    determinism_validation_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one traceability request against prior governance lineage."""

    request = deepcopy(runtime_traceability_request)
    entrypoint = deepcopy(entrypoint_contract) if entrypoint_contract else None
    isolation = deepcopy(isolation_contract) if isolation_contract else None
    session = deepcopy(session_boundary_contract) if session_boundary_contract else None
    safety = deepcopy(safety_rollback_contract) if safety_rollback_contract else None
    diff = deepcopy(diff_audit_contract) if diff_audit_contract else None
    determinism = deepcopy(determinism_validation_contract) if determinism_validation_contract else None
    trace_blockers = _trace_blockers(request)
    lineage_blockers = _lineage_blockers(request, entrypoint, isolation, session, safety, diff, determinism)
    traceability_status = classify_runtime_traceability_state(request, blockers=trace_blockers + lineage_blockers)
    lineage_status = classify_runtime_lineage_state(request, blockers=lineage_blockers)
    manifest_id = request.get("manifest_id") or (determinism or {}).get("manifest_id") or (diff or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (determinism or {}).get("fixture_set_id") or (diff or {}).get("fixture_set_id")
    seed = {"trace_id": request.get("runtime_trace_id"), "manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "status": traceability_status, "token": STABLE_RUNTIME_TRACEABILITY_TOKEN}
    return {
        "runtime_traceability_contract_id": f"v3_2_runtime_traceability_{deterministic_hash(seed)[:16]}",
        "runtime_trace_id": request.get("runtime_trace_id"),
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_trace_identity_state": request.get("runtime_trace_identity_state"),
        "runtime_source_evidence_lineage": request.get("runtime_source_evidence_lineage"),
        "runtime_manifest_lineage": request.get("runtime_manifest_lineage"),
        "runtime_fixture_lineage": request.get("runtime_fixture_lineage"),
        "runtime_entrypoint_lineage": request.get("runtime_entrypoint_lineage"),
        "runtime_isolation_lineage": request.get("runtime_isolation_lineage"),
        "runtime_session_lineage": request.get("runtime_session_lineage"),
        "runtime_safety_rollback_lineage": request.get("runtime_safety_rollback_lineage"),
        "runtime_diff_audit_lineage": request.get("runtime_diff_audit_lineage"),
        "runtime_determinism_lineage": request.get("runtime_determinism_lineage"),
        "runtime_final_classification_lineage": request.get("runtime_final_classification_lineage"),
        "runtime_trace_completeness_state": request.get("runtime_trace_completeness_state"),
        "runtime_trace_explainability_state": request.get("runtime_trace_explainability_state"),
        "entrypoint_contract_status": (entrypoint or {}).get("runtime_entrypoint_status"),
        "isolation_contract_status": (isolation or {}).get("runtime_isolation_status"),
        "session_boundary_contract_status": (session or {}).get("runtime_session_boundary_status"),
        "safety_contract_status": (safety or {}).get("runtime_safety_status"),
        "rollback_contract_status": (safety or {}).get("runtime_rollback_status"),
        "diff_audit_contract_status": (diff or {}).get("runtime_diff_audit_status"),
        "determinism_contract_status": (determinism or {}).get("runtime_determinism_status"),
        "runtime_traceability_status": traceability_status,
        "runtime_lineage_status": lineage_status,
        "runtime_trace_blocker_state": "blocked" if trace_blockers else "unblocked_for_contract_only",
        "runtime_lineage_blocker_state": "blocked" if lineage_blockers else "unblocked_for_contract_only",
        "trace_blockers": trace_blockers,
        "lineage_blockers": lineage_blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "runtime_traceability_authorizes_runtime_consumption": False,
        "runtime_traceability_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_traceability_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_traceability_failures_allowed": False,
            "implicit_lineage_approval_allowed": False,
            "fallback_traceability_allowed": False,
        },
    }


def classify_runtime_traceability_state(runtime_traceability_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _trace_blockers(runtime_traceability_request or {}))
    for blocker, status in _STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    if blocker_set:
        return RUNTIME_TRACEABILITY_BLOCKED
    return RUNTIME_TRACEABILITY_SATISFIED


def classify_runtime_lineage_state(runtime_traceability_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _lineage_blockers(runtime_traceability_request or {}, None, None, None, None, None, None))
    for blocker, status in _LINEAGE_STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    if blocker_set:
        return RUNTIME_LINEAGE_BROKEN
    return RUNTIME_TRACEABILITY_SATISFIED


def summarize_runtime_traceability_contract(
    runtime_traceability_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_7_runtime_traceability_contracts",
    runtime_traceability_requests_hash: str | None = None,
    experimental_runtime_entrypoint_contracts_hash: str | None = None,
    runtime_isolation_contracts_hash: str | None = None,
    runtime_session_boundary_contracts_hash: str | None = None,
    runtime_safety_rollback_contracts_hash: str | None = None,
    runtime_diff_audit_contracts_hash: str | None = None,
    runtime_determinism_validation_contracts_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
    safety_rollback_count: int | None = None,
    diff_audit_count: int | None = None,
    determinism_count: int | None = None,
) -> dict[str, Any]:
    contracts = [deepcopy(record) for record in sorted(runtime_traceability_contracts, key=_record_sort_key)]
    trace_counts = Counter(record["runtime_traceability_status"] for record in contracts)
    lineage_counts = Counter(record["runtime_lineage_status"] for record in contracts)
    trace_blockers = Counter(blocker for record in contracts for blocker in record["trace_blockers"])
    lineage_blockers = Counter(blocker for record in contracts for blocker in record["lineage_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_traceability_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_traceability_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "runtime_isolation_contract_count": isolation_count,
            "runtime_session_boundary_contract_count": session_count,
            "runtime_safety_rollback_contract_count": safety_rollback_count,
            "runtime_diff_audit_contract_count": diff_audit_count,
            "runtime_determinism_validation_contract_count": determinism_count,
            "runtime_traceability_requests_hash": runtime_traceability_requests_hash,
            "experimental_runtime_entrypoint_contracts_hash": experimental_runtime_entrypoint_contracts_hash,
            "runtime_isolation_contracts_hash": runtime_isolation_contracts_hash,
            "runtime_session_boundary_contracts_hash": runtime_session_boundary_contracts_hash,
            "runtime_safety_rollback_contracts_hash": runtime_safety_rollback_contracts_hash,
            "runtime_diff_audit_contracts_hash": runtime_diff_audit_contracts_hash,
            "runtime_determinism_validation_contracts_hash": runtime_determinism_validation_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_traceability_satisfied_count": trace_counts[RUNTIME_TRACEABILITY_SATISFIED],
            "runtime_traceability_blocked_count": len(contracts) - trace_counts[RUNTIME_TRACEABILITY_SATISFIED],
            "runtime_lineage_broken_count": lineage_counts[RUNTIME_LINEAGE_BROKEN] + trace_counts[RUNTIME_LINEAGE_BROKEN],
            "runtime_evidence_unexplainable_count": trace_counts[RUNTIME_EVIDENCE_UNEXPLAINABLE],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_traceability_status_counts": {status: trace_counts[status] for status in RUNTIME_TRACEABILITY_STATUSES},
        "runtime_lineage_status_counts": {status: lineage_counts[status] for status in RUNTIME_LINEAGE_STATUSES},
        "runtime_trace_identity_distribution": _distribution(contracts, "runtime_trace_identity_state"),
        "source_lineage_distribution": _distribution(contracts, "runtime_source_evidence_lineage"),
        "manifest_lineage_distribution": _distribution(contracts, "runtime_manifest_lineage"),
        "fixture_lineage_distribution": _distribution(contracts, "runtime_fixture_lineage"),
        "entrypoint_lineage_distribution": _distribution(contracts, "runtime_entrypoint_lineage"),
        "isolation_lineage_distribution": _distribution(contracts, "runtime_isolation_lineage"),
        "session_lineage_distribution": _distribution(contracts, "runtime_session_lineage"),
        "safety_rollback_lineage_distribution": _distribution(contracts, "runtime_safety_rollback_lineage"),
        "diff_audit_lineage_distribution": _distribution(contracts, "runtime_diff_audit_lineage"),
        "determinism_lineage_distribution": _distribution(contracts, "runtime_determinism_lineage"),
        "final_classification_lineage_distribution": _distribution(contracts, "runtime_final_classification_lineage"),
        "runtime_evidence_explainability_distribution": _distribution(contracts, "runtime_trace_explainability_state"),
        "runtime_trace_blocker_distribution": dict(sorted(trace_blockers.items())),
        "runtime_lineage_blocker_distribution": dict(sorted(lineage_blockers.items())),
        "runtime_disabled_path_verification": {"runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_runtime_prohibited": True, "production_routing_authorized": False, "silent_traceability_failures_allowed": False, "implicit_lineage_approval_allowed": False, "fallback_traceability_allowed": False},
        "runtime_traceability_contracts": contracts,
        "safety_confirmations": {"runtime_traceability_enables_runtime_manifest_consumption": False, "runtime_traceability_authorizes_production_routing": False, "runtime_traceability_allows_silent_failures": False, "production_runtime_routing_prohibited": True, "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "legacy_planner_ownership_preserved": True, "production_output_affected": False, "production_behavior_changed": False, "production_planner_routing_changed": False},
        "metadata": {"source": "v3_2_runtime_traceability_contracts", "governance_only": True, "runtime_traceability_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_consumer": False, "production_behavior_changed": False, "planner_remap_performed": False, "stable_generation_token": STABLE_RUNTIME_TRACEABILITY_TOKEN, "deterministic_serializer": "json_sort_keys_sha256"},
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


_STATUS_PRIORITY = (
    ("runtime_trace_identity_missing", RUNTIME_TRACE_IDENTITY_MISSING),
    ("runtime_source_lineage_missing", RUNTIME_SOURCE_LINEAGE_MISSING),
    ("runtime_manifest_lineage_missing", RUNTIME_MANIFEST_LINEAGE_MISSING),
    ("runtime_fixture_lineage_missing", RUNTIME_FIXTURE_LINEAGE_MISSING),
    ("runtime_entrypoint_lineage_missing", RUNTIME_ENTRYPOINT_LINEAGE_MISSING),
    ("runtime_isolation_lineage_missing", RUNTIME_ISOLATION_LINEAGE_MISSING),
    ("runtime_session_lineage_missing", RUNTIME_SESSION_LINEAGE_MISSING),
    ("runtime_safety_rollback_lineage_missing", RUNTIME_SAFETY_ROLLBACK_LINEAGE_MISSING),
    ("runtime_diff_audit_lineage_missing", RUNTIME_DIFF_AUDIT_LINEAGE_MISSING),
    ("runtime_determinism_lineage_missing", RUNTIME_DETERMINISM_LINEAGE_MISSING),
    ("runtime_final_classification_lineage_missing", RUNTIME_FINAL_CLASSIFICATION_LINEAGE_MISSING),
    ("runtime_evidence_unexplainable", RUNTIME_EVIDENCE_UNEXPLAINABLE),
    ("runtime_lineage_broken", RUNTIME_LINEAGE_BROKEN),
)
_LINEAGE_STATUS_PRIORITY = _STATUS_PRIORITY[1:]


def _trace_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not request.get("runtime_trace_id") or request.get("runtime_trace_identity_state") != "runtime_trace_identity_present":
        blockers.append("runtime_trace_identity_missing")
    if request.get("runtime_trace_explainability_state") != "runtime_evidence_explainable":
        blockers.append("runtime_evidence_unexplainable")
    if request.get("runtime_trace_completeness_state") != "runtime_trace_complete":
        blockers.append("runtime_lineage_broken")
    return sorted(set(blockers), key=blockers.index)


def _lineage_blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None, isolation: dict[str, Any] | None, session: dict[str, Any] | None, safety: dict[str, Any] | None, diff: dict[str, Any] | None, determinism: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    expected = {
        "runtime_source_evidence_lineage": "source_lineage_present",
        "runtime_manifest_lineage": "manifest_lineage_present",
        "runtime_fixture_lineage": "fixture_lineage_present",
        "runtime_entrypoint_lineage": "entrypoint_lineage_present",
        "runtime_isolation_lineage": "isolation_lineage_present",
        "runtime_session_lineage": "session_lineage_present",
        "runtime_safety_rollback_lineage": "safety_rollback_lineage_present",
        "runtime_diff_audit_lineage": "diff_audit_lineage_present",
        "runtime_determinism_lineage": "determinism_lineage_present",
        "runtime_final_classification_lineage": "final_classification_lineage_present",
    }
    blocker_names = {
        "runtime_source_evidence_lineage": "runtime_source_lineage_missing",
        "runtime_manifest_lineage": "runtime_manifest_lineage_missing",
        "runtime_fixture_lineage": "runtime_fixture_lineage_missing",
        "runtime_entrypoint_lineage": "runtime_entrypoint_lineage_missing",
        "runtime_isolation_lineage": "runtime_isolation_lineage_missing",
        "runtime_session_lineage": "runtime_session_lineage_missing",
        "runtime_safety_rollback_lineage": "runtime_safety_rollback_lineage_missing",
        "runtime_diff_audit_lineage": "runtime_diff_audit_lineage_missing",
        "runtime_determinism_lineage": "runtime_determinism_lineage_missing",
        "runtime_final_classification_lineage": "runtime_final_classification_lineage_missing",
    }
    for field, expected_value in expected.items():
        if request.get(field) != expected_value:
            blockers.append(blocker_names[field])
    if entrypoint is None or entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
        blockers.append("runtime_entrypoint_lineage_missing")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("runtime_isolation_lineage_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("runtime_session_lineage_missing")
    if safety is None or safety.get("runtime_safety_status") != RUNTIME_SAFETY_SATISFIED or safety.get("runtime_rollback_status") != RUNTIME_ROLLBACK_READY:
        blockers.append("runtime_safety_rollback_lineage_missing")
    if diff is None or diff.get("runtime_diff_audit_status") != RUNTIME_DIFF_AUDIT_SATISFIED or diff.get("runtime_drift_status") != RUNTIME_DIFF_AUDIT_SATISFIED:
        blockers.append("runtime_diff_audit_lineage_missing")
    if determinism is None or determinism.get("runtime_determinism_status") != RUNTIME_DETERMINISM_SATISFIED or determinism.get("runtime_replay_status") != RUNTIME_REPLAY_CONSISTENCY_SATISFIED:
        blockers.append("runtime_determinism_lineage_missing")
    if request.get("runtime_lineage_integrity_state") == RUNTIME_LINEAGE_BROKEN:
        blockers.append("runtime_lineage_broken")
    return sorted(set(blockers), key=blockers.index)


def _records(value: dict[str, Any] | list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [deepcopy(record) for record in value]
    return [deepcopy(record) for record in value.get(key, [])]


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
