"""Runtime provenance contracts for v3.3 planning-only intelligence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    PLANNING_ONLY_LIMITATION,
    PRODUCTION_PROHIBITED_RISK,
    default_runtime_intelligence_classifications,
)
from app.runtime_intelligence.classification_hashing import deterministic_hash
from app.runtime_intelligence.evidence_contracts import (
    EVIDENCE_PROVENANCE_RISK,
    default_runtime_evidence_contracts,
)
from app.runtime_intelligence.provenance_hashing import (
    hash_provenance_manifest,
    serialize_provenance_manifest,
    validate_provenance_replay_stability,
)


PROVENANCE_LABELS = (
    "extraction_source",
    "trusted_bundle_source",
    "normalized_data_source",
    "validated_data_source",
    "runtime_trace_source",
    "replay_trace_source",
    "drift_detection_source",
    "conflict_detection_source",
    "manual_audit_source",
    "generated_report_source",
    "unsupported_source",
    "authorization_gate_source",
)

PROVENANCE_PLANNING_LIMITATION = "runtime provenance contracts are planning-only"
PROVENANCE_CERTAINTY_LIMITATION = "provenance contracts do not fabricate runtime certainty"
PROVENANCE_HASH_RISK = "runtime provenance without stable hashes must not be trusted"


def build_provenance_contract(
    *,
    provenance_label: str,
    deterministic_rank: int,
    allowed_evidence_type_ids: list[str],
    allowed_classification_ids: list[str],
    source_required: bool,
    hash_required: bool,
    replay_safe: bool,
    drift_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"provenance_label": provenance_label, "deterministic_rank": deterministic_rank}
    return {
        "provenance_type_id": f"runtime_provenance_{provenance_label}_{deterministic_hash(seed)[:12]}",
        "provenance_label": provenance_label,
        "deterministic_rank": deterministic_rank,
        "allowed_evidence_type_ids": sorted(set(allowed_evidence_type_ids)),
        "allowed_classification_ids": sorted(set(allowed_classification_ids)),
        "source_required": source_required,
        "hash_required": hash_required,
        "replay_safe": replay_safe,
        "drift_visible": drift_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_provenance_planning_only": True,
        "runtime_evidence_synthesis_enabled": False,
        "runtime_reasoning_decisions_enabled": False,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_provenance_contracts(
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    classification_by_label = {row["classification_label"]: row["classification_id"] for row in classification_rows}
    evidence_by_label = {row["evidence_label"]: row["evidence_type_id"] for row in evidence_rows}

    def class_ids(*labels: str) -> list[str]:
        return [classification_by_label[label] for label in labels]

    def evidence_ids(*labels: str) -> list[str]:
        return [evidence_by_label[label] for label in labels]

    rows = [
        ("extraction_source", 10, evidence_ids("extracted_static_record", "provenance_signal"), class_ids("verified", "partially_verified", "provenance_incomplete"), True),
        ("trusted_bundle_source", 20, evidence_ids("validated_static_record", "provenance_signal"), class_ids("verified", "replay_verified"), True),
        ("normalized_data_source", 30, evidence_ids("normalized_static_record", "provenance_signal"), class_ids("verified", "partially_verified", "inferred"), True),
        ("validated_data_source", 40, evidence_ids("validated_static_record", "provenance_signal"), class_ids("verified", "replay_verified"), True),
        ("runtime_trace_source", 50, evidence_ids("runtime_trace_event", "observed_runtime_state"), class_ids("verified", "experimental_only", "unstable"), False),
        ("replay_trace_source", 60, evidence_ids("replay_trace_event", "observed_runtime_state"), class_ids("replay_verified", "verified", "unstable"), True),
        ("drift_detection_source", 70, evidence_ids("drift_signal", "runtime_trace_event"), class_ids("drift_detected", "unstable", "blocked"), False),
        ("conflict_detection_source", 80, evidence_ids("conflict_signal", "runtime_trace_event"), class_ids("conflicting", "blocked"), False),
        ("manual_audit_source", 90, evidence_ids("provenance_signal", "limitation_signal"), class_ids("partially_verified", "blocked", "experimental_only"), False),
        ("generated_report_source", 100, evidence_ids("provenance_signal", "validated_static_record", "limitation_signal"), class_ids("verified", "partially_verified", "experimental_only"), True),
        ("unsupported_source", 110, evidence_ids("unsupported_signal", "provenance_signal"), class_ids("unsupported", "blocked"), False),
        ("authorization_gate_source", 120, evidence_ids("authorization_signal", "provenance_signal"), class_ids("authorization_prohibited", "blocked"), False),
    ]
    return [
        build_provenance_contract(
            provenance_label=label,
            deterministic_rank=rank,
            allowed_evidence_type_ids=evidence_type_ids,
            allowed_classification_ids=classification_ids,
            source_required=True,
            hash_required=True,
            replay_safe=replay_safe,
            drift_visible=True,
            production_authorized=False,
            explicit_limitations=[
                PLANNING_ONLY_LIMITATION,
                PROVENANCE_PLANNING_LIMITATION,
                PROVENANCE_CERTAINTY_LIMITATION,
            ],
            explicit_risks=[
                PRODUCTION_PROHIBITED_RISK,
                EVIDENCE_PROVENANCE_RISK,
                PROVENANCE_HASH_RISK,
            ],
        )
        for label, rank, evidence_type_ids, classification_ids, replay_safe in rows
    ]


def order_provenance_contracts(provenance_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        deepcopy(row)
        for row in sorted(
            provenance_contracts,
            key=lambda row: (int(row["deterministic_rank"]), str(row["provenance_label"]), str(row["provenance_type_id"])),
        )
    ]


def build_runtime_provenance_manifest(
    provenance_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    run_id: str = "v3_3_phase_3_runtime_provenance_contracts",
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    ordered = order_provenance_contracts(
        provenance_contracts
        or default_runtime_provenance_contracts(
            classifications=classification_rows,
            evidence_contracts=evidence_rows,
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_provenance_contracts.1",
        "run": {"run_id": run_id, "provenance_contract_count": len(ordered)},
        "provenance_contracts": ordered,
        "classification_reference_count": len(classification_rows),
        "evidence_reference_count": len(evidence_rows),
        "runtime_provenance_planning_only": True,
        "runtime_evidence_synthesis_enabled": False,
        "runtime_reasoning_decisions_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_provenance_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "provenance_certainty_fabricated": False,
            "unsupported_provenance_visible": True,
        },
    }
    manifest["deterministic_hash"] = hash_provenance_manifest(manifest)
    manifest["replay_validation"] = validate_provenance_replay_stability(manifest)
    return manifest


def serialize_runtime_provenance_manifest(manifest: dict[str, Any]) -> str:
    return serialize_provenance_manifest(manifest)
