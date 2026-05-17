"""Diagnostics and explainability summaries for v4.1 refresh continuity certification."""

from __future__ import annotations

from .refresh_continuity_certification_continuity import certify_refresh_continuity
from .refresh_continuity_certification_integrity import (
    enabled_continuity_certification_capability_flags,
    validate_continuity_certification_non_execution,
)
from .refresh_continuity_certification_models import (
    CONTINUITY_LAYERS,
    RefreshContinuityCertification,
    default_refresh_continuity_certification,
)
from .refresh_continuity_certification_visibility import (
    count_continuity_states,
    fail_visible_continuity_ids,
    validate_refresh_continuity_certification_visibility,
)


def build_refresh_continuity_certification_diagnostics(
    payload: RefreshContinuityCertification | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_continuity_certification()
    visibility = validate_refresh_continuity_certification_visibility(source)
    continuity = certify_refresh_continuity(source)
    non_execution = validate_continuity_certification_non_execution(source)
    enabled_flags = enabled_continuity_certification_capability_flags(source)
    return {
        "diagnostics_id": source.diagnostics.diagnostics_id,
        "diagnostics_mode": "descriptive_only",
        "diagnostic_layer_count": len(CONTINUITY_LAYERS),
        "continuity_state_counts": count_continuity_states(source.certifications),
        "fail_visible_continuity_ids": fail_visible_continuity_ids(source.certifications),
        "continuity_failure_visibility_ids": source.diagnostics.failure_visibility_ids,
        "unsupported_visibility_ids": source.diagnostics.unsupported_visibility_ids,
        "blocked_visibility_ids": source.diagnostics.blocked_visibility_ids,
        "prohibited_visibility_ids": source.diagnostics.prohibited_visibility_ids,
        "stale_visibility_ids": source.diagnostics.stale_visibility_ids,
        "cross_layer_conflict_ids": source.diagnostics.cross_layer_conflict_ids,
        "visibility_valid": visibility["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
    }


def build_unified_refresh_continuity_certification(
    payload: RefreshContinuityCertification | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_continuity_certification()
    continuity = certify_refresh_continuity(source)
    visibility = validate_refresh_continuity_certification_visibility(source)
    return {
        "schema": "v4_1_unified_refresh_continuity_certification",
        "continuity_id": source.identity.continuity_id,
        "layer_order": CONTINUITY_LAYERS,
        "layer_validity": {layer: continuity[f"{layer}_continuity_valid"] for layer in CONTINUITY_LAYERS},
        "cross_layer_continuity_valid": continuity["cross_layer_continuity_valid"],
        "provenance_continuity_valid": continuity["provenance_continuity_valid"],
        "lineage_continuity_valid": continuity["lineage_continuity_valid"],
        "replay_continuity_valid": continuity["replay_continuity_valid"],
        "rollback_continuity_valid": continuity["rollback_continuity_valid"],
        "fail_visible_continuity_count": visibility["fail_visible_continuity_count"],
        "certification_mode": "descriptive_only_non_authorizing",
    }


def build_cross_layer_continuity_diagnostics(
    payload: RefreshContinuityCertification | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_continuity_certification()
    visibility = validate_refresh_continuity_certification_visibility(source)
    return {
        "schema": "v4_1_cross_layer_continuity_diagnostics",
        "diagnostics_id": source.diagnostics.diagnostics_id,
        "continuity_failure_visibility_count": visibility["continuity_failure_visibility_count"],
        "unsupported_continuity_state_visible": visibility["unsupported_continuity_state_visible"],
        "blocked_continuity_state_visible": visibility["blocked_continuity_state_visible"],
        "prohibited_continuity_state_visible": visibility["prohibited_continuity_state_visible"],
        "stale_continuity_evidence_visible": visibility["stale_continuity_evidence_visible"],
        "cross_layer_continuity_conflict_visible": visibility["cross_layer_continuity_conflict_visible"],
        "hidden_certification_count": visibility["hidden_certification_count"],
        "certification_action_semantics_count": visibility["certification_action_semantics_count"],
        "diagnostics_mode": "fail_visible_descriptive_only",
    }


def build_cross_layer_continuity_explainability(
    payload: RefreshContinuityCertification | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_continuity_certification()
    return {
        "schema": "v4_1_cross_layer_continuity_explainability",
        "explainability_id": source.explainability.explainability_id,
        "limitation_explanation_ids": source.explainability.limitation_explanation_ids,
        "prohibited_explanation_ids": source.explainability.prohibited_explanation_ids,
        "unsupported_explanation_ids": source.explainability.unsupported_explanation_ids,
        "blocked_explanation_ids": source.explainability.blocked_explanation_ids,
        "failure_explanation_count": len(source.explainability.failure_explanation_ids),
        "cross_layer_explanation_ids": source.explainability.cross_layer_explanation_ids,
        "explanation_texts": source.explainability.explanation_texts,
        "explainability_mode": "descriptive_only_non_recommending_non_authorizing",
    }
