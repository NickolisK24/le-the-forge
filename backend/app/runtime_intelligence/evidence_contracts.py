"""Runtime evidence contracts for v3.3 planning-only intelligence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    PLANNING_ONLY_LIMITATION,
    PRODUCTION_PROHIBITED_RISK,
    default_runtime_intelligence_classifications,
)
from app.runtime_intelligence.classification_hashing import deterministic_hash
from app.runtime_intelligence.evidence_hashing import (
    hash_evidence_manifest,
    serialize_evidence_manifest,
    validate_evidence_replay_stability,
)


EVIDENCE_LABELS = (
    "observed_runtime_state",
    "extracted_static_record",
    "normalized_static_record",
    "validated_static_record",
    "runtime_trace_event",
    "replay_trace_event",
    "drift_signal",
    "conflict_signal",
    "unsupported_signal",
    "provenance_signal",
    "authorization_signal",
    "limitation_signal",
)

EVIDENCE_PLANNING_LIMITATION = "runtime evidence contracts are planning-only"
EVIDENCE_SYNTHESIS_LIMITATION = "runtime evidence synthesis is not enabled in this phase"
EVIDENCE_PROVENANCE_RISK = "runtime evidence without provenance must not be trusted"


def build_evidence_contract(
    *,
    evidence_label: str,
    deterministic_rank: int,
    allowed_classification_ids: list[str],
    provenance_required: bool,
    source_required: bool,
    replay_safe: bool,
    drift_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"evidence_label": evidence_label, "deterministic_rank": deterministic_rank}
    return {
        "evidence_type_id": f"runtime_evidence_{evidence_label}_{deterministic_hash(seed)[:12]}",
        "evidence_label": evidence_label,
        "deterministic_rank": deterministic_rank,
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "provenance_required": provenance_required,
        "source_required": source_required,
        "replay_safe": replay_safe,
        "drift_visible": drift_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_evidence_planning_only": True,
        "runtime_evidence_synthesis_enabled": False,
        "runtime_reasoning_decisions_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_evidence_contracts(
    classifications: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_label = {row["classification_label"]: row["classification_id"] for row in (classifications or default_runtime_intelligence_classifications())}

    def ids(*labels: str) -> list[str]:
        return [by_label[label] for label in labels]

    rows = [
        ("observed_runtime_state", 10, ids("verified", "partially_verified", "experimental_only"), True, True, True, True, []),
        ("extracted_static_record", 20, ids("verified", "partially_verified", "provenance_incomplete"), True, True, True, True, []),
        ("normalized_static_record", 30, ids("verified", "partially_verified", "inferred"), True, True, True, True, []),
        ("validated_static_record", 40, ids("verified", "replay_verified"), True, True, True, True, []),
        ("runtime_trace_event", 50, ids("verified", "experimental_only", "unstable"), True, True, False, True, ["runtime trace events are not runtime decisions"]),
        ("replay_trace_event", 60, ids("replay_verified", "verified", "unstable"), True, True, True, True, []),
        ("drift_signal", 70, ids("drift_detected", "unstable", "blocked"), True, True, False, True, ["drift evidence requires explicit review"]),
        ("conflict_signal", 80, ids("conflicting", "blocked"), True, True, False, True, ["conflict evidence requires reconciliation"]),
        ("unsupported_signal", 90, ids("unsupported", "blocked"), True, True, False, True, ["unsupported evidence is visible but not usable"]),
        ("provenance_signal", 100, ids("provenance_incomplete", "partially_verified", "verified"), True, True, False, True, ["provenance signal may identify missing evidence"]),
        ("authorization_signal", 110, ids("authorization_prohibited", "blocked"), True, True, False, True, ["authorization-prohibited evidence blocks enablement"]),
        ("limitation_signal", 120, ids("experimental_only", "partially_verified", "blocked"), True, True, True, True, ["limitation evidence constrains future planning"]),
    ]
    return [
        build_evidence_contract(
            evidence_label=label,
            deterministic_rank=rank,
            allowed_classification_ids=classification_ids,
            provenance_required=True,
            source_required=True,
            replay_safe=replay_safe,
            drift_visible=drift_visible,
            production_authorized=False,
            explicit_limitations=[PLANNING_ONLY_LIMITATION, EVIDENCE_PLANNING_LIMITATION, EVIDENCE_SYNTHESIS_LIMITATION, *limitations],
            explicit_risks=[PRODUCTION_PROHIBITED_RISK, EVIDENCE_PROVENANCE_RISK],
        )
        for label, rank, classification_ids, _provenance, _source, replay_safe, drift_visible, limitations in rows
    ]


def order_evidence_contracts(evidence_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            evidence_contracts,
            key=lambda row: (int(row["deterministic_rank"]), str(row["evidence_label"]), str(row["evidence_type_id"])),
        )
    ]


def build_runtime_evidence_manifest(
    evidence_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_2_runtime_evidence_contracts",
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    ordered = order_evidence_contracts(evidence_contracts or default_runtime_evidence_contracts(classification_rows))
    manifest = {
        "schema_version": "v3_3.runtime_evidence_contracts.1",
        "run": {"run_id": run_id, "evidence_contract_count": len(ordered)},
        "evidence_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "runtime_evidence_planning_only": True,
        "runtime_evidence_synthesis_enabled": False,
        "runtime_reasoning_decisions_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_evidence_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "runtime_certainty_fabricated": False,
            "unsupported_evidence_visible": True,
        },
    }
    manifest["deterministic_hash"] = hash_evidence_manifest(manifest)
    manifest["replay_validation"] = validate_evidence_replay_stability(manifest)
    return manifest


def serialize_runtime_evidence_manifest(manifest: dict[str, Any]) -> str:
    return serialize_evidence_manifest(manifest)
