"""Runtime decision boundary contracts for v3.3 planning-only intelligence."""

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
from app.runtime_intelligence.decision_boundary_hashing import (
    hash_decision_boundary_manifest,
    serialize_decision_boundary_manifest,
    validate_decision_boundary_replay_stability,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


BOUNDARY_LABELS = (
    "unsupported_hard_stop",
    "authorization_prohibited_hard_stop",
    "production_routing_hard_stop",
    "default_manifest_consumption_hard_stop",
    "confidence_ceiling_stop",
    "replay_mismatch_stop",
    "drift_detected_escalation",
    "conflict_detected_escalation",
    "provenance_incomplete_escalation",
    "blocker_detected_stop",
    "recommendation_prohibited_boundary",
    "manual_review_required_boundary",
)

VALID_BOUNDARY_ACTIONS = (
    "hard_stop",
    "escalation",
    "manual_review_required",
    "prohibition",
    "planning_only_marker",
)

BOUNDARY_PLANNING_LIMITATION = "runtime decision boundary contracts are planning-only"
BOUNDARY_ROUTING_LIMITATION = "live decision routing is not enabled"
BOUNDARY_CERTAINTY_RISK = "decision boundaries must not fabricate boundary certainty"


def build_decision_boundary_contract(
    *,
    boundary_label: str,
    deterministic_rank: int,
    allowed_classification_ids: list[str],
    allowed_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_reasoning_stage_ids: list[str],
    allowed_explanation_type_ids: list[str],
    allowed_confidence_type_ids: list[str],
    allowed_synthesis_type_ids: list[str],
    boundary_action: str,
    blocks_downstream_reasoning: bool,
    blocks_synthesis_execution: bool,
    blocks_recommendation_logic: bool,
    blocks_production_authorization: bool,
    requires_manual_review: bool,
    requires_replay_validation: bool,
    requires_hash_validation: bool,
    preserves_conflicts: bool,
    preserves_drift: bool,
    preserves_unsupported: bool,
    preserves_blockers: bool,
    preserves_limitations: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"boundary_label": boundary_label, "deterministic_rank": deterministic_rank}
    return {
        "boundary_type_id": f"runtime_boundary_{boundary_label}_{deterministic_hash(seed)[:12]}",
        "boundary_label": boundary_label,
        "deterministic_rank": deterministic_rank,
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_reasoning_stage_ids": sorted(set(allowed_reasoning_stage_ids)),
        "allowed_explanation_type_ids": sorted(set(allowed_explanation_type_ids)),
        "allowed_confidence_type_ids": sorted(set(allowed_confidence_type_ids)),
        "allowed_synthesis_type_ids": sorted(set(allowed_synthesis_type_ids)),
        "boundary_action": boundary_action,
        "blocks_downstream_reasoning": blocks_downstream_reasoning,
        "blocks_synthesis_execution": blocks_synthesis_execution,
        "blocks_recommendation_logic": blocks_recommendation_logic,
        "blocks_production_authorization": blocks_production_authorization,
        "requires_manual_review": requires_manual_review,
        "requires_replay_validation": requires_replay_validation,
        "requires_hash_validation": requires_hash_validation,
        "preserves_conflicts": preserves_conflicts,
        "preserves_drift": preserves_drift,
        "preserves_unsupported": preserves_unsupported,
        "preserves_blockers": preserves_blockers,
        "preserves_limitations": preserves_limitations,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_decision_boundaries_planning_only": True,
        "live_decision_routing_enabled": False,
        "live_synthesis_execution_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_decision_boundary_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    reasoning_rows = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
    )
    explanation_rows = explanation_contracts or default_runtime_explanation_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
    )
    confidence_rows = confidence_contracts or default_runtime_confidence_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
    )
    synthesis_rows = synthesis_contracts or default_runtime_evidence_synthesis_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
    )
    c = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in provenance_rows}
    r = {row["stage_label"]: row["stage_type_id"] for row in reasoning_rows}
    x = {row["explanation_label"]: row["explanation_type_id"] for row in explanation_rows}
    k = {row["confidence_label"]: row["confidence_type_id"] for row in confidence_rows}
    s = {row["synthesis_label"]: row["synthesis_type_id"] for row in synthesis_rows}
    configs = [
        ("unsupported_hard_stop", 10, ["unsupported"], ["unsupported_signal"], ["unsupported_source"], ["blocker_detection"], ["unsupported_summary"], ["unsupported"], ["unsupported_preserving_merge"], "hard_stop", True, True, True, True, False, False, True, False, False, True, True, True),
        ("authorization_prohibited_hard_stop", 20, ["authorization_prohibited"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["authorization_prohibited"], ["decision_boundary_preserving_merge"], "hard_stop", True, True, True, True, False, False, True, False, False, False, True, True),
        ("production_routing_hard_stop", 30, ["authorization_prohibited", "blocked"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["authorization_prohibited", "blocked"], ["decision_boundary_preserving_merge"], "hard_stop", True, True, True, True, False, False, True, False, False, False, True, True),
        ("default_manifest_consumption_hard_stop", 40, ["authorization_prohibited", "blocked"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["authorization_prohibited", "blocked"], ["decision_boundary_preserving_merge"], "hard_stop", True, True, True, True, False, False, True, False, False, False, True, True),
        ("confidence_ceiling_stop", 50, ["partially_verified", "inferred"], ["limitation_signal"], ["manual_audit_source"], ["classification_assignment"], ["confidence_summary"], ["partially_validated", "inferred_limited"], ["confidence_bounded_merge"], "hard_stop", True, True, True, False, False, False, True, False, False, False, False, True),
        ("replay_mismatch_stop", 60, ["unstable", "conflicting"], ["replay_trace_event", "conflict_signal"], ["replay_trace_source"], ["replay_check"], ["replay_summary"], ["replay_verified", "conflict_present"], ["replay_verified_merge"], "hard_stop", True, True, True, False, False, True, True, True, False, False, True, True),
        ("drift_detected_escalation", 70, ["drift_detected", "unstable"], ["drift_signal"], ["drift_detection_source"], ["drift_check"], ["drift_summary"], ["drift_present"], ["drift_preserving_merge"], "escalation", False, True, True, False, False, False, True, False, True, False, False, True),
        ("conflict_detected_escalation", 80, ["conflicting"], ["conflict_signal"], ["conflict_detection_source"], ["risk_detection"], ["risk_summary"], ["conflict_present"], ["conflict_preserving_merge"], "escalation", False, True, True, False, False, False, True, True, False, False, False, True),
        ("provenance_incomplete_escalation", 90, ["provenance_incomplete"], ["provenance_signal"], ["manual_audit_source"], ["provenance_validation"], ["provenance_summary"], ["provenance_incomplete"], ["provenance_preserving_merge"], "escalation", False, True, True, False, True, False, True, False, False, False, False, True),
        ("blocker_detected_stop", 100, ["blocked", "authorization_prohibited"], ["authorization_signal", "conflict_signal"], ["authorization_gate_source"], ["blocker_detection"], ["blocker_summary"], ["blocked", "authorization_prohibited"], ["blocker_preserving_merge"], "hard_stop", True, True, True, True, False, False, True, True, False, False, True, True),
        ("recommendation_prohibited_boundary", 110, ["experimental_only", "authorization_prohibited"], ["limitation_signal", "authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["experimental_only", "authorization_prohibited"], ["decision_boundary_preserving_merge"], "prohibition", True, True, True, True, False, False, True, False, False, False, True, True),
        ("manual_review_required_boundary", 120, ["partially_verified", "provenance_incomplete", "experimental_only"], ["limitation_signal", "provenance_signal"], ["manual_audit_source"], ["limitation_detection"], ["limitation_summary"], ["partially_validated", "provenance_incomplete", "experimental_only"], ["limitation_preserving_merge"], "manual_review_required", False, True, True, False, True, False, True, False, False, False, False, True),
    ]
    rows = []
    for label, rank, classifications_, evidence, provenance, reasoning, explanations, confidence, synthesis, action, blocks_reasoning, blocks_synthesis, blocks_recommendation, blocks_production, manual_review, replay_validation, hash_validation, conflicts, drift, unsupported, blockers, limitations in configs:
        rows.append(
            build_decision_boundary_contract(
                boundary_label=label,
                deterministic_rank=rank,
                allowed_classification_ids=[c[item] for item in classifications_],
                allowed_evidence_type_ids=[e[item] for item in evidence],
                allowed_provenance_type_ids=[p[item] for item in provenance],
                allowed_reasoning_stage_ids=[r[item] for item in reasoning],
                allowed_explanation_type_ids=[x[item] for item in explanations],
                allowed_confidence_type_ids=[k[item] for item in confidence],
                allowed_synthesis_type_ids=[s[item] for item in synthesis],
                boundary_action=action,
                blocks_downstream_reasoning=blocks_reasoning,
                blocks_synthesis_execution=blocks_synthesis,
                blocks_recommendation_logic=blocks_recommendation,
                blocks_production_authorization=blocks_production,
                requires_manual_review=manual_review,
                requires_replay_validation=replay_validation,
                requires_hash_validation=hash_validation,
                preserves_conflicts=conflicts,
                preserves_drift=drift,
                preserves_unsupported=unsupported,
                preserves_blockers=blockers,
                preserves_limitations=limitations,
                production_authorized=False,
                explicit_limitations=[
                    PLANNING_ONLY_LIMITATION,
                    BOUNDARY_PLANNING_LIMITATION,
                    BOUNDARY_ROUTING_LIMITATION,
                ],
                explicit_risks=[
                    PRODUCTION_PROHIBITED_RISK,
                    BOUNDARY_CERTAINTY_RISK,
                ],
            )
        )
    return rows


def order_decision_boundary_contracts(boundary_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            boundary_contracts,
            key=lambda row: (
                int(row["deterministic_rank"]),
                str(row["boundary_label"]),
                str(row["boundary_type_id"]),
            ),
        )
    ]


def build_runtime_decision_boundary_manifest(
    boundary_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_8_runtime_decision_boundary_contracts",
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    reasoning_rows = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
    )
    explanation_rows = explanation_contracts or default_runtime_explanation_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
    )
    confidence_rows = confidence_contracts or default_runtime_confidence_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
    )
    synthesis_rows = synthesis_contracts or default_runtime_evidence_synthesis_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
    )
    ordered = order_decision_boundary_contracts(
        boundary_contracts
        or default_runtime_decision_boundary_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
            provenance_contracts=provenance_rows,
            reasoning_stage_contracts=reasoning_rows,
            explanation_contracts=explanation_rows,
            confidence_contracts=confidence_rows,
            synthesis_contracts=synthesis_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_decision_boundary_contracts.1",
        "run": {"run_id": run_id, "boundary_contract_count": len(ordered)},
        "boundary_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "provenance_reference_count": len(provenance_rows),
        "reasoning_stage_reference_count": len(reasoning_rows),
        "explanation_reference_count": len(explanation_rows),
        "confidence_reference_count": len(confidence_rows),
        "synthesis_reference_count": len(synthesis_rows),
        "runtime_decision_boundaries_planning_only": True,
        "live_decision_routing_enabled": False,
        "live_synthesis_execution_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_decision_boundary_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "boundary_certainty_fabricated": False,
            "unsupported_bypass_allowed": False,
            "conflict_suppression_allowed": False,
            "drift_suppression_allowed": False,
        },
    }
    manifest["deterministic_hash"] = hash_decision_boundary_manifest(manifest)
    manifest["replay_validation"] = validate_decision_boundary_replay_stability(manifest)
    return manifest


def serialize_runtime_decision_boundary_manifest(manifest: dict[str, Any]) -> str:
    return serialize_decision_boundary_manifest(manifest)
