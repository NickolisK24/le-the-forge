"""Runtime determinism validation contracts for v3.2 governance.

This layer validates repeat-run stability, deterministic ordering, deterministic
hashing, and replay consistency on top of the v3.2 runtime governance stack. It
is governance-only and does not enable runtime manifest consumption or
production routing.
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
from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import RUNTIME_DIFF_AUDIT_SATISFIED
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED


RUNTIME_DETERMINISM_SATISFIED = "runtime_determinism_satisfied"
RUNTIME_DETERMINISM_BLOCKED = "runtime_determinism_blocked"
REPEAT_RUN_CONSISTENCY_SATISFIED = "repeat_run_consistency_satisfied"
REPEAT_RUN_CONSISTENCY_FAILED = "repeat_run_consistency_failed"
DETERMINISTIC_ORDERING_SATISFIED = "deterministic_ordering_satisfied"
DETERMINISTIC_ORDERING_FAILED = "deterministic_ordering_failed"
DETERMINISTIC_HASHING_SATISFIED = "deterministic_hashing_satisfied"
DETERMINISTIC_HASHING_FAILED = "deterministic_hashing_failed"
RUNTIME_REPLAY_CONSISTENCY_SATISFIED = "runtime_replay_consistency_satisfied"
RUNTIME_REPLAY_CONSISTENCY_FAILED = "runtime_replay_consistency_failed"
RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED = "runtime_nondeterministic_drift_detected"
RUNTIME_INSTABILITY_DETECTED = "runtime_instability_detected"
RUNTIME_TRANSITION_INSTABILITY_DETECTED = "runtime_transition_instability_detected"
RUNTIME_AUDIT_COMPATIBILITY_MISSING = "runtime_audit_compatibility_missing"
RUNTIME_ROLLBACK_COMPATIBILITY_MISSING = "runtime_rollback_compatibility_missing"
RUNTIME_SESSION_COMPATIBILITY_MISSING = "runtime_session_compatibility_missing"
RUNTIME_ISOLATION_COMPATIBILITY_MISSING = "runtime_isolation_compatibility_missing"
RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING = "runtime_entrypoint_compatibility_missing"

RUNTIME_DETERMINISM_STATUSES = (
    RUNTIME_DETERMINISM_SATISFIED,
    RUNTIME_DETERMINISM_BLOCKED,
    REPEAT_RUN_CONSISTENCY_FAILED,
    DETERMINISTIC_ORDERING_FAILED,
    DETERMINISTIC_HASHING_FAILED,
    RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED,
    RUNTIME_INSTABILITY_DETECTED,
    RUNTIME_TRANSITION_INSTABILITY_DETECTED,
    RUNTIME_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING,
)
RUNTIME_REPLAY_STATUSES = (
    RUNTIME_REPLAY_CONSISTENCY_SATISFIED,
    RUNTIME_REPLAY_CONSISTENCY_FAILED,
    RUNTIME_AUDIT_COMPATIBILITY_MISSING,
)
STABLE_RUNTIME_DETERMINISM_VALIDATION_TOKEN = "v3_2_phase_6_runtime_determinism_validation_contracts_token"


def build_runtime_determinism_validation_contract(
    runtime_determinism_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_diff_audit_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_6_runtime_determinism_validation_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime determinism validation contracts."""

    requests = _records(runtime_determinism_requests, "runtime_determinism_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    entrypoint_by_key = {_trace_key(record): record for record in entrypoints if _trace_key(record)}
    isolation_by_key = {_trace_key(record): record for record in isolations if _trace_key(record)}
    session_by_key = {_trace_key(record): record for record in sessions if _trace_key(record)}
    safety_by_key = {_trace_key(record): record for record in safety_records if _trace_key(record)}
    diff_by_key = {_trace_key(record): record for record in diff_records if _trace_key(record)}
    contracts = [
        evaluate_runtime_determinism_validation_contract(
            request,
            entrypoint_contract=entrypoint_by_key.get(_trace_key(request)),
            isolation_contract=isolation_by_key.get(_trace_key(request)),
            session_boundary_contract=session_by_key.get(_trace_key(request)),
            safety_rollback_contract=safety_by_key.get(_trace_key(request)),
            diff_audit_contract=diff_by_key.get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [
            evaluate_runtime_determinism_validation_contract(
                {},
                entrypoint_contract=None,
                isolation_contract=None,
                session_boundary_contract=None,
                safety_rollback_contract=None,
                diff_audit_contract=None,
            )
        ]
    return summarize_runtime_determinism_validation_contract(
        contracts,
        run_id=run_id,
        runtime_determinism_requests_hash=_source_hash(runtime_determinism_requests),
        experimental_runtime_entrypoint_contracts_hash=_source_hash(experimental_runtime_entrypoint_contracts),
        runtime_isolation_contracts_hash=_source_hash(runtime_isolation_contracts),
        runtime_session_boundary_contracts_hash=_source_hash(runtime_session_boundary_contracts),
        runtime_safety_rollback_contracts_hash=_source_hash(runtime_safety_rollback_contracts),
        runtime_diff_audit_contracts_hash=_source_hash(runtime_diff_audit_contracts),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
        session_count=len(sessions),
        safety_rollback_count=len(safety_records),
        diff_audit_count=len(diff_records),
    )


def evaluate_runtime_determinism_validation_contract(
    runtime_determinism_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
    safety_rollback_contract: dict[str, Any] | None,
    diff_audit_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one determinism request against prior governance layers."""

    request = deepcopy(runtime_determinism_request)
    entrypoint = deepcopy(entrypoint_contract) if entrypoint_contract else None
    isolation = deepcopy(isolation_contract) if isolation_contract else None
    session = deepcopy(session_boundary_contract) if session_boundary_contract else None
    safety = deepcopy(safety_rollback_contract) if safety_rollback_contract else None
    diff = deepcopy(diff_audit_contract) if diff_audit_contract else None
    determinism_blockers = _determinism_blockers(request, entrypoint, isolation, session, safety, diff)
    instability_blockers = _instability_blockers(request)
    replay_blockers = _replay_blockers(request, diff)
    determinism_status = classify_runtime_determinism_state(request, blockers=determinism_blockers + instability_blockers)
    replay_status = classify_runtime_replay_state(request, blockers=replay_blockers)
    manifest_id = request.get("manifest_id") or (diff or {}).get("manifest_id") or (safety or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (diff or {}).get("fixture_set_id") or (safety or {}).get("fixture_set_id")
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "determinism": determinism_status,
        "replay": replay_status,
        "token": STABLE_RUNTIME_DETERMINISM_VALIDATION_TOKEN,
    }
    return {
        "runtime_determinism_validation_contract_id": f"v3_2_runtime_determinism_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_entrypoint_status": (entrypoint or {}).get("runtime_entrypoint_status"),
        "runtime_isolation_status": (isolation or {}).get("runtime_isolation_status"),
        "runtime_session_boundary_status": (session or {}).get("runtime_session_boundary_status"),
        "runtime_safety_status": (safety or {}).get("runtime_safety_status"),
        "runtime_rollback_status": (safety or {}).get("runtime_rollback_status"),
        "runtime_diff_audit_status": (diff or {}).get("runtime_diff_audit_status"),
        "runtime_drift_status": (diff or {}).get("runtime_drift_status"),
        "runtime_repeat_run_state": request.get("runtime_repeat_run_state"),
        "runtime_replay_consistency_state": request.get("runtime_replay_consistency_state"),
        "runtime_deterministic_ordering_state": request.get("runtime_deterministic_ordering_state"),
        "runtime_deterministic_hashing_state": request.get("runtime_deterministic_hashing_state"),
        "runtime_transition_consistency_state": request.get("runtime_transition_consistency_state"),
        "runtime_nondeterministic_drift_state": request.get("runtime_nondeterministic_drift_state"),
        "runtime_instability_classification": request.get("runtime_instability_classification"),
        "runtime_replay_trace_classification": request.get("runtime_replay_trace_classification"),
        "runtime_determinism_status": determinism_status,
        "runtime_replay_status": replay_status,
        "runtime_repeat_run_status": REPEAT_RUN_CONSISTENCY_SATISFIED if "repeat_run_consistency_failed" not in determinism_blockers else REPEAT_RUN_CONSISTENCY_FAILED,
        "runtime_ordering_status": DETERMINISTIC_ORDERING_SATISFIED if "deterministic_ordering_failed" not in determinism_blockers else DETERMINISTIC_ORDERING_FAILED,
        "runtime_hashing_status": DETERMINISTIC_HASHING_SATISFIED if "deterministic_hashing_failed" not in determinism_blockers else DETERMINISTIC_HASHING_FAILED,
        "runtime_determinism_blocker_state": "blocked" if determinism_blockers else "unblocked_for_contract_only",
        "runtime_instability_blocker_state": "blocked" if instability_blockers else "unblocked_for_contract_only",
        "runtime_replay_blocker_state": "blocked" if replay_blockers else "unblocked_for_contract_only",
        "determinism_blockers": determinism_blockers,
        "instability_blockers": instability_blockers,
        "replay_blockers": replay_blockers,
        "repeat_run_hashes": deepcopy(request.get("repeat_run_hashes", [])),
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "runtime_determinism_validation_authorizes_runtime_consumption": False,
        "runtime_determinism_validation_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_determinism_validation_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_determinism_failures_allowed": False,
            "hidden_runtime_instability_allowed": False,
            "implicit_replay_consistency_approval_allowed": False,
            "fallback_determinism_validation_allowed": False,
        },
    }


def classify_runtime_determinism_state(runtime_determinism_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    """Classify runtime determinism state with explicit non-boolean categories."""

    blocker_set = set(blockers if blockers is not None else _determinism_blockers(runtime_determinism_request or {}, None, None, None, None, None))
    if "runtime_audit_compatibility_missing" in blocker_set:
        return RUNTIME_AUDIT_COMPATIBILITY_MISSING
    if "runtime_rollback_compatibility_missing" in blocker_set:
        return RUNTIME_ROLLBACK_COMPATIBILITY_MISSING
    if "runtime_session_compatibility_missing" in blocker_set:
        return RUNTIME_SESSION_COMPATIBILITY_MISSING
    if "runtime_isolation_compatibility_missing" in blocker_set:
        return RUNTIME_ISOLATION_COMPATIBILITY_MISSING
    if "runtime_entrypoint_compatibility_missing" in blocker_set:
        return RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING
    if "repeat_run_consistency_failed" in blocker_set:
        return REPEAT_RUN_CONSISTENCY_FAILED
    if "deterministic_ordering_failed" in blocker_set:
        return DETERMINISTIC_ORDERING_FAILED
    if "deterministic_hashing_failed" in blocker_set:
        return DETERMINISTIC_HASHING_FAILED
    if "runtime_nondeterministic_drift_detected" in blocker_set:
        return RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED
    if "runtime_instability_detected" in blocker_set:
        return RUNTIME_INSTABILITY_DETECTED
    if "runtime_transition_instability_detected" in blocker_set:
        return RUNTIME_TRANSITION_INSTABILITY_DETECTED
    if blocker_set:
        return RUNTIME_DETERMINISM_BLOCKED
    return RUNTIME_DETERMINISM_SATISFIED


def classify_runtime_replay_state(runtime_determinism_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    """Classify runtime replay consistency with explicit non-boolean categories."""

    blocker_set = set(blockers if blockers is not None else _replay_blockers(runtime_determinism_request or {}, None))
    if "runtime_audit_compatibility_missing" in blocker_set:
        return RUNTIME_AUDIT_COMPATIBILITY_MISSING
    if "runtime_replay_consistency_failed" in blocker_set:
        return RUNTIME_REPLAY_CONSISTENCY_FAILED
    if blocker_set:
        return RUNTIME_REPLAY_CONSISTENCY_FAILED
    return RUNTIME_REPLAY_CONSISTENCY_SATISFIED


def summarize_runtime_determinism_validation_contract(
    runtime_determinism_validation_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_6_runtime_determinism_validation_contracts",
    runtime_determinism_requests_hash: str | None = None,
    experimental_runtime_entrypoint_contracts_hash: str | None = None,
    runtime_isolation_contracts_hash: str | None = None,
    runtime_session_boundary_contracts_hash: str | None = None,
    runtime_safety_rollback_contracts_hash: str | None = None,
    runtime_diff_audit_contracts_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
    safety_rollback_count: int | None = None,
    diff_audit_count: int | None = None,
) -> dict[str, Any]:
    """Return a deterministic summary envelope for determinism contracts."""

    contracts = [deepcopy(record) for record in sorted(runtime_determinism_validation_contracts, key=_record_sort_key)]
    determinism_counts = Counter(record["runtime_determinism_status"] for record in contracts)
    replay_counts = Counter(record["runtime_replay_status"] for record in contracts)
    determinism_blockers = Counter(blocker for record in contracts for blocker in record["determinism_blockers"])
    instability_blockers = Counter(blocker for record in contracts for blocker in record["instability_blockers"])
    replay_blockers = Counter(blocker for record in contracts for blocker in record["replay_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_determinism_validation_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_determinism_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "runtime_isolation_contract_count": isolation_count,
            "runtime_session_boundary_contract_count": session_count,
            "runtime_safety_rollback_contract_count": safety_rollback_count,
            "runtime_diff_audit_contract_count": diff_audit_count,
            "runtime_determinism_requests_hash": runtime_determinism_requests_hash,
            "experimental_runtime_entrypoint_contracts_hash": experimental_runtime_entrypoint_contracts_hash,
            "runtime_isolation_contracts_hash": runtime_isolation_contracts_hash,
            "runtime_session_boundary_contracts_hash": runtime_session_boundary_contracts_hash,
            "runtime_safety_rollback_contracts_hash": runtime_safety_rollback_contracts_hash,
            "runtime_diff_audit_contracts_hash": runtime_diff_audit_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_determinism_satisfied_count": determinism_counts[RUNTIME_DETERMINISM_SATISFIED],
            "runtime_determinism_blocked_count": len(contracts) - determinism_counts[RUNTIME_DETERMINISM_SATISFIED],
            "runtime_replay_consistency_satisfied_count": replay_counts[RUNTIME_REPLAY_CONSISTENCY_SATISFIED],
            "runtime_replay_consistency_failed_count": replay_counts[RUNTIME_REPLAY_CONSISTENCY_FAILED],
            "repeat_run_consistency_failed_count": determinism_counts[REPEAT_RUN_CONSISTENCY_FAILED],
            "deterministic_ordering_failed_count": determinism_counts[DETERMINISTIC_ORDERING_FAILED],
            "deterministic_hashing_failed_count": determinism_counts[DETERMINISTIC_HASHING_FAILED],
            "runtime_nondeterministic_drift_detected_count": determinism_counts[RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED],
            "runtime_instability_detected_count": determinism_counts[RUNTIME_INSTABILITY_DETECTED],
            "runtime_transition_instability_detected_count": determinism_counts[RUNTIME_TRANSITION_INSTABILITY_DETECTED],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_determinism_status_counts": {status: determinism_counts[status] for status in RUNTIME_DETERMINISM_STATUSES},
        "runtime_replay_status_counts": {status: replay_counts[status] for status in RUNTIME_REPLAY_STATUSES},
        "repeat_run_consistency_distribution": _distribution(contracts, "runtime_repeat_run_state"),
        "deterministic_ordering_distribution": _distribution(contracts, "runtime_deterministic_ordering_state"),
        "deterministic_hashing_distribution": _distribution(contracts, "runtime_deterministic_hashing_state"),
        "replay_consistency_distribution": _distribution(contracts, "runtime_replay_consistency_state"),
        "runtime_nondeterministic_drift_distribution": _distribution(contracts, "runtime_nondeterministic_drift_state"),
        "runtime_instability_distribution": _distribution(contracts, "runtime_instability_classification"),
        "runtime_transition_instability_distribution": _distribution(contracts, "runtime_transition_consistency_state"),
        "runtime_audit_compatibility_distribution": _distribution(contracts, "runtime_diff_audit_status"),
        "runtime_rollback_compatibility_distribution": _distribution(contracts, "runtime_rollback_status"),
        "runtime_session_compatibility_distribution": _distribution(contracts, "runtime_session_boundary_status"),
        "runtime_isolation_compatibility_distribution": _distribution(contracts, "runtime_isolation_status"),
        "runtime_determinism_blocker_distribution": dict(sorted(determinism_blockers.items())),
        "runtime_instability_blocker_distribution": dict(sorted(instability_blockers.items())),
        "runtime_replay_blocker_distribution": dict(sorted(replay_blockers.items())),
        "phase_1_entrypoint_compatibility": {"entrypoint_contract_records": entrypoint_count, "requires_experimental_runtime_eligible": True, "production_runtime_prohibited": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "phase_2_isolation_compatibility": {"isolation_contract_records": isolation_count, "requires_runtime_isolation_satisfied": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "phase_3_session_compatibility": {"session_boundary_contract_records": session_count, "requires_session_boundary_satisfied": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "phase_4_rollback_compatibility": {"runtime_safety_rollback_contract_records": safety_rollback_count, "requires_runtime_safety_satisfied": True, "requires_runtime_rollback_ready": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "phase_5_audit_compatibility": {"runtime_diff_audit_contract_records": diff_audit_count, "requires_runtime_diff_audit_satisfied": True, "runtime_manifest_consumption_enabled": False, "production_routing_authorized": False},
        "runtime_disabled_path_verification": {"runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_runtime_prohibited": True, "production_routing_authorized": False, "silent_determinism_failures_allowed": False, "implicit_replay_consistency_approval_allowed": False, "fallback_determinism_validation_allowed": False},
        "runtime_determinism_validation_contracts": contracts,
        "safety_confirmations": {"runtime_determinism_validation_enables_runtime_manifest_consumption": False, "runtime_determinism_validation_authorizes_production_routing": False, "runtime_determinism_validation_allows_silent_failures": False, "runtime_determinism_validation_allows_hidden_instability": False, "production_runtime_routing_prohibited": True, "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "legacy_planner_ownership_preserved": True, "production_output_affected": False, "production_behavior_changed": False, "production_planner_routing_changed": False},
        "metadata": {"source": "v3_2_runtime_determinism_validation_contracts", "governance_only": True, "runtime_determinism_validation_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_consumer": False, "production_behavior_changed": False, "planner_remap_performed": False, "stable_generation_token": STABLE_RUNTIME_DETERMINISM_VALIDATION_TOKEN, "deterministic_serializer": "json_sort_keys_sha256"},
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _determinism_blockers(
    request: dict[str, Any],
    entrypoint: dict[str, Any] | None,
    isolation: dict[str, Any] | None,
    session: dict[str, Any] | None,
    safety: dict[str, Any] | None,
    diff: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    if entrypoint is None or entrypoint.get("runtime_entrypoint_status") != EXPERIMENTAL_RUNTIME_ELIGIBLE:
        blockers.append("runtime_entrypoint_compatibility_missing")
    if isolation is None or isolation.get("runtime_isolation_status") != RUNTIME_ISOLATION_SATISFIED:
        blockers.append("runtime_isolation_compatibility_missing")
    if session is None or session.get("runtime_session_boundary_status") != RUNTIME_SESSION_BOUNDARY_SATISFIED:
        blockers.append("runtime_session_compatibility_missing")
    if safety is None or safety.get("runtime_safety_status") != RUNTIME_SAFETY_SATISFIED or safety.get("runtime_rollback_status") != RUNTIME_ROLLBACK_READY:
        blockers.append("runtime_rollback_compatibility_missing")
    if diff is None or diff.get("runtime_diff_audit_status") != RUNTIME_DIFF_AUDIT_SATISFIED or diff.get("runtime_drift_status") != RUNTIME_DIFF_AUDIT_SATISFIED:
        blockers.append("runtime_audit_compatibility_missing")
    if request.get("runtime_repeat_run_state") != REPEAT_RUN_CONSISTENCY_SATISFIED:
        blockers.append("repeat_run_consistency_failed")
    if request.get("runtime_deterministic_ordering_state") != DETERMINISTIC_ORDERING_SATISFIED:
        blockers.append("deterministic_ordering_failed")
    if request.get("runtime_deterministic_hashing_state") != DETERMINISTIC_HASHING_SATISFIED:
        blockers.append("deterministic_hashing_failed")
    if request.get("runtime_nondeterministic_drift_state") == RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED:
        blockers.append("runtime_nondeterministic_drift_detected")
    if request.get("runtime_instability_classification") == RUNTIME_INSTABILITY_DETECTED:
        blockers.append("runtime_instability_detected")
    if request.get("runtime_transition_consistency_state") == RUNTIME_TRANSITION_INSTABILITY_DETECTED:
        blockers.append("runtime_transition_instability_detected")
    if not _repeat_hashes_stable(request.get("repeat_run_hashes", [])):
        blockers.append("deterministic_hashing_failed")
    return sorted(set(blockers), key=blockers.index)


def _instability_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if request.get("runtime_nondeterministic_drift_state") == RUNTIME_NONDETERMINISTIC_DRIFT_DETECTED:
        blockers.append("runtime_nondeterministic_drift_detected")
    if request.get("runtime_instability_classification") == RUNTIME_INSTABILITY_DETECTED:
        blockers.append("runtime_instability_detected")
    if request.get("runtime_transition_consistency_state") == RUNTIME_TRANSITION_INSTABILITY_DETECTED:
        blockers.append("runtime_transition_instability_detected")
    return sorted(set(blockers), key=blockers.index)


def _replay_blockers(request: dict[str, Any], diff: dict[str, Any] | None) -> list[str]:
    blockers: list[str] = []
    if diff is None or diff.get("runtime_diff_audit_status") != RUNTIME_DIFF_AUDIT_SATISFIED:
        blockers.append("runtime_audit_compatibility_missing")
    if request.get("runtime_replay_consistency_state") != RUNTIME_REPLAY_CONSISTENCY_SATISFIED:
        blockers.append("runtime_replay_consistency_failed")
    if request.get("runtime_replay_trace_classification") != "runtime_replay_trace_audited":
        blockers.append("runtime_replay_consistency_failed")
    return sorted(set(blockers), key=blockers.index)


def _repeat_hashes_stable(hashes: Any) -> bool:
    if not isinstance(hashes, list) or len(hashes) < 2:
        return False
    return len({str(item) for item in hashes}) == 1


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
