"""Runtime evidence synthesis contracts for v3.3 planning-only intelligence."""

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
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_hashing import (
    hash_evidence_synthesis_manifest,
    serialize_evidence_synthesis_manifest,
    validate_evidence_synthesis_replay_stability,
)
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


SYNTHESIS_LABELS = (
    "single_source_preservation",
    "multi_source_alignment",
    "provenance_preserving_merge",
    "confidence_bounded_merge",
    "conflict_preserving_merge",
    "drift_preserving_merge",
    "unsupported_preserving_merge",
    "blocker_preserving_merge",
    "limitation_preserving_merge",
    "replay_verified_merge",
    "explanation_ready_merge",
    "decision_boundary_preserving_merge",
)

PRESERVATION_RULES = {
    "provenance_preserving_merge": "preserves_provenance",
    "conflict_preserving_merge": "preserves_conflicts",
    "drift_preserving_merge": "preserves_drift",
    "unsupported_preserving_merge": "preserves_unsupported",
    "blocker_preserving_merge": "preserves_blockers",
    "limitation_preserving_merge": "preserves_limitations",
    "decision_boundary_preserving_merge": "preserves_blockers",
}

SYNTHESIS_PLANNING_LIMITATION = "runtime evidence synthesis contracts are planning-only"
SYNTHESIS_EXECUTION_LIMITATION = "live runtime evidence synthesis execution is not enabled"
SYNTHESIS_CERTAINTY_RISK = "synthesis contracts must not fabricate synthesized certainty"


def build_evidence_synthesis_contract(
    *,
    synthesis_label: str,
    deterministic_rank: int,
    allowed_input_evidence_type_ids: list[str],
    allowed_output_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_classification_ids: list[str],
    allowed_confidence_type_ids: list[str],
    allowed_reasoning_stage_ids: list[str],
    allowed_explanation_type_ids: list[str],
    minimum_input_count: int,
    maximum_input_count: int,
    preserves_conflicts: bool,
    preserves_drift: bool,
    preserves_unsupported: bool,
    preserves_blockers: bool,
    preserves_limitations: bool,
    preserves_provenance: bool,
    requires_replay_validation: bool,
    requires_hash_validation: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"synthesis_label": synthesis_label, "deterministic_rank": deterministic_rank}
    return {
        "synthesis_type_id": f"runtime_synthesis_{synthesis_label}_{deterministic_hash(seed)[:12]}",
        "synthesis_label": synthesis_label,
        "deterministic_rank": deterministic_rank,
        "allowed_input_evidence_type_ids": sorted(set(allowed_input_evidence_type_ids)),
        "allowed_output_evidence_type_ids": sorted(set(allowed_output_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "allowed_confidence_type_ids": sorted(set(allowed_confidence_type_ids)),
        "allowed_reasoning_stage_ids": sorted(set(allowed_reasoning_stage_ids)),
        "allowed_explanation_type_ids": sorted(set(allowed_explanation_type_ids)),
        "minimum_input_count": int(minimum_input_count),
        "maximum_input_count": int(maximum_input_count),
        "preserves_conflicts": preserves_conflicts,
        "preserves_drift": preserves_drift,
        "preserves_unsupported": preserves_unsupported,
        "preserves_blockers": preserves_blockers,
        "preserves_limitations": preserves_limitations,
        "preserves_provenance": preserves_provenance,
        "requires_replay_validation": requires_replay_validation,
        "requires_hash_validation": requires_hash_validation,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_evidence_synthesis_planning_only": True,
        "live_synthesis_execution_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_evidence_synthesis_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
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
    c = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in provenance_rows}
    r = {row["stage_label"]: row["stage_type_id"] for row in reasoning_rows}
    x = {row["explanation_label"]: row["explanation_type_id"] for row in explanation_rows}
    k = {row["confidence_label"]: row["confidence_type_id"] for row in confidence_rows}
    configs = [
        ("single_source_preservation", 10, ["observed_runtime_state", "validated_static_record"], ["validated_static_record"], ["validated_data_source"], ["verified"], ["deterministic_verified", "validated_static"], ["evidence_collection"], ["evidence_summary"], 1, 1, False, False, False, False, True, True, False, True),
        ("multi_source_alignment", 20, ["observed_runtime_state", "normalized_static_record", "validated_static_record"], ["validated_static_record"], ["trusted_bundle_source", "validated_data_source"], ["verified", "partially_verified"], ["deterministic_verified", "validated_static", "partially_validated"], ["compatibility_check"], ["reasoning_chain_summary"], 2, 5, False, False, False, False, True, True, False, True),
        ("provenance_preserving_merge", 30, ["provenance_signal", "validated_static_record"], ["provenance_signal"], ["extraction_source", "validated_data_source", "manual_audit_source"], ["verified", "provenance_incomplete"], ["provenance_incomplete", "validated_static"], ["provenance_validation"], ["provenance_summary"], 2, 5, False, False, False, False, True, True, False, True),
        ("confidence_bounded_merge", 40, ["validated_static_record", "limitation_signal"], ["validated_static_record"], ["generated_report_source", "manual_audit_source"], ["verified", "partially_verified", "inferred"], ["partially_validated", "inferred_limited", "deterministic_verified"], ["classification_assignment"], ["confidence_summary"], 2, 4, False, False, False, False, True, True, False, True),
        ("conflict_preserving_merge", 50, ["conflict_signal", "validated_static_record"], ["conflict_signal"], ["conflict_detection_source"], ["conflicting"], ["conflict_present"], ["risk_detection"], ["risk_summary"], 2, 5, True, False, False, False, True, True, False, True),
        ("drift_preserving_merge", 60, ["drift_signal", "runtime_trace_event"], ["drift_signal"], ["drift_detection_source", "runtime_trace_source"], ["drift_detected", "unstable"], ["drift_present"], ["drift_check"], ["drift_summary"], 2, 5, False, True, False, False, True, True, False, True),
        ("unsupported_preserving_merge", 70, ["unsupported_signal", "provenance_signal"], ["unsupported_signal"], ["unsupported_source"], ["unsupported"], ["unsupported"], ["blocker_detection"], ["unsupported_summary"], 1, 5, False, False, True, True, True, True, False, True),
        ("blocker_preserving_merge", 80, ["authorization_signal", "conflict_signal", "unsupported_signal"], ["authorization_signal"], ["authorization_gate_source", "manual_audit_source"], ["blocked", "authorization_prohibited", "unsupported"], ["blocked", "authorization_prohibited", "unsupported"], ["blocker_detection"], ["blocker_summary"], 1, 5, True, False, True, True, True, True, False, True),
        ("limitation_preserving_merge", 90, ["limitation_signal", "provenance_signal"], ["limitation_signal"], ["manual_audit_source", "generated_report_source"], ["experimental_only", "partially_verified"], ["experimental_only", "partially_validated"], ["limitation_detection"], ["limitation_summary"], 1, 5, False, False, False, False, True, True, False, True),
        ("replay_verified_merge", 100, ["replay_trace_event", "validated_static_record"], ["replay_trace_event"], ["replay_trace_source", "trusted_bundle_source"], ["replay_verified", "verified"], ["replay_verified"], ["replay_check"], ["replay_summary"], 2, 4, False, False, False, False, True, True, True, True),
        ("explanation_ready_merge", 110, ["provenance_signal", "limitation_signal", "validated_static_record"], ["provenance_signal"], ["generated_report_source"], ["verified", "experimental_only", "partially_verified"], ["partially_validated", "validated_static"], ["explanation_preparation"], ["evidence_summary", "reasoning_chain_summary", "confidence_summary"], 2, 6, False, False, False, False, True, True, False, True),
        ("decision_boundary_preserving_merge", 120, ["authorization_signal", "limitation_signal"], ["authorization_signal"], ["authorization_gate_source", "generated_report_source"], ["authorization_prohibited", "blocked", "experimental_only"], ["authorization_prohibited", "blocked", "experimental_only"], ["decision_boundary_check"], ["decision_boundary_summary"], 1, 4, False, False, True, True, True, True, False, True),
    ]
    rows = []
    for label, rank, input_evidence, output_evidence, provenance, classifications_, confidence, reasoning, explanations, min_count, max_count, conflicts, drift, unsupported, blockers, limitations, provenance_preserved, replay_validation, hash_validation in configs:
        rows.append(
            build_evidence_synthesis_contract(
                synthesis_label=label,
                deterministic_rank=rank,
                allowed_input_evidence_type_ids=[e[item] for item in input_evidence],
                allowed_output_evidence_type_ids=[e[item] for item in output_evidence],
                allowed_provenance_type_ids=[p[item] for item in provenance],
                allowed_classification_ids=[c[item] for item in classifications_],
                allowed_confidence_type_ids=[k[item] for item in confidence],
                allowed_reasoning_stage_ids=[r[item] for item in reasoning],
                allowed_explanation_type_ids=[x[item] for item in explanations],
                minimum_input_count=min_count,
                maximum_input_count=max_count,
                preserves_conflicts=conflicts,
                preserves_drift=drift,
                preserves_unsupported=unsupported,
                preserves_blockers=blockers,
                preserves_limitations=limitations,
                preserves_provenance=provenance_preserved,
                requires_replay_validation=replay_validation,
                requires_hash_validation=hash_validation,
                production_authorized=False,
                explicit_limitations=[
                    PLANNING_ONLY_LIMITATION,
                    SYNTHESIS_PLANNING_LIMITATION,
                    SYNTHESIS_EXECUTION_LIMITATION,
                ],
                explicit_risks=[
                    PRODUCTION_PROHIBITED_RISK,
                    SYNTHESIS_CERTAINTY_RISK,
                ],
            )
        )
    return rows


def order_evidence_synthesis_contracts(synthesis_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            synthesis_contracts,
            key=lambda row: (
                int(row["deterministic_rank"]),
                str(row["synthesis_label"]),
                str(row["synthesis_type_id"]),
            ),
        )
    ]


def build_runtime_evidence_synthesis_manifest(
    synthesis_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_7_runtime_evidence_synthesis_contracts",
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
    ordered = order_evidence_synthesis_contracts(
        synthesis_contracts
        or default_runtime_evidence_synthesis_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
            provenance_contracts=provenance_rows,
            reasoning_stage_contracts=reasoning_rows,
            explanation_contracts=explanation_rows,
            confidence_contracts=confidence_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_evidence_synthesis_contracts.1",
        "run": {"run_id": run_id, "synthesis_contract_count": len(ordered)},
        "synthesis_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "provenance_reference_count": len(provenance_rows),
        "reasoning_stage_reference_count": len(reasoning_rows),
        "explanation_reference_count": len(explanation_rows),
        "confidence_reference_count": len(confidence_rows),
        "runtime_evidence_synthesis_planning_only": True,
        "live_synthesis_execution_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_evidence_synthesis_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "synthesized_certainty_fabricated": False,
            "conflict_suppression_allowed": False,
            "drift_suppression_allowed": False,
        },
    }
    manifest["deterministic_hash"] = hash_evidence_synthesis_manifest(manifest)
    manifest["replay_validation"] = validate_evidence_synthesis_replay_stability(manifest)
    return manifest


def serialize_runtime_evidence_synthesis_manifest(manifest: dict[str, Any]) -> str:
    return serialize_evidence_synthesis_manifest(manifest)
