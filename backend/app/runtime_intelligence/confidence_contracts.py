"""Runtime confidence contracts for v3.3 planning-only intelligence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    PLANNING_ONLY_LIMITATION,
    PRODUCTION_PROHIBITED_RISK,
    default_runtime_intelligence_classifications,
)
from app.runtime_intelligence.classification_hashing import deterministic_hash
from app.runtime_intelligence.confidence_hashing import (
    hash_confidence_manifest,
    serialize_confidence_manifest,
    validate_confidence_replay_stability,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


CONFIDENCE_LABELS = (
    "deterministic_verified",
    "replay_verified",
    "validated_static",
    "partially_validated",
    "inferred_limited",
    "experimental_only",
    "provenance_incomplete",
    "conflict_present",
    "drift_present",
    "unsupported",
    "blocked",
    "authorization_prohibited",
)

NON_UPGRADEABLE_CONFIDENCE_LABELS = (
    "unsupported",
    "blocked",
    "drift_present",
    "conflict_present",
    "provenance_incomplete",
    "authorization_prohibited",
)

CONFIDENCE_PLANNING_LIMITATION = "runtime confidence contracts are planning-only"
CONFIDENCE_SCORING_LIMITATION = "live scoring and probabilistic inference are not enabled"
CONFIDENCE_CERTAINTY_RISK = "confidence contracts must not fabricate runtime certainty"


def build_confidence_contract(
    *,
    confidence_label: str,
    deterministic_rank: int,
    allowed_classification_ids: list[str],
    allowed_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_reasoning_stage_ids: list[str],
    allowed_explanation_type_ids: list[str],
    trust_level: str,
    certainty_level: str,
    confidence_floor: int,
    confidence_ceiling: int,
    can_upgrade_without_revalidation: bool,
    requires_provenance: bool,
    requires_replay_validation: bool,
    blocker_visible: bool,
    risk_visible: bool,
    limitation_visible: bool,
    replay_safe: bool,
    drift_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"confidence_label": confidence_label, "deterministic_rank": deterministic_rank}
    return {
        "confidence_type_id": f"runtime_confidence_{confidence_label}_{deterministic_hash(seed)[:12]}",
        "confidence_label": confidence_label,
        "deterministic_rank": deterministic_rank,
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_reasoning_stage_ids": sorted(set(allowed_reasoning_stage_ids)),
        "allowed_explanation_type_ids": sorted(set(allowed_explanation_type_ids)),
        "trust_level": trust_level,
        "certainty_level": certainty_level,
        "confidence_floor": int(confidence_floor),
        "confidence_ceiling": int(confidence_ceiling),
        "can_upgrade_without_revalidation": can_upgrade_without_revalidation,
        "requires_provenance": requires_provenance,
        "requires_replay_validation": requires_replay_validation,
        "blocker_visible": blocker_visible,
        "risk_visible": risk_visible,
        "limitation_visible": limitation_visible,
        "replay_safe": replay_safe,
        "drift_visible": drift_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_confidence_planning_only": True,
        "live_confidence_scoring_enabled": False,
        "probabilistic_inference_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_confidence_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
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
    c = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in provenance_rows}
    r = {row["stage_label"]: row["stage_type_id"] for row in reasoning_rows}
    x = {row["explanation_label"]: row["explanation_type_id"] for row in explanation_rows}
    configs = [
        ("deterministic_verified", 10, ["verified"], ["validated_static_record", "provenance_signal"], ["validated_data_source"], ["classification_assignment", "explanation_preparation"], ["classification_summary", "confidence_summary"], "verified", "deterministic", 95, 100, True, True, False, False, False, True, True, True),
        ("replay_verified", 20, ["replay_verified", "verified"], ["replay_trace_event", "validated_static_record"], ["replay_trace_source", "trusted_bundle_source"], ["replay_check"], ["replay_summary", "confidence_summary"], "replay_verified", "replay_stable", 90, 100, True, True, True, False, False, True, True, True),
        ("validated_static", 30, ["verified", "partially_verified"], ["validated_static_record", "normalized_static_record"], ["validated_data_source", "normalized_data_source"], ["classification_assignment"], ["evidence_summary", "classification_summary"], "validated", "static_validated", 80, 95, True, True, False, False, False, True, True, True),
        ("partially_validated", 40, ["partially_verified"], ["validated_static_record", "limitation_signal"], ["manual_audit_source", "generated_report_source"], ["limitation_detection"], ["limitation_summary", "confidence_summary"], "partial", "partial", 50, 79, False, True, False, False, True, True, True, True),
        ("inferred_limited", 50, ["inferred", "experimental_only"], ["normalized_static_record", "limitation_signal"], ["normalized_data_source", "manual_audit_source"], ["classification_assignment", "limitation_detection"], ["classification_summary", "limitation_summary"], "inferred_limited", "limited_inference", 30, 60, False, True, False, False, True, True, False, True),
        ("experimental_only", 60, ["experimental_only"], ["limitation_signal", "authorization_signal"], ["authorization_gate_source", "generated_report_source"], ["compatibility_check", "decision_boundary_check"], ["decision_boundary_summary", "limitation_summary"], "experimental", "experimental_only", 20, 60, False, True, False, True, True, True, False, True),
        ("provenance_incomplete", 70, ["provenance_incomplete"], ["provenance_signal"], ["manual_audit_source"], ["provenance_validation"], ["provenance_summary", "unsupported_summary"], "incomplete", "provenance_incomplete", 0, 49, False, True, False, True, True, True, False, True),
        ("conflict_present", 80, ["conflicting"], ["conflict_signal"], ["conflict_detection_source"], ["risk_detection"], ["risk_summary"], "conflict", "conflicting", 0, 40, False, True, False, True, True, True, False, True),
        ("drift_present", 90, ["drift_detected", "unstable"], ["drift_signal", "runtime_trace_event"], ["drift_detection_source", "runtime_trace_source"], ["drift_check"], ["drift_summary"], "drift", "drift_visible", 0, 40, False, True, False, True, True, True, False, True),
        ("unsupported", 100, ["unsupported"], ["unsupported_signal"], ["unsupported_source"], ["blocker_detection"], ["unsupported_summary"], "unsupported", "unsupported", 0, 0, False, True, False, True, True, True, False, True),
        ("blocked", 110, ["blocked"], ["authorization_signal", "conflict_signal"], ["authorization_gate_source", "manual_audit_source"], ["blocker_detection", "decision_boundary_check"], ["blocker_summary"], "blocked", "blocked", 0, 0, False, True, False, True, True, True, False, True),
        ("authorization_prohibited", 120, ["authorization_prohibited"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], "prohibited", "authorization_prohibited", 0, 0, False, True, False, True, True, True, False, True),
    ]
    rows = []
    for label, rank, classification_labels, evidence_labels, provenance_labels, reasoning_labels, explanation_labels, trust, certainty, floor, ceiling, upgrade, provenance_required, replay_required, blocker, risk, limitation, replay_safe, drift_visible in configs:
        rows.append(
            build_confidence_contract(
                confidence_label=label,
                deterministic_rank=rank,
                allowed_classification_ids=[c[item] for item in classification_labels],
                allowed_evidence_type_ids=[e[item] for item in evidence_labels],
                allowed_provenance_type_ids=[p[item] for item in provenance_labels],
                allowed_reasoning_stage_ids=[r[item] for item in reasoning_labels],
                allowed_explanation_type_ids=[x[item] for item in explanation_labels],
                trust_level=trust,
                certainty_level=certainty,
                confidence_floor=floor,
                confidence_ceiling=ceiling,
                can_upgrade_without_revalidation=upgrade,
                requires_provenance=provenance_required,
                requires_replay_validation=replay_required,
                blocker_visible=blocker,
                risk_visible=risk,
                limitation_visible=limitation,
                replay_safe=replay_safe,
                drift_visible=drift_visible,
                production_authorized=False,
                explicit_limitations=[
                    PLANNING_ONLY_LIMITATION,
                    CONFIDENCE_PLANNING_LIMITATION,
                    CONFIDENCE_SCORING_LIMITATION,
                ],
                explicit_risks=[
                    PRODUCTION_PROHIBITED_RISK,
                    CONFIDENCE_CERTAINTY_RISK,
                ],
            )
        )
    return rows


def order_confidence_contracts(confidence_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            confidence_contracts,
            key=lambda row: (
                int(row["deterministic_rank"]),
                str(row["confidence_label"]),
                str(row["confidence_type_id"]),
            ),
        )
    ]


def build_runtime_confidence_manifest(
    confidence_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_6_runtime_confidence_contracts",
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
    ordered = order_confidence_contracts(
        confidence_contracts
        or default_runtime_confidence_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
            provenance_contracts=provenance_rows,
            reasoning_stage_contracts=reasoning_rows,
            explanation_contracts=explanation_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_confidence_contracts.1",
        "run": {"run_id": run_id, "confidence_contract_count": len(ordered)},
        "confidence_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "provenance_reference_count": len(provenance_rows),
        "reasoning_stage_reference_count": len(reasoning_rows),
        "explanation_reference_count": len(explanation_rows),
        "runtime_confidence_planning_only": True,
        "live_confidence_scoring_enabled": False,
        "probabilistic_inference_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_confidence_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "confidence_certainty_fabricated": False,
            "unsupported_confidence_visible": True,
            "authorization_prohibited_confidence_visible": True,
        },
    }
    manifest["deterministic_hash"] = hash_confidence_manifest(manifest)
    manifest["replay_validation"] = validate_confidence_replay_stability(manifest)
    return manifest


def serialize_runtime_confidence_manifest(manifest: dict[str, Any]) -> str:
    return serialize_confidence_manifest(manifest)
