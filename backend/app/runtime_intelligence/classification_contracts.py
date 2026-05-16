"""Runtime intelligence classification contracts for v3.3.

These contracts provide deterministic planning-only classifications for future
runtime reasoning. They do not authorize production routing, manifest
consumption, or production-authoritative manifests.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_hashing import (
    deterministic_hash,
    hash_classification_manifest,
    stable_serialize,
    validate_replay_stability,
)


CLASSIFICATION_LABELS = (
    "verified",
    "replay_verified",
    "partially_verified",
    "inferred",
    "unsupported",
    "blocked",
    "conflicting",
    "unstable",
    "drift_detected",
    "provenance_incomplete",
    "authorization_prohibited",
    "experimental_only",
)

PLANNING_ONLY_LIMITATION = "runtime intelligence classifications are planning-only"
PRODUCTION_PROHIBITED_RISK = "classification must not authorize production runtime routing"


def build_classification_contract(
    *,
    classification_label: str,
    deterministic_rank: int,
    trust_state: str,
    replay_safe: bool,
    production_authorized: bool,
    drift_visible: bool,
    provenance_required: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"classification_label": classification_label, "deterministic_rank": deterministic_rank}
    return {
        "classification_id": f"runtime_intelligence_{classification_label}_{deterministic_hash(seed)[:12]}",
        "classification_label": classification_label,
        "deterministic_rank": deterministic_rank,
        "trust_state": trust_state,
        "replay_safe": replay_safe,
        "production_authorized": production_authorized,
        "drift_visible": drift_visible,
        "provenance_required": provenance_required,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_intelligence_planning_only": True,
        "default_runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
    }


def default_runtime_intelligence_classifications() -> list[dict[str, Any]]:
    rows = [
        ("verified", 10, "verified_evidence", True, False, True, True, [], []),
        ("replay_verified", 20, "replay_verified_evidence", True, False, True, True, [], []),
        ("partially_verified", 30, "partial_evidence", True, False, True, True, ["verification coverage is partial"], ["remaining evidence gaps require review"]),
        ("inferred", 40, "inferred_evidence", False, False, True, True, ["inference is not runtime certainty"], ["inferred classifications require review before use"]),
        ("unsupported", 50, "unsupported_runtime_evidence", False, False, True, True, ["unsupported runtime evidence is visible but not usable"], ["unsupported runtime conditions must block automation"]),
        ("blocked", 60, "blocked_evidence", False, False, True, True, ["blocked classifications require governance action"], ["blocked runtime evidence must not proceed silently"]),
        ("conflicting", 70, "conflicting_evidence", False, False, True, True, ["conflicting evidence requires reconciliation"], ["conflict may indicate unsafe runtime reasoning"]),
        ("unstable", 80, "unstable_evidence", False, False, True, True, ["unstable evidence is not replay-trusted"], ["unstable runtime classifications may drift"]),
        ("drift_detected", 90, "drift_visible_evidence", False, False, True, True, ["drift requires explicit review"], ["drift may invalidate replay assumptions"]),
        ("provenance_incomplete", 100, "provenance_incomplete", False, False, True, True, ["provenance is incomplete"], ["missing provenance blocks runtime certainty"]),
        ("authorization_prohibited", 110, "authorization_prohibited", False, False, True, True, ["authorization is explicitly prohibited"], ["authorization-prohibited states must block runtime enablement"]),
        ("experimental_only", 120, "experimental_only", True, False, True, True, ["experimental-only does not imply production authorization"], ["experimental scope must remain isolated"]),
    ]
    return [
        build_classification_contract(
            classification_label=label,
            deterministic_rank=rank,
            trust_state=trust,
            replay_safe=replay_safe,
            production_authorized=production_authorized,
            drift_visible=drift_visible,
            provenance_required=provenance_required,
            explicit_limitations=[PLANNING_ONLY_LIMITATION, *limitations],
            explicit_risks=[PRODUCTION_PROHIBITED_RISK, *risks],
        )
        for label, rank, trust, replay_safe, production_authorized, drift_visible, provenance_required, limitations, risks in rows
    ]


def order_classifications(classifications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(row) for row in sorted(classifications, key=lambda row: (int(row["deterministic_rank"]), str(row["classification_label"]), str(row["classification_id"])))]


def build_runtime_intelligence_classification_manifest(
    classifications: list[dict[str, Any]] | None = None,
    *,
    run_id: str = "v3_3_phase_1_runtime_intelligence_classification_contracts",
) -> dict[str, Any]:
    ordered = order_classifications(classifications or default_runtime_intelligence_classifications())
    manifest = {
        "schema_version": "v3_3.runtime_intelligence_classification_contracts.1",
        "run": {"run_id": run_id, "classification_count": len(ordered)},
        "classifications": ordered,
        "runtime_intelligence_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "metadata": {
            "source": "v3_3_runtime_intelligence_classification_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "runtime_certainty_fabricated": False,
            "unsupported_classifications_visible": True,
        },
    }
    manifest["deterministic_hash"] = hash_classification_manifest(manifest)
    manifest["replay_validation"] = validate_replay_stability(manifest)
    return manifest


def serialize_classification_manifest(manifest: dict[str, Any]) -> str:
    return stable_serialize(manifest)


def classification_labels() -> tuple[str, ...]:
    return CLASSIFICATION_LABELS
