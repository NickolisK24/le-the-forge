"""Runtime explanation contracts for v3.3 planning-only intelligence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    PLANNING_ONLY_LIMITATION,
    PRODUCTION_PROHIBITED_RISK,
    default_runtime_intelligence_classifications,
)
from app.runtime_intelligence.classification_hashing import deterministic_hash
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.explanation_hashing import (
    hash_explanation_manifest,
    serialize_explanation_manifest,
    validate_explanation_replay_stability,
)
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


EXPLANATION_LABELS = (
    "evidence_summary",
    "provenance_summary",
    "classification_summary",
    "reasoning_chain_summary",
    "blocker_summary",
    "risk_summary",
    "limitation_summary",
    "drift_summary",
    "replay_summary",
    "confidence_summary",
    "decision_boundary_summary",
    "unsupported_summary",
)

EXPLANATION_PLANNING_LIMITATION = "runtime explanation contracts are planning-only"
EXPLANATION_DECISION_LIMITATION = "active runtime explanation decisions are not enabled"
EXPLANATION_CERTAINTY_RISK = "explanations must not fabricate runtime certainty"


def build_explanation_contract(
    *,
    explanation_label: str,
    deterministic_rank: int,
    allowed_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_classification_ids: list[str],
    allowed_reasoning_stage_ids: list[str],
    required_explanation_sections: list[str],
    blocker_visible: bool,
    risk_visible: bool,
    limitation_visible: bool,
    confidence_visible: bool,
    replay_safe: bool,
    drift_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"explanation_label": explanation_label, "deterministic_rank": deterministic_rank}
    return {
        "explanation_type_id": f"runtime_explanation_{explanation_label}_{deterministic_hash(seed)[:12]}",
        "explanation_label": explanation_label,
        "deterministic_rank": deterministic_rank,
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "allowed_reasoning_stage_ids": sorted(set(allowed_reasoning_stage_ids)),
        "required_explanation_sections": sorted(set(required_explanation_sections)),
        "blocker_visible": blocker_visible,
        "risk_visible": risk_visible,
        "limitation_visible": limitation_visible,
        "confidence_visible": confidence_visible,
        "replay_safe": replay_safe,
        "drift_visible": drift_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_explanation_planning_only": True,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_explanation_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
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
    c = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in provenance_rows}
    r = {row["stage_label"]: row["stage_type_id"] for row in reasoning_rows}
    configs = [
        ("evidence_summary", 10, ["observed_runtime_state", "validated_static_record"], ["validated_data_source", "generated_report_source"], ["verified", "partially_verified"], ["evidence_collection", "explanation_preparation"], ["evidence", "classification", "limitations"], False, False, True, False, True),
        ("provenance_summary", 20, ["provenance_signal", "validated_static_record"], ["extraction_source", "validated_data_source", "generated_report_source"], ["verified", "provenance_incomplete"], ["provenance_validation", "explanation_preparation"], ["provenance", "source", "limitations"], False, False, True, False, True),
        ("classification_summary", 30, ["validated_static_record", "limitation_signal"], ["validated_data_source", "generated_report_source"], ["verified", "partially_verified", "inferred", "experimental_only"], ["classification_assignment", "explanation_preparation"], ["classification", "confidence", "limitations"], False, False, True, True, True),
        ("reasoning_chain_summary", 40, ["provenance_signal", "limitation_signal"], ["generated_report_source", "manual_audit_source"], ["verified", "experimental_only", "partially_verified"], ["explanation_preparation"], ["reasoning", "lineage", "limitations"], False, True, True, False, True),
        ("blocker_summary", 50, ["authorization_signal", "unsupported_signal", "conflict_signal"], ["authorization_gate_source", "unsupported_source"], ["blocked", "authorization_prohibited", "unsupported"], ["blocker_detection", "decision_boundary_check"], ["blockers", "decision_boundary", "limitations"], True, False, True, False, False),
        ("risk_summary", 60, ["conflict_signal", "drift_signal"], ["conflict_detection_source", "drift_detection_source"], ["conflicting", "drift_detected", "unstable"], ["risk_detection"], ["risks", "drift", "limitations"], False, True, True, False, False),
        ("limitation_summary", 70, ["limitation_signal", "provenance_signal"], ["manual_audit_source", "generated_report_source"], ["experimental_only", "partially_verified", "blocked"], ["limitation_detection"], ["limitations", "scope", "risks"], False, True, True, False, True),
        ("drift_summary", 80, ["drift_signal", "runtime_trace_event"], ["drift_detection_source", "runtime_trace_source"], ["drift_detected", "unstable"], ["drift_check"], ["drift", "evidence", "risks"], False, True, True, False, False),
        ("replay_summary", 90, ["replay_trace_event", "validated_static_record"], ["replay_trace_source", "trusted_bundle_source"], ["replay_verified", "verified"], ["replay_check"], ["replay", "hash", "limitations"], False, False, True, False, True),
        ("confidence_summary", 100, ["validated_static_record", "provenance_signal"], ["validated_data_source", "generated_report_source"], ["verified", "partially_verified", "inferred"], ["classification_assignment", "explanation_preparation"], ["confidence", "classification", "risks"], False, True, True, True, True),
        ("decision_boundary_summary", 110, ["authorization_signal", "limitation_signal"], ["authorization_gate_source", "generated_report_source"], ["authorization_prohibited", "blocked", "experimental_only"], ["decision_boundary_check"], ["decision_boundary", "blockers", "limitations"], True, True, True, False, False),
        ("unsupported_summary", 120, ["unsupported_signal", "provenance_signal"], ["unsupported_source", "manual_audit_source"], ["unsupported", "blocked", "provenance_incomplete"], ["blocker_detection", "explanation_preparation", "decision_boundary_check"], ["unsupported", "blockers", "limitations"], True, True, True, False, False),
    ]
    rows = []
    for label, rank, evidence_labels, provenance_labels, classification_labels, reasoning_labels, sections, blocker, risk, limitation, confidence, replay_safe in configs:
        rows.append(
            build_explanation_contract(
                explanation_label=label,
                deterministic_rank=rank,
                allowed_evidence_type_ids=[e[item] for item in evidence_labels],
                allowed_provenance_type_ids=[p[item] for item in provenance_labels],
                allowed_classification_ids=[c[item] for item in classification_labels],
                allowed_reasoning_stage_ids=[r[item] for item in reasoning_labels],
                required_explanation_sections=sections,
                blocker_visible=blocker,
                risk_visible=risk,
                limitation_visible=limitation,
                confidence_visible=confidence,
                replay_safe=replay_safe,
                drift_visible=True,
                production_authorized=False,
                explicit_limitations=[
                    PLANNING_ONLY_LIMITATION,
                    EXPLANATION_PLANNING_LIMITATION,
                    EXPLANATION_DECISION_LIMITATION,
                ],
                explicit_risks=[
                    PRODUCTION_PROHIBITED_RISK,
                    EXPLANATION_CERTAINTY_RISK,
                ],
            )
        )
    return rows


def order_explanation_contracts(explanation_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            explanation_contracts,
            key=lambda row: (
                int(row["deterministic_rank"]),
                str(row["explanation_label"]),
                str(row["explanation_type_id"]),
            ),
        )
    ]


def build_runtime_explanation_manifest(
    explanation_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_5_runtime_explanation_contracts",
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
    ordered = order_explanation_contracts(
        explanation_contracts
        or default_runtime_explanation_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
            provenance_contracts=provenance_rows,
            reasoning_stage_contracts=reasoning_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_explanation_contracts.1",
        "run": {"run_id": run_id, "explanation_contract_count": len(ordered)},
        "explanation_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "provenance_reference_count": len(provenance_rows),
        "reasoning_stage_reference_count": len(reasoning_rows),
        "runtime_explanation_planning_only": True,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_explanation_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "explanation_certainty_fabricated": False,
            "unsupported_explanation_visible": True,
            "decision_boundary_explanation_visible": True,
        },
    }
    manifest["deterministic_hash"] = hash_explanation_manifest(manifest)
    manifest["replay_validation"] = validate_explanation_replay_stability(manifest)
    return manifest


def serialize_runtime_explanation_manifest(manifest: dict[str, Any]) -> str:
    return serialize_explanation_manifest(manifest)
