"""Experimental runtime closeout and v3.3 readiness audit for v3.2.

This module summarizes the v3.2 limited experimental runtime governance chain
from Phase 1 through Phase 11. It is audit-only and does not enable runtime
manifest consumption, production routing, or production-authoritative manifests.
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
from app.planner_adapters.v3_2.limited_runtime_consumption_experiment_contracts import LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE
from app.planner_adapters.v3_2.runtime_determinism_validation_contracts import RUNTIME_DETERMINISM_SATISFIED
from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import RUNTIME_DIFF_AUDIT_SATISFIED
from app.planner_adapters.v3_2.runtime_drift_detection_contracts import (
    RUNTIME_DRIFT_DETECTION_SATISFIED,
    RUNTIME_DRIFT_NOT_DETECTED,
)
from app.planner_adapters.v3_2.runtime_isolation_contracts import RUNTIME_ISOLATION_SATISFIED
from app.planner_adapters.v3_2.runtime_kill_switch_contracts import RUNTIME_KILL_SWITCH_SATISFIED
from app.planner_adapters.v3_2.runtime_replayability_contracts import RUNTIME_REPLAYABILITY_SATISFIED
from app.planner_adapters.v3_2.runtime_safety_rollback_contracts import (
    RUNTIME_ROLLBACK_READY,
    RUNTIME_SAFETY_SATISFIED,
)
from app.planner_adapters.v3_2.runtime_session_boundary_contracts import RUNTIME_SESSION_BOUNDARY_SATISFIED
from app.planner_adapters.v3_2.runtime_traceability_contracts import RUNTIME_TRACEABILITY_SATISFIED


V3_2_CLOSEOUT_SATISFIED = "v3_2_closeout_satisfied"
V3_2_CLOSEOUT_BLOCKED = "v3_2_closeout_blocked"
V3_2_PHASE_COVERAGE_COMPLETE = "v3_2_phase_coverage_complete"
V3_2_PHASE_COVERAGE_INCOMPLETE = "v3_2_phase_coverage_incomplete"
V3_2_CONTRACTS_COMPATIBLE = "v3_2_contracts_compatible"
V3_2_CONTRACTS_INCOMPATIBLE = "v3_2_contracts_incompatible"
V3_3_READY_FOR_PLANNING = "v3_3_ready_for_planning"
V3_3_BLOCKED = "v3_3_blocked"
V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY = "v3_3_limited_experimental_continuation_only"
PRODUCTION_RUNTIME_STILL_PROHIBITED = "production_runtime_still_prohibited"
DEFAULT_RUNTIME_MANIFEST_CONSUMPTION_STILL_DISABLED = "default_runtime_manifest_consumption_still_disabled"
PRODUCTION_AUTHORITATIVE_MANIFEST_TREATMENT_STILL_PROHIBITED = (
    "production_authoritative_manifest_treatment_still_prohibited"
)
UNRESOLVED_BLOCKERS_PRESENT = "unresolved_blockers_present"
UNRESOLVED_RISKS_PRESENT = "unresolved_risks_present"
UNRESOLVED_LIMITATIONS_PRESENT = "unresolved_limitations_present"

V3_2_CLOSEOUT_STATUSES = (V3_2_CLOSEOUT_SATISFIED, V3_2_CLOSEOUT_BLOCKED)
V3_2_PHASE_COVERAGE_STATUSES = (V3_2_PHASE_COVERAGE_COMPLETE, V3_2_PHASE_COVERAGE_INCOMPLETE)
V3_2_CONTRACT_COMPATIBILITY_STATUSES = (V3_2_CONTRACTS_COMPATIBLE, V3_2_CONTRACTS_INCOMPATIBLE)
V3_3_READINESS_STATUSES = (
    V3_3_READY_FOR_PLANNING,
    V3_3_BLOCKED,
    V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY,
)
STABLE_CLOSEOUT_TOKEN = "v3_2_phase_12_experimental_runtime_closeout_readiness_audit_token"


def build_experimental_runtime_closeout_readiness_audit(
    *,
    experimental_runtime_entrypoint_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_isolation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_session_boundary_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_safety_rollback_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_diff_audit_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_determinism_validation_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_traceability_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_replayability_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_drift_detection_contracts: dict[str, Any] | list[dict[str, Any]],
    limited_runtime_experiment_contracts: dict[str, Any] | list[dict[str, Any]],
    runtime_kill_switch_contracts: dict[str, Any] | list[dict[str, Any]],
    closeout_context: dict[str, Any] | None = None,
    run_id: str = "v3_2_phase_12_experimental_runtime_closeout_readiness_audit",
) -> dict[str, Any]:
    entrypoints = _records(experimental_runtime_entrypoint_contracts, "runtime_entrypoint_contracts")
    isolations = _records(runtime_isolation_contracts, "runtime_isolation_contracts")
    sessions = _records(runtime_session_boundary_contracts, "runtime_session_boundary_contracts")
    safety_records = _records(runtime_safety_rollback_contracts, "runtime_safety_rollback_contracts")
    diff_records = _records(runtime_diff_audit_contracts, "runtime_diff_audit_contracts")
    determinism_records = _records(runtime_determinism_validation_contracts, "runtime_determinism_validation_contracts")
    traceability_records = _records(runtime_traceability_contracts, "runtime_traceability_contracts")
    replayability_records = _records(runtime_replayability_contracts, "runtime_replayability_contracts")
    drift_records = _records(runtime_drift_detection_contracts, "runtime_drift_detection_contracts")
    experiment_records = _records(limited_runtime_experiment_contracts, "limited_runtime_experiment_contracts")
    kill_switch_records = _records(runtime_kill_switch_contracts, "runtime_kill_switch_contracts")
    maps = {
        "entrypoint": _by_key(entrypoints),
        "isolation": _by_key(isolations),
        "session": _by_key(sessions),
        "safety": _by_key(safety_records),
        "diff": _by_key(diff_records),
        "determinism": _by_key(determinism_records),
        "traceability": _by_key(traceability_records),
        "replayability": _by_key(replayability_records),
        "drift": _by_key(drift_records),
        "experiment": _by_key(experiment_records),
        "kill_switch": _by_key(kill_switch_records),
    }
    keys = sorted(set().union(*(set(mapping) for mapping in maps.values())), key=lambda item: (item[1], item[0]))
    if not keys:
        keys = [(None, None)]
    records = [
        evaluate_experimental_runtime_closeout_readiness_audit(
            manifest_id=manifest_id,
            fixture_set_id=fixture_set_id,
            entrypoint_contract=maps["entrypoint"].get((manifest_id, fixture_set_id)),
            isolation_contract=maps["isolation"].get((manifest_id, fixture_set_id)),
            session_boundary_contract=maps["session"].get((manifest_id, fixture_set_id)),
            safety_rollback_contract=maps["safety"].get((manifest_id, fixture_set_id)),
            diff_audit_contract=maps["diff"].get((manifest_id, fixture_set_id)),
            determinism_validation_contract=maps["determinism"].get((manifest_id, fixture_set_id)),
            traceability_contract=maps["traceability"].get((manifest_id, fixture_set_id)),
            replayability_contract=maps["replayability"].get((manifest_id, fixture_set_id)),
            drift_detection_contract=maps["drift"].get((manifest_id, fixture_set_id)),
            limited_runtime_experiment_contract=maps["experiment"].get((manifest_id, fixture_set_id)),
            runtime_kill_switch_contract=maps["kill_switch"].get((manifest_id, fixture_set_id)),
            closeout_context=closeout_context,
        )
        for manifest_id, fixture_set_id in keys
    ]
    return summarize_experimental_runtime_closeout_readiness_audit(
        records,
        run_id=run_id,
        phase_counts={
            "phase_1_entrypoint_count": len(entrypoints),
            "phase_2_isolation_count": len(isolations),
            "phase_3_session_boundary_count": len(sessions),
            "phase_4_safety_rollback_count": len(safety_records),
            "phase_5_diff_audit_count": len(diff_records),
            "phase_6_determinism_count": len(determinism_records),
            "phase_7_traceability_count": len(traceability_records),
            "phase_8_replayability_count": len(replayability_records),
            "phase_9_drift_detection_count": len(drift_records),
            "phase_10_limited_experiment_count": len(experiment_records),
            "phase_11_kill_switch_count": len(kill_switch_records),
        },
        source_hashes={
            "entrypoint_hash": _source_hash(experimental_runtime_entrypoint_contracts),
            "isolation_hash": _source_hash(runtime_isolation_contracts),
            "session_hash": _source_hash(runtime_session_boundary_contracts),
            "safety_rollback_hash": _source_hash(runtime_safety_rollback_contracts),
            "diff_audit_hash": _source_hash(runtime_diff_audit_contracts),
            "determinism_hash": _source_hash(runtime_determinism_validation_contracts),
            "traceability_hash": _source_hash(runtime_traceability_contracts),
            "replayability_hash": _source_hash(runtime_replayability_contracts),
            "drift_detection_hash": _source_hash(runtime_drift_detection_contracts),
            "limited_experiment_hash": _source_hash(limited_runtime_experiment_contracts),
            "kill_switch_hash": _source_hash(runtime_kill_switch_contracts),
        },
    )


def evaluate_experimental_runtime_closeout_readiness_audit(
    *,
    manifest_id: str | None,
    fixture_set_id: str | None,
    entrypoint_contract: dict[str, Any] | None,
    isolation_contract: dict[str, Any] | None,
    session_boundary_contract: dict[str, Any] | None,
    safety_rollback_contract: dict[str, Any] | None,
    diff_audit_contract: dict[str, Any] | None,
    determinism_validation_contract: dict[str, Any] | None,
    traceability_contract: dict[str, Any] | None,
    replayability_contract: dict[str, Any] | None,
    drift_detection_contract: dict[str, Any] | None,
    limited_runtime_experiment_contract: dict[str, Any] | None,
    runtime_kill_switch_contract: dict[str, Any] | None,
    closeout_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = deepcopy(closeout_context or {})
    phase_statuses = {
        "phase_1_entrypoint": (entrypoint_contract or {}).get("runtime_entrypoint_status"),
        "phase_2_isolation": (isolation_contract or {}).get("runtime_isolation_status"),
        "phase_3_session_boundary": (session_boundary_contract or {}).get("runtime_session_boundary_status"),
        "phase_4_safety": (safety_rollback_contract or {}).get("runtime_safety_status"),
        "phase_4_rollback": (safety_rollback_contract or {}).get("runtime_rollback_status"),
        "phase_5_diff_audit": (diff_audit_contract or {}).get("runtime_diff_audit_status"),
        "phase_6_determinism": (determinism_validation_contract or {}).get("runtime_determinism_status"),
        "phase_7_traceability": (traceability_contract or {}).get("runtime_traceability_status"),
        "phase_8_replayability": (replayability_contract or {}).get("runtime_replayability_status"),
        "phase_9_drift_detection": (drift_detection_contract or {}).get("runtime_drift_detection_status"),
        "phase_10_limited_experiment": (limited_runtime_experiment_contract or {}).get("limited_runtime_experiment_status"),
        "phase_11_kill_switch": (runtime_kill_switch_contract or {}).get("runtime_kill_switch_status"),
    }
    blockers = _closeout_blockers(
        phase_statuses,
        entrypoint_contract,
        isolation_contract,
        session_boundary_contract,
        safety_rollback_contract,
        diff_audit_contract,
        determinism_validation_contract,
        traceability_contract,
        replayability_contract,
        drift_detection_contract,
        limited_runtime_experiment_contract,
        runtime_kill_switch_contract,
    )
    unresolved_blockers = sorted(set(blockers + list(context.get("unresolved_blockers", []))))
    unresolved_risks = sorted(set(context.get("unresolved_risks", [])))
    unresolved_limitations = sorted(
        set(
            context.get(
                "unresolved_limitations",
                [
                    "v3.3 readiness is planning-only",
                    "production runtime routing remains out of scope",
                    "default runtime manifest consumption remains disabled",
                    "production-authoritative manifest treatment remains prohibited",
                ],
            )
        )
    )
    phase_coverage_state = (
        V3_2_PHASE_COVERAGE_COMPLETE
        if all(value is not None for value in phase_statuses.values())
        else V3_2_PHASE_COVERAGE_INCOMPLETE
    )
    contract_compatibility_state = V3_2_CONTRACTS_COMPATIBLE if not blockers else V3_2_CONTRACTS_INCOMPATIBLE
    closeout_status = classify_v3_2_closeout_state(
        phase_coverage_state=phase_coverage_state,
        contract_compatibility_state=contract_compatibility_state,
        unresolved_blockers=unresolved_blockers,
    )
    readiness_status = classify_v3_3_readiness_state(
        closeout_status=closeout_status,
        unresolved_risks=unresolved_risks,
    )
    seed = {
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "closeout_status": closeout_status,
        "readiness_status": readiness_status,
        "token": STABLE_CLOSEOUT_TOKEN,
    }
    return {
        "experimental_runtime_closeout_audit_id": f"v3_2_closeout_{deterministic_hash(seed)[:16]}",
        "manifest_id": manifest_id,
        "fixture_set_id": fixture_set_id,
        "evidence_chain_statuses": phase_statuses,
        "phase_coverage_state": phase_coverage_state,
        "contract_compatibility_state": contract_compatibility_state,
        "entrypoint_readiness_state": phase_statuses["phase_1_entrypoint"],
        "isolation_readiness_state": phase_statuses["phase_2_isolation"],
        "session_boundary_readiness_state": phase_statuses["phase_3_session_boundary"],
        "safety_rollback_readiness_state": phase_statuses["phase_4_rollback"],
        "diff_audit_readiness_state": phase_statuses["phase_5_diff_audit"],
        "determinism_readiness_state": phase_statuses["phase_6_determinism"],
        "traceability_readiness_state": phase_statuses["phase_7_traceability"],
        "replayability_readiness_state": phase_statuses["phase_8_replayability"],
        "drift_detection_readiness_state": phase_statuses["phase_9_drift_detection"],
        "limited_experiment_readiness_state": phase_statuses["phase_10_limited_experiment"],
        "kill_switch_readiness_state": phase_statuses["phase_11_kill_switch"],
        "production_routing_prohibition_state": PRODUCTION_RUNTIME_STILL_PROHIBITED,
        "default_manifest_consumption_disabled_state": DEFAULT_RUNTIME_MANIFEST_CONSUMPTION_STILL_DISABLED,
        "production_authoritative_manifest_prohibition_state": PRODUCTION_AUTHORITATIVE_MANIFEST_TREATMENT_STILL_PROHIBITED,
        "unresolved_blocker_state": UNRESOLVED_BLOCKERS_PRESENT if unresolved_blockers else "no_unresolved_blockers",
        "unresolved_risk_state": UNRESOLVED_RISKS_PRESENT if unresolved_risks else "no_unresolved_risks",
        "unresolved_limitation_state": UNRESOLVED_LIMITATIONS_PRESENT if unresolved_limitations else "no_unresolved_limitations",
        "unresolved_blockers": unresolved_blockers,
        "unresolved_risks": unresolved_risks,
        "unresolved_limitations": unresolved_limitations,
        "v3_2_closeout_status": closeout_status,
        "v3_3_readiness_status": readiness_status,
        "closeout_trace_classification": "planning_only_runtime_governance_closeout",
        "runtime_manifest_consumption_enabled": False,
        "runtime_manifest_consumption_enabled_by_default": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_runtime_classification": PRODUCTION_RUNTIME_PROHIBITED,
        "production_authoritative_manifest_treatment": False,
        "v3_3_readiness_authorizes_production_enablement": False,
        "new_runtime_behavior_added": False,
        "new_runtime_consumption_behavior_added": False,
        "new_planner_behavior_added": False,
        "production_output_affected": False,
        "metadata": {
            "governance_only": True,
            "closeout_readiness_audit_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "production_consumer": False,
            "planner_remap_performed": False,
            "silent_readiness_approval_allowed": False,
            "implicit_production_readiness_allowed": False,
            "fallback_closeout_logic_allowed": False,
        },
    }


def classify_v3_2_closeout_state(
    *,
    phase_coverage_state: str,
    contract_compatibility_state: str,
    unresolved_blockers: list[str] | None = None,
) -> str:
    if phase_coverage_state != V3_2_PHASE_COVERAGE_COMPLETE:
        return V3_2_CLOSEOUT_BLOCKED
    if contract_compatibility_state != V3_2_CONTRACTS_COMPATIBLE:
        return V3_2_CLOSEOUT_BLOCKED
    if unresolved_blockers:
        return V3_2_CLOSEOUT_BLOCKED
    return V3_2_CLOSEOUT_SATISFIED


def classify_v3_3_readiness_state(
    *,
    closeout_status: str,
    unresolved_risks: list[str] | None = None,
) -> str:
    if closeout_status != V3_2_CLOSEOUT_SATISFIED:
        return V3_3_BLOCKED
    if unresolved_risks:
        return V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY
    return V3_3_READY_FOR_PLANNING


def summarize_experimental_runtime_closeout_readiness_audit(
    closeout_records: list[dict[str, Any]],
    *,
    run_id: str = "v3_2_phase_12_experimental_runtime_closeout_readiness_audit",
    phase_counts: dict[str, int] | None = None,
    source_hashes: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    records = [deepcopy(record) for record in sorted(closeout_records, key=_record_sort_key)]
    closeout_counts = Counter(record["v3_2_closeout_status"] for record in records)
    readiness_counts = Counter(record["v3_3_readiness_status"] for record in records)
    blocker_counts = Counter(blocker for record in records for blocker in record["unresolved_blockers"])
    risk_counts = Counter(risk for record in records for risk in record["unresolved_risks"])
    limitation_counts = Counter(limitation for record in records for limitation in record["unresolved_limitations"])
    envelope = {
        "schema_version": "v3_2.experimental_runtime_closeout_readiness_audit.1",
        "run": {"run_id": run_id, **(phase_counts or {}), "source_hashes": source_hashes or {}},
        "summary": {
            "records_evaluated": len(records),
            "v3_2_closeout_satisfied_count": closeout_counts[V3_2_CLOSEOUT_SATISFIED],
            "v3_2_closeout_blocked_count": closeout_counts[V3_2_CLOSEOUT_BLOCKED],
            "v3_3_ready_for_planning_count": readiness_counts[V3_3_READY_FOR_PLANNING],
            "v3_3_blocked_count": readiness_counts[V3_3_BLOCKED],
            "v3_3_limited_experimental_continuation_only_count": readiness_counts[
                V3_3_LIMITED_EXPERIMENTAL_CONTINUATION_ONLY
            ],
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
            "production_authoritative_manifest_treatment": False,
            "new_runtime_behavior_added": False,
            "new_runtime_consumption_behavior_added": False,
            "new_planner_behavior_added": False,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "v3_2_closeout_status_counts": {status: closeout_counts[status] for status in V3_2_CLOSEOUT_STATUSES},
        "phase_coverage_distribution": _distribution(records, "phase_coverage_state"),
        "contract_compatibility_distribution": _distribution(records, "contract_compatibility_state"),
        "v3_3_readiness_status_counts": {status: readiness_counts[status] for status in V3_3_READINESS_STATUSES},
        "entrypoint_readiness_summary": _distribution(records, "entrypoint_readiness_state"),
        "isolation_readiness_summary": _distribution(records, "isolation_readiness_state"),
        "session_boundary_readiness_summary": _distribution(records, "session_boundary_readiness_state"),
        "safety_rollback_readiness_summary": _distribution(records, "safety_rollback_readiness_state"),
        "diff_audit_readiness_summary": _distribution(records, "diff_audit_readiness_state"),
        "determinism_readiness_summary": _distribution(records, "determinism_readiness_state"),
        "traceability_readiness_summary": _distribution(records, "traceability_readiness_state"),
        "replayability_readiness_summary": _distribution(records, "replayability_readiness_state"),
        "drift_detection_readiness_summary": _distribution(records, "drift_detection_readiness_state"),
        "limited_experiment_readiness_summary": _distribution(records, "limited_experiment_readiness_state"),
        "kill_switch_readiness_summary": _distribution(records, "kill_switch_readiness_state"),
        "production_routing_prohibition_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False},
        "default_manifest_consumption_disabled_verification": {"runtime_manifest_consumption_enabled": False, "default_manifest_consumption_enabled": False},
        "production_authoritative_manifest_prohibited_verification": {"production_authoritative_manifest_treatment": False, "production_authoritative_manifest_treatment_prohibited": True},
        "unresolved_blocker_summary": dict(sorted(blocker_counts.items())),
        "unresolved_risk_summary": dict(sorted(risk_counts.items())),
        "unresolved_limitation_summary": dict(sorted(limitation_counts.items())),
        "experimental_runtime_closeout_readiness_audits": records,
        "safety_confirmations": {
            "closeout_audit_enables_runtime_manifest_consumption": False,
            "closeout_audit_authorizes_production_routing": False,
            "closeout_audit_treats_manifest_as_production_authoritative": False,
            "v3_3_readiness_authorizes_production_enablement": False,
            "production_runtime_routing_prohibited": True,
            "runtime_manifest_consumption_enabled": False,
            "runtime_production_consumption_enabled": False,
            "legacy_planner_ownership_preserved": True,
            "production_output_affected": False,
            "production_behavior_changed": False,
            "production_planner_routing_changed": False,
        },
        "metadata": {
            "source": "v3_2_experimental_runtime_closeout_readiness_audit",
            "governance_only": True,
            "closeout_readiness_audit_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "stable_generation_token": STABLE_CLOSEOUT_TOKEN,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(envelope)
    return envelope


def _closeout_blockers(
    phase_statuses: dict[str, str | None],
    entrypoint: dict[str, Any] | None,
    isolation: dict[str, Any] | None,
    session: dict[str, Any] | None,
    safety: dict[str, Any] | None,
    diff: dict[str, Any] | None,
    determinism: dict[str, Any] | None,
    traceability: dict[str, Any] | None,
    replayability: dict[str, Any] | None,
    drift: dict[str, Any] | None,
    experiment: dict[str, Any] | None,
    kill_switch: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    expected = {
        "phase_1_entrypoint": EXPERIMENTAL_RUNTIME_ELIGIBLE,
        "phase_2_isolation": RUNTIME_ISOLATION_SATISFIED,
        "phase_3_session_boundary": RUNTIME_SESSION_BOUNDARY_SATISFIED,
        "phase_4_safety": RUNTIME_SAFETY_SATISFIED,
        "phase_4_rollback": RUNTIME_ROLLBACK_READY,
        "phase_5_diff_audit": RUNTIME_DIFF_AUDIT_SATISFIED,
        "phase_6_determinism": RUNTIME_DETERMINISM_SATISFIED,
        "phase_7_traceability": RUNTIME_TRACEABILITY_SATISFIED,
        "phase_8_replayability": RUNTIME_REPLAYABILITY_SATISFIED,
        "phase_10_limited_experiment": LIMITED_RUNTIME_EXPERIMENT_ELIGIBLE,
        "phase_11_kill_switch": RUNTIME_KILL_SWITCH_SATISFIED,
    }
    for phase, expected_status in expected.items():
        if phase_statuses.get(phase) is None:
            blockers.append(f"{phase}_coverage_missing")
        elif phase_statuses.get(phase) != expected_status:
            blockers.append(f"{phase}_contract_incompatible")
    if phase_statuses.get("phase_9_drift_detection") is None:
        blockers.append("phase_9_drift_detection_coverage_missing")
    elif phase_statuses.get("phase_9_drift_detection") not in {RUNTIME_DRIFT_DETECTION_SATISFIED, RUNTIME_DRIFT_NOT_DETECTED}:
        blockers.append("phase_9_drift_detection_contract_incompatible")
    for record in [entrypoint, isolation, session, safety, diff, determinism, traceability, replayability, drift, experiment, kill_switch]:
        if not record:
            continue
        if record.get("production_routing_authorized") is True:
            blockers.append("production_routing_authorization_detected")
        if record.get("runtime_manifest_consumption_enabled") is True or record.get("runtime_manifest_consumption_enabled_by_default") is True:
            blockers.append("default_runtime_manifest_consumption_enabled")
        if record.get("production_authoritative_manifest_treatment") is True:
            blockers.append("production_authoritative_manifest_treatment_detected")
    return sorted(set(blockers), key=blockers.index)


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
