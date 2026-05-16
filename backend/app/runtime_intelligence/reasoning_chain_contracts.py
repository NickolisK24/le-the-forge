"""Runtime reasoning chain contracts for v3.3 planning-only intelligence."""

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
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_hashing import (
    hash_reasoning_chain_manifest,
    serialize_reasoning_chain_manifest,
    validate_reasoning_chain_replay_stability,
)


REASONING_STAGE_LABELS = (
    "evidence_collection",
    "source_validation",
    "provenance_validation",
    "classification_assignment",
    "compatibility_check",
    "blocker_detection",
    "risk_detection",
    "limitation_detection",
    "drift_check",
    "replay_check",
    "explanation_preparation",
    "decision_boundary_check",
)

REASONING_PLANNING_LIMITATION = "runtime reasoning chain contracts are planning-only"
REASONING_DECISION_LIMITATION = "active runtime reasoning decisions are not enabled"
REASONING_CERTAINTY_RISK = "reasoning chains must not fabricate runtime certainty"


def build_reasoning_stage_contract(
    *,
    stage_label: str,
    deterministic_rank: int,
    allowed_evidence_type_ids: list[str],
    allowed_provenance_type_ids: list[str],
    allowed_classification_ids: list[str],
    required_previous_stage_ids: list[str],
    blocker_capable: bool,
    risk_capable: bool,
    limitation_capable: bool,
    replay_safe: bool,
    drift_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"stage_label": stage_label, "deterministic_rank": deterministic_rank}
    return {
        "stage_type_id": f"runtime_reasoning_{stage_label}_{deterministic_hash(seed)[:12]}",
        "stage_label": stage_label,
        "deterministic_rank": deterministic_rank,
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_provenance_type_ids": sorted(set(allowed_provenance_type_ids)),
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "required_previous_stage_ids": list(dict.fromkeys(required_previous_stage_ids)),
        "blocker_capable": blocker_capable,
        "risk_capable": risk_capable,
        "limitation_capable": limitation_capable,
        "replay_safe": replay_safe,
        "drift_visible": drift_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_reasoning_planning_only": True,
        "runtime_evidence_synthesis_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_reasoning_chain_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    c = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in provenance_rows}
    previous_stage_ids: dict[str, str] = {}
    configs = [
        ("evidence_collection", 10, ["observed_runtime_state", "extracted_static_record", "runtime_trace_event"], ["extraction_source", "runtime_trace_source"], ["verified", "partially_verified", "experimental_only"], [], False, False, False, True),
        ("source_validation", 20, ["extracted_static_record", "provenance_signal"], ["extraction_source", "trusted_bundle_source"], ["verified", "provenance_incomplete"], ["evidence_collection"], True, True, True, True),
        ("provenance_validation", 30, ["provenance_signal", "validated_static_record"], ["validated_data_source", "manual_audit_source"], ["verified", "provenance_incomplete"], ["source_validation"], True, True, True, True),
        ("classification_assignment", 40, ["validated_static_record", "normalized_static_record"], ["validated_data_source", "normalized_data_source"], ["verified", "partially_verified", "inferred"], ["provenance_validation"], True, True, True, True),
        ("compatibility_check", 50, ["validated_static_record", "limitation_signal"], ["generated_report_source", "manual_audit_source"], ["verified", "experimental_only", "blocked"], ["classification_assignment"], True, True, True, True),
        ("blocker_detection", 60, ["authorization_signal", "unsupported_signal", "conflict_signal"], ["authorization_gate_source", "unsupported_source"], ["blocked", "authorization_prohibited", "unsupported"], ["compatibility_check"], True, False, False, False),
        ("risk_detection", 70, ["conflict_signal", "drift_signal"], ["conflict_detection_source", "drift_detection_source"], ["conflicting", "drift_detected", "unstable"], ["blocker_detection"], False, True, False, False),
        ("limitation_detection", 80, ["limitation_signal", "provenance_signal"], ["manual_audit_source", "generated_report_source"], ["experimental_only", "partially_verified"], ["risk_detection"], False, False, True, True),
        ("drift_check", 90, ["drift_signal", "runtime_trace_event"], ["drift_detection_source", "runtime_trace_source"], ["drift_detected", "unstable"], ["limitation_detection"], True, True, True, False),
        ("replay_check", 100, ["replay_trace_event", "validated_static_record"], ["replay_trace_source", "trusted_bundle_source"], ["replay_verified", "verified"], ["drift_check"], True, True, True, True),
        ("explanation_preparation", 110, ["provenance_signal", "limitation_signal"], ["generated_report_source", "manual_audit_source"], ["verified", "experimental_only", "partially_verified"], ["replay_check"], False, True, True, True),
        ("decision_boundary_check", 120, ["authorization_signal", "limitation_signal"], ["authorization_gate_source", "generated_report_source"], ["authorization_prohibited", "blocked", "experimental_only"], ["explanation_preparation"], True, True, True, False),
    ]
    rows = []
    for label, rank, evidence_labels, provenance_labels, classification_labels, previous_labels, blocker, risk, limitation, replay_safe in configs:
        required_previous_stage_ids = [previous_stage_ids[item] for item in previous_labels]
        row = build_reasoning_stage_contract(
            stage_label=label,
            deterministic_rank=rank,
            allowed_evidence_type_ids=[e[item] for item in evidence_labels],
            allowed_provenance_type_ids=[p[item] for item in provenance_labels],
            allowed_classification_ids=[c[item] for item in classification_labels],
            required_previous_stage_ids=required_previous_stage_ids,
            blocker_capable=blocker,
            risk_capable=risk,
            limitation_capable=limitation,
            replay_safe=replay_safe,
            drift_visible=True,
            production_authorized=False,
            explicit_limitations=[
                PLANNING_ONLY_LIMITATION,
                REASONING_PLANNING_LIMITATION,
                REASONING_DECISION_LIMITATION,
            ],
            explicit_risks=[
                PRODUCTION_PROHIBITED_RISK,
                REASONING_CERTAINTY_RISK,
            ],
        )
        previous_stage_ids[label] = row["stage_type_id"]
        rows.append(row)
    return rows


def order_reasoning_stage_contracts(reasoning_stage_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            reasoning_stage_contracts,
            key=lambda row: (int(row["deterministic_rank"]), str(row["stage_label"]), str(row["stage_type_id"])),
        )
    ]


def build_runtime_reasoning_chain_manifest(
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_4_runtime_reasoning_chain_contracts",
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    ordered = order_reasoning_stage_contracts(
        reasoning_stage_contracts
        or default_runtime_reasoning_chain_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
            provenance_contracts=provenance_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_reasoning_chain_contracts.1",
        "run": {"run_id": run_id, "reasoning_stage_contract_count": len(ordered)},
        "reasoning_stage_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "provenance_reference_count": len(provenance_rows),
        "runtime_reasoning_planning_only": True,
        "runtime_evidence_synthesis_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_reasoning_chain_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "reasoning_certainty_fabricated": False,
            "decision_boundary_visible": True,
        },
    }
    manifest["deterministic_hash"] = hash_reasoning_chain_manifest(manifest)
    manifest["replay_validation"] = validate_reasoning_chain_replay_stability(manifest)
    return manifest


def serialize_runtime_reasoning_chain_manifest(manifest: dict[str, Any]) -> str:
    return serialize_reasoning_chain_manifest(manifest)
