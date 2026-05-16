"""Deterministic v3.3 runtime intelligence closeout readiness audit."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .classification_hashing import deterministic_hash, stable_serialize


V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING = "v3_3_ready_for_future_controlled_execution_planning"
V3_3_BLOCKED_MISSING_REPORTS = "v3_3_blocked_missing_reports"
V3_3_BLOCKED_INVALID_CROSS_CONTRACT_REFERENCES = "v3_3_blocked_invalid_cross_contract_references"
V3_3_BLOCKED_PRODUCTION_AUTHORIZATION_DETECTED = "v3_3_blocked_production_authorization_detected"
V3_3_BLOCKED_PLANNING_ONLY_VIOLATION = "v3_3_blocked_planning_only_violation"
V3_3_BLOCKED_HASH_OR_REPLAY_VALIDATION_FAILURE = "v3_3_blocked_hash_or_replay_validation_failure"
V3_3_BLOCKED_GOVERNANCE_COVERAGE_GAP = "v3_3_blocked_governance_coverage_gap"


EXPECTED_PHASE_REPORTS: tuple[dict[str, str], ...] = (
    {
        "phase_id": "phase_1_runtime_intelligence_classification",
        "phase_label": "Runtime intelligence classification contracts",
        "report_path": "docs/generated/v3_3_runtime_intelligence_classification_report.json",
    },
    {
        "phase_id": "phase_2_runtime_evidence",
        "phase_label": "Runtime evidence contracts",
        "report_path": "docs/generated/v3_3_runtime_evidence_contracts_report.json",
    },
    {
        "phase_id": "phase_3_runtime_provenance",
        "phase_label": "Runtime provenance contracts",
        "report_path": "docs/generated/v3_3_runtime_provenance_contracts_report.json",
    },
    {
        "phase_id": "phase_4_runtime_reasoning_chain",
        "phase_label": "Runtime reasoning chain contracts",
        "report_path": "docs/generated/v3_3_runtime_reasoning_chain_contracts_report.json",
    },
    {
        "phase_id": "phase_5_runtime_explanation",
        "phase_label": "Runtime explanation contracts",
        "report_path": "docs/generated/v3_3_runtime_explanation_contracts_report.json",
    },
    {
        "phase_id": "phase_6_runtime_confidence",
        "phase_label": "Runtime confidence contracts",
        "report_path": "docs/generated/v3_3_runtime_confidence_contracts_report.json",
    },
    {
        "phase_id": "phase_7_runtime_evidence_synthesis",
        "phase_label": "Runtime evidence synthesis contracts",
        "report_path": "docs/generated/v3_3_runtime_evidence_synthesis_contracts_report.json",
    },
    {
        "phase_id": "phase_8_runtime_decision_boundary",
        "phase_label": "Runtime decision boundary contracts",
        "report_path": "docs/generated/v3_3_runtime_decision_boundary_contracts_report.json",
    },
    {
        "phase_id": "phase_9_runtime_replay_orchestration",
        "phase_label": "Runtime replay orchestration contracts",
        "report_path": "docs/generated/v3_3_runtime_replay_orchestration_contracts_report.json",
    },
    {
        "phase_id": "phase_10_runtime_drift_audit",
        "phase_label": "Runtime drift audit contracts",
        "report_path": "docs/generated/v3_3_runtime_drift_audit_contracts_report.json",
    },
    {
        "phase_id": "phase_11_runtime_session_governance",
        "phase_label": "Runtime session governance contracts",
        "report_path": "docs/generated/v3_3_runtime_session_governance_contracts_report.json",
    },
)


COMPATIBILITY_CHAIN: tuple[dict[str, Any], ...] = (
    {"chain_id": "classification_to_evidence", "phase_ids": ("phase_2_runtime_evidence",)},
    {"chain_id": "classification_evidence_to_provenance", "phase_ids": ("phase_3_runtime_provenance",)},
    {"chain_id": "classification_evidence_provenance_to_reasoning", "phase_ids": ("phase_4_runtime_reasoning_chain",)},
    {"chain_id": "classification_evidence_provenance_reasoning_to_explanations", "phase_ids": ("phase_5_runtime_explanation",)},
    {"chain_id": "classification_evidence_provenance_reasoning_explanations_to_confidence", "phase_ids": ("phase_6_runtime_confidence",)},
    {"chain_id": "classification_evidence_provenance_reasoning_explanations_confidence_to_synthesis", "phase_ids": ("phase_7_runtime_evidence_synthesis",)},
    {"chain_id": "classification_evidence_provenance_reasoning_explanations_confidence_synthesis_to_boundaries", "phase_ids": ("phase_8_runtime_decision_boundary",)},
    {"chain_id": "classification_evidence_provenance_reasoning_explanations_confidence_synthesis_boundaries_to_replay", "phase_ids": ("phase_9_runtime_replay_orchestration",)},
    {"chain_id": "classification_evidence_provenance_reasoning_explanations_confidence_synthesis_boundaries_replay_to_drift", "phase_ids": ("phase_10_runtime_drift_audit",)},
    {"chain_id": "classification_evidence_provenance_reasoning_explanations_confidence_synthesis_boundaries_replay_drift_to_session", "phase_ids": ("phase_11_runtime_session_governance",)},
)


def load_phase_reports(repo_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    reports: dict[str, dict[str, Any]] = {}
    for phase in EXPECTED_PHASE_REPORTS:
        report_path = root / phase["report_path"]
        if not report_path.exists():
            reports[phase["phase_id"]] = {
                "phase_id": phase["phase_id"],
                "phase_label": phase["phase_label"],
                "report_path": phase["report_path"],
                "readable": False,
                "missing": True,
                "error": "report_missing",
            }
            continue
        try:
            reports[phase["phase_id"]] = {
                "phase_id": phase["phase_id"],
                "phase_label": phase["phase_label"],
                "report_path": phase["report_path"],
                "readable": True,
                "missing": False,
                "report": json.loads(report_path.read_text(encoding="utf-8")),
            }
        except (OSError, json.JSONDecodeError) as exc:
            reports[phase["phase_id"]] = {
                "phase_id": phase["phase_id"],
                "phase_label": phase["phase_label"],
                "report_path": phase["report_path"],
                "readable": False,
                "missing": False,
                "error": type(exc).__name__,
            }
    return reports


def build_runtime_intelligence_closeout_readiness_audit(
    *,
    repo_root: Path | str | None = None,
    phase_reports: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    loaded_reports = deepcopy(phase_reports) if phase_reports is not None else load_phase_reports(repo_root)
    phase_results = [_evaluate_phase_report(phase, loaded_reports.get(phase["phase_id"])) for phase in EXPECTED_PHASE_REPORTS]
    compatibility = _evaluate_compatibility_chain(phase_results)
    governance = _evaluate_governance_coverage(phase_results)
    counts = _count_closeout_failures(phase_results, compatibility, governance)
    readiness_status = classify_v3_3_runtime_intelligence_readiness(counts)
    blockers = _readiness_blockers(counts, compatibility, governance)
    risks = _readiness_risks(readiness_status)
    limitations = _readiness_limitations()
    audit = {
        "schema_version": "v3_3.runtime_intelligence_closeout_readiness_audit.1",
        "phase": "v3.3_phase_12_runtime_intelligence_closeout_readiness_audit",
        "audit_only": True,
        "runtime_intelligence_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "live_runtime_execution_enabled": False,
        "live_session_execution_enabled": False,
        "live_drift_detection_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "expected_phase_count": len(EXPECTED_PHASE_REPORTS),
        "audited_phase_count": sum(1 for result in phase_results if result["readable"] and not result["missing"]),
        "phase_results": phase_results,
        "compatibility_chain_validation": compatibility,
        "governance_coverage_validation": governance,
        "readiness_status": readiness_status,
        "readiness_blockers": blockers,
        "readiness_risks": risks,
        "readiness_limitations": limitations,
        "future_controlled_execution_planning_recommendations": _future_planning_recommendations(),
        "summary": {
            **counts,
            "readiness_status": readiness_status,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_3_closeout_is_audit_only": True,
            "runtime_intelligence_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "live_runtime_execution_enabled": False,
            "live_session_execution_enabled": False,
            "live_drift_detection_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "passing_readiness_does_not_authorize_production_runtime_behavior": True,
        },
    }
    audit["deterministic_hash"] = deterministic_hash(_without_hash(audit))
    audit["replay_validation_results"] = {
        "replay_stable": audit["deterministic_hash"] == deterministic_hash(_without_hash(deepcopy(audit))),
        "serializer": "json_sort_keys_sha256",
    }
    return audit


def evaluate_runtime_intelligence_closeout_readiness_audit(audit: dict[str, Any]) -> dict[str, Any]:
    summary = audit["summary"]
    return {
        "passed": audit["readiness_status"] == V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
        "readiness_status": audit["readiness_status"],
        "blocker_count": len(audit["readiness_blockers"]),
        "risk_count": len(audit["readiness_risks"]),
        "limitation_count": len(audit["readiness_limitations"]),
        "missing_report_count": summary["missing_report_count"],
        "invalid_cross_contract_reference_failure_count": summary["invalid_cross_contract_reference_failure_count"],
        "production_authorized_contract_detection_count": summary["production_authorized_contract_detection_count"],
        "planning_only_violation_count": summary["planning_only_violation_count"],
        "stable_hash_validation_failure_count": summary["stable_hash_validation_failure_count"],
        "replay_validation_failure_count": summary["replay_validation_failure_count"],
        "governance_coverage_gap_count": summary["governance_coverage_gap_count"],
    }


def classify_v3_3_runtime_intelligence_readiness(counts: dict[str, int]) -> str:
    if counts["missing_report_count"] or counts["unreadable_report_count"]:
        return V3_3_BLOCKED_MISSING_REPORTS
    if counts["invalid_cross_contract_reference_failure_count"]:
        return V3_3_BLOCKED_INVALID_CROSS_CONTRACT_REFERENCES
    if (
        counts["production_authorized_contract_detection_count"]
        or counts["production_runtime_routing_violation_count"]
        or counts["default_manifest_consumption_violation_count"]
        or counts["production_authoritative_manifest_violation_count"]
    ):
        return V3_3_BLOCKED_PRODUCTION_AUTHORIZATION_DETECTED
    if counts["planning_only_violation_count"]:
        return V3_3_BLOCKED_PLANNING_ONLY_VIOLATION
    if (
        counts["stable_hash_validation_failure_count"]
        or counts["replay_validation_failure_count"]
        or counts["duplicate_detection_failure_count"]
    ):
        return V3_3_BLOCKED_HASH_OR_REPLAY_VALIDATION_FAILURE
    if counts["governance_coverage_gap_count"]:
        return V3_3_BLOCKED_GOVERNANCE_COVERAGE_GAP
    return V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING


def summarize_runtime_intelligence_closeout_readiness_audit(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "readiness_status": audit["readiness_status"],
        "audited_phase_count": audit["audited_phase_count"],
        "expected_phase_count": audit["expected_phase_count"],
        "missing_report_count": audit["summary"]["missing_report_count"],
        "unreadable_report_count": audit["summary"]["unreadable_report_count"],
        "compatibility_chain_valid": audit["compatibility_chain_validation"]["passed"],
        "governance_coverage_valid": audit["governance_coverage_validation"]["passed"],
        "readiness_blocker_count": len(audit["readiness_blockers"]),
        "readiness_risk_count": len(audit["readiness_risks"]),
        "readiness_limitation_count": len(audit["readiness_limitations"]),
        "deterministic_hash": audit["deterministic_hash"],
        "runtime_intelligence_planning_only": audit["runtime_intelligence_planning_only"],
        "production_runtime_prohibited": audit["production_runtime_prohibited"],
        "default_runtime_manifest_consumption_disabled": not audit["runtime_manifest_consumption_enabled"],
        "production_authoritative_manifest_treatment_prohibited": not audit["production_authoritative_manifest_treatment"],
    }


def serialize_runtime_intelligence_closeout_readiness_audit(audit: dict[str, Any]) -> str:
    return stable_serialize(audit)


def _evaluate_phase_report(phase: dict[str, str], loaded: dict[str, Any] | None) -> dict[str, Any]:
    if loaded is None:
        loaded = {
            "phase_id": phase["phase_id"],
            "phase_label": phase["phase_label"],
            "report_path": phase["report_path"],
            "missing": True,
            "readable": False,
            "error": "report_missing",
        }
    report = loaded.get("report", {})
    summary = report.get("summary", {}) if isinstance(report, dict) else {}
    safety = report.get("safety_confirmations", {}) if isinstance(report, dict) else {}
    invalid_reference_count = _sum_summary_keys(summary, ("invalid_",), ("reference_count",))
    production_authorized_count = _sum_summary_keys(summary, ("production_authorized",), ("count",))
    planning_only_valid = _planning_only_valid(report, safety)
    production_routing_valid = report.get("production_runtime_routing_authorized") is False and safety.get("production_runtime_routing_prohibited") is True
    default_manifest_valid = report.get("runtime_manifest_consumption_enabled") is False and safety.get("default_runtime_manifest_consumption_disabled") is True
    production_authoritative_valid = report.get("production_authoritative_manifest_treatment") is False and safety.get("production_authoritative_manifest_treatment_prohibited") is True
    return {
        "phase_id": phase["phase_id"],
        "phase_label": phase["phase_label"],
        "report_path": phase["report_path"],
        "missing": bool(loaded.get("missing")),
        "readable": bool(loaded.get("readable")),
        "error": loaded.get("error"),
        "stable_hash_valid": bool(summary.get("stable_hash_valid")),
        "replay_validation_passed": bool(summary.get("replay_validation_passed")),
        "duplicate_detection_passed": bool(summary.get("duplicate_detection_passed")),
        "invalid_cross_contract_reference_count": invalid_reference_count,
        "production_authorized_contract_count": production_authorized_count,
        "planning_only_valid": planning_only_valid,
        "production_runtime_routing_prohibited": production_routing_valid,
        "default_runtime_manifest_consumption_disabled": default_manifest_valid,
        "production_authoritative_manifest_treatment_prohibited": production_authoritative_valid,
        "summary": summary,
        "safety_confirmations": safety,
    }


def _evaluate_compatibility_chain(phase_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_phase = {result["phase_id"]: result for result in phase_results}
    chain_results = []
    for chain in COMPATIBILITY_CHAIN:
        invalid_count = sum(by_phase[phase_id]["invalid_cross_contract_reference_count"] for phase_id in chain["phase_ids"])
        chain_results.append(
            {
                "chain_id": chain["chain_id"],
                "phase_ids": list(chain["phase_ids"]),
                "invalid_cross_contract_reference_count": invalid_count,
                "passed": invalid_count == 0,
            }
        )
    return {
        "passed": all(result["passed"] for result in chain_results),
        "chain_results": chain_results,
    }


def _evaluate_governance_coverage(phase_results: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = {result["phase_id"]: result["summary"] for result in phase_results}
    safety_values = [result["safety_confirmations"] for result in phase_results]
    coverage = {
        "unsupported_state_visibility": _any_positive(summaries, "unsupported"),
        "provenance_requirements": _any_positive(summaries, "provenance_contracts_requiring") or _any_positive(summaries, "requires_provenance"),
        "source_requirements": _any_positive(summaries, "source"),
        "hash_requirements": _all_summary_true(phase_results, "stable_hash_valid") and _any_positive(summaries, "hash"),
        "replay_validation": _all_summary_true(phase_results, "replay_validation_passed"),
        "drift_visibility": _any_positive(summaries, "drift_visible") or _any_positive(summaries, "drift_preserving"),
        "conflict_visibility": _any_positive(summaries, "conflict"),
        "blocker_visibility": _any_positive(summaries, "blocker"),
        "limitation_visibility": _any_positive(summaries, "limitation"),
        "confidence_boundary_visibility": summaries.get("phase_6_runtime_confidence", {}).get("floor_ceiling_violation_count", -1) == 0
        and _any_positive(summaries, "confidence"),
        "decision_boundary_visibility": _any_positive(summaries, "boundary_visible") or _any_positive(summaries, "decision_boundary"),
        "recommendation_prohibition": _all_safety_false(safety_values, "recommendation_logic_enabled"),
        "production_authorization_prohibition": all(result["production_authorized_contract_count"] == 0 for result in phase_results),
        "default_manifest_consumption_prohibition": all(result["default_runtime_manifest_consumption_disabled"] for result in phase_results),
        "runtime_routing_prohibition": all(result["production_runtime_routing_prohibited"] for result in phase_results),
        "session_isolation": summaries.get("phase_11_runtime_session_governance", {}).get("session_isolating_contract_count", 0) > 0,
        "session_invalidation": summaries.get("phase_11_runtime_session_governance", {}).get("invalidation_visible_contract_count", 0) > 0,
        "session_rollback_visibility": summaries.get("phase_11_runtime_session_governance", {}).get("rollback_visible_contract_count", 0) > 0,
        "cross_session_mutation_blocking": summaries.get("phase_11_runtime_session_governance", {}).get("cross_session_mutation_blocking_contract_count", 0) > 0,
        "manual_review_escalation": _any_positive(summaries, "manual_review"),
        "audit_summary_readiness": summaries.get("phase_11_runtime_session_governance", {}).get("total_session_governance_contract_count", 0) > 0,
    }
    gaps = [key for key, passed in sorted(coverage.items()) if not passed]
    return {
        "passed": not gaps,
        "coverage": coverage,
        "coverage_gaps": gaps,
    }


def _count_closeout_failures(
    phase_results: list[dict[str, Any]],
    compatibility: dict[str, Any],
    governance: dict[str, Any],
) -> dict[str, int]:
    return {
        "missing_report_count": sum(1 for result in phase_results if result["missing"]),
        "unreadable_report_count": sum(1 for result in phase_results if not result["missing"] and not result["readable"]),
        "stable_hash_validation_failure_count": sum(1 for result in phase_results if result["readable"] and not result["stable_hash_valid"]),
        "replay_validation_failure_count": sum(1 for result in phase_results if result["readable"] and not result["replay_validation_passed"]),
        "duplicate_detection_failure_count": sum(1 for result in phase_results if result["readable"] and not result["duplicate_detection_passed"]),
        "invalid_cross_contract_reference_failure_count": sum(result["invalid_cross_contract_reference_count"] for result in phase_results),
        "production_authorized_contract_detection_count": sum(result["production_authorized_contract_count"] for result in phase_results),
        "planning_only_violation_count": sum(1 for result in phase_results if result["readable"] and not result["planning_only_valid"]),
        "production_runtime_routing_violation_count": sum(1 for result in phase_results if result["readable"] and not result["production_runtime_routing_prohibited"]),
        "default_manifest_consumption_violation_count": sum(1 for result in phase_results if result["readable"] and not result["default_runtime_manifest_consumption_disabled"]),
        "production_authoritative_manifest_violation_count": sum(1 for result in phase_results if result["readable"] and not result["production_authoritative_manifest_treatment_prohibited"]),
        "compatibility_chain_failure_count": sum(1 for result in compatibility["chain_results"] if not result["passed"]),
        "governance_coverage_gap_count": len(governance["coverage_gaps"]),
    }


def _planning_only_valid(report: dict[str, Any], safety: dict[str, Any]) -> bool:
    if not report:
        return False
    planning_markers = [value for key, value in report.items() if key.endswith("_planning_only") or "remains_planning_only" in key]
    safety_planning_markers = [value for key, value in safety.items() if key.endswith("_planning_only") or "remains_planning_only" in key]
    if planning_markers and not all(value is True for value in planning_markers):
        return False
    if safety_planning_markers and not all(value is True for value in safety_planning_markers):
        return False
    disabled_runtime_flags = (
        "active_runtime_reasoning_decisions_enabled",
        "autonomous_planner_mutation_enabled",
        "live_decision_routing_enabled",
        "live_drift_detection_enabled",
        "live_replay_execution_enabled",
        "live_runtime_execution_enabled",
        "live_session_execution_enabled",
        "live_synthesis_execution_enabled",
        "probabilistic_inference_enabled",
        "recommendation_logic_enabled",
        "runtime_evidence_synthesis_enabled",
        "runtime_reasoning_decisions_enabled",
        "unrestricted_runtime_execution_enabled",
    )
    for key in disabled_runtime_flags:
        if report.get(key) is True or safety.get(key) is True:
            return False
    return True


def _sum_summary_keys(summary: dict[str, Any], prefixes: tuple[str, ...], suffixes: tuple[str, ...]) -> int:
    total = 0
    for key, value in summary.items():
        if any(key.startswith(prefix) for prefix in prefixes) and any(key.endswith(suffix) for suffix in suffixes):
            if isinstance(value, int):
                total += value
    return total


def _any_positive(summaries: dict[str, dict[str, Any]], token: str) -> bool:
    for summary in summaries.values():
        for key, value in summary.items():
            if token in key and isinstance(value, int) and value > 0:
                return True
    return False


def _all_summary_true(phase_results: list[dict[str, Any]], key: str) -> bool:
    readable = [result for result in phase_results if result["readable"]]
    return bool(readable) and all(result["summary"].get(key) is True for result in readable)


def _all_safety_false(safety_values: list[dict[str, Any]], key: str) -> bool:
    observed = [safety for safety in safety_values if key in safety]
    return bool(observed) and all(safety[key] is False for safety in observed)


def _readiness_blockers(
    counts: dict[str, int],
    compatibility: dict[str, Any],
    governance: dict[str, Any],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for key, value in sorted(counts.items()):
        if value:
            blockers.append({"blocker_id": key, "count": value})
    for result in compatibility["chain_results"]:
        if not result["passed"]:
            blockers.append({"blocker_id": f"compatibility_chain:{result['chain_id']}", "count": result["invalid_cross_contract_reference_count"]})
    for gap in governance["coverage_gaps"]:
        blockers.append({"blocker_id": f"governance_coverage:{gap}", "count": 1})
    return blockers


def _readiness_risks(readiness_status: str) -> list[str]:
    risks = [
        "future controlled execution must add a new explicitly scoped non-production governance phase",
        "runtime intelligence outputs remain planning-only until future execution controls are defined",
        "production runtime routing remains out of scope for this closeout",
    ]
    if readiness_status != V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING:
        risks.append("blocked readiness requires remediation before future controlled execution planning")
    return risks


def _readiness_limitations() -> list[str]:
    return [
        "no live runtime execution is enabled",
        "no live session execution is enabled",
        "no live drift detection is enabled",
        "no live replay execution is enabled",
        "no live synthesis execution is enabled",
        "no live decision routing is enabled",
        "no active runtime reasoning decisions are enabled",
        "no recommendation logic is enabled",
        "passing readiness does not authorize production runtime behavior",
    ]


def _future_planning_recommendations() -> list[str]:
    return [
        "define a future non-production controlled execution gate before any live execution experiment",
        "reuse the v3.3 classification, evidence, provenance, reasoning, explanation, confidence, synthesis, boundary, replay, drift, and session audit chain as planning evidence",
        "keep production routing, default manifest consumption, and production-authoritative manifest treatment prohibited until separately governed",
    ]


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    stable.pop("replay_validation_results", None)
    return stable
