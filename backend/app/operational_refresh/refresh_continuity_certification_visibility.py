"""Fail-visible visibility helpers for v4.1 refresh continuity certification."""

from __future__ import annotations

from .refresh_continuity_certification_models import (
    CONTINUITY_LAYERS,
    CONTINUITY_SEVERITY_BLOCKED,
    CONTINUITY_SEVERITY_INFO,
    CONTINUITY_SEVERITY_PROHIBITED,
    CONTINUITY_SEVERITY_WARNING,
    CONTINUITY_STATE_BLOCKED,
    CONTINUITY_STATE_CROSS_LAYER_CONFLICT,
    CONTINUITY_STATE_FAILURE,
    CONTINUITY_STATE_PRESERVED,
    CONTINUITY_STATE_PROHIBITED,
    CONTINUITY_STATE_STALE,
    CONTINUITY_STATE_UNSUPPORTED,
    CONTINUITY_STATES,
    FAIL_VISIBLE_CONTINUITY_STATES,
    PROHIBITED_CONTINUITY_DOMAINS,
    RefreshContinuityCertification,
    RefreshContinuityCertificationEntry,
    default_refresh_continuity_certification,
)


VALID_CONTINUITY_SEVERITIES: tuple[str, ...] = (
    CONTINUITY_SEVERITY_INFO,
    CONTINUITY_SEVERITY_WARNING,
    CONTINUITY_SEVERITY_BLOCKED,
    CONTINUITY_SEVERITY_PROHIBITED,
)


def count_continuity_states(
    certifications: tuple[RefreshContinuityCertificationEntry, ...] | list[RefreshContinuityCertificationEntry],
) -> dict[str, int]:
    counts = {state: 0 for state in CONTINUITY_STATES}
    counts["invalid"] = 0
    for certification in certifications:
        if certification.state in counts:
            counts[certification.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_continuity_ids(
    certifications: tuple[RefreshContinuityCertificationEntry, ...] | list[RefreshContinuityCertificationEntry],
) -> tuple[str, ...]:
    return tuple(
        certification.certification_id
        for certification in certifications
        if certification.state in FAIL_VISIBLE_CONTINUITY_STATES and certification.fail_visible
    )


def _entry_action_semantics_enabled(entry: RefreshContinuityCertificationEntry) -> bool:
    return (
        entry.remediation_enabled
        or entry.automatic_correction_enabled
        or entry.automatic_repair_enabled
        or entry.recommendation_enabled
        or entry.ranking_enabled
        or entry.scoring_enabled
        or entry.selection_enabled
        or entry.approval_enabled
        or entry.authorization_enabled
        or entry.orchestration_enabled
        or entry.execution_enabled
        or entry.planner_integration_enabled
        or entry.production_consumption_enabled
        or entry.runtime_mutation_enabled
    )


def _layer_aggregation_ids(payload: RefreshContinuityCertification, layer: str) -> tuple[str, ...]:
    aggregation = payload.cross_layer_aggregation
    mapping = {
        "manifest": aggregation.manifest_certification_ids,
        "dependency": aggregation.dependency_certification_ids,
        "lineage": aggregation.lineage_certification_ids,
        "schema": aggregation.schema_certification_ids,
        "sequencing": aggregation.sequencing_certification_ids,
        "drift": aggregation.drift_certification_ids,
        "replay": aggregation.replay_certification_ids,
        "rollback": aggregation.rollback_certification_ids,
        "diagnostics": aggregation.diagnostics_certification_ids,
        "explainability": aggregation.explainability_certification_ids,
    }
    return mapping[layer]


def validate_refresh_continuity_certification_visibility(
    payload: RefreshContinuityCertification | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_continuity_certification()
    counts = count_continuity_states(source.certifications)
    preserved_by_layer = {
        layer: tuple(
            entry.certification_id
            for entry in source.certifications
            if entry.layer == layer and entry.state == CONTINUITY_STATE_PRESERVED
        )
        for layer in CONTINUITY_LAYERS
    }
    failures = tuple(
        entry.certification_id for entry in source.certifications if entry.state == CONTINUITY_STATE_FAILURE
    )
    unsupported = tuple(
        entry.certification_id for entry in source.certifications if entry.state == CONTINUITY_STATE_UNSUPPORTED
    )
    blocked = tuple(entry.certification_id for entry in source.certifications if entry.state == CONTINUITY_STATE_BLOCKED)
    prohibited = tuple(
        entry.certification_id for entry in source.certifications if entry.state == CONTINUITY_STATE_PROHIBITED
    )
    stale = tuple(entry.certification_id for entry in source.certifications if entry.state == CONTINUITY_STATE_STALE)
    conflicts = tuple(
        entry.certification_id for entry in source.certifications if entry.state == CONTINUITY_STATE_CROSS_LAYER_CONFLICT
    )
    aggregation = source.cross_layer_aggregation
    integrity = source.integrity_boundary
    hidden_count = sum(1 for entry in source.certifications if entry.hidden)
    action_semantics_count = sum(1 for entry in source.certifications if _entry_action_semantics_enabled(entry))
    severity_valid = all(entry.severity in VALID_CONTINUITY_SEVERITIES for entry in source.certifications)
    prohibited_domains_visible = set(PROHIBITED_CONTINUITY_DOMAINS).issubset(
        set(integrity.prohibited_continuity_domains)
    )
    layer_coverage_complete = all(preserved_by_layer[layer] for layer in CONTINUITY_LAYERS)
    layer_aggregation_complete = all(
        set(preserved_by_layer[layer]).issubset(set(_layer_aggregation_ids(source, layer)))
        for layer in CONTINUITY_LAYERS
    )
    failure_visible = set(failures).issubset(set(aggregation.continuity_failure_ids))
    unsupported_visible = set(unsupported).issubset(set(aggregation.unsupported_continuity_ids)) and bool(unsupported)
    blocked_visible = set(blocked).issubset(set(aggregation.blocked_continuity_ids)) and bool(blocked)
    prohibited_visible = set(prohibited).issubset(set(aggregation.prohibited_continuity_ids)) and bool(prohibited)
    stale_visible = set(stale).issubset(set(aggregation.stale_continuity_ids)) and bool(stale)
    conflict_visible = set(conflicts).issubset(set(aggregation.cross_layer_conflict_ids)) and bool(conflicts)
    visibility_failures = [
        not layer_coverage_complete,
        not layer_aggregation_complete,
        not failure_visible,
        not unsupported_visible,
        not blocked_visible,
        not prohibited_visible,
        not stale_visible,
        not conflict_visible,
        not severity_valid,
        not prohibited_domains_visible,
        hidden_count != 0,
        action_semantics_count != 0,
        counts["invalid"] != 0,
    ]
    return {
        "valid": not any(visibility_failures),
        "continuity_state_counts": counts,
        "certifications_by_layer": {layer: len(preserved_by_layer[layer]) for layer in CONTINUITY_LAYERS},
        "fail_visible_continuity_count": len(fail_visible_continuity_ids(source.certifications)),
        "continuity_failure_visibility_count": len(aggregation.continuity_failure_ids),
        "unsupported_continuity_state_count": len(aggregation.unsupported_continuity_ids),
        "blocked_continuity_state_count": len(aggregation.blocked_continuity_ids),
        "prohibited_continuity_state_count": len(aggregation.prohibited_continuity_ids),
        "stale_continuity_evidence_count": len(aggregation.stale_continuity_ids),
        "cross_layer_continuity_conflict_count": len(aggregation.cross_layer_conflict_ids),
        "prohibited_domain_visibility_count": len(integrity.prohibited_continuity_domains),
        "hidden_certification_count": hidden_count,
        "certification_action_semantics_count": action_semantics_count,
        "invalid_continuity_state_count": counts["invalid"],
        "continuity_layer_coverage_complete": layer_coverage_complete,
        "cross_layer_continuity_aggregation_visible": layer_aggregation_complete,
        "continuity_failure_visibility_preserved": failure_visible,
        "unsupported_continuity_state_visible": unsupported_visible,
        "blocked_continuity_state_visible": blocked_visible,
        "prohibited_continuity_state_visible": prohibited_visible,
        "stale_continuity_evidence_visible": stale_visible,
        "cross_layer_continuity_conflict_visible": conflict_visible,
        "continuity_severities_valid": severity_valid,
        "prohibited_domains_visible": prohibited_domains_visible,
        **{f"{layer}_continuity_visible": bool(preserved_by_layer[layer]) for layer in CONTINUITY_LAYERS},
    }
