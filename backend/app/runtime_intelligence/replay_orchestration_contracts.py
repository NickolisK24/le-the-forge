"""Runtime replay orchestration contracts for v3.3 planning-only intelligence."""

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
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from app.runtime_intelligence.replay_orchestration_hashing import (
    hash_replay_orchestration_manifest,
    serialize_replay_orchestration_manifest,
    validate_replay_orchestration_replay_stability,
)


REPLAY_LABELS = (
    "replay_session_identity",
    "replay_input_manifest",
    "replay_evidence_sequence",
    "replay_provenance_sequence",
    "replay_reasoning_sequence",
    "replay_synthesis_sequence",
    "replay_confidence_sequence",
    "replay_boundary_sequence",
    "replay_explanation_sequence",
    "replay_mismatch_detection",
    "replay_audit_summary",
    "replay_reproducibility_boundary",
)

REPLAY_PLANNING_LIMITATION = "runtime replay orchestration contracts are planning-only"
REPLAY_EXECUTION_LIMITATION = "live replay execution is not enabled"
REPLAY_CERTAINTY_RISK = "replay orchestration contracts must not fabricate replay certainty"


def build_replay_orchestration_contract(
    *,
    replay_label: str,
    deterministic_rank: int,
    allowed_classification_ids: list[str],
    allowed_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_reasoning_stage_ids: list[str],
    allowed_explanation_type_ids: list[str],
    allowed_confidence_type_ids: list[str],
    allowed_synthesis_type_ids: list[str],
    allowed_boundary_type_ids: list[str],
    required_previous_replay_type_ids: list[str],
    requires_input_hash: bool,
    requires_output_hash: bool,
    requires_sequence_hash: bool,
    mismatch_visible: bool,
    drift_visible: bool,
    conflict_visible: bool,
    blocker_visible: bool,
    boundary_visible: bool,
    reproducibility_required: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"replay_label": replay_label, "deterministic_rank": deterministic_rank}
    return {
        "replay_type_id": f"runtime_replay_{replay_label}_{deterministic_hash(seed)[:12]}",
        "replay_label": replay_label,
        "deterministic_rank": deterministic_rank,
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_reasoning_stage_ids": sorted(set(allowed_reasoning_stage_ids)),
        "allowed_explanation_type_ids": sorted(set(allowed_explanation_type_ids)),
        "allowed_confidence_type_ids": sorted(set(allowed_confidence_type_ids)),
        "allowed_synthesis_type_ids": sorted(set(allowed_synthesis_type_ids)),
        "allowed_boundary_type_ids": sorted(set(allowed_boundary_type_ids)),
        "required_previous_replay_type_ids": list(dict.fromkeys(required_previous_replay_type_ids)),
        "requires_input_hash": requires_input_hash,
        "requires_output_hash": requires_output_hash,
        "requires_sequence_hash": requires_sequence_hash,
        "mismatch_visible": mismatch_visible,
        "drift_visible": drift_visible,
        "conflict_visible": conflict_visible,
        "blocker_visible": blocker_visible,
        "boundary_visible": boundary_visible,
        "reproducibility_required": reproducibility_required,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_replay_orchestration_planning_only": True,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_replay_orchestration_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
    boundary_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(classifications=classification_rows, evidence_contracts=evidence_rows)
    reasoning_rows = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows)
    explanation_rows = explanation_contracts or default_runtime_explanation_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows)
    confidence_rows = confidence_contracts or default_runtime_confidence_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows, explanation_contracts=explanation_rows)
    synthesis_rows = synthesis_contracts or default_runtime_evidence_synthesis_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows, explanation_contracts=explanation_rows, confidence_contracts=confidence_rows)
    boundary_rows = boundary_contracts or default_runtime_decision_boundary_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows, explanation_contracts=explanation_rows, confidence_contracts=confidence_rows, synthesis_contracts=synthesis_rows)
    c = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in provenance_rows}
    r = {row["stage_label"]: row["stage_type_id"] for row in reasoning_rows}
    x = {row["explanation_label"]: row["explanation_type_id"] for row in explanation_rows}
    k = {row["confidence_label"]: row["confidence_type_id"] for row in confidence_rows}
    s = {row["synthesis_label"]: row["synthesis_type_id"] for row in synthesis_rows}
    b = {row["boundary_label"]: row["boundary_type_id"] for row in boundary_rows}
    previous: dict[str, str] = {}
    configs = [
        ("replay_session_identity", 10, ["verified", "experimental_only"], ["provenance_signal"], ["generated_report_source"], ["evidence_collection"], ["replay_summary"], ["replay_verified"], ["single_source_preservation"], ["manual_review_required_boundary"], [], True, False, False, False, False, False, False, False, True),
        ("replay_input_manifest", 20, ["verified"], ["validated_static_record", "provenance_signal"], ["trusted_bundle_source"], ["source_validation"], ["evidence_summary"], ["validated_static"], ["single_source_preservation"], ["manual_review_required_boundary"], ["replay_session_identity"], True, False, True, False, False, False, False, False, True),
        ("replay_evidence_sequence", 30, ["verified", "partially_verified"], ["observed_runtime_state", "validated_static_record", "runtime_trace_event"], ["validated_data_source"], ["evidence_collection"], ["evidence_summary"], ["validated_static"], ["multi_source_alignment"], ["confidence_ceiling_stop"], ["replay_input_manifest"], False, False, True, False, True, False, False, False, True),
        ("replay_provenance_sequence", 40, ["verified", "provenance_incomplete"], ["provenance_signal"], ["extraction_source", "manual_audit_source"], ["provenance_validation"], ["provenance_summary"], ["provenance_incomplete"], ["provenance_preserving_merge"], ["provenance_incomplete_escalation"], ["replay_evidence_sequence"], False, False, True, False, True, False, False, False, True),
        ("replay_reasoning_sequence", 50, ["verified", "experimental_only"], ["validated_static_record", "limitation_signal"], ["generated_report_source"], ["classification_assignment", "decision_boundary_check"], ["reasoning_chain_summary"], ["partially_validated"], ["explanation_ready_merge"], ["manual_review_required_boundary"], ["replay_provenance_sequence"], False, False, True, False, True, False, False, True, True),
        ("replay_synthesis_sequence", 60, ["verified", "conflicting", "drift_detected"], ["conflict_signal", "drift_signal", "validated_static_record"], ["generated_report_source"], ["compatibility_check"], ["reasoning_chain_summary"], ["conflict_present", "drift_present"], ["conflict_preserving_merge", "drift_preserving_merge"], ["conflict_detected_escalation", "drift_detected_escalation"], ["replay_reasoning_sequence"], False, False, True, False, True, True, False, True, True),
        ("replay_confidence_sequence", 70, ["verified", "partially_verified", "unsupported"], ["limitation_signal", "unsupported_signal"], ["manual_audit_source"], ["classification_assignment"], ["confidence_summary"], ["deterministic_verified", "unsupported", "blocked"], ["confidence_bounded_merge"], ["unsupported_hard_stop", "confidence_ceiling_stop"], ["replay_synthesis_sequence"], False, False, True, False, True, True, True, True, True),
        ("replay_boundary_sequence", 80, ["blocked", "authorization_prohibited", "experimental_only"], ["authorization_signal", "limitation_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["blocked", "authorization_prohibited"], ["decision_boundary_preserving_merge"], ["blocker_detected_stop", "authorization_prohibited_hard_stop"], ["replay_confidence_sequence"], False, False, True, False, True, True, True, True, True),
        ("replay_explanation_sequence", 90, ["verified", "experimental_only"], ["provenance_signal", "limitation_signal"], ["generated_report_source"], ["explanation_preparation"], ["evidence_summary", "replay_summary", "decision_boundary_summary"], ["partially_validated"], ["explanation_ready_merge"], ["manual_review_required_boundary"], ["replay_boundary_sequence"], False, True, True, False, True, True, True, True, True),
        ("replay_mismatch_detection", 100, ["conflicting", "unstable"], ["replay_trace_event", "conflict_signal"], ["replay_trace_source"], ["replay_check"], ["replay_summary"], ["conflict_present"], ["replay_verified_merge"], ["replay_mismatch_stop"], ["replay_explanation_sequence"], False, True, True, True, True, True, True, True, True),
        ("replay_audit_summary", 110, ["verified", "replay_verified"], ["replay_trace_event", "provenance_signal"], ["generated_report_source"], ["explanation_preparation"], ["replay_summary"], ["replay_verified"], ["replay_verified_merge"], ["manual_review_required_boundary"], ["replay_mismatch_detection"], False, True, True, True, True, True, True, True, True),
        ("replay_reproducibility_boundary", 120, ["replay_verified", "authorization_prohibited"], ["replay_trace_event", "authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["replay_verified", "authorization_prohibited"], ["decision_boundary_preserving_merge"], ["replay_mismatch_stop", "recommendation_prohibited_boundary"], ["replay_audit_summary"], True, True, True, True, True, True, True, True, True),
    ]
    rows = []
    for label, rank, classifications_, evidence, provenance, reasoning, explanations, confidence, synthesis, boundaries, previous_labels, in_hash, out_hash, seq_hash, mismatch, drift, conflict, blocker, boundary, reproducibility in configs:
        row = build_replay_orchestration_contract(
            replay_label=label,
            deterministic_rank=rank,
            allowed_classification_ids=[c[item] for item in classifications_],
            allowed_evidence_type_ids=[e[item] for item in evidence],
            allowed_provenance_type_ids=[p[item] for item in provenance],
            allowed_reasoning_stage_ids=[r[item] for item in reasoning],
            allowed_explanation_type_ids=[x[item] for item in explanations],
            allowed_confidence_type_ids=[k[item] for item in confidence],
            allowed_synthesis_type_ids=[s[item] for item in synthesis],
            allowed_boundary_type_ids=[b[item] for item in boundaries],
            required_previous_replay_type_ids=[previous[item] for item in previous_labels],
            requires_input_hash=in_hash,
            requires_output_hash=out_hash,
            requires_sequence_hash=seq_hash,
            mismatch_visible=mismatch,
            drift_visible=drift,
            conflict_visible=conflict,
            blocker_visible=blocker,
            boundary_visible=boundary,
            reproducibility_required=reproducibility,
            production_authorized=False,
            explicit_limitations=[PLANNING_ONLY_LIMITATION, REPLAY_PLANNING_LIMITATION, REPLAY_EXECUTION_LIMITATION],
            explicit_risks=[PRODUCTION_PROHIBITED_RISK, REPLAY_CERTAINTY_RISK],
        )
        previous[label] = row["replay_type_id"]
        rows.append(row)
    return rows


def order_replay_orchestration_contracts(replay_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(row) for row in sorted(replay_contracts, key=lambda row: (int(row["deterministic_rank"]), str(row["replay_label"]), str(row["replay_type_id"])))]


def build_runtime_replay_orchestration_manifest(
    replay_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
    boundary_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_9_runtime_replay_orchestration_contracts",
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(classifications=classification_rows, evidence_contracts=evidence_rows)
    reasoning_rows = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows)
    explanation_rows = explanation_contracts or default_runtime_explanation_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows)
    confidence_rows = confidence_contracts or default_runtime_confidence_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows, explanation_contracts=explanation_rows)
    synthesis_rows = synthesis_contracts or default_runtime_evidence_synthesis_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows, explanation_contracts=explanation_rows, confidence_contracts=confidence_rows)
    boundary_rows = boundary_contracts or default_runtime_decision_boundary_contracts(classifications=classification_rows, evidence_contracts=evidence_rows, provenance_contracts=provenance_rows, reasoning_stage_contracts=reasoning_rows, explanation_contracts=explanation_rows, confidence_contracts=confidence_rows, synthesis_contracts=synthesis_rows)
    ordered = order_replay_orchestration_contracts(
        replay_contracts
        or default_runtime_replay_orchestration_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
            provenance_contracts=provenance_rows,
            reasoning_stage_contracts=reasoning_rows,
            explanation_contracts=explanation_rows,
            confidence_contracts=confidence_rows,
            synthesis_contracts=synthesis_rows,
            boundary_contracts=boundary_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_replay_orchestration_contracts.1",
        "run": {"run_id": run_id, "replay_contract_count": len(ordered)},
        "replay_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "provenance_reference_count": len(provenance_rows),
        "reasoning_stage_reference_count": len(reasoning_rows),
        "explanation_reference_count": len(explanation_rows),
        "confidence_reference_count": len(confidence_rows),
        "synthesis_reference_count": len(synthesis_rows),
        "boundary_reference_count": len(boundary_rows),
        "runtime_replay_orchestration_planning_only": True,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_replay_orchestration_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "replay_certainty_fabricated": False,
            "replay_mismatch_suppression_allowed": False,
            "decision_boundary_bypass_allowed": False,
        },
    }
    manifest["deterministic_hash"] = hash_replay_orchestration_manifest(manifest)
    manifest["replay_validation"] = validate_replay_orchestration_replay_stability(manifest)
    return manifest


def serialize_runtime_replay_orchestration_manifest(manifest: dict[str, Any]) -> str:
    return serialize_replay_orchestration_manifest(manifest)
