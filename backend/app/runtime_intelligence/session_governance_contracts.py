"""Runtime session governance contracts for v3.3 planning-only intelligence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    PLANNING_ONLY_LIMITATION,
    PRODUCTION_PROHIBITED_RISK,
)
from app.runtime_intelligence.classification_hashing import deterministic_hash
from app.runtime_intelligence.drift_audit_contracts import _resolve_deps
from app.runtime_intelligence.session_governance_hashing import (
    hash_session_governance_manifest,
    serialize_session_governance_manifest,
    validate_session_governance_replay_stability,
)


SESSION_LABELS = (
    "session_identity",
    "session_input_manifest",
    "session_isolation_boundary",
    "session_lineage_record",
    "session_replay_scope",
    "session_drift_scope",
    "session_synthesis_scope",
    "session_decision_boundary_scope",
    "session_invalidation_rule",
    "session_rollback_rule",
    "session_authorization_boundary",
    "session_audit_summary",
)

SESSION_GOVERNANCE_PLANNING_LIMITATION = "runtime session governance contracts are planning-only"
SESSION_EXECUTION_LIMITATION = "live session execution is not enabled"
SESSION_CERTAINTY_RISK = "session governance contracts must not fabricate session certainty"


def build_session_governance_contract(
    *,
    session_label: str,
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
    allowed_drift_type_ids: list[str],
    required_previous_session_contract_ids: list[str],
    requires_session_id: bool,
    requires_input_manifest_hash: bool,
    requires_lineage_hash: bool,
    requires_replay_scope: bool,
    requires_drift_scope: bool,
    requires_rollback_path: bool,
    requires_invalidation_rule: bool,
    isolates_session_state: bool,
    blocks_cross_session_mutation: bool,
    blocks_invalidated_session_reuse: bool,
    blocks_production_authorization: bool,
    rollback_visible: bool,
    invalidation_visible: bool,
    drift_visible: bool,
    replay_mismatch_visible: bool,
    boundary_visible: bool,
    production_authorized: bool,
    explicit_limitations: list[str],
    explicit_risks: list[str],
    explainability_required: bool = True,
) -> dict[str, Any]:
    seed = {"session_label": session_label, "deterministic_rank": deterministic_rank}
    return {
        "session_contract_id": f"runtime_session_{session_label}_{deterministic_hash(seed)[:12]}",
        "session_label": session_label,
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
        "allowed_drift_type_ids": sorted(set(allowed_drift_type_ids)),
        "required_previous_session_contract_ids": list(dict.fromkeys(required_previous_session_contract_ids)),
        "requires_session_id": requires_session_id,
        "requires_input_manifest_hash": requires_input_manifest_hash,
        "requires_lineage_hash": requires_lineage_hash,
        "requires_replay_scope": requires_replay_scope,
        "requires_drift_scope": requires_drift_scope,
        "requires_rollback_path": requires_rollback_path,
        "requires_invalidation_rule": requires_invalidation_rule,
        "isolates_session_state": isolates_session_state,
        "blocks_cross_session_mutation": blocks_cross_session_mutation,
        "blocks_invalidated_session_reuse": blocks_invalidated_session_reuse,
        "blocks_production_authorization": blocks_production_authorization,
        "rollback_visible": rollback_visible,
        "invalidation_visible": invalidation_visible,
        "drift_visible": drift_visible,
        "replay_mismatch_visible": replay_mismatch_visible,
        "boundary_visible": boundary_visible,
        "production_authorized": production_authorized,
        "explicit_limitations": sorted(set(explicit_limitations)),
        "explicit_risks": sorted(set(explicit_risks)),
        "explainability_required": explainability_required,
        "runtime_session_governance_planning_only": True,
        "live_session_execution_enabled": False,
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


def default_runtime_session_governance_contracts(
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
    drift_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    deps = _all_deps(classifications, evidence_contracts, provenance_contracts, reasoning_stage_contracts, explanation_contracts, confidence_contracts, synthesis_contracts, boundary_contracts, replay_contracts, drift_contracts)
    c = {row["classification_label"]: row["classification_id"] for row in deps["classifications"]}
    e = {row["evidence_label"]: row["evidence_type_id"] for row in deps["evidence"]}
    p = {row["provenance_label"]: row["provenance_type_id"] for row in deps["provenance"]}
    r = {row["stage_label"]: row["stage_type_id"] for row in deps["reasoning"]}
    x = {row["explanation_label"]: row["explanation_type_id"] for row in deps["explanations"]}
    k = {row["confidence_label"]: row["confidence_type_id"] for row in deps["confidence"]}
    s = {row["synthesis_label"]: row["synthesis_type_id"] for row in deps["synthesis"]}
    b = {row["boundary_label"]: row["boundary_type_id"] for row in deps["boundaries"]}
    y = {row["replay_label"]: row["replay_type_id"] for row in deps["replay"]}
    d = {row["drift_label"]: row["drift_type_id"] for row in deps["drift"]}
    previous: dict[str, str] = {}
    configs = [
        ("session_identity", 10, ["verified", "experimental_only"], ["provenance_signal"], ["generated_report_source"], ["evidence_collection"], ["confidence_summary"], ["deterministic_verified"], ["single_source_preservation"], ["manual_review_required_boundary"], ["replay_session_identity"], ["patch_version_drift"], [], True, True, False, False, False, False, False, True, True, False, False, False, False, True, False, False),
        ("session_input_manifest", 20, ["verified"], ["validated_static_record"], ["trusted_bundle_source"], ["source_validation"], ["evidence_summary"], ["validated_static"], ["single_source_preservation"], ["manual_review_required_boundary"], ["replay_input_manifest"], ["hash_manifest_drift"], ["session_identity"], False, True, False, False, False, False, False, True, True, False, False, False, False, True, False, False),
        ("session_isolation_boundary", 30, ["experimental_only", "blocked"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["blocked"], ["decision_boundary_preserving_merge"], ["blocker_detected_stop"], ["replay_boundary_sequence"], ["decision_boundary_drift"], ["session_input_manifest"], False, False, False, False, False, False, False, True, True, True, False, False, False, True, False, True),
        ("session_lineage_record", 40, ["verified", "provenance_incomplete"], ["provenance_signal"], ["manual_audit_source"], ["provenance_validation"], ["provenance_summary"], ["provenance_incomplete"], ["provenance_preserving_merge"], ["provenance_incomplete_escalation"], ["replay_provenance_sequence"], ["provenance_lineage_drift"], ["session_isolation_boundary"], False, False, True, False, False, False, False, True, True, False, False, False, False, True, False, False),
        ("session_replay_scope", 50, ["replay_verified", "verified"], ["replay_trace_event"], ["replay_trace_source"], ["replay_check"], ["replay_summary"], ["replay_verified"], ["replay_verified_merge"], ["replay_mismatch_stop"], ["replay_audit_summary"], ["replay_sequence_drift"], ["session_lineage_record"], False, False, False, True, False, False, False, True, True, False, False, False, False, True, True, False),
        ("session_drift_scope", 60, ["drift_detected", "unstable"], ["drift_signal"], ["drift_detection_source"], ["drift_check"], ["drift_summary"], ["drift_present"], ["drift_preserving_merge"], ["drift_detected_escalation"], ["replay_synthesis_sequence"], ["evidence_shape_drift", "confidence_boundary_drift"], ["session_replay_scope"], False, False, False, False, True, False, False, True, True, False, False, False, True, True, True, False),
        ("session_synthesis_scope", 70, ["verified", "conflicting"], ["conflict_signal", "validated_static_record"], ["generated_report_source"], ["compatibility_check"], ["reasoning_chain_summary"], ["conflict_present"], ["conflict_preserving_merge"], ["conflict_detected_escalation"], ["replay_synthesis_sequence"], ["synthesis_output_drift"], ["session_drift_scope"], False, False, False, False, False, False, False, True, True, False, False, False, True, True, False, False),
        ("session_decision_boundary_scope", 80, ["blocked", "authorization_prohibited"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["authorization_prohibited"], ["decision_boundary_preserving_merge"], ["production_routing_hard_stop"], ["replay_boundary_sequence"], ["decision_boundary_drift"], ["session_synthesis_scope"], False, False, False, False, False, False, False, True, True, False, True, False, True, True, False, True),
        ("session_invalidation_rule", 90, ["blocked", "unsupported"], ["unsupported_signal"], ["unsupported_source"], ["blocker_detection"], ["unsupported_summary"], ["unsupported"], ["unsupported_preserving_merge"], ["unsupported_hard_stop"], ["replay_confidence_sequence"], ["unsupported_state_drift"], ["session_decision_boundary_scope"], False, False, False, False, False, False, True, True, True, True, False, True, True, True, False, True),
        ("session_rollback_rule", 100, ["unstable", "drift_detected"], ["drift_signal"], ["manual_audit_source"], ["risk_detection"], ["risk_summary"], ["drift_present"], ["drift_preserving_merge"], ["drift_detected_escalation"], ["replay_mismatch_detection"], ["replay_sequence_drift"], ["session_invalidation_rule"], False, False, False, False, False, True, False, True, True, True, True, True, True, True, True, True),
        ("session_authorization_boundary", 110, ["authorization_prohibited"], ["authorization_signal"], ["authorization_gate_source"], ["decision_boundary_check"], ["decision_boundary_summary"], ["authorization_prohibited"], ["decision_boundary_preserving_merge"], ["authorization_prohibited_hard_stop", "production_routing_hard_stop"], ["replay_reproducibility_boundary"], ["production_authorization_drift"], ["session_rollback_rule"], False, False, False, False, False, False, False, True, True, True, True, False, False, True, False, True),
        ("session_audit_summary", 120, ["verified", "experimental_only"], ["provenance_signal", "replay_trace_event"], ["generated_report_source"], ["explanation_preparation"], ["replay_summary"], ["replay_verified"], ["explanation_ready_merge"], ["manual_review_required_boundary"], ["replay_audit_summary"], ["hash_manifest_drift"], ["session_authorization_boundary"], True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True),
    ]
    rows = []
    for label, rank, classifications_, evidence, provenance, reasoning, explanations, confidence, synthesis, boundaries, replay, drift, previous_labels, session_id, input_hash, lineage_hash, replay_scope, drift_scope, rollback_path, invalidation_rule, isolates, cross_block, reuse_block, production_block, rollback_visible, invalidation_visible, drift_visible, replay_mismatch, boundary_visible in configs:
        row = build_session_governance_contract(
            session_label=label,
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
            allowed_drift_type_ids=[d[item] for item in drift],
            required_previous_session_contract_ids=[previous[item] for item in previous_labels],
            requires_session_id=session_id,
            requires_input_manifest_hash=input_hash,
            requires_lineage_hash=lineage_hash,
            requires_replay_scope=replay_scope,
            requires_drift_scope=drift_scope,
            requires_rollback_path=rollback_path,
            requires_invalidation_rule=invalidation_rule,
            isolates_session_state=isolates,
            blocks_cross_session_mutation=cross_block,
            blocks_invalidated_session_reuse=reuse_block,
            blocks_production_authorization=production_block,
            rollback_visible=rollback_visible,
            invalidation_visible=invalidation_visible,
            drift_visible=drift_visible,
            replay_mismatch_visible=replay_mismatch,
            boundary_visible=boundary_visible,
            production_authorized=False,
            explicit_limitations=[PLANNING_ONLY_LIMITATION, SESSION_GOVERNANCE_PLANNING_LIMITATION, SESSION_EXECUTION_LIMITATION],
            explicit_risks=[PRODUCTION_PROHIBITED_RISK, SESSION_CERTAINTY_RISK],
        )
        previous[label] = row["session_contract_id"]
        rows.append(row)
    return rows


def order_session_governance_contracts(session_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(row) for row in sorted(session_contracts, key=lambda row: (int(row["deterministic_rank"]), str(row["session_label"]), str(row["session_contract_id"])))]


def build_runtime_session_governance_manifest(session_contracts: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    deps = _all_deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
        kwargs.get("replay_contracts"),
        kwargs.get("drift_contracts"),
    )
    ordered = order_session_governance_contracts(
        session_contracts
        or default_runtime_session_governance_contracts(
            classifications=deps["classifications"],
            evidence_contracts=deps["evidence"],
            provenance_contracts=deps["provenance"],
            reasoning_stage_contracts=deps["reasoning"],
            explanation_contracts=deps["explanations"],
            confidence_contracts=deps["confidence"],
            synthesis_contracts=deps["synthesis"],
            boundary_contracts=deps["boundaries"],
            replay_contracts=deps["replay"],
            drift_contracts=deps["drift"],
        )
    )
    manifest = {
        "schema_version": "v3_3.runtime_session_governance_contracts.1",
        "run": {"run_id": kwargs.get("run_id", "v3_3_phase_11_runtime_session_governance_contracts"), "session_contract_count": len(ordered)},
        "session_contracts": ordered,
        "classification_reference_count": len(deps["classifications"]),
        "evidence_reference_count": len(deps["evidence"]),
        "provenance_reference_count": len(deps["provenance"]),
        "reasoning_stage_reference_count": len(deps["reasoning"]),
        "explanation_reference_count": len(deps["explanations"]),
        "confidence_reference_count": len(deps["confidence"]),
        "synthesis_reference_count": len(deps["synthesis"]),
        "boundary_reference_count": len(deps["boundaries"]),
        "replay_reference_count": len(deps["replay"]),
        "drift_reference_count": len(deps["drift"]),
        "runtime_session_governance_planning_only": True,
        "live_session_execution_enabled": False,
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
            "source": "v3_3_runtime_session_governance_contracts",
            "deterministic_serializer": "json_sort_keys_sha256",
            "silent_fallback_logic_allowed": False,
            "session_certainty_fabricated": False,
            "invalidated_session_reuse_allowed": False,
        },
    }
    manifest["deterministic_hash"] = hash_session_governance_manifest(manifest)
    manifest["replay_validation"] = validate_session_governance_replay_stability(manifest)
    return manifest


def serialize_runtime_session_governance_manifest(manifest: dict[str, Any]) -> str:
    return serialize_session_governance_manifest(manifest)


def _all_deps(classifications, evidence_contracts, provenance_contracts, reasoning_stage_contracts, explanation_contracts, confidence_contracts, synthesis_contracts, boundary_contracts, replay_contracts, drift_contracts):
    deps = _resolve_deps(classifications, evidence_contracts, provenance_contracts, reasoning_stage_contracts, explanation_contracts, confidence_contracts, synthesis_contracts, boundary_contracts, replay_contracts)
    drift = drift_contracts
    if drift is None:
        from app.runtime_intelligence.drift_audit_contracts import default_runtime_drift_audit_contracts

        drift = default_runtime_drift_audit_contracts(
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
    deps["drift"] = drift
    return deps
