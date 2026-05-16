"""Runtime drift audit contracts for v3.3 planning-only intelligence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    PLANNING_ONLY_LIMITATION,
    PRODUCTION_PROHIBITED_RISK,
    default_runtime_intelligence_classifications,
)
from app.runtime_intelligence.classification_hashing import deterministic_hash
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts
from app.runtime_intelligence.decision_boundary_contracts import default_runtime_decision_boundary_contracts
from app.runtime_intelligence.drift_audit_hashing import (
    hash_drift_audit_manifest,
    serialize_drift_audit_manifest,
    validate_drift_audit_replay_stability,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from app.runtime_intelligence.replay_orchestration_contracts import default_runtime_replay_orchestration_contracts


DRIFT_LABELS = (
    "patch_version_drift",
    "evidence_shape_drift",
    "provenance_lineage_drift",
    "reasoning_sequence_drift",
    "synthesis_output_drift",
    "confidence_boundary_drift",
    "decision_boundary_drift",
    "replay_sequence_drift",
    "explanation_output_drift",
    "hash_manifest_drift",
    "unsupported_state_drift",
    "production_authorization_drift",
)

VALID_DRIFT_CATEGORIES = (
    "patch",
    "evidence",
    "provenance",
    "reasoning",
    "synthesis",
    "confidence",
    "boundary",
    "replay",
    "explanation",
    "hash",
    "unsupported",
    "authorization",
)

VALID_DRIFT_ACTIONS = (
    "record_only",
    "escalation",
    "manual_review_required",
    "hard_stop",
    "authorization_block",
)

DRIFT_AUDIT_PLANNING_LIMITATION = "runtime drift audit contracts are planning-only"
DRIFT_AUDIT_EXECUTION_LIMITATION = "live drift detection is not enabled"
DRIFT_CERTAINTY_RISK = "drift audit contracts must not fabricate drift certainty"


def build_drift_audit_contract(
    *,
    drift_label: str,
    deterministic_rank: int,
    allowed_classification_ids: list[str],
    allowed_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_reasoning_stage_ids: list[str],
    allowed_explanation_type_ids: list[str],
    allowed_confidence_type_ids: list[str],
    allowed_synthesis_type_ids: list[str],
    allowed_boundary_type_ids: list[str],
    allowed_replay_type_ids: list[str],
    drift_category: str,
    drift_action: str,
    requires_baseline_hash: bool,
    requires_current_hash: bool,
    requires_diff_summary: bool,
    requires_replay_validation: bool,
    requires_manual_review: bool,
    blocks_confidence_upgrade: bool,
    blocks_production_authorization: bool,
    preserves_drift: bool,
    preserves_conflicts: bool,
    preserves_unsupported: bool,
    preserves_blockers: bool,
    boundary_visible: bool,
    replay_mismatch_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"drift_label": drift_label, "deterministic_rank": deterministic_rank}
    return {
        "drift_type_id": f"runtime_drift_{drift_label}_{deterministic_hash(seed)[:12]}",
        "drift_label": drift_label,
        "deterministic_rank": deterministic_rank,
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_reasoning_stage_ids": sorted(set(allowed_reasoning_stage_ids)),
        "allowed_explanation_type_ids": sorted(set(allowed_explanation_type_ids)),
        "allowed_confidence_type_ids": sorted(set(allowed_confidence_type_ids)),
        "allowed_synthesis_type_ids": sorted(set(allowed_synthesis_type_ids)),
        "allowed_boundary_type_ids": sorted(set(allowed_boundary_type_ids)),
        "allowed_replay_type_ids": sorted(set(allowed_replay_type_ids)),
        "drift_category": drift_category,
        "drift_action": drift_action,
        "requires_baseline_hash": requires_baseline_hash,
        "requires_current_hash": requires_current_hash,
        "requires_diff_summary": requires_diff_summary,
        "requires_replay_validation": requires_replay_validation,
        "requires_manual_review": requires_manual_review,
        "blocks_confidence_upgrade": blocks_confidence_upgrade,
        "blocks_production_authorization": blocks_production_authorization,
        "preserves_drift": preserves_drift,
        "preserves_conflicts": preserves_conflicts,
        "preserves_unsupported": preserves_unsupported,
        "preserves_blockers": preserves_blockers,
        "boundary_visible": boundary_visible,
        "replay_mismatch_visible": replay_mismatch_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_drift_audit_planning_only": True,
        "live_drift_detection_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_drift_audit_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
    boundary_contracts: list[dict[str, Any]] | None = None,
    replay_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    deps = _resolve_deps(
        classifications,
        evidence_contracts,
        provenance_contracts,
        reasoning_stage_contracts,
        explanation_contracts,
        confidence_contracts,
        synthesis_contracts,
        boundary_contracts,
        replay_contracts,
    )
    c = {row["classification_label"]: row["classification_id"] for row in deps["classifications"]}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in deps["evidence"]}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in deps["provenance"]}
    r = {row["stage_label"]: row["stage_type_id"] for row in deps["reasoning"]}
    x = {row["explanation_label"]: row["explanation_type_id"] for row in deps["explanations"]}
    k = {row["confidence_label"]: row["confidence_type_id"] for row in deps["confidence"]}
    s = {row["synthesis_label"]: row["synthesis_type_id"] for row in deps["synthesis"]}
    b = {row["boundary_label"]: row["boundary_type_id"] for row in deps["boundaries"]}
    y = {row["replay_label"]: row["replay_type_id"] for row in deps["replay"]}
    configs = [
        ("patch_version_drift", 10, "patch", "escalation", ["drift_detected"], ["drift_signal"], ["generated_report_source"], ["drift_check"], ["drift_summary"], ["drift_present"], ["drift_preserving_merge"], ["drift_detected_escalation"], ["replay_audit_summary"], False, False, True, False, False, True, False, True, False, False, False, True, False),
        ("evidence_shape_drift", 20, "evidence", "escalation", ["drift_detected", "partially_verified"], ["observed_runtime_state", "validated_static_record"], ["validated_data_source"], ["evidence_collection"], ["evidence_summary"], ["partially_validated"], ["multi_source_alignment"], ["confidence_ceiling_stop"], ["replay_evidence_sequence"], True, True, True, False, False, True, False, True, False, False, False, True, False),
        ("provenance_lineage_drift", 30, "provenance", "manual_review_required", ["provenance_incomplete"], ["provenance_signal"], ["manual_audit_source"], ["provenance_validation"], ["provenance_summary"], ["provenance_incomplete"], ["provenance_preserving_merge"], ["provenance_incomplete_escalation"], ["replay_provenance_sequence"], True, True, True, False, True, True, False, True, False, False, False, True, False),
        ("reasoning_sequence_drift", 40, "reasoning", "escalation", ["unstable", "drift_detected"], ["limitation_signal"], ["generated_report_source"], ["decision_boundary_check"], ["reasoning_chain_summary"], ["partially_validated"], ["explanation_ready_merge"], ["manual_review_required_boundary"], ["replay_reasoning_sequence"], True, True, True, False, False, True, False, True, False, False, True, True, False),
        ("synthesis_output_drift", 50, "synthesis", "escalation", ["drift_detected", "conflicting"], ["drift_signal", "conflict_signal"], ["generated_report_source"], ["compatibility_check"], ["drift_summary"], ["drift_present", "conflict_present"], ["drift_preserving_merge", "conflict_preserving_merge"], ["drift_detected_escalation"], ["replay_synthesis_sequence"], True, True, True, False, False, True, False, True, True, False, False, True, False),
        ("confidence_boundary_drift", 60, "confidence", "hard_stop", ["unstable", "partially_verified"], ["limitation_signal"], ["manual_audit_source"], ["classification_assignment"], ["confidence_summary"], ["partially_validated", "inferred_limited"], ["confidence_bounded_merge"], ["confidence_ceiling_stop"], ["replay_confidence_sequence"], True, True, True, False, False, True, False, True, False, False, True, True, False),
        ("decision_boundary_drift", 70, "boundary", "hard_stop", ["blocked", "authorization_prohibited"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["blocked"], ["decision_boundary_preserving_merge"], ["blocker_detected_stop"], ["replay_boundary_sequence"], True, True, True, False, False, True, True, True, False, False, True, True, False),
        ("replay_sequence_drift", 80, "replay", "escalation", ["unstable", "conflicting"], ["replay_trace_event"], ["replay_trace_source"], ["replay_check"], ["replay_summary"], ["conflict_present"], ["replay_verified_merge"], ["replay_mismatch_stop"], ["replay_mismatch_detection"], True, True, True, True, False, True, False, True, True, False, False, True, True),
        ("explanation_output_drift", 90, "explanation", "record_only", ["partially_verified", "drift_detected"], ["provenance_signal"], ["generated_report_source"], ["explanation_preparation"], ["reasoning_chain_summary"], ["partially_validated"], ["explanation_ready_merge"], ["manual_review_required_boundary"], ["replay_explanation_sequence"], True, True, True, False, False, False, False, True, False, False, False, True, False),
        ("hash_manifest_drift", 100, "hash", "hard_stop", ["unstable"], ["replay_trace_event"], ["generated_report_source"], ["replay_check"], ["replay_summary"], ["replay_verified"], ["replay_verified_merge"], ["replay_mismatch_stop"], ["replay_audit_summary"], True, True, False, True, False, True, False, True, False, False, False, True, True),
        ("unsupported_state_drift", 110, "unsupported", "hard_stop", ["unsupported"], ["unsupported_signal"], ["unsupported_source"], ["blocker_detection"], ["unsupported_summary"], ["unsupported"], ["unsupported_preserving_merge"], ["unsupported_hard_stop"], ["replay_confidence_sequence"], True, True, True, False, False, True, False, True, False, True, True, True, False),
        ("production_authorization_drift", 120, "authorization", "authorization_block", ["authorization_prohibited"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["authorization_prohibited"], ["decision_boundary_preserving_merge"], ["production_routing_hard_stop"], ["replay_reproducibility_boundary"], True, True, True, False, True, True, True, True, False, False, True, True, False),
    ]
    rows = []
    for label, rank, category, action, classifications_, evidence, provenance, reasoning, explanations, confidence, synthesis, boundaries, replay, baseline_hash, current_hash, diff_summary, replay_validation, manual_review, confidence_block, production_block, drift, conflicts, unsupported, blockers, boundary_visible, replay_mismatch in configs:
        rows.append(
            build_drift_audit_contract(
                drift_label=label,
                deterministic_rank=rank,
                allowed_classification_ids=[c[item] for item in classifications_],
                allowed_evidence_type_ids=[e[item] for item in evidence],
                allowed_provenance_type_ids=[p[item] for item in provenance],
                allowed_reasoning_stage_ids=[r[item] for item in reasoning],
                allowed_explanation_type_ids=[x[item] for item in explanations],
                allowed_confidence_type_ids=[k[item] for item in confidence],
                allowed_synthesis_type_ids=[s[item] for item in synthesis],
                allowed_boundary_type_ids=[b[item] for item in boundaries],
                allowed_replay_type_ids=[y[item] for item in replay],
                drift_category=category,
                drift_action=action,
                requires_baseline_hash=baseline_hash,
                requires_current_hash=current_hash,
                requires_diff_summary=diff_summary,
                requires_replay_validation=replay_validation,
                requires_manual_review=manual_review,
                blocks_confidence_upgrade=confidence_block,
                blocks_production_authorization=production_block,
                preserves_drift=drift,
                preserves_conflicts=conflicts,
                preserves_unsupported=unsupported,
                preserves_blockers=blockers,
                boundary_visible=boundary_visible,
                replay_mismatch_visible=replay_mismatch,
                production_authorized=False,
                explicit_limitations=[PLANNING_ONLY_LIMITATION, DRIFT_AUDIT_PLANNING_LIMITATION, DRIFT_AUDIT_EXECUTION_LIMITATION],
                explicit_risks=[PRODUCTION_PROHIBITED_RISK, DRIFT_CERTAINTY_RISK],
            )
        )
    return rows


def order_drift_audit_contracts(drift_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(row) for row in sorted(drift_contracts, key=lambda row: (int(row["deterministic_rank"]), str(row["drift_label"]), str(row["drift_type_id"])))]


def build_runtime_drift_audit_manifest(drift_contracts: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    deps = _resolve_deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
        kwargs.get("replay_contracts"),
    )
    ordered = order_drift_audit_contracts(
        drift_contracts
        or default_runtime_drift_audit_contracts(
            classifications=deps["classifications"],
            evidence_contracts=deps["evidence"],
            provenance_contracts=deps["provenance"],
            reasoning_stage_contracts=deps["reasoning"],
            explanation_contracts=deps["explanations"],
            confidence_contracts=deps["confidence"],
            synthesis_contracts=deps["synthesis"],
            boundary_contracts=deps["boundaries"],
            replay_contracts=deps["replay"],
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_drift_audit_contracts.1",
        "run": {"run_id": kwargs.get("run_id", "v3_3_phase_10_runtime_drift_audit_contracts"), "drift_contract_count": len(ordered)},
        "drift_contracts": ordered,
        "classification_reference_count": len(deps["classifications"]),
        "evidence_reference_count": len(deps["evidence"]),
        "provenance_reference_count": len(deps["provenance"]),
        "reasoning_stage_reference_count": len(deps["reasoning"]),
        "explanation_reference_count": len(deps["explanations"]),
        "confidence_reference_count": len(deps["confidence"]),
        "synthesis_reference_count": len(deps["synthesis"]),
        "boundary_reference_count": len(deps["boundaries"]),
        "replay_reference_count": len(deps["replay"]),
        "runtime_drift_audit_planning_only": True,
        "live_drift_detection_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_drift_audit_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "drift_certainty_fabricated": False,
            "drift_suppression_allowed": False,
        },
    }
    manifest["deterministic_hash"] = hash_drift_audit_manifest(manifest)
    manifest["replay_validation"] = validate_drift_audit_replay_stability(manifest)
    return manifest


def serialize_runtime_drift_audit_manifest(manifest: dict[str, Any]) -> str:
    return serialize_drift_audit_manifest(manifest)


def _resolve_deps(classifications, evidence_contracts, provenance_contracts, reasoning_stage_contracts, explanation_contracts, confidence_contracts, synthesis_contracts, boundary_contracts, replay_contracts):
    c = classifications or default_runtime_intelligence_classifications()
    e = evidence_contracts or default_runtime_evidence_contracts(c)
    p = provenance_contracts or default_runtime_provenance_contracts(classifications=c, evidence_contracts=e)
    r = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p)
    x = explanation_contracts or default_runtime_explanation_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r)
    k = confidence_contracts or default_runtime_confidence_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x)
    s = synthesis_contracts or default_runtime_evidence_synthesis_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x, confidence_contracts=k)
    b = boundary_contracts or default_runtime_decision_boundary_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x, confidence_contracts=k, synthesis_contracts=s)
    y = replay_contracts or default_runtime_replay_orchestration_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x, confidence_contracts=k, synthesis_contracts=s, boundary_contracts=b)
    return {"classifications": c, "evidence": e, "provenance": p, "reasoning": r, "explanations": x, "confidence": k, "synthesis": s, "boundaries": b, "replay": y}
