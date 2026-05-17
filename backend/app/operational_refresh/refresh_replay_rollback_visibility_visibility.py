"""Fail-visible visibility helpers for v4.1 replay and rollback governance."""

from __future__ import annotations

from .refresh_replay_rollback_visibility_models import (
    FAIL_VISIBLE_REPLAY_ROLLBACK_STATES,
    PROHIBITED_REPLAY_DOMAINS,
    PROHIBITED_ROLLBACK_DOMAINS,
    REPLAY_ROLLBACK_STATE_BLOCKED,
    REPLAY_ROLLBACK_STATE_PROHIBITED,
    REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT,
    REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT,
    REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_STALE,
    REPLAY_ROLLBACK_STATE_UNSUPPORTED,
    REPLAY_ROLLBACK_STATE_VISIBLE,
    REPLAY_ROLLBACK_STATES,
    VISIBILITY_TYPE_REPLAY,
    VISIBILITY_TYPE_ROLLBACK,
    RefreshReplayRollbackVisibility,
    ReplayRollbackEvidence,
    default_refresh_replay_rollback_visibility,
    default_replay_rollback_evidence,
)


STACK_LAYERS: tuple[str, ...] = ("manifest", "dependency", "lineage", "schema", "sequencing", "drift")


def count_replay_rollback_evidence_states(
    evidence: tuple[ReplayRollbackEvidence, ...] | list[ReplayRollbackEvidence],
) -> dict[str, int]:
    counts = {state: 0 for state in REPLAY_ROLLBACK_STATES}
    counts["invalid"] = 0
    for item in evidence:
        if item.state in counts:
            counts[item.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_replay_rollback_evidence_ids(
    evidence: tuple[ReplayRollbackEvidence, ...] | list[ReplayRollbackEvidence],
) -> tuple[str, ...]:
    return tuple(item.evidence_id for item in evidence if item.state in FAIL_VISIBLE_REPLAY_ROLLBACK_STATES and item.fail_visible)


def _ids_for(
    evidence: tuple[ReplayRollbackEvidence, ...],
    *,
    state: str | None = None,
    visibility_type: str | None = None,
    source_layer: str | None = None,
) -> tuple[str, ...]:
    return tuple(
        item.evidence_id
        for item in evidence
        if (state is None or item.state == state)
        and (visibility_type is None or item.visibility_type == visibility_type)
        and (source_layer is None or item.source_layer == source_layer)
    )


def _execution_semantics_enabled(item: ReplayRollbackEvidence) -> bool:
    return (
        item.replay_execution_enabled
        or item.rollback_execution_enabled
        or item.recovery_execution_enabled
        or item.automatic_rollback_enabled
        or item.automatic_recovery_enabled
        or item.remediation_enabled
        or item.automatic_correction_enabled
        or item.refresh_execution_enabled
        or item.orchestration_enabled
        or item.automatic_sequencing_enabled
        or item.schema_migration_execution_enabled
        or item.planner_integration_enabled
        or item.production_consumption_enabled
        or item.runtime_mutation_enabled
        or item.silent_replay_rollback_correction_enabled
    )


def validate_refresh_replay_rollback_visibility(visibility: RefreshReplayRollbackVisibility) -> dict[str, object]:
    counts = count_replay_rollback_evidence_states(visibility.evidence)
    replay_layer_ids = {
        layer: _ids_for(
            visibility.evidence,
            state=REPLAY_ROLLBACK_STATE_VISIBLE,
            visibility_type=VISIBILITY_TYPE_REPLAY,
            source_layer=layer,
        )
        for layer in STACK_LAYERS
    }
    rollback_layer_ids = {
        layer: _ids_for(
            visibility.evidence,
            state=REPLAY_ROLLBACK_STATE_VISIBLE,
            visibility_type=VISIBILITY_TYPE_ROLLBACK,
            source_layer=layer,
        )
        for layer in STACK_LAYERS
    }
    blocked_replay_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_BLOCKED, visibility_type=VISIBILITY_TYPE_REPLAY)
    blocked_rollback_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_BLOCKED, visibility_type=VISIBILITY_TYPE_ROLLBACK)
    unsupported_replay_ids = _ids_for(
        visibility.evidence,
        state=REPLAY_ROLLBACK_STATE_UNSUPPORTED,
        visibility_type=VISIBILITY_TYPE_REPLAY,
    )
    unsupported_rollback_ids = _ids_for(
        visibility.evidence,
        state=REPLAY_ROLLBACK_STATE_UNSUPPORTED,
        visibility_type=VISIBILITY_TYPE_ROLLBACK,
    )
    stale_replay_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_STALE, visibility_type=VISIBILITY_TYPE_REPLAY)
    stale_rollback_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_STALE, visibility_type=VISIBILITY_TYPE_ROLLBACK)
    prohibited_replay_ids = _ids_for(
        visibility.evidence,
        state=REPLAY_ROLLBACK_STATE_PROHIBITED,
        visibility_type=VISIBILITY_TYPE_REPLAY,
    )
    prohibited_rollback_ids = _ids_for(
        visibility.evidence,
        state=REPLAY_ROLLBACK_STATE_PROHIBITED,
        visibility_type=VISIBILITY_TYPE_ROLLBACK,
    )
    replay_discontinuity_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY)
    rollback_discontinuity_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY)
    replay_lineage_gap_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY)
    rollback_lineage_gap_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY)
    replay_provenance_gap_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY)
    rollback_provenance_gap_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY)
    replay_drift_conflict_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT)
    rollback_drift_conflict_ids = _ids_for(visibility.evidence, state=REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT)
    blocked = visibility.blocked_state_visibility
    unsupported = visibility.unsupported_state_visibility
    replay_domains_visible = set(PROHIBITED_REPLAY_DOMAINS).issubset(set(unsupported.prohibited_replay_domains))
    rollback_domains_visible = set(PROHIBITED_ROLLBACK_DOMAINS).issubset(set(unsupported.prohibited_rollback_domains))
    hidden_evidence_count = sum(1 for item in visibility.evidence if item.hidden)
    evidence_execution_count = sum(1 for item in visibility.evidence if _execution_semantics_enabled(item))
    replay_stack_visible = all(replay_layer_ids[layer] for layer in STACK_LAYERS)
    rollback_stack_visible = all(rollback_layer_ids[layer] for layer in STACK_LAYERS)
    visibility_failures = [
        not replay_stack_visible,
        not rollback_stack_visible,
        bool(set(blocked_replay_ids) - set(blocked.blocked_replay_ids)),
        bool(set(blocked_rollback_ids) - set(blocked.blocked_rollback_ids)),
        bool(set(unsupported_replay_ids) - set(unsupported.unsupported_replay_ids)),
        bool(set(unsupported_rollback_ids) - set(unsupported.unsupported_rollback_ids)),
        bool(set(stale_replay_ids) - set(unsupported.stale_replay_ids)),
        bool(set(stale_rollback_ids) - set(unsupported.stale_rollback_ids)),
        bool(set(prohibited_replay_ids) - set(unsupported.prohibited_replay_ids)),
        bool(set(prohibited_rollback_ids) - set(unsupported.prohibited_rollback_ids)),
        bool(set(replay_discontinuity_ids) - set(blocked.replay_discontinuity_visibility)),
        bool(set(rollback_discontinuity_ids) - set(blocked.rollback_discontinuity_visibility)),
        bool(set(replay_lineage_gap_ids) - set(blocked.replay_lineage_discontinuity_visibility)),
        bool(set(rollback_lineage_gap_ids) - set(blocked.rollback_lineage_discontinuity_visibility)),
        bool(set(replay_provenance_gap_ids) - set(blocked.replay_provenance_discontinuity_visibility)),
        bool(set(rollback_provenance_gap_ids) - set(blocked.rollback_provenance_discontinuity_visibility)),
        bool(set(replay_drift_conflict_ids) - set(blocked.replay_drift_conflict_visibility)),
        bool(set(rollback_drift_conflict_ids) - set(blocked.rollback_drift_conflict_visibility)),
        not replay_domains_visible,
        not rollback_domains_visible,
    ]
    return {
        "evidence_state_counts": counts,
        "fail_visible_evidence_count": len(fail_visible_replay_rollback_evidence_ids(visibility.evidence)),
        "replay_stack_layer_visibility": {layer: len(replay_layer_ids[layer]) for layer in STACK_LAYERS},
        "rollback_stack_layer_visibility": {layer: len(rollback_layer_ids[layer]) for layer in STACK_LAYERS},
        "blocked_replay_visibility_count": len(blocked.blocked_replay_ids),
        "blocked_rollback_visibility_count": len(blocked.blocked_rollback_ids),
        "unsupported_replay_visibility_count": len(unsupported.unsupported_replay_ids),
        "unsupported_rollback_visibility_count": len(unsupported.unsupported_rollback_ids),
        "stale_replay_visibility_count": len(unsupported.stale_replay_ids),
        "stale_rollback_visibility_count": len(unsupported.stale_rollback_ids),
        "prohibited_replay_visibility_count": len(unsupported.prohibited_replay_ids),
        "prohibited_rollback_visibility_count": len(unsupported.prohibited_rollback_ids),
        "replay_discontinuity_visibility_count": len(blocked.replay_discontinuity_visibility),
        "rollback_discontinuity_visibility_count": len(blocked.rollback_discontinuity_visibility),
        "replay_lineage_discontinuity_visibility_count": len(blocked.replay_lineage_discontinuity_visibility),
        "rollback_lineage_discontinuity_visibility_count": len(blocked.rollback_lineage_discontinuity_visibility),
        "replay_provenance_discontinuity_visibility_count": len(blocked.replay_provenance_discontinuity_visibility),
        "rollback_provenance_discontinuity_visibility_count": len(blocked.rollback_provenance_discontinuity_visibility),
        "replay_drift_conflict_visibility_count": len(blocked.replay_drift_conflict_visibility),
        "rollback_drift_conflict_visibility_count": len(blocked.rollback_drift_conflict_visibility),
        "prohibited_replay_domain_visibility_count": len(unsupported.prohibited_replay_domains),
        "prohibited_rollback_domain_visibility_count": len(unsupported.prohibited_rollback_domains),
        "failure_visibility_count": len(unsupported.failure_visibility),
        "hidden_evidence_count": hidden_evidence_count,
        "invalid_evidence_state_count": counts["invalid"],
        "evidence_execution_semantics_count": evidence_execution_count,
        "replay_stack_visible": replay_stack_visible,
        "rollback_stack_visible": rollback_stack_visible,
        "blocked_replay_visible": not bool(set(blocked_replay_ids) - set(blocked.blocked_replay_ids)),
        "blocked_rollback_visible": not bool(set(blocked_rollback_ids) - set(blocked.blocked_rollback_ids)),
        "unsupported_replay_visible": not bool(set(unsupported_replay_ids) - set(unsupported.unsupported_replay_ids)),
        "unsupported_rollback_visible": not bool(set(unsupported_rollback_ids) - set(unsupported.unsupported_rollback_ids)),
        "stale_replay_visible": not bool(set(stale_replay_ids) - set(unsupported.stale_replay_ids)),
        "stale_rollback_visible": not bool(set(stale_rollback_ids) - set(unsupported.stale_rollback_ids)),
        "prohibited_replay_visible": not bool(set(prohibited_replay_ids) - set(unsupported.prohibited_replay_ids)),
        "prohibited_rollback_visible": not bool(set(prohibited_rollback_ids) - set(unsupported.prohibited_rollback_ids)),
        "replay_discontinuity_visible": not bool(set(replay_discontinuity_ids) - set(blocked.replay_discontinuity_visibility)),
        "rollback_discontinuity_visible": not bool(set(rollback_discontinuity_ids) - set(blocked.rollback_discontinuity_visibility)),
        "replay_lineage_discontinuity_visible": not bool(
            set(replay_lineage_gap_ids) - set(blocked.replay_lineage_discontinuity_visibility)
        ),
        "rollback_lineage_discontinuity_visible": not bool(
            set(rollback_lineage_gap_ids) - set(blocked.rollback_lineage_discontinuity_visibility)
        ),
        "replay_provenance_discontinuity_visible": not bool(
            set(replay_provenance_gap_ids) - set(blocked.replay_provenance_discontinuity_visibility)
        ),
        "rollback_provenance_discontinuity_visible": not bool(
            set(rollback_provenance_gap_ids) - set(blocked.rollback_provenance_discontinuity_visibility)
        ),
        "replay_drift_conflict_visible": not bool(set(replay_drift_conflict_ids) - set(blocked.replay_drift_conflict_visibility)),
        "rollback_drift_conflict_visible": not bool(
            set(rollback_drift_conflict_ids) - set(blocked.rollback_drift_conflict_visibility)
        ),
        "prohibited_replay_domains_visible": replay_domains_visible,
        "prohibited_rollback_domains_visible": rollback_domains_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *visibility.evidence,
                visibility.lineage_visibility,
                visibility.provenance_visibility,
                visibility.continuity_metadata,
                visibility.drift_visibility,
                visibility.blocked_state_visibility,
                visibility.unsupported_state_visibility,
                visibility.diagnostics,
                visibility.governance,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_evidence_count == 0
            and counts["invalid"] == 0
            and evidence_execution_count == 0
        ),
    }


def build_default_replay_rollback_evidence() -> tuple[ReplayRollbackEvidence, ...]:
    return default_replay_rollback_evidence()


def build_default_refresh_replay_rollback_visibility() -> RefreshReplayRollbackVisibility:
    return default_refresh_replay_rollback_visibility()
