"""Runtime replayability contracts for v3.2 governance.

This layer validates replay input evidence, replay output evidence, hash
consistency, trace preservation, and lineage preservation across the v3.2
runtime governance chain. It is governance-only and does not enable runtime
manifest consumption or production routing.
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
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED
from app.planner_adapters.v3_2.runtime_traceability_contracts import RUNTIME_TRACEABILITY_SATISFIED


RUNTIME_REPLAYABILITY_SATISFIED = "runtime_replayability_satisfied"
RUNTIME_REPLAYABILITY_BLOCKED = "runtime_replayability_blocked"
RUNTIME_REPLAY_INPUT_MISSING = "runtime_replay_input_missing"
RUNTIME_REPLAY_OUTPUT_MISSING = "runtime_replay_output_missing"
RUNTIME_REPLAY_HASH_MISMATCH = "runtime_replay_hash_mismatch"
RUNTIME_REPLAY_TRACE_MISMATCH = "runtime_replay_trace_mismatch"
RUNTIME_REPLAY_LINEAGE_BROKEN = "runtime_replay_lineage_broken"
RUNTIME_REPLAY_DETERMINISM_FAILED = "runtime_replay_determinism_failed"
RUNTIME_REPLAY_EVIDENCE_INCOMPLETE = "runtime_replay_evidence_incomplete"
RUNTIME_REPLAY_OUTPUT_UNSTABLE = "runtime_replay_output_unstable"
RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING = "runtime_traceability_compatibility_missing"
RUNTIME_DETERMINISM_COMPATIBILITY_MISSING = "runtime_determinism_compatibility_missing"
RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING = "runtime_diff_audit_compatibility_missing"
RUNTIME_ROLLBACK_COMPATIBILITY_MISSING = "runtime_rollback_compatibility_missing"
RUNTIME_SESSION_COMPATIBILITY_MISSING = "runtime_session_compatibility_missing"
RUNTIME_ISOLATION_COMPATIBILITY_MISSING = "runtime_isolation_compatibility_missing"
RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING = "runtime_entrypoint_compatibility_missing"

RUNTIME_REPLAYABILITY_STATUSES = (
    RUNTIME_REPLAYABILITY_SATISFIED,
    RUNTIME_REPLAYABILITY_BLOCKED,
    RUNTIME_REPLAY_INPUT_MISSING,
    RUNTIME_REPLAY_OUTPUT_MISSING,
    RUNTIME_REPLAY_HASH_MISMATCH,
    RUNTIME_REPLAY_TRACE_MISMATCH,
    RUNTIME_REPLAY_LINEAGE_BROKEN,
    RUNTIME_REPLAY_DETERMINISM_FAILED,
    RUNTIME_REPLAY_EVIDENCE_INCOMPLETE,
    RUNTIME_REPLAY_OUTPUT_UNSTABLE,
    RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING,
    RUNTIME_DETERMINISM_COMPATIBILITY_MISSING,
    RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING,
    RUNTIME_ROLLBACK_COMPATIBILITY_MISSING,
    RUNTIME_SESSION_COMPATIBILITY_MISSING,
    RUNTIME_ISOLATION_COMPATIBILITY_MISSING,
    RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING,
)
RUNTIME_REPLAY_MISMATCH_STATUSES = (
    RUNTIME_REPLAYABILITY_SATISFIED,
    RUNTIME_REPLAY_HASH_MISMATCH,
    RUNTIME_REPLAY_TRACE_MISMATCH,
    RUNTIME_REPLAY_LINEAGE_BROKEN,
    RUNTIME_REPLAY_OUTPUT_UNSTABLE,
)
STABLE_RUNTIME_REPLAYABILITY_TOKEN = "v3_2_phase_8_runtime_replayability_contracts_token"


def build_runtime_replayability_contract(
    runtime_replayability_requests: dict[str, Any] | list[dict[str, Any]],
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_diff_audit_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_determinism_validation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_traceability_contracts: dict[str, Any] | list[dict[str, Any]],
    run_id: str = "v3_2_phase_8_runtime_replayability_contracts",
) -> dict[str, Any]:
    """Build deterministic runtime replayability contracts."""

    requests = _records(runtime_replayability_requests, "runtime_replayability_requests")
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    determinism_records = _records(runtime_determinism_validation_contracts, "runtime_determinism_validation_contracts")
    traceability_records = _records(runtime_traceability_contracts, "runtime_traceability_contracts")
    by_key = {
        "entrypoint": {_trace_key(record): record for record in entrypoints if _trace_key(record)},
        "isolation": {_trace_key(record): record for record in isolations if _trace_key(record)},
        "session": {_trace_key(record): record for record in sessions if _trace_key(record)},
        "safety": {_trace_key(record): record for record in safety_records if _trace_key(record)},
        "diff": {_trace_key(record): record for record in diff_records if _trace_key(record)},
        "determinism": {_trace_key(record): record for record in determinism_records if _trace_key(record)},
        "traceability": {_trace_key(record): record for record in traceability_records if _trace_key(record)},
    }
    contracts = [
        evaluate_runtime_replayability_contract(
            request,
            entrypoint_contract=by_key["entrypoint"].get(_trace_key(request)),
            isolation_contract=by_key["isolation"].get(_trace_key(request)),
            session_boundary_contract=by_key["session"].get(_trace_key(request)),
            safety_rollback_contract=by_key["safety"].get(_trace_key(request)),
            diff_audit_contract=by_key["diff"].get(_trace_key(request)),
            determinism_validation_contract=by_key["determinism"].get(_trace_key(request)),
            traceability_contract=by_key["traceability"].get(_trace_key(request)),
        )
        for request in sorted(requests, key=_record_sort_key)
    ]
    if not contracts:
        contracts = [
            evaluate_runtime_replayability_contract(
                {},
                entrypoint_contract=None,
                isolation_contract=None,
                session_boundary_contract=None,
                safety_rollback_contract=None,
                diff_audit_contract=None,
                determinism_validation_contract=None,
                traceability_contract=None,
            )
        ]
    return summarize_runtime_replayability_contract(
        contracts,
        run_id=run_id,
        runtime_replayability_requests_hash=_source_hash(runtime_replayability_requests),
        experimental_runtime_entrypoint_contracts_hash=_source_hash(experimental_runtime_entrypoint_contracts),
        runtime_isolation_contracts_hash=_source_hash(runtime_isolation_contracts),
        runtime_session_boundary_contracts_hash=_source_hash(runtime_session_boundary_contracts),
        runtime_safety_rollback_contracts_hash=_source_hash(runtime_safety_rollback_contracts),
        runtime_diff_audit_contracts_hash=_source_hash(runtime_diff_audit_contracts),
        runtime_determinism_validation_contracts_hash=_source_hash(runtime_determinism_validation_contracts),
        runtime_traceability_contracts_hash=_source_hash(runtime_traceability_contracts),
        request_count=len(requests),
        entrypoint_count=len(entrypoints),
        isolation_count=len(isolations),
        session_count=len(sessions),
        safety_rollback_count=len(safety_records),
        diff_audit_count=len(diff_records),
        determinism_count=len(determinism_records),
        traceability_count=len(traceability_records),
    )


def evaluate_runtime_replayability_contract(
    runtime_replayability_request: dict[str, Any],
    *,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
    safety_rollback_contract: dict[str, Any] | None,
    diff_audit_contract: dict[str, Any] | None,
    determinism_validation_contract: dict[str, Any] | None,
    traceability_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one replayability request against the governance chain."""

    request = deepcopy(runtime_replayability_request)
    entrypoint = deepcopy(entrypoint_contract) if entrypoint_contract else None
    isolation = deepcopy(isolation_contract) if isolation_contract else None
    session = deepcopy(session_boundary_contract) if session_boundary_contract else None
    safety = deepcopy(safety_rollback_contract) if safety_rollback_contract else None
    diff = deepcopy(diff_audit_contract) if diff_audit_contract else None
    determinism = deepcopy(determinism_validation_contract) if determinism_validation_contract else None
    traceability = deepcopy(traceability_contract) if traceability_contract else None
    replay_blockers = _replay_blockers(request, entrypoint, isolation, session, safety, diff, determinism, traceability)
    instability_blockers = _instability_blockers(request)
    replayability_status = classify_runtime_replayability_state(request, blockers=replay_blockers + instability_blockers)
    mismatch_status = classify_runtime_replay_mismatch_state(request, blockers=instability_blockers)
    manifest_id = request.get("manifest_id") or (traceability or {}).get("manifest_id") or (determinism or {}).get("manifest_id")
    fixture_set_id = request.get("fixture_set_id") or (traceability or {}).get("fixture_set_id") or (determinism or {}).get("fixture_set_id")
    seed = {"manifest_id": manifest_id, "fixture_set_id": fixture_set_id, "status": replayability_status, "mismatch": mismatch_status, "token": STABLE_RUNTIME_REPLAYABILITY_TOKEN}
    return {
        "runtime_replayability_contract_id": f"v3_2_runtime_replayability_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "runtime_replay_input_state": request.get("runtime_replay_input_state"),
        "runtime_replay_output_state": request.get("runtime_replay_output_state"),
        "runtime_replay_hash_state": request.get("runtime_replay_hash_state"),
        "runtime_replay_trace_state": request.get("runtime_replay_trace_state"),
        "runtime_replay_lineage_preservation_state": request.get("runtime_replay_lineage_preservation_state"),
        "runtime_replay_determinism_state": request.get("runtime_replay_determinism_state"),
        "runtime_replay_mismatch_state": request.get("runtime_replay_mismatch_state"),
        "runtime_replay_evidence_completeness_state": request.get("runtime_replay_evidence_completeness_state"),
        "runtime_replay_output_stability_state": request.get("runtime_replay_output_stability_state"),
        "entrypoint_contract_status": (entrypoint or {}).get("runtime_entrypoint_status"),
        "isolation_contract_status": (isolation or {}).get("runtime_isolation_status"),
        "session_boundary_contract_status": (session or {}).get("runtime_session_boundary_status"),
        "safety_contract_status": (safety or {}).get("runtime_safety_status"),
        "rollback_contract_status": (safety or {}).get("runtime_rollback_status"),
        "diff_audit_contract_status": (diff or {}).get("runtime_diff_audit_status"),
        "determinism_contract_status": (determinism or {}).get("runtime_determinism_status"),
        "traceability_contract_status": (traceability or {}).get("runtime_traceability_status"),
        "runtime_replayability_status": replayability_status,
        "runtime_replay_mismatch_status": mismatch_status,
        "runtime_replay_blocker_state": "blocked" if replay_blockers else "unblocked_for_contract_only",
        "runtime_replay_instability_blocker_state": "blocked" if instability_blockers else "unblocked_for_contract_only",
        "replay_blockers": replay_blockers,
        "replay_instability_blockers": instability_blockers,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "runtime_replayability_authorizes_runtime_consumption": False,
        "runtime_replayability_authorizes_production_routing": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "runtime_replayability_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_replay_failures_allowed": False,
            "implicit_replay_approval_allowed": False,
            "fallback_replayability_allowed": False,
        },
    }


def classify_runtime_replayability_state(runtime_replayability_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _replay_blockers(runtime_replayability_request or {}, None, None, None, None, None, None, None))
    for blocker, status in _STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    if blocker_set:
        return RUNTIME_REPLAYABILITY_BLOCKED
    return RUNTIME_REPLAYABILITY_SATISFIED


def classify_runtime_replay_mismatch_state(runtime_replayability_request: dict[str, Any], *, blockers: list[str] | None = None) -> str:
    blocker_set = set(blockers if blockers is not None else _instability_blockers(runtime_replayability_request or {}))
    for blocker, status in _MISMATCH_STATUS_PRIORITY:
        if blocker in blocker_set:
            return status
    if blocker_set:
        return RUNTIME_REPLAYABILITY_BLOCKED
    return RUNTIME_REPLAYABILITY_SATISFIED


def summarize_runtime_replayability_contract(
    runtime_replayability_contracts: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_8_runtime_replayability_contracts",
    runtime_replayability_requests_hash: str | None = None,
    experimental_runtime_entrypoint_contracts_hash: str | None = None,
    runtime_isolation_contracts_hash: str | None = None,
    runtime_session_boundary_contracts_hash: str | None = None,
    runtime_safety_rollback_contracts_hash: str | None = None,
    runtime_diff_audit_contracts_hash: str | None = None,
    runtime_determinism_validation_contracts_hash: str | None = None,
    runtime_traceability_contracts_hash: str | None = None,
    request_count: int | None = None,
    entrypoint_count: int | None = None,
    isolation_count: int | None = None,
    session_count: int | None = None,
    safety_rollback_count: int | None = None,
    diff_audit_count: int | None = None,
    determinism_count: int | None = None,
    traceability_count: int | None = None,
) -> dict[str, Any]:
    contracts = [deepcopy(record) for record in sorted(runtime_replayability_contracts, key=_record_sort_key)]
    replay_counts = Counter(record["runtime_replayability_status"] for record in contracts)
    mismatch_counts = Counter(record["runtime_replay_mismatch_status"] for record in contracts)
    replay_blockers = Counter(blocker for record in contracts for blocker in record["replay_blockers"])
    instability_blockers = Counter(blocker for record in contracts for blocker in record["replay_instability_blockers"])
    envelope = {
        "schema_version": "v3_2.runtime_replayability_contracts.1",
        "run": {
            "run_id": run_id,
            "runtime_replayability_request_count": len(contracts) if request_count is None else request_count,
            "entrypoint_contract_count": entrypoint_count,
            "runtime_isolation_contract_count": isolation_count,
            "runtime_session_boundary_contract_count": session_count,
            "runtime_safety_rollback_contract_count": safety_rollback_count,
            "runtime_diff_audit_contract_count": diff_audit_count,
            "runtime_determinism_validation_contract_count": determinism_count,
            "runtime_traceability_contract_count": traceability_count,
            "runtime_replayability_requests_hash": runtime_replayability_requests_hash,
            "experimental_runtime_entrypoint_contracts_hash": experimental_runtime_entrypoint_contracts_hash,
            "runtime_isolation_contracts_hash": runtime_isolation_contracts_hash,
            "runtime_session_boundary_contracts_hash": runtime_session_boundary_contracts_hash,
            "runtime_safety_rollback_contracts_hash": runtime_safety_rollback_contracts_hash,
            "runtime_diff_audit_contracts_hash": runtime_diff_audit_contracts_hash,
            "runtime_determinism_validation_contracts_hash": runtime_determinism_validation_contracts_hash,
            "runtime_traceability_contracts_hash": runtime_traceability_contracts_hash,
        },
        "summary": {
            "records_evaluated": len(contracts),
            "runtime_replayability_satisfied_count": replay_counts[RUNTIME_REPLAYABILITY_SATISFIED],
            "runtime_replayability_blocked_count": len(contracts) - replay_counts[RUNTIME_REPLAYABILITY_SATISFIED],
            "runtime_replay_hash_mismatch_count": replay_counts[RUNTIME_REPLAY_HASH_MISMATCH] + mismatch_counts[RUNTIME_REPLAY_HASH_MISMATCH],
            "runtime_replay_trace_mismatch_count": replay_counts[RUNTIME_REPLAY_TRACE_MISMATCH] + mismatch_counts[RUNTIME_REPLAY_TRACE_MISMATCH],
            "runtime_replay_output_unstable_count": replay_counts[RUNTIME_REPLAY_OUTPUT_UNSTABLE] + mismatch_counts[RUNTIME_REPLAY_OUTPUT_UNSTABLE],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "runtime_replayability_status_counts": {status: replay_counts[status] for status in RUNTIME_REPLAYABILITY_STATUSES},
        "runtime_replay_mismatch_status_counts": {status: mismatch_counts[status] for status in RUNTIME_REPLAY_MISMATCH_STATUSES},
        "replay_input_distribution": _distribution(contracts, "runtime_replay_input_state"),
        "replay_output_distribution": _distribution(contracts, "runtime_replay_output_state"),
        "replay_hash_consistency_distribution": _distribution(contracts, "runtime_replay_hash_state"),
        "replay_trace_consistency_distribution": _distribution(contracts, "runtime_replay_trace_state"),
        "replay_lineage_preservation_distribution": _distribution(contracts, "runtime_replay_lineage_preservation_state"),
        "replay_determinism_distribution": _distribution(contracts, "runtime_replay_determinism_state"),
        "replay_mismatch_distribution": _distribution(contracts, "runtime_replay_mismatch_state"),
        "replay_evidence_completeness_distribution": _distribution(contracts, "runtime_replay_evidence_completeness_state"),
        "replay_instability_distribution": _distribution(contracts, "runtime_replay_output_stability_state"),
        "traceability_compatibility_distribution": _distribution(contracts, "traceability_contract_status"),
        "determinism_compatibility_distribution": _distribution(contracts, "determinism_contract_status"),
        "diff_audit_compatibility_distribution": _distribution(contracts, "diff_audit_contract_status"),
        "rollback_compatibility_distribution": _distribution(contracts, "rollback_contract_status"),
        "session_compatibility_distribution": _distribution(contracts, "session_boundary_contract_status"),
        "isolation_compatibility_distribution": _distribution(contracts, "isolation_contract_status"),
        "entrypoint_compatibility_distribution": _distribution(contracts, "entrypoint_contract_status"),
        "runtime_replay_blocker_distribution": dict(sorted(replay_blockers.items())),
        "runtime_replay_instability_blocker_distribution": dict(sorted(instability_blockers.items())),
        "runtime_disabled_path_verification": {"runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "production_runtime_prohibited": True, "production_routing_authorized": False, "silent_replay_failures_allowed": False, "implicit_replay_approval_allowed": False, "fallback_replayability_allowed": False},
        "runtime_replayability_contracts": contracts,
        "safety_confirmations": {"runtime_replayability_enables_runtime_manifest_consumption": False, "runtime_replayability_authorizes_production_routing": False, "runtime_replayability_allows_silent_failures": False, "production_runtime_routing_prohibited": True, "runtime_manifest_consumption_enabled": False, "runtime_production_consumption_enabled": False, "legacy_planner_ownership_preserved": True, "production_output_affected": False, "production_behavior_changed": False, "production_planner_routing_changed": False},
        "metadata": {"source": "v3_2_runtime_replayability_contracts", "governance_only": True, "runtime_replayability_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_consumer": False, "production_behavior_changed": False, "planner_remap_performed": False, "stable_generation_token": STABLE_RUNTIME_REPLAYABILITY_TOKEN, "deterministic_serializer": "json_sort_keys_sha256"},
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


_STATUS_PRIORITY = (
    ("runtime_entrypoint_compatibility_missing", RUNTIME_ENTRYPOINT_COMPATIBILITY_MISSING),
    ("runtime_isolation_compatibility_missing", RUNTIME_ISOLATION_COMPATIBILITY_MISSING),
    ("runtime_session_compatibility_missing", RUNTIME_SESSION_COMPATIBILITY_MISSING),
    ("runtime_rollback_compatibility_missing", RUNTIME_ROLLBACK_COMPATIBILITY_MISSING),
    ("runtime_diff_audit_compatibility_missing", RUNTIME_DIFF_AUDIT_COMPATIBILITY_MISSING),
    ("runtime_determinism_compatibility_missing", RUNTIME_DETERMINISM_COMPATIBILITY_MISSING),
    ("runtime_traceability_compatibility_missing", RUNTIME_TRACEABILITY_COMPATIBILITY_MISSING),
    ("runtime_replay_input_missing", RUNTIME_REPLAY_INPUT_MISSING),
    ("runtime_replay_output_missing", RUNTIME_REPLAY_OUTPUT_MISSING),
    ("runtime_replay_evidence_incomplete", RUNTIME_REPLAY_EVIDENCE_INCOMPLETE),
    ("runtime_replay_hash_mismatch", RUNTIME_REPLAY_HASH_MISMATCH),
    ("runtime_replay_trace_mismatch", RUNTIME_REPLAY_TRACE_MISMATCH),
    ("runtime_replay_lineage_broken", RUNTIME_REPLAY_LINEAGE_BROKEN),
    ("runtime_replay_determinism_failed", RUNTIME_REPLAY_DETERMINISM_FAILED),
    ("runtime_replay_output_unstable", RUNTIME_REPLAY_OUTPUT_UNSTABLE),
)
_MISMATCH_STATUS_PRIORITY = _STATUS_PRIORITY[10:]


def _replay_blockers(request: dict[str, Any], entrypoint: dict[str, Any] | None, isolation: dict[str, Any] | None, session: dict[str, Any] | None, safety: dict[str, Any] | None, diff: dict[str, Any] | None, determinism: dict[str, Any] | None, traceability: dict[str, Any] | None) -> list[str]:
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
        blockers.append("runtime_diff_audit_compatibility_missing")
    if determinism is None or determinism.get("runtime_determinism_status") != RUNTIME_DETERMINISM_SATISFIED:
        blockers.append("runtime_determinism_compatibility_missing")
    if traceability is None or traceability.get("runtime_traceability_status") != RUNTIME_TRACEABILITY_SATISFIED:
        blockers.append("runtime_traceability_compatibility_missing")
    if request.get("runtime_replay_input_state") != "runtime_replay_input_present":
        blockers.append("runtime_replay_input_missing")
    if request.get("runtime_replay_output_state") != "runtime_replay_output_present":
        blockers.append("runtime_replay_output_missing")
    if request.get("runtime_replay_evidence_completeness_state") != "runtime_replay_evidence_complete":
        blockers.append("runtime_replay_evidence_incomplete")
    if request.get("runtime_replay_determinism_state") != "runtime_replay_determinism_satisfied":
        blockers.append("runtime_replay_determinism_failed")
    return sorted(set(blockers), key=blockers.index)


def _instability_blockers(request: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if request.get("runtime_replay_hash_state") != "runtime_replay_hash_consistent":
        blockers.append("runtime_replay_hash_mismatch")
    if request.get("runtime_replay_trace_state") != "runtime_replay_trace_consistent":
        blockers.append("runtime_replay_trace_mismatch")
    if request.get("runtime_replay_lineage_preservation_state") != "runtime_replay_lineage_preserved":
        blockers.append("runtime_replay_lineage_broken")
    if request.get("runtime_replay_mismatch_state") == RUNTIME_REPLAY_HASH_MISMATCH:
        blockers.append("runtime_replay_hash_mismatch")
    if request.get("runtime_replay_mismatch_state") == RUNTIME_REPLAY_TRACE_MISMATCH:
        blockers.append("runtime_replay_trace_mismatch")
    if request.get("runtime_replay_output_stability_state") != "runtime_replay_output_stable":
        blockers.append("runtime_replay_output_unstable")
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
